from __future__ import annotations

import html
import re
from typing import Any

from docs_db import DocsStore, clean_slug, clean_text

PREVIEW_CSS_PATH = "/assets/easiio-docs-preview.css"

PREVIEW_CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: #0f172a;
  background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 42%, #ffffff 100%);
}
a { color: #2563eb; text-decoration: none; }
a:hover { text-decoration: underline; }
.docs-preview-shell { max-width: 1120px; margin: 0 auto; padding: 42px 22px 64px; }
.docs-preview-hero {
  padding: 32px;
  border: 1px solid #dbeafe;
  border-radius: 28px;
  background: rgba(255,255,255,0.88);
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.10);
}
.docs-preview-eyebrow { color: #2563eb; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; font-size: 12px; }
.docs-preview-hero h1 { margin: 10px 0 10px; font-size: clamp(34px, 6vw, 62px); line-height: 1; }
.docs-preview-hero p { max-width: 760px; color: #475569; font-size: 18px; line-height: 1.65; }
.docs-preview-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 18px; margin-top: 28px; }
.docs-preview-card {
  display: block;
  padding: 22px;
  border: 1px solid #e2e8f0;
  border-radius: 22px;
  background: #fff;
  box-shadow: 0 16px 45px rgba(15, 23, 42, 0.06);
}
.docs-preview-card h2 { margin: 0 0 8px; font-size: 20px; }
.docs-preview-card p { margin: 0 0 14px; color: #64748b; line-height: 1.55; }
.docs-preview-meta { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
.docs-preview-pill { border-radius: 999px; padding: 6px 10px; background: #eff6ff; color: #1d4ed8; font-size: 12px; font-weight: 700; }
.docs-preview-layout { display: grid; grid-template-columns: minmax(210px, 280px) 1fr; gap: 24px; margin-top: 28px; }
.docs-preview-nav, .docs-preview-article {
  border: 1px solid #e2e8f0;
  border-radius: 24px;
  background: rgba(255,255,255,0.92);
  box-shadow: 0 16px 45px rgba(15, 23, 42, 0.06);
}
.docs-preview-nav { padding: 18px; align-self: start; position: sticky; top: 16px; }
.docs-preview-nav h2 { margin: 0 0 12px; font-size: 16px; }
.docs-preview-nav a { display: block; padding: 9px 0; color: #334155; border-top: 1px solid #f1f5f9; }
.docs-preview-article { padding: 30px; min-width: 0; }
.docs-preview-article h1 { margin-top: 0; font-size: clamp(30px, 4vw, 48px); }
.docs-preview-article h2 { margin-top: 30px; font-size: 26px; }
.docs-preview-article h3 { margin-top: 24px; font-size: 21px; }
.docs-preview-article p, .docs-preview-article li { color: #334155; line-height: 1.75; font-size: 16px; }
.docs-preview-article code { background: #f1f5f9; padding: 2px 6px; border-radius: 6px; }
.docs-preview-article pre { overflow: auto; padding: 16px; border-radius: 16px; background: #0f172a; color: #e2e8f0; }
.docs-preview-footer { margin-top: 38px; color: #64748b; font-size: 14px; }
@media (max-width: 760px) {
  .docs-preview-shell { padding: 22px 14px 44px; }
  .docs-preview-hero { padding: 22px; }
  .docs-preview-layout { grid-template-columns: 1fr; }
  .docs-preview-nav { position: static; }
  .docs-preview-article { padding: 22px; }
}
""".strip()


def _escape(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def _path_for_doc(doc: dict[str, Any], *, single: bool = False) -> str:
    if single:
        return "/"
    return f"/{clean_slug(doc.get('slug'))}.html"


def _matches_target(doc: dict[str, Any], target: str) -> bool:
    if not target or target == "all":
        return True
    targets = doc.get("framework_targets") or []
    return target in targets or target == "sitelet"


def _markdown_to_html(markdown: str) -> str:
    text = _escape(markdown)
    text = re.sub(r"^### (.*)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.*)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
    text = re.sub(r"^# (.*)$", r"<h1>\1</h1>", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    lines = text.splitlines()
    out: list[str] = []
    in_list = False
    in_pre = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_pre:
                out.append("</code></pre>")
                in_pre = False
            else:
                out.append("<pre><code>")
                in_pre = True
            continue
        if in_pre:
            out.append(line)
            continue
        if stripped.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{stripped[2:]}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if not stripped:
            continue
        if stripped.startswith("<h") or stripped.startswith("<pre"):
            out.append(stripped)
        else:
            out.append(f"<p>{stripped}</p>")
    if in_list:
        out.append("</ul>")
    if in_pre:
        out.append("</code></pre>")
    return "\n".join(out)


def render_doc_content(doc: dict[str, Any]) -> str:
    content = str(doc.get("content") or "")
    content_format = str(doc.get("content_format") or "markdown")
    if content_format == "html":
        return content
    if content_format in {"markdown", "mdx"}:
        return _markdown_to_html(content)
    return f"<pre>{_escape(content)}</pre>"


def _doc_card(doc: dict[str, Any]) -> str:
    tags = "".join(f"<span class='docs-preview-pill'>{_escape(tag)}</span>" for tag in doc.get("tags", [])[:4])
    targets = "".join(f"<span class='docs-preview-pill'>{_escape(target)}</span>" for target in doc.get("framework_targets", [])[:4])
    pills = tags + targets
    return f"""
    <a class="docs-preview-card" href="{_path_for_doc(doc)}">
      <h2>{_escape(doc.get('title'))}</h2>
      <p>{_escape(doc.get('summary'))}</p>
      <div class="docs-preview-meta">
        <span class="docs-preview-pill">{_escape(doc.get('category') or 'Docs')}</span>
        {pills}
      </div>
    </a>
    """


def _nav(docs: list[dict[str, Any]], current_slug: str = "") -> str:
    links = [f"<a href='{_path_for_doc(doc)}'>{_escape(doc.get('title'))}</a>" for doc in docs]
    if current_slug:
        links.insert(0, "<a href='/'>← Docs home</a>")
    return f"<aside class='docs-preview-nav'><h2>Documentation</h2>{''.join(links)}</aside>"


def _base_html(title: str, body: str, description: str = "") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{_escape(title)}</title>
  <meta name="description" content="{_escape(description or title)}" />
  <link rel="stylesheet" href="{PREVIEW_CSS_PATH}" />
</head>
<body>
{body}
</body>
</html>"""


def render_docs_space_html(site_id: str, docs: list[dict[str, Any]], summary: dict[str, Any] | None = None, *, target: str = "sitelet") -> str:
    site_title = (summary or {}).get("name") or site_id
    cards = "\n".join(_doc_card(doc) for doc in docs)
    categories = ", ".join((summary or {}).get("categories") or [])
    body = f"""
<main class="docs-preview-shell" data-easiio-docs-sitelet-preview="space">
  <section class="docs-preview-hero">
    <div class="docs-preview-eyebrow">Easiio Docs Sitelet Preview</div>
    <h1>{_escape(site_title)} Documentation</h1>
    <p>Preview this documentation space before publishing to Sitelet, WordPress, Next.js, static sites, or RAG knowledge workflows.</p>
    <div class="docs-preview-meta">
      <span class="docs-preview-pill">site_id: {_escape(site_id)}</span>
      <span class="docs-preview-pill">target: {_escape(target or 'sitelet')}</span>
      <span class="docs-preview-pill">docs: {len(docs)}</span>
      <span class="docs-preview-pill">categories: {_escape(categories or 'none')}</span>
    </div>
  </section>
  <section class="docs-preview-grid" aria-label="Documentation pages">
    {cards or '<p>No published public documentation is ready for preview.</p>'}
  </section>
  <p class="docs-preview-footer">Generated by Easiio Docs Module. Upload to Sitelet only after human approval.</p>
</main>
"""
    return _base_html(f"{site_title} Documentation", body, f"Sitelet preview for {site_title} documentation")


def render_single_doc_html(doc: dict[str, Any], docs: list[dict[str, Any]] | None = None) -> str:
    docs = docs or [doc]
    content = render_doc_content(doc)
    tags = "".join(f"<span class='docs-preview-pill'>{_escape(tag)}</span>" for tag in doc.get("tags", []))
    targets = "".join(f"<span class='docs-preview-pill'>{_escape(target)}</span>" for target in doc.get("framework_targets", []))
    body = f"""
<main class="docs-preview-shell" data-easiio-docs-sitelet-preview="doc">
  <section class="docs-preview-layout">
    {_nav(docs, current_slug=str(doc.get('slug') or ''))}
    <article class="docs-preview-article">
      <div class="docs-preview-eyebrow">Easiio Docs Sitelet Preview</div>
      <h1>{_escape(doc.get('title'))}</h1>
      <p>{_escape(doc.get('summary'))}</p>
      <div class="docs-preview-meta">
        <span class="docs-preview-pill">{_escape(doc.get('category') or 'Docs')}</span>
        <span class="docs-preview-pill">{_escape(doc.get('status'))}</span>
        <span class="docs-preview-pill">{_escape(doc.get('visibility'))}</span>
        {tags}{targets}
      </div>
      <hr />
      {content}
      <p class="docs-preview-footer">Generated by Easiio Docs Module. Upload to Sitelet only after human approval.</p>
    </article>
  </section>
</main>
"""
    return _base_html(str(doc.get("title") or "Documentation"), body, str(doc.get("summary") or ""))


def build_sitelet_preview_payload(store: DocsStore, site_id: str, *, slug: str = "", target: str = "sitelet", status: str = "published", visibility: str = "public") -> dict[str, Any]:
    site_id = clean_text(site_id, 100)
    slug = clean_slug(slug)
    target = clean_text(target or "sitelet", 80)
    if not site_id:
        raise ValueError("site_id is required")
    all_docs = store.list_docs(site_id, status=status, visibility=visibility)
    docs = [doc for doc in all_docs if _matches_target(doc, target)]
    full_docs = [store.get_doc(site_id, doc["slug"]) or doc for doc in docs]
    summary = store.get_space_summary(site_id)
    title = f"{summary.get('name') or site_id} Docs Preview"

    if slug:
        doc = store.get_doc(site_id, slug)
        if not doc or doc.get("status") != status or doc.get("visibility") != visibility:
            raise ValueError("doc not found or not previewable")
        pages = [{"path": "/", "title": doc.get("title") or slug, "html": render_single_doc_html(doc, full_docs or [doc])}]
        preview_scope = "single-doc"
        title = f"{doc.get('title')} Docs Preview"
    else:
        pages = [{"path": "/", "title": title, "html": render_docs_space_html(site_id, full_docs, summary, target=target)}]
        for doc in full_docs:
            pages.append({"path": _path_for_doc(doc), "title": doc.get("title") or doc.get("slug"), "html": render_single_doc_html(doc, full_docs)})
        preview_scope = "space"

    return {
        "title": title,
        "source": "easiio-docs-module",
        "kind": "site",
        "pages": pages,
        "assets": [{"path": PREVIEW_CSS_PATH, "contentType": "text/css; charset=utf-8", "content": PREVIEW_CSS}],
        "metadata": {
            "exportType": "easiio-docs-sitelet-preview",
            "site_id": site_id,
            "target": target,
            "status": status,
            "visibility": visibility,
            "slug": slug,
            "previewScope": preview_scope,
            "documentCount": len(pages) if slug else len(full_docs),
            "requiresUploadApproval": True,
            "uploadBlocked": True,
        },
    }


def build_sitelet_preview_response(payload: dict[str, Any]) -> dict[str, Any]:
    metadata = payload.get("metadata", {})
    return {
        "ok": True,
        "exportType": "easiio-docs-sitelet-preview",
        "previewScope": metadata.get("previewScope", "space"),
        "requiresUploadApproval": True,
        "uploadBlocked": True,
        "siteletPayload": payload,
        "uploadInstructions": {
            "step": "After review, POST siteletPayload to SITELET_BASE_URL/api/generated with Authorization: Bearer SITELET_API_TOKEN.",
            "publishBlocked": True,
            "humanApprovalRequired": True,
        },
    }
