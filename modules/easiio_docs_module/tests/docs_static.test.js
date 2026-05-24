const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const jsPath = path.join(root, 'frontend', 'docs.js');
const cssPath = path.join(root, 'frontend', 'docs.css');
const demoPath = path.join(root, 'frontend', 'demo.html');

function read(filePath) {
  return fs.readFileSync(filePath, 'utf8');
}

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

test('docs frontend files exist', () => {
  assert.ok(fs.existsSync(jsPath), 'frontend/docs.js should exist');
  assert.ok(fs.existsSync(cssPath), 'frontend/docs.css should exist');
  assert.ok(fs.existsSync(demoPath), 'frontend/demo.html should exist');
});

test('docs widget reads embed configuration and exposes controller', () => {
  const js = read(jsPath);
  for (const expected of ['data-easiio-docs', 'apiBase', 'siteId', 'mode', 'rootSelector', 'window.EasiioDocs']) {
    assert.ok(js.includes(expected), `docs.js should include ${expected}`);
  }
  for (const method of ['mount', 'loadDocs', 'openDoc', 'showEditor', 'saveDoc', 'deleteDoc', 'loadSpace']) {
    assert.match(js, new RegExp(`${method}\\s*[:(]`), `controller should expose or define ${method}`);
  }
});

test('docs widget calls site-scoped docs backend APIs', () => {
  const js = read(jsPath);
  for (const expected of [
    '/api/docs/docs',
    '/api/docs/doc',
    '/api/docs/doc/delete',
    '/api/docs/space',
    'site_id=${encodeURIComponent(state.config.siteId',
    'data-mode="admin"',
    'content_format',
    'framework_targets',
    'rag_enabled'
  ]) {
    assert.ok(js.includes(expected), `docs.js should include ${expected}`);
  }
});

test('docs widget supports public reader, admin editor, auth forwarding, and framework filters', () => {
  const js = read(jsPath);
  for (const expected of [
    'credentialMode',
    'authToken',
    'getAuthHeaders',
    'Authorization',
    'Bearer ${state.config.authToken}',
    'credentials: state.config.credentialMode',
    'loginRequired',
    'targetFilter',
    'visibility',
    'contentFormat'
  ]) {
    assert.ok(js.includes(expected), `docs.js should include ${expected}`);
  }
});

test('docs widget renders safe Markdown/MDX-ish content and never injects unsanitized HTML except html format', () => {
  const js = read(jsPath);
  for (const expected of ['renderContent', 'escapeHtml', "format === 'html'", 'replace(/^# (.*)$/gm', 'replace(/^- (.*)$/gm']) {
    assert.ok(js.includes(expected), `docs.js should include ${expected}`);
  }
});

test('docs CSS contains public/admin responsive styles', () => {
  const css = read(cssPath);
  for (const expected of [
    '.easiio-docs',
    '.easiio-docs-search',
    '.easiio-docs-list',
    '.easiio-docs-editor',
    '.easiio-docs-content',
    '.easiio-docs-targets',
    '@media'
  ]) {
    assert.ok(css.includes(expected), `docs.css should include ${expected}`);
  }
});

test('demo page embeds docs widget in local backend mode', () => {
  const html = read(demoPath);
  assert.ok(html.includes('data-easiio-docs'), 'demo should include data-easiio-docs script');
  assert.ok(html.includes('data-api-base="http://localhost:8110"'), 'demo should point at local docs backend');
  assert.ok(html.includes('docs.js'), 'demo should load docs.js');
  assert.ok(html.includes('docs.css'), 'demo should load docs.css');
});
