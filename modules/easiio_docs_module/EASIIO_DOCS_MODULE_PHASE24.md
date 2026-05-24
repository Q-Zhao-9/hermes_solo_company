# Easiio Docs Module — Phase 24 Packaging and Onboarding

Phase 24 adds local-only Packaging and onboarding guidance for installing and operating the Easiio Docs Module as a reusable website component.

## Scope

Phase 24 provides owner-protected guide/checklist endpoints and admin UI controls for:

- clean install paths and module layout
- environment variable reference
- Start/stop commands
- Backup and restore checklist
- Sitelet integration
- WordPress plugin usage
- static/framework integration notes
- admin workflow guide
- reusable v1 onboarding checklist

## Endpoints

```text
GET /api/docs/deploy/onboarding-guide?site_id=<site_id>&integration=<target>
GET /api/docs/deploy/onboarding-checklist?site_id=<site_id>&integration=<target>
```

Supported integrations:

```text
sitelet
wordpress
static-html
nextjs-mdx
docusaurus
mkdocs
hugo
vitepress
```

## Safety model

The Phase 24 workflows are local-only and review-first.

- No external deployment is executed.
- No external connector calls are made.
- No upload, publish, DNS, rollback, restore, or WordPress/Sitelet write occurs.
- Secret values are represented as placeholders only, for example `EASIIO_DOCS_OWNER_TOKEN=[REDACTED]`.
- Owner/admin authorization protects the endpoints when `EASIIO_DOCS_OWNER_TOKEN` is configured.

## Response types

```text
easiio-docs-onboarding-guide
easiio-docs-onboarding-checklist
```

Guide responses include `installMarkdown` with install, environment, start/stop, backup/restore, integration, and admin workflow sections.

Checklist responses include structured checklist rows suitable for admin UI rendering and future release package handoff.

## Validation

Targeted validation:

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_connectors.py backend/docs_audit.py
node --check frontend/admin.js
node tests/deployment_onboarding_static.test.js
python3 tests/test_docs_backend.py -v -k phase24
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

Runtime smoke marker:

```text
easiio_docs_phase24_smoke_ok
phase24_smoke_cleanup_ok
```

## Recommended next phase

Phase 25 should be final QA, stabilization, version freeze, release package preparation, and v1 handoff documentation.
