const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

const app = read('backend/app.py');
const audit = read('backend/docs_audit.py');
const adminHtml = read('frontend/admin.html');
const adminJs = read('frontend/admin.js');
const readme = read('README.md');
const phaseDoc = read('EASIIO_DOCS_MODULE_PHASE16.md');

function assert(condition, message) {
  if (!condition) {
    console.error(`FAIL ${message}`);
    process.exit(1);
  }
  console.log(`PASS ${message}`);
}

assert(app.includes('17-release-dashboard'), 'health marker includes Phase 16 approval workflow');
assert(app.includes('/api/docs/deploy/approval'), 'approval update route is wired');
assert(app.includes('/api/docs/deploy/approvals'), 'approval history route is wired');
assert(app.includes('/api/docs/deploy/release-notes'), 'release notes route is wired');
assert(app.includes('build_deployment_approval_response'), 'approval response helper is imported/used');
assert(app.includes('build_deployment_release_notes_response'), 'release notes response helper is imported/used');
assert(app.includes('build_deployment_approval_history_response'), 'approval history response helper is imported/used');

assert(audit.includes('approval_status'), 'audit schema stores approval status');
assert(audit.includes('approval_history_json'), 'audit schema stores approval history');
assert(audit.includes('release_notes_json'), 'audit schema stores release notes');
assert(audit.includes('package_locked'), 'audit schema stores package locking state');
assert(audit.includes('update_deployment_approval'), 'audit store can update approval status');
assert(audit.includes('build_deployment_approval_response'), 'approval response helper exists');
assert(audit.includes('build_deployment_release_notes_response'), 'release notes helper exists');
assert(audit.includes('build_deployment_approval_history_response'), 'approval history helper exists');
assert(audit.includes('packageLocked'), 'responses expose packageLocked state');

assert(adminHtml.includes('Deployment approval workflow'), 'admin UI has approval workflow panel');
assert(adminHtml.includes('docs-admin-approval-status'), 'admin UI has approval status control');
assert(adminHtml.includes('docs-admin-approval-update'), 'admin UI has approval update button');
assert(adminHtml.includes('docs-admin-release-notes'), 'admin UI has release notes button');
assert(adminHtml.includes('docs-admin-approval-history'), 'admin UI has approval history button');

assert(adminJs.includes('updateDeploymentApproval'), 'admin JS can update approval status');
assert(adminJs.includes('loadDeploymentReleaseNotes'), 'admin JS can load release notes');
assert(adminJs.includes('loadDeploymentApprovalHistory'), 'admin JS can load approval history');
assert(adminJs.includes('/api/docs/deploy/approval'), 'admin JS calls approval endpoint');
assert(adminJs.includes('/api/docs/deploy/release-notes'), 'admin JS calls release notes endpoint');
assert(adminJs.includes('/api/docs/deploy/approvals'), 'admin JS calls approval history endpoint');

assert(readme.includes('Phase 16'), 'README documents Phase 16');
assert(readme.includes('/api/docs/deploy/approval'), 'README documents approval endpoint');
assert(phaseDoc.includes('Phase 16'), 'dedicated Phase 16 doc exists');
assert(phaseDoc.includes('package locking'), 'dedicated Phase 16 doc explains package locking');

console.log('PASS Phase 16 deployment approval workflow assets and routes are wired');
