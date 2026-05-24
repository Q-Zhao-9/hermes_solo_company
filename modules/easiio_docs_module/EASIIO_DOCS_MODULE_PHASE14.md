# Easiio Docs Module — Phase 14 Deployment Audit Operations

Phase 14 adds operations polish for the Phase 13 deployment history/audit log.

## What changed

- Health marker advanced to:

```json
{"phase":"14-audit-operations"}
```

- Deployment history supports filters:

```text
target
environment
locale
limit
```

- Added owner-protected summary endpoint:

```text
GET /api/docs/deploy/summary?site_id=...&target=...&environment=...&locale=...
```

- Added owner-protected CSV export endpoint:

```text
GET /api/docs/deploy/history.csv?site_id=...&target=...&environment=...&locale=...
```

- Updated admin UI with:
  - history target filter
  - history environment filter
  - history locale filter
  - Load audit summary button
  - Load deployment history button
  - Export history CSV button

## Backend helpers

Updated `backend/docs_audit.py` with:

- `filter_deployment_history()`
- `summarize_deployment_history()`
- `deployment_history_to_csv()`
- `build_deployment_summary_response()`
- `build_deployment_history_csv_response()`

## Safety model

- Summary and CSV endpoints are owner-protected when `EASIIO_DOCS_OWNER_TOKEN` is configured.
- The CSV export contains only local audit metadata.
- No owner token, auth header, password, API key, credential, or connection secret is stored or exported.
- No external deploy, WordPress publish, Sitelet upload, DNS change, or hosting action is performed.

## Validation

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py backend/docs_wordpress.py backend/docs_rag.py backend/docs_exporters.py backend/docs_importers.py backend/docs_deploy.py backend/docs_audit.py
node --check frontend/admin.js
node tests/deployment_ops_static.test.js
python3 tests/test_docs_backend.py -v
```

## Recommended Phase 15

Add package re-download and manifest inspection helpers:

- list package files by audit ID
- download/re-open a local package by audit ID
- compare two deployment manifests
- mark checklist status per handoff package
