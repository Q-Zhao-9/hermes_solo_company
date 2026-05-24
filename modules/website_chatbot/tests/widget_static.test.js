const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const widgetPath = path.join(root, 'widget', 'widget.js');
const cssPath = path.join(root, 'widget', 'widget.css');
const demoPath = path.join(root, 'widget', 'demo.html');

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

test('widget files exist', () => {
  assert.ok(fs.existsSync(widgetPath), 'widget/widget.js should exist');
  assert.ok(fs.existsSync(cssPath), 'widget/widget.css should exist');
  assert.ok(fs.existsSync(demoPath), 'widget/demo.html should exist');
});

test('widget exposes EasiioChatbot controller API', () => {
  const js = read(widgetPath);
  assert.match(js, /window\.EasiioChatbot\s*=/, 'should assign window.EasiioChatbot');
  for (const method of ['set', 'show', 'open', 'close', 'minimize', 'openKnowledge', 'closeKnowledge', 'loadRagContentList']) {
    assert.match(js, new RegExp(`${method}\\s*[:(]`), `controller should expose ${method}`);
  }
});

test('widget implements CRM-ready mock-mode UI hooks', () => {
  const js = read(widgetPath);
  for (const id of [
    'easiio-chatbot-root',
    'easiio-chatbot-capsule',
    'easiio-chatbot-launcher',
    'easiio-chatbot-unread',
    'easiio-chatbot-panel',
    'easiio-chatbot-greeting',
    'easiio-chatbot-lead-form'
  ]) {
    assert.ok(js.includes(id), `widget should render #${id}`);
  }
  assert.ok(js.includes('apiBase') && js.includes('mock'), 'widget should support mock apiBase');
  assert.ok(js.includes('Book demo') && js.includes('Pricing') && js.includes('Contact sales'), 'widget should include quick actions');
});

test('widget caches visitor contact and conversation per site in localStorage', () => {
  const js = read(widgetPath);
  for (const expected of [
    'siteStorageKey',
    'loadCachedState',
    'saveCachedVisitor',
    'saveCachedMessage',
    'easiio_chatbot_cache_v1',
    'content: getWebsiteTextSnapshot()',
    'localStorage.setItem(siteStorageKey()'
  ]) {
    assert.ok(js.includes(expected), `widget should include ${expected}`);
  }
});

test('widget can disable automatic lead prompts while quick-action buttons open the lead form', () => {
  const js = read(widgetPath);
  for (const expected of [
    'leadFormsEnabled',
    "ds.leadFormsEnabled === 'true'",
    'onQuickAction',
    "showLeadForm(message, 'quick_action')",
    'button.addEventListener(\'click\', () => onQuickAction(button.dataset.message))',
    'showLeadForm',
    'clearLeadFormReminder'
  ]) {
    assert.ok(js.includes(expected), `widget should include ${expected}`);
  }
  assert.ok(!js.includes('state.questionCount >= 3'), 'question-count prompt should be disabled for now');
  assert.ok(js.includes('if (!state.config.leadFormsEnabled && reason !== \'quick_action\') return;'), 'automatic prompts should be gated but quick actions can open the form');
});

test('quick actions can reopen the lead form after it was dismissed', () => {
  const js = read(widgetPath);
  assert.ok(js.includes('form.dataset.dismissedAt = new Date().toISOString();'), 'dismiss should record dismissal state');
  assert.ok(js.includes('delete form.dataset.dismissedAt;'), 'showLeadForm should clear previous dismissal state');
  assert.ok(js.includes("form.removeAttribute('hidden');"), 'showLeadForm should explicitly remove hidden attribute when reopening');
  assert.ok(js.includes('form.hidden = false;'), 'showLeadForm should reset hidden property when reopening');
  assert.ok(js.includes("if (reason !== 'quick_action' && hasContactInfo()) return;"), 'quick actions should show the form even when cached contact info exists');
  const showLeadFormBody = js.match(/function showLeadForm\(message, reason\) \{([\s\S]*?)\n  \}/)[1];
  assert.ok(!showLeadFormBody.includes('if (hasContactInfo()) return;'), 'quick actions must not be blocked by cached visitor email/phone');
});

test('lead form defaults to no phone field and includes configurable message textarea', () => {
  const js = read(widgetPath);
  const css = read(cssPath);
  assert.ok(js.includes('DEFAULT_LEAD_FORM_CONFIG'), 'widget should define a default lead form config');
  assert.ok(js.includes("name: 'message'"), 'default lead form should include a message field');
  assert.ok(js.includes("type: 'textarea'"), 'message field should render as a textarea');
  assert.ok(!js.includes('name="phone" autocomplete="tel"'), 'default rendered lead form should not hard-code a phone input');
  assert.ok(js.includes('renderLeadFormFields'), 'widget should render configurable form fields');
  assert.ok(js.includes('loadLeadFormConfig'), 'widget should load backend form config');
  assert.ok(js.includes('/api/chat/form-config'), 'widget should call the backend form config API');
  assert.ok(js.includes('data-lead-form-config'), 'widget should support embedded JSON form config');
  assert.ok(css.includes('.easiio-chatbot-lead-form textarea'), 'CSS should style lead form textarea fields');
});

test('widget includes optional per-site RAG admin interface', () => {
  const js = read(widgetPath);
  const css = read(cssPath);
  for (const expected of [
    'ragAdminEnabled',
    'data-content-id',
    'easiio-chatbot-rag-admin',
    'easiio-chatbot-rag-form',
    'Website knowledge',
    '/api/rag/content',
    '/api/rag/content/delete',
    'site_id=${encodeURIComponent(state.config.siteId'
  ]) {
    assert.ok(js.includes(expected), `widget should include ${expected}`);
  }
  for (const expected of ['.easiio-chatbot-rag-admin', '.easiio-chatbot-rag-list', '.easiio-chatbot-rag-delete']) {
    assert.ok(css.includes(expected), `CSS should include ${expected}`);
  }
});

test('widget CSS contains responsive launcher and panel rules', () => {
  const css = read(cssPath);
  for (const selector of [
    '#easiio-chatbot-capsule',
    '#easiio-chatbot-launcher',
    '#easiio-chatbot-panel',
    '#easiio-chatbot-unread',
    '#easiio-chatbot-greeting',
    '@media'
  ]) {
    assert.ok(css.includes(selector), `CSS should contain ${selector}`);
  }
});

test('demo page loads widget in backend mode with data attributes', () => {
  const html = read(demoPath);
  assert.ok(html.includes('data-easiio-chatbot'), 'demo should include data-easiio-chatbot script');
  assert.ok(html.includes('data-api-base="http://localhost:8099"'), 'demo should use local backend mode');
  assert.ok(html.includes('widget.js'), 'demo should load widget.js');
});
