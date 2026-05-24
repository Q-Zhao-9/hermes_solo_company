const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const rendererPath = path.join(root, 'backend', 'docs_sitelet.py');
const appPath = path.join(root, 'backend', 'app.py');
const read = filePath => fs.readFileSync(filePath, 'utf8');

function test(name, fn) {
  try {
    fn();
    console.log(`PASS ${name}`);
  } catch (error) {
    console.error(`FAIL ${name}`);
    console.error(error.message);
    process.exitCode = 1;
  }
}

test('Phase 3 Sitelet renderer file exists', () => {
  assert.ok(fs.existsSync(rendererPath), 'backend/docs_sitelet.py should exist');
});

test('Phase 3 renderer builds Sitelet-compatible payloads', () => {
  const source = read(rendererPath);
  for (const expected of [
    'build_sitelet_preview_payload',
    'render_docs_space_html',
    'render_single_doc_html',
    'easiio-docs-sitelet-preview',
    'source": "easiio-docs-module"',
    'kind": "site"',
    '/assets/easiio-docs-preview.css',
    'requiresUploadApproval',
    'uploadBlocked'
  ]) {
    assert.ok(source.includes(expected), `docs_sitelet.py should include ${expected}`);
  }
});

test('Phase 3 app exposes preview and upload endpoints', () => {
  const app = read(appPath);
  for (const expected of [
    'docs_sitelet',
    '/api/docs/sitelet-preview',
    '/api/docs/sitelet-preview/upload',
    'confirmSiteletUpload',
    'SITELET_BASE_URL',
    'SITELET_API_TOKEN'
  ]) {
    assert.ok(app.includes(expected), `app.py should include ${expected}`);
  }
});
