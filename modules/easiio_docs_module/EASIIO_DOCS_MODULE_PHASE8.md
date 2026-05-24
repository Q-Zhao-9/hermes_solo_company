# Easiio Docs Module — Phase 8 Auth/Permissions and Admin Hardening

Phase 8 adds owner-token protection to the Easiio Docs Module so admin UI assets, write/action endpoints, and non-public/draft reads can be safely protected before exposing the module beyond trusted local development.

## Goal

Harden the Phase 7 admin/export UI and existing action endpoints without breaking public website embeds.

Public, published docs remain readable for normal documentation widgets. Admin and mutation actions become protected when an owner token is configured.

## Configuration

Set the owner token before starting the backend:

```bash
EASIIO_DOCS_OWNER_TOKEN=[REDACTED]
```

Protected requests can authenticate with either header:

```text
Authorization: Bearer [REDACTED]
X-Easiio-Owner-Token: [REDACTED]
```

A query-string fallback exists for local/manual debugging only:

```text
?owner_token=[REDACTED]
```

Do not print, commit, or expose real owner tokens.

## Files changed

```text
backend/app.py
frontend/admin.html
frontend/admin.js
tests/test_docs_backend.py
tests/admin_export_ui_static.test.js
README.md
EASIIO_DOCS_MODULE_PHASE8.md
```

## Protected routes when `EASIIO_DOCS_OWNER_TOKEN` is configured

Admin UI assets:

```text
GET /docs/admin.html
GET /docs/admin.js
GET /docs/admin.css
```

Write/action endpoints:

```text
POST /api/docs/doc
POST /api/docs/doc/delete
POST /api/docs/sitelet-preview/upload
POST /api/docs/wordpress/draft-execution
POST /api/docs/rag/sync
POST /api/docs/export/package
```

Non-public/draft reads:

```text
GET /api/docs/docs?status!=published
GET /api/docs/docs?visibility!=public
GET /api/docs/doc for private/draft/internal/login_required docs
GET /api/docs/revisions
GET /api/docs/space
GET preview endpoints when status/visibility/include_private requests non-public content
```

## Public routes preserved

These remain public for website embeds when returning published public content:

```text
GET /health
GET /docs/docs.js
GET /docs/docs.css
GET /docs/demo.html
GET /api/docs/docs?status=published&visibility=public
GET /api/docs/doc for published public docs
GET /api/docs/sitelet-preview with default published/public filters
GET /api/docs/wordpress/shortcode
GET /api/docs/wordpress/draft-plan with default published/public filters
GET /api/docs/rag/preview with default published/public filters
GET /api/docs/export/preview with default published/public filters
```

## Admin UI update

`frontend/admin.html` now includes an **Owner token** password field.

`frontend/admin.js` reads the token and sends it as:

```text
Authorization: Bearer [REDACTED]
```

for export preview/package requests. Browser confirmation is still required before sending `confirmExportPackage:true`.

## Health response

`GET /health` now reports:

```json
{
  "ok": true,
  "service": "easiio-docs-module",
  "phase": "8-auth-permissions",
  "adminAuthConfigured": true
}
```

`adminAuthConfigured` is `true` only when `EASIIO_DOCS_OWNER_TOKEN` is set.

## Verification

Full verification command:

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

Passed result included:

```text
PASS Phase 8 admin/export UI auth assets and routes are wired
Ran 17 tests
OK
```

## Runtime smoke

Runtime smoke used a temporary SQLite DB, temporary RAG store, and temporary owner token. It verified:

- `/health` reports Phase 8 and auth configured.
- `/docs/admin.html` returns `401` without owner auth.
- `/docs/admin.html` returns `200` with owner auth.
- document creation is blocked without owner auth.
- document creation succeeds with owner auth.
- published public document reads still work without owner auth.
- private document reads are blocked without owner auth.
- export preview for published public docs still works.
- export package creation is blocked without owner auth.
- export package creation succeeds with owner auth and creates the ZIP.

Smoke marker:

```text
easiio_docs_phase8_smoke_ok
```

Cleanup marker:

```text
phase8_smoke_cleanup_ok
```

## Next recommended phase

Phase 9 should add the in-browser docs editor/admin content-management UI:

- create/edit docs spaces and pages from the browser
- edit title, slug, summary, content, status, visibility, tags, locale, and framework targets
- preview Markdown/MDX before saving
- revision history viewer
- publish workflow using the Phase 8 owner-token protection
