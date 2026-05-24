# Easiio Docs Module — Phase 20

## Phase 20: Deployment connector dry-run adapters

Phase 20 adds local-only deployment connector planning for reviewed Easiio Docs deployment packages.

The goal is to help an operator answer: “Is this package ready for a Sitelet, WordPress, or static-hosting handoff?” without performing any external deployment.

## What Phase 20 adds

- Connector catalog endpoint for supported dry-run adapters.
- Connector preflight endpoint for package readiness checks.
- Secret redaction for connector configuration.
- Admin UI panel for connector catalog and preflight.
- Static and backend tests.
- Local-only safety guarantees.

## Health marker

```json
{
  "phase": "20-connector-dry-run"
}
```

The `/health` response keeps `phaseHistory`, including `19-restore-planning`.

## Endpoints

```text
GET  /api/docs/deploy/connectors
POST /api/docs/deploy/connector/preflight
```

Both endpoints are owner/admin protected when `EASIIO_DOCS_OWNER_TOKEN` is configured.

## Supported connectors

```text
sitelet
wordpress
static-hosting
```

These are dry-run adapters only. They do not call Sitelet, WordPress, S3, Cloudflare, Netlify, Vercel, FTP, DNS, or any external API.

## Preflight confirmation gate

`POST /api/docs/deploy/connector/preflight` requires:

```json
{
  "confirmConnectorDryRun": true
}
```

Example payload:

```json
{
  "id": 12,
  "connector": "sitelet",
  "connectorConfig": {
    "base_url": "https://sitelet.easiiodev.ai",
    "api_token": "[REDACTED]"
  },
  "confirmConnectorDryRun": true,
  "requestedBy": "operator"
}
```

## Preflight checks

The preflight response checks local metadata only:

- local deployment package ZIP exists
- package readiness score
- operator handoff readiness
- connector target compatibility
- required connector config fields
- external calls are blocked

## Secret safety

Connector config fields containing values such as these are redacted before returning responses:

```text
token
secret
password
authorization
api_key
access_key
private_key
credential
```

Responses must never include raw owner tokens, API tokens, authorization headers, passwords, private keys, or credentials.

## Admin UI

`/docs/admin.html` now includes:

```text
Deployment connector dry-run
```

Controls:

- Connector type
- Connector config JSON
- Load connector catalog
- Run connector dry-run preflight

## Validation

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_connectors.py backend/docs_audit.py
node --check frontend/admin.js
node tests/deployment_connectors_static.test.js
python3 tests/test_docs_backend.py -v -k phase20
```

Full validation:

```bash
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py backend/docs_wordpress.py backend/docs_rag.py backend/docs_exporters.py backend/docs_importers.py backend/docs_deploy.py backend/docs_audit.py backend/docs_connectors.py
node --check frontend/docs.js
node --check frontend/admin.js
for f in tests/*.test.js; do node "$f"; done
python3 tests/test_docs_backend.py -v
```

## Runtime smoke marker

```text
easiio_docs_phase20_smoke_ok
```

## Safety model

Phase 20 is local-only:

- no deploy
- no publish
- no upload
- no rollback execution
- no external API calls
- no DNS changes
- no WordPress writes
- no Sitelet writes
- no credential storage

It only produces a reviewable preflight result for a human/operator.

## Recommended Phase 21

Phase 21 can add connector runbooks and environment profiles:

- saved redacted connector profiles
- operator runbook generation per target
- per-environment preflight checklist templates
- audit entries for preflight metadata only
- no external deployment execution by default
