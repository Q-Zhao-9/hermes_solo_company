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
const phaseDocPath = path.join(root, 'EASIIO_DOCS_MODULE_PHASE24.md');

assert(app.includes('24-onboarding-guide'), 'health marker must identify Phase 24');
assert(app.includes('/api/docs/deploy/onboarding-guide'), 'onboarding guide endpoint must be wired');
assert(app.includes('/api/docs/deploy/onboarding-checklist'), 'onboarding checklist endpoint must be wired');
assert(app.includes('build_onboarding_guide_response'), 'app must use onboarding guide helper');
assert(app.includes('build_onboarding_checklist_response'), 'app must use onboarding checklist helper');

assert(connectors.includes('ONBOARDING_INTEGRATIONS'), 'connector module must define onboarding integrations');
assert(connectors.includes('build_onboarding_guide_response'), 'connector module must build onboarding guide');
assert(connectors.includes('build_onboarding_checklist_response'), 'connector module must build onboarding checklist');
assert(connectors.includes('easiio-docs-onboarding-guide'), 'onboarding guide response must identify export type');
assert(connectors.includes('easiio-docs-onboarding-checklist'), 'onboarding checklist response must identify export type');
assert(connectors.includes('installMarkdown'), 'onboarding guide must include install Markdown');
assert(connectors.includes('Environment variable reference'), 'onboarding guide must include env var reference');
assert(connectors.includes('Start/stop commands'), 'onboarding guide must include start/stop commands');
assert(connectors.includes('Backup and restore'), 'onboarding guide must include backup/restore instructions');
assert(connectors.includes('Sitelet integration'), 'onboarding guide must include Sitelet integration');
assert(connectors.includes('WordPress plugin usage'), 'onboarding guide must include WordPress usage');
assert(connectors.includes('localOnly'), 'Phase 24 responses must declare local-only behavior');
assert(connectors.includes('externalCallsBlocked'), 'Phase 24 responses must block external calls');

assert(adminHtml.includes('Packaging and onboarding'), 'admin UI must include Phase 24 onboarding panel label');
assert(adminHtml.includes('docs-admin-onboarding-site-id'), 'admin UI must include onboarding site ID input');
assert(adminHtml.includes('docs-admin-onboarding-integration'), 'admin UI must include onboarding integration select');
assert(adminHtml.includes('docs-admin-onboarding-guide'), 'admin UI must include onboarding guide button');
assert(adminHtml.includes('docs-admin-onboarding-checklist'), 'admin UI must include onboarding checklist button');

assert(adminJs.includes('loadOnboardingGuide'), 'admin JS must load onboarding guide');
assert(adminJs.includes('loadOnboardingChecklist'), 'admin JS must load onboarding checklist');
assert(adminJs.includes('/api/docs/deploy/onboarding-guide'), 'admin JS must call onboarding guide endpoint');
assert(adminJs.includes('/api/docs/deploy/onboarding-checklist'), 'admin JS must call onboarding checklist endpoint');

assert(readme.includes('Phase 24'), 'README must document Phase 24');
assert(readme.includes('24-onboarding-guide'), 'README must document Phase 24 health marker');
assert(readme.includes('/api/docs/deploy/onboarding-guide'), 'README must document onboarding guide endpoint');
assert(readme.includes('/api/docs/deploy/onboarding-checklist'), 'README must document onboarding checklist endpoint');
assert(fs.existsSync(phaseDocPath), 'dedicated Phase 24 doc must exist');
const phaseDoc = fs.readFileSync(phaseDocPath, 'utf8');
assert(phaseDoc.includes('Phase 24'), 'Phase 24 doc must identify the phase');
assert(phaseDoc.includes('easiio_docs_phase24_smoke_ok'), 'Phase 24 doc must include smoke marker');
assert(phaseDoc.includes('Packaging and onboarding'), 'Phase 24 doc must describe packaging and onboarding');
assert(phaseDoc.includes('local-only'), 'Phase 24 doc must describe local-only safety');

console.log('PASS Phase 24 packaging and onboarding assets are wired');
