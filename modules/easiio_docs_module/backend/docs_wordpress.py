from __future__ import annotations

import html
import re
from typing import Any

from docs_db import DocsStore, clean_slug, clean_text
from docs_sitelet import render_doc_content

SUPPORTED_WP_TARGET = "wordpress-shortcode"


def _escape(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def _bool_text(value: Any) -> str:
    return "true" if str(value).lower() in {"1", "true", "yes", "on"} or value is True else "false"


def _safe_slug(value: str) -> str:
    return clean_slug(value) or "docs"


def _matches_target(doc: dict[str, Any], target: str) -> bool:
    if not target or target == "all":
        return True
    targets = doc.get("framework_targets") or []
    return target in targets


def _published_public_docs(store: DocsStore, site_id: str, *, target: str = SUPPORTED_WP_TARGET, status: str = "published", visibility: str = "public") -> list[dict[str, Any]]:
    docs = store.list_docs(site_id, status=status, visibility=visibility)
    filtered = [doc for doc in docs if _matches_target(doc, target)]
    return [store.get_doc(site_id, doc["slug"]) or doc for doc in filtered]


def build_wordpress_shortcode(site_id: str, *, api_base: str = "https://chat.easiio.com", mode: str = "public", title: str = "Documentation", require_login: Any = False, target_filter: str = SUPPORTED_WP_TARGET, credential_mode: str = "same-origin") -> str:
    site_id = clean_text(site_id, 100)
    mode = "admin" if mode == "admin" else "public"
    attrs = {
        "site_id": site_id,
        "mode": mode,
        "title": clean_text(title or "Documentation", 160),
        "api_base": clean_text(api_base or "https://chat.easiio.com", 300).rstrip("/"),
        "target_filter": clean_text(target_filter or SUPPORTED_WP_TARGET, 80),
        "require_login": _bool_text(require_login),
        "credential_mode": credential_mode if credential_mode in {"omit", "same-origin", "include"} else "same-origin",
    }
    joined = " ".join(f'{key}="{_escape(value)}"' for key, value in attrs.items() if value)
    return f"[easiio_docs {joined}]"


def build_wordpress_embed_html(site_id: str, *, api_base: str = "https://chat.easiio.com", mode: str = "public", title: str = "Documentation", require_login: Any = False, target_filter: str = SUPPORTED_WP_TARGET, credential_mode: str = "same-origin") -> str:
    api_base = clean_text(api_base or "https://chat.easiio.com", 300).rstrip("/")
    mode = "admin" if mode == "admin" else "public"
    root_id = f"easiio-docs-root-{_safe_slug(site_id)}"
    return f"""<link rel="stylesheet" href="{_escape(api_base)}/docs/docs.css" />
<div id="{_escape(root_id)}"></div>
<script
  async
  src="{_escape(api_base)}/docs/docs.js"
  data-easiio-docs
  data-api-base="{_escape(api_base)}"
  data-site-id="{_escape(site_id)}"
  data-mode="{_escape(mode)}"
  data-root-selector="#{_escape(root_id)}"
  data-title="{_escape(title)}"
  data-target-filter="{_escape(target_filter)}"
  data-login-required="{_bool_text(require_login)}"
  data-credential-mode="{_escape(credential_mode)}">
</script>"""


def build_wordpress_shortcode_response(site_id: str, **options: Any) -> dict[str, Any]:
    site_id = clean_text(site_id, 100)
    if not site_id:
        raise ValueError("site_id is required")
    shortcode = build_wordpress_shortcode(site_id, **options)
    embed_html = build_wordpress_embed_html(site_id, **options)
    return {
        "ok": True,
        "exportType": "easiio-docs-wordpress-shortcode",
        "requiresWordPressPlugin": True,
        "publishBlocked": True,
        "shortcode": shortcode,
        "embedHtml": embed_html,
        "usage": "Install the Easiio Docs WordPress plugin, then paste this shortcode into a WordPress page or post.",
    }


def _doc_to_wordpress_section(doc: dict[str, Any]) -> str:
    body = render_doc_content(doc)
    tags = ", ".join(doc.get("tags") or [])
    meta = f"<p><strong>Category:</strong> {_escape(doc.get('category') or 'Docs')}</p>"
    if tags:
        meta += f"<p><strong>Tags:</strong> {_escape(tags)}</p>"
    return f"""
<section class="easiio-docs-wp-section" data-easiio-doc-slug="{_escape(doc.get('slug'))}">
  <h2>{_escape(doc.get('title'))}</h2>
  <p>{_escape(doc.get('summary'))}</p>
  {meta}
  <div class="easiio-docs-wp-content">
    {body}
  </div>
</section>
"""


def _wrap_gutenberg_html(inner_html: str) -> str:
    return "<!-- wp:html -->\n" + inner_html.strip() + "\n<!-- /wp:html -->"


def _excerpt_for_docs(docs: list[dict[str, Any]], site_id: str) -> str:
    if docs:
        return clean_text(docs[0].get("summary") or f"Documentation for {site_id}.", 240)
    return f"Documentation for {site_id}."


def build_wordpress_draft_plan(store: DocsStore, site_id: str, *, target: str = SUPPORTED_WP_TARGET, status: str = "published", visibility: str = "public", page_title: str = "", slug: str = "") -> dict[str, Any]:
    site_id = clean_text(site_id, 100)
    if not site_id:
        raise ValueError("site_id is required")
    docs = _published_public_docs(store, site_id, target=target, status=status, visibility=visibility)
    title = clean_text(page_title, 200) or f"{site_id} Documentation"
    wp_slug = _safe_slug(slug or f"{site_id}-documentation")
    sections = "\n".join(_doc_to_wordpress_section(doc) for doc in docs)
    if not sections:
        sections = "<p>No published public documentation is ready for WordPress draft creation.</p>"
    content = _wrap_gutenberg_html(f"""
<div class="easiio-docs-wordpress-export" data-site-id="{_escape(site_id)}" data-export-type="easiio-docs-wordpress-draft-plan">
  <h1>{_escape(title)}</h1>
  <p>This draft was prepared from the Easiio Docs Module. Review in WordPress before publishing.</p>
  {sections}
</div>
""")
    draft_step = {
        "step": 1,
        "mcpTool": "mcp_easiio_wp_create_draft_post",
        "description": "Create a WordPress draft from the approved Easiio Docs Module content. Do not publish.",
        "arguments": {
            "title": title,
            "content": content,
            "excerpt": _excerpt_for_docs(docs, site_id),
            "slug": wp_slug,
            "status": "draft",
        },
    }
    verify_step = {
        "step": 2,
        "mcpTool": "mcp_easiio_wp_get_post",
        "description": "Verify the created WordPress post/page remains a draft and contains expected docs content.",
        "arguments": {"id": "<POST_ID_FROM_STEP_1>"},
    }
    return {
        "ok": True,
        "exportType": "easiio-docs-wordpress-draft-plan",
        "executionMode": "hermes-mcp-handoff",
        "site_id": site_id,
        "target": target,
        "documentCount": len(docs),
        "requiresHumanApproval": True,
        "publishBlocked": True,
        "outreachBlocked": True,
        "draftSteps": [draft_step],
        "verificationSteps": [verify_step],
        "notes": [
            "This plan does not call WordPress directly.",
            "Use mcp_easiio_wp_create_draft_post only after human approval.",
            "Publishing requires a separate explicit approval after draft verification.",
        ],
    }


def build_wordpress_draft_execution(store: DocsStore, payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("confirmDraftCreation") is not True:
        return {
            "ok": False,
            "error": "confirmDraftCreation is required before preparing WordPress draft execution",
            "requiresHumanApproval": True,
            "publishBlocked": True,
        }
    plan = build_wordpress_draft_plan(
        store,
        clean_text(payload.get("site_id"), 100),
        target=payload.get("target", SUPPORTED_WP_TARGET),
        status=payload.get("status", "published"),
        visibility=payload.get("visibility", "public"),
        page_title=payload.get("page_title", ""),
        slug=payload.get("slug", ""),
    )
    plan.update({
        "exportType": "easiio-docs-wordpress-draft-execution",
        "approvedBy": clean_text(payload.get("approvedBy"), 200),
        "approvalRecorded": True,
        "publishBlocked": True,
    })
    return plan
