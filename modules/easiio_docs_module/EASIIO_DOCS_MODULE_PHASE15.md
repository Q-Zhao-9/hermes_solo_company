# Easiio Docs Module — Phase 15

## Phase 15 — Deployment package operations

Phase 15 extends the Phase 12–14 deployment handoff/audit workflow with local package operations for operators:

- inspect one deployment package by audit record ID
- re-download an existing local deployment ZIP by audit record ID
- compare two package manifests/file lists
- track manual deployment checklist status

The workflow remains owner-protected and local-only. It does not upload, publish, deploy, change DNS, or sync to WordPress/Sitelet automatically.

## Health marker

```json
{"phase":"15-package-operations"}
```

## Endpoints

All endpoints are owner/admin protected when `EASIIO_DOCS_OWNER_TOKEN` is configured.

```text
GET  /api/docs/deploy/package?id=<audit_id>
GET  /api/docs/deploy/package/download?id=<audit_id>
GET  /api/docs/deploy/compare?left_id=<audit_id>&right_id=<audit_id>
POST /api/docs/deploy/checklist
```

Checklist update payload:

```json
{
  "id": 1,
  "checklist": {
    "manual_review": {"completed": true, "note": "Reviewed"},
    "wordpress_upload": {"completed": false, "note": "Waiting for approval"}
  },
  "updatedBy": "operator"
}
```

## Default checklist keys

```text
manual_review
static_files_verified
sitelet_upload
wordpress_upload
production_publish
```

## Admin UI

`frontend/admin.html` and `frontend/admin.js` add a Deployment package operations panel with controls for:

- package audit ID
- compare left/right package IDs
- checklist JSON
- load package detail
- download package ZIP
- compare packages
- update checklist

## Safety guarantees

- owner-protected package inspection/download/compare/checklist routes
- only local ZIPs already recorded in the audit table can be downloaded
- checklist state is metadata-only
- no auth tokens, headers, passwords, API keys, or secrets are stored in package operations
- no external write/publish/deploy happens

## Validation

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py backend/docs_wordpress.py backend/docs_rag.py backend/docs_exporters.py backend/docs_importers.py backend/docs_deploy.py backend/docs_audit.py
node --check frontend/admin.js
node tests/deployment_package_ops_static.test.js
python3 tests/test_docs_backend.py -v
```

Runtime smoke marker:

```text
easiio_docs_phase15_smoke_ok
phase15_smoke_cleanup_ok
```
