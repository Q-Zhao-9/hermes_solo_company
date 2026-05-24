const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

const app = read('backend/app.py');
const connectors = read('backend/docs_connectors.py');
const adminHtml = read('frontend/admin.html');
const adminJs = read('frontend/admin.js');
const readme = read('README.md');
const phaseDocPath = path.join(root, 'EASIIO_DOCS_MODULE_PHASE20.md');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(app.includes('20-connector-dry-run'), 'health marker must identify Phase 20');
assert(app.includes('/api/docs/deploy/connectors'), 'connector catalog endpoint must be wired');
assert(app.includes('/api/docs/deploy/connector/preflight'), 'connector preflight endpoint must be wired');
assert(app.includes('build_connector_catalog_response'), 'app must import/use connector catalog helper');
assert(app.includes('build_connector_preflight_response'), 'app must import/use connector preflight helper');

assert(connectors.includes('SUPPORTED_CONNECTORS'), 'connector module must define supported connectors');
assert(connectors.includes('sitelet'), 'connector module must support Sitelet dry-run connector');
assert(connectors.includes('wordpress'), 'connector module must support WordPress dry-run connector');
assert(connectors.includes('static-hosting'), 'connector module must support static hosting dry-run connector');
assert(connectors.includes('confirmConnectorDryRun'), 'connector preflight must require explicit dry-run confirmation');
assert(connectors.includes('redact_connector_config'), 'connector module must redact secrets from config');
assert(connectors.includes('localOnly'), 'connector dry-run response must declare local-only behavior');
assert(connectors.includes('externalCallsBlocked'), 'connector dry-run must explicitly block external calls');
assert(connectors.includes('easiio-docs-connector-preflight'), 'connector response must identify preflight export type');

assert(adminHtml.includes('Deployment connector dry-run'), 'admin UI must include connector dry-run panel');
assert(adminHtml.includes('docs-admin-connector-type'), 'admin UI must include connector type input/select');
assert(adminHtml.includes('docs-admin-connector-config'), 'admin UI must include connector config textarea');
assert(adminHtml.includes('docs-admin-connector-catalog'), 'admin UI must include connector catalog button');
assert(adminHtml.includes('docs-admin-connector-preflight'), 'admin UI must include connector preflight button');

assert(adminJs.includes('connectorType'), 'admin JS must expose connector type helper');
assert(adminJs.includes('connectorConfigPayload'), 'admin JS must parse connector config JSON');
assert(adminJs.includes('loadConnectorCatalog'), 'admin JS must load connector catalog');
assert(adminJs.includes('runConnectorPreflight'), 'admin JS must run connector preflight');
assert(adminJs.includes('/api/docs/deploy/connectors'), 'admin JS must call connector catalog endpoint');
assert(adminJs.includes('/api/docs/deploy/connector/preflight'), 'admin JS must call connector preflight endpoint');
assert(adminJs.includes('confirmConnectorDryRun'), 'admin JS must send connector dry-run confirmation flag');

assert(readme.includes('Phase 20'), 'README must document Phase 20');
assert(readme.includes('20-connector-dry-run'), 'README must document Phase 20 health marker');
assert(readme.includes('/api/docs/deploy/connectors'), 'README must document connector catalog endpoint');
assert(readme.includes('/api/docs/deploy/connector/preflight'), 'README must document connector preflight endpoint');
assert(readme.includes('confirmConnectorDryRun'), 'README must document connector dry-run confirmation gate');
assert(fs.existsSync(phaseDocPath), 'dedicated Phase 20 doc must exist');
const phaseDoc = fs.readFileSync(phaseDocPath, 'utf8');
assert(phaseDoc.includes('Phase 20'), 'Phase 20 doc must identify the phase');
assert(phaseDoc.includes('easiio_docs_phase20_smoke_ok'), 'Phase 20 doc must include smoke marker');
assert(phaseDoc.includes('local-only'), 'Phase 20 doc must describe local-only safety');
assert(phaseDoc.includes('dry-run'), 'Phase 20 doc must describe dry-run connector behavior');

console.log('PASS Phase 20 connector dry-run assets and routes are wired');
