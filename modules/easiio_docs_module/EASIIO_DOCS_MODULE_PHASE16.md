# Easiio Docs Module — Phase 16

## Phase 16 — Deployment approval workflow and release notes

Phase 16 extends local deployment package operations with a review/approval layer:

- update approval state for a deployment package
- track approval history events
- generate package release notes from manifest and ZIP content
- package locking for approved/released packages so checklist mutation is blocked
- expose admin UI controls for approval, release notes, and approval history

## Health marker

```json
{"phase":"16-approval-workflow"}
```

## Owner-protected endpoints

```text
POST /api/docs/deploy/approval
GET  /api/docs/deploy/approvals?id=<audit_id>
GET  /api/docs/deploy/release-notes?id=<audit_id>
```

Approval payload:

```json
{
  "id": 1,
  "status": "approved",
  "actor": "operator",
  "note": "Approved after manual staging review"
}
```

Supported approval states:

```text
draft
reviewed
approved
released
rejected
```

`approved` and `released` lock the package metadata checklist so later checklist updates return a package-locked response instead of silently changing approved handoff state.

## Admin UI

`frontend/admin.html` and `frontend/admin.js` add a Deployment approval workflow panel with:

- approval status selector
- approval actor input
- approval note field
- Update approval
- Load release notes
- Load approval history

## Safety guarantees

- All approval endpoints are owner/admin protected when owner auth is configured.
- Approval workflow is local metadata only.
- It does not publish, upload, deploy, call WordPress, call Sitelet, or modify DNS/hosting.
- Audit/release-note output must not contain raw tokens, passwords, auth headers, or API keys.
- Package locking prevents accidental checklist changes after approval/release.

## Verification

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py backend/docs_wordpress.py backend/docs_rag.py backend/docs_exporters.py backend/docs_importers.py backend/docs_deploy.py backend/docs_audit.py
node --check frontend/admin.js
node tests/deployment_approval_static.test.js
python3 tests/test_docs_backend.py -v
```

Smoke marker:

```text
easiio_docs_phase16_smoke_ok
```

## Suggested Phase 17

Deployment release dashboard and operator handoff report:

- release dashboard by site/environment
- approved package report export
- deployment readiness scoring
- operator handoff Markdown/PDF report
- still no automatic external deployment without explicit separate confirmation
