# Easiio Docs Module — Phase 6 Framework Exporters

## Goal

Phase 6 turns Easiio Docs spaces into reviewable framework export packages for:

- Next.js MDX
- Docusaurus
- MkDocs
- Hugo
- VitePress
- static HTML

The exporter is local-first and approval-gated. Preview endpoints are read-only. ZIP package creation requires explicit confirmation.

## Added files

```text
backend/docs_exporters.py
tests/exporters_static.test.js
EASIIO_DOCS_MODULE_PHASE6.md
```

## Updated files

```text
backend/app.py
tests/test_docs_backend.py
README.md
```

## API endpoints

```text
GET  /api/docs/export/preview?site_id=<site_id>&target=<target>
POST /api/docs/export/package
```

Supported `target` values:

```text
nextjs-mdx
docusaurus
mkdocs
hugo
vitepress
static-html
```

## Safety behavior

By default, framework exports include only documents where:

```text
status = published
visibility = public
framework_targets contains selected target
```

The exporter excludes by default:

- draft documents
- archived documents
- private documents
- internal documents
- login-required documents
- documents that do not explicitly target the requested framework

ZIP package writing is blocked unless the request includes:

```json
{"confirmExportPackage": true}
```

## Example preview

```bash
curl -s 'http://127.0.0.1:8110/api/docs/export/preview?site_id=ai-solo-company&target=docusaurus'
```

The response includes generated file paths and full file content for review, plus:

```json
{
  "requiresExportApproval": true,
  "packageBlocked": true
}
```

## Example package execution

```bash
curl -s http://127.0.0.1:8110/api/docs/export/package \
  -H 'Content-Type: application/json' \
  -d '{"confirmExportPackage":true,"site_id":"ai-solo-company","target":"docusaurus","approvedBy":"reviewer"}'
```

ZIP output path:

```text
/home/jianl/.hermes/tools/easiio_docs_module/dist/easiio-docs-exports/<site_id>-<target>.zip
```

## Generated structure by target

### Next.js MDX

```text
content/docs/index.mdx
content/docs/<slug>.mdx
easiio-docs-export-manifest.json
README.md
```

### Docusaurus

```text
docs/<slug>.md
sidebars.js
easiio-docs-export-manifest.json
README.md
```

### MkDocs

```text
docs/index.md
docs/<slug>.md
mkdocs.yml
easiio-docs-export-manifest.json
README.md
```

### Hugo

```text
content/docs/_index.md
content/docs/<slug>.md
config.toml
easiio-docs-export-manifest.json
README.md
```

### VitePress

```text
docs/index.md
docs/<slug>.md
docs/.vitepress/config.js
easiio-docs-export-manifest.json
README.md
```

### Static HTML

```text
index.html
<slug>.html
assets/easiio-docs-preview.css
easiio-docs-export-manifest.json
README.md
```

## Validation

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py backend/docs_wordpress.py backend/docs_rag.py backend/docs_exporters.py
node --check frontend/docs.js
node tests/docs_static.test.js
node tests/sitelet_preview_static.test.js
node tests/wp_plugin_static.test.js
node tests/rag_sync_static.test.js
node tests/exporters_static.test.js
python3 tests/test_docs_backend.py -v
```

Expected result:

```text
PASS Phase 6 framework exporter helpers and endpoints are wired
Ran 14 tests ... OK
```

## Runtime smoke

Phase 6 runtime smoke verified:

- `/health`
- document creation
- Docusaurus export preview
- package denial without `confirmExportPackage`
- approved Docusaurus ZIP package creation
- ZIP contains `docs/getting-started.md`
- ZIP contains `easiio-docs-export-manifest.json`
- static HTML preview contains `getting-started.html`

Smoke marker:

```text
easiio_docs_phase6_smoke_ok
```

## Next recommended phase

Phase 7 should add an admin/export UI so a site owner can choose a docs space, target framework, preview generated files, download ZIP packages, and later hand off exports to Sitelet/deployment workflows.
