# Easiio Docs Module — Phase 17

## Phase 17 — Release dashboard and operator handoff report

Phase 17 adds owner-protected release operations for reviewing approved deployment packages before a human operator performs any external deployment.

## Scope

Phase 17 adds:

- release dashboard grouped by approval status and readiness state
- readiness scoring per deployment package
- release queue view for draft/reviewed/approved packages
- operator handoff report generated as Markdown
- admin UI controls for release dashboard and handoff report

It remains local-only and review-first. It does **not** upload, publish, deploy, modify DNS, call WordPress, or call Sitelet.

## Health marker

```json
{"phase":"17-release-dashboard"}
```

## New owner-protected endpoints

```text
GET /api/docs/deploy/releases?site_id=<site>&target=<target>&environment=<env>&locale=<locale>&approval_status=<status>&limit=25
GET /api/docs/deploy/handoff-report?id=<audit_id>
```

## Readiness scoring

Readiness is metadata-only and based on:

- checklist completion, up to 60 points
- approval status, up to 30 points
- existing local ZIP package, up to 10 points

A package is `readyForOperatorHandoff` only when it is approved/released, the local ZIP exists, and checklist items are complete.

## Admin UI

`frontend/admin.html` adds a **Release dashboard** panel with:

- approval status filter
- Load release dashboard
- Load operator handoff report

`frontend/admin.js` adds:

```text
releaseDashboardQuery()
loadReleaseDashboard()
renderReleaseDashboard()
loadOperatorHandoffReport()
```

## Safety guarantees

- endpoints require owner/admin auth when configured
- reports do not expose raw owner tokens or auth headers
- no external deployment is performed
- dashboard and handoff report are local review artifacts only
- package data comes from local audit/package metadata

## Validation

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_audit.py
node --check frontend/admin.js
python3 tests/test_docs_backend.py -v
node tests/deployment_release_dashboard_static.test.js
```

Smoke marker:

```text
easiio_docs_phase17_smoke_ok
```

## Recommended Phase 18

Phase 18 can add manual external publish adapters with strict confirmation gates and dry-run-first execution, or a release archive/attestation workflow before external deployment is introduced.
