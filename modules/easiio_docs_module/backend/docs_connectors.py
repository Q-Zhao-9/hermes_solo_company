from __future__ import annotations

import hashlib
import json
import sqlite3
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from docs_audit import DocsAuditStore, calculate_deployment_readiness
from docs_db import clean_text

SUPPORTED_CONNECTORS = {
    "sitelet": {
        "id": "sitelet",
        "label": "Sitelet preview/deployment handoff",
        "description": "Dry-run preflight for handing a local Easiio Docs deployment package to a Sitelet operator or future Sitelet API connector.",
        "targets": ["sitelet", "static-html"],
        "requiredConfig": ["base_url"],
        "optionalConfig": ["sitelet_project", "notes"],
        "secretConfig": ["api_token", "authorization", "owner_token"],
    },
    "wordpress": {
        "id": "wordpress",
        "label": "WordPress plugin/shortcode handoff",
        "description": "Dry-run preflight for WordPress package/plugin operator handoff. It does not call wp-admin or the WordPress REST API.",
        "targets": ["wordpress", "static-html"],
        "requiredConfig": ["site_url"],
        "optionalConfig": ["shortcode_page", "plugin_slug", "notes"],
        "secretConfig": ["application_password", "api_token", "authorization", "password"],
    },
    "static-hosting": {
        "id": "static-hosting",
        "label": "Static hosting handoff",
        "description": "Dry-run preflight for static hosting targets such as S3, Cloudflare Pages, Netlify, Vercel static output, or manual FTP handoff.",
        "targets": ["static-html", "nextjs-mdx", "docusaurus", "mkdocs", "hugo", "vitepress"],
        "requiredConfig": ["destination"],
        "optionalConfig": ["cdn_url", "bucket", "branch", "notes"],
        "secretConfig": ["access_key", "secret_key", "api_token", "authorization", "password"],
    },
}

SECRET_KEYWORDS = ("token", "secret", "password", "authorization", "api_key", "access_key", "private_key", "credential")


def redact_connector_config(config: dict[str, Any] | None) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    if not isinstance(config, dict):
        return redacted
    for key, value in config.items():
        clean_key = clean_text(key, 120)
        lowered = clean_key.lower()
        if any(word in lowered for word in SECRET_KEYWORDS):
            redacted[clean_key] = "[REDACTED]" if value not in (None, "") else ""
        elif isinstance(value, (str, int, float, bool)) or value is None:
            redacted[clean_key] = clean_text(value, 500) if isinstance(value, str) else value
        elif isinstance(value, list):
            redacted[clean_key] = [clean_text(item, 200) if isinstance(item, str) else item for item in value[:20]]
        elif isinstance(value, dict):
            redacted[clean_key] = redact_connector_config(value)
        else:
            redacted[clean_key] = clean_text(str(value), 300)
    return redacted


def _init_connector_schema(audit_store: DocsAuditStore) -> None:
    with audit_store.connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS docs_connector_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id TEXT NOT NULL,
                name TEXT NOT NULL,
                connector TEXT NOT NULL,
                environment TEXT NOT NULL DEFAULT '',
                target TEXT NOT NULL DEFAULT '',
                redacted_config_json TEXT NOT NULL DEFAULT '{}',
                secret_placeholders_only INTEGER NOT NULL DEFAULT 1,
                created_by TEXT NOT NULL DEFAULT '',
                updated_at INTEGER NOT NULL,
                created_at INTEGER NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_docs_connector_profiles_site ON docs_connector_profiles(site_id, updated_at DESC)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS docs_connector_dry_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id TEXT NOT NULL,
                audit_record_id INTEGER NOT NULL DEFAULT 0,
                profile_id INTEGER NOT NULL DEFAULT 0,
                connector TEXT NOT NULL,
                environment TEXT NOT NULL DEFAULT '',
                target TEXT NOT NULL DEFAULT '',
                passed INTEGER NOT NULL DEFAULT 0,
                readiness_score INTEGER NOT NULL DEFAULT 0,
                dry_run_only INTEGER NOT NULL DEFAULT 1,
                local_only INTEGER NOT NULL DEFAULT 1,
                external_calls_blocked INTEGER NOT NULL DEFAULT 1,
                requested_by TEXT NOT NULL DEFAULT '',
                redacted_config_json TEXT NOT NULL DEFAULT '{}',
                preflight_json TEXT NOT NULL DEFAULT '{}',
                created_at INTEGER NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_docs_connector_dry_runs_site ON docs_connector_dry_runs(site_id, created_at DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_docs_connector_dry_runs_package ON docs_connector_dry_runs(audit_record_id, created_at DESC)")


def _load_json(text: str, fallback: Any) -> Any:
    try:
        parsed = json.loads(text or "")
        return parsed if parsed is not None else fallback
    except json.JSONDecodeError:
        return fallback


def _connector_catalog() -> list[dict[str, Any]]:
    return [dict(value) for value in SUPPORTED_CONNECTORS.values()]


def build_connector_catalog_response() -> dict[str, Any]:
    return {
        "ok": True,
        "exportType": "easiio-docs-connector-catalog",
        "phase": "22-connector-runbooks",
        "connectors": _connector_catalog(),
        "dryRunOnly": True,
        "localOnly": True,
        "externalCallsBlocked": True,
        "safety": [
            "No connector endpoint uploads, publishes, deploys, rolls back, or calls external APIs in Phase 22.",
            "Secrets in connectorConfig are redacted before profile persistence and before returning responses.",
            "Profiles store secret placeholders only; dry-run history stores redacted metadata only.",
        ],
    }


def _connector_for_id(connector_id: str) -> dict[str, Any] | None:
    return SUPPORTED_CONNECTORS.get(clean_text(connector_id, 80).lower())


def _connector_for_payload(payload: dict[str, Any]) -> dict[str, Any] | None:
    return _connector_for_id(payload.get("connector") or payload.get("connectorType") or payload.get("type") or "")


def _missing_required_config(connector: dict[str, Any], config: dict[str, Any]) -> list[str]:
    missing = []
    for key in connector.get("requiredConfig") or []:
        value = config.get(key)
        if value in (None, ""):
            missing.append(key)
    return missing


def _profile_from_row(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if not row:
        return None
    return {
        "id": int(row["id"]),
        "site_id": row["site_id"],
        "name": row["name"],
        "connector": row["connector"],
        "environment": row["environment"],
        "target": row["target"],
        "redactedConfig": _load_json(row["redacted_config_json"], {}),
        "secretPlaceholdersOnly": bool(row["secret_placeholders_only"]),
        "createdBy": row["created_by"],
        "updatedAt": int(row["updated_at"]),
        "createdAt": int(row["created_at"]),
        "localOnly": True,
    }


def get_connector_profile(audit_store: DocsAuditStore, profile_id: int | str) -> dict[str, Any] | None:
    _init_connector_schema(audit_store)
    try:
        pid = int(profile_id)
    except (TypeError, ValueError):
        return None
    with audit_store.connect() as conn:
        row = conn.execute("SELECT * FROM docs_connector_profiles WHERE id = ?", (pid,)).fetchone()
    return _profile_from_row(row)


def build_connector_profile_save_response(audit_store: DocsAuditStore, payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("confirmSaveConnectorProfile") is not True:
        return {
            "ok": False,
            "error": "confirmSaveConnectorProfile is required before saving connector profile placeholders",
            "requiresConnectorProfileConfirmation": True,
            "connectorProfileBlocked": True,
            "secretPlaceholdersOnly": True,
            "localOnly": True,
        }
    connector = _connector_for_payload(payload)
    if not connector:
        return {"ok": False, "error": "unsupported connector", "supportedConnectors": sorted(SUPPORTED_CONNECTORS), "connectorProfileBlocked": True}
    site_id = clean_text(payload.get("site_id") or payload.get("siteId"), 100)
    if not site_id:
        return {"ok": False, "error": "site_id is required", "connectorProfileBlocked": True}
    name = clean_text(payload.get("name") or payload.get("profileName") or f"{connector['id']} profile", 160)
    config = payload.get("connectorConfig") if isinstance(payload.get("connectorConfig"), dict) else {}
    redacted_config = redact_connector_config(config)
    now = int(time.time())
    values = {
        "site_id": site_id,
        "name": name,
        "connector": connector["id"],
        "environment": clean_text(payload.get("environment"), 40),
        "target": clean_text(payload.get("target") or payload.get("deploymentTarget") or "", 80),
        "redacted_config_json": json.dumps(redacted_config, ensure_ascii=False, sort_keys=True),
        "secret_placeholders_only": 1,
        "created_by": clean_text(payload.get("requestedBy") or payload.get("actor") or "operator", 120),
        "updated_at": now,
        "created_at": now,
    }
    _init_connector_schema(audit_store)
    with audit_store.connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO docs_connector_profiles (
                site_id, name, connector, environment, target, redacted_config_json,
                secret_placeholders_only, created_by, updated_at, created_at
            ) VALUES (
                :site_id, :name, :connector, :environment, :target, :redacted_config_json,
                :secret_placeholders_only, :created_by, :updated_at, :created_at
            )
            """,
            values,
        )
        profile_id = int(cur.lastrowid)
        row = conn.execute("SELECT * FROM docs_connector_profiles WHERE id = ?", (profile_id,)).fetchone()
    profile = _profile_from_row(row)
    return {
        "ok": True,
        "exportType": "easiio-docs-connector-profile",
        "phase": "22-connector-runbooks",
        "profile": profile,
        "redactedConfig": redacted_config,
        "secretPlaceholdersOnly": True,
        "localOnly": True,
        "externalCallsBlocked": True,
    }


def build_connector_profiles_response(audit_store: DocsAuditStore, *, site_id: str = "", connector: str = "", limit: int = 25) -> dict[str, Any]:
    _init_connector_schema(audit_store)
    where: list[str] = []
    args: list[Any] = []
    clean_site = clean_text(site_id, 100)
    clean_connector = clean_text(connector, 80).lower()
    if clean_site:
        where.append("site_id = ?")
        args.append(clean_site)
    if clean_connector:
        where.append("connector = ?")
        args.append(clean_connector)
    sql = "SELECT * FROM docs_connector_profiles"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY updated_at DESC, id DESC LIMIT ?"
    args.append(max(1, min(int(limit or 25), 100)))
    with audit_store.connect() as conn:
        rows = conn.execute(sql, args).fetchall()
    return {
        "ok": True,
        "exportType": "easiio-docs-connector-profiles",
        "phase": "22-connector-runbooks",
        "site_id": clean_site,
        "profiles": [_profile_from_row(row) for row in rows],
        "secretPlaceholdersOnly": True,
        "localOnly": True,
    }


def _dry_run_from_row(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if not row:
        return None
    return {
        "id": int(row["id"]),
        "site_id": row["site_id"],
        "auditRecordId": int(row["audit_record_id"]),
        "profileId": int(row["profile_id"]),
        "connector": row["connector"],
        "environment": row["environment"],
        "target": row["target"],
        "passed": bool(row["passed"]),
        "readinessScore": int(row["readiness_score"]),
        "dryRunOnly": bool(row["dry_run_only"]),
        "localOnly": bool(row["local_only"]),
        "externalCallsBlocked": bool(row["external_calls_blocked"]),
        "requestedBy": row["requested_by"],
        "redactedConfig": _load_json(row["redacted_config_json"], {}),
        "preflight": _load_json(row["preflight_json"], {}),
        "createdAt": int(row["created_at"]),
    }


def record_connector_dry_run(audit_store: DocsAuditStore, preflight_response: dict[str, Any], *, profile: dict[str, Any] | None = None) -> dict[str, Any]:
    _init_connector_schema(audit_store)
    record_package = preflight_response.get("package") if isinstance(preflight_response.get("package"), dict) else {}
    preflight = preflight_response.get("preflight") if isinstance(preflight_response.get("preflight"), dict) else {}
    connector = preflight_response.get("connector") if isinstance(preflight_response.get("connector"), dict) else {}
    redacted_config = preflight_response.get("redactedConfig") if isinstance(preflight_response.get("redactedConfig"), dict) else {}
    now = int(time.time())
    values = {
        "site_id": clean_text(record_package.get("site_id"), 100),
        "audit_record_id": int(preflight_response.get("auditRecordId") or record_package.get("id") or 0),
        "profile_id": int((profile or {}).get("id") or 0),
        "connector": clean_text(connector.get("id"), 80),
        "environment": clean_text(record_package.get("environment") or (profile or {}).get("environment"), 40),
        "target": clean_text(record_package.get("deploymentTarget") or record_package.get("exportTarget") or (profile or {}).get("target"), 80),
        "passed": 1 if preflight.get("passed") else 0,
        "readiness_score": int(preflight.get("readinessScore") or 0),
        "dry_run_only": 1,
        "local_only": 1,
        "external_calls_blocked": 1,
        "requested_by": clean_text(preflight_response.get("requestedBy"), 120),
        "redacted_config_json": json.dumps(redacted_config, ensure_ascii=False, sort_keys=True),
        "preflight_json": json.dumps({
            "passed": bool(preflight.get("passed")),
            "readinessScore": int(preflight.get("readinessScore") or 0),
            "packageExists": bool(preflight.get("packageExists")),
            "missingConfig": preflight.get("missingConfig") or [],
            "checks": preflight.get("checks") or [],
        }, ensure_ascii=False, sort_keys=True),
        "created_at": now,
    }
    with audit_store.connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO docs_connector_dry_runs (
                site_id, audit_record_id, profile_id, connector, environment, target,
                passed, readiness_score, dry_run_only, local_only, external_calls_blocked,
                requested_by, redacted_config_json, preflight_json, created_at
            ) VALUES (
                :site_id, :audit_record_id, :profile_id, :connector, :environment, :target,
                :passed, :readiness_score, :dry_run_only, :local_only, :external_calls_blocked,
                :requested_by, :redacted_config_json, :preflight_json, :created_at
            )
            """,
            values,
        )
        row = conn.execute("SELECT * FROM docs_connector_dry_runs WHERE id = ?", (int(cur.lastrowid),)).fetchone()
    return _dry_run_from_row(row) or {}


def build_connector_dry_run_history_response(audit_store: DocsAuditStore, *, site_id: str = "", audit_record_id: str = "", profile_id: str = "", connector: str = "", limit: int = 25) -> dict[str, Any]:
    _init_connector_schema(audit_store)
    where: list[str] = []
    args: list[Any] = []
    if clean_text(site_id, 100):
        where.append("site_id = ?")
        args.append(clean_text(site_id, 100))
    if clean_text(audit_record_id, 40):
        where.append("audit_record_id = ?")
        args.append(int(audit_record_id))
    if clean_text(profile_id, 40):
        where.append("profile_id = ?")
        args.append(int(profile_id))
    if clean_text(connector, 80):
        where.append("connector = ?")
        args.append(clean_text(connector, 80).lower())
    sql = "SELECT * FROM docs_connector_dry_runs"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY created_at DESC, id DESC LIMIT ?"
    args.append(max(1, min(int(limit or 25), 100)))
    with audit_store.connect() as conn:
        rows = conn.execute(sql, args).fetchall()
    return {
        "ok": True,
        "exportType": "easiio-docs-connector-dry-run-history",
        "phase": "22-connector-runbooks",
        "dryRuns": [_dry_run_from_row(row) for row in rows],
        "secretPlaceholdersOnly": True,
        "localOnly": True,
        "externalCallsBlocked": True,
    }


def build_connector_preflight_response(audit_store: DocsAuditStore, payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("confirmConnectorDryRun") is not True:
        return {
            "ok": False,
            "error": "confirmConnectorDryRun is required before running connector preflight",
            "requiresConnectorDryRunConfirmation": True,
            "connectorDryRunBlocked": True,
            "dryRunOnly": True,
            "localOnly": True,
            "externalCallsBlocked": True,
        }
    profile = None
    profile_id = payload.get("profileId") or payload.get("profile_id") or payload.get("connectorProfileId")
    profile_config: dict[str, Any] = {}
    if profile_id not in (None, ""):
        profile = get_connector_profile(audit_store, profile_id)
        if not profile:
            return {"ok": False, "error": "connector profile not found", "notFound": True, "connectorDryRunBlocked": True}
        profile_config = profile.get("redactedConfig") if isinstance(profile.get("redactedConfig"), dict) else {}
    connector = _connector_for_payload(payload) or (profile and _connector_for_id(profile.get("connector", "")))
    if not connector:
        return {"ok": False, "error": "unsupported connector", "supportedConnectors": sorted(SUPPORTED_CONNECTORS), "connectorDryRunBlocked": True}
    record_id = payload.get("id") or payload.get("record_id") or payload.get("auditRecordId")
    record = audit_store.get_deployment_package_detail(record_id)
    if not record:
        return {"ok": False, "error": "deployment package audit record not found", "notFound": True, "connectorDryRunBlocked": True}
    config = payload.get("connectorConfig") if isinstance(payload.get("connectorConfig"), dict) else profile_config
    redacted_config = redact_connector_config(config)
    readiness = calculate_deployment_readiness(record)
    package_path = Path(record.get("packagePath") or "")
    package_exists = package_path.exists() and package_path.is_file()
    target_supported = not connector.get("targets") or record.get("deploymentTarget") in connector.get("targets") or record.get("exportTarget") in connector.get("targets")
    missing_config = _missing_required_config(connector, config)
    checks = [
        {"name": "package_exists", "passed": bool(package_exists), "message": "Local deployment package ZIP is available." if package_exists else "Local deployment package ZIP is missing."},
        {"name": "readiness", "passed": bool(readiness.get("readyForOperatorHandoff") or readiness.get("score", 0) >= 80), "message": f"Readiness score is {readiness.get('score', 0)}/100."},
        {"name": "target_supported", "passed": bool(target_supported), "message": f"Connector supports target {record.get('deploymentTarget') or record.get('exportTarget')}." if target_supported else "Connector does not normally support this target."},
        {"name": "required_config", "passed": not missing_config, "message": "Required connector config is present." if not missing_config else f"Missing config: {', '.join(missing_config)}"},
        {"name": "external_calls", "passed": True, "message": "External calls are blocked in Phase 22 dry-run/runbook mode."},
    ]
    preflight_passed = all(check.get("passed") for check in checks)
    response = {
        "ok": True,
        "exportType": "easiio-docs-connector-preflight",
        "phase": "22-connector-runbooks",
        "connector": connector,
        "profile": profile,
        "auditRecordId": int(record.get("id") or 0),
        "package": {
            "id": record.get("id"),
            "site_id": record.get("site_id"),
            "deploymentTarget": record.get("deploymentTarget"),
            "exportTarget": record.get("exportTarget"),
            "environment": record.get("environment"),
            "locale": record.get("locale"),
            "approvalStatus": record.get("approvalStatus"),
            "packageSize": record.get("packageSize"),
            "packageFileName": package_path.name,
        },
        "preflight": {
            "passed": bool(preflight_passed),
            "packageExists": bool(package_exists),
            "packagePath": package_path.name,
            "readinessScore": int(readiness.get("score") or 0),
            "readyForOperatorHandoff": bool(readiness.get("readyForOperatorHandoff")),
            "missingConfig": missing_config,
            "checks": checks,
        },
        "readiness": readiness,
        "redactedConfig": redacted_config,
        "requestedBy": clean_text(payload.get("requestedBy") or payload.get("actor") or "", 120),
        "dryRunOnly": True,
        "localOnly": True,
        "externalCallsBlocked": True,
        "secretPlaceholdersOnly": bool(profile),
        "nextOperatorSteps": [
            "Review the local deployment handoff ZIP and manifest.",
            "Verify connector configuration outside this module before any real deployment.",
            "Use a separate, explicit future deployment execution workflow if external publishing is approved.",
        ],
    }
    response["dryRunRecord"] = record_connector_dry_run(audit_store, response, profile=profile)
    return response



def get_connector_dry_run(audit_store: DocsAuditStore, dry_run_id: int | str) -> dict[str, Any] | None:
    _init_connector_schema(audit_store)
    try:
        run_id = int(dry_run_id)
    except (TypeError, ValueError):
        return None
    with audit_store.connect() as conn:
        row = conn.execute("SELECT * FROM docs_connector_dry_runs WHERE id = ?", (run_id,)).fetchone()
    return _dry_run_from_row(row)


def _checks_by_name(dry_run: dict[str, Any]) -> dict[str, dict[str, Any]]:
    preflight = dry_run.get("preflight") if isinstance(dry_run.get("preflight"), dict) else {}
    checks = preflight.get("checks") if isinstance(preflight.get("checks"), list) else []
    result: dict[str, dict[str, Any]] = {}
    for check in checks:
        if isinstance(check, dict) and check.get("name"):
            result[clean_text(check.get("name"), 120)] = check
    return result


def build_connector_runbook_response(audit_store: DocsAuditStore, *, dry_run_id: str = "") -> dict[str, Any]:
    dry_run = get_connector_dry_run(audit_store, dry_run_id)
    if not dry_run:
        return {"ok": False, "error": "connector dry-run record not found", "notFound": True, "localOnly": True, "externalCallsBlocked": True}
    connector = _connector_for_id(dry_run.get("connector", "")) or {"id": dry_run.get("connector", ""), "label": dry_run.get("connector", "Connector")}
    checks = _checks_by_name(dry_run)
    missing = []
    for name, check in checks.items():
        if not check.get("passed"):
            missing.append(f"- {name}: {check.get('message', 'Needs review.')}")
    redacted_config = dry_run.get("redactedConfig") if isinstance(dry_run.get("redactedConfig"), dict) else {}
    runbook_lines = [
        f"# Connector runbook — {connector.get('label') or connector.get('id')}",
        "",
        f"Dry-run ID: {dry_run.get('id')}",
        f"Package audit ID: {dry_run.get('auditRecordId')}",
        f"Site ID: {dry_run.get('site_id')}",
        f"Connector: {dry_run.get('connector')}",
        f"Environment: {dry_run.get('environment') or 'not specified'}",
        f"Target: {dry_run.get('target') or 'not specified'}",
        f"Readiness score: {dry_run.get('readinessScore')}/100",
        f"Preflight result: {'passed' if dry_run.get('passed') else 'needs review'}",
        "",
        "## Safety boundary",
        "No external connector calls are made by this module. This runbook is local-only and review-first.",
        "Do not paste real credentials into this report. Connector profiles store redacted placeholders only.",
        "",
        "## Redacted connector configuration",
        "```json",
        json.dumps(redacted_config, ensure_ascii=False, indent=2, sort_keys=True),
        "```",
        "",
        "## Preflight checks",
    ]
    for name, check in checks.items():
        runbook_lines.append(f"- [{'x' if check.get('passed') else ' '}] {name}: {check.get('message', '')}")
    runbook_lines.extend([
        "",
        "## Operator handoff steps",
        "1. Review the local deployment package manifest and release notes.",
        "2. Confirm the connector target/environment outside this module.",
        "3. Verify credentials only in the approved external deployment tool; do not store them here.",
        "4. If all checks passed, use a separate explicitly approved deployment workflow.",
        "5. If checks failed, resolve the items listed below and run another dry-run.",
    ])
    if missing:
        runbook_lines.extend(["", "## Items needing review", *missing])
    return {
        "ok": True,
        "exportType": "easiio-docs-connector-runbook",
        "phase": "22-connector-runbooks",
        "dryRun": dry_run,
        "connector": connector,
        "runbookMarkdown": "\n".join(runbook_lines),
        "localOnly": True,
        "dryRunOnly": True,
        "externalCallsBlocked": True,
        "secretPlaceholdersOnly": True,
    }


def build_connector_dry_run_comparison_response(audit_store: DocsAuditStore, *, left_id: str = "", right_id: str = "") -> dict[str, Any]:
    left = get_connector_dry_run(audit_store, left_id)
    right = get_connector_dry_run(audit_store, right_id)
    if not left or not right:
        return {"ok": False, "error": "both connector dry-run records are required", "notFound": True, "localOnly": True, "externalCallsBlocked": True}
    left_checks = _checks_by_name(left)
    right_checks = _checks_by_name(right)
    all_names = sorted(set(left_checks) | set(right_checks))
    check_diffs: list[dict[str, Any]] = []
    for name in all_names:
        l = left_checks.get(name, {})
        r = right_checks.get(name, {})
        if l.get("passed") != r.get("passed") or l.get("message") != r.get("message"):
            check_diffs.append({
                "name": name,
                "leftPassed": bool(l.get("passed")),
                "rightPassed": bool(r.get("passed")),
                "leftMessage": clean_text(l.get("message"), 500),
                "rightMessage": clean_text(r.get("message"), 500),
            })
    left_score = int(left.get("readinessScore") or 0)
    right_score = int(right.get("readinessScore") or 0)
    return {
        "ok": True,
        "exportType": "easiio-docs-connector-dry-run-comparison",
        "phase": "22-connector-runbooks",
        "left": left,
        "right": right,
        "scoreDelta": left_score - right_score,
        "statusChanged": bool(left.get("passed")) != bool(right.get("passed")),
        "connectorChanged": left.get("connector") != right.get("connector"),
        "profileChanged": left.get("profileId") != right.get("profileId"),
        "checkDiffs": check_diffs,
        "summary": {
            "leftLabel": f"#{left.get('id')} {left.get('connector')} {left_score}/100",
            "rightLabel": f"#{right.get('id')} {right.get('connector')} {right_score}/100",
            "recommendation": "Prefer the dry-run with passing checks and higher readiness; resolve any failed required configuration before external deployment.",
        },
        "localOnly": True,
        "dryRunOnly": True,
        "externalCallsBlocked": True,
        "secretPlaceholdersOnly": True,
    }


OPERATOR_PLAYBOOK_TARGETS = {
    "sitelet": {
        "target": "sitelet",
        "title": "Sitelet Deployment Playbook",
        "description": "Final human operator checklist for handing an Easiio Docs package to Sitelet preview/deployment operations.",
        "steps": [
            "Open the local deployment package and review easiio-docs-deployment-manifest.json.",
            "Confirm the Sitelet preview URL, site ID, environment, and rollback package before any external action.",
            "Upload or hand off files only through an explicitly approved Sitelet deployment workflow outside this module.",
            "Record the resulting Sitelet URL and operator notes in the release tracker.",
        ],
        "verification": ["Preview URL loads", "Docs navigation works", "Assets resolve", "Rollback package remains available"],
    },
    "wordpress": {
        "target": "wordpress",
        "title": "WordPress Deployment Playbook",
        "description": "Final human operator checklist for WordPress plugin, shortcode, or page handoff.",
        "steps": [
            "Verify the WordPress plugin/shortcode instructions and target page outside this module.",
            "Confirm the shortcode page, site URL, plugin status, and editor permissions before any manual publish.",
            "Use the approved WordPress admin process separately; this module does not log in or call wp-admin.",
            "Record the page URL, shortcode used, and reviewer notes in the release tracker.",
        ],
        "verification": ["Shortcode renders", "Public/private visibility is correct", "No draft/internal docs leak", "Rollback instructions are available"],
    },
    "static-hosting": {
        "target": "static-hosting",
        "title": "Static Hosting Deployment Playbook",
        "description": "Final human operator checklist for static hosting, CDN, or manual file handoff.",
        "steps": [
            "Unpack the local deployment ZIP in a temporary review folder.",
            "Confirm destination, CDN/cache behavior, branch/bucket/path, and rollback artifact before upload.",
            "Deploy only through an explicitly approved external hosting workflow outside this module.",
            "Record final URL, checksum, and cache purge notes in the release tracker.",
        ],
        "verification": ["Index page loads", "Static assets load", "Search/docs links work", "Previous release can be restored"],
    },
    "nextjs-mdx": {
        "target": "nextjs-mdx",
        "title": "Next.js MDX Deployment Playbook",
        "description": "Final human operator checklist for Next.js / MDX handoff.",
        "steps": ["Review generated MDX files.", "Run the external Next.js build pipeline separately.", "Confirm routes and metadata.", "Record deployment URL and rollback commit."],
        "verification": ["Build passes", "Routes render", "Metadata is correct", "Rollback commit exists"],
    },
    "docusaurus": {
        "target": "docusaurus",
        "title": "Docusaurus Deployment Playbook",
        "description": "Final human operator checklist for Docusaurus docs handoff.",
        "steps": ["Review docs folder output.", "Run the external Docusaurus build separately.", "Confirm sidebar/navigation.", "Record deployment notes."],
        "verification": ["Build passes", "Sidebar works", "Search/index works", "Rollback artifact exists"],
    },
    "mkdocs": {
        "target": "mkdocs",
        "title": "MkDocs Deployment Playbook",
        "description": "Final human operator checklist for MkDocs handoff.",
        "steps": ["Review mkdocs.yml and docs output.", "Run external MkDocs build separately.", "Confirm navigation.", "Record deployment notes."],
        "verification": ["Build passes", "Navigation works", "Assets load", "Rollback artifact exists"],
    },
    "hugo": {
        "target": "hugo",
        "title": "Hugo Deployment Playbook",
        "description": "Final human operator checklist for Hugo handoff.",
        "steps": ["Review content output.", "Run external Hugo build separately.", "Confirm section routing.", "Record deployment notes."],
        "verification": ["Build passes", "Sections render", "Assets load", "Rollback artifact exists"],
    },
    "vitepress": {
        "target": "vitepress",
        "title": "VitePress Deployment Playbook",
        "description": "Final human operator checklist for VitePress handoff.",
        "steps": ["Review markdown and config output.", "Run external VitePress build separately.", "Confirm sidebar and search.", "Record deployment notes."],
        "verification": ["Build passes", "Sidebar works", "Search works", "Rollback artifact exists"],
    },
}


def _operator_playbook_for_target(target: str) -> dict[str, Any] | None:
    clean_target = clean_text(target, 80).lower()
    if clean_target in OPERATOR_PLAYBOOK_TARGETS:
        return OPERATOR_PLAYBOOK_TARGETS[clean_target]
    if clean_target == "static-html":
        return OPERATOR_PLAYBOOK_TARGETS["static-hosting"]
    return None


def build_operator_playbook_catalog_response() -> dict[str, Any]:
    return {
        "ok": True,
        "exportType": "easiio-docs-operator-playbook-catalog",
        "phase": "23-operator-playbooks",
        "playbooks": [dict(item) for item in OPERATOR_PLAYBOOK_TARGETS.values()],
        "localOnly": True,
        "externalCallsBlocked": True,
        "secretPlaceholdersOnly": True,
    }


def build_operator_release_playbook_response(audit_store: DocsAuditStore, *, record_id: str = "", target: str = "") -> dict[str, Any]:
    record = audit_store.get_deployment_package_detail(record_id)
    if not record:
        return {"ok": False, "error": "deployment package audit record not found", "notFound": True, "localOnly": True, "externalCallsBlocked": True}
    target_value = clean_text(target or record.get("deploymentTarget") or record.get("exportTarget") or "static-hosting", 80).lower()
    template = _operator_playbook_for_target(target_value)
    if not template:
        return {"ok": False, "error": "unsupported operator playbook target", "supportedTargets": sorted(OPERATOR_PLAYBOOK_TARGETS), "localOnly": True, "externalCallsBlocked": True}
    readiness = calculate_deployment_readiness(record)
    checklist = record.get("checklist") if isinstance(record.get("checklist"), dict) else {}
    manifest = record.get("manifest") if isinstance(record.get("manifest"), dict) else {}
    package_path = Path(record.get("packagePath") or "")
    docs_count = record.get("docCount") or manifest.get("documentCount") or 0
    file_count = record.get("fileCount") or manifest.get("fileCount") or 0
    checklist_lines = []
    for key in ["manual_review", "static_files_verified", "sitelet_upload", "wordpress_upload", "production_publish"]:
        item = checklist.get(key) if isinstance(checklist, dict) else {}
        completed = bool(item.get("completed")) if isinstance(item, dict) else False
        note = clean_text(item.get("note", "") if isinstance(item, dict) else "", 300)
        checklist_lines.append(f"- [{'x' if completed else ' '}] {key}: {note}")
    playbook_lines = [
        f"# {template['title']}",
        "",
        "Final operator release playbook for Easiio Docs Module handoff.",
        "",
        "## Safety boundary",
        "No external deployment is executed by this module. This playbook is local-only and review-first.",
        "Do not paste or store real credentials, passwords, API tokens, authorization headers, private keys, or connection strings here.",
        "",
        "## Release package",
        f"- Audit record ID: {record.get('id')}",
        f"- Site ID: {record.get('site_id')}",
        f"- Target: {template['target']}",
        f"- Environment: {record.get('environment') or 'not specified'}",
        f"- Locale: {record.get('locale') or 'not specified'}",
        f"- Approval status: {record.get('approvalStatus') or record.get('approval_status') or 'unknown'}",
        f"- Package file: {package_path.name if package_path.name else 'not available'}",
        f"- Documents: {docs_count}",
        f"- Files: {file_count}",
        f"- Readiness score: {readiness.get('score', 0)}/100",
        "",
        "## Target playbook summary",
        str(template.get("description", "")),
        "",
        "## Operator steps",
    ]
    for idx, step in enumerate(template.get("steps", []), start=1):
        playbook_lines.append(f"{idx}. {step}")
    playbook_lines.extend(["", "## Operator handoff checklist", *checklist_lines, "", "## Verification checklist"])
    for item in template.get("verification", []):
        playbook_lines.append(f"- [ ] {item}")
    playbook_lines.extend([
        "",
        "## Final notes",
        "- Keep the local release archive and restore package available before any external publish.",
        "- If anything fails, stop and use the rollback/restore planning workflow; do not improvise deployment steps.",
        "- Record external deployment results outside this module after the human operator completes them.",
    ])
    return {
        "ok": True,
        "exportType": "easiio-docs-operator-release-playbook",
        "phase": "23-operator-playbooks",
        "auditRecordId": int(record.get("id") or 0),
        "target": template["target"],
        "playbook": dict(template),
        "package": {
            "site_id": record.get("site_id"),
            "environment": record.get("environment"),
            "locale": record.get("locale"),
            "packageFileName": package_path.name,
            "packageSize": record.get("packageSize"),
            "approvalStatus": record.get("approvalStatus") or record.get("approval_status"),
        },
        "readiness": readiness,
        "readyForOperatorHandoff": bool(readiness.get("readyForOperatorHandoff")),
        "playbookMarkdown": "\n".join(playbook_lines),
        "localOnly": True,
        "externalCallsBlocked": True,
        "secretPlaceholdersOnly": True,
    }


ONBOARDING_INTEGRATIONS = {
    "sitelet": {
        "id": "sitelet",
        "title": "Sitelet integration",
        "summary": "Embed or hand off published docs into Sitelet previews and deployment packages.",
        "checklistKey": "sitelet",
    },
    "wordpress": {
        "id": "wordpress",
        "title": "WordPress plugin usage",
        "summary": "Use the Easiio Docs WordPress plugin shortcode and central docs backend.",
        "checklistKey": "wordpress",
    },
    "static-html": {
        "id": "static-html",
        "title": "Static HTML integration",
        "summary": "Embed docs.js/docs.css or use static deployment handoff packages.",
        "checklistKey": "static_html",
    },
    "nextjs-mdx": {"id": "nextjs-mdx", "title": "Next.js MDX integration", "summary": "Use exported MDX files in a Next.js app.", "checklistKey": "nextjs"},
    "docusaurus": {"id": "docusaurus", "title": "Docusaurus integration", "summary": "Use exported Markdown/docs folder with Docusaurus.", "checklistKey": "docusaurus"},
    "mkdocs": {"id": "mkdocs", "title": "MkDocs integration", "summary": "Use exported Markdown and mkdocs.yml handoff.", "checklistKey": "mkdocs"},
    "hugo": {"id": "hugo", "title": "Hugo integration", "summary": "Use exported content files in Hugo.", "checklistKey": "hugo"},
    "vitepress": {"id": "vitepress", "title": "VitePress integration", "summary": "Use exported Markdown/config in VitePress.", "checklistKey": "vitepress"},
}


def _onboarding_integration(integration: str) -> dict[str, Any]:
    key = clean_text(integration or "sitelet", 80).lower()
    if key in ONBOARDING_INTEGRATIONS:
        return ONBOARDING_INTEGRATIONS[key]
    if key == "static-hosting":
        return ONBOARDING_INTEGRATIONS["static-html"]
    return ONBOARDING_INTEGRATIONS["sitelet"]


def _onboarding_checklist(site_id: str, integration: str) -> list[dict[str, Any]]:
    integ = _onboarding_integration(integration)
    return [
        {"key": "install", "label": "Install module files", "done": False, "detail": "Confirm backend, frontend, tests, WordPress plugin, and docs files exist under the module root."},
        {"key": "env", "label": "Configure environment variables", "done": False, "detail": "Set local DB/RAG paths and owner token outside source control using redacted placeholders in docs."},
        {"key": "start_stop", "label": "Verify start/stop commands", "done": False, "detail": "Run backend/app.py locally, call /health, then stop the process cleanly after smoke checks."},
        {"key": "backup", "label": "Backup and restore", "done": False, "detail": "Back up SQLite data, dist packages, release archive, and restore packages before production handoff."},
        {"key": integ["checklistKey"], "label": integ["title"], "done": False, "detail": integ["summary"]},
        {"key": "admin_workflow", "label": "Admin workflow", "done": False, "detail": "Use the protected admin UI for docs editing, export, deployment handoff, release archive, and operator playbooks."},
        {"key": "security", "label": "Security review", "done": False, "detail": "Keep private/internal docs out of public exports and never store raw credentials in profiles, docs, or reports."},
    ]


def build_onboarding_checklist_response(*, site_id: str = "", integration: str = "sitelet") -> dict[str, Any]:
    clean_site = clean_text(site_id or "demo-site", 120)
    integ = _onboarding_integration(integration)
    return {
        "ok": True,
        "exportType": "easiio-docs-onboarding-checklist",
        "phase": "24-onboarding-guide",
        "siteId": clean_site,
        "integration": integ["id"],
        "checklist": _onboarding_checklist(clean_site, integ["id"]),
        "localOnly": True,
        "externalCallsBlocked": True,
        "secretPlaceholdersOnly": True,
    }


def build_onboarding_guide_response(*, site_id: str = "", integration: str = "sitelet") -> dict[str, Any]:
    clean_site = clean_text(site_id or "demo-site", 120)
    integ = _onboarding_integration(integration)
    checklist = _onboarding_checklist(clean_site, integ["id"])
    root_path = "/home/jianl/.hermes/tools/easiio_docs_module"
    install_lines = [
        "# Easiio Docs Module onboarding guide",
        "",
        f"Site ID: `{clean_site}`",
        f"Integration: `{integ['id']}` — {integ['title']}",
        "",
        "## Safety boundary",
        "This onboarding guide is local-only. It does not deploy, publish, upload, call external services, change DNS, or execute rollback/restore.",
        "Use placeholders only. Do not store raw credentials in this module.",
        "",
        "## Install paths",
        f"- Module root: `{root_path}`",
        f"- Backend: `{root_path}/backend/app.py`",
        f"- Admin UI: `{root_path}/frontend/admin.html`",
        f"- Widget: `{root_path}/frontend/docs.js` and `{root_path}/frontend/docs.css`",
        f"- WordPress plugin ZIP: `{root_path}/dist/easiio-docs-wordpress-plugin.zip`",
        "",
        "## Environment variable reference",
        "```bash",
        "EASIIO_DOCS_DB=/path/to/easiio_docs.db",
        "EASIIO_CHATBOT_RAG_STORE=/path/to/rag_content.json",
        "EASIIO_DOCS_OWNER_TOKEN=[REDACTED]",
        "```",
        "",
        "## Start/stop commands",
        "```bash",
        f"cd {root_path}",
        "python3 backend/app.py --host 127.0.0.1 --port 8110",
        "curl http://127.0.0.1:8110/health",
        "# Stop with Ctrl+C or the process manager after smoke checks.",
        "```",
        "",
        "## Backup and restore",
        "- Back up the SQLite DB configured by `EASIIO_DOCS_DB`.",
        "- Back up `dist/easiio-docs-deployments/`, `dist/easiio-docs-release-archive/`, and `dist/easiio-docs-restore-packages/`.",
        "- Verify archive integrity and prepare restore packages before any external handoff.",
        "",
        f"## {integ['title']}",
        integ["summary"],
        "",
    ]
    if integ["id"] == "sitelet":
        install_lines.extend(["### Sitelet integration", "Use Sitelet preview/export endpoints and operator playbooks for local handoff. Keep owner/API tokens outside this module and redacted in docs.", ""])
    elif integ["id"] == "wordpress":
        install_lines.extend(["### WordPress plugin usage", "Install the plugin ZIP through WordPress admin separately, then render `[easiio_docs site_id=\"%s\" mode=\"public\"]`. Keep admin/editor mode on protected pages only." % clean_site, ""])
    else:
        install_lines.extend([f"### {integ['title']}", "Use the matching exporter/deployment handoff package, review generated files locally, then hand off through an explicitly approved external workflow.", ""])
    install_lines.extend(["## Admin workflow guide", "1. Open `/docs/admin.html` with owner authorization configured.", "2. Create or edit docs as draft/private until reviewed.", "3. Preview/export only public published docs for public sites.", "4. Create deployment package, approval metadata, archive/attestation, restore plan, connector dry-run, and operator playbook.", "5. Execute any external deployment outside this module with separate explicit approval.", "", "## Reusable v1 onboarding checklist"])
    for item in checklist:
        install_lines.append(f"- [ ] {item['label']}: {item['detail']}")
    return {
        "ok": True,
        "exportType": "easiio-docs-onboarding-guide",
        "phase": "24-onboarding-guide",
        "siteId": clean_site,
        "integration": integ["id"],
        "integrationInfo": dict(integ),
        "installMarkdown": "\n".join(install_lines),
        "checklist": checklist,
        "localOnly": True,
        "externalCallsBlocked": True,
        "secretPlaceholdersOnly": True,
    }


V1_RELEASE_VERSION = "v1.0.0"
V1_RELEASE_DIR = Path(__file__).resolve().parents[1] / "dist" / "easiio-docs-v1-release"  # dist/easiio-docs-v1-release
V1_RELEASE_INCLUDE_FILES = [
    "README.md",
    "backend/app.py",
    "backend/docs_db.py",
    "backend/docs_sitelet.py",
    "backend/docs_wordpress.py",
    "backend/docs_rag.py",
    "backend/docs_exporters.py",
    "backend/docs_importers.py",
    "backend/docs_deploy.py",
    "backend/docs_audit.py",
    "backend/docs_connectors.py",
    "frontend/docs.js",
    "frontend/docs.css",
    "frontend/demo.html",
    "frontend/admin.html",
    "frontend/admin.js",
    "frontend/admin.css",
    "wordpress-plugin/easiio-docs/easiio-docs.php",
    "tests/test_docs_backend.py",
    "tests/deployment_v1_release_static.test.js",
    "EASIIO_DOCS_MODULE_PHASE25.md",
]


def _v1_final_qa_checklist() -> list[dict[str, Any]]:
    return [
        {"key": "full_regression", "label": "Full regression test suite", "status": "required", "command": "python3 -m py_compile ... && node --check ... && for f in tests/*.test.js; do node $f; done && python3 tests/test_docs_backend.py -v"},
        {"key": "runtime_smoke", "label": "Runtime smoke test", "status": "required", "marker": "easiio_docs_phase25_smoke_ok"},
        {"key": "artifact_cleanup", "label": "Temporary artifact cleanup", "status": "required", "marker": "phase25_smoke_cleanup_ok"},
        {"key": "docs_review", "label": "README and phase documentation review", "status": "required"},
        {"key": "release_package", "label": "Local v1 release package created", "status": "optional-confirmed"},
    ]


def _v1_security_checklist() -> list[dict[str, Any]]:
    return [
        {"key": "secret_redaction", "label": "Secrets, tokens, credentials, and authorization headers are redacted or omitted", "status": "required"},
        {"key": "local_only", "label": "No external deployment is executed by this module", "status": "required"},
        {"key": "owner_protection", "label": "Admin/release endpoints are owner protected when EASIIO_DOCS_OWNER_TOKEN is configured", "status": "required"},
        {"key": "public_scope", "label": "Default public exports use published/public docs only", "status": "required"},
        {"key": "confirmation_gates", "label": "Package/archive/restore/connector/v1 package actions remain confirmation-gated", "status": "required"},
    ]


def _v1_release_markdown() -> str:
    lines = [
        "# Easiio Docs Module v1 release summary",
        "",
        f"Version: `{V1_RELEASE_VERSION}`",
        "Health marker: `25-v1-release`",
        "",
        "## Release freeze",
        "The reusable Easiio Docs Module v1 surface is frozen after Phase 25 for handoff and future integration work.",
        "",
        "## Safety boundary",
        "No external deployment is executed by this module.",
        "No WordPress, Sitelet, hosting, DNS, FTP, rollback, restore, or connector API call is performed by the v1 release package workflow.",
        "All credentials must remain outside the package and be represented only with placeholders such as `[REDACTED]`.",
        "",
        "## Final QA checklist",
    ]
    for item in _v1_final_qa_checklist():
        lines.append(f"- [ ] {item['label']} (`{item['key']}`)")
    lines.append("")
    lines.append("## Security checklist")
    for item in _v1_security_checklist():
        lines.append(f"- [ ] {item['label']} (`{item['key']}`)")
    lines.extend([
        "",
        "## Included release areas",
        "- Backend/content core and admin API",
        "- Embeddable docs widget",
        "- Sitelet preview/export handoff",
        "- WordPress shortcode/plugin helper",
        "- Chatbot/RAG sync planning",
        "- Framework exporters/importers/localization",
        "- Deployment handoff/history/audit/package/approval/archive/restore",
        "- Connector dry-run/profile/runbook/comparison workflows",
        "- Operator playbooks and onboarding guides",
    ])
    return "\n".join(lines)


def build_v1_release_summary_response() -> dict[str, Any]:
    return {
        "ok": True,
        "exportType": "easiio-docs-v1-release-summary",
        "phase": "25-v1-release",
        "version": V1_RELEASE_VERSION,
        "releaseFreeze": {"frozen": True, "scope": "Reusable Easiio Docs Module v1 MVP/handoff", "nextRecommendedWork": "maintenance, docs polishing, and real external connector integrations only after explicit approval"},
        "finalQaChecklist": _v1_final_qa_checklist(),
        "securityChecklist": _v1_security_checklist(),
        "includedFiles": list(V1_RELEASE_INCLUDE_FILES),
        "releaseMarkdown": _v1_release_markdown(),
        "localOnly": True,
        "externalCallsBlocked": True,
        "secretPlaceholdersOnly": True,
    }


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_v1_release_package_response(*, confirm: bool = False, approved_by: str = "") -> dict[str, Any]:
    if not confirm:
        return {"ok": False, "error": "confirmV1ReleasePackage:true is required before creating the local v1 release package", "confirmV1ReleasePackageRequired": True}
    root = Path(__file__).resolve().parents[1]
    V1_RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    package_path = V1_RELEASE_DIR / f"easiio-docs-module-{V1_RELEASE_VERSION}-{timestamp}.zip"
    summary = build_v1_release_summary_response()
    included: list[str] = []
    file_hashes: dict[str, str] = {}
    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in V1_RELEASE_INCLUDE_FILES:
            path = root / rel
            if path.exists() and path.is_file():
                z.write(path, rel)
                included.append(rel)
                file_hashes[rel] = _sha256_file(path)
        manifest = {
            "exportType": "easiio-docs-v1-release-package-manifest",
            "version": V1_RELEASE_VERSION,
            "phase": "25-v1-release",
            "createdAt": timestamp,
            "approvedBy": clean_text(approved_by or "operator", 120),
            "includedFiles": included,
            "fileHashes": file_hashes,
            "localOnly": True,
            "externalCallsBlocked": True,
            "secretPlaceholdersOnly": True,
            "safety": "No external deployment is executed by this module.",
        }
        z.writestr("easiio-docs-v1-release-manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
        z.writestr("EASIIO_DOCS_MODULE_V1_RELEASE_SUMMARY.md", summary["releaseMarkdown"])
    return {
        "ok": True,
        "exportType": "easiio-docs-v1-release-package",
        "phase": "25-v1-release",
        "version": V1_RELEASE_VERSION,
        "packagePath": str(package_path),
        "packageFileName": package_path.name,
        "packageSize": package_path.stat().st_size,
        "packageSha256": _sha256_file(package_path),
        "manifest": manifest,
        "localOnly": True,
        "externalCallsBlocked": True,
        "secretPlaceholdersOnly": True,
    }
