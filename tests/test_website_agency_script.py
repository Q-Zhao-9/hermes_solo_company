import importlib.util
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


def run_script(*args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        check=True,
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
