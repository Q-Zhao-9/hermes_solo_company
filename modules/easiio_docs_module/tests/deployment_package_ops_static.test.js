const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

const app = read('backend/app.py');
const audit = read('backend/docs_audit.py');
const adminHtml = read('frontend/admin.html');
const adminJs = read('frontend/admin.js');
const readme = read('README.md');

function assert(condition, message) {
  if (!condition) {
    console.error(`FAIL ${message}`);
    process.exit(1);
  }
}

assert(app.includes('17-release-dashboard'), 'health marker should report Phase 15');
assert(app.includes('/api/docs/deploy/package'), 'package detail route should be wired');
assert(app.includes('/api/docs/deploy/package/download'), 'package download route should be wired');
assert(app.includes('/api/docs/deploy/compare'), 'package compare route should be wired');
assert(app.includes('/api/docs/deploy/checklist'), 'checklist update route should be wired');
assert(app.includes('build_deployment_package_detail_response'), 'app should call package detail helper');
assert(app.includes('build_deployment_package_comparison_response'), 'app should call comparison helper');
assert(app.includes('build_deployment_checklist_response'), 'app should call checklist helper');
assert(app.includes('application/zip'), 'download route should return zip content type');

assert(audit.includes('checklist_json'), 'audit store should persist checklist JSON');
assert(audit.includes('get_deployment_package_detail'), 'audit helper should load package detail by ID');
assert(audit.includes('build_deployment_package_detail_response'), 'package detail response helper should exist');
assert(audit.includes('build_deployment_package_download_response'), 'package download helper should exist');
assert(audit.includes('build_deployment_package_comparison_response'), 'package comparison helper should exist');
assert(audit.includes('build_deployment_checklist_response'), 'checklist update helper should exist');
assert(audit.includes('manual_review'), 'default checklist should include manual review');
assert(audit.includes('wordpress_upload'), 'default checklist should include WordPress upload tracking');

assert(adminHtml.includes('Deployment package operations'), 'admin UI should expose package operations panel');
assert(adminHtml.includes('docs-admin-package-id'), 'admin UI should include package ID input');
assert(adminHtml.includes('docs-admin-compare-left-id'), 'admin UI should include compare left ID input');
assert(adminHtml.includes('docs-admin-compare-right-id'), 'admin UI should include compare right ID input');
assert(adminHtml.includes('docs-admin-package-detail'), 'admin UI should include detail button');
assert(adminHtml.includes('docs-admin-package-download'), 'admin UI should include download button');
assert(adminHtml.includes('docs-admin-package-compare'), 'admin UI should include compare button');
assert(adminHtml.includes('docs-admin-checklist-update'), 'admin UI should include checklist update button');

assert(adminJs.includes('packageOpsId'), 'admin JS should expose packageOpsId helper');
assert(adminJs.includes('loadDeploymentPackageDetail'), 'admin JS should load package detail');
assert(adminJs.includes('downloadDeploymentPackage'), 'admin JS should download package zip');
assert(adminJs.includes('compareDeploymentPackages'), 'admin JS should compare packages');
assert(adminJs.includes('updateDeploymentChecklist'), 'admin JS should update checklist');
assert(adminJs.includes('/api/docs/deploy/package/download'), 'admin JS should call package download route');
assert(adminJs.includes('/api/docs/deploy/compare'), 'admin JS should call compare route');
assert(adminJs.includes('/api/docs/deploy/checklist'), 'admin JS should call checklist route');

assert(readme.includes('Phase 15'), 'README should document Phase 15');
assert(readme.includes('/api/docs/deploy/package/download'), 'README should mention package download endpoint');
assert(readme.includes('EASIIO_DOCS_MODULE_PHASE15.md'), 'README should reference dedicated Phase 15 docs');

console.log('PASS Phase 15 deployment package operations assets and routes are wired');
