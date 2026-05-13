import importlib.util
import argparse
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "website_agency.py"


def load_module():
    spec = importlib.util.spec_from_file_location("website_agency", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["website_agency"] = module
    spec.loader.exec_module(module)
    return module


def run_script(*args: str, check: bool = True) -> dict:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        check=check,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_create_static_site_writes_artifacts(tmp_path):
    result = run_script(
        "create-site",
        "--name",
        "Acme Dental",
        "--description",
        "Family dental clinic for busy parents.",
        "--audience",
        "local families",
        "--goal",
        "Book an appointment",
        "--platform",
        "static",
        "--output-dir",
        str(tmp_path),
    )

    project_dir = Path(result["projectDir"])
    assert result["ok"] is True
    assert result["platform"] == "static"
    assert (project_dir / "index.html").exists()
    assert (project_dir / "styles.css").exists()
    assert (project_dir / "docs" / "website-brief.md").exists()
    assert "Book an appointment" in (project_dir / "index.html").read_text(encoding="utf-8")
    assert result["preview"]["command"].endswith("-m http.server 3010 --bind 0.0.0.0")
    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert state["project"]["name"] == "Acme Dental"
    assert state["project"]["platform"] == "static"


def test_create_nextjs_site_for_app_description(tmp_path):
    result = run_script(
        "create-site",
        "--name",
        "Acme Portal",
        "--description",
        "SaaS dashboard with login for operations teams.",
        "--audience",
        "operations managers",
        "--goal",
        "Request a demo",
        "--output-dir",
        str(tmp_path),
    )

    project_dir = Path(result["projectDir"])
    assert result["ok"] is True
    assert result["platform"] == "nextjs"
    assert (project_dir / "package.json").exists()
    assert (project_dir / "app" / "page.tsx").exists()
    assert result["preview"]["command"] == "npm run dev -- --hostname 0.0.0.0 --port 3010"


def test_build_preview_detects_static_project(tmp_path):
    project_dir = tmp_path / "site"
    project_dir.mkdir()
    (project_dir / "index.html").write_text("<h1>Hello</h1>", encoding="utf-8")

    result = run_script("build-preview", "--project-dir", str(project_dir), "--port", "3333")

    assert result["ok"] is True
    assert result["preview"]["platform"] == "static"
    assert result["preview"]["localUrl"] == "http://127.0.0.1:3333/"
    assert result["preview"]["proxyHint"] == "scripts/start_hermes_proxy_connector.py --target http://127.0.0.1:3333/"


def test_slugify_has_stable_fallback():
    module = load_module()
    assert module.slugify("Acme Dental!") == "acme-dental"
    assert module.slugify("!!!", fallback="site") == "site"


def test_preview_share_prefers_hermesproxy_and_records_history(tmp_path, monkeypatch):
    module = load_module()
    project_dir = tmp_path / "site"
    project_dir.mkdir()
    (project_dir / "index.html").write_text("<h1>Hello</h1>", encoding="utf-8")

    monkeypatch.setattr(
        module,
        "start_preview_process",
        lambda project_dir, command, log_file: {"pid": 123, "logFile": "/tmp/preview.log"},
    )
    monkeypatch.setattr(
        module,
        "start_hermes_proxy",
        lambda **kwargs: {
            "ok": True,
            "publicUrl": "https://hermesproxy.example/p/tunnel-1/",
            "tunnelId": "tunnel-1",
            "site": kwargs["site"],
        },
    )

    result = module.preview_share(
        argparse.Namespace(
            project_dir=str(project_dir),
            port=3333,
            start_local=True,
            log_file=None,
            prefer="hermesproxy",
            fallback="auto",
            site="demo-site",
            proxy_base_url="https://hermesproxy.example",
            proxy_token="secret",
            wait_seconds=1,
            title="Demo",
            sitelet_base_url="",
            sitelet_api_token="",
        )
    )

    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["preview"]["method"] == "hermesproxy"
    assert result["preview"]["publicUrl"] == "https://hermesproxy.example/p/tunnel-1/"
    assert state["lastPreview"]["method"] == "hermesproxy"
    assert state["previews"][0]["preview"]["tunnelId"] == "tunnel-1"


def test_preview_share_falls_back_to_sitelet_for_static_html(tmp_path, monkeypatch):
    module = load_module()
    project_dir = tmp_path / "site"
    project_dir.mkdir()
    (project_dir / "index.html").write_text("<h1>Hello</h1>", encoding="utf-8")

    monkeypatch.setattr(module, "start_preview_process", lambda *args, **kwargs: {"pid": 456})
    monkeypatch.setattr(module, "start_hermes_proxy", lambda **kwargs: {"ok": False, "error": "not configured"})
    monkeypatch.setattr(
        module,
        "publish_sitelet_static",
        lambda **kwargs: {
            "ok": True,
            "siteletUrl": "https://sitelet.example/sitelet?id=1",
            "generatedUrl": "https://sitelet.example/generated/1",
        },
    )

    result = module.preview_share(
        argparse.Namespace(
            project_dir=str(project_dir),
            port=3333,
            start_local=True,
            log_file=None,
            prefer="hermesproxy",
            fallback="auto",
            site=None,
            proxy_base_url="",
            proxy_token="",
            wait_seconds=1,
            title="Demo",
            sitelet_base_url="https://sitelet.example",
            sitelet_api_token="token",
        )
    )

    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["preview"]["method"] == "sitelet"
    assert result["preview"]["publicUrl"] == "https://sitelet.example/sitelet?id=1"
    assert [attempt["method"] for attempt in state["previews"][0]["attempts"]] == ["hermesproxy", "sitelet"]


def test_inline_static_css_replaces_local_stylesheet(tmp_path):
    module = load_module()
    project_dir = tmp_path / "site"
    project_dir.mkdir()
    (project_dir / "styles.css").write_text("body { color: red; }", encoding="utf-8")
    index = project_dir / "index.html"
    index.write_text('<link rel="stylesheet" href="styles.css"><h1>Hello</h1>', encoding="utf-8")

    html = module.inline_static_css(index)

    assert "<style>" in html
    assert "body { color: red; }" in html
    assert 'href="styles.css"' not in html


def test_qa_passes_for_generated_static_site(tmp_path):
    generated = run_script(
        "create-site",
        "--name",
        "Acme Dental",
        "--description",
        "Family dental clinic for busy parents.",
        "--audience",
        "local families",
        "--goal",
        "Book an appointment",
        "--platform",
        "static",
        "--output-dir",
        str(tmp_path),
    )

    result = run_script("qa", "--project-dir", generated["projectDir"])
    project_dir = Path(generated["projectDir"])
    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))

    assert result["ok"] is True
    assert result["summary"]["failures"] == 0
    assert (project_dir / "docs" / "qa-report.md").exists()
    assert state["lastQa"]["ok"] is True
    assert state["qaReports"][0]["summary"]["failures"] == 0


def test_qa_reports_static_html_failures(tmp_path):
    project_dir = tmp_path / "broken-site"
    project_dir.mkdir()
    (project_dir / "index.html").write_text(
        '<html><head></head><body><h1>One</h1><h1>Two</h1><img src="hero.png"><a href="missing.html">Missing</a></body></html>',
        encoding="utf-8",
    )

    result = run_script("qa", "--project-dir", str(project_dir), check=False)

    failures = {check["name"]: check["message"] for check in result["checks"] if check["status"] == "fail"}
    assert result["ok"] is False
    assert "html-title" in failures
    assert "meta-description" in failures
    assert "single-h1" in failures
    assert "image-alt" in failures
    assert any("Broken local link" in check["message"] for check in result["checks"])


def test_qa_nextjs_source_checks(tmp_path):
    generated = run_script(
        "create-site",
        "--name",
        "Acme Portal",
        "--description",
        "SaaS dashboard with login for operations teams.",
        "--audience",
        "operations managers",
        "--goal",
        "Request a demo",
        "--output-dir",
        str(tmp_path),
    )

    result = run_script("qa", "--project-dir", generated["projectDir"])

    assert result["ok"] is True
    assert result["platform"] == "nextjs"
    assert result["summary"]["failures"] == 0
