from __future__ import annotations

import json
import time
import zipfile
from pathlib import Path
from typing import Any

from docs_db import DocsStore, clean_slug, clean_text
from docs_sitelet import render_docs_space_html, render_single_doc_html

ROOT = Path(__file__).resolve().parents[1]
EXPORTS_DIR = ROOT / "dist" / "easiio-docs-exports"

EXPORT_TARGETS = {
    "nextjs-mdx": {
        "label": "Next.js MDX",
        "doc_dir": "content/docs",
        "extension": ".mdx",
        "config_files": ["README.md"],
    },
    "docusaurus": {
        "label": "Docusaurus",
        "doc_dir": "docs",
        "extension": ".md",
        "config_files": ["sidebars.js", "README.md"],
    },
    "mkdocs": {
        "label": "MkDocs",
        "doc_dir": "docs",
        "extension": ".md",
        "config_files": ["mkdocs.yml", "README.md"],
    },
    "hugo": {
        "label": "Hugo",
        "doc_dir": "content/docs",
        "extension": ".md",
        "config_files": ["config.toml", "README.md"],
    },
    "vitepress": {
        "label": "VitePress",
        "doc_dir": "docs",
        "extension": ".md",
        "config_files": ["docs/.vitepress/config.js", "README.md"],
    },
    "static-html": {
        "label": "Static HTML",
        "doc_dir": "",
        "extension": ".html",
        "config_files": ["index.html", "assets/easiio-docs-preview.css", "README.md"],
    },
}


def _target(value: Any) -> str:
    target = clean_text(value or "nextjs-mdx", 80)
    if target not in EXPORT_TARGETS:
        raise ValueError(f"unsupported export target: {target}")
    return target


def _matches_target(doc: dict[str, Any], target: str) -> bool:
    targets = doc.get("framework_targets") or []
    return target in targets or "all" in targets


def _exportable_docs(store: DocsStore, site_id: str, target: str, *, status: str = "published", visibility: str = "public", locale: str = "") -> list[dict[str, Any]]:
    site_id = clean_text(site_id, 100)
    if not site_id:
        raise ValueError("site_id is required")
    locale = store.clean_locale(locale)
    docs = store.list_docs(site_id, status=status, visibility=visibility, locale=locale)
    full_docs: list[dict[str, Any]] = []
    for doc in docs:
        if _matches_target(doc, target):
            full = store.get_doc(site_id, doc.get("slug", "")) or doc
            full_docs.append(full)
    full_docs.sort(key=lambda d: (str(d.get("category") or ""), str(d.get("title") or ""), str(d.get("slug") or "")))
    return full_docs


def _frontmatter(doc: dict[str, Any], target: str) -> str:
    tags = doc.get("tags") if isinstance(doc.get("tags"), list) else []
    lines = [
        "---",
        f"title: {json.dumps(doc.get('title') or doc.get('slug') or '')}",
        f"description: {json.dumps(doc.get('summary') or '')}",
        f"slug: {json.dumps('/' + clean_slug(doc.get('slug')))}",
        f"sidebar_label: {json.dumps(doc.get('title') or doc.get('slug') or '')}",
        f"category: {json.dumps(doc.get('category') or 'Docs')}",
        f"tags: {json.dumps(tags, ensure_ascii=False)}",
        f"locale: {json.dumps(doc.get('locale') or 'en')}",
        f"easiio_site_id: {json.dumps(doc.get('site_id') or '')}",
        f"easiio_target: {json.dumps(target)}",
        "---",
        "",
    ]
    return "\n".join(lines)


def _markdown_body(doc: dict[str, Any], target: str) -> str:
    content = str(doc.get("content") or "")
    content_format = str(doc.get("content_format") or "markdown")
    if content_format == "html":
        content = "<div>\n" + content + "\n</div>"
    elif content_format == "text":
        content = "```text\n" + content + "\n```"
    return _frontmatter(doc, target) + content.strip() + "\n"


def _localized_path(path: str, target: str, locale: str = "") -> str:
    locale = clean_text(locale, 20).lower().replace("_", "-")
    if not locale or locale == "en":
        return path
    if target == "docusaurus" and path.startswith("docs/"):
        return path.replace("docs/", f"i18n/{locale}/docusaurus-plugin-content-docs/current/", 1)
    if target == "mkdocs" and path.startswith("docs/"):
        return path.replace("docs/", f"docs/{locale}/", 1)
    if target == "vitepress" and path.startswith("docs/"):
        return path.replace("docs/", f"docs/{locale}/", 1)
    if target == "hugo" and path.startswith("content/docs/"):
        return path.replace("content/docs/", f"content/{locale}/docs/", 1)
    if target == "nextjs-mdx" and path.startswith("content/docs/"):
        return path.replace("content/docs/", f"content/docs/{locale}/", 1)
    if target == "static-html":
        return f"{locale}/{path}"
    return path


def _doc_path(doc: dict[str, Any], target: str, locale: str = "") -> str:
    slug = clean_slug(doc.get("slug"))
    meta = EXPORT_TARGETS[target]
    if target == "static-html":
        return _localized_path(f"{slug}.html", target, locale or doc.get("locale", ""))
    return _localized_path(f"{meta['doc_dir']}/{slug}{meta['extension']}", target, locale or doc.get("locale", ""))


def _readme(site_id: str, target: str, docs: list[dict[str, Any]]) -> str:
    return f"""# Easiio Docs Export — {site_id}

Target: `{target}`
Generated by: Easiio Docs Module Phase 6 framework exporter
Document count: {len(docs)}

## Safety

This package only includes `published` + `public` documents that explicitly target `{target}`.
Private, internal, login-required, draft, and archived documents are excluded by default.

## Files

""" + "\n".join(f"- `{_doc_path(doc, target)}` — {doc.get('title') or doc.get('slug')}" for doc in docs) + "\n"


def _config_files(site_id: str, target: str, docs: list[dict[str, Any]], summary: dict[str, Any]) -> list[dict[str, str]]:
    files = [{"path": "README.md", "content": _readme(site_id, target, docs)}]
    if target == "docusaurus":
        items = ",\n      ".join(json.dumps(clean_slug(doc.get("slug"))) for doc in docs)
        files.append({"path": "sidebars.js", "content": "module.exports = {\n  docs: [\n      " + items + "\n  ],\n};\n"})
    elif target == "mkdocs":
        nav = "\n".join(f"    - {doc.get('title') or doc.get('slug')}: {_doc_path(doc, target)}" for doc in docs)
        files.append({"path": "mkdocs.yml", "content": f"site_name: {site_id} Documentation\ndocs_dir: docs\nnav:\n  - Home: index.md\n  - Docs:\n{nav or '    - No docs: index.md'}\n"})
        files.append({"path": "docs/index.md", "content": f"# {site_id} Documentation\n\n" + "\n".join(f"- [{doc.get('title')}]({clean_slug(doc.get('slug'))}.md)" for doc in docs) + "\n"})
    elif target == "hugo":
        files.append({"path": "config.toml", "content": f"baseURL = '/'\ntitle = '{site_id} Documentation'\n[params]\n  source = 'easiio-docs-module'\n"})
        files.append({"path": "content/docs/_index.md", "content": _frontmatter({"title": f"{site_id} Documentation", "summary": "Documentation exported from Easiio Docs Module", "slug": "docs", "category": "Docs", "tags": [], "site_id": site_id}, target) + f"# {site_id} Documentation\n"})
    elif target == "vitepress":
        sidebar = ",\n          ".join("{ text: " + json.dumps(doc.get('title') or doc.get('slug')) + ", link: '/" + clean_slug(doc.get('slug')) + "' }" for doc in docs)
        files.append({"path": "docs/.vitepress/config.js", "content": "export default {\n  title: " + json.dumps(f"{site_id} Documentation") + ",\n  themeConfig: {\n    sidebar: [\n          " + sidebar + "\n    ]\n  }\n};\n"})
        files.append({"path": "docs/index.md", "content": f"# {site_id} Documentation\n\n" + "\n".join(f"- [{doc.get('title')}]({clean_slug(doc.get('slug'))}.md)" for doc in docs) + "\n"})
    elif target == "nextjs-mdx":
        files.append({"path": "content/docs/index.mdx", "content": f"# {site_id} Documentation\n\n" + "\n".join(f"- [{doc.get('title')}](/docs/{clean_slug(doc.get('slug'))})" for doc in docs) + "\n"})
    elif target == "static-html":
        from docs_sitelet import PREVIEW_CSS
        files.append({"path": "index.html", "content": render_docs_space_html(site_id, docs, summary, target=target)})
        files.append({"path": "assets/easiio-docs-preview.css", "content": PREVIEW_CSS})
    return files


def _manifest(site_id: str, target: str, docs: list[dict[str, Any]], files: list[dict[str, str]], locale: str = "") -> dict[str, Any]:
    return {
        "site_id": site_id,
        "target": target,
        "locale": locale or "all",
        "source": "easiio-docs-module",
        "exportType": "easiio-docs-framework-export",
        "generated_at": int(time.time()),
        "document_count": len(docs),
        "file_count": len(files) + 1,
        "documents": [{"slug": doc.get("slug"), "title": doc.get("title"), "locale": doc.get("locale") or "en", "path": _doc_path(doc, target, locale), "localizedPath": _doc_path(doc, target, locale)} for doc in docs],
    }


def build_export_files(store: DocsStore, site_id: str, *, target: str, status: str = "published", visibility: str = "public", locale: str = "") -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    target = _target(target)
    site_id = clean_text(site_id, 100)
    locale = store.clean_locale(locale)
    docs = _exportable_docs(store, site_id, target, status=status, visibility=visibility, locale=locale)
    summary = store.get_space_summary(site_id)
    files: list[dict[str, str]] = []
    for doc in docs:
        if target == "static-html":
            content = render_single_doc_html(doc, docs)
        else:
            content = _markdown_body(doc, target)
        files.append({"path": _doc_path(doc, target, locale), "content": content})
    files.extend(_config_files(site_id, target, docs, summary))
    files.append({"path": "easiio-docs-export-manifest.json", "content": json.dumps(_manifest(site_id, target, docs, files, locale=locale), ensure_ascii=False, indent=2, sort_keys=True) + "\n"})
    return files, docs


def build_export_preview(store: DocsStore, site_id: str, *, target: str = "nextjs-mdx", status: str = "published", visibility: str = "public", locale: str = "", fallback_locale: str = "en") -> dict[str, Any]:
    target = _target(target)
    site_id = clean_text(site_id, 100)
    locale = store.clean_locale(locale)
    files, docs = build_export_files(store, site_id, target=target, status=status, visibility=visibility, locale=locale)
    return {
        "ok": True,
        "exportType": "easiio-docs-framework-export-preview",
        "site_id": site_id,
        "target": target,
        "locale": locale or "all",
        "fallback_locale": store.clean_locale(fallback_locale, "en"),
        "documentCount": len(docs),
        "fileCount": len(files),
        "files": files,
        "filePaths": [file["path"] for file in files],
        "requiresExportApproval": True,
        "packageBlocked": True,
        "packageInstructions": {
            "endpoint": "POST /api/docs/export/package",
            "requiredFlag": "confirmExportPackage:true",
            "note": "Review generated files before writing a local ZIP package.",
        },
    }


def _safe_package_name(site_id: str, target: str) -> str:
    return f"{clean_slug(site_id) or 'docs'}-{target}.zip"


def build_export_package(store: DocsStore, payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("confirmExportPackage") is not True:
        return {
            "ok": False,
            "error": "confirmExportPackage is required before writing an export ZIP",
            "requiresExportApproval": True,
            "packageBlocked": True,
        }
    target = _target(payload.get("target") or "nextjs-mdx")
    site_id = clean_text(payload.get("site_id"), 100)
    files, docs = build_export_files(
        store,
        site_id,
        target=target,
        status=payload.get("status") or "published",
        visibility=payload.get("visibility") or "public",
        locale=payload.get("locale") or "",
    )
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    package_path = EXPORTS_DIR / _safe_package_name(site_id, target)
    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            zf.writestr(file["path"], file["content"])
    return {
        "ok": True,
        "exportType": "easiio-docs-framework-export-package",
        "site_id": site_id,
        "target": target,
        "documentCount": len(docs),
        "fileCount": len(files),
        "filePaths": [file["path"] for file in files],
        "packagePath": str(package_path),
        "packageSize": package_path.stat().st_size,
        "requiresExportApproval": True,
        "packageBlocked": False,
        "approvedBy": clean_text(payload.get("approvedBy"), 120),
    }
