const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

const app = read('backend/app.py');
const audit = read('backend/docs_audit.py');
const adminHtml = read('frontend/admin.html');
const adminJs = read('frontend/admin.js');
const readme = read('README.md');
const phaseDocPath = path.join(root, 'EASIIO_DOCS_MODULE_PHASE18.md');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(app.includes('18-release-archive'), 'health marker must identify Phase 18');
assert(app.includes('/api/docs/deploy/archive'), 'release archive endpoint must be wired');
assert(app.includes('/api/docs/deploy/attestation'), 'release attestation endpoint must be wired');
assert(app.includes('/api/docs/deploy/report/download'), 'release report download endpoint must be wired');
assert(app.includes('build_release_archive_response'), 'app must import/use archive creation helper');
assert(app.includes('build_release_archive_index_response'), 'app must import/use archive index helper');
assert(app.includes('build_release_attestation_response'), 'app must import/use attestation helper');
assert(app.includes('build_release_report_download_response'), 'app must import/use report download helper');

assert(audit.includes('docs_release_archive'), 'audit module must persist release archive records');
assert(audit.includes('build_release_archive_response'), 'audit module must expose archive creation helper');
assert(audit.includes('build_release_archive_index_response'), 'audit module must expose archive index helper');
assert(audit.includes('build_release_attestation_response'), 'audit module must expose attestation helper');
assert(audit.includes('build_release_report_download_response'), 'audit module must expose report download helper');
assert(audit.includes('sha256'), 'attestation workflow must compute sha256 hashes');
assert(audit.includes('packageSha256'), 'attestation must include package hash');
assert(audit.includes('manifestSha256'), 'attestation must include manifest hash');
assert(audit.includes('handoffReportSha256'), 'attestation must include handoff report hash');
assert(audit.includes('confirmArchiveRelease'), 'archive creation must require explicit confirmation');

assert(adminHtml.includes('Release archive'), 'admin UI must include release archive panel');
assert(adminHtml.includes('docs-admin-release-archive-create'), 'admin UI must include archive creation button');
assert(adminHtml.includes('docs-admin-release-archive-index'), 'admin UI must include archive index button');
assert(adminHtml.includes('docs-admin-release-attestation'), 'admin UI must include attestation button');
assert(adminHtml.includes('docs-admin-release-report-download'), 'admin UI must include report download button');

assert(adminJs.includes('createReleaseArchive'), 'admin JS must create release archive');
assert(adminJs.includes('loadReleaseArchiveIndex'), 'admin JS must load release archive index');
assert(adminJs.includes('loadReleaseAttestation'), 'admin JS must load release attestation');
assert(adminJs.includes('downloadReleaseReport'), 'admin JS must download release report');
assert(adminJs.includes('/api/docs/deploy/archive'), 'admin JS must call release archive endpoint');
assert(adminJs.includes('/api/docs/deploy/attestation'), 'admin JS must call attestation endpoint');
assert(adminJs.includes('/api/docs/deploy/report/download'), 'admin JS must call report download endpoint');

assert(readme.includes('Phase 18'), 'README must document Phase 18');
assert(readme.includes('18-release-archive'), 'README must document Phase 18 health marker');
assert(readme.includes('/api/docs/deploy/archive'), 'README must document archive endpoint');
assert(readme.includes('/api/docs/deploy/attestation'), 'README must document attestation endpoint');
assert(readme.includes('/api/docs/deploy/report/download'), 'README must document report download endpoint');
assert(fs.existsSync(phaseDocPath), 'dedicated Phase 18 doc must exist');
const phaseDoc = fs.readFileSync(phaseDocPath, 'utf8');
assert(phaseDoc.includes('Phase 18'), 'Phase 18 doc must identify the phase');
assert(phaseDoc.includes('easiio_docs_phase18_smoke_ok'), 'Phase 18 doc must include smoke marker');

console.log('PASS Phase 18 release archive assets and routes are wired');
