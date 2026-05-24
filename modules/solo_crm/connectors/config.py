"""Protected configuration helpers for outbound CRM connectors."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_CONNECTORS_CONFIG = Path(os.environ.get(
    "SOLO_CRM_CONNECTORS_CONFIG",
    Path.home() / ".hermes" / "tools" / "solo_crm" / "data" / "crm_connectors.json",
))
SENSITIVE_KEYS = {"access_token", "token", "api_key", "client_secret", "refresh_token", "webhook_url", "service_account_json"}


def connectors_config_path() -> Path:
    return Path(os.environ.get("SOLO_CRM_CONNECTORS_CONFIG", str(DEFAULT_CONNECTORS_CONFIG))).expanduser()


def load_connectors_config(path: str | Path | None = None) -> dict[str, Any]:
    config_path = Path(path).expanduser() if path else connectors_config_path()
    if not config_path.exists():
        return {"sites": {}}
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return {"sites": {}}
    if not isinstance(data, dict):
        return {"sites": {}}
    sites = data.get("sites")
    if not isinstance(sites, dict):
        data["sites"] = {}
    return data


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _public_provider_config(raw: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in raw.items():
        if key in SENSITIVE_KEYS:
            continue
        if key == "token_env":
            env_name = str(value or "").strip()
            result["token_env"] = env_name
            result["configured"] = bool(env_name and os.environ.get(env_name))
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            result[key] = value
    result.setdefault("enabled", _bool(raw.get("enabled")))
    result.setdefault("configured", False)
    return result


def sanitize_connectors_config(config: dict[str, Any] | None = None) -> dict[str, Any]:
    raw = config or load_connectors_config()
    sanitized: dict[str, Any] = {"sites": {}}
    for site_id, site_cfg in (raw.get("sites") or {}).items():
        if not isinstance(site_id, str) or not isinstance(site_cfg, dict):
            continue
        providers: dict[str, Any] = {}
        for provider, provider_cfg in (site_cfg.get("providers") or {}).items():
            if isinstance(provider, str) and isinstance(provider_cfg, dict):
                providers[provider] = _public_provider_config(provider_cfg)
        sanitized["sites"][site_id] = {"enabled": _bool(site_cfg.get("enabled")), "providers": providers}
    return sanitized


def provider_config_for_site(config: dict[str, Any] | None, site_id: str, provider: str) -> dict[str, Any]:
    raw = config or load_connectors_config()
    site_cfg = (raw.get("sites") or {}).get(site_id)
    if not isinstance(site_cfg, dict) or not _bool(site_cfg.get("enabled")):
        return {}
    provider_cfg = (site_cfg.get("providers") or {}).get(provider)
    if not isinstance(provider_cfg, dict) or not _bool(provider_cfg.get("enabled")):
        return {}
    resolved = {key: value for key, value in provider_cfg.items() if key not in SENSITIVE_KEYS}
    token_env = str(provider_cfg.get("token_env") or "").strip()
    if token_env:
        token = os.environ.get(token_env, "")
        if token:
            resolved["access_token"] = token
    elif isinstance(provider_cfg.get("access_token"), str):
        # Supported for temporary local testing only; sanitize_connectors_config never returns it.
        resolved["access_token"] = str(provider_cfg.get("access_token") or "")
    resolved["enabled"] = True
    return resolved
