"""Google Sheets outbound connector for Solo CRM.

This connector is intentionally dependency-free and uses a Google Apps Script
webhook as the write bridge. That is the easiest free/small-business setup:
Solo CRM posts sanitized lead rows to a server-side Apps Script Web App, and the
script appends those rows into a Google Sheet.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable

from .base import CRMConnector

HTTPClient = Callable[..., dict[str, Any]]


def default_http_client(method: str, url: str, *, headers: dict[str, str] | None = None,
                        json_body: dict[str, Any] | None = None, timeout: float = 15) -> dict[str, Any]:
    data = None if json_body is None else json.dumps(json_body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method.upper(), headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:  # noqa: S310 - configured connector endpoint
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"google_sheets_http_{exc.code}: {body[:300]}") from exc


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _tags(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if str(item).strip())
    if isinstance(value, str):
        return value
    return ""


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class GoogleSheetsConnector(CRMConnector):
    """Append Solo CRM records to Google Sheets through a private webhook."""

    provider = "google_sheets"

    def __init__(self, config: dict[str, Any], http_client: HTTPClient | None = None) -> None:
        self.config = dict(config or {})
        self.webhook_url = _clean(self.config.get("webhook_url"))
        self.sheet_name = _clean(self.config.get("sheet_name")) or "Leads"
        self.spreadsheet_id = _clean(self.config.get("spreadsheet_id"))
        self.timeout = float(self.config.get("timeout", 15) or 15)
        self.http_client = http_client or default_http_client

    def _headers(self) -> dict[str, str]:
        if not self.webhook_url:
            raise RuntimeError("google_sheets_not_configured")
        return {"Content-Type": "application/json", "Accept": "application/json"}

    def _append_row(self, record_type: str, row: dict[str, Any]) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "source": "easiio_solo_crm",
            "provider": self.provider,
            "record_type": record_type,
            "sheet_name": self.sheet_name,
            "row": {key: value for key, value in row.items() if value not in (None, "")},
        }
        if self.spreadsheet_id:
            payload["spreadsheet_id"] = self.spreadsheet_id
        result = self.http_client("POST", self.webhook_url, headers=self._headers(), json_body=payload, timeout=self.timeout)
        row_id = _clean((result or {}).get("row_id") or (result or {}).get("id") or (result or {}).get("range"))
        return {"provider": self.provider, "ok": bool((result or {}).get("ok", True)), "row_id": row_id}

    def test_connection(self) -> dict[str, Any]:
        result = self._append_row("test", {"timestamp": _now_iso(), "message": "Easiio Google Sheets connector test"})
        return {"provider": self.provider, "ok": bool(result.get("ok"))}

    def upsert_contact(self, contact: dict[str, Any], company: dict[str, Any] | None = None,
                       website: dict[str, Any] | None = None, visitor: dict[str, Any] | None = None) -> dict[str, Any]:
        row = {
            "timestamp": _now_iso(),
            "contact_id": contact.get("id"),
            "name": _clean(contact.get("name")),
            "email": _clean(contact.get("email")),
            "phone": _clean(contact.get("phone")),
            "role": _clean(contact.get("role")),
            "status": _clean(contact.get("status")),
            "source": _clean(contact.get("source")),
            "tags": _tags(contact.get("tags")),
            "company": _clean((company or {}).get("name")),
            "company_website": _clean((company or {}).get("website")),
            "site_id": _clean((website or {}).get("site_id")),
            "website_domain": _clean((website or {}).get("domain")),
            "visitor_key": _clean((visitor or {}).get("visitor_key")),
        }
        appended = self._append_row("contact", row)
        return {"provider": self.provider, "ok": bool(appended.get("ok")), "external_contact_id": appended.get("row_id") or _clean(contact.get("email"))}

    def upsert_company(self, company: dict[str, Any]) -> dict[str, Any]:
        row = {
            "timestamp": _now_iso(),
            "company_id": company.get("id"),
            "company": _clean(company.get("name")),
            "company_website": _clean(company.get("website")),
            "industry": _clean(company.get("industry")),
            "notes": _clean(company.get("notes")),
        }
        appended = self._append_row("company", row)
        return {"provider": self.provider, "ok": bool(appended.get("ok")), "external_company_id": appended.get("row_id")}

    def upsert_deal(self, deal: dict[str, Any], contact: dict[str, Any] | None = None,
                    company: dict[str, Any] | None = None) -> dict[str, Any]:
        row = {
            "timestamp": _now_iso(),
            "deal_id": deal.get("id"),
            "deal_title": _clean(deal.get("title")),
            "deal_value": deal.get("value"),
            "currency": _clean(deal.get("currency")),
            "stage": _clean(deal.get("stage")),
            "probability": deal.get("probability"),
            "close_date": _clean(deal.get("close_date")),
            "contact_email": _clean((contact or {}).get("email")),
            "company": _clean((company or {}).get("name")),
            "notes": _clean(deal.get("notes")),
        }
        appended = self._append_row("deal", row)
        return {"provider": self.provider, "ok": bool(appended.get("ok")), "external_deal_id": appended.get("row_id")}

    def add_activity(self, activity: dict[str, Any], contact: dict[str, Any] | None = None,
                     deal: dict[str, Any] | None = None) -> dict[str, Any]:
        row = {
            "timestamp": _now_iso(),
            "activity_id": activity.get("id"),
            "activity_kind": _clean(activity.get("kind")),
            "activity_body": _clean(activity.get("body")),
            "happened_at": _clean(activity.get("happened_at")),
            "follow_up_at": _clean(activity.get("follow_up_at")),
            "completed": activity.get("completed"),
            "contact_email": _clean((contact or {}).get("email")),
            "deal_title": _clean((deal or {}).get("title")),
        }
        appended = self._append_row("activity", row)
        return {"provider": self.provider, "ok": bool(appended.get("ok")), "external_activity_id": appended.get("row_id")}
