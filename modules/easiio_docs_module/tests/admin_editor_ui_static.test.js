const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const adminHtmlPath = path.join(root, 'frontend', 'admin.html');
const adminJsPath = path.join(root, 'frontend', 'admin.js');
const adminCssPath = path.join(root, 'frontend', 'admin.css');
const appPath = path.join(root, 'backend', 'app.py');

const html = fs.readFileSync(adminHtmlPath, 'utf8');
const js = fs.readFileSync(adminJsPath, 'utf8');
const css = fs.readFileSync(adminCssPath, 'utf8');
const app = fs.readFileSync(appPath, 'utf8');

for (const expected of [
  'Docs editor',
  'docs-admin-editor-form',
  'docs-admin-doc-list',
  'docs-admin-load-docs',
  'docs-admin-save-doc',
  'docs-admin-delete-doc',
  'docs-admin-revisions',
  'docs-admin-content',
  'docs-admin-framework-targets',
  'docs-admin-rag-enabled',
]) {
  assert(html.includes(expected), `admin.html should include Phase 9 editor marker ${expected}`);
}

for (const expected of [
  'loadDocs',
  'editDoc',
  'saveDoc',
  'deleteDoc',
  'loadRevisions',
  'collectEditorPayload',
  'populateEditor',
  'renderDocList',
  'renderRevisions',
  '/api/docs/docs',
  '/api/docs/doc',
  '/api/docs/doc/delete',
  '/api/docs/revisions',
  'changed_by',
  'framework_targets',
  'rag_enabled',
]) {
  assert(js.includes(expected), `admin.js should include Phase 9 editor behavior ${expected}`);
}

for (const expected of [
  '.easiio-docs-admin-editor',
  '.easiio-docs-admin-doc-list',
  '.easiio-docs-admin-form-grid',
  '.easiio-docs-admin-editor textarea',
  '.easiio-docs-admin-revisions',
]) {
  assert(css.includes(expected), `admin.css should include Phase 9 editor style ${expected}`);
}

assert(app.includes('17-release-dashboard'), 'health phase should mention Phase 9 admin editor');
console.log('PASS Phase 9 admin editor UI assets are wired');
