# Easiio Docs Module — Phase 7 Admin/Export UI

## Goal

Phase 7 adds a lightweight browser UI for site owners/operators to preview framework export files and create approved ZIP packages without using raw curl commands.

The UI is local-first and should be hosted behind a protected/admin boundary in real deployments.

## Added files

```text
frontend/admin.html
frontend/admin.js
frontend/admin.css
tests/admin_export_ui_static.test.js
EASIIO_DOCS_MODULE_PHASE7.md
```

## Updated files

```text
backend/app.py
tests/test_docs_backend.py
README.md
```

## UI route

```text
GET /docs/admin.html
GET /docs/admin.js
GET /docs/admin.css
```

Local URL:

```text
http://127.0.0.1:8110/docs/admin.html
```

## UI workflow

1. Enter `site_id`.
2. Choose export target:
   - `nextjs-mdx`
   - `docusaurus`
   - `mkdocs`
   - `hugo`
   - `vitepress`
   - `static-html`
3. Click **Preview files**.
4. Review generated file count, document count, safety status, file paths, and file contents.
5. Click **Create approved ZIP**.
6. Browser confirmation must be accepted before the UI calls the package endpoint with:

```json
{"confirmExportPackage": true}
```

## Safety behavior

The UI uses the existing Phase 6 safety guarantees:

- preview first
- package creation is confirmation-gated
- exports include only `published` + `public` docs
- selected docs must include the chosen framework target in `framework_targets`
- draft/private/internal/login-required docs are excluded by default
- no secrets or tokens are rendered in frontend files

## Backend behavior

Health now reports:

```json
{"phase":"7-admin-export-ui"}
```

The admin UI reuses existing backend endpoints:

```text
GET  /api/docs/export/preview
POST /api/docs/export/package
```

## Validation

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py backend/docs_wordpress.py backend/docs_rag.py backend/docs_exporters.py
node --check frontend/docs.js
node --check frontend/admin.js
node tests/docs_static.test.js
node tests/sitelet_preview_static.test.js
node tests/wp_plugin_static.test.js
node tests/rag_sync_static.test.js
node tests/exporters_static.test.js
node tests/admin_export_ui_static.test.js
python3 tests/test_docs_backend.py -v
```

Expected result:

```text
PASS Phase 7 admin/export UI assets and routes are wired
Ran 15 tests ... OK
```

## Runtime smoke

Phase 7 runtime smoke verified:

- `/health` reports `7-admin-export-ui`
- `/docs/admin.html` serves the UI shell
- `/docs/admin.js` serves the UI controller
- `/docs/admin.css` serves the UI styles
- document creation still works
- export preview still works
- package endpoint remains blocked without `confirmExportPackage`
- approved ZIP creation still works
- generated ZIP contains docs markdown and manifest

Smoke marker:

```text
easiio_docs_phase7_smoke_ok
```

## Next recommended phase

Phase 8 should add protected/admin access controls for the docs admin UI and write endpoints, including local owner token or site-level auth integration before exposing the UI beyond trusted local development.
