---
name: website-wiki-module
description: Build and maintain Jian's reusable Easiio website wiki/knowledge-base module that can be embedded into any created website, with per-site content, WordPress shortcode integration, and chatbot RAG sync.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, wiki, knowledge-base, rag, wordpress, static-website]
    related_skills: [website-chatbot-solo-crm, static-website-local-preview, sitelet-cloud-render]
---

# Website Wiki Module

Use this skill when the user asks to build, extend, integrate, debug, or package the reusable wiki/knowledge-base module for websites created by Hermes.

## Related Easiio Docs Module

A newer reusable documentation backend/content core lives at:

```text
/home/jianl/.hermes/tools/easiio_docs_module
```

Phase 1/2 files:

```text
Phase 1/2/3/4/5/6 files:

```text
/home/jianl/.hermes/tools/easiio_docs_module/backend/app.py
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_db.py
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_sitelet.py
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_wordpress.py
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_rag.py
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_exporters.py
/home/jianl/.hermes/tools/easiio_docs_module/frontend/docs.js
/home/jianl/.hermes/tools/easiio_docs_module/frontend/docs.css
/home/jianl/.hermes/tools/easiio_docs_module/frontend/demo.html
/home/jianl/.hermes/tools/easiio_docs_module/frontend/admin.html
/home/jianl/.hermes/tools/easiio_docs_module/frontend/admin.js
/home/jianl/.hermes/tools/easiio_docs_module/frontend/admin.css
/home/jianl/.hermes/tools/easiio_docs_module/wordpress-plugin/easiio-docs/easiio-docs.php
/home/jianl/.hermes/tools/easiio_docs_module/dist/easiio-docs-wordpress-plugin.zip
/home/jianl/.hermes/tools/easiio_docs_module/tests/test_docs_backend.py
/home/jianl/.hermes/tools/easiio_docs_module/tests/docs_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/sitelet_preview_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/wp_plugin_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/rag_sync_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/exporters_static.test.js
/home/jianl/.hermes/tools/easiio_docs_module/tests/admin_export_ui_static.test.js
```

Phase 3 adds Sitelet preview payload generation:

```text
GET /api/docs/sitelet-preview?site_id=<site>&target=sitelet
GET /api/docs/sitelet-preview?site_id=<site>&slug=<doc-slug>
POST /api/docs/sitelet-preview/upload
```

Preview generation returns a Sitelet `/api/generated` compatible `siteletPayload` with `source:"easiio-docs-module"`, `kind:"site"`, multi-page `pages`, and `/assets/easiio-docs-preview.css`. Upload is confirmation-gated with `confirmSiteletUpload:true` and needs `SITELET_BASE_URL` plus `SITELET_API_TOKEN`; do not print tokens.

Verification:

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py
node --check frontend/docs.js
node tests/docs_static.test.js
node tests/sitelet_preview_static.test.js
python3 tests/test_docs_backend.py -v
```
```

Phase 6 adds framework export preview and confirmation-gated ZIP packaging:

```text
GET /api/docs/export/preview?site_id=<site>&target=<nextjs-mdx|docusaurus|mkdocs|hugo|vitepress|static-html>
POST /api/docs/export/package
```

The Phase 6 exporter lives in `backend/docs_exporters.py`, writes approved local ZIP packages under `dist/easiio-docs-exports/`, and defaults to `status=published`, `visibility=public`, and `framework_targets` containing the selected target. Package writing is blocked unless `confirmExportPackage:true` is supplied. Verification includes `node tests/exporters_static.test.js` and `python3 tests/test_docs_backend.py -v`; smoke marker: `easiio_docs_phase6_smoke_ok`.

Phase 7 adds an admin/export UI:

```text
GET /docs/admin.html
GET /docs/admin.js
GET /docs/admin.css
```

The UI lets an operator enter `site_id`, choose an export target, preview generated files through `/api/docs/export/preview`, and create approved ZIP packages through `/api/docs/export/package` only after browser confirmation sends `confirmExportPackage:true`. Verification includes `node --check frontend/admin.js`, `node tests/admin_export_ui_static.test.js`, and `python3 tests/test_docs_backend.py -v`; smoke marker: `easiio_docs_phase7_smoke_ok`.

Phase 8 adds owner-token auth hardening for the Easiio Docs Module:

```text
EASIIO_DOCS_OWNER_TOKEN=[REDACTED]
```

When configured, protected requests use `Authorization: Bearer [REDACTED]` or `X-Easiio-Owner-Token: [REDACTED]` (query `owner_token` exists only for local/manual debugging). Protected routes include `/docs/admin.html`, `/docs/admin.js`, `/docs/admin.css`, write/action endpoints (`POST /api/docs/doc`, delete, Sitelet upload, WordPress draft execution, RAG sync, export package), revisions/space, and non-public/draft reads. Public published doc reads and default public previews remain public for website embeds. Verification includes `node --check frontend/admin.js`, `node tests/admin_export_ui_static.test.js`, and `python3 tests/test_docs_backend.py -v`; smoke marker: `easiio_docs_phase8_smoke_ok`.

Phase 9 expands `/docs/admin.html` into an in-browser docs editor/admin content-management UI. It supports loading docs by `site_id`, creating/editing docs, saving revisions, deleting docs, viewing revision history, editing status/visibility/category/tags/version/locale/framework targets/RAG eligibility, and keeping Phase 7 export preview/package controls in the same UI. Health reports `phase:"9-admin-editor"`. Verification includes `node tests/admin_editor_ui_static.test.js` plus the usual admin/backend tests; smoke marker: `easiio_docs_phase9_smoke_ok`.

Phase 10 adds import/export management. New file: `/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_importers.py`. New endpoints: `POST /api/docs/import/preview`, `POST /api/docs/import/execute`, `GET /api/docs/bundle/preview`, `POST /api/docs/bundle/package`. Imports support `markdown-folder`, `docusaurus`, `mkdocs`, `vitepress`, `hugo`, and `easiio-bundle`, detect slug conflicts, default to draft/private, and execution requires `confirmImport:true`. Portable bundle packaging writes ZIPs under `dist/easiio-docs-bundles/` and requires `confirmBundlePackage:true`. Admin UI adds import controls and portable bundle controls. Health reports `phase:"10-import-export-management"`. Verification includes `node tests/import_export_static.test.js` and `python3 tests/test_docs_backend.py -v`; smoke marker: `easiio_docs_phase10_smoke_ok`.

Phase 11 adds localization/multilingual docs. Health reports `phase:"11-localization"`. Locale behavior includes `GET /api/docs/docs?...&locale=<locale>`, `GET /api/docs/doc?...&locale=<locale>&fallback_locale=<locale>` with `fallbackUsed`, summary locale counts in `counts.locales`, locale-aware export preview/package paths and manifests, import locale detection from path/frontmatter/file metadata, locale-aware portable bundle preview/package metadata, and admin UI Locale filter/Fallback locale controls. New static test: `tests/localization_static.test.js`. Verification includes `node tests/localization_static.test.js` and `python3 tests/test_docs_backend.py -v`; smoke marker: `easiio_docs_phase11_smoke_ok`.

Phase 12 adds deployment handoff / publish preparation. Health reports `phase:"12-deployment-handoff"`. New file: `/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_deploy.py`. New endpoints: `GET /api/docs/deploy/preview` and `POST /api/docs/deploy/package`. Deployment handoff packages include generated docs files plus `easiio-docs-deployment-manifest.json`, support targets `static-html`, `sitelet`, `wordpress`, `nextjs-mdx`, `docusaurus`, `mkdocs`, `hugo`, `vitepress`, and environments `local`, `preview`, `staging`, `production`. Package writing is confirmation-gated with `confirmDeploymentPackage:true`, owner-protected when auth is configured, and handoff-only: it does not publish, upload, change DNS, or deploy externally. ZIPs write under `dist/easiio-docs-deployments/`. Admin UI adds Deployment handoff controls. New static test: `tests/deployment_static.test.js`. Verification includes `backend/docs_deploy.py`, `node tests/deployment_static.test.js`, and `python3 tests/test_docs_backend.py -v`; smoke marker: `easiio_docs_phase12_smoke_ok`.

Phase 13 adds deployment history / audit log. Health reports `phase:"13-deployment-history"`. New file: `/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_audit.py`. New endpoint: owner-protected `GET /api/docs/deploy/history`. Confirmed deployment handoff packages now record a local SQLite `docs_deployment_audit` row with site ID, target, export target, environment, locale, status/visibility scope, package path/size, approved-by label, document/file counts, file paths, manifest JSON, and timestamp. The audit log is metadata-only and must never store raw owner tokens, auth headers, passwords, API keys, or secrets. Admin UI adds Deployment history controls plus `loadDeploymentHistory()`/`renderDeploymentHistory()`. New static test: `tests/deployment_history_static.test.js`; dedicated docs: `EASIIO_DOCS_MODULE_PHASE13.md`. Verification includes `backend/docs_audit.py`, `node tests/deployment_history_static.test.js`, and `python3 tests/test_docs_backend.py -v`; smoke marker: `easiio_docs_phase13_smoke_ok`.

Phase 14 adds deployment audit operations. Health reports `phase:"14-audit-operations"`. New owner-protected endpoints: `GET /api/docs/deploy/summary` and `GET /api/docs/deploy/history.csv`. Deployment history supports `target`, `environment`, `locale`, and `limit` filters. `backend/docs_audit.py` includes `filter_deployment_history`, `summarize_deployment_history`, `deployment_history_to_csv`, `build_deployment_summary_response`, and `build_deployment_history_csv_response`. Admin UI adds history target/environment/locale filters, Load audit summary, and Export history CSV. New static test: `tests/deployment_ops_static.test.js`; dedicated docs: `EASIIO_DOCS_MODULE_PHASE14.md`. Verification includes `node tests/deployment_ops_static.test.js` and `python3 tests/test_docs_backend.py -v`; smoke marker: `easiio_docs_phase14_smoke_ok`.

Phase 15 adds deployment package operations. Health reports `phase:"15-package-operations"`. New owner-protected endpoints: `GET /api/docs/deploy/package?id=<audit_id>`, `GET /api/docs/deploy/package/download?id=<audit_id>`, `GET /api/docs/deploy/compare?left_id=<audit_id>&right_id=<audit_id>`, and `POST /api/docs/deploy/checklist`. `backend/docs_audit.py` persists `checklist_json`, exposes package detail/download/compare/checklist helpers, and uses default checklist keys `manual_review`, `static_files_verified`, `sitelet_upload`, `wordpress_upload`, and `production_publish`. Admin UI adds Deployment package operations controls for package ID, compare IDs, checklist JSON, load detail, download ZIP, compare packages, and update checklist. Operations are local-only and do not publish/deploy externally. New static test: `tests/deployment_package_ops_static.test.js`; dedicated docs: `EASIIO_DOCS_MODULE_PHASE15.md`. Verification includes `node tests/deployment_package_ops_static.test.js` and `python3 tests/test_docs_backend.py -v`; smoke marker: `easiio_docs_phase15_smoke_ok`.

Phase 16 adds deployment approval workflow and release notes. Health reports `phase:"16-approval-workflow"`. New owner-protected endpoints: `POST /api/docs/deploy/approval`, `GET /api/docs/deploy/approvals?id=<audit_id>`, and `GET /api/docs/deploy/release-notes?id=<audit_id>`. `backend/docs_audit.py` persists `approval_status`, `approval_history_json`, `release_notes_json`, `package_locked`, `approval_updated_by`, and `approval_updated_at`; approved/released packages are locked from checklist mutation. Supported approval states: `draft`, `reviewed`, `approved`, `released`, `rejected`. Admin UI adds Deployment approval workflow controls for status, actor, note, update approval, load release notes, and load approval history. Approval remains local metadata only and does not deploy/publish externally. New static test: `tests/deployment_approval_static.test.js`; dedicated docs: `EASIIO_DOCS_MODULE_PHASE16.md`. Verification includes `node tests/deployment_approval_static.test.js` and `python3 tests/test_docs_backend.py -v`; smoke marker: `easiio_docs_phase16_smoke_ok`.

Phase 17 adds release dashboard and operator handoff reports. Health history includes `phase:"17-release-dashboard"`; current health may report a later phase. New owner-protected endpoints: `GET /api/docs/deploy/releases?site_id=<site>&target=<target>&environment=<env>&locale=<locale>&approval_status=<status>&limit=25` and `GET /api/docs/deploy/handoff-report?id=<audit_id>`. `backend/docs_audit.py` adds `calculate_deployment_readiness`, `build_deployment_release_dashboard_response`, and `build_deployment_operator_handoff_report_response`. Readiness is local metadata only: checklist completion up to 60 points, approved/released state up to 30 points, and local ZIP existence up to 10 points; `readyForOperatorHandoff` requires approval/release, an existing package ZIP, and completed checklist items. Admin UI adds Release dashboard controls for approval status filtering, loading the dashboard, and loading operator handoff Markdown. New static test: `tests/deployment_release_dashboard_static.test.js`; dedicated docs: `EASIIO_DOCS_MODULE_PHASE17.md`. Verification includes `node tests/deployment_release_dashboard_static.test.js` and `python3 tests/test_docs_backend.py -v`; smoke marker: `easiio_docs_phase17_smoke_ok`.

Phase 18 adds release archive and attestation workflow. Health history includes `phase:"18-release-archive"`; current health may report a later phase. New owner-protected endpoints: `POST /api/docs/deploy/archive`, `GET /api/docs/deploy/archive`, `GET /api/docs/deploy/attestation?id=<audit_id>`, and `GET /api/docs/deploy/report/download?id=<audit_id>`. Archive creation requires `confirmArchiveRelease:true`, only proceeds for Phase 17-ready packages, writes local artifacts under `dist/easiio-docs-release-archive/<site>/package-<audit_id>/`, and stores metadata in SQLite table `docs_release_archive`. Attestation JSON includes SHA-256 hashes for the package ZIP, manifest, operator handoff report, release notes, and individual ZIP files. Admin UI adds Release archive controls for creating archives, loading archive index, loading attestation JSON, and downloading archived operator handoff Markdown. New static test: `tests/deployment_archive_static.test.js`; dedicated docs: `EASIIO_DOCS_MODULE_PHASE18.md`. Verification includes `node tests/deployment_archive_static.test.js`, full `tests/*.test.js`, and `python3 tests/test_docs_backend.py -v`; smoke marker: `easiio_docs_phase18_smoke_ok`. Phase 18 remains local-only and does not deploy/publish/upload externally.

Phase 19 adds release restore / rollback planning. Health history includes `phase:"19-restore-planning"`; current health may report a later phase. New owner-protected endpoints: `GET /api/docs/deploy/archive/integrity?id=<audit_id>`, `GET /api/docs/deploy/rollback-plan?id=<current_audit_id>&previous_id=<rollback_target_audit_id>`, and `POST /api/docs/deploy/restore-package`. Restore package creation requires `confirmPrepareRestore:true`, verifies Phase 18 archive/package hashes before preparation, writes local restore ZIPs under `dist/easiio-docs-restore-packages/<site>/`, and includes rollback-plan Markdown, current/target attestations, integrity JSON, and the rollback target package when available. `backend/docs_deploy.py` now uses timestamped deployment handoff ZIP filenames so multiple archived releases do not overwrite each other. Admin UI adds Release restore / rollback controls for archive integrity, rollback plan, and restore package preparation. New static test: `tests/deployment_restore_static.test.js`; dedicated docs: `EASIIO_DOCS_MODULE_PHASE19.md`. Verification includes `node tests/deployment_restore_static.test.js`, full `tests/*.test.js`, and `python3 tests/test_docs_backend.py -v`; smoke marker: `easiio_docs_phase19_smoke_ok`. Phase 19 remains local-only and does not deploy/publish/upload externally.

Phase 20 adds deployment connector dry-run adapters. Health history includes `phase:"20-connector-dry-run"`; current health may report a later phase. New file: `/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_connectors.py`. New owner-protected endpoints: `GET /api/docs/deploy/connectors` and `POST /api/docs/deploy/connector/preflight`. Supported dry-run connectors are `sitelet`, `wordpress`, and `static-hosting`. Preflight requires `confirmConnectorDryRun:true`, checks only local package/audit/readiness/config metadata, redacts connector secrets into `redactedConfig`, and returns `dryRunOnly:true`, `localOnly:true`, and `externalCallsBlocked:true`. It does not call Sitelet, WordPress, hosting, DNS, FTP, or any external API. Admin UI adds Deployment connector dry-run controls for connector type, connector config JSON, catalog loading, and preflight execution. New static test: `tests/deployment_connectors_static.test.js`; dedicated docs: `EASIIO_DOCS_MODULE_PHASE20.md`. Verification includes `node tests/deployment_connectors_static.test.js`, full `tests/*.test.js`, and `python3 tests/test_docs_backend.py -v`; smoke marker: `easiio_docs_phase20_smoke_ok`. Phase 20 remains local-only and does not deploy/publish/upload externally.

Phase 21 adds connector profiles and dry-run history. Health history includes `phase:"21-connector-profiles"`; current health may report a later phase. `backend/docs_connectors.py` creates local SQLite tables `docs_connector_profiles` and `docs_connector_dry_runs`. Owner-protected endpoints: `GET /api/docs/deploy/connector/profiles`, `POST /api/docs/deploy/connector/profile`, and `GET /api/docs/deploy/connector/dry-runs`. Profile save requires `confirmSaveConnectorProfile:true` and stores secret placeholders only: raw tokens/passwords/authorization headers/API keys/access keys/private keys/credentials are replaced in `redactedConfig` before persistence. Connector preflight accepts `profileId`/`profile_id`, resolves the saved redacted profile config, and records a redacted dry-run history row. Admin UI adds connector profile name/ID controls, Save connector profile, Load connector profiles, and Load dry-run history actions. Static test: `tests/deployment_connector_profiles_static.test.js`; dedicated docs: `EASIIO_DOCS_MODULE_PHASE21.md`; smoke marker: `easiio_docs_phase21_smoke_ok`. Phase 21 remains local-only and does not deploy/publish/upload or call external connector APIs.

Phase 22 adds connector runbooks and dry-run comparison. Health history includes `phase:"22-connector-runbooks"`; current health may report a later phase. New owner-protected endpoints: `GET /api/docs/deploy/connector/runbook?id=<dry_run_id>` and `GET /api/docs/deploy/connector/dry-run-compare?left_id=<dry_run_id>&right_id=<dry_run_id>`. `build_connector_runbook_response` returns `runbookMarkdown` with operator handoff steps and the explicit safety line “No external connector calls are made”; `build_connector_dry_run_comparison_response` returns score deltas, status/connector/profile changes, and check diffs. Admin UI adds runbook dry-run ID, compare left/right dry-run IDs, Load connector runbook, and Compare connector dry-runs controls. New static test: `tests/deployment_connector_runbooks_static.test.js`; dedicated docs: `EASIIO_DOCS_MODULE_PHASE22.md`. Verification includes `node tests/deployment_connector_runbooks_static.test.js`, full `tests/*.test.js`, and `python3 tests/test_docs_backend.py -v`; smoke marker: `easiio_docs_phase22_smoke_ok`. Phase 22 remains local-only and does not deploy/publish/upload or call external connector APIs.

Phase 23 adds final operator release playbooks. Current health may report a later phase; Phase 23 is preserved as `23-operator-playbooks` in `phaseHistory` and includes Phase 22 in `phaseHistory`. New owner-protected endpoints: `GET /api/docs/deploy/operator-playbooks` and `GET /api/docs/deploy/operator-playbook?id=<audit_id>&target=<target>`. `backend/docs_connectors.py` defines `OPERATOR_PLAYBOOK_TARGETS` for `sitelet`, `wordpress`, `static-hosting`, `nextjs-mdx`, `docusaurus`, `mkdocs`, `hugo`, and `vitepress`; `static-html` maps to `static-hosting`. `build_operator_playbook_catalog_response` returns target templates; `build_operator_release_playbook_response` returns `easiio-docs-operator-release-playbook`, `playbookMarkdown`, readiness/package metadata, `localOnly:true`, `externalCallsBlocked:true`, and the safety line “No external deployment is executed by this module.” Admin UI adds Final operator release playbooks controls and functions `loadOperatorPlaybookCatalog`/`loadOperatorReleasePlaybook`. New static test: `tests/deployment_operator_playbooks_static.test.js`; dedicated docs: `EASIIO_DOCS_MODULE_PHASE23.md`; smoke marker: `easiio_docs_phase23_smoke_ok`. Phase 23 remains local-only and does not deploy/publish/upload or call external services.

Phase 24 adds packaging and onboarding guides. Current health may report a later phase; Phase 24 is preserved as `24-onboarding-guide` in `phaseHistory`. New owner-protected endpoints: `GET /api/docs/deploy/onboarding-guide?site_id=<site_id>&integration=<target>` and `GET /api/docs/deploy/onboarding-checklist?site_id=<site_id>&integration=<target>`. Supported integrations include `sitelet`, `wordpress`, `static-html`, `nextjs-mdx`, `docusaurus`, `mkdocs`, `hugo`, and `vitepress`. `backend/docs_connectors.py` defines `ONBOARDING_INTEGRATIONS`, `build_onboarding_guide_response`, and `build_onboarding_checklist_response`; guide responses include `installMarkdown` with install paths, environment variable reference, start/stop commands, backup/restore, integration-specific instructions, admin workflow, and a reusable v1 onboarding checklist. Responses are local-only with `localOnly:true`, `externalCallsBlocked:true`, `secretPlaceholdersOnly:true`, and placeholders such as `EASIIO_DOCS_OWNER_TOKEN=[REDACTED]`. Admin UI adds Packaging and onboarding controls plus `loadOnboardingGuide`/`loadOnboardingChecklist`. New static test: `tests/deployment_onboarding_static.test.js`; dedicated docs: `EASIIO_DOCS_MODULE_PHASE24.md`; smoke markers: `easiio_docs_phase24_smoke_ok` and `phase24_smoke_cleanup_ok`. Phase 24 remains local-only and does not deploy/publish/upload or call external services.

Phase 25 adds final QA, release freeze metadata, and local v1 release packaging. Current health reports `phase:"25-v1-release"` and preserves Phase 24 in `phaseHistory`. New owner-protected endpoints: `GET /api/docs/deploy/v1-release-summary` and `POST /api/docs/deploy/v1-release-package`; package creation requires `confirmV1ReleasePackage:true`. `backend/docs_connectors.py` defines `build_v1_release_summary_response` and `build_v1_release_package_response`; packages are local ZIPs under `dist/easiio-docs-v1-release/` and include a generated `easiio-docs-v1-release-manifest.json` plus `EASIIO_DOCS_MODULE_V1_RELEASE_SUMMARY.md`. Admin UI adds Final QA and v1 release controls plus `loadV1ReleaseSummary`/`createV1ReleasePackage`. New static test: `tests/deployment_v1_release_static.test.js`; dedicated docs: `EASIIO_DOCS_MODULE_PHASE25.md`; smoke markers: `easiio_docs_phase25_smoke_ok` and `phase25_smoke_cleanup_ok`. Phase 25 remains local-only and review-first: it does not deploy, publish, upload, call external services, change DNS, execute rollback/restore, or call connector APIs. After Phase 25, the Easiio Docs Module v1 MVP/handoff is complete; future phases should be maintenance or explicitly approved external integrations.

Phase 1 API prefix is `/api/docs/*`, not `/api/wiki/*`.

## Sitelet console docs integration

Sitelet can embed the Easiio Docs Module in the canonical Sitelet console checkout:

```text
/home/jianl/github-work/hermes_proxy/sitelet-engine
```

Integration files/pattern:

```text
app/docs/page.tsx
app/components/SiteletDocsEmbed.tsx
app/api/docs/[...path]/route.ts
public/docs/docs.js
public/docs/docs.css
docs/sitelet-docs-module-integration.md
tests/sitelet_docs_module_integration_static_test.js
```

Use `site_id="sitelet-console"` for Sitelet help content. Seed/refresh the docs module content with:

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 scripts/seed_sitelet_console_docs.py
```

The Sitelet page should use same-origin `data-api-base="."`; the Next.js proxy reads `EASIIO_DOCS_API_BASE` server-side and may attach `EASIIO_DOCS_OWNER_TOKEN` server-side only. Never expose docs or Sitelet owner tokens in browser JS. Validation: `cd /home/jianl/github-work/hermes_proxy/sitelet-engine && npm run test:docs-module && npm run test:backend-ui && npm run test:phase12 && npm run build`; smoke marker: `sitelet_docs_module_integration_smoke_ok`.

When committing this integration, run git from the repo root `/home/jianl/github-work/hermes_proxy` because `sitelet-engine` is nested in the monorepo. Stage only Sitelet repo files; the docs seed script and default SQLite DB live under `/home/jianl/.hermes/tools/easiio_docs_module` and are not part of the GitHub repo unless separately requested. Before push, run `npm run test:docs-module`, compile the seed script, scan changed files for high-confidence secrets, then `git push origin main` and verify `git ls-remote origin refs/heads/main` matches `git rev-parse HEAD`.

## Project paths

Main wiki project:

```text
/home/jianl/.hermes/tools/website_wiki_module
```

Important files:

```text
/home/jianl/.hermes/tools/website_wiki_module/backend/app.py
/home/jianl/.hermes/tools/website_wiki_module/backend/wiki_db.py
/home/jianl/.hermes/tools/website_wiki_module/frontend/wiki.js
/home/jianl/.hermes/tools/website_wiki_module/frontend/wiki.css
/home/jianl/.hermes/tools/website_wiki_module/frontend/demo.html
/home/jianl/.hermes/tools/website_wiki_module/wordpress-plugin/easiio-wiki/easiio-wiki.php
/home/jianl/.hermes/tools/website_wiki_module/wordpress-plugin/easiio-wiki/README.md
/home/jianl/.hermes/tools/website_wiki_module/dist/easiio-wiki-wordpress-plugin.zip
/home/jianl/.hermes/tools/website_wiki_module/tests/test_wiki_backend.py
/home/jianl/.hermes/tools/website_wiki_module/tests/wiki_static.test.js
/home/jianl/.hermes/tools/website_wiki_module/tests/wp_plugin_static.test.js
/home/jianl/.hermes/tools/website_wiki_module/WEBSITE_WIKI_MODULE_PLAN.md
/home/jianl/.hermes/tools/website_wiki_module/README.md
```

## Architecture

The module is intentionally lightweight and reusable across static sites, Sitelet previews, WordPress, and future app sites:

```text
Website page
  -> embeddable wiki.js/wiki.css
  -> wiki backend HTTP API
  -> SQLite website_wiki.db
  -> optional sync to website_chatbot RAG store by site_id
```

The backend is dependency-free Python stdlib and defaults to port `8105`.

Default wiki DB:

```text
/home/jianl/.hermes/tools/website_wiki_module/data/website_wiki.db
```

Override with:

```bash
EASIIO_WIKI_DB=/path/to/website_wiki.db
```

The wiki can sync published `rag_enabled` pages into the chatbot RAG store used by `website-chatbot-solo-crm`:

```text
/home/jianl/.hermes/tools/website_chatbot/data/rag_content.json
```

Override the RAG store with:

```bash
EASIIO_CHATBOT_RAG_STORE=/path/to/rag_content.json
```

Per-site wiki backend access can be protected for login-only websites. Configure one or both environment variables before starting the backend:

```bash
# Basic auth users. Roles: viewer, editor, admin.
EASIIO_WIKI_SITE_CREDENTIALS='{"factory-site":{"alice":{"password":"[REDACTED]","role":"viewer"},"editor":{"password":"[REDACTED]","role":"editor"}}}'

# Bearer tokens issued/rendered by the website login backend.
EASIIO_WIKI_SITE_TOKENS='{"factory-site":{"[REDACTED]":{"username":"wp-user","role":"viewer"}}}'
```

When a `site_id` appears in either variable, all wiki API calls for that site require `Authorization`. `viewer` can read; `editor` or `admin` is required for create/update/delete.

## Data model behavior

SQLite tables:

- `wiki_spaces`: one logical wiki space per `site_id`.
- `wiki_pages`: page data, status, tags, category, and `rag_enabled` flag.
- `wiki_page_revisions`: a revision row is created on every upsert.

Pages are isolated by `(site_id, slug)`. A slug that exists for one website must not leak into another website.

## Backend API

Run backend:

```bash
python3 /home/jianl/.hermes/tools/website_wiki_module/backend/app.py --host 127.0.0.1 --port 8105
```

Health:

```bash
curl http://127.0.0.1:8105/health
```

Create/update a page:

```bash
curl -s http://127.0.0.1:8105/api/wiki/page \
  -H 'Content-Type: application/json' \
  -d '{
    "site_id":"factory-site",
    "slug":"cnc-machining",
    "title":"CNC Machining Capabilities",
    "summary":"Materials, tolerance, and inspection details.",
    "content":"# CNC Machining\nWe support aluminum, copper, and mold components.",
    "status":"published",
    "tags":["cnc","manufacturing"],
    "rag_enabled":true,
    "sync_to_rag":true
  }'
```

List/search pages:

```bash
curl -s 'http://127.0.0.1:8105/api/wiki/pages?site_id=factory-site&q=cnc&status=published'
```

Get one page:

```bash
curl -s 'http://127.0.0.1:8105/api/wiki/page?site_id=factory-site&slug=cnc-machining'
```

Delete one page:

```bash
curl -s http://127.0.0.1:8105/api/wiki/page/delete \
  -H 'Content-Type: application/json' \
  -d '{"site_id":"factory-site","slug":"cnc-machining"}'
```

List revisions:

```bash
curl -s 'http://127.0.0.1:8105/api/wiki/revisions?site_id=factory-site&slug=cnc-machining'
```

## Embedding in a website

### AI Solo Company website integration pattern

For the AI Solo Company class site, integrate the wiki through the existing website login gateway instead of exposing the wiki backend directly:

```text
Site directory: /mnt/c/Users/jianl/solo-company-class-site
Gateway: /home/jianl/.hermes/tools/website_chatbot/backend/site_gateway.py
Wiki backend: http://127.0.0.1:8105
Site ID: ai-solo-company-class
Public proxy URL: https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-ai-solo/
```

Implementation checklist:

1. Copy reusable assets into the site so the page works under the site-specific Hermes Proxy path:

```bash
mkdir -p /mnt/c/Users/jianl/solo-company-class-site/wiki
cp /home/jianl/.hermes/tools/website_wiki_module/frontend/wiki.js /mnt/c/Users/jianl/solo-company-class-site/wiki/wiki.js
cp /home/jianl/.hermes/tools/website_wiki_module/frontend/wiki.css /mnt/c/Users/jianl/solo-company-class-site/wiki/wiki.css
```

2. Add a user wiki page (`wiki.html`) with body/page protection and same-origin wiki API:

```html
<body data-auth-required="true" data-login-next="wiki.html">
<div id="ai-solo-wiki-root"></div>
<script
  async
  src="wiki/wiki.js"
  data-easiio-wiki
  data-api-base="."
  data-site-id="ai-solo-company-class"
  data-mode="public"
  data-root-selector="#ai-solo-wiki-root"
  data-login-required="true"
  data-credential-mode="same-origin">
</script>
```

3. Add an admin page (`wiki-admin.html`) using the same embed but with:

```html
<body data-admin-required="true" data-login-next="wiki-admin.html">
<script data-mode="admin" ...></script>
```

4. In `site-auth.js`, support generic protected pages in addition to admin-only pages. The useful functions are `getCurrentUser()`, `requireLogin(nextPage)`, `requireAdmin(nextPage)`, and `initProtectedPages()` reading `document.body.dataset.authRequired`, `dataset.adminRequired`, and `dataset.loginNext`.

5. In `site_gateway.py`, proxy wiki API calls through the same-origin website gateway:

```text
GET  /api/wiki/* -> require logged-in user -> proxy to http://127.0.0.1:8105
POST /api/wiki/* -> require admin user     -> proxy to http://127.0.0.1:8105
```

Add/verify a `--wiki-api-base` CLI option and start the gateway with:

```bash
source /home/jianl/.hermes/tools/website_chatbot/data/ai_solo_admin.env
python3 /home/jianl/.hermes/tools/website_chatbot/backend/site_gateway.py \
  --host 0.0.0.0 \
  --port 8020 \
  --site-dir /mnt/c/Users/jianl/solo-company-class-site \
  --api-base http://127.0.0.1:8099 \
  --wiki-api-base http://127.0.0.1:8105
```

Do not print values from `ai_solo_admin.env`; secrets must remain `[REDACTED]`.

6. Seed or update AI Solo pages directly in the default wiki DB using `WikiStore` under `site_id='ai-solo-company-class'`.

For one-off requests like “populate this guide into the Wiki Manager,” do not edit browser UI files unless the user asks for a new panel. Draft the Markdown content, then upsert it directly into the wiki DB and sync it to chatbot RAG:

```bash
python3 - <<'PY'
from pathlib import Path
import sys, json
sys.path.insert(0, '/home/jianl/.hermes/tools/website_wiki_module/backend')
from wiki_db import WikiStore
from app import sync_page_to_rag
store = WikiStore('/home/jianl/.hermes/tools/website_wiki_module/data/website_wiki.db')
content = Path('/tmp/page.md').read_text(encoding='utf-8')
page = store.upsert_page({
    'site_id': 'ai-solo-company-class',
    'slug': 'descriptive-lowercase-slug',
    'title': 'Readable Page Title',
    'summary': 'Short searchable summary for the Wiki Manager list.',
    'content': content,
    'content_format': 'markdown',
    'status': 'published',
    'category': 'User Guide',
    'tags': ['ai-solo', 'user-guide', 'wiki-manager'],
    'rag_enabled': True,
    'changed_by': 'Hermes Agent',
})
print(json.dumps({'slug': page['slug'], 'title': page['title'], 'rag_synced': sync_page_to_rag(page)}, ensure_ascii=False))
PY
```

Then verify by calling `handle_request()` for `/api/wiki/pages`, `/api/wiki/page`, and `/api/wiki/revisions`, and inspect the RAG store for `content_id: wiki:<slug>`. Also fetch the public/protected static shell through `https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-ai-solo/wiki.html` and `admin.html` to confirm the Wiki Manager host UI is reachable. This DB/RAG population is runtime content, not a Git change.

7. Verification sequence:

```bash
python3 -m py_compile /home/jianl/.hermes/tools/website_chatbot/backend/site_gateway.py
python3 /mnt/c/Users/jianl/solo-company-class-site/auth_download_static_test.py
python3 /mnt/c/Users/jianl/solo-company-class-site/portal_static_test.py
node --check /mnt/c/Users/jianl/solo-company-class-site/site-auth.js
node --check /mnt/c/Users/jianl/solo-company-class-site/wiki/wiki.js
```

Then verify HTTP behavior:

- `/wiki.html`, `/wiki-admin.html`, `/wiki/wiki.js`, `/wiki/wiki.css` return HTTP 200 locally and through `https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-ai-solo/`.
- anonymous `GET /api/wiki/pages?site_id=ai-solo-company-class` through the gateway returns 401/login_required.
- after `/auth/login`, logged-in requests can list seeded pages.
- admin session can POST a temporary wiki page and delete it.

Pitfalls from the AI Solo integration:

- The login endpoint is `/auth/login`, not `/api/login`.
- Use same-origin `data-api-base="."` for pages behind the website gateway.
- Keep static asset paths relative (`wiki/wiki.js`, `wiki/wiki.css`) for Hermes Proxy subpath compatibility.
- If port `8020` is occupied by an old gateway process, stop it before starting the updated gateway; old processes may not include wiki routing.
- The site-specific proxy URL is required: use `/p/VaYZmN7v5naw-ai-solo/`, not the unsuffixed `/p/VaYZmN7v5naw/`.

Public mode:

```html
<link rel="stylesheet" href="https://chat.easiio.com/wiki.css" />
<div id="easiio-wiki-root"></div>
<script
  async
  src="https://chat.easiio.com/wiki.js"
  data-easiio-wiki
  data-api-base="https://chat.easiio.com"
  data-site-id="factory-site"
  data-mode="public"
  data-root-selector="#easiio-wiki-root"
  data-title="Factory Knowledge Base">
</script>
```

Admin/editor mode, only on protected/admin-only pages:

```html
data-mode="admin"
```

Admin mode can create/edit/delete pages and set `rag_enabled`/`sync_to_rag`. Do not expose admin mode on normal public visitor pages.

Login-protected embed mode can forward website credentials to the backend:

```html
<script
  async
  src="https://chat.easiio.com/wiki.js"
  data-easiio-wiki
  data-api-base="https://chat.easiio.com"
  data-site-id="factory-site"
  data-mode="public"
  data-login-required="true"
  data-credential-mode="include"
  data-auth-token="USER_SESSION_WIKI_TOKEN">
</script>
```

Use `data-credential-mode="include"` when the wiki API is behind the same website login/session boundary. Use `data-auth-token` only from logged-in/protected server-rendered pages when using the built-in bearer-token check.

## WordPress integration

Package ZIP:

```text
/home/jianl/.hermes/tools/website_wiki_module/dist/easiio-wiki-wordpress-plugin.zip
```

Shortcode:

```text
[easiio_wiki site_id="easiio-main" mode="public"]
```

Protected admin/editor page only:

```text
[easiio_wiki site_id="easiio-main" mode="admin"]
```

Require WordPress login before rendering the wiki:

```text
[easiio_wiki site_id="easiio-main" mode="public" require_login="true" credential_mode="include"]
```

For the built-in wiki backend token check, render the shortcode only for logged-in users and pass a token configured in `EASIIO_WIKI_SITE_TOKENS`:

```text
[easiio_wiki site_id="easiio-main" require_login="true" auth_token="[REDACTED]"]
```

Optional custom backend/title:

```text
[easiio_wiki api_base="https://chat.easiio.com" site_id="factory-site" title="Factory Knowledge Base"]
```

The plugin only renders the embed. Wiki content remains in the central backend by `site_id`.

## TDD workflow used and expected

Use strict TDD for changes:

1. Write or update backend tests in `tests/test_wiki_backend.py`.
2. Run the target test and confirm it fails for the expected missing behavior.
3. Implement the minimal backend code.
4. Run backend tests.
5. Write/update static frontend/plugin tests.
6. Implement frontend/plugin changes.
7. Run full verification.

Initial MVP tests covered:

- DB upsert/list/search/get/delete by `site_id`.
- Site isolation for same slug across different sites.
- Revision created on every update.
- HTTP API validation and flow.
- Published `rag_enabled` page syncing to chatbot RAG by `site_id`.
- Protected-site auth: Basic Auth users, Bearer tokens, 401 unauthenticated, 403 invalid credential, and viewer vs editor write permissions.
- Static checks for widget config, APIs, admin mode, credential forwarding (`data-login-required`, `data-credential-mode`, `data-auth-token`), CSS selectors, demo embed.
- Static checks for WordPress header, direct-access guard, shortcode, escaping, login-required attributes, and ZIP package.

## Verification commands

```bash
python3 -m py_compile \
  /home/jianl/.hermes/tools/website_wiki_module/backend/app.py \
  /home/jianl/.hermes/tools/website_wiki_module/backend/wiki_db.py

python3 /home/jianl/.hermes/tools/website_wiki_module/tests/test_wiki_backend.py -v
node --check /home/jianl/.hermes/tools/website_wiki_module/frontend/wiki.js
node /home/jianl/.hermes/tools/website_wiki_module/tests/wiki_static.test.js
node /home/jianl/.hermes/tools/website_wiki_module/tests/wp_plugin_static.test.js
```

Verify the plugin ZIP contains the shortcode PHP:

```bash
python3 - <<'PY'
from pathlib import Path
import zipfile
p=Path('/home/jianl/.hermes/tools/website_wiki_module/dist/easiio-wiki-wordpress-plugin.zip')
with zipfile.ZipFile(p) as z:
    names=set(z.namelist())
    assert 'easiio-wiki/easiio-wiki.php' in names
    php=z.read('easiio-wiki/easiio-wiki.php').decode()
assert 'add_shortcode' in php and 'data-easiio-wiki' in php
print('PASS plugin zip includes shortcode PHP')
PY
```

Run a backend smoke test:

```bash
python3 /home/jianl/.hermes/tools/website_wiki_module/backend/app.py --host 127.0.0.1 --port 8105
curl -sS http://127.0.0.1:8105/health
curl -sS http://127.0.0.1:8105/api/wiki/page \
  -H 'Content-Type: application/json' \
  -d '{"site_id":"demo-site","slug":"getting-started","title":"Getting Started","content":"# Getting Started\nThis reusable wiki module can be embedded into any website and synced to chatbot RAG.","status":"published","tags":["wiki","rag"],"rag_enabled":true,"sync_to_rag":true}'
curl -sS 'http://127.0.0.1:8105/api/wiki/pages?site_id=demo-site&q=wiki&status=published'
```

Run a protected-backend smoke test when auth behavior changes:

```bash
TMPDIR=$(mktemp -d)
export EASIIO_WIKI_DB="$TMPDIR/wiki.db"
export EASIIO_CHATBOT_RAG_STORE="$TMPDIR/rag.json"
export EASIIO_WIKI_SITE_TOKENS='{"factory-site":{"[REDACTED]":{"username":"smoke-user","role":"editor"}}}'
python3 /home/jianl/.hermes/tools/website_wiki_module/backend/app.py --host 127.0.0.1 --port 8105
# In another shell: verify /health is 200, unauthenticated protected list is 401,
# bad token is 403, valid Bearer token can write/read for factory-site.
```

Stop demo servers after smoke tests.

## Packaging the WordPress plugin

If plugin source changes, rebuild the ZIP with Python instead of relying on `zip`, which may not be installed:

```bash
python3 - <<'PY'
from pathlib import Path
import zipfile
root=Path('/home/jianl/.hermes/tools/website_wiki_module/wordpress-plugin')
out=Path('/home/jianl/.hermes/tools/website_wiki_module/dist/easiio-wiki-wordpress-plugin.zip')
out.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in sorted((root/'easiio-wiki').rglob('*')):
        if path.is_file():
            z.write(path, path.relative_to(root))
print(out, out.stat().st_size)
PY
```

## Pitfalls

- Keep `data-mode="admin"` off public pages; it exposes editing UI.
- Do not expose SQLite paths, environment variables, or secrets in frontend JS.
- Use distinct stable `site_id` values for every website.
- A wiki page syncs to chatbot RAG only when `status="published"`, `rag_enabled=true`, and `sync_to_rag=true` are used on save.
- Static tests are intentionally string-based because this WSL environment may lack browser/PHP dependencies.
- Wiki frontend Markdown must render structure, not escaped plain text. For guide pages, verify headings, ordered/unordered lists, tables, blockquotes, code, and links render through `markdownToHtml`/`renderMarkdownTable`, and copy updated `frontend/wiki.js` and `frontend/wiki.css` into site-specific paths such as `/mnt/c/Users/jianl/solo-company-class-site/wiki/`.
- `zip` and `php` may be missing in WSL; use Python `zipfile` for packaging and static plugin tests when PHP CLI is unavailable.
- Always stop any local backend server started for smoke tests.
