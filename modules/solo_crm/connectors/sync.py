"""Sync orchestration from local Solo CRM records to enabled external CRMs."""
from __future__ import annotations

from typing import Any

from .config import load_connectors_config, provider_config_for_site
from .hubspot import HubSpotConnector


def _safe_error(exc: Exception) -> str:
    text = str(exc)
    lowered = text.lower()
    for marker in ("token", "secret", "bearer", "password", "key"):
        if marker in lowered:
            return "provider_error"
    return text[:180] or "provider_error"


def _get_company(crm: Any, contact: dict[str, Any] | None, deal: dict[str, Any] | None) -> dict[str, Any] | None:
    company_id = None
    if contact and contact.get("company_id") is not None:
        company_id = int(contact["company_id"])
    elif deal and deal.get("company_id") is not None:
        company_id = int(deal["company_id"])
    if company_id and hasattr(crm, "get_company"):
        return crm.get_company(company_id)
    return None


def _get_website(crm: Any, site_id: str) -> dict[str, Any] | None:
    if hasattr(crm, "get_website_by_site_id"):
        return crm.get_website_by_site_id(site_id)
    return None


def _get_visitor(crm: Any, contact: dict[str, Any] | None) -> dict[str, Any] | None:
    # SoloCRM does not currently expose get_visitor; keep hook here for future idempotency.
    return None


def _sync_hubspot(config: dict[str, Any], contact: dict[str, Any], company: dict[str, Any] | None,
                  website: dict[str, Any] | None, visitor: dict[str, Any] | None,
                  deal: dict[str, Any] | None, activity: dict[str, Any] | None) -> dict[str, Any]:
    connector = HubSpotConnector(config)
    result = connector.upsert_contact(contact, company=company, website=website, visitor=visitor)
    if company:
        company_result = connector.upsert_company(company)
        if company_result.get("external_company_id"):
            result["external_company_id"] = company_result["external_company_id"]
    if deal:
        deal_result = connector.upsert_deal(deal, contact=contact, company=company)
        if deal_result.get("external_deal_id"):
            result["external_deal_id"] = deal_result["external_deal_id"]
    if activity:
        activity_result = connector.add_activity(activity, contact=contact, deal=deal)
        if activity_result.get("external_activity_id"):
            result["external_activity_id"] = activity_result["external_activity_id"]
    return result


def sync_contact_to_enabled_crms(crm: Any, site_id: str, contact_id: int, *, deal_id: int | None = None,
                                 activity_id: int | None = None) -> dict[str, Any]:
    """Sync one local CRM contact/deal/activity to enabled external CRM providers.

    Local CRM writes are the source of truth; this function returns sanitized status
    objects and never raises provider errors to callers.
    """
    config = load_connectors_config()
    providers: list[dict[str, Any]] = []
    contact = crm.get_contact(int(contact_id)) if contact_id else None
    if not contact:
        return {"enabled": False, "ok": False, "providers": [], "error": "contact_not_found"}
    deal = crm.get_deal(int(deal_id)) if deal_id and hasattr(crm, "get_deal") else None
    activity = crm.get_activity(int(activity_id)) if activity_id and hasattr(crm, "get_activity") else None
    company = _get_company(crm, contact, deal)
    website = _get_website(crm, site_id)
    visitor = _get_visitor(crm, contact)

    hubspot_config = provider_config_for_site(config, site_id, "hubspot")
    if hubspot_config:
        try:
            providers.append(_sync_hubspot(hubspot_config, contact, company, website, visitor, deal, activity))
        except Exception as exc:  # external sync must not break local lead capture
            providers.append({"provider": "hubspot", "ok": False, "error": _safe_error(exc)})

    return {"enabled": bool(providers), "ok": bool(providers) and all(item.get("ok") for item in providers), "providers": providers}
