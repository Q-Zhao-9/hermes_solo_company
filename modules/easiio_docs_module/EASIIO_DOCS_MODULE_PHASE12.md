# Easiio Docs Module — Phase 12 Deployment Handoff

Phase 12 adds a safe, review-first deployment handoff workflow for Easiio Docs Module exports.

## Summary

Phase 12 lets operators preview and package docs artifacts for downstream deployment workflows without automatically publishing anything externally.

The module can now:

- preview deployment handoff files for a docs space
- generate a deployment manifest with an operator checklist
- package reviewed artifacts into a local ZIP
- scope deployment artifacts by target, environment, locale, status, and visibility
- preserve default public safety behavior: `status=published`, `visibility=public`
- require explicit confirmation before any deployment handoff ZIP is written

## New backend file

```text
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_deploy.py
```

## Health marker

```json
{
  "phase": "12-deployment-handoff"
}
```

## New API endpoints

### Preview deployment handoff

```text
GET /api/docs/deploy/preview?site_id=...&target=sitelet&environment=staging&locale=en
```

Returns:

- generated docs files
- `easiio-docs-deployment-manifest.json`
- `deploymentTarget`
- `environment`
- locale metadata
- file paths
- document/file counts
- operator checklist
- `requiresDeploymentApproval:true`
- `deploymentBlocked:true`

This endpoint is preview-only.

### Create deployment handoff package

```text
POST /api/docs/deploy/package
```

Required confirmation flag:

```json
{
  "confirmDeploymentPackage": true
}
```

Without that flag, the endpoint returns `409` and no ZIP is written.

Successful packages are written under:

```text
/home/jianl/.hermes/tools/easiio_docs_module/dist/easiio-docs-deployments/
```

## Supported deployment targets

```text
static-html
sitelet
wordpress
nextjs-mdx
docusaurus
mkdocs
hugo
vitepress
```

`sitelet` and `wordpress` handoffs currently package static HTML artifacts and a manifest/checklist for the next reviewed platform-specific handoff. They do not upload to Sitelet or create/publish WordPress content automatically.

## Supported environments

```text
local
preview
staging
production
```

Environment is metadata/checklist context only. Selecting `production` does not deploy to production.

## Admin UI changes

Updated:

```text
/home/jianl/.hermes/tools/easiio_docs_module/frontend/admin.html
/home/jianl/.hermes/tools/easiio_docs_module/frontend/admin.js
```

Added:

- Deployment handoff panel
- Environment selector
- Preview deployment handoff button
- Create deployment handoff ZIP button
- browser confirmation before sending `confirmDeploymentPackage:true`
- exported `previewDeployment` and `packageDeployment` functions on `window.EasiioDocsAdmin`

## Safety model

Phase 12 is intentionally handoff-only.

It does **not**:

- publish to WordPress
- upload to Sitelet
- deploy to hosting
- modify DNS
- write to production services
- include private/internal/draft docs by default

Default scope remains:

```text
status=published
visibility=public
```

Owner-token protection from Phase 8 still applies to write/action endpoints when `EASIIO_DOCS_OWNER_TOKEN` is configured.

## Validation

Full validation command used:

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py backend/docs_wordpress.py backend/docs_rag.py backend/docs_exporters.py backend/docs_importers.py backend/docs_deploy.py
node --check frontend/admin.js
node tests/exporters_static.test.js
node tests/admin_export_ui_static.test.js
node tests/admin_editor_ui_static.test.js
node tests/import_export_static.test.js
node tests/localization_static.test.js
node tests/deployment_static.test.js
python3 tests/test_docs_backend.py -v
```

Result:

```text
Ran 22 tests in 0.460s
OK
```

Runtime smoke marker:

```text
easiio_docs_phase12_smoke_ok
```

Smoke cleanup marker:

```text
phase12_smoke_cleanup_ok
```

## Recommended next phase

Phase 13 can add a deployment history/audit log and handoff records, so operators can see who generated a package, when, for which target/environment/locale, and with which file manifest.
