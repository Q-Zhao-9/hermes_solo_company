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
