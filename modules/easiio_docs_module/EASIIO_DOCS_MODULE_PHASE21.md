# Easiio Docs Module — Phase 21

## Phase 21: Connector profiles and dry-run history

Phase 21 extends the Phase 20 connector dry-run system with reusable connector profiles and local dry-run history.

Health marker:

```json
{"phase":"21-connector-profiles"}
```

## Scope

Phase 21 adds:

- saved connector profiles for Sitelet, WordPress, and static-hosting dry-runs
- secret-placeholder-only profile storage
- connector preflight by `profileId`
- persisted dry-run history for operator review
- admin UI controls for saving/listing profiles and loading dry-run history

## Endpoints

Owner-protected endpoints:

```text
GET  /api/docs/deploy/connector/profiles?site_id=<site_id>&connector=<connector>
POST /api/docs/deploy/connector/profile
GET  /api/docs/deploy/connector/dry-runs?site_id=<site_id>&connector=<connector>&id=<audit_id>&profile_id=<profile_id>
POST /api/docs/deploy/connector/preflight
```

Profile save requires:

```json
{"confirmSaveConnectorProfile": true}
```

Preflight still requires:

```json
{"confirmConnectorDryRun": true}
```

## Safety model

Phase 21 remains local-only:

- no deploy
- no publish
- no upload
- no DNS changes
- no rollback execution
- no external Sitelet, WordPress, hosting, SSH, FTP, or cloud API calls

Connector profiles store secret placeholders only in `redactedConfig`. Secrets such as tokens, passwords, authorization headers, access keys, private keys, credentials, and API keys are replaced with `[REDACTED]` before persistence.

Dry-run history stores redacted metadata only, including pass/fail, readiness score, package ID, profile ID, connector, target, environment, and local-only flags.

## Tests

Static test:

```bash
node tests/deployment_connector_profiles_static.test.js
```

Backend test:

```bash
python3 tests/test_docs_backend.py -v -k phase21
```

Full validation includes Python compilation, Node syntax/static tests, and backend tests.

## Smoke marker

Runtime smoke should print:

```text
easiio_docs_phase21_smoke_ok
phase21_smoke_cleanup_ok
```

## Recommended Phase 22

Phase 22 can add operator runbook templates and dry-run comparison dashboards, still review-first and local-only.
