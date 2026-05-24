"""Sync orchestration from local Solo CRM records to enabled external CRMs."""
from __future__ import annotations

from typing import Any

from .sync_log import append_sync_event, get_sync_event, update_sync_event
from .config import load_connectors_config, provider_config_for_site
from .hubspot import HubSpotConnector
from .google_sheets import GoogleSheetsConnector


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


def _sync_google_sheets(config: dict[str, Any], contact: dict[str, Any], company: dict[str, Any] | None,
                        website: dict[str, Any] | None, visitor: dict[str, Any] | None,
                        deal: dict[str, Any] | None, activity: dict[str, Any] | None) -> dict[str, Any]:
    connector = GoogleSheetsConnector(config)
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
                                 activity_id: int | None = None, provider_names: list[str] | None = None,
                                 retry_of: str | None = None) -> dict[str, Any]:
    """Sync one local CRM contact/deal/activity to enabled external CRM providers.

    Local CRM writes are the source of truth; this function returns sanitized status
    objects and never raises provider errors to callers.
    """
    config = load_connectors_config()
    providers: list[dict[str, Any]] = []
    enabled_filter = set(provider_names or [])
    contact = crm.get_contact(int(contact_id)) if contact_id else None
    if not contact:
        return {"enabled": False, "ok": False, "providers": [], "error": "contact_not_found"}
    deal = crm.get_deal(int(deal_id)) if deal_id and hasattr(crm, "get_deal") else None
    activity = crm.get_activity(int(activity_id)) if activity_id and hasattr(crm, "get_activity") else None
    company = _get_company(crm, contact, deal)
    website = _get_website(crm, site_id)
    visitor = _get_visitor(crm, contact)

    hubspot_config = provider_config_for_site(config, site_id, "hubspot")
    if hubspot_config and (not enabled_filter or "hubspot" in enabled_filter):
        try:
            result = _sync_hubspot(hubspot_config, contact, company, website, visitor, deal, activity)
            providers.append(result)
            append_sync_event(
                site_id=site_id, provider="hubspot", status="success", ok=True,
                contact_id=contact_id, deal_id=deal_id, activity_id=activity_id,
                result=result, retryable=False, retry_of=retry_of,
            )
        except Exception as exc:  # external sync must not break local lead capture
            result = {"provider": "hubspot", "ok": False, "error": _safe_error(exc)}
            providers.append(result)
            append_sync_event(
                site_id=site_id, provider="hubspot", status="failed", ok=False,
                contact_id=contact_id, deal_id=deal_id, activity_id=activity_id,
                error=result["error"], result=result, retryable=True, retry_of=retry_of,
            )

    google_sheets_config = provider_config_for_site(config, site_id, "google_sheets")
    if google_sheets_config and (not enabled_filter or "google_sheets" in enabled_filter):
        try:
            result = _sync_google_sheets(google_sheets_config, contact, company, website, visitor, deal, activity)
            providers.append(result)
            append_sync_event(
                site_id=site_id, provider="google_sheets", status="success", ok=True,
                contact_id=contact_id, deal_id=deal_id, activity_id=activity_id,
                result=result, retryable=False, retry_of=retry_of,
            )
        except Exception as exc:  # external sync must not break local lead capture
            result = {"provider": "google_sheets", "ok": False, "error": _safe_error(exc)}
            providers.append(result)
            append_sync_event(
                site_id=site_id, provider="google_sheets", status="failed", ok=False,
                contact_id=contact_id, deal_id=deal_id, activity_id=activity_id,
                error=result["error"], result=result, retryable=True, retry_of=retry_of,
            )

    return {"enabled": bool(providers), "ok": bool(providers) and all(item.get("ok") for item in providers), "providers": providers}


def retry_sync_event(crm: Any, event_id: str) -> dict[str, Any]:
    """Retry one failed provider sync event by id and return sanitized status."""
    event = get_sync_event(str(event_id or ""))
    if not event:
        return {"enabled": False, "ok": False, "providers": [], "error": "event_not_found"}
    if event.get("status") != "failed" or not event.get("retryable"):
        return {"enabled": False, "ok": False, "providers": [], "error": "event_not_retryable"}
    contact_id = event.get("contact_id")
    if not contact_id:
        return {"enabled": False, "ok": False, "providers": [], "error": "contact_not_found"}
    result = sync_contact_to_enabled_crms(
        crm,
        str(event.get("site_id") or "default"),
        int(contact_id),
        deal_id=int(event["deal_id"]) if event.get("deal_id") is not None else None,
        activity_id=int(event["activity_id"]) if event.get("activity_id") is not None else None,
        provider_names=[str(event.get("provider") or "")],
        retry_of=str(event.get("id") or event_id),
    )
    if result.get("ok"):
        update_sync_event(str(event_id), {"retry_status": "retried"})
    return result
