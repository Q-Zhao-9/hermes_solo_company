from __future__ import annotations

import json
import re
import time
import zipfile
from pathlib import Path
from typing import Any

from docs_db import DocsStore, clean_framework_targets, clean_list, clean_slug, clean_text

ROOT = Path(__file__).resolve().parents[1]
BUNDLES_DIR = ROOT / "dist" / "easiio-docs-bundles"

SUPPORTED_IMPORT_FORMATS = {"markdown-folder", "docusaurus", "mkdocs", "vitepress", "hugo", "easiio-bundle"}
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
TITLE_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def _source_format(value: Any) -> str:
    source_format = clean_text(value or "markdown-folder", 80)
    if source_format not in SUPPORTED_IMPORT_FORMATS:
        raise ValueError(f"unsupported import source_format: {source_format}")
    return source_format


def _clean_status(value: Any) -> str:
    status = clean_text(value or "draft", 40)
    return status if status in {"draft", "published", "archived"} else "draft"


def _clean_visibility(value: Any) -> str:
    visibility = clean_text(value or "private", 40)
    return visibility if visibility in {"public", "private", "login_required", "internal"} else "private"


def _safe_zip_name(site_id: str, suffix: str) -> str:
    return f"{clean_slug(site_id) or 'docs'}-{suffix}.zip"


def _parse_frontmatter_value(raw: str) -> Any:
    value = raw.strip()
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        try:
            return json.loads(value.replace("'", '"'))
        except Exception:
            return [item.strip().strip('"\'') for item in value.strip("[]").split(",") if item.strip()]
    return value.strip('"\'')


def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER_RE.match(content or "")
    if not match:
        return {}, content or ""
    meta: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = _parse_frontmatter_value(value)
    return meta, content[match.end():]


def _slug_from_path(path: str) -> str:
    clean_path = clean_text(path, 300).replace("\\", "/")
    name = clean_path.rsplit("/", 1)[-1]
    for ext in (".mdx", ".md", ".markdown", ".html", ".txt"):
        if name.lower().endswith(ext):
            name = name[:-len(ext)]
            break
    if name in {"index", "_index", "readme"}:
        parts = [part for part in clean_path.split("/") if part]
        if len(parts) >= 2:
            name = parts[-2]
    return clean_slug(name)


def _title_from_content(slug: str, content: str, meta: dict[str, Any]) -> str:
    if meta.get("title"):
        return clean_text(meta.get("title"), 300)
    match = TITLE_RE.search(content or "")
    if match:
        return clean_text(match.group(1), 300)
    return clean_text(slug.replace("-", " ").title(), 300)


def _locale_from_path(path: str) -> str:
    # localized import: detect language folders like en/docs/page.md or es/guide.md
    clean_path = clean_text(path, 300).replace("\\", "/")
    parts = [part.lower() for part in clean_path.split("/") if part]
    if parts and re.match(r"^[a-z]{2}(-[a-z0-9]{2,8})?$", parts[0]):
        return parts[0]
    if "i18n" in parts:
        idx = parts.index("i18n")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return ""


def _normalize_import_file(file: dict[str, Any], site_id: str, source_format: str, payload: dict[str, Any], store: DocsStore) -> dict[str, Any] | None:
    path = clean_text(file.get("path"), 300)
    content = clean_text(file.get("content"), 500000)
    if not path or not content:
        return None
    if not path.lower().endswith((".md", ".mdx", ".markdown", ".html", ".txt")):
        return None
    meta, body = _parse_frontmatter(content)
    slug = clean_slug(meta.get("slug") or file.get("slug") or _slug_from_path(path))
    if not slug:
        return None
    content_format = "mdx" if path.lower().endswith(".mdx") else "markdown"
    if path.lower().endswith(".html"):
        content_format = "html"
    if path.lower().endswith(".txt"):
        content_format = "text"
    doc = {
        "site_id": site_id,
        "slug": slug,
        "title": _title_from_content(slug, body, meta),
        "summary": clean_text(meta.get("description") or meta.get("summary") or file.get("summary"), 1200),
        "content": body.strip() or content,
        "content_format": clean_text(meta.get("content_format") or content_format, 40),
        "status": _clean_status(meta.get("status") or payload.get("default_status")),
        "visibility": _clean_visibility(meta.get("visibility") or payload.get("default_visibility")),
        "category": clean_text(meta.get("category") or payload.get("default_category") or source_format, 120),
        "tags": clean_list(meta.get("tags") if isinstance(meta.get("tags"), list) else payload.get("default_tags"), limit=30, item_limit=80),
        "version_label": clean_text(meta.get("version_label") or payload.get("version_label"), 80),
        "locale": clean_text(meta.get("locale") or file.get("locale") or _locale_from_path(path) or payload.get("locale") or "en", 20).lower().replace("_", "-"),
        "framework_targets": clean_framework_targets(meta.get("framework_targets") if isinstance(meta.get("framework_targets"), list) else payload.get("framework_targets")),
        "rag_enabled": bool(meta.get("rag_enabled") if "rag_enabled" in meta else payload.get("rag_enabled", False)),
        "changed_by": clean_text(payload.get("approvedBy") or payload.get("changed_by") or "phase10-import", 200),
    }
    existing = store.get_doc(site_id, slug)
    return {
        "path": path,
        "slug": slug,
        "title": doc["title"],
        "status": doc["status"],
        "visibility": doc["visibility"],
        "category": doc["category"],
        "content_format": doc["content_format"],
        "locale": doc["locale"],
        "conflict": bool(existing),
        "action": "update" if existing else "create",
        "doc": doc,
    }


def _import_docs_from_payload(store: DocsStore, payload: dict[str, Any]) -> tuple[str, str, list[dict[str, Any]]]:
    site_id = clean_text(payload.get("site_id"), 100)
    if not site_id:
        raise ValueError("site_id is required")
    source_format = _source_format(payload.get("source_format"))
    files = payload.get("files")
    docs: list[dict[str, Any]] = []
    if source_format == "easiio-bundle" and isinstance(payload.get("bundle"), dict):
        bundle = payload["bundle"]
        files = []
        for doc in bundle.get("documents", []):
            if isinstance(doc, dict):
                docs.append({
                    "path": f"documents/{doc.get('slug')}.md",
                    "slug": clean_slug(doc.get("slug")),
                    "title": clean_text(doc.get("title"), 300),
                    "status": _clean_status(doc.get("status") or payload.get("default_status")),
                    "visibility": _clean_visibility(doc.get("visibility") or payload.get("default_visibility")),
                    "category": clean_text(doc.get("category"), 120),
                    "content_format": clean_text(doc.get("content_format") or "markdown", 40),
                    "conflict": bool(store.get_doc(site_id, doc.get("slug", ""))),
                    "action": "update" if store.get_doc(site_id, doc.get("slug", "")) else "create",
                    "doc": {**doc, "site_id": site_id, "changed_by": clean_text(payload.get("approvedBy") or "phase10-bundle-import", 200)},
                })
    if files is None:
        files = []
    if not isinstance(files, list):
        raise ValueError("files must be a list")
    for file in files:
        if isinstance(file, dict):
            normalized = _normalize_import_file(file, site_id, source_format, payload, store)
            if normalized:
                docs.append(normalized)
    return site_id, source_format, docs


def build_import_preview(store: DocsStore, payload: dict[str, Any]) -> dict[str, Any]:
    site_id, source_format, docs = _import_docs_from_payload(store, payload)
    conflicts = [doc for doc in docs if doc.get("conflict")]
    return {
        "ok": True,
        "exportType": "easiio-docs-import-preview",
        "site_id": site_id,
        "source_format": source_format,
        "documentCount": len(docs),
        "conflictCount": len(conflicts),
        "documents": [{k: v for k, v in doc.items() if k != "doc"} for doc in docs],
        "requiresImportApproval": True,
        "importBlocked": True,
        "importInstructions": {
            "endpoint": "POST /api/docs/import/execute",
            "requiredFlag": "confirmImport:true",
            "note": "Review detected documents and slug conflicts before importing.",
        },
    }


def execute_import(store: DocsStore, payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("confirmImport") is not True:
        return {"ok": False, "error": "confirmImport is required before importing docs", "requiresImportApproval": True, "importBlocked": True}
    site_id, source_format, docs = _import_docs_from_payload(store, payload)
    imported = []
    for item in docs:
        doc = dict(item["doc"])
        doc["site_id"] = site_id
        imported_doc = store.upsert_doc(doc)
        imported.append({"slug": imported_doc.get("slug"), "title": imported_doc.get("title"), "action": item.get("action")})
    return {
        "ok": True,
        "exportType": "easiio-docs-import-result",
        "site_id": site_id,
        "source_format": source_format,
        "importedCount": len(imported),
        "documents": imported,
        "requiresImportApproval": True,
        "importBlocked": False,
        "approvedBy": clean_text(payload.get("approvedBy"), 120),
    }


def _bundle_docs(store: DocsStore, site_id: str, *, status: str = "published", visibility: str = "public", locale: str = "") -> list[dict[str, Any]]:
    docs = []
    for doc in store.list_docs(site_id, status=status, visibility=visibility, locale=locale):
        full = store.get_doc(site_id, doc.get("slug", "")) or doc
        docs.append(full)
    docs.sort(key=lambda d: (str(d.get("category") or ""), str(d.get("title") or ""), str(d.get("slug") or "")))
    return docs


def _portable_bundle(store: DocsStore, site_id: str, *, status: str = "published", visibility: str = "public", locale: str = "") -> dict[str, Any]:
    site_id = clean_text(site_id, 100)
    if not site_id:
        raise ValueError("site_id is required")
    locale = store.clean_locale(locale)
    docs = _bundle_docs(store, site_id, status=status, visibility=visibility, locale=locale)
    return {
        "schema": "easiio-docs-portable-bundle/v1",
        "source": "easiio-docs-module",
        "generated_at": int(time.time()),
        "site_id": site_id,
        "locale": locale or "all",
        "space": store.get_space_summary(site_id),
        "documents": docs,
    }


def build_portable_bundle_preview(store: DocsStore, site_id: str, *, status: str = "published", visibility: str = "public", locale: str = "") -> dict[str, Any]:
    bundle = _portable_bundle(store, site_id, status=status, visibility=visibility, locale=locale)
    docs = bundle["documents"]
    return {
        "ok": True,
        "exportType": "easiio-docs-portable-bundle-preview",
        "site_id": bundle["site_id"],
        "locale": bundle.get("locale", "all"),
        "documentCount": len(docs),
        "documents": [{"slug": doc.get("slug"), "title": doc.get("title"), "status": doc.get("status"), "visibility": doc.get("visibility")} for doc in docs],
        "bundle": bundle,
        "requiresBundleApproval": True,
        "bundleBlocked": True,
        "bundleInstructions": {
            "endpoint": "POST /api/docs/bundle/package",
            "requiredFlag": "confirmBundlePackage:true",
            "note": "Review bundle contents before writing a local portable ZIP.",
        },
    }


def build_portable_bundle_package(store: DocsStore, payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("confirmBundlePackage") is not True:
        return {"ok": False, "error": "confirmBundlePackage is required before writing a portable bundle", "requiresBundleApproval": True, "bundleBlocked": True}
    site_id = clean_text(payload.get("site_id"), 100)
    bundle = _portable_bundle(store, site_id, status=payload.get("status") or "published", visibility=payload.get("visibility") or "public", locale=payload.get("locale") or "")
    BUNDLES_DIR.mkdir(parents=True, exist_ok=True)
    package_path = BUNDLES_DIR / _safe_zip_name(site_id, "portable-bundle")
    files = [
        {"path": "easiio-docs-bundle.json", "content": json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=True) + "\n"},
        {"path": "README.md", "content": f"# Easiio Docs Portable Bundle — {site_id}\n\nDocuments: {len(bundle['documents'])}\n\nImport with POST /api/docs/import/preview then POST /api/docs/import/execute.\n"},
    ]
    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            zf.writestr(file["path"], file["content"])
    return {
        "ok": True,
        "exportType": "easiio-docs-portable-bundle-package",
        "site_id": site_id,
        "documentCount": len(bundle["documents"]),
        "fileCount": len(files),
        "filePaths": [file["path"] for file in files],
        "packagePath": str(package_path),
        "packageSize": package_path.stat().st_size,
        "requiresBundleApproval": True,
        "bundleBlocked": False,
        "approvedBy": clean_text(payload.get("approvedBy"), 120),
    }
