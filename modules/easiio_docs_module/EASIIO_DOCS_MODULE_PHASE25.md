# Easiio Docs Module — Phase 25 Final QA and v1 Release

Phase 25 finalizes the reusable Easiio Docs Module v1 MVP/handoff with final QA, release freeze metadata, and a confirmation-gated local v1 release package.

## Scope

Phase 25 adds:

- final QA summary endpoint
- release freeze metadata
- security/safety checklist
- confirmation-gated local v1 release ZIP package
- admin UI controls for v1 release summary/package
- final phase marker for the reusable module

## Health marker

```text
25-v1-release
```

## Endpoints

```text
GET  /api/docs/deploy/v1-release-summary
POST /api/docs/deploy/v1-release-package
```

The package endpoint requires:

```json
{
  "confirmV1ReleasePackage": true,
  "approvedBy": "operator-name"
}
```

## Response types

```text
easiio-docs-v1-release-summary
easiio-docs-v1-release-package
```

## v1 release package

Local release packages are written under:

```text
dist/easiio-docs-v1-release/
```

The ZIP includes selected source, tests, README, Phase 25 docs, and a generated manifest:

```text
easiio-docs-v1-release-manifest.json
EASIIO_DOCS_MODULE_V1_RELEASE_SUMMARY.md
```

## Final QA checklist

- Full regression test suite
- Runtime smoke test
- Temporary artifact cleanup
- README and phase documentation review
- Local v1 release package creation

## Security checklist

- Secret redaction
- Local-only behavior
- Owner-protected admin/release endpoints
- Published/public default export scope
- Confirmation gates for package/archive/restore/connector/v1 package operations

## Safety model

Phase 25 is local-only and review-first.

No external deployment is executed by this module.

It does not:

- deploy
- publish
- upload
- call external services
- write to WordPress/Sitelet externally
- change DNS
- execute rollback/restore
- call connector APIs

Secrets must remain outside the package and be represented only with placeholders such as `[REDACTED]`.

## Validation

Targeted validation:

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_connectors.py backend/docs_audit.py
node --check frontend/admin.js
node tests/deployment_v1_release_static.test.js
python3 tests/test_docs_backend.py -v -k phase25
```

Full validation:

```bash
set -e
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py backend/docs_wordpress.py backend/docs_rag.py backend/docs_exporters.py backend/docs_importers.py backend/docs_deploy.py backend/docs_audit.py backend/docs_connectors.py
node --check frontend/docs.js
node --check frontend/admin.js
for f in tests/*.test.js; do echo "RUN $f"; node "$f"; done
python3 tests/test_docs_backend.py -v
```

Runtime smoke markers:

```text
easiio_docs_phase25_smoke_ok
phase25_smoke_cleanup_ok
```

## v1 status

After Phase 25, the reusable Easiio Docs Module v1 MVP/handoff is complete. Future phases should be treated as maintenance or explicit new integration work, especially any real external connector/publishing automation.
