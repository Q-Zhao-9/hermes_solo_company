const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');
function read(rel) {
  return fs.readFileSync(path.join(root, rel), 'utf8');
}

const app = read('backend/app.py');
const connectors = read('backend/docs_connectors.py');
const adminHtml = read('frontend/admin.html');
const adminJs = read('frontend/admin.js');
const readme = read('README.md');
const phaseDocPath = path.join(root, 'EASIIO_DOCS_MODULE_PHASE22.md');

assert(app.includes('22-connector-runbooks'), 'health marker must identify Phase 22');
assert(app.includes('/api/docs/deploy/connector/runbook'), 'connector runbook endpoint must be wired');
assert(app.includes('/api/docs/deploy/connector/dry-run-compare'), 'connector dry-run compare endpoint must be wired');
assert(app.includes('build_connector_runbook_response'), 'app must use connector runbook helper');
assert(app.includes('build_connector_dry_run_comparison_response'), 'app must use dry-run comparison helper');

assert(connectors.includes('build_connector_runbook_response'), 'connector module must generate runbooks');
assert(connectors.includes('easiio-docs-connector-runbook'), 'runbook response must identify export type');
assert(connectors.includes('build_connector_dry_run_comparison_response'), 'connector module must compare dry-runs');
assert(connectors.includes('easiio-docs-connector-dry-run-comparison'), 'comparison response must identify export type');
assert(connectors.includes('runbookMarkdown'), 'runbook response must include Markdown handoff content');
assert(connectors.includes('No external connector calls are made'), 'runbook must state no external connector calls are made');
assert(connectors.includes('localOnly'), 'Phase 22 responses must declare local-only behavior');
assert(connectors.includes('externalCallsBlocked'), 'Phase 22 responses must block external calls');

assert(adminHtml.includes('Connector runbooks'), 'admin UI must include connector runbooks label/controls');
assert(adminHtml.includes('docs-admin-connector-runbook-id'), 'admin UI must include connector runbook dry-run ID input');
assert(adminHtml.includes('docs-admin-connector-runbook'), 'admin UI must include connector runbook button');
assert(adminHtml.includes('docs-admin-connector-compare-left-id'), 'admin UI must include connector compare left input');
assert(adminHtml.includes('docs-admin-connector-compare-right-id'), 'admin UI must include connector compare right input');
assert(adminHtml.includes('docs-admin-connector-dry-run-compare'), 'admin UI must include connector dry-run compare button');

assert(adminJs.includes('loadConnectorRunbook'), 'admin JS must load connector runbooks');
assert(adminJs.includes('compareConnectorDryRuns'), 'admin JS must compare connector dry-runs');
assert(adminJs.includes('/api/docs/deploy/connector/runbook'), 'admin JS must call connector runbook endpoint');
assert(adminJs.includes('/api/docs/deploy/connector/dry-run-compare'), 'admin JS must call connector dry-run compare endpoint');

assert(readme.includes('Phase 22'), 'README must document Phase 22');
assert(readme.includes('22-connector-runbooks'), 'README must document Phase 22 health marker');
assert(readme.includes('/api/docs/deploy/connector/runbook'), 'README must document runbook endpoint');
assert(readme.includes('/api/docs/deploy/connector/dry-run-compare'), 'README must document dry-run compare endpoint');
assert(fs.existsSync(phaseDocPath), 'dedicated Phase 22 doc must exist');
const phaseDoc = fs.readFileSync(phaseDocPath, 'utf8');
assert(phaseDoc.includes('Phase 22'), 'Phase 22 doc must identify the phase');
assert(phaseDoc.includes('easiio_docs_phase22_smoke_ok'), 'Phase 22 doc must include smoke marker');
assert(phaseDoc.includes('Connector runbooks'), 'Phase 22 doc must describe connector runbooks');
assert(phaseDoc.includes('dry-run comparison'), 'Phase 22 doc must describe dry-run comparison');
assert(phaseDoc.includes('local-only'), 'Phase 22 doc must describe local-only safety');

console.log('PASS Phase 22 connector runbooks and dry-run comparison assets are wired');
