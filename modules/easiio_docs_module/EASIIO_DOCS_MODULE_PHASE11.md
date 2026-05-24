# Easiio Docs Module — Phase 11 Localization / Multilingual Docs

## Summary

Phase 11 adds multilingual documentation support to the reusable Easiio Docs Module.

It keeps the module local-first and framework-agnostic while adding locale-aware behavior for:

- document list filtering
- single-document lookup with fallback language behavior
- site summary locale counts
- framework export preview/package paths
- import preview/execution metadata
- portable bundle preview/package metadata
- admin UI filters and fallback controls

## Updated files

```text
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_db.py
/home/jianl/.hermes/tools/easiio_docs_module/backend/app.py
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_exporters.py
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_importers.py
/home/jianl/.hermes/tools/easiio_docs_module/frontend/admin.html
/home/jianl/.hermes/tools/easiio_docs_module/frontend/admin.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/test_docs_backend.py
/home/jianl/.hermes/tools/easiio_docs_module/tests/localization_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/README.md
```

## API behavior

### Health

```text
GET /health
```

Reports:

```json
{
  "phase": "11-localization",
  "adminAuthConfigured": true
}
```

`adminAuthConfigured` depends on whether `EASIIO_DOCS_OWNER_TOKEN` is set.

### Locale-filtered list

```text
GET /api/docs/docs?site_id=<site>&status=published&visibility=public&locale=es
```

Returns only docs whose normalized `locale` is `es`.

### Localized single-doc lookup with fallback

```text
GET /api/docs/doc?site_id=<site>&slug=<slug>&locale=es&fallback_locale=en
```

Behavior:

1. If the requested slug exists in the requested locale, return it.
2. If the slug exists but is not in the requested locale, look for a same-category fallback document in `fallback_locale`.
3. If no category fallback exists, return the original slug document and mark fallback usage.

The response includes:

```json
{
  "ok": true,
  "fallbackUsed": true,
  "doc": {
    "locale": "en"
  }
}
```

### Locale-aware site summary

```text
GET /api/docs/space?site_id=<site>
```

The summary now includes locale counts:

```json
{
  "counts": {
    "locales": {
      "en": 10,
      "es": 7,
      "zh-cn": 4
    }
  }
}
```

### Localized framework exports

```text
GET /api/docs/export/preview?site_id=<site>&target=docusaurus&locale=es
POST /api/docs/export/package
```

Export preview/package accepts `locale` and filters docs before generating files.

Example Docusaurus localized path:

```text
i18n/es/docusaurus-plugin-content-docs/current/empezar.md
```

The export manifest includes locale metadata.

### Import locale detection

```text
POST /api/docs/import/preview
POST /api/docs/import/execute
```

Import preview/execution can infer locale from:

- explicit file object metadata: `{"locale":"es"}`
- frontmatter: `locale: es`
- path prefixes such as:
  - `en/docs/guide.md`
  - `es/docs/guia.md`
  - `zh-cn/docs/intro.md`

Import execution remains confirmation-gated with:

```json
{"confirmImport": true}
```

### Locale-aware portable bundles

```text
GET /api/docs/bundle/preview?site_id=<site>&locale=es
POST /api/docs/bundle/package
```

Bundle preview/package accepts `locale` and records it in bundle metadata.

Bundle package creation remains confirmation-gated with:

```json
{"confirmBundlePackage": true}
```

## Admin UI behavior

The protected admin UI at:

```text
/docs/admin.html
```

now includes:

- Locale filter
- Fallback locale
- locale-aware docs list loading
- locale-aware single-doc editing lookup
- locale-aware export preview/package
- locale-aware import preview/execute
- locale-aware portable bundle preview/package

Admin routes remain protected when `EASIIO_DOCS_OWNER_TOKEN` is configured.

## Safety

Phase 11 preserves existing safety rules:

- public published docs remain readable without auth for embeds
- non-public/draft reads require owner token when configured
- write/action endpoints remain owner-protected when configured
- package/import actions remain confirmation-gated
- private/internal docs are not exported, bundled, imported as public, or synced by default
- owner tokens/secrets are never exposed in responses or docs

## Verification

Full verification command that passed:

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
node tests/localization_static.test.js
python3 tests/test_docs_backend.py -v
```

Result:

```text
PASS Phase 11 localization assets and routes are wired
Ran 21 tests
OK
```

Runtime smoke marker:

```text
easiio_docs_phase11_smoke_ok
```

Cleanup marker:

```text
phase11_smoke_cleanup_ok
```

## Recommended Phase 12

Recommended next phase: deployment handoff / publish workflow.

Possible scope:

- approval-gated handoff from docs exports to Sitelet/deployment workflows
- deployment plan preview endpoint
- deployment package manifest for docs spaces
- audit trail for export/import/package/deploy handoffs
- safer production-oriented operator flow for generated docs artifacts
