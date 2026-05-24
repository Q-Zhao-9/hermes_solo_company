from __future__ import annotations

import argparse
import hmac
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from docs_audit import DocsAuditStore, build_deployment_approval_history_response, build_deployment_approval_response, build_deployment_checklist_response, build_deployment_history_csv_response, build_deployment_history_response, build_deployment_operator_handoff_report_response, build_deployment_package_comparison_response, build_deployment_package_detail_response, build_deployment_package_download_response, build_deployment_release_dashboard_response, build_deployment_release_notes_response, build_deployment_summary_response, build_release_archive_index_response, build_release_archive_integrity_response, build_release_archive_response, build_release_attestation_response, build_release_report_download_response, build_release_rollback_plan_response, build_release_restore_package_response
from docs_connectors import build_connector_catalog_response, build_connector_dry_run_comparison_response, build_connector_dry_run_history_response, build_connector_preflight_response, build_connector_profile_save_response, build_connector_profiles_response, build_connector_runbook_response, build_operator_playbook_catalog_response, build_operator_release_playbook_response, build_onboarding_checklist_response, build_onboarding_guide_response, build_v1_release_package_response, build_v1_release_summary_response
from docs_db import DocsStore, clean_text
from docs_deploy import build_deployment_handoff_package, build_deployment_handoff_preview
from docs_exporters import build_export_package, build_export_preview
from docs_importers import build_import_preview, build_portable_bundle_package, build_portable_bundle_preview, execute_import
from docs_rag import build_rag_preview, sync_docs_to_chatbot_rag
from docs_sitelet import build_sitelet_preview_payload, build_sitelet_preview_response
from docs_wordpress import build_wordpress_draft_execution, build_wordpress_draft_plan, build_wordpress_shortcode_response

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
SERVICE_NAME = "easiio-docs-module"
PHASE_HISTORY = [
    "9-admin-editor",
    "10-import-export-management",
    "11-localization",
    "12-deployment-handoff",
    "13-deployment-history",
    "14-audit-operations",
    "15-package-operations",
    "16-approval-workflow",
    "17-release-dashboard",
    "18-release-archive",
    "19-restore-planning",
    "20-connector-dry-run",
    "21-connector-profiles",
    "22-connector-runbooks",
    "23-operator-playbooks",
    "24-onboarding-guide",
    "25-v1-release",
]
DEFAULT_DB = ROOT / "data" / "easiio_docs.db"
DOCS_DB_PATH = Path(os.environ.get("EASIIO_DOCS_DB", str(DEFAULT_DB)))


@dataclass
class Response:
    status: int
    body: bytes
    headers: dict[str, str]


def json_response(status: int, data: dict[str, Any], extra_headers: dict[str, str] | None = None) -> Response:
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }
    if extra_headers:
        headers.update(extra_headers)
    return Response(status=status, body=json.dumps(data, ensure_ascii=False).encode("utf-8"), headers=headers)


def asset_response(file_name: str, content_type: str) -> Response:
    path = FRONTEND / file_name
    if not path.exists() or not path.is_file():
        return json_response(404, {"ok": False, "error": "asset not found"})
    return Response(
        status=200,
        body=path.read_bytes(),
        headers={
            "Content-Type": content_type,
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Easiio-Owner-Token",
            "Cache-Control": "public, max-age=300",
        },
    )


def configured_owner_token() -> str:
    return os.environ.get("EASIIO_DOCS_OWNER_TOKEN", "").strip()


def get_header(headers: dict[str, str] | None, name: str) -> str:
    if not headers:
        return ""
    lowered = name.lower()
    for key, value in headers.items():
        if key.lower() == lowered:
            return str(value or "")
    return ""


def is_owner_authorized(headers: dict[str, str] | None, params: dict[str, str] | None = None) -> bool:
    token = configured_owner_token()
    if not token:
        return True
    supplied = ""
    authorization = get_header(headers, "Authorization")
    if authorization.lower().startswith("bearer "):
        supplied = authorization.split(" ", 1)[1].strip()
    if not supplied:
        supplied = get_header(headers, "X-Easiio-Owner-Token").strip()
    if not supplied and params:
        supplied = str(params.get("owner_token", "")).strip()
    return bool(supplied) and hmac.compare_digest(supplied, token)


def require_owner_auth(headers: dict[str, str] | None, params: dict[str, str] | None = None) -> Response | None:
    if is_owner_authorized(headers, params):
        return None
    return json_response(401, {
        "ok": False,
        "error": "owner token is required for this Easiio Docs admin action",
        "authRequired": True,
        "authScheme": "Bearer",
    }, {"WWW-Authenticate": 'Bearer realm="easiio-docs-owner"'})


def needs_owner_for_read(status: str = "published", visibility: str = "public", include_private: bool = False) -> bool:
    return include_private or clean_text(status, 40) != "published" or clean_text(visibility, 40) != "public"


def parse_body(body: bytes) -> dict[str, Any]:
    if not body:
        return {}
    try:
        parsed = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        raise ValueError("invalid JSON body")
    if not isinstance(parsed, dict):
        raise ValueError("JSON body must be an object")
    return parsed


def get_store() -> DocsStore:
    return DocsStore(DOCS_DB_PATH)


def get_audit_store() -> DocsAuditStore:
    return DocsAuditStore(DOCS_DB_PATH)


def upload_sitelet_payload(sitelet_payload: dict[str, Any]) -> dict[str, Any]:
    base_url = os.environ.get("SITELET_BASE_URL", "").rstrip("/")
    api_token = os.environ.get("SITELET_API_TOKEN", "")
    if not base_url:
        raise ValueError("SITELET_BASE_URL is required for upload")
    if not api_token:
        raise ValueError("SITELET_API_TOKEN is required for upload")
    data = json.dumps(sitelet_payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url}/api/generated",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_token}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            parsed = json.loads(body or "{}")
            return {"ok": True, "status": response.status, "siteletResponse": parsed}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ValueError(f"Sitelet upload failed with HTTP {exc.code}: {body[:500]}") from exc


def handle_request(method: str, raw_path: str, body: bytes = b"", headers: dict[str, str] | None = None) -> Response:
    headers = headers or {}
    parsed = urlparse(raw_path)
    route = parsed.path.rstrip("/") or "/"
    params = {key: values[-1] if values else "" for key, values in parse_qs(parsed.query).items()}
    if method == "OPTIONS":
        return Response(204, b"", {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET,POST,OPTIONS", "Access-Control-Allow-Headers": "Content-Type, Authorization"})
    if method == "GET" and route == "/docs/docs.js":
        return asset_response("docs.js", "application/javascript; charset=utf-8")
    if method == "GET" and route == "/docs/docs.css":
        return asset_response("docs.css", "text/css; charset=utf-8")
    if method == "GET" and route == "/docs/demo.html":
        return asset_response("demo.html", "text/html; charset=utf-8")
    if method == "GET" and route == "/docs/admin.html":
        auth_error = require_owner_auth(headers, params)
        if auth_error:
            return auth_error
        return asset_response("admin.html", "text/html; charset=utf-8")
    if method == "GET" and route == "/docs/admin.js":
        auth_error = require_owner_auth(headers, params)
        if auth_error:
            return auth_error
        return asset_response("admin.js", "application/javascript; charset=utf-8")
    if method == "GET" and route == "/docs/admin.css":
        auth_error = require_owner_auth(headers, params)
        if auth_error:
            return auth_error
        return asset_response("admin.css", "text/css; charset=utf-8")
    if method == "GET" and route == "/health":
        return json_response(200, {"ok": True, "service": SERVICE_NAME, "phase": "25-v1-release", "phaseHistory": PHASE_HISTORY, "adminAuthConfigured": bool(configured_owner_token())})

    store = get_store()
    try:
        if method == "GET" and route == "/api/docs/docs":
            site_id = clean_text(params.get("site_id"), 100)
            if not site_id:
                return json_response(400, {"ok": False, "error": "site_id is required"})
            status_filter = params.get("status", "published")
            visibility_filter = params.get("visibility", "") or "public"
            if needs_owner_for_read(status_filter, visibility_filter):
                auth_error = require_owner_auth(headers, params)
                if auth_error:
                    return auth_error
            docs = store.list_docs(
                site_id,
                q=params.get("q", ""),
                status=status_filter,
                visibility=params.get("visibility", ""),
                locale=params.get("locale", ""),
            )
            return json_response(200, {"ok": True, "site_id": site_id, "locale": params.get("locale", ""), "docs": docs})
        if method == "GET" and route == "/api/docs/doc":
            site_id = clean_text(params.get("site_id"), 100)
            doc, fallback_used = store.get_doc_localized(site_id, params.get("slug", ""), locale=params.get("locale", ""), fallback_locale=params.get("fallback_locale", "en"))
            if not doc:
                return json_response(404, {"ok": False, "error": "doc not found"})
            if needs_owner_for_read(doc.get("status", "published"), doc.get("visibility", "public")):
                auth_error = require_owner_auth(headers, params)
                if auth_error:
                    return auth_error
            return json_response(200, {"ok": True, "doc": doc, "requestedLocale": params.get("locale", ""), "fallbackLocale": params.get("fallback_locale", "en"), "fallbackUsed": fallback_used})
        if method == "GET" and route == "/api/docs/revisions":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            site_id = clean_text(params.get("site_id"), 100)
            revisions = store.list_revisions(site_id, params.get("slug", ""))
            return json_response(200, {"ok": True, "site_id": site_id, "revisions": revisions})
        if method == "GET" and route == "/api/docs/space":
            site_id = clean_text(params.get("site_id"), 100)
            if not site_id:
                return json_response(400, {"ok": False, "error": "site_id is required"})
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            return json_response(200, {"ok": True, "space": store.get_space_summary(site_id)})
        if method == "GET" and route == "/api/docs/sitelet-preview":
            if needs_owner_for_read(params.get("status", "published"), params.get("visibility", "public")):
                auth_error = require_owner_auth(headers, params)
                if auth_error:
                    return auth_error
            sitelet_payload = build_sitelet_preview_payload(
                store,
                clean_text(params.get("site_id"), 100),
                slug=params.get("slug", ""),
                target=params.get("target", "sitelet"),
                status=params.get("status", "published"),
                visibility=params.get("visibility", "public"),
            )
            return json_response(200, build_sitelet_preview_response(sitelet_payload))
        if method == "GET" and route == "/api/docs/wordpress/shortcode":
            return json_response(200, build_wordpress_shortcode_response(
                clean_text(params.get("site_id"), 100),
                api_base=params.get("api_base", "https://chat.easiio.com"),
                mode=params.get("mode", "public"),
                title=params.get("title", "Documentation"),
                require_login=params.get("require_login", "false"),
                target_filter=params.get("target_filter") or params.get("target") or "wordpress-shortcode",
                credential_mode=params.get("credential_mode", "same-origin"),
            ))
        if method == "GET" and route == "/api/docs/wordpress/draft-plan":
            if needs_owner_for_read(params.get("status", "published"), params.get("visibility", "public")):
                auth_error = require_owner_auth(headers, params)
                if auth_error:
                    return auth_error
            return json_response(200, build_wordpress_draft_plan(
                store,
                clean_text(params.get("site_id"), 100),
                target=params.get("target", "wordpress-shortcode"),
                status=params.get("status", "published"),
                visibility=params.get("visibility", "public"),
                page_title=params.get("page_title", ""),
                slug=params.get("slug", ""),
            ))
        if method == "GET" and route == "/api/docs/rag/preview":
            include_private = params.get("include_private", "false").lower() in {"1", "true", "yes", "on"}
            if needs_owner_for_read(params.get("status", "published"), params.get("visibility", "public"), include_private=include_private):
                auth_error = require_owner_auth(headers, params)
                if auth_error:
                    return auth_error
            return json_response(200, build_rag_preview(
                store,
                clean_text(params.get("site_id"), 100),
                target=params.get("target", "rag"),
                status=params.get("status", "published"),
                visibility=params.get("visibility", "public"),
                include_private=include_private,
            ))
        if method == "GET" and route == "/api/docs/export/preview":
            if needs_owner_for_read(params.get("status", "published"), params.get("visibility", "public")):
                auth_error = require_owner_auth(headers, params)
                if auth_error:
                    return auth_error
            return json_response(200, build_export_preview(
                store,
                clean_text(params.get("site_id"), 100),
                target=params.get("target", "nextjs-mdx"),
                status=params.get("status", "published"),
                visibility=params.get("visibility", "public"),
                locale=params.get("locale", ""),
                fallback_locale=params.get("fallback_locale", "en"),
            ))
        if method == "GET" and route == "/api/docs/bundle/preview":
            if needs_owner_for_read(params.get("status", "published"), params.get("visibility", "public")):
                auth_error = require_owner_auth(headers, params)
                if auth_error:
                    return auth_error
            return json_response(200, build_portable_bundle_preview(
                store,
                clean_text(params.get("site_id"), 100),
                status=params.get("status", "published"),
                visibility=params.get("visibility", "public"),
                locale=params.get("locale", ""),
            ))
        if method == "GET" and route == "/api/docs/deploy/preview":
            if needs_owner_for_read(params.get("status", "published"), params.get("visibility", "public")):
                auth_error = require_owner_auth(headers, params)
                if auth_error:
                    return auth_error
            return json_response(200, build_deployment_handoff_preview(
                store,
                clean_text(params.get("site_id"), 100),
                target=params.get("target", "static-html"),
                environment=params.get("environment", "preview"),
                status=params.get("status", "published"),
                visibility=params.get("visibility", "public"),
                locale=params.get("locale", ""),
            ))
        if method == "GET" and route == "/api/docs/deploy/package":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            result = build_deployment_package_detail_response(get_audit_store(), record_id=params.get("id") or params.get("record_id") or "")
            return json_response(200 if result.get("ok") else 404, result)
        if method == "GET" and route == "/api/docs/deploy/package/download":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            result = build_deployment_package_download_response(get_audit_store(), record_id=params.get("id") or params.get("record_id") or "")
            if not result.get("ok"):
                return json_response(404, result)
            return Response(200, result["body"], {
                "Content-Type": "application/zip",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Easiio-Owner-Token",
                "Content-Disposition": f"attachment; filename={result['fileName']}",
            })
        if method == "GET" and route == "/api/docs/deploy/compare":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            result = build_deployment_package_comparison_response(get_audit_store(), left_id=params.get("left_id") or params.get("left") or "", right_id=params.get("right_id") or params.get("right") or "")
            return json_response(200 if result.get("ok") else 404, result)
        if method == "GET" and route == "/api/docs/deploy/approvals":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            result = build_deployment_approval_history_response(get_audit_store(), record_id=params.get("id") or params.get("record_id") or "")
            return json_response(200 if result.get("ok") else 404, result)
        if method == "GET" and route == "/api/docs/deploy/release-notes":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            result = build_deployment_release_notes_response(get_audit_store(), record_id=params.get("id") or params.get("record_id") or "")
            return json_response(200 if result.get("ok") else 404, result)
        if method == "GET" and route == "/api/docs/deploy/releases":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            try:
                limit = int(params.get("limit", "25") or 25)
            except ValueError:
                limit = 25
            return json_response(200, build_deployment_release_dashboard_response(
                get_audit_store(),
                site_id=params.get("site_id", ""),
                limit=limit,
                target=params.get("target", ""),
                environment=params.get("environment", ""),
                locale=params.get("locale", ""),
                approval_status=params.get("approval_status", "") or params.get("approvalStatus", ""),
            ))
        if method == "GET" and route == "/api/docs/deploy/handoff-report":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            result = build_deployment_operator_handoff_report_response(get_audit_store(), record_id=params.get("id") or params.get("record_id") or "")
            return json_response(200 if result.get("ok") else 404, result)
        if method == "GET" and route == "/api/docs/deploy/connectors":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            return json_response(200, build_connector_catalog_response())
        if method == "GET" and route == "/api/docs/deploy/connector/profiles":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            try:
                limit = int(params.get("limit", "25") or 25)
            except ValueError:
                limit = 25
            return json_response(200, build_connector_profiles_response(get_audit_store(), site_id=params.get("site_id", ""), connector=params.get("connector", ""), limit=limit))
        if method == "GET" and route == "/api/docs/deploy/connector/dry-runs":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            try:
                limit = int(params.get("limit", "25") or 25)
            except ValueError:
                limit = 25
            return json_response(200, build_connector_dry_run_history_response(get_audit_store(), site_id=params.get("site_id", ""), audit_record_id=params.get("id") or params.get("auditRecordId") or "", profile_id=params.get("profile_id") or params.get("profileId") or "", connector=params.get("connector", ""), limit=limit))
        if method == "GET" and route == "/api/docs/deploy/connector/runbook":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            result = build_connector_runbook_response(get_audit_store(), dry_run_id=params.get("id") or params.get("dry_run_id") or params.get("dryRunId") or "")
            return json_response(200 if result.get("ok") else 404, result)
        if method == "GET" and route == "/api/docs/deploy/connector/dry-run-compare":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            result = build_connector_dry_run_comparison_response(get_audit_store(), left_id=params.get("left_id") or params.get("leftId") or "", right_id=params.get("right_id") or params.get("rightId") or "")
            return json_response(200 if result.get("ok") else 404, result)
        if method == "GET" and route == "/api/docs/deploy/operator-playbooks":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            return json_response(200, build_operator_playbook_catalog_response())
        if method == "GET" and route == "/api/docs/deploy/operator-playbook":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            result = build_operator_release_playbook_response(get_audit_store(), record_id=params.get("id") or params.get("record_id") or "", target=params.get("target", ""))
            return json_response(200 if result.get("ok") else 404, result)
        if method == "GET" and route == "/api/docs/deploy/onboarding-guide":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            return json_response(200, build_onboarding_guide_response(site_id=params.get("site_id", ""), integration=params.get("integration", "sitelet")))
        if method == "GET" and route == "/api/docs/deploy/onboarding-checklist":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            return json_response(200, build_onboarding_checklist_response(site_id=params.get("site_id", ""), integration=params.get("integration", "sitelet")))
        if method == "GET" and route == "/api/docs/deploy/v1-release-summary":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            return json_response(200, build_v1_release_summary_response())
        if method == "POST" and route == "/api/docs/deploy/v1-release-package":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            payload = parse_body(body)
            result = build_v1_release_package_response(confirm=bool(payload.get("confirmV1ReleasePackage")), approved_by=str(payload.get("approvedBy", "")))
            return json_response(200 if result.get("ok") else 409, result)
        if method == "GET" and route == "/api/docs/deploy/archive/integrity":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            result = build_release_archive_integrity_response(get_audit_store(), record_id=params.get("id") or params.get("record_id") or "")
            return json_response(200 if result.get("ok") else 404, result)
        if method == "GET" and route == "/api/docs/deploy/rollback-plan":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            result = build_release_rollback_plan_response(get_audit_store(), record_id=params.get("id") or params.get("record_id") or "", previous_id=params.get("previous_id") or params.get("previousId") or "")
            return json_response(200 if result.get("ok") else 404, result)
        if method == "GET" and route == "/api/docs/deploy/archive":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            try:
                limit = int(params.get("limit", "25") or 25)
            except ValueError:
                limit = 25
            return json_response(200, build_release_archive_index_response(
                get_audit_store(),
                site_id=params.get("site_id", ""),
                limit=limit,
                target=params.get("target", ""),
                environment=params.get("environment", ""),
                locale=params.get("locale", ""),
            ))
        if method == "GET" and route == "/api/docs/deploy/attestation":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            result = build_release_attestation_response(get_audit_store(), record_id=params.get("id") or params.get("record_id") or "")
            return json_response(200 if result.get("ok") else 404, result)
        if method == "GET" and route == "/api/docs/deploy/report/download":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            result = build_release_report_download_response(get_audit_store(), record_id=params.get("id") or params.get("record_id") or "")
            if not result.get("ok"):
                return json_response(404, result)
            return Response(200, result["body"].encode("utf-8"), {
                "Content-Type": "text/markdown; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Easiio-Owner-Token",
                "Content-Disposition": f"attachment; filename={result['fileName']}",
            })
        if method == "GET" and route == "/api/docs/deploy/history":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            limit_raw = params.get("limit", "25")
            try:
                limit = int(limit_raw)
            except ValueError:
                limit = 25
            return json_response(200, build_deployment_history_response(
                get_audit_store(),
                site_id=params.get("site_id", ""),
                limit=limit,
                target=params.get("target", ""),
                environment=params.get("environment", ""),
                locale=params.get("locale", ""),
            ))
        if method == "GET" and route == "/api/docs/deploy/summary":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            try:
                limit = int(params.get("limit", "10") or 10)
            except ValueError:
                limit = 10
            return json_response(200, build_deployment_summary_response(
                get_audit_store(),
                site_id=params.get("site_id", ""),
                limit=limit,
                target=params.get("target", ""),
                environment=params.get("environment", ""),
                locale=params.get("locale", ""),
            ))
        if method == "GET" and route == "/api/docs/deploy/history.csv":
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
            try:
                limit = int(params.get("limit", "500") or 500)
            except ValueError:
                limit = 500
            csv_text = build_deployment_history_csv_response(
                get_audit_store(),
                site_id=params.get("site_id", ""),
                limit=limit,
                target=params.get("target", ""),
                environment=params.get("environment", ""),
                locale=params.get("locale", ""),
            )
            return Response(200, csv_text.encode("utf-8"), {
                "Content-Type": "text/csv; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Easiio-Owner-Token",
                "Content-Disposition": "attachment; filename=easiio-docs-deployment-history.csv",
            })
        if method != "POST":
            return json_response(405, {"ok": False, "error": "method not allowed"})
        payload = parse_body(body)
        protected_post_routes = {
            "/api/docs/doc",
            "/api/docs/doc/delete",
            "/api/docs/sitelet-preview/upload",
            "/api/docs/wordpress/draft-execution",
            "/api/docs/rag/sync",
            "/api/docs/export/package",
            "/api/docs/import/preview",
            "/api/docs/import/execute",
            "/api/docs/bundle/package",
            "/api/docs/deploy/package",
            "/api/docs/deploy/checklist",
            "/api/docs/deploy/approval",
            "/api/docs/deploy/archive",
            "/api/docs/deploy/restore-package",
            "/api/docs/deploy/connector/preflight",
            "/api/docs/deploy/connector/profile",
        }
        if route in protected_post_routes:
            auth_error = require_owner_auth(headers, params)
            if auth_error:
                return auth_error
        if route == "/api/docs/doc":
            doc = store.upsert_doc(payload)
            return json_response(200, {"ok": True, "doc": doc})
        if route == "/api/docs/doc/delete":
            site_id = clean_text(payload.get("site_id"), 100)
            slug = clean_text(payload.get("slug"), 160)
            deleted = store.delete_doc(site_id, slug)
            return json_response(200, {"ok": True, "site_id": site_id, "slug": slug, "deleted": deleted})
        if route == "/api/docs/sitelet-preview/upload":
            if payload.get("confirmSiteletUpload") is not True:
                return json_response(409, {
                    "ok": False,
                    "error": "confirmSiteletUpload is required before uploading to Sitelet",
                    "requiresUploadApproval": True,
                    "uploadBlocked": True,
                })
            sitelet_payload = payload.get("siteletPayload")
            if not isinstance(sitelet_payload, dict):
                sitelet_payload = build_sitelet_preview_payload(
                    store,
                    clean_text(payload.get("site_id"), 100),
                    slug=payload.get("slug", ""),
                    target=payload.get("target", "sitelet"),
                    status=payload.get("status", "published"),
                    visibility=payload.get("visibility", "public"),
                )
            result = upload_sitelet_payload(sitelet_payload)
            return json_response(200, {
                "ok": True,
                "exportType": "easiio-docs-sitelet-preview-upload-result",
                "requiresUploadApproval": True,
                "uploadBlocked": False,
                **result,
            })
        if route == "/api/docs/wordpress/draft-execution":
            execution = build_wordpress_draft_execution(store, payload)
            return json_response(200 if execution.get("ok") else 409, execution)
        if route == "/api/docs/rag/sync":
            result = sync_docs_to_chatbot_rag(store, payload)
            return json_response(200 if result.get("ok") else 409, result)
        if route == "/api/docs/export/package":
            result = build_export_package(store, payload)
            return json_response(200 if result.get("ok") else 409, result)
        if route == "/api/docs/import/preview":
            result = build_import_preview(store, payload)
            return json_response(200, result)
        if route == "/api/docs/import/execute":
            result = execute_import(store, payload)
            return json_response(200 if result.get("ok") else 409, result)
        if route == "/api/docs/bundle/package":
            result = build_portable_bundle_package(store, payload)
            return json_response(200 if result.get("ok") else 409, result)
        if route == "/api/docs/deploy/package":
            # confirmDeploymentPackage is validated inside docs_deploy before any ZIP is written.
            result = build_deployment_handoff_package(store, payload, audit_store=get_audit_store())
            return json_response(200 if result.get("ok") else 409, result)
        if route == "/api/docs/deploy/checklist":
            result = build_deployment_checklist_response(get_audit_store(), payload)
            return json_response(200 if result.get("ok") else (409 if result.get("packageLocked") else 404), result)
        if route == "/api/docs/deploy/approval":
            result = build_deployment_approval_response(get_audit_store(), payload)
            return json_response(200 if result.get("ok") else 404, result)
        if route == "/api/docs/deploy/archive":
            result = build_release_archive_response(get_audit_store(), payload)
            return json_response(200 if result.get("ok") else (409 if result.get("archiveBlocked") or result.get("requiresArchiveConfirmation") else 404), result)
        if route == "/api/docs/deploy/restore-package":
            result = build_release_restore_package_response(get_audit_store(), payload)
            return json_response(200 if result.get("ok") else (409 if result.get("restoreBlocked") or result.get("requiresRestoreConfirmation") else 404), result)
        if route == "/api/docs/deploy/connector/preflight":
            result = build_connector_preflight_response(get_audit_store(), payload)
            return json_response(200 if result.get("ok") else (409 if result.get("connectorDryRunBlocked") or result.get("requiresConnectorDryRunConfirmation") else 404), result)
        if route == "/api/docs/deploy/connector/profile":
            result = build_connector_profile_save_response(get_audit_store(), payload)
            return json_response(200 if result.get("ok") else (409 if result.get("connectorProfileBlocked") or result.get("requiresConnectorProfileConfirmation") else 404), result)
        return json_response(404, {"ok": False, "error": "not found"})
    except ValueError as exc:
        return json_response(400, {"ok": False, "error": str(exc)})
    except Exception as exc:
        return json_response(500, {"ok": False, "error": f"server error: {exc}"})


class DocsHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.respond(handle_request("OPTIONS", self.path))

    def do_GET(self):
        self.respond(handle_request("GET", self.path, headers=dict(self.headers)))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        self.respond(handle_request("POST", self.path, self.rfile.read(length), headers=dict(self.headers)))

    def respond(self, response: Response):
        self.send_response(response.status)
        for key, value in response.headers.items():
            self.send_header(key, value)
        self.end_headers()
        if response.body:
            self.wfile.write(response.body)

    def log_message(self, fmt, *args):
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Easiio Docs Module backend")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8110)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), DocsHandler)
    print(f"{SERVICE_NAME} listening on http://{args.host}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
