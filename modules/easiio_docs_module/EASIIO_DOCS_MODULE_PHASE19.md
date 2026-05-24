# Easiio Docs Module — Phase 19 Restore Planning

Phase 19 adds a **local-only release restore / rollback planning workflow** on top of the Phase 18 release archive and attestation workflow.

It does not deploy, publish, upload, or call external services. It prepares review artifacts that a human operator can use before taking any external action.

## Scope

Phase 19 implements:

- archived release integrity verification
- current-to-previous release rollback plan generation
- local restore package preparation
- admin UI controls for restore planning
- static and backend tests
- runtime smoke validation marker

## Health marker

```json
{
  "phase": "19-restore-planning"
}
```

`phaseHistory` continues to include earlier deployment/release markers including `18-release-archive`.

## Endpoints

All Phase 19 endpoints are owner/admin protected when `EASIIO_DOCS_OWNER_TOKEN` is configured.

```text
GET  /api/docs/deploy/archive/integrity?id=<audit_id>
GET  /api/docs/deploy/rollback-plan?id=<current_audit_id>&previous_id=<rollback_target_audit_id>
POST /api/docs/deploy/restore-package
```

Restore package creation requires:

```json
{
  "id": 12,
  "previous_id": 10,
  "confirmPrepareRestore": true,
  "createdBy": "operator"
}
```

## Restore package output

Local restore package ZIPs are written under:

```text
dist/easiio-docs-restore-packages/<site_id>/
```

A restore package contains local review artifacts such as:

```text
README.txt
rollback-plan.md
current-attestation.json
rollback-target-attestation.json
integrity.json
rollback-target-package.zip
```

## Safety model

- Integrity verification only reads local archive/package metadata and recomputes hashes.
- Rollback planning only generates Markdown and JSON metadata.
- Restore package preparation creates a local ZIP artifact only.
- No WordPress, Sitelet, hosting, DNS, GitHub, cloud, or external deployment API is called.
- No raw owner token, authorization header, password, API key, or private key is stored in restore artifacts.
- A restore package is not proof that a rollback was executed; it is only a handoff package for human review.

## Validation

Targeted validation:

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_deploy.py backend/docs_audit.py
node --check frontend/admin.js
node tests/deployment_restore_static.test.js
python3 tests/test_docs_backend.py -v -k phase19
```

Full validation:

```bash
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py backend/docs_wordpress.py backend/docs_rag.py backend/docs_exporters.py backend/docs_importers.py backend/docs_deploy.py backend/docs_audit.py
node --check frontend/docs.js
node --check frontend/admin.js
for f in tests/*.test.js; do node "$f"; done
python3 tests/test_docs_backend.py -v
```

Runtime smoke marker:

```text
easiio_docs_phase19_smoke_ok
```

Cleanup marker:

```text
phase19_smoke_cleanup_ok
phase19_restore_artifact_cleanup_ok
```

## Recommended Phase 20

Phase 20 can add **deployment connector dry-run adapters**: Sitelet/WordPress/static-hosting preflight checks and redacted connector configuration, still no real external publish by default.
