# Easiio Docs Module — Phase 22

## Connector runbooks and dry-run comparison

Phase 22 adds local-only Connector runbooks and dry-run comparison for the Easiio Docs Module deployment connector workflow.

Current health marker:

```text
22-connector-runbooks
```

Phase history preserves:

```text
21-connector-profiles
20-connector-dry-run
```

## Scope

Phase 22 helps an operator review connector readiness before any real external deployment by generating:

- Connector runbooks from a saved dry-run record.
- Dry-run comparison summaries between two connector dry-run records.
- Admin UI controls for loading runbooks and comparing dry-runs.

It remains local-only and review-first.

## Endpoints

Owner-protected endpoints:

```text
GET /api/docs/deploy/connector/runbook?id=<dry_run_id>
GET /api/docs/deploy/connector/dry-run-compare?left_id=<dry_run_id>&right_id=<dry_run_id>
```

Existing Phase 21 endpoints remain available:

```text
GET  /api/docs/deploy/connector/profiles
POST /api/docs/deploy/connector/profile
GET  /api/docs/deploy/connector/dry-runs
POST /api/docs/deploy/connector/preflight
```

## Runbook output

Runbook responses use:

```text
easiio-docs-connector-runbook
```

The response includes:

```json
{
  "runbookMarkdown": "# Connector runbook ...",
  "localOnly": true,
  "dryRunOnly": true,
  "externalCallsBlocked": true,
  "secretPlaceholdersOnly": true
}
```

The runbook explicitly states:

```text
No external connector calls are made by this module.
```

## Dry-run comparison output

Comparison responses use:

```text
easiio-docs-connector-dry-run-comparison
```

The response includes:

```json
{
  "scoreDelta": 20,
  "statusChanged": true,
  "connectorChanged": true,
  "profileChanged": true,
  "checkDiffs": [],
  "localOnly": true,
  "externalCallsBlocked": true
}
```

## Admin UI

Updated files:

```text
frontend/admin.html
frontend/admin.js
```

New controls:

- Runbook dry-run ID
- Load connector runbook
- Compare left dry-run ID
- Compare right dry-run ID
- Compare connector dry-runs

## Safety model

Phase 22 does not:

- deploy
- publish
- upload
- call Sitelet
- call WordPress
- call hosting providers
- call DNS providers
- execute rollback
- execute restore
- store raw credentials

Connector runbooks and dry-run comparison are local-only metadata/reporting workflows. Credentials remain redacted placeholders only.

## Validation

Targeted validation:

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_connectors.py backend/docs_audit.py
node --check frontend/admin.js
node tests/deployment_connector_runbooks_static.test.js
python3 tests/test_docs_backend.py -v -k phase22
```

Full validation:

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py backend/docs_wordpress.py backend/docs_rag.py backend/docs_exporters.py backend/docs_importers.py backend/docs_deploy.py backend/docs_audit.py backend/docs_connectors.py
node --check frontend/docs.js
node --check frontend/admin.js
for f in tests/*.test.js; do node "$f"; done
python3 tests/test_docs_backend.py -v
```

Runtime smoke marker:

```text
easiio_docs_phase22_smoke_ok
```

Cleanup marker:

```text
phase22_smoke_cleanup_ok
```

## Recommended next phase

Phase 23 should likely add operator release playbooks / final production handoff templates, still without automatic external deployment execution by default.
