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
const phaseDocPath = path.join(root, 'EASIIO_DOCS_MODULE_PHASE23.md');

assert(app.includes('23-operator-playbooks'), 'health marker must identify Phase 23');
assert(app.includes('/api/docs/deploy/operator-playbooks'), 'operator playbook catalog endpoint must be wired');
assert(app.includes('/api/docs/deploy/operator-playbook'), 'operator release playbook endpoint must be wired');
assert(app.includes('build_operator_playbook_catalog_response'), 'app must use operator playbook catalog helper');
assert(app.includes('build_operator_release_playbook_response'), 'app must use operator release playbook helper');

assert(connectors.includes('OPERATOR_PLAYBOOK_TARGETS'), 'connector module must define operator playbook targets');
assert(connectors.includes('build_operator_playbook_catalog_response'), 'connector module must build playbook catalog');
assert(connectors.includes('build_operator_release_playbook_response'), 'connector module must generate release playbooks');
assert(connectors.includes('easiio-docs-operator-release-playbook'), 'release playbook response must identify export type');
assert(connectors.includes('playbookMarkdown'), 'operator playbook response must include Markdown content');
assert(connectors.includes('Sitelet Deployment Playbook'), 'operator playbooks must include Sitelet target playbook');
assert(connectors.includes('WordPress Deployment Playbook'), 'operator playbooks must include WordPress target playbook');
assert(connectors.includes('Static Hosting Deployment Playbook'), 'operator playbooks must include static hosting target playbook');
assert(connectors.includes('No external deployment is executed'), 'operator playbook must state no external deployment is executed');
assert(connectors.includes('localOnly'), 'Phase 23 playbook responses must declare local-only behavior');
assert(connectors.includes('externalCallsBlocked'), 'Phase 23 playbook responses must block external calls');

assert(adminHtml.includes('Final operator release playbooks'), 'admin UI must include Phase 23 playbook panel label');
assert(adminHtml.includes('docs-admin-operator-playbook-id'), 'admin UI must include operator playbook audit ID input');
assert(adminHtml.includes('docs-admin-operator-playbook-target'), 'admin UI must include operator playbook target select');
assert(adminHtml.includes('docs-admin-operator-playbook-catalog'), 'admin UI must include playbook catalog button');
assert(adminHtml.includes('docs-admin-operator-playbook-load'), 'admin UI must include load playbook button');

assert(adminJs.includes('loadOperatorPlaybookCatalog'), 'admin JS must load operator playbook catalog');
assert(adminJs.includes('loadOperatorReleasePlaybook'), 'admin JS must load operator release playbook');
assert(adminJs.includes('/api/docs/deploy/operator-playbooks'), 'admin JS must call playbook catalog endpoint');
assert(adminJs.includes('/api/docs/deploy/operator-playbook'), 'admin JS must call operator playbook endpoint');

assert(readme.includes('Phase 23'), 'README must document Phase 23');
assert(readme.includes('23-operator-playbooks'), 'README must document Phase 23 health marker');
assert(readme.includes('/api/docs/deploy/operator-playbooks'), 'README must document playbook catalog endpoint');
assert(readme.includes('/api/docs/deploy/operator-playbook'), 'README must document operator playbook endpoint');
assert(fs.existsSync(phaseDocPath), 'dedicated Phase 23 doc must exist');
const phaseDoc = fs.readFileSync(phaseDocPath, 'utf8');
assert(phaseDoc.includes('Phase 23'), 'Phase 23 doc must identify the phase');
assert(phaseDoc.includes('easiio_docs_phase23_smoke_ok'), 'Phase 23 doc must include smoke marker');
assert(phaseDoc.includes('Final operator release playbooks'), 'Phase 23 doc must describe final operator release playbooks');
assert(phaseDoc.includes('local-only'), 'Phase 23 doc must describe local-only safety');

console.log('PASS Phase 23 final operator release playbooks assets are wired');
