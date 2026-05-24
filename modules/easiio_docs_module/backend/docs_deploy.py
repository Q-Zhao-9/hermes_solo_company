from __future__ import annotations

import json
import time
import zipfile
from pathlib import Path
from typing import Any

from docs_audit import DocsAuditStore
from docs_db import DocsStore, clean_slug, clean_text
from docs_exporters import build_export_files, build_export_preview

ROOT = Path(__file__).resolve().parents[1]
DEPLOYMENTS_DIR = ROOT / "dist" / "easiio-docs-deployments"  # dist/easiio-docs-deployments

DEPLOYMENT_TARGETS = {"static-html", "sitelet", "wordpress", "nextjs-mdx", "docusaurus", "mkdocs", "hugo", "vitepress"}
ENVIRONMENTS = {"local", "preview", "staging", "production"}


def _deployment_target(value: Any) -> str:
    target = clean_text(value or "static-html", 80)
    if target not in DEPLOYMENT_TARGETS:
        raise ValueError(f"unsupported deployment target: {target}")
    return target


def _environment(value: Any) -> str:
    env = clean_text(value or "preview", 40).lower()
    return env if env in ENVIRONMENTS else "preview"


def _export_target_for_deployment(target: str) -> str:
    if target == "sitelet":
        return "static-html"
    if target == "wordpress":
        return "static-html"
    return target


def _deployment_manifest(site_id: str, deployment_target: str, environment: str, export_preview: dict[str, Any], payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    file_paths = list(export_preview.get("filePaths") or [])
    return {
        "source": "easiio-docs-module",
        "exportType": "easiio-docs-deployment-handoff-manifest",
        "site_id": site_id,
        "deploymentTarget": deployment_target,
        "environment": environment,
        "locale": export_preview.get("locale") or payload.get("locale") or "all",
        "status": payload.get("status") or "published",
        "visibility": payload.get("visibility") or "public",
        "generated_at": int(time.time()),
        "documentCount": export_preview.get("documentCount", 0),
        "fileCount": len(file_paths) + 1,
        "filePaths": file_paths + ["easiio-docs-deployment-manifest.json"],
        "operatorChecklist": deployment_checklist(deployment_target, environment),
        "handoffNotes": [
            "Review generated files before deploying.",
            "Deploy private/internal/draft docs only through a protected owner workflow.",
            "This package does not push to external hosting, DNS, WordPress, or Sitelet automatically.",
        ],
    }


def deployment_checklist(deployment_target: str, environment: str) -> list[str]:
    checklist = [
        "Review generated docs files and deployment manifest before approving handoff.",
        f"Confirm target environment is {environment}.",
        "Confirm only intended published/public docs are included by default.",
        "Run the target platform build or preview command outside this module before publishing.",
    ]
    if deployment_target == "sitelet":
        checklist.append("Use Sitelet preview/upload workflow only after reviewing the generated payload and URL.")
    elif deployment_target == "wordpress":
        checklist.append("Create WordPress drafts first; do not publish without separate human approval.")
    elif deployment_target == "static-html":
        checklist.append("Upload static files to the approved hosting bucket or static server after review.")
    else:
        checklist.append(f"Copy files into the {deployment_target} project and run its normal build/deploy pipeline.")
    return checklist


def build_deployment_handoff_preview(store: DocsStore, site_id: str, *, target: str = "static-html", environment: str = "preview", status: str = "published", visibility: str = "public", locale: str = "") -> dict[str, Any]:
    site_id = clean_text(site_id, 100)
    if not site_id:
        raise ValueError("site_id is required")
    deployment_target = _deployment_target(target)
    env = _environment(environment)
    export_target = _export_target_for_deployment(deployment_target)
    export_preview = build_export_preview(store, site_id, target=export_target, status=status, visibility=visibility, locale=locale)
    files = list(export_preview.get("files") or [])
    manifest = _deployment_manifest(site_id, deployment_target, env, export_preview, {"status": status, "visibility": visibility, "locale": locale})
    files.append({"path": "easiio-docs-deployment-manifest.json", "content": json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"})
    return {
        "ok": True,
        "exportType": "easiio-docs-deployment-handoff-preview",
        "site_id": site_id,
        "deploymentTarget": deployment_target,
        "exportTarget": export_target,
        "environment": env,
        "locale": export_preview.get("locale", "all"),
        "documentCount": export_preview.get("documentCount", 0),
        "fileCount": len(files),
        "files": files,
        "filePaths": [file["path"] for file in files],
        "manifest": manifest,
        "checklist": deployment_checklist(deployment_target, env),
        "requiresDeploymentApproval": True,
        "deploymentBlocked": True,
        "packageInstructions": {
            "endpoint": "POST /api/docs/deploy/package",
            "requiredFlag": "confirmDeploymentPackage:true",
            "note": "Review the deployment handoff preview before writing a local deployment ZIP.",
        },
    }


def _safe_package_name(site_id: str, target: str, environment: str) -> str:
    # Include a millisecond timestamp so repeated reviewed releases do not overwrite
    # earlier local handoff ZIPs that may later be archived/restored by Phase 18/19.
    stamp = int(time.time() * 1000)
    return f"{clean_slug(site_id) or 'docs'}-{target}-{environment}-{stamp}-deployment-handoff.zip"


def build_deployment_handoff_package(store: DocsStore, payload: dict[str, Any], audit_store: DocsAuditStore | None = None) -> dict[str, Any]:
    if payload.get("confirmDeploymentPackage") is not True:
        return {
            "ok": False,
            "error": "confirmDeploymentPackage is required before writing a deployment handoff ZIP",
            "requiresDeploymentApproval": True,
            "deploymentBlocked": True,
        }
    site_id = clean_text(payload.get("site_id"), 100)
    deployment_target = _deployment_target(payload.get("target") or payload.get("deploymentTarget") or "static-html")
    env = _environment(payload.get("environment") or "preview")
    preview = build_deployment_handoff_preview(
        store,
        site_id,
        target=deployment_target,
        environment=env,
        status=payload.get("status") or "published",
        visibility=payload.get("visibility") or "public",
        locale=payload.get("locale") or "",
    )
    DEPLOYMENTS_DIR.mkdir(parents=True, exist_ok=True)
    package_path = DEPLOYMENTS_DIR / _safe_package_name(site_id, deployment_target, env)
    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file in preview["files"]:
            archive.writestr(file["path"], file["content"])
    result = {
        "ok": True,
        "exportType": "easiio-docs-deployment-handoff-package",
        "site_id": site_id,
        "deploymentTarget": deployment_target,
        "exportTarget": preview.get("exportTarget"),
        "environment": env,
        "locale": preview.get("locale", "all"),
        "documentCount": preview.get("documentCount", 0),
        "fileCount": preview.get("fileCount", 0),
        "filePaths": preview.get("filePaths", []),
        "packagePath": str(package_path),
        "packageSize": package_path.stat().st_size,
        "manifest": preview.get("manifest", {}),
        "approvedBy": clean_text(payload.get("approvedBy") or "", 120),
        "requiresDeploymentApproval": True,
        "deploymentBlocked": False,
        "checklist": preview.get("checklist", []),
        "auditRecorded": False,
        "auditRecordId": 0,
    }
    if audit_store is not None:
        audit_record = audit_store.record_deployment_package(result)
        result["auditRecorded"] = True
        result["auditRecordId"] = audit_record.get("id", 0)
    return result
