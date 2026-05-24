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
const phaseDocPath = path.join(root, 'EASIIO_DOCS_MODULE_PHASE25.md');

assert(app.includes('25-v1-release'), 'health marker must identify Phase 25');
assert(app.includes('/api/docs/deploy/v1-release-summary'), 'v1 release summary endpoint must be wired');
assert(app.includes('/api/docs/deploy/v1-release-package'), 'v1 release package endpoint must be wired');
assert(app.includes('build_v1_release_summary_response'), 'app must use v1 release summary helper');
assert(app.includes('build_v1_release_package_response'), 'app must use v1 release package helper');

assert(connectors.includes('V1_RELEASE_VERSION'), 'connector module must define v1 release version');
assert(connectors.includes('build_v1_release_summary_response'), 'connector module must build v1 release summary');
assert(connectors.includes('build_v1_release_package_response'), 'connector module must build v1 release package');
assert(connectors.includes('easiio-docs-v1-release-summary'), 'summary response must identify export type');
assert(connectors.includes('easiio-docs-v1-release-package'), 'package response must identify export type');
assert(connectors.includes('confirmV1ReleasePackage'), 'release package must be confirmation gated');
assert(connectors.includes('dist/easiio-docs-v1-release'), 'release package output directory must be documented in code');
assert(connectors.includes('finalQaChecklist'), 'release summary must include final QA checklist');
assert(connectors.includes('securityChecklist'), 'release summary must include security checklist');
assert(connectors.includes('releaseFreeze'), 'release summary must include release freeze data');
assert(connectors.includes('No external deployment is executed by this module'), 'Phase 25 must preserve local-only safety');

assert(adminHtml.includes('Final QA and v1 release'), 'admin UI must include final QA panel label');
assert(adminHtml.includes('docs-admin-v1-release-summary'), 'admin UI must include v1 release summary button');
assert(adminHtml.includes('docs-admin-v1-release-package'), 'admin UI must include v1 release package button');
assert(adminJs.includes('loadV1ReleaseSummary'), 'admin JS must load v1 release summary');
assert(adminJs.includes('createV1ReleasePackage'), 'admin JS must create v1 release package');
assert(adminJs.includes('/api/docs/deploy/v1-release-summary'), 'admin JS must call summary endpoint');
assert(adminJs.includes('/api/docs/deploy/v1-release-package'), 'admin JS must call package endpoint');

assert(readme.includes('Phase 25'), 'README must document Phase 25');
assert(readme.includes('25-v1-release'), 'README must document Phase 25 health marker');
assert(readme.includes('/api/docs/deploy/v1-release-summary'), 'README must document v1 release summary endpoint');
assert(readme.includes('/api/docs/deploy/v1-release-package'), 'README must document v1 release package endpoint');
assert(fs.existsSync(phaseDocPath), 'dedicated Phase 25 doc must exist');
const phaseDoc = fs.readFileSync(phaseDocPath, 'utf8');
assert(phaseDoc.includes('Phase 25'), 'Phase 25 doc must identify the phase');
assert(phaseDoc.includes('easiio_docs_phase25_smoke_ok'), 'Phase 25 doc must include smoke marker');
assert(phaseDoc.includes('Final QA'), 'Phase 25 doc must describe final QA');
assert(phaseDoc.includes('v1 release package'), 'Phase 25 doc must describe v1 release package');
assert(phaseDoc.includes('local-only'), 'Phase 25 doc must describe local-only safety');

console.log('PASS Phase 25 final QA and v1 release assets are wired');
