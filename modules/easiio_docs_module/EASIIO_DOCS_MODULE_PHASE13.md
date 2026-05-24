# Easiio Docs Module — Phase 13 Deployment History / Audit Log

Phase 13 adds a local audit trail for deployment handoff packages.

## What changed

- Added `backend/docs_audit.py` with `DocsAuditStore`.
- Added SQLite table `docs_deployment_audit` in the existing Easiio Docs database.
- Updated deployment package creation to record each confirmed package.
- Added owner-protected history endpoint:

```text
GET /api/docs/deploy/history?site_id=...&limit=25&target=static-html&environment=staging
```

- Updated `/health` phase marker:

```json
{"phase":"13-deployment-history"}
```

- Added admin UI controls for loading deployment history.
- Added backend and static tests for Phase 13.

## Safety model

- History is local-only SQLite metadata.
- It records confirmed package creation only.
- It does not deploy, upload, publish, push to Sitelet, push to WordPress, or change DNS/hosting.
- It does not store owner tokens, auth headers, passwords, API keys, or credentials.
- The history endpoint is owner-protected when `EASIIO_DOCS_OWNER_TOKEN` is configured.

## Recorded fields

Each audit row records:

- `site_id`
- event type: `deployment_package_created`
- deployment target
- export target
- environment
- locale
- status / visibility scope
- package path
- package size
- approved by
- document count
- file count
- file paths
- deployment manifest JSON
- timestamp

## Validation

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py backend/docs_wordpress.py backend/docs_rag.py backend/docs_exporters.py backend/docs_importers.py backend/docs_deploy.py backend/docs_audit.py
node --check frontend/admin.js
node tests/deployment_history_static.test.js
python3 tests/test_docs_backend.py -v
```

## Recommended Phase 14

Deployment history is now available. The next useful phase is analytics/operations polish, for example:

- audit-log filtering and CSV export
- deployment package comparison
- restore/re-download helper for local packages
- admin dashboard counters for recent deployments
- Sitelet/WordPress handoff checklist status tracking
