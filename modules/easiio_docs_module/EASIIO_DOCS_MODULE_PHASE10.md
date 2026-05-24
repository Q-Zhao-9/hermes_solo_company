# Easiio Docs Module — Phase 10 Import/Export Management

Phase 10 adds safe import/export management on top of the Phase 9 admin editor and Phase 8 owner-token protection.

## Implemented files

New:

```text
backend/docs_importers.py
tests/import_export_static.test.js
EASIIO_DOCS_MODULE_PHASE10.md
```

Updated:

```text
backend/app.py
frontend/admin.html
frontend/admin.js
tests/test_docs_backend.py
tests/admin_export_ui_static.test.js
tests/admin_editor_ui_static.test.js
README.md
```

## New backend endpoints

```text
POST /api/docs/import/preview
POST /api/docs/import/execute
GET  /api/docs/bundle/preview
POST /api/docs/bundle/package
```

## Import preview

`POST /api/docs/import/preview` accepts JSON file arrays and returns a reviewable import plan. It detects whether each slug is a create or update before anything is written.

Supported source formats:

```text
markdown-folder
docusaurus
mkdocs
vitepress
hugo
easiio-bundle
```

Example payload:

```json
{
  "site_id": "ai-solo-company",
  "source_format": "docusaurus",
  "default_status": "draft",
  "default_visibility": "private",
  "framework_targets": ["sitelet", "static-html"],
  "files": [
    {
      "path": "docs/getting-started.md",
      "content": "---\ntitle: Getting Started\ncategory: Guide\n---\n# Getting Started\nImported content."
    }
  ]
}
```

Returns:

```text
exportType: easiio-docs-import-preview
requiresImportApproval: true
importBlocked: true
conflictCount: <number>
```

## Import execution

`POST /api/docs/import/execute` is confirmation-gated:

```json
{
  "confirmImport": true
}
```

Without the flag, the endpoint returns `409` and does not write anything.

Imported docs default to:

```text
status=draft
visibility=private
```

unless frontmatter or payload defaults override them. This keeps imports review-first and avoids accidentally publishing migrated docs.

## Portable Easiio Docs bundles

Phase 10 also adds a portable bundle format:

```text
easiio-docs-portable-bundle/v1
```

Preview:

```text
GET /api/docs/bundle/preview?site_id=<site_id>
```

Package:

```text
POST /api/docs/bundle/package
```

Package creation requires:

```json
{
  "confirmBundlePackage": true
}
```

ZIP output directory:

```text
dist/easiio-docs-bundles/
```

ZIP contents include:

```text
easiio-docs-bundle.json
README.md
```

## Admin UI

`/docs/admin.html` now includes:

- import source selector
- default import status/visibility controls
- file JSON textarea
- import preview button
- approved import execution button
- portable bundle preview button
- portable bundle ZIP button

The UI sends owner auth through:

```text
Authorization: Bearer [REDACTED]
```

and still requires browser confirmation before execution/package flags are sent.

## Safety behavior

- Import preview is read-only.
- Import execution requires owner auth when `EASIIO_DOCS_OWNER_TOKEN` is configured.
- Import execution requires `confirmImport:true`.
- Bundle package creation requires `confirmBundlePackage:true`.
- Imports default to draft/private.
- Existing slug conflicts are surfaced before execution.
- Public published embed reads remain public.

## Verification

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py backend/docs_wordpress.py backend/docs_rag.py backend/docs_exporters.py backend/docs_importers.py
node --check frontend/docs.js
node --check frontend/admin.js
node tests/docs_static.test.js
node tests/sitelet_preview_static.test.js
node tests/wp_plugin_static.test.js
node tests/rag_sync_static.test.js
node tests/exporters_static.test.js
node tests/admin_export_ui_static.test.js
node tests/admin_editor_ui_static.test.js
node tests/import_export_static.test.js
python3 tests/test_docs_backend.py -v
```

Runtime smoke marker:

```text
easiio_docs_phase10_smoke_ok
phase10_smoke_cleanup_ok
```

## Next recommended phase

Phase 11 should add localization/multilingual docs:

- locale-aware listing and route filters
- localized slug/path export behavior
- fallback from locale-specific docs to default locale
- admin UI locale management
- import/export handling for locale folders
