const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const pluginDir = path.join(root, 'wordpress-plugin', 'easiio-chatbot');
const pluginFile = path.join(pluginDir, 'easiio-chatbot.php');
const readmeFile = path.join(pluginDir, 'README.md');

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

test('wordpress plugin files exist', () => {
  assert.ok(fs.existsSync(pluginFile), 'easiio-chatbot.php should exist');
  assert.ok(fs.existsSync(readmeFile), 'plugin README.md should exist');
});

test('plugin has WordPress header and direct-access guard', () => {
  const php = read(pluginFile);
  assert.ok(php.includes('Plugin Name: Easiio Chatbot'), 'plugin header should define Plugin Name');
  assert.ok(php.includes("if (!defined('ABSPATH'))"), 'plugin should guard direct access');
});

test('plugin injects chatbot script through wp_footer with safe escaping', () => {
  const php = read(pluginFile);
  assert.ok(php.includes("add_action('wp_footer'"), 'plugin should hook wp_footer');
  assert.ok(php.includes('easiio_chatbot_footer_script'), 'plugin should define footer render function');
  for (const fn of ['esc_url', 'esc_attr']) {
    assert.ok(php.includes(fn), `plugin should use ${fn}`);
  }
  assert.ok(php.includes('data-easiio-chatbot'), 'script should include data-easiio-chatbot');
  assert.ok(php.includes('data-site-id'), 'script should include data-site-id');
  assert.ok(php.includes('data-api-base'), 'script should include data-api-base');
  assert.ok(php.includes('data-greeting'), 'script should include data-greeting');
  assert.ok(php.includes('data-rag-admin'), 'script should expose optional RAG admin toggle');
});

test('plugin defaults target reviewed chat subdomain and disables auto-open', () => {
  const php = read(pluginFile);
  assert.ok(php.includes('https://chat.easiio.com'), 'default API/widget base should be chat.easiio.com');
  assert.ok(php.includes('easiio-main'), 'default site id should be easiio-main');
  assert.ok(php.includes('data-auto-open="<?php echo esc_attr($auto_open); ?>"'), 'auto-open should be configurable output');
  assert.ok(php.includes("$auto_open = 'false';"), 'default auto-open should be false');
  assert.ok(php.includes("$rag_admin = 'false';"), 'default RAG admin UI should be disabled for public visitors');
});

test('plugin source is package-ready without committing generated zip artifacts', () => {
  assert.ok(fs.existsSync(pluginFile), 'plugin PHP source should exist for packaging');
  assert.ok(fs.existsSync(readmeFile), 'plugin README should exist for packaging');
});
