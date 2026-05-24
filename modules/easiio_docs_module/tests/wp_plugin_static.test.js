const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const pluginDir = path.join(root, 'wordpress-plugin', 'easiio-docs');
const pluginFile = path.join(pluginDir, 'easiio-docs.php');
const readmeFile = path.join(pluginDir, 'README.md');
const appPath = path.join(root, 'backend', 'app.py');
const wpPath = path.join(root, 'backend', 'docs_wordpress.py');

function read(filePath) { return fs.readFileSync(filePath, 'utf8'); }
function test(name, fn) {
  try { fn(); console.log(`PASS ${name}`); }
  catch (error) { console.error(`FAIL ${name}`); console.error(error.message); process.exitCode = 1; }
}

test('wordpress docs plugin files exist', () => {
  assert.ok(fs.existsSync(pluginFile), 'easiio-docs.php should exist');
  assert.ok(fs.existsSync(readmeFile), 'plugin README.md should exist');
});

test('plugin has WordPress header guard and shortcode', () => {
  const php = read(pluginFile);
  for (const expected of [
    'Plugin Name: Easiio Docs',
    "if (!defined('ABSPATH'))",
    "add_shortcode('easiio_docs'",
    'easiio_docs_shortcode',
    'shortcode_atts'
  ]) assert.ok(php.includes(expected), `plugin should include ${expected}`);
});

test('plugin renders escaped docs widget embed attributes', () => {
  const php = read(pluginFile);
  for (const expected of [
    'data-easiio-docs',
    'data-api-base',
    'data-site-id',
    'data-mode',
    'data-root-selector',
    'data-target-filter',
    'data-credential-mode',
    'data-auth-token',
    'esc_attr',
    'esc_url'
  ]) assert.ok(php.includes(expected), `plugin should include ${expected}`);
});

test('plugin supports login-protected docs and admin mode', () => {
  const php = read(pluginFile);
  for (const expected of ['require_login', 'is_user_logged_in', 'wp_get_current_user', 'mode', 'admin', 'credential_mode']) {
    assert.ok(php.includes(expected), `plugin should include ${expected}`);
  }
});

test('backend has WordPress draft-plan and execution helpers', () => {
  assert.ok(fs.existsSync(wpPath), 'backend/docs_wordpress.py should exist');
  const wp = read(wpPath);
  for (const expected of [
    'build_wordpress_shortcode_response',
    'build_wordpress_draft_plan',
    'easiio-docs-wordpress-draft-plan',
    'mcp_easiio_wp_create_draft_post',
    'mcp_easiio_wp_get_post',
    'publishBlocked',
    'requiresHumanApproval'
  ]) assert.ok(wp.includes(expected), `docs_wordpress.py should include ${expected}`);
  const app = read(appPath);
  for (const expected of ['/api/docs/wordpress/shortcode', '/api/docs/wordpress/draft-plan', '/api/docs/wordpress/draft-execution']) {
    assert.ok(app.includes(expected), `app.py should include ${expected}`);
  }
});

test('plugin source is package-ready without committing generated zip artifacts', () => {
  assert.ok(fs.existsSync(pluginFile), 'easiio-docs.php should exist for packaging');
  assert.ok(fs.existsSync(readmeFile), 'plugin README.md should exist for packaging');
});
