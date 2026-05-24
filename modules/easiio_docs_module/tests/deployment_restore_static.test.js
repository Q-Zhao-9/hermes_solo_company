const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

const app = read('backend/app.py');
const audit = read('backend/docs_audit.py');
const adminHtml = read('frontend/admin.html');
const adminJs = read('frontend/admin.js');
const readme = read('README.md');
const phaseDocPath = path.join(root, 'EASIIO_DOCS_MODULE_PHASE19.md');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(app.includes('19-restore-planning'), 'health marker must identify Phase 19');
assert(app.includes('/api/docs/deploy/archive/integrity'), 'archive integrity endpoint must be wired');
assert(app.includes('/api/docs/deploy/rollback-plan'), 'rollback plan endpoint must be wired');
assert(app.includes('/api/docs/deploy/restore-package'), 'restore package endpoint must be wired');
assert(app.includes('build_release_archive_integrity_response'), 'app must import/use archive integrity helper');
assert(app.includes('build_release_rollback_plan_response'), 'app must import/use rollback plan helper');
assert(app.includes('build_release_restore_package_response'), 'app must import/use restore package helper');

assert(audit.includes('build_release_archive_integrity_response'), 'audit module must expose archive integrity helper');
assert(audit.includes('build_release_rollback_plan_response'), 'audit module must expose rollback plan helper');
assert(audit.includes('build_release_restore_package_response'), 'audit module must expose restore package helper');
assert(audit.includes('confirmPrepareRestore'), 'restore package creation must require explicit confirmation');
assert(audit.includes('easiio-docs-restore-packages'), 'restore package artifacts must use local restore package directory');
assert(audit.includes('verifyReleaseIntegrity'), 'Phase 19 helper naming must describe integrity verification');
assert(audit.includes('rollbackPlanMarkdown'), 'rollback planning response must include markdown');

assert(adminHtml.includes('Release restore / rollback'), 'admin UI must include release restore panel');
assert(adminHtml.includes('docs-admin-archive-integrity'), 'admin UI must include archive integrity button');
assert(adminHtml.includes('docs-admin-rollback-plan'), 'admin UI must include rollback plan button');
assert(adminHtml.includes('docs-admin-restore-package'), 'admin UI must include restore package button');
assert(adminHtml.includes('docs-admin-rollback-previous-id'), 'admin UI must include previous release ID input');

assert(adminJs.includes('verifyReleaseIntegrity'), 'admin JS must verify release integrity');
assert(adminJs.includes('loadRollbackPlan'), 'admin JS must load rollback plan');
assert(adminJs.includes('prepareRestorePackage'), 'admin JS must prepare restore package');
assert(adminJs.includes('/api/docs/deploy/archive/integrity'), 'admin JS must call archive integrity endpoint');
assert(adminJs.includes('/api/docs/deploy/rollback-plan'), 'admin JS must call rollback plan endpoint');
assert(adminJs.includes('/api/docs/deploy/restore-package'), 'admin JS must call restore package endpoint');
assert(adminJs.includes('confirmPrepareRestore'), 'admin JS must send restore confirmation flag');

assert(readme.includes('Phase 19'), 'README must document Phase 19');
assert(readme.includes('19-restore-planning'), 'README must document Phase 19 health marker');
assert(readme.includes('/api/docs/deploy/archive/integrity'), 'README must document integrity endpoint');
assert(readme.includes('/api/docs/deploy/rollback-plan'), 'README must document rollback plan endpoint');
assert(readme.includes('/api/docs/deploy/restore-package'), 'README must document restore package endpoint');
assert(fs.existsSync(phaseDocPath), 'dedicated Phase 19 doc must exist');
const phaseDoc = fs.readFileSync(phaseDocPath, 'utf8');
assert(phaseDoc.includes('Phase 19'), 'Phase 19 doc must identify the phase');
assert(phaseDoc.includes('easiio_docs_phase19_smoke_ok'), 'Phase 19 doc must include smoke marker');
assert(phaseDoc.includes('local-only'), 'Phase 19 doc must describe local-only safety');

console.log('PASS Phase 19 restore planning assets and routes are wired');
