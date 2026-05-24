const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const app = fs.readFileSync(path.join(root, 'backend', 'app.py'), 'utf8');
const adminHtml = fs.readFileSync(path.join(root, 'frontend', 'admin.html'), 'utf8');
const adminJs = fs.readFileSync(path.join(root, 'frontend', 'admin.js'), 'utf8');
const importersPath = path.join(root, 'backend', 'docs_importers.py');

assert(fs.existsSync(importersPath), 'Phase 10 should add backend/docs_importers.py');
const importers = fs.readFileSync(importersPath, 'utf8');

[
  'build_import_preview',
  'execute_import',
  'build_portable_bundle_preview',
  'build_portable_bundle_package',
  'confirmImport',
  'confirmBundlePackage',
  'easiio-docs-import-preview',
  'easiio-docs-portable-bundle'
].forEach((expected) => assert(importers.includes(expected), `docs_importers.py should include ${expected}`));

[
  '/api/docs/import/preview',
  '/api/docs/import/execute',
  '/api/docs/bundle/preview',
  '/api/docs/bundle/package',
  'docs_importers',
  '17-release-dashboard'
].forEach((expected) => assert(app.includes(expected), `app.py should include ${expected}`));

[
  'docs-admin-import-source-format',
  'docs-admin-import-files',
  'docs-admin-import-preview',
  'docs-admin-import-execute',
  'docs-admin-bundle-preview',
  'docs-admin-bundle-package'
].forEach((expected) => assert(adminHtml.includes(expected), `admin.html should include ${expected}`));

[
  'previewImport',
  'executeImport',
  'previewBundle',
  'packageBundle',
  'confirmImport',
  'confirmBundlePackage',
  '/api/docs/import/preview',
  '/api/docs/import/execute',
  '/api/docs/bundle/preview',
  '/api/docs/bundle/package'
].forEach((expected) => assert(adminJs.includes(expected), `admin.js should include ${expected}`));

console.log('PASS Phase 10 import/export management assets and routes are wired');
