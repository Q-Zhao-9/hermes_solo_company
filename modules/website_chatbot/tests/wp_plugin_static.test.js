const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const pluginDir = path.join(root, 'wordpress-plugin', 'easiio-chatbot');
const pluginFile = path.join(pluginDir, 'easiio-chatbot.php');
const readmeFile = path.join(pluginDir, 'README.md');
const packageFile = path.join(root, 'dist', 'easiio-chatbot-wordpress-plugin.zip');

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
  assert.ok(php.includes('data-auto-open="<?php echo esc_attr($options[\'auto_open\']); ?>"'), 'auto-open should be configurable output');
  assert.ok(php.includes('data-voice-enabled="<?php echo esc_attr($options[\'voice_enabled\']); ?>"'), 'voice playback should be configurable output');
  assert.ok(php.includes('data-voice-input-enabled="<?php echo esc_attr($options[\'voice_input_enabled\']); ?>"'), 'voice input should be configurable output');
  assert.ok(php.includes("'auto_open' => 'false'"), 'default auto-open should be false');
  assert.ok(php.includes("'rag_admin' => 'false'"), 'default RAG admin UI should be disabled for public visitors');
  assert.ok(php.includes("'lead_forms_enabled' => 'false'"), 'default lead forms should be disabled for factual chat');
  assert.ok(php.includes("'voice_enabled' => 'false'"), 'default voice playback should be disabled until reviewed');
  assert.ok(php.includes("'voice_input_enabled' => 'false'"), 'default voice input should be disabled until reviewed');
});

test('plugin exposes a WordPress settings page with sanitized options', () => {
  const php = read(pluginFile);
  assert.ok(php.includes('add_options_page'), 'plugin should register a Settings page');
  assert.ok(php.includes('register_setting'), 'plugin should register settings');
  assert.ok(php.includes('manage_options'), 'settings page should require manage_options');
  assert.ok(php.includes('easiio_chatbot_sanitize_options'), 'plugin should sanitize all saved options');
  for (const fn of ['esc_url_raw', 'sanitize_text_field', 'sanitize_textarea_field', 'sanitize_hex_color']) {
    assert.ok(php.includes(fn), `plugin should use ${fn}`);
  }
});

test('plugin includes backend health check AJAX without exposing secrets', () => {
  const php = read(pluginFile);
  assert.ok(php.includes('wp_ajax_easiio_chatbot_health_check'), 'plugin should register admin AJAX health check');
  assert.ok(php.includes('check_ajax_referer'), 'health check should verify nonce');
  assert.ok(php.includes('wp_remote_get'), 'health check should use server-side HTTP request');
  assert.ok(php.includes('wp_send_json_success'), 'health check should return sanitized success JSON');
  assert.ok(php.includes('wp_send_json_error'), 'health check should return sanitized error JSON');
});

test('plugin avoids secret-bearing settings and public secret output', () => {
  const php = read(pluginFile);
  const forbiddenSettings = [
    'api_key',
    'access_token',
    'webhook_url',
    'smtp_password',
    'brevo_api_key',
    'hubspot_private_app_token',
    'openai_api_key'
  ];
  for (const forbidden of forbiddenSettings) {
    assert.ok(!php.toLowerCase().includes(`name="${forbidden}"`), `plugin should not render secret field ${forbidden}`);
    assert.ok(!php.toLowerCase().includes(`'${forbidden}' =>`), `plugin defaults should not include secret ${forbidden}`);
  }
});

test('plugin README documents settings page and server-side secret boundary', () => {
  const readme = read(readmeFile);
  assert.ok(readme.includes('Settings → Easiio Chatbot'), 'README should document settings page');
  assert.ok(readme.includes('server-side only'), 'README should explain secrets stay server-side only');
  assert.ok(readme.includes('Health check'), 'README should document health check');
});

test('plugin source package is ready to zip without generated artifacts committed', () => {
  assert.ok(fs.existsSync(pluginDir), 'plugin source directory should exist');
  assert.ok(fs.existsSync(pluginFile), 'plugin PHP source should exist');
  assert.ok(!fs.existsSync(packageFile), 'generated plugin zip should stay out of the source repo');
  const php = read(pluginFile);
  assert.ok(php.length > 500, 'plugin PHP source should not be empty');
});

test('plugin exposes safe optional voice-call settings', () => {
  const php = read(pluginFile);
  for (const expected of [
    "'voice_call_enabled' => 'false'",
    "'voice_call_label' => 'Call AI Assistant'",
    "'voice_call_api_base' => ''",
    "'voice_call_consent_text' =>",
    'data-voice-call-enabled="<?php echo esc_attr($options[\'voice_call_enabled\']); ?>"',
    'data-voice-call-label="<?php echo esc_attr($options[\'voice_call_label\']); ?>"',
    'data-voice-call-api-base="<?php echo esc_url($options[\'voice_call_api_base\']); ?>"',
    'data-voice-call-consent-text="<?php echo esc_attr($options[\'voice_call_consent_text\']); ?>"',
    'Enable browser AI voice call',
    'Voice-call API base URL'
  ]) {
    assert.ok(php.includes(expected), `plugin should include ${expected}`);
  }
});
