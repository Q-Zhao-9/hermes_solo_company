import importlib.util
import argparse
import json
import subprocess
import sys
import zipfile
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


def test_create_site_auto_selects_restaurant_template(tmp_path):
    result = run_script(
        "create-site",
        "--name",
        "Acme Bistro",
        "--description",
        "Neighborhood restaurant with seasonal menu and private dining.",
        "--audience",
        "local diners",
        "--goal",
        "Reserve a table",
        "--platform",
        "static",
        "--output-dir",
        str(tmp_path),
    )

    project_dir = Path(result["projectDir"])
    html = (project_dir / "index.html").read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    brief = (project_dir / "docs" / "website-brief.md").read_text(encoding="utf-8")
    assert result["ok"] is True
    assert result["template"] == "restaurant"
    assert "Restaurant website" in html
    assert "Menu highlights" in html
    assert "Reserve a table" in html
    assert "## Template\nrestaurant" in brief
    assert state["project"]["template"] == "restaurant"


def test_create_site_explicit_portfolio_template(tmp_path):
    result = run_script(
        "create-site",
        "--name",
        "Mira Chen",
        "--description",
        "Independent product designer portfolio for selected case studies.",
        "--audience",
        "startup founders",
        "--goal",
        "Start a collaboration",
        "--platform",
        "static",
        "--template",
        "portfolio",
        "--output-dir",
        str(tmp_path),
    )

    html = (Path(result["projectDir"]) / "index.html").read_text(encoding="utf-8")
    assert result["template"] == "portfolio"
    assert "Portfolio website" in html
    assert "Featured work" in html
    assert "Case studies" in html


def test_create_static_site_with_multiple_pages(tmp_path):
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
        "--pages",
        "home,about,services,contact,faq",
        "--output-dir",
        str(tmp_path),
    )

    project_dir = Path(result["projectDir"])
    index = (project_dir / "index.html").read_text(encoding="utf-8")
    about = (project_dir / "about.html").read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    sitemap = (project_dir / "docs" / "sitemap.md").read_text(encoding="utf-8")
    assert result["ok"] is True
    assert (project_dir / "services.html").exists()
    assert (project_dir / "contact.html").exists()
    assert (project_dir / "faq.html").exists()
    assert 'href="about.html"' in index
    assert "About Acme Dental" in about
    assert [page["slug"] for page in state["pages"]] == ["home", "about", "services", "contact", "faq"]
    assert "- FAQ:" in sitemap


def test_add_page_updates_static_navigation_and_state(tmp_path):
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
        "--pages",
        "home,contact",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(result["projectDir"])

    added = run_script(
        "add-page",
        "--project-dir",
        str(project_dir),
        "--title",
        "Pricing",
        "--page-type",
        "pricing",
        "--description",
        "Simple package options for families.",
        "--goal",
        "Request pricing",
    )

    index = (project_dir / "index.html").read_text(encoding="utf-8")
    pricing = (project_dir / "pricing.html").read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert added["ok"] is True
    assert 'href="pricing.html"' in index
    assert "Simple package options for families." in pricing
    assert state["lastPage"]["type"] == "add-page"
    assert [page["slug"] for page in state["pages"]] == ["home", "contact", "pricing"]


def test_media_plan_creates_manifest_placeholders_and_history(tmp_path):
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
        "--pages",
        "home,about",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(result["projectDir"])

    plan = run_script("media-plan", "--project-dir", str(project_dir), "--style", "bright clinical")

    manifest = json.loads(Path(plan["manifestPath"]).read_text(encoding="utf-8"))
    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert plan["ok"] is True
    assert [asset["page"] for asset in plan["assets"]] == ["home", "about"]
    assert (project_dir / "assets" / "images" / "home-hero.svg").exists()
    assert "altText" in manifest["assets"][0]
    assert state["lastMedia"]["type"] == "media-plan"


def test_media_apply_inserts_static_images_with_alt_text(tmp_path):
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
        "--pages",
        "home,about",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(result["projectDir"])
    run_script("media-plan", "--project-dir", str(project_dir))

    applied = run_script("media-apply", "--project-dir", str(project_dir))

    index = (project_dir / "index.html").read_text(encoding="utf-8")
    about = (project_dir / "about.html").read_text(encoding="utf-8")
    css = (project_dir / "styles.css").read_text(encoding="utf-8")
    assert applied["ok"] is True
    assert "assets/images/home-hero.svg" in index
    assert "assets/images/about-hero.svg" in about
    assert 'alt="Acme Dental home visual for local families"' in index
    assert ".media-figure" in css


def test_media_add_copies_asset_and_records_metadata(tmp_path):
    result = run_script(
        "create-site",
        "--name",
        "Acme Dental",
        "--description",
        "Family dental clinic for busy parents.",
        "--platform",
        "static",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(result["projectDir"])
    source = tmp_path / "source.svg"
    source.write_text("<svg xmlns=\"http://www.w3.org/2000/svg\"></svg>", encoding="utf-8")

    added = run_script(
        "media-add",
        "--project-dir",
        str(project_dir),
        "--file",
        str(source),
        "--asset-id",
        "team-photo",
        "--filename",
        "team-photo.svg",
        "--alt-text",
        "Acme Dental care team",
    )

    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert added["ok"] is True
    assert (project_dir / "assets" / "images" / "team-photo.svg").exists()
    assert state["mediaAssets"][0]["id"] == "team-photo"


def test_wordpress_media_upload_calls_mcp(monkeypatch, tmp_path):
    module = load_module()
    result = run_script(
        "create-site",
        "--name",
        "Acme Dental",
        "--description",
        "Family dental clinic for busy parents.",
        "--platform",
        "static",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(result["projectDir"])
    manifest = project_dir / "docs" / "media-plan.json"
    manifest.write_text(
        json.dumps(
            {
                "assets": [
                    {
                        "id": "home-hero",
                        "title": "Home Hero",
                        "altText": "Acme Dental homepage",
                        "sourceUrl": "https://cdn.example/home.jpg",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    calls = []

    def fake_call(endpoint, api_token, name, arguments):
        calls.append((endpoint, api_token, name, arguments))
        return {"id": 100, "url": arguments["url"]}

    monkeypatch.setattr(module, "call_wordpress_mcp_tool", fake_call)
    upload = module.wordpress_media_upload(
        argparse.Namespace(
            project_dir=str(project_dir),
            manifest=str(manifest),
            asset_id="",
            url="",
            mcp_url="https://wp.example/wp-json/hermes-mcp/v1/mcp",
            mcp_token="token",
        )
    )

    assert upload["ok"] is True
    assert calls[0][2] == "upload_media_from_url"
    assert calls[0][3]["alt_text"] == "Acme Dental homepage"


def test_create_nextjs_uses_saas_template_content(tmp_path):
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

    page = (Path(result["projectDir"]) / "app" / "page.tsx").read_text(encoding="utf-8")
    assert result["template"] == "saas"
    assert "SaaS website" in page
    assert "Product value" in page
    assert "Product confidence" in page


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


def test_list_sections_for_generated_static_site(tmp_path):
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

    result = run_script("list-sections", "--project-dir", generated["projectDir"])

    section_ids = [section["id"] for section in result["sections"]]
    assert result["ok"] is True
    assert "top" in section_ids
    assert "services" in section_ids
    assert "contact" in section_ids


def test_edit_section_updates_static_site_and_records_revision(tmp_path):
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
    project_dir = Path(generated["projectDir"])

    result = run_script(
        "edit-section",
        "--project-dir",
        str(project_dir),
        "--section",
        "top",
        "--heading",
        "Premium dental care for busy families",
        "--body",
        "A calm, modern clinic experience with easy scheduling.",
        "--cta",
        "Schedule today",
        "--request",
        "make hero more premium",
    )

    html = (project_dir / "index.html").read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert "Premium dental care for busy families" in html
    assert "A calm, modern clinic experience" in html
    assert "Schedule today" in html
    assert '<p class="eyebrow">Local service website</p>' in html
    assert state["lastRevision"]["type"] == "edit-section"
    assert state["lastRevision"]["request"] == "make hero more premium"


def test_change_style_updates_css_and_records_revision(tmp_path):
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
    project_dir = Path(generated["projectDir"])

    result = run_script("change-style", "--project-dir", str(project_dir), "--preset", "luxury")

    css = (project_dir / "styles.css").read_text(encoding="utf-8")
    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert "#9f7a2f" in css
    assert state["lastRevision"]["type"] == "change-style"
    assert state["lastRevision"]["palette"]["accent"] == "#9f7a2f"


def test_edit_section_updates_nextjs_page(tmp_path):
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
    project_dir = Path(generated["projectDir"])

    result = run_script(
        "edit-section",
        "--project-dir",
        str(project_dir),
        "--section",
        "top",
        "--heading",
        "Operations clarity in one workspace",
        "--body",
        "A faster way to coordinate teams and customers.",
        "--cta",
        "Start your demo",
    )

    page = (project_dir / "app" / "page.tsx").read_text(encoding="utf-8")
    assert result["ok"] is True
    assert "Operations clarity in one workspace" in page
    assert "A faster way to coordinate teams" in page
    assert "Start your demo" in page
    assert '<p className="eyebrow">SaaS website</p>' in page


def test_deploy_prep_static_zip_records_history(tmp_path):
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
    project_dir = Path(generated["projectDir"])

    result = run_script("deploy-prep", "--project-dir", str(project_dir), "--target", "static-zip")

    artifact = Path(result["artifact"])
    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["target"] == "static-zip"
    assert artifact.exists()
    with zipfile.ZipFile(artifact) as archive:
        names = set(archive.namelist())
    assert "index.html" in names
    assert "styles.css" in names
    assert Path(result["notesPath"]).exists()
    assert state["lastDeployment"]["target"] == "static-zip"


def test_deploy_prep_nextjs_vercel_settings(tmp_path):
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
    project_dir = Path(generated["projectDir"])

    result = run_script("deploy-prep", "--project-dir", str(project_dir), "--target", "vercel")

    settings = json.loads(Path(result["artifact"]).read_text(encoding="utf-8"))
    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["target"] == "vercel"
    assert settings["framework"] == "Next.js"
    assert settings["buildCommand"] == "npm run build"
    assert "vercel deploy" in result["commands"]
    assert state["lastDeployment"]["target"] == "vercel"


def test_deploy_run_returns_plan_without_execution(tmp_path):
    generated = run_script(
        "create-site",
        "--name",
        "Acme Dental",
        "--description",
        "Family dental clinic for busy parents.",
        "--platform",
        "static",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(generated["projectDir"])

    result = run_script(
        "deploy-run",
        "--project-dir",
        str(project_dir),
        "--target",
        "static-dir",
        "--destination",
        str(tmp_path / "published"),
    )

    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["dryRun"] is True
    assert result["plan"]["kind"] == "copy-static"
    assert state["lastDeployment"]["type"] == "deploy-plan"


def test_deploy_run_requires_approval_for_execution(tmp_path):
    generated = run_script(
        "create-site",
        "--name",
        "Acme Dental",
        "--description",
        "Family dental clinic for busy parents.",
        "--platform",
        "static",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(generated["projectDir"])

    result = run_script(
        "deploy-run",
        "--project-dir",
        str(project_dir),
        "--target",
        "static-dir",
        "--destination",
        str(tmp_path / "published"),
        "--execute",
        check=False,
    )

    assert result["ok"] is False
    assert "requires explicit approval" in result["error"]


def test_deploy_run_static_dir_copies_files_with_recorded_approval(tmp_path):
    generated = run_script(
        "create-site",
        "--name",
        "Acme Dental",
        "--description",
        "Family dental clinic for busy parents.",
        "--platform",
        "static",
        "--pages",
        "home,about",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(generated["projectDir"])
    destination = tmp_path / "published"
    run_script(
        "approval-record",
        "--project-dir",
        str(project_dir),
        "--target",
        "deploy",
        "--reference",
        "deploy-static-dir",
        "--decision",
        "approved",
    )

    result = run_script(
        "deploy-run",
        "--project-dir",
        str(project_dir),
        "--target",
        "static-dir",
        "--destination",
        str(destination),
        "--execute",
    )

    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert (destination / "index.html").exists()
    assert (destination / "about.html").exists()
    assert state["lastDeployment"]["type"] == "deploy-run"
    assert state["lastDeployment"]["ok"] is True


def test_deploy_run_vercel_executes_cli_with_approval(tmp_path, monkeypatch):
    module = load_module()
    generated = run_script(
        "create-site",
        "--name",
        "Acme Portal",
        "--description",
        "SaaS dashboard with login for operations teams.",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(generated["projectDir"])
    calls = []

    class Completed:
        returncode = 0
        stdout = "Production: https://acme.vercel.app"
        stderr = ""

    def fake_run(argv, **kwargs):
        calls.append((argv, kwargs))
        return Completed()

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    result = module.deploy_run(
        argparse.Namespace(
            project_dir=str(project_dir),
            target="vercel",
            destination="",
            reference="deploy-vercel",
            execute=True,
            approved=True,
            prod=True,
            yes=True,
            timeout=30,
        )
    )

    assert result["ok"] is True
    assert calls[0][0] == ["vercel", "deploy", "--prod", "--yes"]
    assert result["deployment"]["publicUrl"] == "https://acme.vercel.app"


def test_visual_qa_passes_for_generated_static_site(tmp_path):
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
    project_dir = Path(generated["projectDir"])

    result = run_script("visual-qa", "--project-dir", str(project_dir))

    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["summary"]["failures"] == 0
    assert (project_dir / "docs" / "visual-qa-report.md").exists()
    assert state["lastVisualQa"]["summary"]["failures"] == 0


def test_visual_qa_reports_responsive_failures(tmp_path):
    project_dir = tmp_path / "visual-broken"
    project_dir.mkdir()
    (project_dir / "index.html").write_text("<html><body><h1>Hello</h1></body></html>", encoding="utf-8")
    (project_dir / "styles.css").write_text("h1 { width: 900px; letter-spacing: -1px; }", encoding="utf-8")

    result = run_script("visual-qa", "--project-dir", str(project_dir), check=False)

    failures = {check["name"] for check in result["checks"] if check["status"] == "fail"}
    warnings = {check["name"] for check in result["checks"] if check["status"] == "warning"}
    assert result["ok"] is False
    assert "responsive-media-query" in failures
    assert "button-touch-target" in failures
    assert "no-negative-letter-spacing" in failures
    assert "viewport-meta" in failures
    assert "fixed-width-risk" in warnings


def test_summary_returns_discord_friendly_status(tmp_path):
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
    project_dir = Path(generated["projectDir"])
    run_script("qa", "--project-dir", str(project_dir))
    run_script("visual-qa", "--project-dir", str(project_dir))
    run_script("deploy-prep", "--project-dir", str(project_dir), "--target", "static-zip")

    result = run_script("summary", "--project-dir", str(project_dir))

    assert result["ok"] is True
    assert "**Website Status: Acme Dental**" in result["summary"]
    assert "QA:" in result["summary"]
    assert "Visual QA:" in result["summary"]
    assert "Deploy artifact:" in result["summary"]


def test_wordpress_package_generates_draft_files_and_history(tmp_path):
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
    project_dir = Path(generated["projectDir"])

    result = run_script(
        "wordpress-package",
        "--project-dir",
        str(project_dir),
        "--title",
        "Family Dental Services",
        "--slug",
        "family-dental-services",
        "--site-name",
        "Acme WP",
        "--excerpt",
        "Dental service overview",
    )

    content = Path(result["contentFile"]).read_text(encoding="utf-8")
    spec = json.loads(Path(result["specPath"]).read_text(encoding="utf-8"))
    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert "<!-- wp:heading -->" in content
    assert spec["title"] == "Family Dental Services"
    assert spec["slug"] == "family-dental-services"
    assert state["lastWordPress"]["type"] == "wordpress-package"
    assert state["lastWordPress"]["slug"] == "family-dental-services"


def test_wordpress_preview_uses_package_and_records_history(tmp_path, monkeypatch):
    module = load_module()
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
    project_dir = Path(generated["projectDir"])
    package = run_script(
        "wordpress-package",
        "--project-dir",
        str(project_dir),
        "--title",
        "Family Dental Services",
        "--slug",
        "family-dental-services",
    )

    calls = {}

    def fake_publish(**kwargs):
        calls.update(kwargs)
        return {
            "ok": True,
            "siteletUrl": "https://sitelet.example/sitelet/wp-1",
            "generatedUrl": "https://sitelet.example/generated/wp-1",
        }

    monkeypatch.setattr(module, "publish_wordpress_preview", fake_publish)
    result = module.wordpress_preview(
        argparse.Namespace(
            project_dir=str(project_dir),
            spec=package["specPath"],
            title="",
            slug="",
            status="",
            site_name="Acme WP",
            excerpt="",
            content="",
            content_file="",
            sitelet_base_url="https://sitelet.example",
            sitelet_api_token="token",
        )
    )

    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["preview"]["siteletUrl"] == "https://sitelet.example/sitelet/wp-1"
    assert calls["title"] == "Family Dental Services"
    assert calls["slug"] == "family-dental-services"
    assert "<!-- wp:heading -->" in calls["content"]
    assert state["lastWordPress"]["type"] == "wordpress-preview"
    assert state["lastWordPress"]["siteletUrl"] == "https://sitelet.example/sitelet/wp-1"


def test_wordpress_publish_requires_explicit_approval(tmp_path):
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
    project_dir = Path(generated["projectDir"])
    package = run_script(
        "wordpress-package",
        "--project-dir",
        str(project_dir),
        "--title",
        "Family Dental Services",
        "--slug",
        "family-dental-services",
    )

    result = run_script(
        "wordpress-publish",
        "--project-dir",
        str(project_dir),
        "--spec",
        package["specPath"],
        "--mcp-url",
        "https://wp.example/wp-json/hermes-mcp/v1/mcp",
        "--mcp-token",
        "token",
        check=False,
    )

    assert result["ok"] is False
    assert "requires explicit approval" in result["error"]


def test_wordpress_publish_calls_mcp_and_records_history(tmp_path, monkeypatch):
    module = load_module()
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
    project_dir = Path(generated["projectDir"])
    package = run_script(
        "wordpress-package",
        "--project-dir",
        str(project_dir),
        "--title",
        "Family Dental Services",
        "--slug",
        "family-dental-services",
    )
    calls = {}

    def fake_publish(**kwargs):
        calls.update(kwargs)
        return {
            "ok": True,
            "id": 42,
            "status": "draft",
            "edit_link": "https://wp.example/wp-admin/post.php?post=42&action=edit",
            "link": "https://wp.example/family-dental-services/",
            "tool": "create_draft_page",
        }

    monkeypatch.setattr(module, "publish_wordpress_content", fake_publish)
    result = module.wordpress_publish(
        argparse.Namespace(
            project_dir=str(project_dir),
            spec=package["specPath"],
            title="",
            slug="",
            status="",
            excerpt="",
            content="",
            content_file="",
            content_type="page",
            wordpress_id=0,
            no_update_existing=False,
            mcp_url="https://wp.example/wp-json/hermes-mcp/v1/mcp",
            mcp_token="token",
            approved=True,
        )
    )

    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["wordpress"]["id"] == 42
    assert calls["title"] == "Family Dental Services"
    assert calls["slug"] == "family-dental-services"
    assert calls["content_type"] == "page"
    assert calls["update_existing"] is True
    assert "<!-- wp:heading -->" in calls["content"]
    assert state["lastWordPress"]["type"] == "wordpress-publish"
    assert state["lastWordPress"]["wordpressId"] == 42


def test_approval_request_and_record_update_state(tmp_path):
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
    project_dir = Path(generated["projectDir"])

    request = run_script(
        "approval-request",
        "--project-dir",
        str(project_dir),
        "--target",
        "wordpress-publish",
        "--reference",
        "dist/hermes-wordpress/home.json",
        "--summary",
        "Approve WordPress Home draft",
        "--preview-url",
        "https://sitelet.example/sitelet/home",
    )
    decision = run_script(
        "approval-record",
        "--project-dir",
        str(project_dir),
        "--target",
        "wordpress-publish",
        "--reference",
        "dist/hermes-wordpress/home.json",
        "--decision",
        "approved",
        "--approver",
        "client",
        "--notes",
        "Looks good",
    )

    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert request["approval"]["decision"] == "pending"
    assert decision["approval"]["decision"] == "approved"
    assert state["workflowState"] == "approved_for_publish"
    assert state["lastApproval"]["approver"] == "client"


def test_wordpress_publish_accepts_recorded_approval(tmp_path, monkeypatch):
    module = load_module()
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
    project_dir = Path(generated["projectDir"])
    package = run_script(
        "wordpress-package",
        "--project-dir",
        str(project_dir),
        "--title",
        "Family Dental Services",
        "--slug",
        "family-dental-services",
    )
    run_script(
        "approval-record",
        "--project-dir",
        str(project_dir),
        "--target",
        "wordpress-publish",
        "--reference",
        package["specPath"],
        "--decision",
        "approved",
    )

    monkeypatch.setattr(
        module,
        "publish_wordpress_content",
        lambda **kwargs: {
            "ok": True,
            "id": 42,
            "status": "draft",
            "edit_link": "https://wp.example/wp-admin/post.php?post=42&action=edit",
            "link": "https://wp.example/family-dental-services/",
            "tool": "create_draft_page",
        },
    )
    result = module.wordpress_publish(
        argparse.Namespace(
            project_dir=str(project_dir),
            spec=package["specPath"],
            title="",
            slug="",
            status="",
            excerpt="",
            content="",
            content_file="",
            content_type="page",
            wordpress_id=0,
            no_update_existing=False,
            mcp_url="https://wp.example/wp-json/hermes-mcp/v1/mcp",
            mcp_token="token",
            approved=False,
        )
    )

    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert state["workflowState"] == "published"
    assert state["lastWordPress"]["approval"].startswith("wordpress-publish-")


def test_publish_wordpress_content_updates_existing_page(monkeypatch):
    module = load_module()
    calls = []

    def fake_call(endpoint, api_token, name, arguments):
        calls.append((name, arguments))
        if name == "list_pages":
            return {"items": [{"id": 77, "title": "Family Dental Services", "slug": "family-dental-services"}]}
        return {
            "id": arguments["id"],
            "status": arguments["status"],
            "edit_link": "https://wp.example/wp-admin/post.php?post=77&action=edit",
            "link": "https://wp.example/family-dental-services/",
        }

    monkeypatch.setattr(module, "call_wordpress_mcp_tool", fake_call)
    result = module.publish_wordpress_content(
        endpoint="https://wp.example/wp-json/hermes-mcp/v1/mcp",
        api_token="token",
        title="Family Dental Services",
        content="<p>Updated</p>",
        slug="family-dental-services",
        excerpt="",
        status="pending",
        content_type="page",
        wordpress_id=0,
        update_existing=True,
    )

    assert result["ok"] is True
    assert result["tool"] == "update_page"
    assert calls[0][0] == "list_pages"
    assert calls[1][0] == "update_page"
    assert calls[1][1]["id"] == 77


def test_review_build_creates_dashboard_and_client_review(tmp_path):
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
        "--pages",
        "home,about,services",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(generated["projectDir"])
    run_script("qa", "--project-dir", str(project_dir))
    run_script(
        "approval-request",
        "--project-dir",
        str(project_dir),
        "--target",
        "deploy",
        "--summary",
        "Approve final preview",
        "--preview-url",
        "https://preview.example/acme",
    )

    result = run_script(
        "review-build",
        "--project-dir",
        str(project_dir),
        "--public-preview-url",
        "https://preview.example/acme",
        "--client-name",
        "Acme Team",
    )

    dashboard = project_dir / "dist" / "hermes-review" / "index.html"
    client = project_dir / "dist" / "hermes-review" / "client-review.html"
    review_state = json.loads((project_dir / "dist" / "hermes-review" / "state.json").read_text(encoding="utf-8"))
    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert dashboard.exists()
    assert client.exists()
    assert "Acme Dental" in dashboard.read_text(encoding="utf-8")
    assert "Open Client Review" in dashboard.read_text(encoding="utf-8")
    assert "https://preview.example/acme" in client.read_text(encoding="utf-8")
    assert review_state["clientName"] == "Acme Team"
    assert [page["slug"] for page in review_state["pages"]] == ["home", "about", "services"]
    assert state["lastReview"]["type"] == "review-build"


def test_review_comment_records_client_feedback(tmp_path):
    generated = run_script(
        "create-site",
        "--name",
        "Acme Dental",
        "--description",
        "Family dental clinic for busy parents.",
        "--platform",
        "static",
        "--output-dir",
        str(tmp_path),
    )
    project_dir = Path(generated["projectDir"])

    result = run_script(
        "review-comment",
        "--project-dir",
        str(project_dir),
        "--page",
        "home",
        "--author",
        "client",
        "--decision",
        "revision_requested",
        "--comment",
        "Make the hero more premium.",
    )

    state = json.loads((project_dir / "docs" / "hermes-website-state.json").read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert state["workflowState"] == "revision_requested"
    assert state["reviewComments"][0]["page"] == "home"
    assert state["reviewComments"][0]["comment"] == "Make the hero more premium."
