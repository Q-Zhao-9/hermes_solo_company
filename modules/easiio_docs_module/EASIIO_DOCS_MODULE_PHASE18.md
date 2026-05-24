# Easiio Docs Module — Phase 18

## Phase 18 — Release archive and attestation workflow

Phase 18 adds a local release archive layer for packages that have passed the Phase 17 readiness process. It creates owner-protected, review-only archive records with SHA-256 hashes for the ZIP package, deployment manifest, generated operator handoff report, release notes, and individual files inside the ZIP.

## New owner-protected endpoints

```text
POST /api/docs/deploy/archive
GET  /api/docs/deploy/archive
GET  /api/docs/deploy/attestation?id=<audit_id>
GET  /api/docs/deploy/report/download?id=<audit_id>
```

Archive creation requires:

```json
{
  "id": 123,
  "confirmArchiveRelease": true,
  "createdBy": "operator"
}
```

The archive workflow is local-only. It does not deploy, publish, upload, change DNS, or call external services.

## Archive output

Archive files are written under:

```text
dist/easiio-docs-release-archive/<site_id>/package-<audit_id>/
```

Files:

```text
release-attestation.json
operator-handoff-report.md
```

The SQLite table `docs_release_archive` stores archive metadata and the attestation JSON.

## Attestation contents

The attestation includes:

- `attestationType: easiio-docs-release-attestation`
- audit record ID
- site ID
- deployment target
- environment
- locale
- approval status
- package locked state
- package SHA-256
- manifest SHA-256
- operator handoff report SHA-256
- release notes SHA-256
- readiness summary
- per-file SHA-256 hashes from the ZIP package

## Verification

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_audit.py
node --check frontend/admin.js
node tests/deployment_archive_static.test.js
python3 tests/test_docs_backend.py -v -k phase18
```

Runtime smoke marker:

```text
easiio_docs_phase18_smoke_ok
```
