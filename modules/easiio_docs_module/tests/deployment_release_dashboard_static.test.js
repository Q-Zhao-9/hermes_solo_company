const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

const app = read('backend/app.py');
const audit = read('backend/docs_audit.py');
const adminHtml = read('frontend/admin.html');
const adminJs = read('frontend/admin.js');
const readme = read('README.md');
const phaseDoc = read('EASIIO_DOCS_MODULE_PHASE17.md');

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

assert(app.includes('17-release-dashboard'), 'health marker must identify Phase 17');
assert(app.includes('/api/docs/deploy/releases'), 'release dashboard route must be wired');
assert(app.includes('/api/docs/deploy/handoff-report'), 'operator handoff report route must be wired');
assert(app.includes('build_deployment_release_dashboard_response'), 'app must import/use release dashboard helper');
assert(app.includes('build_deployment_operator_handoff_report_response'), 'app must import/use handoff report helper');

assert(audit.includes('build_deployment_release_dashboard_response'), 'audit module must expose dashboard helper');
assert(audit.includes('build_deployment_operator_handoff_report_response'), 'audit module must expose handoff report helper');
assert(audit.includes('calculate_deployment_readiness'), 'audit module must calculate readiness');
assert(audit.includes('readyForOperatorHandoff'), 'readiness response must include operator handoff flag');
assert(audit.includes('releaseQueue'), 'dashboard must expose release queue');
assert(audit.includes('Operator Handoff Report'), 'handoff report must generate markdown report');

assert(adminHtml.includes('Release dashboard'), 'admin UI must include release dashboard panel');
assert(adminHtml.includes('docs-admin-release-dashboard'), 'admin UI must include release dashboard button');
assert(adminHtml.includes('docs-admin-handoff-report'), 'admin UI must include handoff report button');
assert(adminHtml.includes('docs-admin-release-status-filter'), 'admin UI must include approval status filter');
assert(adminHtml.includes('readiness scoring'), 'admin UI must describe readiness scoring');

assert(adminJs.includes('loadReleaseDashboard'), 'admin JS must load release dashboard');
assert(adminJs.includes('renderReleaseDashboard'), 'admin JS must render release dashboard');
assert(adminJs.includes('loadOperatorHandoffReport'), 'admin JS must load operator handoff report');
assert(adminJs.includes('releaseDashboardQuery'), 'admin JS must build release dashboard query');
assert(adminJs.includes('docs-admin-release-dashboard'), 'admin JS must wire release dashboard button');
assert(adminJs.includes('docs-admin-handoff-report'), 'admin JS must wire handoff report button');
assert(adminJs.includes('loadOperatorHandoffReport'), 'admin helper export must include handoff report function');

assert(readme.includes('Phase 17'), 'README must document Phase 17');
assert(readme.includes('/api/docs/deploy/releases'), 'README must document release dashboard endpoint');
assert(readme.includes('/api/docs/deploy/handoff-report'), 'README must document handoff report endpoint');
assert(readme.includes('17-release-dashboard'), 'README must document Phase 17 health marker');
assert(phaseDoc.includes('Phase 17'), 'dedicated Phase 17 doc must exist');
assert(phaseDoc.includes('easiio_docs_phase17_smoke_ok'), 'Phase 17 doc must include smoke marker');

console.log('PASS Phase 17 release dashboard assets and routes are wired');
