# Easiio Docs Module — Phase 23

## Final operator release playbooks

Phase 23 adds final local-only operator release playbooks for the Easiio Docs Module deployment handoff workflow. These playbooks turn a prepared deployment package/audit record into target-specific human instructions for Sitelet, WordPress, static hosting, and framework deployment targets.

## Health marker

```json
{
  "phase": "23-operator-playbooks"
}
```

The `/health` `phaseHistory` keeps previous milestones including:

```text
22-connector-runbooks
21-connector-profiles
20-connector-dry-run
```

## New owner-protected endpoints

```text
GET /api/docs/deploy/operator-playbooks
GET /api/docs/deploy/operator-playbook?id=<audit_id>&target=<target>
```

The catalog endpoint returns:

```text
easiio-docs-operator-playbook-catalog
```

The playbook endpoint returns:

```text
easiio-docs-operator-release-playbook
```

with:

```text
playbookMarkdown
readyForOperatorHandoff
localOnly: true
externalCallsBlocked: true
secretPlaceholdersOnly: true
```

## Supported playbook targets

```text
sitelet
wordpress
static-hosting
nextjs-mdx
docusaurus
mkdocs
hugo
vitepress
```

The `static-html` deployment target maps to the `static-hosting` operator playbook.

## Playbook content

Each generated playbook includes:

- target-specific title, such as `Sitelet Deployment Playbook` or `WordPress Deployment Playbook`
- release package metadata
- approval/readiness state
- operator steps
- operator handoff checklist
- verification checklist
- safety boundary
- rollback/restore reminder

Every playbook includes the safety line:

```text
No external deployment is executed by this module.
```

## Safety model

Phase 23 is local-only and review-first.

It does not:

- deploy
- publish
- upload
- call Sitelet
- call WordPress
- call hosting providers
- change DNS
- execute rollback
- execute restore
- store raw credentials

All endpoints remain owner-protected when `EASIIO_DOCS_OWNER_TOKEN` is configured.

## Admin UI

`frontend/admin.html` and `frontend/admin.js` add:

- Final operator release playbooks panel
- Operator playbook audit ID input
- Operator playbook target select
- Load operator playbook catalog button
- Load operator release playbook button

Admin JS functions:

```text
operatorPlaybookId
operatorPlaybookTarget
loadOperatorPlaybookCatalog
loadOperatorReleasePlaybook
```

## Validation

Targeted validation:

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_connectors.py backend/docs_audit.py
node --check frontend/admin.js
node tests/deployment_operator_playbooks_static.test.js
python3 tests/test_docs_backend.py -v -k phase23
```

Full validation:

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
set -e
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py backend/docs_wordpress.py backend/docs_rag.py backend/docs_exporters.py backend/docs_importers.py backend/docs_deploy.py backend/docs_audit.py backend/docs_connectors.py
node --check frontend/docs.js
node --check frontend/admin.js
for f in tests/*.test.js; do echo "RUN $f"; node "$f"; done
python3 tests/test_docs_backend.py -v
```

Smoke marker:

```text
easiio_docs_phase23_smoke_ok
```

Cleanup marker:

```text
phase23_smoke_cleanup_ok
```

## Recommended next phase

Phase 24 should focus on packaging, onboarding, and module installation guide:

- clean install guide
- env var reference
- start/stop commands
- backup/restore guide
- sample Sitelet integration
- sample WordPress plugin usage guide
- admin workflow guide
