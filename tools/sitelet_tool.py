"""Sitelet preview publishing tool.

Uploads generated HTML to a Sitelet server and returns a public preview URL.
"""

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from html import escape
from pathlib import Path
from typing import Any, Optional

from tools.registry import registry


MAX_HTML_BYTES = 5 * 1024 * 1024


class SiteletPublishError(Exception):
    """Raised when Sitelet upload fails."""


def _clean_base_url(base_url: Optional[str] = None) -> str:
    value = (base_url or os.getenv("SITELET_BASE_URL", "")).strip()
    if not value:
        raise SiteletPublishError(
            "SITELET_BASE_URL is not configured. Set it to the deployed Sitelet base URL "
            "or pass base_url explicitly."
        )

    parsed = urllib.parse.urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise SiteletPublishError("Sitelet base URL must be an absolute http(s) URL.")
    return value.rstrip("/")


def _read_html(html: Optional[str], html_path: Optional[str]) -> str:
    if html and html.strip():
        content = html
    elif html_path and html_path.strip():
        path = Path(html_path).expanduser()
        if not path.exists():
            raise SiteletPublishError(f"HTML file does not exist: {path}")
        if not path.is_file():
            raise SiteletPublishError(f"HTML path is not a file: {path}")
        content = path.read_text(encoding="utf-8")
    else:
        raise SiteletPublishError("Provide either html or html_path.")

    if not content.strip():
        raise SiteletPublishError("Generated page HTML is empty.")
    if len(content.encode("utf-8")) > MAX_HTML_BYTES:
        raise SiteletPublishError("Generated page HTML is larger than the 5 MiB upload limit.")
    return content


def _sitelet_request(
    base_url: str,
    payload: dict[str, Any],
    api_token: Optional[str] = None,
    timeout: int = 20,
) -> dict[str, Any]:
    token = (api_token if api_token is not None else os.getenv("SITELET_API_TOKEN", "")).strip()
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Hermes-Agent Sitelet Publisher",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(
        f"{base_url}/api/generated",
        data=data,
        method="POST",
        headers=headers,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SiteletPublishError(f"Sitelet upload failed with HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SiteletPublishError(f"Could not reach Sitelet server: {exc.reason}") from exc

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SiteletPublishError("Sitelet returned a non-JSON response.") from exc

    if not isinstance(parsed, dict) or not parsed.get("ok"):
        error = parsed.get("error") if isinstance(parsed, dict) else None
        raise SiteletPublishError(error or "Sitelet upload was not accepted.")
    return parsed


def sitelet_publish(
    title: str = "Generated Page",
    html: str = "",
    html_path: str = "",
    source: str = "hermes",
    base_url: str = "",
    timeout: int = 20,
    api_token: str = "",
    task_id: str = None,
) -> str:
    """Upload HTML to Sitelet and return JSON with preview URLs."""
    try:
        resolved_base_url = _clean_base_url(base_url or None)
        content = _read_html(html or None, html_path or None)
        result = _sitelet_request(
            resolved_base_url,
            {
                "title": title or "Generated Page",
                "source": source or "hermes",
                "html": content,
            },
            api_token=api_token or None,
            timeout=max(1, min(int(timeout or 20), 60)),
        )
        return json.dumps(
            {
                "ok": True,
                "id": result.get("id"),
                "title": result.get("title"),
                "generatedUrl": result.get("generatedUrl"),
                "siteletUrl": result.get("siteletUrl"),
                "createdAt": result.get("createdAt"),
                "message": "Sitelet preview is ready. Share siteletUrl with the user.",
            }
        )
    except Exception as exc:
        return json.dumps({"ok": False, "error": str(exc)})


def _html_body_from_wordpress_content(content: str) -> str:
    value = (content or "").strip()
    if not value:
        raise SiteletPublishError("WordPress preview content is required.")

    if re.search(r"</?[a-zA-Z][^>]*>", value):
        return value

    paragraphs = [
        f"<p>{escape(part.strip()).replace(chr(10), '<br>')}</p>"
        for part in re.split(r"\n\s*\n", value)
        if part.strip()
    ]
    return "\n".join(paragraphs)


def _render_wordpress_preview_html(
    title: str,
    content: str,
    site_name: str = "WordPress Preview",
    slug: str = "",
    excerpt: str = "",
    featured_image_url: str = "",
    status: str = "draft",
    theme_css: str = "",
) -> str:
    clean_title = (title or "Untitled WordPress Page").strip()
    clean_site_name = (site_name or "WordPress Preview").strip()
    body = _html_body_from_wordpress_content(content)
    metadata_items = [
        ("Status", status or "draft"),
        ("Slug", slug),
        ("Excerpt", excerpt),
    ]
    metadata = "\n".join(
        f"<span><strong>{escape(label)}:</strong> {escape(value)}</span>"
        for label, value in metadata_items
        if value
    )
    featured = ""
    if featured_image_url:
        featured = (
            '<figure class="wp-preview-featured">'
            f'<img src="{escape(featured_image_url, quote=True)}" alt="">'
            "</figure>"
        )

    css = f"""
:root {{
  color-scheme: light;
  --wp-preview-bg: #f4f6f8;
  --wp-preview-paper: #ffffff;
  --wp-preview-ink: #172033;
  --wp-preview-muted: #5d6b82;
  --wp-preview-line: #d9e0ea;
  --wp-preview-accent: #16756f;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--wp-preview-bg);
  color: var(--wp-preview-ink);
  font: 16px/1.65 Arial, Helvetica, sans-serif;
}}
.wp-preview-shell {{
  width: min(960px, calc(100vw - 32px));
  margin: 0 auto;
  padding: 32px 0 56px;
}}
.wp-preview-bar {{
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
  color: var(--wp-preview-muted);
  font-size: 13px;
}}
.wp-preview-bar strong {{ color: var(--wp-preview-accent); }}
.wp-preview-paper {{
  overflow: hidden;
  border: 1px solid var(--wp-preview-line);
  border-radius: 8px;
  background: var(--wp-preview-paper);
  box-shadow: 0 18px 52px rgba(23, 32, 51, 0.12);
}}
.wp-preview-hero {{
  padding: 34px 36px 22px;
  border-bottom: 1px solid var(--wp-preview-line);
}}
.wp-preview-hero h1 {{
  margin: 0;
  font-size: clamp(32px, 6vw, 56px);
  line-height: 1.05;
  letter-spacing: 0;
}}
.wp-preview-meta {{
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
  margin-top: 16px;
  color: var(--wp-preview-muted);
  font-size: 13px;
}}
.wp-preview-featured {{ margin: 0; border-bottom: 1px solid var(--wp-preview-line); }}
.wp-preview-featured img {{ display: block; width: 100%; height: auto; }}
.wp-preview-content {{
  padding: 28px 36px 38px;
}}
.wp-preview-content :first-child {{ margin-top: 0; }}
.wp-preview-content :last-child {{ margin-bottom: 0; }}
.wp-preview-content img {{ max-width: 100%; height: auto; }}
.wp-preview-content a {{ color: var(--wp-preview-accent); }}
{theme_css or ""}
"""

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(clean_title)} - {escape(clean_site_name)}</title>
  <style>{css}</style>
</head>
<body>
  <main class="wp-preview-shell">
    <div class="wp-preview-bar">
      <strong>{escape(clean_site_name)}</strong>
      <span>Hermes WordPress preview</span>
    </div>
    <article class="wp-preview-paper">
      <header class="wp-preview-hero">
        <h1>{escape(clean_title)}</h1>
        <div class="wp-preview-meta">{metadata}</div>
      </header>
      {featured}
      <section class="wp-preview-content">
        {body}
      </section>
    </article>
  </main>
</body>
</html>"""


def wordpress_preview_publish(
    title: str,
    content: str,
    site_name: str = "WordPress Preview",
    slug: str = "",
    excerpt: str = "",
    featured_image_url: str = "",
    status: str = "draft",
    theme_css: str = "",
    base_url: str = "",
    timeout: int = 20,
    api_token: str = "",
    task_id: str = None,
) -> str:
    """Render a proposed WordPress page edit to HTML and publish it to Sitelet."""
    html = _render_wordpress_preview_html(
        title=title,
        content=content,
        site_name=site_name,
        slug=slug,
        excerpt=excerpt,
        featured_image_url=featured_image_url,
        status=status,
        theme_css=theme_css,
    )
    return sitelet_publish(
        title=f"WordPress Preview - {title or 'Untitled'}",
        html=html,
        source="wordpress-preview",
        base_url=base_url,
        timeout=timeout,
        api_token=api_token,
        task_id=task_id,
    )


SITELET_PUBLISH_SCHEMA = {
    "name": "sitelet_publish",
    "description": (
        "Upload generated HTML to a configured Sitelet server and return a shareable preview URL. "
        "Use this for interactive previews of generated pages in chat."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Short title for the generated preview page.",
            },
            "html": {
                "type": "string",
                "description": "Complete HTML or an HTML fragment to publish. Use html_path instead for large local files.",
            },
            "html_path": {
                "type": "string",
                "description": "Path to a local HTML file to publish when raw html is not supplied.",
            },
            "source": {
                "type": "string",
                "description": "Short source label stored with the preview, for example hermes or discord.",
            },
            "base_url": {
                "type": "string",
                "description": "Optional Sitelet base URL. Defaults to SITELET_BASE_URL.",
            },
            "timeout": {
                "type": "integer",
                "description": "Upload timeout in seconds, capped at 60.",
                "default": 20,
            },
        },
        "required": [],
    },
}


WORDPRESS_PREVIEW_PUBLISH_SCHEMA = {
    "name": "wordpress_preview_publish",
    "description": (
        "Render proposed WordPress page/post edits into standalone preview HTML, upload it to Sitelet, "
        "and return a shareable Sitelet preview URL that is saved in Sitelet history. "
        "Use before deploying edits to a WordPress site."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Proposed WordPress page or post title.",
            },
            "content": {
                "type": "string",
                "description": (
                    "Proposed WordPress body content as HTML, Gutenberg block HTML, or plain text. "
                    "Plain text is converted into paragraphs."
                ),
            },
            "site_name": {
                "type": "string",
                "description": "Name of the WordPress site shown in the preview header.",
            },
            "slug": {
                "type": "string",
                "description": "Optional proposed WordPress slug.",
            },
            "excerpt": {
                "type": "string",
                "description": "Optional excerpt or summary shown in preview metadata.",
            },
            "featured_image_url": {
                "type": "string",
                "description": "Optional public image URL to render as the featured image.",
            },
            "status": {
                "type": "string",
                "description": "Proposed WordPress status label such as draft, pending, or publish.",
                "default": "draft",
            },
            "theme_css": {
                "type": "string",
                "description": "Optional CSS to approximate the target WordPress theme.",
            },
            "base_url": {
                "type": "string",
                "description": "Optional Sitelet base URL. Defaults to SITELET_BASE_URL.",
            },
            "timeout": {
                "type": "integer",
                "description": "Upload timeout in seconds, capped at 60.",
                "default": 20,
            },
        },
        "required": ["title", "content"],
    },
}


registry.register(
    name="sitelet_publish",
    toolset="sitelet",
    schema=SITELET_PUBLISH_SCHEMA,
    handler=lambda args, **kw: sitelet_publish(
        title=args.get("title", "Generated Page"),
        html=args.get("html", ""),
        html_path=args.get("html_path", ""),
        source=args.get("source", "hermes"),
        base_url=args.get("base_url", ""),
        timeout=args.get("timeout", 20),
        task_id=kw.get("task_id"),
    ),
    description=SITELET_PUBLISH_SCHEMA["description"],
    emoji="🌐",
)

registry.register(
    name="wordpress_preview_publish",
    toolset="sitelet",
    schema=WORDPRESS_PREVIEW_PUBLISH_SCHEMA,
    handler=lambda args, **kw: wordpress_preview_publish(
        title=args.get("title", ""),
        content=args.get("content", ""),
        site_name=args.get("site_name", "WordPress Preview"),
        slug=args.get("slug", ""),
        excerpt=args.get("excerpt", ""),
        featured_image_url=args.get("featured_image_url", ""),
        status=args.get("status", "draft"),
        theme_css=args.get("theme_css", ""),
        base_url=args.get("base_url", ""),
        timeout=args.get("timeout", 20),
        task_id=kw.get("task_id"),
    ),
    description=WORDPRESS_PREVIEW_PUBLISH_SCHEMA["description"],
    emoji="🌐",
)
