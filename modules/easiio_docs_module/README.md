# Easiio Docs Module

Reusable documentation/knowledge module for websites built by Hermes and Easiio.

Phase 1 is the backend/content core. It stores Markdown/MDX/HTML/text documents by `site_id`, tracks revisions, exposes an HTTP JSON API, and records metadata needed for later integrations with Sitelet, WordPress, Next.js MDX, Docusaurus, MkDocs, Hugo, VitePress, and chatbot RAG.

Phase 2 adds an embeddable frontend widget (`docs.js` + `docs.css`) that can be dropped into static websites, Sitelet previews, WordPress pages, and future app pages.

Phase 3 adds Sitelet preview integration: the docs module can render a public docs space or a single document into a Sitelet-compatible multi-page payload, with upload explicitly confirmation-gated.

Phase 4 adds WordPress integration: a shortcode plugin package, shortcode-generation API, and draft-first WordPress handoff plans for Hermes MCP review workflows. Publishing remains blocked until a separate human approval.

Phase 5 adds chatbot/RAG sync: published public docs with `rag_enabled=true` and `framework_targets` containing `rag` can be previewed as chatbot knowledge chunks and synced into the website chatbot manual RAG store after explicit approval.

Phase 6 adds framework exporters: published public docs can be previewed and packaged as Next.js MDX, Docusaurus, MkDocs, Hugo, VitePress, or static HTML ZIP exports after explicit approval.

Phase 7 adds an admin/export UI at `/docs/admin.html` so site owners can preview generated export files and create approved ZIP packages through a browser workflow.

Phase 8 adds owner-token auth hardening for admin UI assets, write/action endpoints, and non-public/draft reads when `EASIIO_DOCS_OWNER_TOKEN` is configured.

Phase 9 expands `/docs/admin.html` into an in-browser docs editor/admin content-management UI for loading docs, creating/editing pages, managing metadata, saving revisions, deleting docs, and inspecting revision history.

Phase 10 adds import/export management: import previews and approval-gated import execution for Markdown/Docusaurus/MkDocs/VitePress/Hugo/Easiio bundle sources, plus portable Easiio Docs bundle preview/package endpoints.

Phase 11 adds localization/multilingual docs: locale filtering, locale-aware summary counts, fallback document lookup, localized export paths, locale detection during imports, locale-aware portable bundles, and admin UI locale filters.

Phase 12 adds deployment handoff: reviewed docs exports can be previewed and packaged into deployment handoff ZIPs with a manifest, operator checklist, locale/environment metadata, and explicit `confirmDeploymentPackage:true` approval. The module still does not deploy or publish externally by itself.

Phase 13 adds deployment history: every confirmed deployment handoff package is recorded in a local SQLite audit log with target, environment, locale, package path/size, approver, manifest summary, and timestamp. History is owner-protected and does not store auth tokens or secrets.

Phase 14 adds audit operations: deployment history can be filtered by target/environment/locale, summarized into dashboard counts, and exported as owner-protected CSV for local review.

Phase 15 adds deployment package operations: package detail, download, compare, and checklist tracking.

Phase 16 adds approval workflow and release notes.

Phase 17 adds release dashboard and operator handoff report generation.

Phase 18 adds release archive and attestation workflow with SHA-256 hashes for local review.

Phase 19 adds release restore / rollback planning: archive integrity verification, rollback plan generation, and local restore package preparation.

Phase 20 adds deployment connector dry-run adapters for Sitelet, WordPress, and static hosting. Connector preflight is confirmation-gated with `confirmConnectorDryRun:true`, local-only, and never calls external APIs.

Phase 21 adds connector profiles and dry-run history. Connector profile persistence is owner-protected, confirmation-gated with `confirmSaveConnectorProfile:true`, and stores secret placeholders only in `redactedConfig`.

Phase 22 adds connector runbooks and dry-run comparison. Operators can generate Markdown runbooks from local dry-run records and compare two dry-runs without deploying, publishing, uploading, or calling external services.

## Architecture

```text
Website / Hermes / admin tool
  -> Easiio Docs HTTP API
  -> SQLite docs database
  -> future adapters:
     - embeddable docs.js widget
     - Sitelet preview
     - WordPress shortcode/plugin
     - WordPress draft-first MCP handoff
     - Next.js MDX export
     - Docusaurus/MkDocs/Hugo/VitePress/static HTML export
     - chatbot RAG sync
```

## Project paths

```text
/home/jianl/.hermes/tools/easiio_docs_module
/home/jianl/.hermes/tools/easiio_docs_module/backend/app.py
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_db.py
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_sitelet.py
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_wordpress.py
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_rag.py
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_exporters.py
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_deploy.py
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_audit.py
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_connectors.py
/home/jianl/.hermes/tools/easiio_docs_module/frontend/docs.js
/home/jianl/.hermes/tools/easiio_docs_module/frontend/docs.css
/home/jianl/.hermes/tools/easiio_docs_module/frontend/demo.html
/home/jianl/.hermes/tools/easiio_docs_module/frontend/admin.html
/home/jianl/.hermes/tools/easiio_docs_module/frontend/admin.js
/home/jianl/.hermes/tools/easiio_docs_module/frontend/admin.css
/home/jianl/.hermes/tools/easiio_docs_module/tests/test_docs_backend.py
/home/jianl/.hermes/tools/easiio_docs_module/tests/docs_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/sitelet_preview_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/wp_plugin_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/rag_sync_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/exporters_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/admin_export_ui_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/admin_editor_ui_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/import_export_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/localization_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/deployment_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/deployment_history_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/deployment_ops_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/deployment_connectors_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/deployment_connector_profiles_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/deployment_connector_runbooks_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/wordpress-plugin/easiio-docs/easiio-docs.php
/home/jianl/.hermes/tools/easiio_docs_module/dist/easiio-docs-wordpress-plugin.zip
```

Default SQLite DB:

```text
/home/jianl/.hermes/tools/easiio_docs_module/data/easiio_docs.db
```

Override with:

```bash
EASIIO_DOCS_DB=/path/to/easiio_docs.db
```

Default chatbot RAG store for Phase 5:

```text
/home/jianl/.hermes/tools/website_chatbot/data/rag_content.json
```

Override with:

```bash
EASIIO_CHATBOT_RAG_STORE=/path/to/rag_content.json
```

Phase 8 owner/admin token protection:

```bash
EASIIO_DOCS_OWNER_TOKEN=[REDACTED]
```

When configured, protected requests must send one of:

```text
Authorization: Bearer [REDACTED]
X-Easiio-Owner-Token: [REDACTED]
?owner_token=[REDACTED]
```

Do not publish or commit this token. The query-string option is mainly for local/manual debugging; prefer headers behind a protected proxy.

## Data model

A document includes:

```text
site_id
slug
title
summary
content
content_format: markdown | mdx | html | text
status: draft | published | archived
visibility: public | private | login_required | internal
category
tags
version_label
locale
framework_targets
rag_enabled
created_at
updated_at
```

Supported `framework_targets` in Phase 1:

```text
nextjs-mdx
wordpress-shortcode
sitelet
docusaurus
mkdocs
hugo
vitepress
static-html
rag
```

Documents are isolated by `(site_id, slug)`, so the same slug can exist for different websites without leaking content.

## Run backend

```bash
python3 /home/jianl/.hermes/tools/easiio_docs_module/backend/app.py --host 127.0.0.1 --port 8110
```

Health check:

```bash
curl http://127.0.0.1:8110/health
```

## Embedding in websites

Public reader mode:

```html
<link rel="stylesheet" href="http://localhost:8110/docs/docs.css" />
<div id="easiio-docs-root"></div>
<script
  src="http://localhost:8110/docs/docs.js"
  data-easiio-docs
  data-api-base="http://localhost:8110"
  data-site-id="ai-solo-company"
  data-mode="public"
  data-root-selector="#easiio-docs-root"
  data-title="AI Solo Company Documentation"
  data-subtitle="Guides, manuals, and reusable website handoff notes.">
</script>
```

Admin/editor mode should only be used on protected/admin pages:

```html
data-mode="admin"
```

Optional integration filters:

```html
data-target-filter="sitelet"
data-target-filter="wordpress-shortcode"
data-target-filter="nextjs-mdx"
data-target-filter="rag"
```

Protected/login pages can forward credentials:

```html
data-login-required="true"
data-credential-mode="include"
data-auth-token="SERVER_RENDERED_TOKEN"
```

Local demo page:

```text
http://127.0.0.1:8110/docs/demo.html
```

Admin/export UI:

```text
http://127.0.0.1:8110/docs/admin.html
```

Use the admin UI on protected/local-owner pages only. It can preview generated framework export files and, after browser confirmation, call the confirmation-gated ZIP package endpoint with `confirmExportPackage:true`.

In Phase 8, if `EASIIO_DOCS_OWNER_TOKEN` is configured, `/docs/admin.html`, `/docs/admin.js`, and `/docs/admin.css` require owner authorization. The admin UI includes an **Owner token** password field and sends it as an `Authorization: Bearer [REDACTED]` header for export preview/package requests. Public published docs remain readable without a token; draft/private/internal/login-required reads and all write/action endpoints require owner authorization.

Phase 9 adds an in-browser content editor to the same protected admin UI. Operators can:

- load all docs for a `site_id`, including draft/private docs when owner-authenticated
- create a new doc
- edit slug, title, summary, Markdown/MDX/HTML/text content, status, visibility, category, tags, version label, locale, changed-by, framework targets, and RAG eligibility
- save through `POST /api/docs/doc`, creating a revision
- delete through `POST /api/docs/doc/delete`
- inspect revision history through `GET /api/docs/revisions`

Phase 10 adds import/export management to the same protected UI. Operators can:

- paste JSON file arrays from Markdown folders, Docusaurus, MkDocs, VitePress, or Hugo
- preview imports through `POST /api/docs/import/preview`
- detect existing-slug conflicts before writing
- execute approved imports through `POST /api/docs/import/execute` with `confirmImport:true`
- preview a portable Easiio Docs bundle through `GET /api/docs/bundle/preview`
- create an approved portable bundle ZIP through `POST /api/docs/bundle/package` with `confirmBundlePackage:true`

Phase 11 adds multilingual/localized workflows to the same protected UI. Operators can:

- filter the docs list by locale, such as `en`, `es`, `zh-cn`, or `fr`
- set a fallback locale for single-doc lookup, so a missing translated slug can resolve to the default-language document
- include the selected locale in export preview/package, import preview/execute, and portable bundle preview/package actions
- keep locale as document metadata for export manifests, import previews, and bundle manifests

Phase 12 adds deployment handoff controls to the same protected UI. Operators can:

- preview deployment handoff files through `GET /api/docs/deploy/preview`
- choose deployment target and environment such as Sitelet/staging or static HTML/production
- review the generated `easiio-docs-deployment-manifest.json` and operator checklist before packaging
- create a local reviewed handoff ZIP through `POST /api/docs/deploy/package` only after browser confirmation sends `confirmDeploymentPackage:true`
- keep the process handoff-only: no automatic publishing, DNS changes, WordPress publishing, Sitelet upload, or external hosting writes

## API examples

Create/update a document:

```bash
curl -s http://127.0.0.1:8110/api/docs/doc \
  -H 'Content-Type: application/json' \
  -d '{
    "site_id":"ai-solo-company",
    "slug":"getting-started",
    "title":"Getting Started with AI Solo Company",
    "summary":"Reusable docs module onboarding page.",
    "content":"# Getting Started\nUse this docs module across websites.",
    "content_format":"markdown",
    "status":"published",
    "visibility":"public",
    "category":"Guide",
    "tags":["docs","onboarding"],
    "version_label":"1.0",
    "locale":"en",
    "framework_targets":["nextjs-mdx","wordpress-shortcode","sitelet","docusaurus","mkdocs","hugo","vitepress"],
    "rag_enabled":true
  }'
```

List/search documents:

```bash
curl -s 'http://127.0.0.1:8110/api/docs/docs?site_id=ai-solo-company&q=onboarding&status=published'
```

Get one document:

```bash
curl -s 'http://127.0.0.1:8110/api/docs/doc?site_id=ai-solo-company&slug=getting-started'
```

Get a localized document with fallback to English when the translated slug is not available:

```bash
curl -s 'http://127.0.0.1:8110/api/docs/doc?site_id=ai-solo-company&slug=billing&locale=es&fallback_locale=en'
```

List revisions:

```bash
curl -s 'http://127.0.0.1:8110/api/docs/revisions?site_id=ai-solo-company&slug=getting-started'
```

Get site docs summary:

```bash
curl -s 'http://127.0.0.1:8110/api/docs/space?site_id=ai-solo-company'
```

Build a Sitelet preview payload for a full docs space:

```bash
curl -s 'http://127.0.0.1:8110/api/docs/sitelet-preview?site_id=ai-solo-company&target=sitelet'
```

Build a Sitelet preview payload for one doc:

```bash
curl -s 'http://127.0.0.1:8110/api/docs/sitelet-preview?site_id=ai-solo-company&slug=getting-started'
```

Upload is confirmation-gated. Do not call this endpoint unless a human has approved the generated `siteletPayload`:

```bash
curl -s http://127.0.0.1:8110/api/docs/sitelet-preview/upload \
  -H 'Content-Type: application/json' \
  -d '{"confirmSiteletUpload":true,"site_id":"ai-solo-company"}'
```

Generate a WordPress shortcode:

```bash
curl -s 'http://127.0.0.1:8110/api/docs/wordpress/shortcode?site_id=ai-solo-company&api_base=https://docs.example.com&title=AI%20Solo%20Company%20Docs'
```

Generate a draft-first WordPress handoff plan:

```bash
curl -s 'http://127.0.0.1:8110/api/docs/wordpress/draft-plan?site_id=ai-solo-company&page_title=AI%20Solo%20Company%20Docs'
```

Draft execution is also confirmation-gated and returns an MCP handoff payload rather than publishing directly:

```bash
curl -s http://127.0.0.1:8110/api/docs/wordpress/draft-execution \
  -H 'Content-Type: application/json' \
  -d '{"confirmDraftCreation":true,"site_id":"ai-solo-company","page_title":"AI Solo Company Docs"}'
```

WordPress plugin package:

```text
/home/jianl/.hermes/tools/easiio_docs_module/dist/easiio-docs-wordpress-plugin.zip
```

Shortcode example:

```text
[easiio_docs site_id="ai-solo-company" api_base="https://docs.example.com" title="AI Solo Company Docs"]
```

Preview chatbot/RAG chunks from docs:

```bash
curl -s 'http://127.0.0.1:8110/api/docs/rag/preview?site_id=ai-solo-company'
```

Sync docs into the website chatbot manual RAG store after reviewing the preview:

```bash
curl -s http://127.0.0.1:8110/api/docs/rag/sync \
  -H 'Content-Type: application/json' \
  -d '{"confirmRagSync":true,"site_id":"ai-solo-company","approvedBy":"reviewer"}'
```

RAG sync defaults to `status=published`, `visibility=public`, `rag_enabled=true`, and `framework_targets` containing `rag`. Private/internal docs are not synced unless explicitly requested with `includePrivate` in a protected/admin workflow.

Preview framework export files for a target:

```bash
curl -s 'http://127.0.0.1:8110/api/docs/export/preview?site_id=ai-solo-company&target=docusaurus'
```

Preview localized framework export files:

```bash
curl -s 'http://127.0.0.1:8110/api/docs/export/preview?site_id=ai-solo-company&target=docusaurus&locale=es'
```

Supported Phase 6 export targets:

```text
nextjs-mdx
docusaurus
mkdocs
hugo
vitepress
static-html
```

Package a reviewed export as a local ZIP after explicit approval:

```bash
curl -s http://127.0.0.1:8110/api/docs/export/package \
  -H 'Content-Type: application/json' \
  -d '{"confirmExportPackage":true,"site_id":"ai-solo-company","target":"docusaurus","approvedBy":"reviewer"}'
```

Framework export defaults to `status=published`, `visibility=public`, and `framework_targets` containing the selected target. Private/internal/login-required/draft docs are excluded by default.

Preview a deployment handoff package for reviewed docs artifacts:

```bash
curl -s 'http://127.0.0.1:8110/api/docs/deploy/preview?site_id=ai-solo-company&target=sitelet&environment=staging&locale=en'
```

Create a reviewed deployment handoff ZIP after explicit approval:

```bash
curl -s http://127.0.0.1:8110/api/docs/deploy/package \
  -H 'Content-Type: application/json' \
  -d '{"confirmDeploymentPackage":true,"site_id":"ai-solo-company","target":"sitelet","environment":"staging","locale":"en","approvedBy":"reviewer"}'
```

Deployment handoff ZIPs are written under:

```text
/home/jianl/.hermes/tools/easiio_docs_module/dist/easiio-docs-deployments/
```

Deployment handoff packages include generated docs files plus `easiio-docs-deployment-manifest.json`. They are local handoff artifacts only and do not publish to Sitelet, WordPress, DNS, hosting, or production automatically.

Export ZIPs are written under:

```text
/home/jianl/.hermes/tools/easiio_docs_module/dist/easiio-docs-exports/
```

Delete a document:

```bash
curl -s http://127.0.0.1:8110/api/docs/doc/delete \
  -H 'Content-Type: application/json' \
  -d '{"site_id":"ai-solo-company","slug":"getting-started"}'
```

## Verification

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py backend/docs_wordpress.py backend/docs_rag.py backend/docs_exporters.py backend/docs_importers.py backend/docs_deploy.py backend/docs_audit.py
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
node tests/deployment_static.test.js
node tests/deployment_history_static.test.js
node tests/deployment_ops_static.test.js
python3 tests/test_docs_backend.py -v
```

## Phase roadmap

### Phase 1 — Core backend/content system

Completed:

- SQLite document spaces
- document CRUD
- site isolation by `site_id`
- search/list filters
- revision history
- status/visibility/content-format normalization
- framework target metadata
- site summary endpoint
- HTTP API
- unit tests and runtime smoke test

### Phase 2 — Embeddable frontend widget

Completed:

- `frontend/docs.js`
- `frontend/docs.css`
- `frontend/demo.html`
- public reader mode
- admin/editor mode
- document search
- integration target filter
- site summary display
- Markdown/MDX-ish safe rendering for non-HTML formats
- optional credential forwarding with `data-credential-mode` and `data-auth-token`
- backend serving for `/docs/docs.js`, `/docs/docs.css`, and `/docs/demo.html`
- CORS preflight/asset headers
- static frontend tests and runtime smoke test

### Phase 3 — Sitelet preview integration

Completed:

- `backend/docs_sitelet.py`
- `GET /api/docs/sitelet-preview`
- confirmation-gated `POST /api/docs/sitelet-preview/upload`
- full docs-space Sitelet payload rendering
- single-document Sitelet payload rendering
- generated homepage plus per-doc pages
- generated `/assets/easiio-docs-preview.css`
- filters for `status`, `visibility`, and `target`
- upload instructions that keep `requiresUploadApproval:true` and `uploadBlocked:true` until explicit confirmation
- static and backend tests
- runtime smoke test

### Phase 4 — WordPress integration

Completed:

- `backend/docs_wordpress.py`
- WordPress plugin at `wordpress-plugin/easiio-docs/easiio-docs.php`
- packaged plugin ZIP at `dist/easiio-docs-wordpress-plugin.zip`
- shortcode `[easiio_docs site_id="..."]`
- login-required rendering via `require_login="true"`
- admin/editor-only mode via `mode="admin"`
- `GET /api/docs/wordpress/shortcode`
- `GET /api/docs/wordpress/draft-plan`
- confirmation-gated `POST /api/docs/wordpress/draft-execution`
- draft-first MCP handoff using `mcp_easiio_wp_create_draft_post`
- publishing blocked until a separate explicit human approval
- static WordPress plugin tests, backend tests, package verification, and runtime smoke test

### Phase 5 — Chatbot RAG sync

Completed:

- `backend/docs_rag.py`
- `GET /api/docs/rag/preview`
- confirmation-gated `POST /api/docs/rag/sync`
- conversion of Markdown/MDX/HTML/text docs into chatbot manual-knowledge items
- default filters: `status=published`, `visibility=public`, `rag_enabled=true`, and `framework_targets` containing `rag`
- per-site isolation using `site_id`
- replacement of prior Easiio Docs-generated chunks for the same `site_id` while preserving manual/external chatbot knowledge
- `EASIIO_CHATBOT_RAG_STORE` override support
- static and backend tests
- runtime smoke test

### Phase 6 — Framework exporters

Completed:

- `backend/docs_exporters.py`
- `GET /api/docs/export/preview`
- confirmation-gated `POST /api/docs/export/package`
- Next.js MDX export under `content/docs/*.mdx`
- Docusaurus export under `docs/*.md` with `sidebars.js`
- MkDocs export under `docs/*.md` with `mkdocs.yml`
- Hugo export under `content/docs/*.md` with `config.toml`
- VitePress export under `docs/*.md` with `docs/.vitepress/config.js`
- static HTML export with `index.html`, per-doc HTML files, and preview CSS
- generated `easiio-docs-export-manifest.json`
- default safety filters: `status=published`, `visibility=public`, and `framework_targets` containing the selected export target
- local ZIP output under `dist/easiio-docs-exports/`
- static and backend tests
- runtime smoke test

### Phase 7 — Admin/export UI

Completed:

- `frontend/admin.html`
- `frontend/admin.js`
- `frontend/admin.css`
- `GET /docs/admin.html`
- `GET /docs/admin.js`
- `GET /docs/admin.css`
- browser workflow to enter `site_id`, choose export target, preview generated files, and create approved ZIP packages
- UI support for Next.js MDX, Docusaurus, MkDocs, Hugo, VitePress, and static HTML export targets
- browser confirmation before sending `confirmExportPackage:true`
- reuse of Phase 6 safety filters and confirmation-gated package endpoint
- static and backend tests
- runtime smoke test

### Phase 8 — Auth/permissions and admin hardening

Completed:

- owner-token protection through `EASIIO_DOCS_OWNER_TOKEN`
- support for `Authorization: Bearer [REDACTED]` and `X-Easiio-Owner-Token` headers
- query-string `owner_token` fallback for local/manual debugging only
- protected admin UI asset routes when owner token is configured
- protected write/action endpoints:
  - `POST /api/docs/doc`
  - `POST /api/docs/doc/delete`
  - `POST /api/docs/sitelet-preview/upload`
  - `POST /api/docs/wordpress/draft-execution`
  - `POST /api/docs/rag/sync`
  - `POST /api/docs/export/package`
- owner-token requirement for draft/private/internal/login-required reads when token is configured
- public published document reads remain public for website embeds
- admin UI Owner token field and Bearer header forwarding for preview/package calls
- `/health` reports `phase:"8-auth-permissions"` and `adminAuthConfigured`
- static and backend tests
- runtime smoke marker `easiio_docs_phase8_smoke_ok`

### Phase 9 — In-browser docs editor/admin content management

Completed:

- expanded `frontend/admin.html` from export-only console into a docs editor workspace
- added `frontend/admin.js` editor operations:
  - `loadDocs`
  - `editDoc`
  - `saveDoc`
  - `deleteDoc`
  - `loadRevisions`
  - `collectEditorPayload`
  - `populateEditor`
  - `renderDocList`
  - `renderRevisions`
- added form controls for slug, title, summary, content, content format, status, visibility, category, tags, version label, locale, changed-by, framework targets, and `rag_enabled`
- preserved Phase 8 owner-token forwarding for all editor write/non-public read actions
- preserved Phase 7 export preview/package workflow in the same admin UI
- `/health` reports `phase:"9-admin-editor"` and `adminAuthConfigured`
- added `tests/admin_editor_ui_static.test.js`
- full verification and runtime smoke marker `easiio_docs_phase9_smoke_ok`

### Phase 10 — Import/export management

Completed:

- added `backend/docs_importers.py`
- added import preview endpoint `POST /api/docs/import/preview`
- added confirmation-gated import execution endpoint `POST /api/docs/import/execute` requiring `confirmImport:true`
- added portable Easiio Docs bundle preview endpoint `GET /api/docs/bundle/preview`
- added confirmation-gated portable bundle ZIP endpoint `POST /api/docs/bundle/package` requiring `confirmBundlePackage:true`
- supports source formats: `markdown-folder`, `docusaurus`, `mkdocs`, `vitepress`, `hugo`, `easiio-bundle`
- detects existing slug conflicts before import execution
- imports default to `draft` + `private` unless metadata/payload overrides them
- portable bundle ZIPs are written under `dist/easiio-docs-bundles/`
- admin UI now includes import controls and portable bundle controls
- `/health` reports `phase:"10-import-export-management"` and `adminAuthConfigured`
- added `tests/import_export_static.test.js`
- full verification and runtime smoke marker `easiio_docs_phase10_smoke_ok`

### Phase 11 — Localization/multilingual docs

Completed:

- `/health` now reports `phase:"11-localization"` and `adminAuthConfigured`
- locale normalization to lowercase BCP-47-ish values such as `en`, `es`, `zh-cn`, and `pt-br`
- `GET /api/docs/docs` supports `locale=<locale>` filtering
- `GET /api/docs/doc` supports `locale=<locale>&fallback_locale=<locale>` and returns `fallbackUsed`
- `GET /api/docs/space` summary includes locale counts under `counts.locales`
- framework export previews and approved packages accept `locale` and include locale metadata in manifests/documents
- localized Docusaurus export paths use `i18n/<locale>/docusaurus-plugin-content-docs/current/<slug>.md`
- localized MkDocs, VitePress, Hugo, static HTML, and Next.js MDX paths include locale-aware directories
- import preview/execute detects locale from file paths like `es/docs/guia.md` and from frontmatter/file metadata
- portable bundle preview/package accepts `locale` and records the selected locale in bundle metadata
- admin UI adds Locale filter and Fallback locale controls across list, edit, export, import, and bundle workflows
- added backend Phase 11 tests and `tests/localization_static.test.js`
- full verification and runtime smoke marker `easiio_docs_phase11_smoke_ok`

### Phase 12 — Deployment handoff / publish preparation

Completed:

- `/health` now reports `phase:"12-deployment-handoff"` and `adminAuthConfigured`
- added `backend/docs_deploy.py` for deployment handoff preview/package generation
- added `GET /api/docs/deploy/preview` for review-first deployment handoff previews
- added `POST /api/docs/deploy/package` requiring `confirmDeploymentPackage:true` before writing any ZIP
- generated handoff packages include docs files plus `easiio-docs-deployment-manifest.json`
- manifests include deployment target, environment, locale, status/visibility scope, file paths, document count, generated timestamp, and operator checklist
- supported deployment targets: `static-html`, `sitelet`, `wordpress`, `nextjs-mdx`, `docusaurus`, `mkdocs`, `hugo`, `vitepress`
- supported environments: `local`, `preview`, `staging`, `production`
- admin UI adds Deployment handoff controls with environment selector, preview button, and package button
- package creation remains owner-protected when auth is configured and handoff-only by design: no external deployment, publishing, DNS, hosting, WordPress, or Sitelet write occurs automatically
- handoff ZIPs are written under `dist/easiio-docs-deployments/`
- added backend Phase 12 tests and `tests/deployment_static.test.js`
- full verification and runtime smoke marker `easiio_docs_phase12_smoke_ok`

### Phase 13 — Deployment history / audit log

Completed Phase 13 adds a local deployment history/audit log for confirmed deployment handoff ZIP packages.

Implemented:

- `/health` now reports `phase:"13-deployment-history"` and `adminAuthConfigured`
- added `backend/docs_audit.py` with `DocsAuditStore`
- added local SQLite table `docs_deployment_audit`
- deployment package creation records audit metadata after `confirmDeploymentPackage:true`
- added owner-protected `GET /api/docs/deploy/history`
- added admin UI “Deployment history” controls in `/docs/admin.html`
- added `loadDeploymentHistory()` and `renderDeploymentHistory()` in `frontend/admin.js`
- added backend Phase 13 tests and `tests/deployment_history_static.test.js`
- added dedicated documentation in `EASIIO_DOCS_MODULE_PHASE13.md`

Recorded metadata includes target, export target, environment, locale, status/visibility scope, package path, package size, approved-by label, document count, file count, manifest JSON, file paths, and timestamp.

Safety behavior:

- no external deployment, upload, WordPress publish, Sitelet publish, hosting change, or DNS action is performed
- history endpoint is owner/admin protected when `EASIIO_DOCS_OWNER_TOKEN` is configured
- audit rows do not store raw owner tokens, auth headers, passwords, API keys, or secrets
- deployment history is local SQLite metadata only

### Phase 14 — Deployment audit operations

Completed Phase 14 adds audit operations on top of Phase 13 deployment history.

Implemented:

- `/health` now reports `phase:"18-release-archive"`
- added owner-protected `GET /api/docs/deploy/summary` for deployment audit dashboard counts
- added owner-protected `GET /api/docs/deploy/history.csv` for CSV export
- deployment history now supports `target`, `environment`, and `locale` filters
- `backend/docs_audit.py` now includes `filter_deployment_history`, `summarize_deployment_history`, and `deployment_history_to_csv`
- admin UI adds target/environment/locale history filters
- admin UI adds Load audit summary and Export history CSV actions
- added backend Phase 14 tests and `tests/deployment_ops_static.test.js`

Safety behavior remains local and review-first: audit operations only read local SQLite metadata or export CSV; they never deploy, publish, upload, or store secrets.



### Phase 15 — Deployment package operations

Phase 15 adds owner-protected local package operations on top of the deployment audit log. It keeps the workflow review-first and local-only while allowing operators to inspect, re-download, compare, and track checklist status for previously created deployment handoff ZIP packages.

New endpoints:

```text
GET  /api/docs/deploy/package?id=<audit_id>
GET  /api/docs/deploy/package/download?id=<audit_id>
GET  /api/docs/deploy/compare?left_id=<audit_id>&right_id=<audit_id>
POST /api/docs/deploy/checklist
```

Admin UI adds a **Deployment package operations** panel with package ID, compare left/right IDs, checklist JSON, Load package detail, Download package ZIP, Compare packages, and Update checklist controls.

Dedicated documentation:

```text
/home/jianl/.hermes/tools/easiio_docs_module/EASIIO_DOCS_MODULE_PHASE15.md
```

Verification includes:

```bash
node tests/deployment_package_ops_static.test.js
node tests/deployment_approval_static.test.js
python3 tests/test_docs_backend.py -v
```

Smoke markers:

```text
easiio_docs_phase15_smoke_ok
phase15_smoke_cleanup_ok
```


## Phase 16 — Deployment approval workflow and release notes

Phase 16 adds owner-protected approval metadata for local deployment handoff packages.

New endpoints:

```text
POST /api/docs/deploy/approval
GET  /api/docs/deploy/approvals?id=<audit_id>
GET  /api/docs/deploy/release-notes?id=<audit_id>
```

Supported approval states are `draft`, `reviewed`, `approved`, `released`, and `rejected`. Approved/released packages are locked from later checklist mutation. Release notes are generated from the package manifest and local ZIP content. Admin UI adds approval status, actor, note, release-notes, and approval-history controls. Dedicated docs: `EASIIO_DOCS_MODULE_PHASE16.md`.


## Phase 17 — Release dashboard and operator handoff report

Phase 17 adds owner-protected release review operations:

```text
GET /api/docs/deploy/releases
GET /api/docs/deploy/handoff-report
```

The release dashboard summarizes packages by approval status, readiness scoring, and release queue. The operator handoff report generates Markdown for a selected deployment audit package. These are local review artifacts only and do not deploy, publish, upload, or call external services.

Dedicated docs: `EASIIO_DOCS_MODULE_PHASE17.md`. Static test: `tests/deployment_release_dashboard_static.test.js`. Smoke marker: `easiio_docs_phase17_smoke_ok`.


## Phase 18 — Release archive and attestation workflow

Health history includes `phase:"18-release-archive"`. Phase 18 adds a local, owner-protected release archive for ready deployment packages. It creates a durable attestation JSON and archived operator handoff Markdown report with SHA-256 hashes for the package ZIP, manifest, handoff report, release notes, and individual files inside the ZIP.

New endpoints:

```text
POST /api/docs/deploy/archive
GET  /api/docs/deploy/archive
GET  /api/docs/deploy/attestation?id=<audit_id>
GET  /api/docs/deploy/report/download?id=<audit_id>
```

Archive creation is confirmation-gated with `confirmArchiveRelease:true`. Archive files are written under `dist/easiio-docs-release-archive/`. This remains a local review/attestation workflow only; it does not deploy, publish, upload, change DNS, or call external services.


Compatibility note: Phase history includes `17-release-dashboard` and `18-release-archive`; current health marker is `19-restore-planning`.


## Phase 19 — Release restore / rollback planning

Health reports `phase:"19-restore-planning"`. Phase 19 adds a local, owner-protected restore planning workflow for archived releases. It verifies Phase 18 archive integrity by recomputing SHA-256 hashes, generates a rollback plan from a current release to a previous archived release, and prepares a local restore package ZIP for human operator review.

New endpoints:

```text
GET  /api/docs/deploy/archive/integrity?id=<audit_id>
GET  /api/docs/deploy/rollback-plan?id=<current_audit_id>&previous_id=<rollback_target_audit_id>
POST /api/docs/deploy/restore-package
```

Restore package creation is confirmation-gated with `confirmPrepareRestore:true`. Restore ZIPs are written under `dist/easiio-docs-restore-packages/`. This remains a local-only planning workflow: it does not deploy, publish, upload, call WordPress/Sitelet/hosting APIs, change DNS, or store secrets.

Dedicated docs: `EASIIO_DOCS_MODULE_PHASE19.md`. Static test: `tests/deployment_restore_static.test.js`. Smoke marker: `easiio_docs_phase19_smoke_ok`.

## Phase 20 — Deployment connector dry-run adapters

Current health marker:

```text
22-connector-runbooks
```

Phase 20 adds local-only deployment connector dry-run/preflight adapters. It does not deploy, publish, upload, change DNS, call WordPress, call Sitelet, or call external hosting APIs.

New backend file:

```text
backend/docs_connectors.py
```

New owner-protected endpoints:

```text
GET  /api/docs/deploy/connectors
POST /api/docs/deploy/connector/preflight
```

`POST /api/docs/deploy/connector/preflight` requires explicit dry-run confirmation:

```json
{
  "confirmConnectorDryRun": true
}
```

Supported connector dry-run adapters:

```text
sitelet
wordpress
static-hosting
```

Preflight checks local metadata only:

- package audit record exists
- local deployment ZIP exists
- release readiness score and operator handoff readiness
- connector target compatibility
- required connector config fields
- external calls are blocked

Connector config is returned only as `redactedConfig`; fields such as API tokens, authorization headers, passwords, secrets, private keys, and credentials are replaced with `[REDACTED]`.

Admin UI adds a **Deployment connector dry-run** panel with connector type, connector config JSON, connector catalog loading, and preflight execution.

Phase 20 docs:

```text
EASIIO_DOCS_MODULE_PHASE20.md
```

Phase 20 static test:

```text
tests/deployment_connectors_static.test.js
```

Validation:

```bash
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py backend/docs_wordpress.py backend/docs_rag.py backend/docs_exporters.py backend/docs_importers.py backend/docs_deploy.py backend/docs_audit.py backend/docs_connectors.py
node --check frontend/docs.js
node --check frontend/admin.js
for f in tests/*.test.js; do node "$f"; done
python3 tests/test_docs_backend.py -v
```

Runtime smoke marker:

```text
easiio_docs_phase20_smoke_ok
```

Compatibility note: `phaseHistory` still includes prior milestones such as `19-restore-planning`, `18-release-archive`, and earlier deployment workflow phases.



## Phase 21 — Connector profiles and dry-run history

Current health marker: `22-connector-runbooks`.

Phase 21 adds owner-protected connector configuration profiles and persisted connector dry-run history for Sitelet, WordPress, and static-hosting preflight workflows.

New endpoints:

```text
GET  /api/docs/deploy/connector/profiles
POST /api/docs/deploy/connector/profile
GET  /api/docs/deploy/connector/dry-runs
```

Profile saves require `confirmSaveConnectorProfile:true`. Connector profiles store secret placeholders only: `redactedConfig` values replace tokens, passwords, authorization headers, API keys, access keys, private keys, and credentials with `[REDACTED]` before persistence. Dry-run history stores redacted metadata only.

Admin UI adds Connector profiles controls for saving/listing profiles and loading dry-run history. Phase 21 remains local-only and never deploys, publishes, uploads, rolls back, changes DNS, or calls external connector APIs.

Dedicated docs: `EASIIO_DOCS_MODULE_PHASE21.md`.
Static test: `tests/deployment_connector_profiles_static.test.js`.
Smoke marker: `easiio_docs_phase21_smoke_ok`.

Compatibility note: `phaseHistory` includes `20-connector-dry-run`; current marker is `22-connector-runbooks`.


Compatibility note: Phase 21 health marker was `21-connector-profiles`; Phase 22 current marker is `22-connector-runbooks`.


## Phase 22 connector runbooks and dry-run comparison

Current health marker:

```text
22-connector-runbooks
```

Owner-protected endpoints:

```text
GET /api/docs/deploy/connector/runbook?id=<dry_run_id>
GET /api/docs/deploy/connector/dry-run-compare?left_id=<dry_run_id>&right_id=<dry_run_id>
```

Phase 22 produces local-only operator review artifacts from existing connector dry-run history. Runbooks include `runbookMarkdown` and state that no external connector calls are made. Dry-run comparison returns score deltas, status changes, connector/profile changes, and check diffs.

Safety remains unchanged: no deploy, publish, upload, DNS, rollback, restore, WordPress, Sitelet, hosting, or external API call is performed.

Dedicated doc:

```text
EASIIO_DOCS_MODULE_PHASE22.md
```

Validation includes:

```bash
node tests/deployment_connector_runbooks_static.test.js
python3 tests/test_docs_backend.py -v -k phase22
```


Phase 23 adds final operator release playbooks. Health reports may now report a later phase, and Phase 23 is preserved as `23-operator-playbooks` in `phaseHistory`; it includes Phase 22 in `phaseHistory`. New owner-protected endpoints: `GET /api/docs/deploy/operator-playbooks` and `GET /api/docs/deploy/operator-playbook?id=<audit_id>&target=<target>`. Operator playbooks support `sitelet`, `wordpress`, `static-hosting`, `nextjs-mdx`, `docusaurus`, `mkdocs`, `hugo`, and `vitepress`; `static-html` maps to `static-hosting`. Responses include `playbookMarkdown`, readiness, package metadata, `localOnly:true`, `externalCallsBlocked:true`, and `secretPlaceholdersOnly:true`. Admin UI adds Final operator release playbooks controls for catalog loading and target-specific playbook generation. New static test: `tests/deployment_operator_playbooks_static.test.js`; dedicated docs: `EASIIO_DOCS_MODULE_PHASE23.md`; smoke marker: `easiio_docs_phase23_smoke_ok`. Phase 23 remains local-only and does not deploy/publish/upload or call external services.


## Phase 24 — Packaging and onboarding

Current health marker:

```text
24-onboarding-guide
```

Phase 24 adds owner-protected, local-only onboarding guide/checklist APIs and admin controls for installing and operating the Easiio Docs Module as a reusable website component. It covers clean install paths, environment variables, start/stop commands, backup/restore, Sitelet integration, WordPress plugin usage, admin workflow, and a reusable v1 onboarding checklist.

Endpoints:

```text
GET /api/docs/deploy/onboarding-guide?site_id=<site_id>&integration=<target>
GET /api/docs/deploy/onboarding-checklist?site_id=<site_id>&integration=<target>
```

Dedicated docs:

```text
EASIIO_DOCS_MODULE_PHASE24.md
```

Static wiring test:

```text
tests/deployment_onboarding_static.test.js
```

Safety: Phase 24 is local-only and review-first. It does not deploy, upload, publish, call external services, change DNS, or execute rollback/restore. Secret values are documented as placeholders only, such as `EASIIO_DOCS_OWNER_TOKEN=[REDACTED]`.


## Phase 25 — Final QA and v1 release

Current health marker:

```text
25-v1-release
```

Phase 25 finalizes the reusable Easiio Docs Module v1 MVP/handoff with final QA, release freeze metadata, a security checklist, and a confirmation-gated local v1 release package.

Endpoints:

```text
GET  /api/docs/deploy/v1-release-summary
POST /api/docs/deploy/v1-release-package
```

The package endpoint requires `confirmV1ReleasePackage:true` and writes local ZIP packages under:

```text
dist/easiio-docs-v1-release/
```

Dedicated docs:

```text
EASIIO_DOCS_MODULE_PHASE25.md
```

Static wiring test:

```text
tests/deployment_v1_release_static.test.js
```

Safety: Phase 25 is local-only and review-first. It does not deploy, upload, publish, call external services, change DNS, execute rollback/restore, or call connector APIs. Secrets must stay outside packages and be represented only as placeholders such as `[REDACTED]`.

Smoke markers:

```text
easiio_docs_phase25_smoke_ok
phase25_smoke_cleanup_ok
```

After Phase 25, the Easiio Docs Module v1 MVP/handoff is complete; future work should be maintenance or explicitly approved external integration work.
