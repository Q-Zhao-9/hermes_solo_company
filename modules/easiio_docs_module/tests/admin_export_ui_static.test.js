const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const adminHtmlPath = path.join(root, 'frontend', 'admin.html');
const adminJsPath = path.join(root, 'frontend', 'admin.js');
const adminCssPath = path.join(root, 'frontend', 'admin.css');
const appPath = path.join(root, 'backend', 'app.py');

for (const file of [adminHtmlPath, adminJsPath, adminCssPath]) {
  assert(fs.existsSync(file), `${path.basename(file)} should exist for Phase 7 admin/export UI`);
}

const html = fs.readFileSync(adminHtmlPath, 'utf8');
const js = fs.readFileSync(adminJsPath, 'utf8');
const css = fs.readFileSync(adminCssPath, 'utf8');
const app = fs.readFileSync(appPath, 'utf8');

for (const expected of [
  'Easiio Docs Admin',
  'data-easiio-docs-admin',
  'admin.js',
  'admin.css',
  'site_id',
  'target',
]) {
  assert(html.includes(expected), `admin.html should include ${expected}`);
}

for (const expected of [
  'EasiioDocsAdmin',
  '/api/docs/export/preview',
  '/api/docs/export/package',
  'confirmExportPackage',
  'requiresExportApproval',
  'packageBlocked',
  'downloadPackage',
  'ownerToken',
  'Authorization',
  'docs-admin-owner-token',
  'renderFilePreview',
  'nextjs-mdx',
  'docusaurus',
  'mkdocs',
  'hugo',
  'vitepress',
  'static-html',
]) {
  assert(js.includes(expected), `admin.js should include ${expected}`);
}

for (const expected of [
  '.easiio-docs-admin',
  '.easiio-docs-admin-panel',
  '.easiio-docs-admin-files',
  '.easiio-docs-admin-actions',
  '.easiio-docs-admin-warning',
]) {
  assert(css.includes(expected), `admin.css should include ${expected}`);
}

assert(app.includes('/docs/admin.html'), 'app.py should serve /docs/admin.html');
assert(app.includes('/docs/admin.js'), 'app.py should serve /docs/admin.js');
assert(app.includes('/docs/admin.css'), 'app.py should serve /docs/admin.css');
assert(app.includes('EASIIO_DOCS_OWNER_TOKEN'), 'app.py should support Phase 8 owner-token protection');
assert(app.includes('require_owner_auth'), 'app.py should enforce owner auth on protected endpoints');
assert(app.includes('17-release-dashboard'), 'health phase should mention Phase 9 while preserving Phase 8 auth behavior');

console.log('PASS Phase 9 admin/export UI auth assets and routes are wired');
