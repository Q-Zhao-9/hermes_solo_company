#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');
const jsPath = path.join(root, 'admin', 'chatbot-customizer.js');
const cssPath = path.join(root, 'admin', 'chatbot-customizer.css');

assert.ok(fs.existsSync(jsPath), 'admin/chatbot-customizer.js missing');
assert.ok(fs.existsSync(cssPath), 'admin/chatbot-customizer.css missing');

const js = fs.readFileSync(jsPath, 'utf8');
const css = fs.readFileSync(cssPath, 'utf8');

[
  'window.EasiioChatbotCustomizer',
  'data-easiio-chatbot-customizer',
  'data-site-id',
  'data-api-base',
  '/api/chat/form-config',
  '/api/rag/content',
  '/api/rag/content/delete',
  '/api/crm-connectors/config',
  'loadCrmConnectors',
  'saveCrmConnectors',
  'HubSpot',
  'Google Sheets',
  'token_env',
  'webhook_url_env',
  'access_token',
  'webhook_url',
  'loadFormConfig',
  'saveFormConfig',
  'addFormField',
  'removeFormField',
  'loadKnowledgeBase',
  'saveKnowledgeItem',
  'deleteKnowledgeItem',
  'renderPreview',
  'textarea',
  'message',
  'phone'
].forEach(token => assert.ok(js.includes(token), `${token} missing from customizer JS`));

assert.ok(/fields\s*:\s*\[[\s\S]*name:\s*['"]name['"][\s\S]*name:\s*['"]email['"][\s\S]*name:\s*['"]company['"][\s\S]*name:\s*['"]message['"]/.test(js), 'default fields should include name/email/company/message');
assert.ok(!/name:\s*['"]phone['"]/.test(js), 'phone should not be a default lead form field');
assert.ok(/credentials\s*:\s*['"]same-origin['"]/.test(js), 'admin module should use same-origin credentials by default');
assert.ok(/path\.startswith\(\"\/api\/email-agent\/\"\) or path\.startswith\(\"\/api\/crm-connectors\/\"\)[\s\S]*_proxy_email_agent\(\)/.test(fs.readFileSync(path.join(root, 'backend', 'site_gateway.py'), 'utf8')), 'CRM connector admin API must be admin-protected in site gateway');
assert.ok(!/name:\s*['"]access_token['"]/.test(js), 'admin UI must not collect raw HubSpot access tokens');
assert.ok(!/name:\s*['"]webhook_url['"]/.test(js), 'admin UI must not collect raw Google Sheets webhook URLs');

[
  '.easiio-chatbot-customizer',
  '.chatbot-customizer-grid',
  '.chatbot-field-row',
  '.chatbot-kb-list',
  '.chatbot-preview-form',
  '.chatbot-status',
  'box-sizing: border-box',
  'repeat(auto-fit, minmax(140px, 1fr))',
  '@media (max-width: 1200px)',
  'overflow: hidden'
].forEach(token => assert.ok(css.includes(token), `${token} missing from customizer CSS`));

console.log('PASS chatbot customizer admin module static checks');
