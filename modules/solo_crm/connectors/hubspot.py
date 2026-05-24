"""HubSpot outbound CRM connector for Solo CRM."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Callable

from .base import CRMConnector

HTTPClient = Callable[..., dict[str, Any]]


def default_http_client(method: str, url: str, *, headers: dict[str, str] | None = None,
                        json_body: dict[str, Any] | None = None, timeout: float = 15) -> dict[str, Any]:
    data = None if json_body is None else json.dumps(json_body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method.upper(), headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:  # noqa: S310 - configured CRM endpoint
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"hubspot_http_{exc.code}: {body[:300]}") from exc


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _split_name(name: str) -> tuple[str, str]:
    parts = name.strip().split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def _tags(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if str(item).strip())
    if isinstance(value, str):
        return value
    return ""


class HubSpotConnector(CRMConnector):
    provider = "hubspot"

    def __init__(self, config: dict[str, Any], http_client: HTTPClient | None = None) -> None:
        self.config = dict(config or {})
        self.access_token = _clean(self.config.get("access_token"))
        self.base_url = _clean(self.config.get("base_url")) or "https://api.hubapi.com"
        self.timeout = float(self.config.get("timeout", 15) or 15)
        self.http_client = http_client or default_http_client

    def _headers(self) -> dict[str, str]:
        if not self.access_token:
            raise RuntimeError("hubspot_not_configured")
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.http_client(method, self.base_url.rstrip("/") + path, headers=self._headers(), json_body=body, timeout=self.timeout)

    def test_connection(self) -> dict[str, Any]:
        self._request("GET", "/crm/v3/properties/contacts")
        return {"provider": self.provider, "ok": True}

    def _search_contact_by_email(self, email: str) -> str:
        if not email:
            return ""
        result = self._request("POST", "/crm/v3/objects/contacts/search", {
            "filterGroups": [{"filters": [{"propertyName": "email", "operator": "EQ", "value": email}]}],
            "properties": ["email"],
            "limit": 1,
        })
        results = result.get("results") if isinstance(result, dict) else []
        if isinstance(results, list) and results:
            return _clean((results[0] or {}).get("id"))
        return ""

    def upsert_contact(self, contact: dict[str, Any], company: dict[str, Any] | None = None,
                       website: dict[str, Any] | None = None, visitor: dict[str, Any] | None = None) -> dict[str, Any]:
        email = _clean(contact.get("email"))
        first, last = _split_name(_clean(contact.get("name")))
        props = {
            "email": email,
            "firstname": first,
            "lastname": last,
            "phone": _clean(contact.get("phone")),
            "jobtitle": _clean(contact.get("role")),
            "lifecyclestage": _clean(self.config.get("lifecyclestage")) or "lead",
            "hs_lead_status": _clean(contact.get("status")) or "NEW",
            "easiio_source": _clean(contact.get("source")),
            "easiio_tags": _tags(contact.get("tags")),
            "easiio_site_id": _clean((website or {}).get("site_id")),
            "easiio_visitor_key": _clean((visitor or {}).get("visitor_key")),
        }
        if company:
            props["company"] = _clean(company.get("name"))
            props["website"] = _clean(company.get("website"))
        props = {key: value for key, value in props.items() if value}
        existing_id = self._search_contact_by_email(email)
        if existing_id:
            self._request("PATCH", f"/crm/v3/objects/contacts/{existing_id}", {"properties": props})
            external_id = existing_id
        else:
            created = self._request("POST", "/crm/v3/objects/contacts", {"properties": props})
            external_id = _clean(created.get("id"))
        return {"provider": self.provider, "ok": True, "external_contact_id": external_id}

    def upsert_company(self, company: dict[str, Any]) -> dict[str, Any]:
        props = {
            "name": _clean(company.get("name")),
            "domain": _clean(company.get("website") or company.get("domain")),
            "website": _clean(company.get("website")),
            "industry": _clean(company.get("industry")),
            "description": _clean(company.get("notes")),
        }
        props = {key: value for key, value in props.items() if value}
        created = self._request("POST", "/crm/v3/objects/companies", {"properties": props})
        return {"provider": self.provider, "ok": True, "external_company_id": _clean(created.get("id"))}

    def upsert_deal(self, deal: dict[str, Any], contact: dict[str, Any] | None = None,
                    company: dict[str, Any] | None = None) -> dict[str, Any]:
        amount = deal.get("value")
        props = {
            "dealname": _clean(deal.get("title")),
            "amount": str(amount if amount not in (None, "") else 0),
            "pipeline": _clean(self.config.get("pipeline_id")) or "default",
            "dealstage": _clean(self.config.get("dealstage")) or _clean(deal.get("stage")) or "appointmentscheduled",
            "description": _clean(deal.get("notes")),
        }
        if deal.get("close_date"):
            props["closedate"] = _clean(deal.get("close_date"))
        created = self._request("POST", "/crm/v3/objects/deals", {"properties": {k: v for k, v in props.items() if v}})
        return {"provider": self.provider, "ok": True, "external_deal_id": _clean(created.get("id"))}

    def add_activity(self, activity: dict[str, Any], contact: dict[str, Any] | None = None,
                     deal: dict[str, Any] | None = None) -> dict[str, Any]:
        body = _clean(activity.get("body"))
        if activity.get("kind"):
            body = f"[{_clean(activity.get('kind'))}] {body}".strip()
        props = {"hs_note_body": body or "Easiio CRM activity"}
        created = self._request("POST", "/crm/v3/objects/notes", {"properties": props})
        return {"provider": self.provider, "ok": True, "external_activity_id": _clean(created.get("id"))}
