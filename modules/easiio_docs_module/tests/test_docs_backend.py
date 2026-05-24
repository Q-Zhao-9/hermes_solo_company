import importlib
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


class DocsBackendPhase1Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "docs.db"
        os.environ["EASIIO_DOCS_DB"] = str(self.db_path)
        self.rag_store_path = Path(self.tmp.name) / "rag_content.json"
        os.environ["EASIIO_CHATBOT_RAG_STORE"] = str(self.rag_store_path)
        for module in ["app", "docs_db", "docs_rag"]:
            if module in sys.modules:
                del sys.modules[module]
        self.db = importlib.import_module("docs_db")
        self.app = importlib.import_module("app")
        self.store = self.db.DocsStore(self.db_path)

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("EASIIO_DOCS_DB", None)
        os.environ.pop("EASIIO_CHATBOT_RAG_STORE", None)
        os.environ.pop("EASIIO_DOCS_OWNER_TOKEN", None)
        for module in ["app", "docs_db", "docs_rag"]:
            if module in sys.modules:
                del sys.modules[module]

    def request(self, method, route, payload=None, raw=False, headers=None):
        body = b""
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
        response = self.app.handle_request(method, route, body=body, headers=headers or {})
        if raw:
            return response
        return response.status, json.loads(response.body.decode("utf-8") or "{}")

    def get(self, route, **params):
        query = urlencode(params)
        return self.request("GET", f"{route}?{query}" if query else route)

    def sample_doc(self, **overrides):
        payload = {
            "site_id": "ai-solo-company",
            "slug": "getting-started",
            "title": "Getting Started with AI Solo Company",
            "summary": "Onboarding guide for the AI Solo Company website.",
            "content": "# Getting Started\nUse this documentation module across websites.",
            "content_format": "markdown",
            "status": "published",
            "visibility": "public",
            "category": "Guide",
            "tags": ["onboarding", "docs"],
            "version_label": "1.0",
            "locale": "en",
            "framework_targets": ["nextjs-mdx", "wordpress-shortcode", "docusaurus", "mkdocs", "hugo", "vitepress", "sitelet"],
            "rag_enabled": True,
            "changed_by": "phase1-test",
        }
        payload.update(overrides)
        return payload

    def test_store_upserts_lists_searches_and_isolates_docs_by_site(self):
        created = self.store.upsert_doc(self.sample_doc())
        self.store.upsert_doc(self.sample_doc(site_id="factory-site", title="Factory Getting Started", content="Factory only content."))

        self.assertEqual(created["site_id"], "ai-solo-company")
        self.assertEqual(created["slug"], "getting-started")
        self.assertEqual(created["visibility"], "public")
        self.assertEqual(created["framework_targets"], ["nextjs-mdx", "wordpress-shortcode", "docusaurus", "mkdocs", "hugo", "vitepress", "sitelet"])

        ai_docs = self.store.list_docs("ai-solo-company", q="documentation", status="published")
        factory_docs = self.store.list_docs("factory-site", q="documentation", status="published")
        self.assertEqual([doc["title"] for doc in ai_docs], ["Getting Started with AI Solo Company"])
        self.assertEqual(factory_docs, [])

    def test_store_tracks_revision_history_and_versions(self):
        self.store.upsert_doc(self.sample_doc(version_label="1.0", content="Version one"))
        self.store.upsert_doc(self.sample_doc(version_label="1.1", content="Version two"))

        revisions = self.store.list_revisions("ai-solo-company", "getting-started")
        self.assertEqual(len(revisions), 2)
        self.assertEqual(revisions[0]["version_label"], "1.1")
        self.assertEqual(revisions[0]["content"], "Version two")
        self.assertEqual(revisions[1]["version_label"], "1.0")

    def test_http_api_create_get_list_search_delete_and_revision_flow(self):
        status, created = self.request("POST", "/api/docs/doc", self.sample_doc())
        self.assertEqual(status, 200)
        self.assertTrue(created["ok"])
        self.assertEqual(created["doc"]["site_id"], "ai-solo-company")

        status, listed = self.get("/api/docs/docs", site_id="ai-solo-company", q="onboarding", status="published")
        self.assertEqual(status, 200)
        self.assertEqual(len(listed["docs"]), 1)
        self.assertEqual(listed["docs"][0]["slug"], "getting-started")

        status, doc = self.get("/api/docs/doc", site_id="ai-solo-company", slug="getting-started")
        self.assertEqual(status, 200)
        self.assertIn("documentation module", doc["doc"]["content"])

        self.request("POST", "/api/docs/doc", self.sample_doc(content="Second revision", version_label="1.1"))
        status, revisions = self.get("/api/docs/revisions", site_id="ai-solo-company", slug="getting-started")
        self.assertEqual(status, 200)
        self.assertEqual(len(revisions["revisions"]), 2)

        status, deleted = self.request("POST", "/api/docs/doc/delete", {"site_id": "ai-solo-company", "slug": "getting-started"})
        self.assertEqual(status, 200)
        self.assertTrue(deleted["deleted"])
        status, _ = self.get("/api/docs/doc", site_id="ai-solo-company", slug="getting-started")
        self.assertEqual(status, 404)

    def test_http_api_validates_required_fields_and_supported_values(self):
        status, body = self.request("POST", "/api/docs/doc", {"site_id": "ai-solo-company", "title": "Missing slug", "content": "x"})
        self.assertEqual(status, 400)
        self.assertIn("slug", body["error"])

        created = self.store.upsert_doc(self.sample_doc(status="unknown", visibility="external", content_format="weird", framework_targets=["bad", "mkdocs"]))
        self.assertEqual(created["status"], "draft")
        self.assertEqual(created["visibility"], "public")
        self.assertEqual(created["content_format"], "markdown")
        self.assertEqual(created["framework_targets"], ["mkdocs"])

    def test_space_summary_returns_site_metadata_and_counts(self):
        self.store.upsert_doc(self.sample_doc(slug="getting-started", status="published", visibility="public", category="Guide"))
        self.store.upsert_doc(self.sample_doc(slug="draft-plan", title="Draft Plan", status="draft", visibility="private", category="Plan"))

        summary = self.store.get_space_summary("ai-solo-company")
        self.assertEqual(summary["site_id"], "ai-solo-company")
        self.assertEqual(summary["total_docs"], 2)
        self.assertEqual(summary["status_counts"], {"draft": 1, "published": 1})
        self.assertEqual(summary["visibility_counts"], {"private": 1, "public": 1})
        self.assertEqual(summary["categories"], ["Guide", "Plan"])

        status, body = self.get("/api/docs/space", site_id="ai-solo-company")
        self.assertEqual(status, 200)
        self.assertEqual(body["space"]["total_docs"], 2)

    def test_phase2_serves_embed_assets_and_cors_preflight(self):
        js = self.request("GET", "/docs/docs.js", raw=True)
        self.assertEqual(js.status, 200)
        self.assertIn("application/javascript", js.headers.get("Content-Type", ""))
        self.assertEqual(js.headers.get("Access-Control-Allow-Origin"), "*")
        self.assertIn(b"data-easiio-docs", js.body)
        self.assertIn(b"window.EasiioDocs", js.body)

        css = self.request("GET", "/docs/docs.css", raw=True)
        self.assertEqual(css.status, 200)
        self.assertIn("text/css", css.headers.get("Content-Type", ""))
        self.assertEqual(css.headers.get("Access-Control-Allow-Origin"), "*")
        self.assertIn(b".easiio-docs", css.body)

        demo = self.request("GET", "/docs/demo.html", raw=True)
        self.assertEqual(demo.status, 200)
        self.assertIn("text/html", demo.headers.get("Content-Type", ""))
        self.assertIn(b"data-easiio-docs", demo.body)

        options = self.request("OPTIONS", "/api/docs/docs", raw=True)
        self.assertEqual(options.status, 204)
        self.assertEqual(options.headers.get("Access-Control-Allow-Origin"), "*")
        self.assertIn("GET", options.headers.get("Access-Control-Allow-Methods", ""))
        self.assertIn("POST", options.headers.get("Access-Control-Allow-Methods", ""))

    def test_phase7_serves_admin_export_ui_assets(self):
        health_status, health = self.get("/health")
        self.assertEqual(health_status, 200)
        self.assertEqual(health["phase"], "25-v1-release")
        self.assertIn("20-connector-dry-run", health.get("phaseHistory", []))
        self.assertFalse(health["adminAuthConfigured"])

        html = self.request("GET", "/docs/admin.html", raw=True)
        self.assertEqual(html.status, 200)
        self.assertIn("text/html", html.headers.get("Content-Type", ""))
        self.assertIn(b"data-easiio-docs-admin", html.body)
        self.assertIn(b"Easiio Docs Admin", html.body)

        js = self.request("GET", "/docs/admin.js", raw=True)
        self.assertEqual(js.status, 200)
        self.assertIn("application/javascript", js.headers.get("Content-Type", ""))
        self.assertIn(b"/api/docs/export/preview", js.body)
        self.assertIn(b"confirmExportPackage", js.body)

        css = self.request("GET", "/docs/admin.css", raw=True)
        self.assertEqual(css.status, 200)
        self.assertIn("text/css", css.headers.get("Content-Type", ""))
        self.assertIn(b".easiio-docs-admin", css.body)

    def test_phase8_owner_token_protects_admin_assets_and_write_endpoints(self):
        os.environ["EASIIO_DOCS_OWNER_TOKEN"] = "phase8-owner-token"
        if "app" in sys.modules:
            del sys.modules["app"]
        self.app = importlib.import_module("app")
        auth = {"Authorization": "Bearer phase8-owner-token"}

        status, health = self.get("/health")
        self.assertEqual(status, 200)
        self.assertEqual(health["phase"], "25-v1-release")
        self.assertIn("20-connector-dry-run", health.get("phaseHistory", []))
        self.assertTrue(health["adminAuthConfigured"])

        denied_html = self.request("GET", "/docs/admin.html", raw=True)
        self.assertEqual(denied_html.status, 401)
        self.assertIn(b"owner token", denied_html.body)

        allowed_html = self.request("GET", "/docs/admin.html", raw=True, headers=auth)
        self.assertEqual(allowed_html.status, 200)
        self.assertIn(b"Easiio Docs Admin", allowed_html.body)

        denied_create_status, denied_create = self.request("POST", "/api/docs/doc", self.sample_doc())
        self.assertEqual(denied_create_status, 401)
        self.assertTrue(denied_create["authRequired"])

        allowed_create_status, allowed_create = self.request("POST", "/api/docs/doc", self.sample_doc(), headers=auth)
        self.assertEqual(allowed_create_status, 200)
        self.assertTrue(allowed_create["ok"])

        denied_package_status, denied_package = self.request("POST", "/api/docs/export/package", {"site_id": "ai-solo-company", "target": "docusaurus", "confirmExportPackage": True})
        self.assertEqual(denied_package_status, 401)
        self.assertTrue(denied_package["authRequired"])

        allowed_package_status, allowed_package = self.request("POST", "/api/docs/export/package", {"site_id": "ai-solo-company", "target": "docusaurus", "confirmExportPackage": True}, headers=auth)
        self.assertEqual(allowed_package_status, 200)
        self.assertFalse(allowed_package["packageBlocked"])

    def test_phase8_private_and_draft_reads_require_owner_token_when_configured(self):
        self.store.upsert_doc(self.sample_doc(slug="public-guide", title="Public Guide"))
        self.store.upsert_doc(self.sample_doc(slug="private-plan", title="Private Plan", visibility="private"))
        self.store.upsert_doc(self.sample_doc(slug="draft-plan", title="Draft Plan", status="draft"))
        os.environ["EASIIO_DOCS_OWNER_TOKEN"] = "phase8-owner-token"
        if "app" in sys.modules:
            del sys.modules["app"]
        self.app = importlib.import_module("app")
        auth = {"Authorization": "Bearer phase8-owner-token"}

        status, public_doc = self.get("/api/docs/doc", site_id="ai-solo-company", slug="public-guide")
        self.assertEqual(status, 200)
        self.assertEqual(public_doc["doc"]["slug"], "public-guide")

        status, private_denied = self.get("/api/docs/doc", site_id="ai-solo-company", slug="private-plan")
        self.assertEqual(status, 401)
        self.assertTrue(private_denied["authRequired"])

        status, draft_denied = self.get("/api/docs/docs", site_id="ai-solo-company", status="draft")
        self.assertEqual(status, 401)
        self.assertTrue(draft_denied["authRequired"])

        status, draft_allowed = self.request("GET", "/api/docs/docs?site_id=ai-solo-company&status=draft", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual([doc["slug"] for doc in draft_allowed["docs"]], ["draft-plan"])

    def test_phase3_builds_sitelet_preview_payload_for_docs_space(self):
        self.store.upsert_doc(self.sample_doc(slug="getting-started", title="Getting Started", category="Guide"))
        self.store.upsert_doc(self.sample_doc(slug="wordpress-integration", title="WordPress Integration", category="Integration", framework_targets=["wordpress-shortcode", "sitelet"]))
        self.store.upsert_doc(self.sample_doc(slug="private-plan", title="Private Plan", status="published", visibility="private"))

        status, body = self.get("/api/docs/sitelet-preview", site_id="ai-solo-company", target="sitelet")
        self.assertEqual(status, 200)
        self.assertEqual(body["exportType"], "easiio-docs-sitelet-preview")
        self.assertTrue(body["requiresUploadApproval"])
        self.assertTrue(body["uploadBlocked"])
        payload = body["siteletPayload"]
        self.assertEqual(payload["source"], "easiio-docs-module")
        self.assertEqual(payload["kind"], "site")
        paths = [page["path"] for page in payload["pages"]]
        self.assertIn("/", paths)
        self.assertIn("/getting-started.html", paths)
        self.assertIn("/wordpress-integration.html", paths)
        self.assertNotIn("/private-plan.html", paths)
        self.assertIn("/assets/easiio-docs-preview.css", [asset["path"] for asset in payload["assets"]])
        home = next(page for page in payload["pages"] if page["path"] == "/")
        self.assertIn("Easiio Docs Sitelet Preview", home["html"])
        self.assertIn("WordPress Integration", home["html"])
        self.assertIn("siteletPayload", body["uploadInstructions"]["step"])

    def test_phase3_builds_single_doc_preview_and_upload_is_confirmation_gated(self):
        self.store.upsert_doc(self.sample_doc(slug="single-doc", title="Single Doc", content="# Single Doc\nPreview me."))

        status, body = self.get("/api/docs/sitelet-preview", site_id="ai-solo-company", slug="single-doc")
        self.assertEqual(status, 200)
        self.assertEqual(body["previewScope"], "single-doc")
        paths = [page["path"] for page in body["siteletPayload"]["pages"]]
        self.assertEqual(paths, ["/"])
        self.assertIn("Single Doc", body["siteletPayload"]["pages"][0]["html"])

        status, denied = self.request("POST", "/api/docs/sitelet-preview/upload", {"site_id": "ai-solo-company"})
        self.assertEqual(status, 409)
        self.assertTrue(denied["requiresUploadApproval"])
        self.assertTrue(denied["uploadBlocked"])

    def test_phase4_builds_wordpress_shortcode_and_draft_plan(self):
        self.store.upsert_doc(self.sample_doc(slug="getting-started", title="Getting Started", category="Guide", framework_targets=["wordpress-shortcode", "sitelet"]))
        self.store.upsert_doc(self.sample_doc(slug="private-plan", title="Private Plan", status="published", visibility="private", framework_targets=["wordpress-shortcode"]))

        status, shortcode = self.get("/api/docs/wordpress/shortcode", site_id="ai-solo-company", mode="public", require_login="true")
        self.assertEqual(status, 200)
        self.assertEqual(shortcode["exportType"], "easiio-docs-wordpress-shortcode")
        self.assertIn('[easiio_docs site_id="ai-solo-company"', shortcode["shortcode"])
        self.assertIn('require_login="true"', shortcode["shortcode"])
        self.assertIn("data-easiio-docs", shortcode["embedHtml"])
        self.assertTrue(shortcode["requiresWordPressPlugin"])

        status, plan = self.get("/api/docs/wordpress/draft-plan", site_id="ai-solo-company", target="wordpress-shortcode")
        self.assertEqual(status, 200)
        self.assertEqual(plan["exportType"], "easiio-docs-wordpress-draft-plan")
        self.assertTrue(plan["requiresHumanApproval"])
        self.assertTrue(plan["publishBlocked"])
        steps = plan["draftSteps"]
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0]["mcpTool"], "mcp_easiio_wp_create_draft_post")
        self.assertEqual(steps[0]["arguments"]["status"], "draft")
        self.assertIn("<!-- wp:html -->", steps[0]["arguments"]["content"])
        self.assertIn("Getting Started", steps[0]["arguments"]["content"])
        self.assertNotIn("Private Plan", steps[0]["arguments"]["content"])

    def test_phase4_wordpress_draft_execution_is_confirmation_gated(self):
        self.store.upsert_doc(self.sample_doc(slug="wp-doc", title="WP Doc", framework_targets=["wordpress-shortcode"]))

        status, denied = self.request("POST", "/api/docs/wordpress/draft-execution", {"site_id": "ai-solo-company"})
        self.assertEqual(status, 409)
        self.assertTrue(denied["requiresHumanApproval"])
        self.assertTrue(denied["publishBlocked"])

        status, ready = self.request("POST", "/api/docs/wordpress/draft-execution", {"site_id": "ai-solo-company", "confirmDraftCreation": True, "approvedBy": "phase4-test"})
        self.assertEqual(status, 200)
        self.assertEqual(ready["exportType"], "easiio-docs-wordpress-draft-execution")
        self.assertEqual(ready["executionMode"], "hermes-mcp-handoff")
        self.assertTrue(ready["publishBlocked"])
        self.assertEqual(ready["draftSteps"][0]["mcpTool"], "mcp_easiio_wp_create_draft_post")

    def test_phase5_builds_rag_preview_only_for_public_published_rag_docs(self):
        self.store.upsert_doc(self.sample_doc(slug="rag-guide", title="RAG Guide", content="# RAG Guide\nThis public published document should sync into chatbot RAG. It has enough content to produce a useful chunk.", framework_targets=["rag", "sitelet"], rag_enabled=True))
        self.store.upsert_doc(self.sample_doc(slug="no-rag", title="No RAG", content="Do not sync me", framework_targets=["rag"], rag_enabled=False))
        self.store.upsert_doc(self.sample_doc(slug="private-rag", title="Private RAG", content="Private content", visibility="private", framework_targets=["rag"], rag_enabled=True))
        self.store.upsert_doc(self.sample_doc(slug="draft-rag", title="Draft RAG", content="Draft content", status="draft", framework_targets=["rag"], rag_enabled=True))

        status, preview = self.get("/api/docs/rag/preview", site_id="ai-solo-company")
        self.assertEqual(status, 200)
        self.assertEqual(preview["exportType"], "easiio-docs-rag-preview")
        self.assertTrue(preview["syncBlocked"])
        self.assertTrue(preview["requiresSyncApproval"])
        self.assertEqual(preview["documentCount"], 1)
        self.assertGreaterEqual(preview["chunkCount"], 1)
        chunk = preview["chunks"][0]
        self.assertEqual(chunk["site_id"], "ai-solo-company")
        self.assertEqual(chunk["source"], "easiio-docs-module")
        self.assertEqual(chunk["content_id"], "easiio-docs:ai-solo-company:rag-guide")
        self.assertEqual(chunk["title"], "RAG Guide")
        self.assertIn("RAG Guide", chunk["content"])
        self.assertNotIn("Private RAG", json.dumps(preview))
        self.assertNotIn("Draft RAG", json.dumps(preview))
        self.assertNotIn("No RAG", json.dumps(preview))

    def test_phase5_rag_sync_is_confirmation_gated_and_writes_chatbot_store(self):
        self.store.upsert_doc(self.sample_doc(
            slug="rag-guide",
            title="RAG Guide",
            content="# RAG Guide\nThis document syncs to chatbot RAG. It should be written to the chatbot manual knowledge store.",
            framework_targets=["rag"],
            rag_enabled=True,
        ))
        self.store.upsert_doc(self.sample_doc(
            slug="existing-doc",
            title="Existing Doc",
            content="Existing external item should remain in store.",
            framework_targets=["rag"],
            rag_enabled=True,
        ))
        existing_store = {
            "version": 1,
            "sites": {
                "ai-solo-company": [
                    {"content_id": "manual-existing", "title": "Manual Existing", "url": "https://example.com/manual", "content": "Manual item", "created_at": 1, "updated_at": 1},
                    {"content_id": "easiio-docs:ai-solo-company:old", "title": "Old Docs Sync", "url": "easiio-docs://ai-solo-company/old", "content": "old", "created_at": 1, "updated_at": 1},
                ],
                "other-site": [
                    {"content_id": "other", "title": "Other", "url": "https://example.com/other", "content": "Other content", "created_at": 1, "updated_at": 1}
                ],
            },
        }
        self.rag_store_path.write_text(json.dumps(existing_store), encoding="utf-8")

        status, denied = self.request("POST", "/api/docs/rag/sync", {"site_id": "ai-solo-company"})
        self.assertEqual(status, 409)
        self.assertTrue(denied["requiresSyncApproval"])
        self.assertTrue(denied["syncBlocked"])

        status, synced = self.request("POST", "/api/docs/rag/sync", {"site_id": "ai-solo-company", "confirmRagSync": True, "approvedBy": "phase5-test"})
        self.assertEqual(status, 200)
        self.assertEqual(synced["exportType"], "easiio-docs-rag-sync-result")
        self.assertEqual(synced["storePath"], str(self.rag_store_path))
        self.assertGreaterEqual(synced["syncedCount"], 2)
        self.assertFalse(synced["syncBlocked"])
        persisted = json.loads(self.rag_store_path.read_text(encoding="utf-8"))
        site_items = persisted["sites"]["ai-solo-company"]
        ids = {item["content_id"] for item in site_items}
        self.assertIn("manual-existing", ids)
        self.assertIn("easiio-docs:ai-solo-company:rag-guide", ids)
        self.assertIn("easiio-docs:ai-solo-company:existing-doc", ids)
        self.assertNotIn("easiio-docs:ai-solo-company:old", ids)
        self.assertEqual(persisted["sites"]["other-site"][0]["content_id"], "other")

    def test_phase6_builds_framework_export_preview_for_multiple_targets(self):
        self.store.upsert_doc(self.sample_doc(
            slug="getting-started",
            title="Getting Started",
            summary="Start here.",
            content="# Getting Started\nUse **AI Solo Company** docs across frameworks.",
            framework_targets=["nextjs-mdx", "docusaurus", "mkdocs", "hugo", "vitepress", "static-html"],
            rag_enabled=True,
        ))
        self.store.upsert_doc(self.sample_doc(
            slug="private-plan",
            title="Private Plan",
            content="Private content should not export by default.",
            visibility="private",
            framework_targets=["nextjs-mdx", "docusaurus", "mkdocs", "hugo", "vitepress", "static-html"],
        ))

        for target, expected_path in [
            ("nextjs-mdx", "content/docs/getting-started.mdx"),
            ("docusaurus", "docs/getting-started.md"),
            ("mkdocs", "docs/getting-started.md"),
            ("hugo", "content/docs/getting-started.md"),
            ("vitepress", "docs/getting-started.md"),
            ("static-html", "getting-started.html"),
        ]:
            status, preview = self.get("/api/docs/export/preview", site_id="ai-solo-company", target=target)
            self.assertEqual(status, 200, target)
            self.assertEqual(preview["exportType"], "easiio-docs-framework-export-preview")
            self.assertTrue(preview["packageBlocked"])
            self.assertTrue(preview["requiresExportApproval"])
            self.assertEqual(preview["target"], target)
            self.assertEqual(preview["documentCount"], 1)
            paths = [file["path"] for file in preview["files"]]
            self.assertIn(expected_path, paths)
            self.assertNotIn("private-plan", json.dumps(preview))
            manifest = next(file for file in preview["files"] if file["path"] == "easiio-docs-export-manifest.json")
            self.assertIn('"site_id": "ai-solo-company"', manifest["content"])

    def test_phase6_export_package_is_confirmation_gated_and_writes_zip(self):
        self.store.upsert_doc(self.sample_doc(
            slug="getting-started",
            title="Getting Started",
            content="# Getting Started\nPackage me for Docusaurus.",
            framework_targets=["docusaurus"],
        ))

        status, denied = self.request("POST", "/api/docs/export/package", {"site_id": "ai-solo-company", "target": "docusaurus"})
        self.assertEqual(status, 409)
        self.assertTrue(denied["requiresExportApproval"])
        self.assertTrue(denied["packageBlocked"])

        status, packaged = self.request("POST", "/api/docs/export/package", {"site_id": "ai-solo-company", "target": "docusaurus", "confirmExportPackage": True, "approvedBy": "phase6-test"})
        self.assertEqual(status, 200)
        self.assertEqual(packaged["exportType"], "easiio-docs-framework-export-package")
        self.assertFalse(packaged["packageBlocked"])
        self.assertEqual(packaged["target"], "docusaurus")
        self.assertTrue(Path(packaged["packagePath"]).exists())
        self.assertGreater(packaged["packageSize"], 0)
        self.assertIn("docs/getting-started.md", packaged["filePaths"])

    def test_phase10_portable_bundle_preview_and_package_are_confirmation_gated(self):
        self.store.upsert_doc(self.sample_doc(slug="public-guide", title="Public Guide", framework_targets=["sitelet", "static-html"]))
        self.store.upsert_doc(self.sample_doc(slug="private-plan", title="Private Plan", visibility="private", framework_targets=["sitelet"]))

        status, preview = self.get("/api/docs/bundle/preview", site_id="ai-solo-company")
        self.assertEqual(status, 200)
        self.assertEqual(preview["exportType"], "easiio-docs-portable-bundle-preview")
        self.assertTrue(preview["bundleBlocked"])
        self.assertTrue(preview["requiresBundleApproval"])
        self.assertEqual(preview["documentCount"], 1)
        self.assertEqual(preview["documents"][0]["slug"], "public-guide")
        self.assertNotIn("Private Plan", json.dumps(preview))

        status, denied = self.request("POST", "/api/docs/bundle/package", {"site_id": "ai-solo-company"})
        self.assertEqual(status, 409)
        self.assertTrue(denied["requiresBundleApproval"])

        status, packaged = self.request("POST", "/api/docs/bundle/package", {"site_id": "ai-solo-company", "confirmBundlePackage": True, "approvedBy": "phase10-test"})
        self.assertEqual(status, 200)
        self.assertEqual(packaged["exportType"], "easiio-docs-portable-bundle-package")
        self.assertFalse(packaged["bundleBlocked"])
        self.assertTrue(Path(packaged["packagePath"]).exists())
        self.assertIn("easiio-docs-bundle.json", packaged["filePaths"])

    def test_phase10_import_preview_detects_conflicts_and_execute_is_confirmation_gated(self):
        self.store.upsert_doc(self.sample_doc(slug="existing", title="Existing Doc"))
        files = [
            {"path": "docs/existing.md", "content": "---\ntitle: Existing Imported\ncategory: Imported\ntags: [alpha, beta]\n---\n# Existing Imported\nUpdated content."},
            {"path": "docs/new-guide.md", "content": "# New Guide\nImported from Docusaurus."},
        ]
        payload = {"site_id": "ai-solo-company", "source_format": "docusaurus", "files": files, "default_status": "draft", "default_visibility": "private"}

        status, preview = self.request("POST", "/api/docs/import/preview", payload)
        self.assertEqual(status, 200)
        self.assertEqual(preview["exportType"], "easiio-docs-import-preview")
        self.assertTrue(preview["importBlocked"])
        self.assertTrue(preview["requiresImportApproval"])
        self.assertEqual(preview["documentCount"], 2)
        conflicts = [doc for doc in preview["documents"] if doc["conflict"]]
        self.assertEqual([doc["slug"] for doc in conflicts], ["existing"])

        status, denied = self.request("POST", "/api/docs/import/execute", payload)
        self.assertEqual(status, 409)
        self.assertTrue(denied["requiresImportApproval"])

        execute_payload = {**payload, "confirmImport": True, "approvedBy": "phase10-test"}
        status, imported = self.request("POST", "/api/docs/import/execute", execute_payload)
        self.assertEqual(status, 200)
        self.assertEqual(imported["exportType"], "easiio-docs-import-result")
        self.assertFalse(imported["importBlocked"])
        self.assertEqual(imported["importedCount"], 2)
        created = self.store.get_doc("ai-solo-company", "new-guide")
        self.assertEqual(created["status"], "draft")
        self.assertEqual(created["visibility"], "private")
        self.assertIn("Imported from Docusaurus", created["content"])

    def test_phase11_locale_filtering_summary_and_fallback_doc_lookup(self):
        self.store.upsert_doc(self.sample_doc(slug="getting-started", title="Getting Started", locale="en"))
        self.store.upsert_doc(self.sample_doc(slug="empezar", title="Empezar", locale="es", content="# Empezar\nContenido en español."))
        self.store.upsert_doc(self.sample_doc(slug="billing", title="Billing", locale="en", content="# Billing\nEnglish billing only."))

        en_docs = self.store.list_docs("ai-solo-company", status="published", visibility="public", locale="en")
        es_docs = self.store.list_docs("ai-solo-company", status="published", visibility="public", locale="es")
        self.assertEqual({doc["slug"] for doc in en_docs}, {"getting-started", "billing"})
        self.assertEqual([doc["slug"] for doc in es_docs], ["empezar"])

        summary = self.store.get_space_summary("ai-solo-company")
        self.assertEqual(summary["locale_counts"], {"en": 2, "es": 1})
        self.assertEqual(summary["available_locales"], ["en", "es"])

        status, listed = self.get("/api/docs/docs", site_id="ai-solo-company", status="published", visibility="public", locale="es")
        self.assertEqual(status, 200)
        self.assertEqual([doc["slug"] for doc in listed["docs"]], ["empezar"])
        self.assertEqual(listed["locale"], "es")

        status, localized = self.get("/api/docs/doc", site_id="ai-solo-company", slug="billing", locale="es", fallback_locale="en")
        self.assertEqual(status, 200)
        self.assertTrue(localized["fallbackUsed"])
        self.assertEqual(localized["requestedLocale"], "es")
        self.assertEqual(localized["doc"]["locale"], "en")

    def test_phase11_localized_export_paths_and_import_locale_from_paths(self):
        self.store.upsert_doc(self.sample_doc(slug="getting-started", title="Getting Started", locale="en", framework_targets=["docusaurus", "static-html"]))
        self.store.upsert_doc(self.sample_doc(slug="empezar", title="Empezar", locale="es", content="# Empezar", framework_targets=["docusaurus", "static-html"]))

        status, preview = self.get("/api/docs/export/preview", site_id="ai-solo-company", target="docusaurus", locale="es")
        self.assertEqual(status, 200)
        self.assertEqual(preview["locale"], "es")
        self.assertEqual(preview["documentCount"], 1)
        paths = [file["path"] for file in preview["files"]]
        self.assertIn("i18n/es/docusaurus-plugin-content-docs/current/empezar.md", paths)
        manifest = next(file for file in preview["files"] if file["path"] == "easiio-docs-export-manifest.json")
        self.assertIn('"locale": "es"', manifest["content"])

        files = [
            {"path": "en/docs/guide.md", "content": "# English Guide\nEnglish content."},
            {"path": "es/docs/guia.md", "content": "# Guía\nContenido español."},
        ]
        payload = {"site_id": "import-locales", "source_format": "markdown-folder", "files": files, "default_status": "published", "default_visibility": "public"}
        status, preview = self.request("POST", "/api/docs/import/preview", payload)
        self.assertEqual(status, 200)
        locales = {doc["slug"]: doc["locale"] for doc in preview["documents"]}
        self.assertEqual(locales, {"guide": "en", "guia": "es"})

    def test_phase12_deployment_preview_and_package_are_confirmation_gated(self):
        self.store.upsert_doc(self.sample_doc(
            slug="deploy-guide",
            title="Deploy Guide",
            content="# Deploy Guide\nReady for deployment handoff.",
            framework_targets=["static-html", "sitelet"],
        ))
        self.store.upsert_doc(self.sample_doc(
            slug="private-deploy",
            title="Private Deploy",
            content="Private deployment content should not be included by default.",
            visibility="private",
            framework_targets=["static-html", "sitelet"],
        ))

        status, preview = self.get("/api/docs/deploy/preview", site_id="ai-solo-company", target="static-html", environment="staging")
        self.assertEqual(status, 200)
        self.assertEqual(preview["exportType"], "easiio-docs-deployment-handoff-preview")
        self.assertEqual(preview["deploymentTarget"], "static-html")
        self.assertEqual(preview["environment"], "staging")
        self.assertTrue(preview["requiresDeploymentApproval"])
        self.assertTrue(preview["deploymentBlocked"])
        self.assertEqual(preview["documentCount"], 1)
        self.assertIn("deploy-guide.html", preview["filePaths"])
        self.assertIn("easiio-docs-deployment-manifest.json", preview["filePaths"])
        self.assertNotIn("Private Deploy", json.dumps(preview))
        self.assertIn("review", preview["checklist"][0].lower())

        status, denied = self.request("POST", "/api/docs/deploy/package", {"site_id": "ai-solo-company", "target": "static-html"})
        self.assertEqual(status, 409)
        self.assertTrue(denied["requiresDeploymentApproval"])
        self.assertTrue(denied["deploymentBlocked"])

        status, packaged = self.request("POST", "/api/docs/deploy/package", {
            "site_id": "ai-solo-company",
            "target": "static-html",
            "environment": "staging",
            "confirmDeploymentPackage": True,
            "approvedBy": "phase12-test",
        })
        self.assertEqual(status, 200)
        self.assertEqual(packaged["exportType"], "easiio-docs-deployment-handoff-package")
        self.assertFalse(packaged["deploymentBlocked"])
        self.assertTrue(Path(packaged["packagePath"]).exists())
        self.assertIn("easiio-docs-deployment-manifest.json", packaged["filePaths"])
        self.assertIn("deploy-guide.html", packaged["filePaths"])


    def test_phase13_deployment_history_records_confirmed_packages_and_is_owner_protected(self):
        self.store.upsert_doc(self.sample_doc(
            slug="audit-deploy-guide",
            title="Audit Deploy Guide",
            content="# Audit Deploy Guide\nRecord this deployment handoff.",
            framework_targets=["static-html", "sitelet"],
        ))
        os.environ["EASIIO_DOCS_OWNER_TOKEN"] = "phase13-owner-token"
        if "app" in sys.modules:
            del sys.modules["app"]
        self.app = importlib.import_module("app")
        auth = {"Authorization": "Bearer phase13-owner-token"}

        status, denied_history = self.get("/api/docs/deploy/history", site_id="ai-solo-company")
        self.assertEqual(status, 401)
        self.assertTrue(denied_history["authRequired"])

        status, empty_history = self.request("GET", "/api/docs/deploy/history?site_id=ai-solo-company", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(empty_history["exportType"], "easiio-docs-deployment-history")
        self.assertEqual(empty_history["history"], [])

        status, blocked = self.request("POST", "/api/docs/deploy/package", {"site_id": "ai-solo-company", "target": "static-html"}, headers=auth)
        self.assertEqual(status, 409)

        status, packaged = self.request("POST", "/api/docs/deploy/package", {
            "site_id": "ai-solo-company",
            "target": "sitelet",
            "environment": "staging",
            "locale": "en",
            "confirmDeploymentPackage": True,
            "approvedBy": "phase13-test",
        }, headers=auth)
        self.assertEqual(status, 200)
        self.assertTrue(packaged["auditRecorded"])
        self.assertGreaterEqual(packaged["auditRecordId"], 1)

        status, history = self.request("GET", "/api/docs/deploy/history?site_id=ai-solo-company&limit=5", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(history["exportType"], "easiio-docs-deployment-history")
        self.assertEqual(history["site_id"], "ai-solo-company")
        self.assertEqual(history["count"], 1)
        record = history["history"][0]
        self.assertEqual(record["id"], packaged["auditRecordId"])
        self.assertEqual(record["event_type"], "deployment_package_created")
        self.assertEqual(record["deploymentTarget"], "sitelet")
        self.assertEqual(record["environment"], "staging")
        self.assertEqual(record["locale"], "en")
        self.assertEqual(record["approvedBy"], "phase13-test")
        self.assertEqual(record["packagePath"], packaged["packagePath"])
        self.assertIn("easiio-docs-deployment-manifest.json", record["filePaths"])
        self.assertNotIn("phase13-owner-token", json.dumps(history))


    def test_phase14_deployment_audit_summary_filters_and_csv_export(self):
        self.store.upsert_doc(self.sample_doc(
            slug="audit-ops-guide",
            title="Audit Ops Guide",
            content="# Audit Ops Guide\nUse this for Phase 14 audit operations.",
            framework_targets=["static-html", "sitelet"],
            locale="en",
        ))
        os.environ["EASIIO_DOCS_OWNER_TOKEN"] = "phase14-owner-token"
        if "app" in sys.modules:
            del sys.modules["app"]
        self.app = importlib.import_module("app")
        auth = {"Authorization": "Bearer phase14-owner-token"}

        for target, environment, locale, approver in [
            ("sitelet", "staging", "en", "phase14-sitelet"),
            ("static-html", "production", "en", "phase14-static"),
        ]:
            status, packaged = self.request("POST", "/api/docs/deploy/package", {
                "site_id": "ai-solo-company",
                "target": target,
                "environment": environment,
                "locale": locale,
                "confirmDeploymentPackage": True,
                "approvedBy": approver,
            }, headers=auth)
            self.assertEqual(status, 200)
            self.assertTrue(packaged["auditRecorded"])

        status, denied_summary = self.get("/api/docs/deploy/summary", site_id="ai-solo-company")
        self.assertEqual(status, 401)
        self.assertTrue(denied_summary["authRequired"])

        status, summary = self.request("GET", "/api/docs/deploy/summary?site_id=ai-solo-company&limit=5", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(summary["exportType"], "easiio-docs-deployment-summary")
        self.assertEqual(summary["totals"]["count"], 2)
        self.assertGreater(summary["totals"]["packageSize"], 0)
        self.assertEqual(summary["counts"]["targets"]["sitelet"], 1)
        self.assertEqual(summary["counts"]["targets"]["static-html"], 1)
        self.assertEqual(summary["counts"]["environments"]["staging"], 1)
        self.assertEqual(summary["counts"]["locales"]["en"], 2)
        self.assertEqual(len(summary["latest"]), 2)

        status, filtered = self.request("GET", "/api/docs/deploy/history?site_id=ai-solo-company&target=sitelet&environment=staging&locale=en&limit=10", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(filtered["count"], 1)
        self.assertEqual(filtered["history"][0]["deploymentTarget"], "sitelet")
        self.assertEqual(filtered["filters"]["locale"], "en")

        csv_response = self.request("GET", "/api/docs/deploy/history.csv?site_id=ai-solo-company&target=sitelet&environment=staging&locale=en", headers=auth, raw=True)
        self.assertEqual(csv_response.status, 200)
        self.assertIn("text/csv", csv_response.headers["Content-Type"])
        csv_text = csv_response.body.decode("utf-8")
        self.assertIn("id,site_id,event_type,deploymentTarget,environment,locale,packagePath,packageSize,approvedBy,created_at", csv_text.splitlines()[0])
        self.assertIn("phase14-sitelet", csv_text)
        self.assertNotIn("phase14-owner-token", csv_text)


    def test_phase15_package_detail_download_compare_and_checklist_tracking(self):
        self.store.upsert_doc(self.sample_doc(
            slug="phase15-package-guide",
            title="Phase 15 Package Guide",
            content="# Phase 15 Package Guide\nTrack package details and checklist state.",
            framework_targets=["static-html", "sitelet"],
            locale="en",
        ))
        os.environ["EASIIO_DOCS_OWNER_TOKEN"] = "phase15-owner-token"
        if "app" in sys.modules:
            del sys.modules["app"]
        self.app = importlib.import_module("app")
        auth = {"Authorization": "Bearer phase15-owner-token"}

        package_ids = []
        for target, environment, approver in [
            ("sitelet", "staging", "phase15-sitelet"),
            ("static-html", "production", "phase15-static"),
        ]:
            status, packaged = self.request("POST", "/api/docs/deploy/package", {
                "site_id": "ai-solo-company",
                "target": target,
                "environment": environment,
                "locale": "en",
                "confirmDeploymentPackage": True,
                "approvedBy": approver,
            }, headers=auth)
            self.assertEqual(status, 200)
            self.assertTrue(packaged["auditRecorded"])
            package_ids.append(packaged["auditRecordId"])

        status, denied_detail = self.get("/api/docs/deploy/package", id=str(package_ids[0]))
        self.assertEqual(status, 401)
        self.assertTrue(denied_detail["authRequired"])

        status, detail = self.request("GET", f"/api/docs/deploy/package?id={package_ids[0]}", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(detail["exportType"], "easiio-docs-deployment-package-detail")
        self.assertEqual(detail["package"]["id"], package_ids[0])
        self.assertTrue(detail["packageExists"])
        self.assertIn("easiio-docs-deployment-manifest.json", detail["manifestFiles"])
        self.assertIn("manual_review", detail["checklist"])
        self.assertFalse(detail["checklist"]["manual_review"]["completed"])

        status, updated = self.request("POST", "/api/docs/deploy/checklist", {
            "id": package_ids[0],
            "checklist": {
                "manual_review": {"completed": True, "note": "Reviewed by phase15 test"},
                "wordpress_upload": {"completed": False, "note": "Waiting for approval"},
            },
            "updatedBy": "phase15-test",
        }, headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(updated["exportType"], "easiio-docs-deployment-checklist")
        self.assertTrue(updated["checklist"]["manual_review"]["completed"])
        self.assertEqual(updated["checklistUpdatedBy"], "phase15-test")

        status, detail_after = self.request("GET", f"/api/docs/deploy/package?id={package_ids[0]}", headers=auth)
        self.assertEqual(status, 200)
        self.assertTrue(detail_after["checklist"]["manual_review"]["completed"])
        self.assertNotIn("phase15-owner-token", json.dumps(detail_after))

        download = self.request("GET", f"/api/docs/deploy/package/download?id={package_ids[0]}", headers=auth, raw=True)
        self.assertEqual(download.status, 200)
        self.assertIn("application/zip", download.headers["Content-Type"])
        self.assertGreater(len(download.body), 100)

        status, compare = self.request("GET", f"/api/docs/deploy/compare?left_id={package_ids[0]}&right_id={package_ids[1]}", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(compare["exportType"], "easiio-docs-deployment-package-comparison")
        self.assertEqual(compare["left"]["id"], package_ids[0])
        self.assertEqual(compare["right"]["id"], package_ids[1])
        self.assertTrue(compare["differences"]["targetChanged"])
        self.assertTrue(compare["differences"]["environmentChanged"])
        self.assertIn("onlyInLeft", compare["fileDiff"])


    def test_phase16_approval_workflow_release_notes_history_and_locking(self):
        self.store.upsert_doc(self.sample_doc(
            slug="phase16-approval-guide",
            title="Phase 16 Approval Guide",
            content="# Phase 16 Approval Guide\nApprove a deployment handoff package before release.",
            framework_targets=["static-html", "sitelet"],
            locale="en",
        ))
        os.environ["EASIIO_DOCS_OWNER_TOKEN"] = "phase16-owner-token"
        if "app" in sys.modules:
            del sys.modules["app"]
        self.app = importlib.import_module("app")
        auth = {"Authorization": "Bearer phase16-owner-token"}

        status, packaged = self.request("POST", "/api/docs/deploy/package", {
            "site_id": "ai-solo-company",
            "target": "sitelet",
            "environment": "staging",
            "locale": "en",
            "confirmDeploymentPackage": True,
            "approvedBy": "phase16-packager",
        }, headers=auth)
        self.assertEqual(status, 200)
        package_id = packaged["auditRecordId"]

        status, denied = self.request("POST", "/api/docs/deploy/approval", {
            "id": package_id,
            "status": "reviewed",
            "actor": "phase16-reviewer",
            "note": "Looks ready for approval",
        })
        self.assertEqual(status, 401)
        self.assertTrue(denied["authRequired"])

        status, reviewed = self.request("POST", "/api/docs/deploy/approval", {
            "id": package_id,
            "status": "reviewed",
            "actor": "phase16-reviewer",
            "note": "Looks ready for approval",
        }, headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(reviewed["exportType"], "easiio-docs-deployment-approval")
        self.assertEqual(reviewed["approvalStatus"], "reviewed")
        self.assertFalse(reviewed["packageLocked"])
        self.assertEqual(reviewed["approvalHistory"][-1]["status"], "reviewed")

        status, approved = self.request("POST", "/api/docs/deploy/approval", {
            "id": package_id,
            "status": "approved",
            "actor": "phase16-approver",
            "note": "Approved for staging release",
        }, headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(approved["approvalStatus"], "approved")
        self.assertTrue(approved["packageLocked"])
        self.assertGreaterEqual(len(approved["approvalHistory"]), 2)

        status, locked_checklist = self.request("POST", "/api/docs/deploy/checklist", {
            "id": package_id,
            "checklist": {"manual_review": {"completed": True, "note": "Should be blocked after approval"}},
            "updatedBy": "phase16-test",
        }, headers=auth)
        self.assertEqual(status, 409)
        self.assertTrue(locked_checklist["packageLocked"])

        status, notes = self.request("GET", f"/api/docs/deploy/release-notes?id={package_id}", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(notes["exportType"], "easiio-docs-deployment-release-notes")
        self.assertEqual(notes["approvalStatus"], "approved")
        self.assertIn("Phase 16 Approval Guide", notes["releaseNotes"]["markdown"])
        self.assertIn("sitelet", notes["releaseNotes"]["markdown"])
        self.assertNotIn("phase16-owner-token", json.dumps(notes))

        status, history = self.request("GET", f"/api/docs/deploy/approvals?id={package_id}", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(history["exportType"], "easiio-docs-deployment-approval-history")
        self.assertEqual(history["approvalStatus"], "approved")
        self.assertTrue(history["packageLocked"])
        self.assertGreaterEqual(len(history["approvalHistory"]), 2)


    def test_phase17_release_dashboard_readiness_and_operator_handoff_report(self):
        self.store.upsert_doc(self.sample_doc(
            slug="phase17-release-guide",
            title="Phase 17 Release Guide",
            content="# Phase 17 Release Guide\nOperator handoff and readiness reporting for releases.",
            framework_targets=["static-html", "sitelet"],
            locale="en",
        ))
        self.store.upsert_doc(self.sample_doc(
            slug="phase17-checklist",
            title="Phase 17 Checklist",
            content="# Phase 17 Checklist\nVerify package, approval, and handoff report readiness.",
            framework_targets=["static-html", "sitelet"],
            locale="en",
        ))
        os.environ["EASIIO_DOCS_OWNER_TOKEN"] = "phase17-owner-token"
        if "app" in sys.modules:
            del sys.modules["app"]
        self.app = importlib.import_module("app")
        auth = {"Authorization": "Bearer phase17-owner-token"}

        ids = []
        for target, env in [("sitelet", "staging"), ("static-html", "production")]:
            status, packaged = self.request("POST", "/api/docs/deploy/package", {
                "site_id": "ai-solo-company",
                "target": target,
                "environment": env,
                "locale": "en",
                "confirmDeploymentPackage": True,
                "approvedBy": "phase17-packager",
            }, headers=auth)
            self.assertEqual(status, 200)
            ids.append(packaged["auditRecordId"])

        # Prepare one package with complete manual checklist and approval, leaving another queued.
        status, checklist = self.request("POST", "/api/docs/deploy/checklist", {
            "id": ids[0],
            "checklist": {
                "manual_review": {"completed": True, "note": "Reviewed"},
                "static_files_verified": {"completed": True, "note": "Files verified"},
                "sitelet_upload": {"completed": True, "note": "Ready for Sitelet operator"},
                "wordpress_upload": {"completed": True, "note": "Not applicable"},
                "production_publish": {"completed": True, "note": "Release approved"},
            },
            "updatedBy": "phase17-operator",
        }, headers=auth)
        self.assertEqual(status, 200)
        status, approved = self.request("POST", "/api/docs/deploy/approval", {
            "id": ids[0],
            "status": "approved",
            "actor": "phase17-approver",
            "note": "Approved for operator handoff",
        }, headers=auth)
        self.assertEqual(status, 200)
        self.assertTrue(approved["packageLocked"])

        status, denied = self.request("GET", "/api/docs/deploy/releases?site_id=ai-solo-company")
        self.assertEqual(status, 401)
        self.assertTrue(denied["authRequired"])

        status, dashboard = self.request("GET", "/api/docs/deploy/releases?site_id=ai-solo-company&environment=staging&limit=10", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(dashboard["exportType"], "easiio-docs-release-dashboard")
        self.assertEqual(dashboard["site_id"], "ai-solo-company")
        self.assertGreaterEqual(dashboard["totals"]["count"], 1)
        self.assertGreaterEqual(dashboard["totals"]["approved"], 1)
        self.assertIn("ready", dashboard["counts"]["readiness"])
        self.assertEqual(dashboard["filters"]["environment"], "staging")
        first = dashboard["releases"][0]
        self.assertIn("readiness", first)
        self.assertGreaterEqual(first["readiness"]["score"], 80)
        self.assertTrue(first["readiness"]["readyForOperatorHandoff"])
        self.assertNotIn("phase17-owner-token", json.dumps(dashboard))

        status, report = self.request("GET", f"/api/docs/deploy/handoff-report?id={ids[0]}", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(report["exportType"], "easiio-docs-operator-handoff-report")
        self.assertEqual(report["package"]["id"], ids[0])
        self.assertIn("markdown", report)
        self.assertIn("Operator Handoff Report", report["markdown"])
        self.assertIn("Phase 17 Release Guide", report["markdown"])
        self.assertIn("Readiness score", report["markdown"])
        self.assertTrue(report["readiness"]["readyForOperatorHandoff"])
        self.assertNotIn("phase17-owner-token", json.dumps(report))

        status, queue = self.request("GET", "/api/docs/deploy/releases?site_id=ai-solo-company&approval_status=draft", headers=auth)
        self.assertEqual(status, 200)
        self.assertGreaterEqual(queue["totals"]["draft"], 1)
        self.assertIn("releaseQueue", queue)



    def test_phase18_release_archive_attestation_and_report_download(self):
        self.store.upsert_doc(self.sample_doc(
            slug="phase18-archive-guide",
            title="Phase 18 Archive Guide",
            content="# Phase 18 Archive Guide\nArchive release attestation and operator report download.",
            framework_targets=["static-html", "sitelet"],
            locale="en",
        ))
        os.environ["EASIIO_DOCS_OWNER_TOKEN"] = "phase18-owner-token"
        if "app" in sys.modules:
            del sys.modules["app"]
        self.app = importlib.import_module("app")
        auth = {"Authorization": "Bearer phase18-owner-token"}

        status, packaged = self.request("POST", "/api/docs/deploy/package", {
            "site_id": "ai-solo-company",
            "target": "static-html",
            "environment": "production",
            "locale": "en",
            "confirmDeploymentPackage": True,
            "approvedBy": "phase18-packager",
        }, headers=auth)
        self.assertEqual(status, 200)
        audit_id = packaged["auditRecordId"]

        complete_checklist = {
            "manual_review": {"completed": True, "note": "Reviewed"},
            "static_files_verified": {"completed": True, "note": "Files verified"},
            "sitelet_upload": {"completed": True, "note": "Not applicable"},
            "wordpress_upload": {"completed": True, "note": "Not applicable"},
            "production_publish": {"completed": True, "note": "Release approved"},
        }
        status, checklist = self.request("POST", "/api/docs/deploy/checklist", {"id": audit_id, "checklist": complete_checklist, "updatedBy": "phase18-operator"}, headers=auth)
        self.assertEqual(status, 200)
        status, approval = self.request("POST", "/api/docs/deploy/approval", {"id": audit_id, "status": "released", "actor": "phase18-approver", "note": "Released for archive"}, headers=auth)
        self.assertEqual(status, 200)
        self.assertTrue(approval["packageLocked"])

        status, denied = self.request("POST", "/api/docs/deploy/archive", {"id": audit_id, "confirmArchiveRelease": True})
        self.assertEqual(status, 401)
        self.assertTrue(denied["authRequired"])

        status, blocked = self.request("POST", "/api/docs/deploy/archive", {"id": audit_id}, headers=auth)
        self.assertEqual(status, 409)
        self.assertTrue(blocked["requiresArchiveConfirmation"])

        status, archive = self.request("POST", "/api/docs/deploy/archive", {
            "id": audit_id,
            "confirmArchiveRelease": True,
            "createdBy": "phase18-archiver",
        }, headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(archive["exportType"], "easiio-docs-release-archive")
        self.assertEqual(archive["archive"]["auditRecordId"], audit_id)
        self.assertEqual(archive["attestation"]["attestationType"], "easiio-docs-release-attestation")
        self.assertIn("packageSha256", archive["attestation"])
        self.assertIn("manifestSha256", archive["attestation"])
        self.assertIn("handoffReportSha256", archive["attestation"])
        self.assertEqual(len(archive["attestation"]["packageSha256"]), 64)
        self.assertTrue(archive["archive"]["attestationPath"].endswith("release-attestation.json"))
        self.assertTrue(archive["archive"]["reportPath"].endswith("operator-handoff-report.md"))
        self.assertNotIn("phase18-owner-token", json.dumps(archive))

        status, index = self.request("GET", "/api/docs/deploy/archive?site_id=ai-solo-company&environment=production", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(index["exportType"], "easiio-docs-release-archive-index")
        self.assertGreaterEqual(index["count"], 1)
        self.assertEqual(index["archive"][0]["auditRecordId"], audit_id)

        status, attestation = self.request("GET", f"/api/docs/deploy/attestation?id={audit_id}", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(attestation["attestation"]["auditRecordId"], audit_id)
        self.assertEqual(attestation["archive"]["auditRecordId"], audit_id)

        response = self.app.handle_request("GET", f"/api/docs/deploy/report/download?id={audit_id}", headers=auth)
        self.assertEqual(response.status, 200)
        self.assertIn("text/markdown", response.headers["Content-Type"])
        report_text = response.body.decode("utf-8")
        self.assertIn("Operator Handoff Report", report_text)
        self.assertIn("Phase 18 Archive Guide", report_text)
        self.assertNotIn("phase18-owner-token", report_text)


    def test_phase19_archive_integrity_rollback_plan_and_restore_package(self):
        self.store.upsert_doc(self.sample_doc(
            slug="phase19-restore-guide",
            title="Phase 19 Restore Guide",
            content="# Phase 19 Restore Guide\nStable release content for rollback planning.",
            framework_targets=["static-html", "sitelet"],
            locale="en",
        ))
        os.environ["EASIIO_DOCS_OWNER_TOKEN"] = "phase19-owner-token"
        if "app" in sys.modules:
            del sys.modules["app"]
        self.app = importlib.import_module("app")
        auth = {"Authorization": "Bearer phase19-owner-token"}

        def package_archive(version_label, content, actor):
            self.store.upsert_doc(self.sample_doc(
                slug="phase19-restore-guide",
                title="Phase 19 Restore Guide",
                content=content,
                version_label=version_label,
                framework_targets=["static-html", "sitelet"],
                locale="en",
            ))
            status, packaged = self.request("POST", "/api/docs/deploy/package", {
                "site_id": "ai-solo-company",
                "target": "static-html",
                "environment": "production",
                "locale": "en",
                "confirmDeploymentPackage": True,
                "approvedBy": actor,
            }, headers=auth)
            self.assertEqual(status, 200)
            audit_id = packaged["auditRecordId"]
            complete_checklist = {
                "manual_review": {"completed": True, "note": "Reviewed"},
                "static_files_verified": {"completed": True, "note": "Files verified"},
                "sitelet_upload": {"completed": True, "note": "Not applicable"},
                "wordpress_upload": {"completed": True, "note": "Not applicable"},
                "production_publish": {"completed": True, "note": "Release approved"},
            }
            status, _ = self.request("POST", "/api/docs/deploy/checklist", {"id": audit_id, "checklist": complete_checklist, "updatedBy": actor}, headers=auth)
            self.assertEqual(status, 200)
            status, _ = self.request("POST", "/api/docs/deploy/approval", {"id": audit_id, "status": "released", "actor": actor, "note": "Released for archive"}, headers=auth)
            self.assertEqual(status, 200)
            status, archive = self.request("POST", "/api/docs/deploy/archive", {"id": audit_id, "confirmArchiveRelease": True, "createdBy": actor}, headers=auth)
            self.assertEqual(status, 200)
            return audit_id, archive

        previous_id, previous_archive = package_archive("1.0", "# Phase 19 Restore Guide\nPrevious stable release.", "phase19-previous")
        time.sleep(1)
        current_id, current_archive = package_archive("2.0", "# Phase 19 Restore Guide\nCurrent release that may need rollback.", "phase19-current")
        self.assertNotEqual(previous_id, current_id)

        status, denied_integrity = self.request("GET", f"/api/docs/deploy/archive/integrity?id={current_id}")
        self.assertEqual(status, 401)
        self.assertTrue(denied_integrity["authRequired"])

        status, integrity = self.request("GET", f"/api/docs/deploy/archive/integrity?id={current_id}", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(integrity["exportType"], "easiio-docs-release-integrity")
        self.assertTrue(integrity["integrity"]["verified"])
        self.assertEqual(integrity["integrity"]["auditRecordId"], current_id)
        self.assertEqual(integrity["integrity"]["packageSha256"], current_archive["attestation"]["packageSha256"])

        status, rollback = self.request("GET", f"/api/docs/deploy/rollback-plan?id={current_id}&previous_id={previous_id}", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(rollback["exportType"], "easiio-docs-rollback-plan")
        self.assertEqual(rollback["currentRelease"]["auditRecordId"], current_id)
        self.assertEqual(rollback["rollbackTarget"]["auditRecordId"], previous_id)
        self.assertIn("Rollback Plan", rollback["rollbackPlanMarkdown"])
        self.assertIn(str(previous_id), rollback["rollbackPlanMarkdown"])
        self.assertTrue(rollback["integrity"]["verified"])

        status, denied_restore = self.request("POST", "/api/docs/deploy/restore-package", {"id": current_id, "previous_id": previous_id, "confirmPrepareRestore": True})
        self.assertEqual(status, 401)
        self.assertTrue(denied_restore["authRequired"])

        status, blocked_restore = self.request("POST", "/api/docs/deploy/restore-package", {"id": current_id, "previous_id": previous_id}, headers=auth)
        self.assertEqual(status, 409)
        self.assertTrue(blocked_restore["requiresRestoreConfirmation"])

        status, restore = self.request("POST", "/api/docs/deploy/restore-package", {
            "id": current_id,
            "previous_id": previous_id,
            "confirmPrepareRestore": True,
            "createdBy": "phase19-operator",
        }, headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(restore["exportType"], "easiio-docs-restore-package")
        self.assertTrue(restore["restorePackage"]["localOnly"])
        self.assertTrue(restore["restorePackage"]["packagePath"].endswith(".zip"))
        self.assertIn("rollback-plan.md", restore["restorePackage"]["files"])
        self.assertIn("Rollback Plan", restore["rollbackPlanMarkdown"])
        self.assertNotIn("phase19-owner-token", json.dumps(restore))


    def test_phase20_connector_catalog_and_preflight_dry_run_are_owner_protected_and_secret_safe(self):
        self.store.upsert_doc(self.sample_doc(
            slug="phase20-connector-guide",
            title="Phase 20 Connector Guide",
            content="# Phase 20 Connector Guide\nDry-run connector preflight for deployment handoff packages.",
            framework_targets=["static-html", "sitelet", "wordpress-shortcode"],
            locale="en",
        ))
        os.environ["EASIIO_DOCS_OWNER_TOKEN"] = "phase20-owner-token"
        if "app" in sys.modules:
            del sys.modules["app"]
        self.app = importlib.import_module("app")
        auth = {"Authorization": "Bearer phase20-owner-token"}

        status, health = self.request("GET", "/health", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(health["phase"], "25-v1-release")
        self.assertIn("20-connector-dry-run", health.get("phaseHistory", []))

        status, packaged = self.request("POST", "/api/docs/deploy/package", {
            "site_id": "ai-solo-company",
            "target": "sitelet",
            "environment": "staging",
            "locale": "en",
            "confirmDeploymentPackage": True,
            "approvedBy": "phase20-packager",
        }, headers=auth)
        self.assertEqual(status, 200)
        audit_id = packaged["auditRecordId"]

        complete_checklist = {
            "manual_review": {"completed": True, "note": "Reviewed"},
            "static_files_verified": {"completed": True, "note": "Files verified"},
            "sitelet_upload": {"completed": True, "note": "Dry-run connector only"},
            "wordpress_upload": {"completed": True, "note": "Not applicable"},
            "production_publish": {"completed": True, "note": "Approved for staging dry-run"},
        }
        status, _ = self.request("POST", "/api/docs/deploy/checklist", {"id": audit_id, "checklist": complete_checklist, "updatedBy": "phase20-operator"}, headers=auth)
        self.assertEqual(status, 200)
        status, _ = self.request("POST", "/api/docs/deploy/approval", {"id": audit_id, "status": "approved", "actor": "phase20-approver", "note": "Approved for dry-run preflight"}, headers=auth)
        self.assertEqual(status, 200)

        status, denied_catalog = self.request("GET", "/api/docs/deploy/connectors")
        self.assertEqual(status, 401)
        self.assertTrue(denied_catalog["authRequired"])

        status, catalog = self.request("GET", "/api/docs/deploy/connectors", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(catalog["exportType"], "easiio-docs-connector-catalog")
        connector_ids = [item["id"] for item in catalog["connectors"]]
        self.assertIn("sitelet", connector_ids)
        self.assertIn("wordpress", connector_ids)
        self.assertIn("static-hosting", connector_ids)

        secret_config = {
            "base_url": "https://sitelet.easiiodev.ai",
            "api_token": "phase20-secret-token",
            "authorization": "Bearer phase20-authorization",
            "notes": "safe visible note",
        }
        status, denied_preflight = self.request("POST", "/api/docs/deploy/connector/preflight", {
            "id": audit_id,
            "connector": "sitelet",
            "connectorConfig": secret_config,
            "confirmConnectorDryRun": True,
        })
        self.assertEqual(status, 401)
        self.assertTrue(denied_preflight["authRequired"])

        status, blocked = self.request("POST", "/api/docs/deploy/connector/preflight", {
            "id": audit_id,
            "connector": "sitelet",
            "connectorConfig": secret_config,
        }, headers=auth)
        self.assertEqual(status, 409)
        self.assertTrue(blocked["requiresConnectorDryRunConfirmation"])

        status, preflight = self.request("POST", "/api/docs/deploy/connector/preflight", {
            "id": audit_id,
            "connector": "sitelet",
            "connectorConfig": secret_config,
            "confirmConnectorDryRun": True,
            "requestedBy": "phase20-operator",
        }, headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(preflight["exportType"], "easiio-docs-connector-preflight")
        self.assertEqual(preflight["connector"]["id"], "sitelet")
        self.assertTrue(preflight["dryRunOnly"])
        self.assertTrue(preflight["localOnly"])
        self.assertTrue(preflight["externalCallsBlocked"])
        self.assertTrue(preflight["preflight"]["packageExists"])
        self.assertGreaterEqual(preflight["preflight"]["readinessScore"], 80)
        self.assertIn("base_url", preflight["redactedConfig"])
        self.assertEqual(preflight["redactedConfig"]["api_token"], "[REDACTED]")
        as_json = json.dumps(preflight)
        self.assertNotIn("phase20-secret-token", as_json)
        self.assertNotIn("phase20-authorization", as_json)
        self.assertNotIn("phase20-owner-token", as_json)


    def test_phase21_connector_profiles_and_dry_run_history_are_owner_protected_and_secret_safe(self):
        self.store.upsert_doc(self.sample_doc(
            slug="phase21-profile-guide",
            title="Phase 21 Connector Profile Guide",
            content="# Phase 21 Connector Profile Guide\nConnector profile placeholders and dry-run history.",
            framework_targets=["static-html", "sitelet"],
            locale="en",
        ))
        os.environ["EASIIO_DOCS_OWNER_TOKEN"] = "phase21-owner-token"
        if "app" in sys.modules:
            del sys.modules["app"]
        self.app = importlib.import_module("app")
        auth = {"Authorization": "Bearer phase21-owner-token"}

        status, health = self.request("GET", "/health", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(health["phase"], "25-v1-release")
        self.assertIn("20-connector-dry-run", health.get("phaseHistory", []))

        profile_payload = {
            "site_id": "ai-solo-company",
            "name": "Sitelet staging profile",
            "connector": "sitelet",
            "environment": "staging",
            "target": "sitelet",
            "connectorConfig": {
                "base_url": "https://sitelet.easiiodev.ai",
                "api_token": "phase21-secret-token",
                "authorization": "Bearer phase21-authorization",
                "notes": "safe operator note",
            },
            "requestedBy": "phase21-admin",
        }
        status, denied_profile = self.request("POST", "/api/docs/deploy/connector/profile", {**profile_payload, "confirmSaveConnectorProfile": True})
        self.assertEqual(status, 401)
        self.assertTrue(denied_profile["authRequired"])

        status, blocked_profile = self.request("POST", "/api/docs/deploy/connector/profile", profile_payload, headers=auth)
        self.assertEqual(status, 409)
        self.assertTrue(blocked_profile["requiresConnectorProfileConfirmation"])

        status, saved_profile = self.request("POST", "/api/docs/deploy/connector/profile", {**profile_payload, "confirmSaveConnectorProfile": True}, headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(saved_profile["exportType"], "easiio-docs-connector-profile")
        profile_id = saved_profile["profile"]["id"]
        self.assertTrue(saved_profile["profile"]["secretPlaceholdersOnly"])
        self.assertEqual(saved_profile["profile"]["redactedConfig"]["api_token"], "[REDACTED]")

        status, profiles = self.request("GET", "/api/docs/deploy/connector/profiles?site_id=ai-solo-company", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(profiles["exportType"], "easiio-docs-connector-profiles")
        self.assertEqual(profiles["profiles"][0]["id"], profile_id)
        self.assertTrue(profiles["profiles"][0]["secretPlaceholdersOnly"])

        status, packaged = self.request("POST", "/api/docs/deploy/package", {
            "site_id": "ai-solo-company",
            "target": "sitelet",
            "environment": "staging",
            "locale": "en",
            "confirmDeploymentPackage": True,
            "approvedBy": "phase21-packager",
        }, headers=auth)
        self.assertEqual(status, 200)
        audit_id = packaged["auditRecordId"]
        complete_checklist = {
            "manual_review": {"completed": True, "note": "Reviewed"},
            "static_files_verified": {"completed": True, "note": "Files verified"},
            "sitelet_upload": {"completed": True, "note": "Dry-run only"},
            "wordpress_upload": {"completed": True, "note": "Not applicable"},
            "production_publish": {"completed": True, "note": "Approved for staging dry-run"},
        }
        self.assertEqual(self.request("POST", "/api/docs/deploy/checklist", {"id": audit_id, "checklist": complete_checklist, "updatedBy": "phase21-operator"}, headers=auth)[0], 200)
        self.assertEqual(self.request("POST", "/api/docs/deploy/approval", {"id": audit_id, "status": "approved", "actor": "phase21-approver", "note": "Approved for profile preflight"}, headers=auth)[0], 200)

        status, preflight = self.request("POST", "/api/docs/deploy/connector/preflight", {
            "id": audit_id,
            "profileId": profile_id,
            "confirmConnectorDryRun": True,
            "requestedBy": "phase21-operator",
        }, headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(preflight["profile"]["id"], profile_id)
        self.assertTrue(preflight["dryRunRecord"]["id"] >= 1)
        self.assertEqual(preflight["redactedConfig"]["api_token"], "[REDACTED]")

        status, denied_history = self.request("GET", "/api/docs/deploy/connector/dry-runs?site_id=ai-solo-company")
        self.assertEqual(status, 401)
        self.assertTrue(denied_history["authRequired"])

        status, history = self.request("GET", "/api/docs/deploy/connector/dry-runs?site_id=ai-solo-company", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(history["exportType"], "easiio-docs-connector-dry-run-history")
        self.assertGreaterEqual(len(history["dryRuns"]), 1)
        self.assertEqual(history["dryRuns"][0]["profileId"], profile_id)
        self.assertEqual(history["dryRuns"][0]["connector"], "sitelet")
        self.assertTrue(history["dryRuns"][0]["dryRunOnly"])
        as_json = json.dumps({"saved": saved_profile, "profiles": profiles, "preflight": preflight, "history": history})
        self.assertNotIn("phase21-secret-token", as_json)
        self.assertNotIn("phase21-authorization", as_json)
        self.assertNotIn("phase21-owner-token", as_json)





    def test_phase22_connector_runbooks_and_dry_run_comparison_are_owner_protected_and_local_only(self):
        self.store.upsert_doc(self.sample_doc(
            slug="phase22-runbook-guide",
            title="Phase 22 Connector Runbook Guide",
            content="# Phase 22 Connector Runbook Guide\nConnector runbooks and dry-run comparison dashboards.",
            framework_targets=["static-html", "sitelet"],
            locale="en",
        ))
        os.environ["EASIIO_DOCS_OWNER_TOKEN"] = "phase22-owner-token"
        if "app" in sys.modules:
            del sys.modules["app"]
        self.app = importlib.import_module("app")
        auth = {"Authorization": "Bearer phase22-owner-token"}

        status, health = self.request("GET", "/health", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(health["phase"], "25-v1-release")
        self.assertIn("21-connector-profiles", health.get("phaseHistory", []))

        profile_payload = {
            "site_id": "ai-solo-company",
            "name": "Phase 22 Sitelet staging profile",
            "connector": "sitelet",
            "environment": "staging",
            "target": "sitelet",
            "connectorConfig": {
                "base_url": "https://sitelet.easiiodev.ai",
                "api_token": "phase22-secret-token",
                "authorization": "Bearer phase22-authorization",
                "notes": "safe visible runbook note",
            },
            "confirmSaveConnectorProfile": True,
            "requestedBy": "phase22-admin",
        }
        status, saved_profile = self.request("POST", "/api/docs/deploy/connector/profile", profile_payload, headers=auth)
        self.assertEqual(status, 200)
        profile_id = saved_profile["profile"]["id"]

        status, packaged = self.request("POST", "/api/docs/deploy/package", {
            "site_id": "ai-solo-company",
            "target": "sitelet",
            "environment": "staging",
            "locale": "en",
            "confirmDeploymentPackage": True,
            "approvedBy": "phase22-packager",
        }, headers=auth)
        self.assertEqual(status, 200)
        audit_id = packaged["auditRecordId"]
        complete_checklist = {
            "manual_review": {"completed": True, "note": "Reviewed"},
            "static_files_verified": {"completed": True, "note": "Files verified"},
            "sitelet_upload": {"completed": True, "note": "Dry-run only"},
            "wordpress_upload": {"completed": True, "note": "Not applicable"},
            "production_publish": {"completed": True, "note": "Approved for staging dry-run"},
        }
        self.assertEqual(self.request("POST", "/api/docs/deploy/checklist", {"id": audit_id, "checklist": complete_checklist, "updatedBy": "phase22-operator"}, headers=auth)[0], 200)
        self.assertEqual(self.request("POST", "/api/docs/deploy/approval", {"id": audit_id, "status": "approved", "actor": "phase22-approver", "note": "Approved for runbook preflight"}, headers=auth)[0], 200)

        status, passing_preflight = self.request("POST", "/api/docs/deploy/connector/preflight", {
            "id": audit_id,
            "profileId": profile_id,
            "confirmConnectorDryRun": True,
            "requestedBy": "phase22-operator",
        }, headers=auth)
        self.assertEqual(status, 200)
        pass_run_id = passing_preflight["dryRunRecord"]["id"]
        self.assertTrue(passing_preflight["preflight"]["passed"])

        status, failing_preflight = self.request("POST", "/api/docs/deploy/connector/preflight", {
            "id": audit_id,
            "connector": "wordpress",
            "connectorConfig": {"notes": "missing site_url"},
            "confirmConnectorDryRun": True,
            "requestedBy": "phase22-reviewer",
        }, headers=auth)
        self.assertEqual(status, 200)
        fail_run_id = failing_preflight["dryRunRecord"]["id"]
        self.assertFalse(failing_preflight["preflight"]["passed"])

        status, denied_runbook = self.request("GET", f"/api/docs/deploy/connector/runbook?id={pass_run_id}")
        self.assertEqual(status, 401)
        self.assertTrue(denied_runbook["authRequired"])

        status, runbook = self.request("GET", f"/api/docs/deploy/connector/runbook?id={pass_run_id}", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(runbook["exportType"], "easiio-docs-connector-runbook")
        self.assertEqual(runbook["dryRun"]["id"], pass_run_id)
        self.assertIn("Connector runbook", runbook["runbookMarkdown"])
        self.assertIn("No external connector calls are made", runbook["runbookMarkdown"])
        self.assertTrue(runbook["localOnly"])
        self.assertTrue(runbook["externalCallsBlocked"])

        status, denied_compare = self.request("GET", f"/api/docs/deploy/connector/dry-run-compare?left_id={pass_run_id}&right_id={fail_run_id}")
        self.assertEqual(status, 401)
        self.assertTrue(denied_compare["authRequired"])

        status, comparison = self.request("GET", f"/api/docs/deploy/connector/dry-run-compare?left_id={pass_run_id}&right_id={fail_run_id}", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(comparison["exportType"], "easiio-docs-connector-dry-run-comparison")
        self.assertEqual(comparison["left"]["id"], pass_run_id)
        self.assertEqual(comparison["right"]["id"], fail_run_id)
        self.assertGreaterEqual(comparison["scoreDelta"], 0)
        self.assertGreaterEqual(len(comparison["checkDiffs"]), 1)
        self.assertTrue(comparison["localOnly"])
        self.assertTrue(comparison["externalCallsBlocked"])
        as_json = json.dumps({"runbook": runbook, "comparison": comparison})
        self.assertNotIn("phase22-secret-token", as_json)
        self.assertNotIn("phase22-authorization", as_json)
        self.assertNotIn("phase22-owner-token", as_json)




    def test_phase23_operator_release_playbooks_are_owner_protected_target_specific_and_local_only(self):
        self.store.upsert_doc(self.sample_doc(
            slug="phase23-operator-playbook-guide",
            title="Phase 23 Operator Playbook Guide",
            content="# Phase 23 Operator Playbook Guide\nFinal operator release playbooks for deployment handoff.",
            framework_targets=["sitelet", "wordpress", "static-html"],
            locale="en",
        ))
        os.environ["EASIIO_DOCS_OWNER_TOKEN"] = "phase23-owner-token"
        if "app" in sys.modules:
            del sys.modules["app"]
        self.app = importlib.import_module("app")
        auth = {"Authorization": "Bearer phase23-owner-token"}

        status, health = self.request("GET", "/health", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(health["phase"], "25-v1-release")
        self.assertIn("22-connector-runbooks", health.get("phaseHistory", []))

        status, packaged = self.request("POST", "/api/docs/deploy/package", {
            "site_id": "ai-solo-company",
            "target": "sitelet",
            "environment": "staging",
            "locale": "en",
            "confirmDeploymentPackage": True,
            "approvedBy": "phase23-packager",
        }, headers=auth)
        self.assertEqual(status, 200)
        audit_id = packaged["auditRecordId"]
        complete_checklist = {
            "manual_review": {"completed": True, "note": "Reviewed"},
            "static_files_verified": {"completed": True, "note": "Files verified"},
            "sitelet_upload": {"completed": True, "note": "Dry-run only"},
            "wordpress_upload": {"completed": True, "note": "Not applicable"},
            "production_publish": {"completed": True, "note": "Operator handoff only"},
        }
        self.assertEqual(self.request("POST", "/api/docs/deploy/checklist", {"id": audit_id, "checklist": complete_checklist, "updatedBy": "phase23-operator"}, headers=auth)[0], 200)
        self.assertEqual(self.request("POST", "/api/docs/deploy/approval", {"id": audit_id, "status": "approved", "actor": "phase23-approver", "note": "Approved for final playbook"}, headers=auth)[0], 200)

        status, denied_catalog = self.request("GET", "/api/docs/deploy/operator-playbooks")
        self.assertEqual(status, 401)
        self.assertTrue(denied_catalog["authRequired"])

        status, catalog = self.request("GET", "/api/docs/deploy/operator-playbooks", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(catalog["exportType"], "easiio-docs-operator-playbook-catalog")
        target_ids = {item["target"] for item in catalog["playbooks"]}
        self.assertIn("sitelet", target_ids)
        self.assertIn("wordpress", target_ids)
        self.assertIn("static-hosting", target_ids)
        self.assertTrue(catalog["localOnly"])
        self.assertTrue(catalog["externalCallsBlocked"])

        status, denied_playbook = self.request("GET", f"/api/docs/deploy/operator-playbook?id={audit_id}&target=sitelet")
        self.assertEqual(status, 401)
        self.assertTrue(denied_playbook["authRequired"])

        status, playbook = self.request("GET", f"/api/docs/deploy/operator-playbook?id={audit_id}&target=sitelet", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(playbook["exportType"], "easiio-docs-operator-release-playbook")
        self.assertEqual(playbook["auditRecordId"], audit_id)
        self.assertEqual(playbook["target"], "sitelet")
        self.assertIn("Sitelet Deployment Playbook", playbook["playbookMarkdown"])
        self.assertIn("No external deployment is executed", playbook["playbookMarkdown"])
        self.assertIn("Operator handoff checklist", playbook["playbookMarkdown"])
        self.assertTrue(playbook["readyForOperatorHandoff"])
        self.assertTrue(playbook["localOnly"])
        self.assertTrue(playbook["externalCallsBlocked"])
        self.assertTrue(playbook["secretPlaceholdersOnly"])

        status, wp_playbook = self.request("GET", f"/api/docs/deploy/operator-playbook?id={audit_id}&target=wordpress", headers=auth)
        self.assertEqual(status, 200)
        self.assertIn("WordPress Deployment Playbook", wp_playbook["playbookMarkdown"])
        self.assertIn("shortcode", wp_playbook["playbookMarkdown"].lower())

        as_json = json.dumps({"catalog": catalog, "playbook": playbook, "wp": wp_playbook})
        self.assertNotIn("phase23-owner-token", as_json)
        self.assertNotIn("Authorization", as_json)




    def test_phase24_onboarding_guide_and_checklist_are_owner_protected_and_secret_safe(self):
        os.environ["EASIIO_DOCS_OWNER_TOKEN"] = "phase24-owner-token"
        if "app" in sys.modules:
            del sys.modules["app"]
        self.app = importlib.import_module("app")
        auth = {"Authorization": "Bearer phase24-owner-token"}

        status, health = self.request("GET", "/health", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(health["phase"], "25-v1-release")
        self.assertIn("23-operator-playbooks", health.get("phaseHistory", []))

        status, denied_guide = self.request("GET", "/api/docs/deploy/onboarding-guide?site_id=ai-solo-company&integration=sitelet")
        self.assertEqual(status, 401)
        self.assertTrue(denied_guide["authRequired"])

        status, guide = self.request("GET", "/api/docs/deploy/onboarding-guide?site_id=ai-solo-company&integration=sitelet", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(guide["exportType"], "easiio-docs-onboarding-guide")
        self.assertEqual(guide["siteId"], "ai-solo-company")
        self.assertEqual(guide["integration"], "sitelet")
        self.assertIn("Environment variable reference", guide["installMarkdown"])
        self.assertIn("Start/stop commands", guide["installMarkdown"])
        self.assertIn("Backup and restore", guide["installMarkdown"])
        self.assertIn("Sitelet integration", guide["installMarkdown"])
        self.assertIn("EASIIO_DOCS_OWNER_TOKEN=[REDACTED]", guide["installMarkdown"])
        self.assertTrue(guide["localOnly"])
        self.assertTrue(guide["externalCallsBlocked"])
        self.assertTrue(guide["secretPlaceholdersOnly"])

        status, denied_checklist = self.request("GET", "/api/docs/deploy/onboarding-checklist?site_id=ai-solo-company")
        self.assertEqual(status, 401)
        self.assertTrue(denied_checklist["authRequired"])

        status, checklist = self.request("GET", "/api/docs/deploy/onboarding-checklist?site_id=ai-solo-company&integration=wordpress", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(checklist["exportType"], "easiio-docs-onboarding-checklist")
        self.assertEqual(checklist["siteId"], "ai-solo-company")
        self.assertEqual(checklist["integration"], "wordpress")
        keys = {item["key"] for item in checklist["checklist"]}
        self.assertIn("install", keys)
        self.assertIn("env", keys)
        self.assertIn("backup", keys)
        self.assertIn("wordpress", keys)
        self.assertTrue(checklist["localOnly"])
        self.assertTrue(checklist["externalCallsBlocked"])
        as_json = json.dumps({"guide": guide, "checklist": checklist})
        self.assertNotIn("phase24-owner-token", as_json)
        self.assertNotIn("Authorization", as_json)
        self.assertNotIn("password", as_json.lower())




    def test_phase25_v1_release_summary_and_package_are_owner_protected_confirmation_gated_and_secret_safe(self):
        os.environ["EASIIO_DOCS_OWNER_TOKEN"] = "phase25-owner-token"
        if "app" in sys.modules:
            del sys.modules["app"]
        self.app = importlib.import_module("app")
        auth = {"Authorization": "Bearer phase25-owner-token"}

        status, health = self.request("GET", "/health", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(health["phase"], "25-v1-release")
        self.assertIn("24-onboarding-guide", health.get("phaseHistory", []))

        status, denied_summary = self.request("GET", "/api/docs/deploy/v1-release-summary")
        self.assertEqual(status, 401)
        self.assertTrue(denied_summary["authRequired"])

        status, summary = self.request("GET", "/api/docs/deploy/v1-release-summary", headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(summary["exportType"], "easiio-docs-v1-release-summary")
        self.assertEqual(summary["version"], "v1.0.0")
        self.assertTrue(summary["releaseFreeze"]["frozen"])
        self.assertTrue(summary["localOnly"])
        self.assertTrue(summary["externalCallsBlocked"])
        self.assertTrue(summary["secretPlaceholdersOnly"])
        qa_keys = {item["key"] for item in summary["finalQaChecklist"]}
        self.assertIn("full_regression", qa_keys)
        self.assertIn("runtime_smoke", qa_keys)
        self.assertIn("artifact_cleanup", qa_keys)
        security_keys = {item["key"] for item in summary["securityChecklist"]}
        self.assertIn("secret_redaction", security_keys)
        self.assertIn("local_only", security_keys)
        self.assertIn("25-v1-release", summary["releaseMarkdown"])
        self.assertIn("No external deployment is executed by this module", summary["releaseMarkdown"])

        status, denied_package = self.request("POST", "/api/docs/deploy/v1-release-package", {"approvedBy": "phase25-tester"})
        self.assertEqual(status, 401)
        self.assertTrue(denied_package["authRequired"])

        status, missing_confirm = self.request("POST", "/api/docs/deploy/v1-release-package", {"approvedBy": "phase25-tester"}, headers=auth)
        self.assertEqual(status, 409)
        self.assertFalse(missing_confirm["ok"])
        self.assertIn("confirmV1ReleasePackage", missing_confirm["error"])

        status, package = self.request("POST", "/api/docs/deploy/v1-release-package", {"approvedBy": "phase25-tester", "confirmV1ReleasePackage": True}, headers=auth)
        self.assertEqual(status, 200)
        self.assertEqual(package["exportType"], "easiio-docs-v1-release-package")
        self.assertEqual(package["version"], "v1.0.0")
        self.assertTrue(package["ok"])
        self.assertTrue(package["localOnly"])
        self.assertTrue(package["externalCallsBlocked"])
        self.assertTrue(package["secretPlaceholdersOnly"])
        self.assertTrue(package["packagePath"].endswith(".zip"))
        self.assertGreater(package["packageSize"], 0)
        self.assertIn("EASIIO_DOCS_MODULE_PHASE25.md", package["manifest"]["includedFiles"])
        self.assertIn("README.md", package["manifest"]["includedFiles"])

        as_json = json.dumps({"summary": summary, "package": package})
        self.assertNotIn("phase25-owner-token", as_json)
        self.assertNotIn("Authorization", as_json)
        self.assertNotIn("password", as_json.lower())




if __name__ == "__main__":
    unittest.main()
