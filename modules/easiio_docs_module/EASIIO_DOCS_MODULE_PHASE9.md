# Easiio Docs Module — Phase 9 In-Browser Docs Editor/Admin Content Management

Phase 9 expands the protected `/docs/admin.html` console from export/package management into a practical in-browser docs editor.

## Scope

Phase 9 focuses on local-first admin content management while preserving all Phase 8 auth/permission hardening.

Implemented capabilities:

- load all docs for a `site_id`
- create a new docs page
- edit an existing docs page
- save a doc through `POST /api/docs/doc`
- delete a doc through `POST /api/docs/doc/delete`
- inspect revisions through `GET /api/docs/revisions`
- manage publishing metadata from the browser
- preserve export preview/package controls in the same admin UI

## Updated files

```text
frontend/admin.html
frontend/admin.js
frontend/admin.css
backend/app.py
tests/test_docs_backend.py
tests/admin_export_ui_static.test.js
tests/admin_editor_ui_static.test.js
README.md
```

## Admin UI route

```text
GET /docs/admin.html
GET /docs/admin.js
GET /docs/admin.css
```

These routes remain protected when `EASIIO_DOCS_OWNER_TOKEN` is configured.

## Editor fields

The Phase 9 editor supports:

- `site_id`
- `slug`
- `title`
- `summary`
- `content`
- `content_format`
  - `markdown`
  - `mdx`
  - `html`
  - `text`
- `status`
  - `draft`
  - `published`
  - `archived`
- `visibility`
  - `public`
  - `private`
  - `login_required`
  - `internal`
- `category`
- `tags`
- `version_label`
- `locale`
- `changed_by`
- `framework_targets`
  - `nextjs-mdx`
  - `wordpress-shortcode`
  - `sitelet`
  - `docusaurus`
  - `mkdocs`
  - `hugo`
  - `vitepress`
  - `static-html`
  - `rag`
- `rag_enabled`

## Admin JS functions

`frontend/admin.js` now exposes:

```text
loadDocs
editDoc
saveDoc
deleteDoc
loadRevisions
collectEditorPayload
populateEditor
renderDocList
renderRevisions
previewExport
createPackage
authHeaders
ownerToken
```

## Safety behavior

Phase 9 does not loosen Phase 8 security.

When `EASIIO_DOCS_OWNER_TOKEN` is configured:

- admin UI assets require owner authorization
- `POST /api/docs/doc` requires owner authorization
- `POST /api/docs/doc/delete` requires owner authorization
- `GET /api/docs/revisions` requires owner authorization
- draft/private/internal/login-required reads require owner authorization
- public published docs remain readable for website embeds

Editor requests send:

```text
Authorization: Bearer [REDACTED]
```

when the operator enters an owner token in the UI.

## Health phase

`GET /health` now reports:

```json
{
  "phase": "9-admin-editor",
  "adminAuthConfigured": true
}
```

## Verification

Full verification command used:

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
node tests/admin_editor_ui_static.test.js
python3 tests/test_docs_backend.py -v
```

Result:

```text
PASS Phase 9 admin/export UI auth assets and routes are wired
PASS Phase 9 admin editor UI assets are wired
Ran 17 tests
OK
```

## Runtime smoke

Runtime smoke covered:

- health reports `phase=9-admin-editor`
- admin auth configured
- admin page is blocked without token
- admin page loads with token
- doc create is blocked without token
- doc create succeeds with token
- draft/private list is blocked without token
- draft/private list succeeds with token
- doc update creates another revision
- published public doc is readable without token
- revision history loads with token
- delete succeeds with token

Smoke marker:

```text
easiio_docs_phase9_smoke_ok
```

Cleanup marker:

```text
phase9_smoke_cleanup_ok
```

## Recommended next phase

Phase 10 should add import/export management:

- import Markdown folders
- import Docusaurus/MkDocs/VitePress/Hugo docs
- export a portable Easiio Docs bundle
- dry-run import previews
- conflict detection for existing slugs
- confirmation-gated import execution
