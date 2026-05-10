"""Tests for the Sitelet preview publishing tool."""

import json
import urllib.error
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from tools.sitelet_tool import (
    SiteletPublishError,
    _clean_base_url,
    _render_wordpress_preview_html,
    _read_html,
    sitelet_publish,
    wordpress_preview_publish,
)


def _mock_urlopen(response_data, status=200):
    mock_resp = MagicMock()
    mock_resp.status = status
    mock_resp.read.return_value = json.dumps(response_data).encode("utf-8")
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


class TestSiteletConfig:
    def test_clean_base_url_from_env(self, monkeypatch):
        monkeypatch.setenv("SITELET_BASE_URL", "https://sitelet.example.com/")
        assert _clean_base_url() == "https://sitelet.example.com"

    def test_clean_base_url_rejects_missing(self, monkeypatch):
        monkeypatch.delenv("SITELET_BASE_URL", raising=False)
        with pytest.raises(SiteletPublishError) as exc_info:
            _clean_base_url()
        assert "SITELET_BASE_URL" in str(exc_info.value)

    def test_clean_base_url_rejects_relative(self):
        with pytest.raises(SiteletPublishError):
            _clean_base_url("/api/generated")


class TestHtmlInput:
    def test_raw_html_wins(self, tmp_path):
        html_file = tmp_path / "page.html"
        html_file.write_text("<p>from file</p>", encoding="utf-8")
        assert _read_html("<p>raw</p>", str(html_file)) == "<p>raw</p>"

    def test_reads_html_path(self, tmp_path):
        html_file = tmp_path / "page.html"
        html_file.write_text("<p>from file</p>", encoding="utf-8")
        assert _read_html(None, str(html_file)) == "<p>from file</p>"

    def test_requires_html_or_path(self):
        with pytest.raises(SiteletPublishError):
            _read_html("", "")


class TestPublish:
    @patch("tools.sitelet_tool.urllib.request.urlopen")
    def test_publish_posts_json_with_token(self, mock_urlopen_fn, monkeypatch):
        monkeypatch.setenv("SITELET_BASE_URL", "https://sitelet.example.com")
        monkeypatch.setenv("SITELET_API_TOKEN", "stlt_secret")
        mock_urlopen_fn.return_value = _mock_urlopen(
            {
                "ok": True,
                "id": "page-1",
                "title": "Draft",
                "generatedUrl": "https://sitelet.example.com/generated/page-1",
                "siteletUrl": "https://sitelet.example.com/sitelet?url=x",
                "createdAt": "2026-05-09T00:00:00.000Z",
            }
        )

        result = json.loads(sitelet_publish(title="Draft", html="<h1>Hello</h1>"))

        assert result["ok"] is True
        assert result["id"] == "page-1"
        assert result["siteletUrl"].startswith("https://sitelet.example.com/sitelet")

        request = mock_urlopen_fn.call_args[0][0]
        assert request.full_url == "https://sitelet.example.com/api/generated"
        assert request.get_header("Authorization") == "Bearer stlt_secret"
        payload = json.loads(request.data.decode("utf-8"))
        assert payload == {
            "title": "Draft",
            "source": "hermes",
            "html": "<h1>Hello</h1>",
        }

    @patch("tools.sitelet_tool.urllib.request.urlopen")
    def test_publish_works_without_token_for_anonymous_servers(self, mock_urlopen_fn, monkeypatch):
        monkeypatch.setenv("SITELET_BASE_URL", "http://localhost:3020")
        monkeypatch.delenv("SITELET_API_TOKEN", raising=False)
        mock_urlopen_fn.return_value = _mock_urlopen(
            {
                "ok": True,
                "id": "page-2",
                "generatedUrl": "http://localhost:3020/generated/page-2",
                "siteletUrl": "http://localhost:3020/sitelet?url=x",
            }
        )

        result = json.loads(sitelet_publish(html="<h1>Hello</h1>"))

        assert result["ok"] is True
        request = mock_urlopen_fn.call_args[0][0]
        assert request.get_header("Authorization") is None

    @patch("tools.sitelet_tool.urllib.request.urlopen")
    def test_publish_http_error_returns_json_error(self, mock_urlopen_fn, monkeypatch):
        monkeypatch.setenv("SITELET_BASE_URL", "https://sitelet.example.com")
        error_body = json.dumps({"ok": False, "error": "Invalid bearer token."}).encode()
        mock_urlopen_fn.side_effect = urllib.error.HTTPError(
            url="https://sitelet.example.com/api/generated",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=BytesIO(error_body),
        )

        result = json.loads(sitelet_publish(html="<h1>Hello</h1>"))

        assert result["ok"] is False
        assert "HTTP 401" in result["error"]
        assert "Invalid bearer token" in result["error"]


class TestWordPressPreview:
    def test_render_wordpress_preview_wraps_plain_text(self):
        html = _render_wordpress_preview_html(
            title="About Us",
            content="First paragraph.\n\nSecond paragraph.",
            site_name="Example WP",
            slug="about-us",
            excerpt="Company overview",
        )

        assert "<title>About Us - Example WP</title>" in html
        assert "<h1>About Us</h1>" in html
        assert "<p>First paragraph.</p>" in html
        assert "<p>Second paragraph.</p>" in html
        assert "<strong>Slug:</strong> about-us" in html
        assert "<strong>Excerpt:</strong> Company overview" in html

    def test_render_wordpress_preview_preserves_html_content(self):
        html = _render_wordpress_preview_html(
            title="Services",
            content="<div class=\"wp-block-group\"><h2>Consulting</h2></div>",
        )

        assert '<div class="wp-block-group"><h2>Consulting</h2></div>' in html

    @patch("tools.sitelet_tool.urllib.request.urlopen")
    def test_wordpress_preview_publish_uploads_rendered_html(self, mock_urlopen_fn, monkeypatch):
        monkeypatch.setenv("SITELET_BASE_URL", "https://sitelet.example.com")
        monkeypatch.setenv("SITELET_API_TOKEN", "stlt_secret")
        mock_urlopen_fn.return_value = _mock_urlopen(
            {
                "ok": True,
                "id": "wp-preview-1",
                "title": "WordPress Preview - About Us",
                "generatedUrl": "https://sitelet.example.com/generated/wp-preview-1",
                "siteletUrl": "https://sitelet.example.com/sitelet?url=x",
                "createdAt": "2026-05-10T00:00:00.000Z",
            }
        )

        result = json.loads(
            wordpress_preview_publish(
                title="About Us",
                content="<p>Draft content</p>",
                site_name="Example WP",
                slug="about-us",
            )
        )

        assert result["ok"] is True
        assert result["id"] == "wp-preview-1"
        request = mock_urlopen_fn.call_args[0][0]
        payload = json.loads(request.data.decode("utf-8"))
        assert payload["title"] == "WordPress Preview - About Us"
        assert payload["source"] == "wordpress-preview"
        assert "<h1>About Us</h1>" in payload["html"]
        assert "<p>Draft content</p>" in payload["html"]
