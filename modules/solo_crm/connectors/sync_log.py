"""Safe local sync log and retry queue for outbound CRM connectors."""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_SYNC_LOG = Path(os.environ.get(
    "SOLO_CRM_SYNC_LOG",
    Path.home() / ".hermes" / "tools" / "solo_crm" / "data" / "crm_sync_log.json",
))
SENSITIVE_KEYS = {"access_token", "token", "api_key", "client_secret", "refresh_token", "webhook_url", "service_account_json"}


def sync_log_path() -> Path:
    return Path(os.environ.get("SOLO_CRM_SYNC_LOG", str(DEFAULT_SYNC_LOG))).expanduser()


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load(path: str | Path | None = None) -> dict[str, Any]:
    log_path = Path(path).expanduser() if path else sync_log_path()
    if not log_path.exists():
        return {"events": []}
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
    except Exception:
        return {"events": []}
    if not isinstance(data, dict):
        return {"events": []}
    if not isinstance(data.get("events"), list):
        data["events"] = []
    return data


def _save(data: dict[str, Any], path: str | Path | None = None) -> None:
    log_path = Path(path).expanduser() if path else sync_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = log_path.with_suffix(log_path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(log_path)


def _safe_scalar(value: Any) -> Any:
    if isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in ("secret", "token", "bearer ", "password", "api_key", "webhook")):
            return "[REDACTED]"
        return value[:240]
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return str(value)[:240]


def sanitize_value(value: Any) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if key_text in SENSITIVE_KEYS or key_text.endswith("_env"):
                continue
            result[key_text] = sanitize_value(item)
        return result
    if isinstance(value, list):
        return [sanitize_value(item) for item in value[:20]]
    return _safe_scalar(value)


def append_sync_event(*, site_id: str, provider: str, status: str, ok: bool, contact_id: int | None = None,
                      deal_id: int | None = None, activity_id: int | None = None, error: str | None = None,
                      result: dict[str, Any] | None = None, retryable: bool | None = None,
                      retry_of: str | None = None, path: str | Path | None = None) -> dict[str, Any]:
    """Append a sanitized sync event and return it."""
    event = {
        "id": uuid.uuid4().hex,
        "created_at": _now(),
        "site_id": str(site_id or "default")[:120],
        "provider": str(provider or "unknown")[:80],
        "status": "success" if status == "success" or ok else "failed",
        "ok": bool(ok),
        "contact_id": int(contact_id) if contact_id is not None else None,
        "deal_id": int(deal_id) if deal_id is not None else None,
        "activity_id": int(activity_id) if activity_id is not None else None,
        "retryable": bool((not ok) if retryable is None else retryable),
        "retry_status": "pending" if (not ok and (retryable is None or retryable)) else "none",
        "retry_of": str(retry_of) if retry_of else None,
    }
    if error:
        event["error"] = str(sanitize_value(error))[:180]
    if result:
        event["result"] = sanitize_value(result)
    data = _load(path)
    data["events"].append(event)
    _save(data, path)
    return dict(event)


def list_sync_events(*, site_id: str | None = None, status: str | None = None,
                     provider: str | None = None, limit: int = 50,
                     path: str | Path | None = None) -> list[dict[str, Any]]:
    events = [dict(event) for event in _load(path).get("events", []) if isinstance(event, dict)]
    if site_id:
        events = [event for event in events if event.get("site_id") == site_id]
    if status:
        events = [event for event in events if event.get("status") == status]
    if provider:
        events = [event for event in events if event.get("provider") == provider]
    indexed = list(enumerate(events))
    indexed.sort(key=lambda item: (str(item[1].get("created_at") or ""), item[0]), reverse=True)
    return [event for _, event in indexed[: max(1, min(int(limit or 50), 200))]]


def get_sync_event(event_id: str, *, path: str | Path | None = None) -> dict[str, Any] | None:
    for event in _load(path).get("events", []):
        if isinstance(event, dict) and event.get("id") == event_id:
            return dict(event)
    return None


def update_sync_event(event_id: str, updates: dict[str, Any], *, path: str | Path | None = None) -> dict[str, Any] | None:
    data = _load(path)
    updated = None
    for event in data.get("events", []):
        if isinstance(event, dict) and event.get("id") == event_id:
            for key, value in updates.items():
                event[str(key)] = sanitize_value(value)
            event["updated_at"] = _now()
            updated = dict(event)
            break
    if updated:
        _save(data, path)
    return updated
