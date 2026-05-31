const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const widgetPath = path.join(root, 'widget', 'widget.js');
const cssPath = path.join(root, 'widget', 'widget.css');
const demoPath = path.join(root, 'widget', 'demo.html');
const aiSoloVoiceDemoPath = path.join(root, 'widget', 'ai-solo-company-voice-chatbot.html');

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
  assert.ok(fs.existsSync(aiSoloVoiceDemoPath), 'widget/ai-solo-company-voice-chatbot.html should exist');
});

test('widget exposes EasiioChatbot controller API', () => {
  const js = read(widgetPath);
  assert.match(js, /window\.EasiioChatbot\s*=/, 'should assign window.EasiioChatbot');
  for (const method of ['set', 'show', 'open', 'startVoiceCall', 'close', 'minimize', 'openKnowledge', 'closeKnowledge', 'loadRagContentList']) {
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

test('widget includes helpful feedback controls for RAG answers', () => {
  const js = read(widgetPath);
  const css = read(cssPath);
  for (const expected of [
    'renderAnswerFeedback',
    'sendAnswerFeedback',
    '/api/rag/feedback',
    'data-rag-feedback',
    "rating: target.dataset.ragFeedback",
    'answer_log_id'
  ]) {
    assert.ok(js.includes(expected), `widget should include ${expected}`);
  }
  for (const expected of ['.easiio-chatbot-feedback', '.easiio-chatbot-feedback button']) {
    assert.ok(css.includes(expected), `CSS should include ${expected}`);
  }
});

test('widget includes optional voice playback for bot replies', () => {
  const js = read(widgetPath);
  const css = read(cssPath);
  const html = read(demoPath);
  for (const expected of [
    'voiceEnabled',
    "ds.voiceEnabled === 'true'",
    'renderVoicePlayback',
    'requestVoiceAudio',
    '/api/chat/voice',
    'data-voice-playback',
    'new Audio(audioUrl)',
    'audio_url',
    'resolveApiUrl',
    'applyRemoteWidgetConfig',
    'remoteWidgetConfigEnabled',
    'data.form_config.widget_config',
    'voice_enabled',
    'voice_label',
    'voice_autoplay',
    'voice_format'
  ]) {
    assert.ok(js.includes(expected), `widget should include ${expected}`);
  }
  for (const expected of ['.easiio-chatbot-voice', '.easiio-chatbot-voice button', '.easiio-chatbot-voice-status']) {
    assert.ok(css.includes(expected), `CSS should include ${expected}`);
  }
  assert.ok(html.includes('data-voice-enabled="true"'), 'demo should enable optional voice playback for testing');
});

test('widget includes optional browser voice input for visitor questions', () => {
  const js = read(widgetPath);
  const css = read(cssPath);
  const html = read(demoPath);
  for (const expected of [
    'voiceInputEnabled',
    "ds.voiceInputEnabled === 'true'",
    'renderVoiceInputControl',
    'startVoiceInput',
    'SpeechRecognition',
    'webkitSpeechRecognition',
    'data-voice-input',
    'voice_input_enabled',
    'voice_input_label',
    'voice_input_language'
  ]) {
    assert.ok(js.includes(expected), `widget should include ${expected}`);
  }
  for (const expected of ['.easiio-chatbot-voice-input', '.easiio-chatbot-voice-input.is-listening']) {
    assert.ok(css.includes(expected), `CSS should contain ${expected}`);
  }
  assert.ok(html.includes('data-voice-input-enabled="true"'), 'demo should enable optional voice input for testing');
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
  assert.ok(css.includes('width: min(460px, calc(100vw - 32px));'), 'desktop panel should be wide enough for voice/chat controls');
  assert.ok(css.includes('overflow-wrap: anywhere;'), 'bot messages should not be clipped by long text');
  assert.ok(css.includes('flex-wrap: wrap;'), 'composer/actions should wrap instead of cutting off buttons');
});

test('demo page loads widget in backend mode with data attributes', () => {
  const html = read(demoPath);
  assert.ok(html.includes('data-easiio-chatbot'), 'demo should include data-easiio-chatbot script');
  assert.ok(html.includes('data-api-base="http://localhost:8099"'), 'demo should use local backend mode');
  assert.ok(html.includes('widget.js'), 'demo should load widget.js');
});

test('widget includes optional browser AI voice-call flow', () => {
  const js = read(widgetPath);
  const css = read(cssPath);
  const html = read(demoPath);
  for (const expected of [
    'voiceCallEnabled',
    "ds.voiceCallEnabled === 'true'",
    'voiceCallApiBase',
    'voiceCallLabel',
    'voiceCallConsentText',
    'renderVoiceCallControl',
    'startVoiceCallSession',
    'startVoiceCallRecording',
    'stopVoiceCallRecording',
    'submitVoiceCallAudioTurn',
    'endVoiceCallSession',
    '/api/voice-call/session',
    '/api/voice-call/browser/audio-turn',
    '/api/voice-call/end',
    'data-voice-call-start',
    'data-voice-call-record',
    'data-voice-call-end',
    'MediaRecorder',
    'getUserMedia'
  ]) {
    assert.ok(js.includes(expected), `widget should include ${expected}`);
  }
  for (const expected of ['.easiio-chatbot-voice-call', '.easiio-chatbot-voice-call-panel', '.easiio-chatbot-voice-call-status']) {
    assert.ok(css.includes(expected), `CSS should contain ${expected}`);
  }
  assert.ok(html.includes('data-voice-call-enabled="true"'), 'demo should enable optional voice call for testing');
});

test('AI Solo Company demo loads chatbot with public Hermes Proxy voice-call button', () => {
  const js = read(widgetPath);
  const css = read(cssPath);
  const html = read(aiSoloVoiceDemoPath);
  assert.ok(html.includes('data-ai-solo-voice-chatbot-demo'), 'AI Solo demo should have a stable marker');
  assert.ok(html.includes('data-site-id="ai-solo-company"'), 'AI Solo demo should use the AI Solo Company site id');
  assert.ok(html.includes('data-voice-call-enabled="true"'), 'AI Solo demo should enable voice calls');
  assert.ok(html.includes('data-voice-call-label="Start voice call"'), 'AI Solo demo should use a clear voice-call CTA');
  assert.ok(html.includes('data-remote-widget-config="false"'), 'AI Solo demo should preserve embedded voice-call settings instead of remote defaults');
  assert.ok(html.includes('data-voice-call-api-base="https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-voice-api"'), 'AI Solo demo should point voice calls to the public Hermes Proxy voice API');
  assert.ok(html.includes('data-api-base="https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-chatbot-api"'), 'AI Solo demo should point text chat to the public Hermes Proxy chatbot API');
  assert.ok(html.includes('Ask by chat, speak a short question, or start a voice call'), 'AI Solo demo should explain the combined interface');
  assert.ok(js.includes('quickActions.appendChild(quickButton(state.config.voiceCallLabel || \'Call AI Assistant\', startVoiceCallSession))'), 'launcher quick actions should include a direct voice-call button');
  assert.ok(js.includes('function onPanelClick(event)'), 'panel should use delegated click handling for voice-call buttons');
  assert.ok(js.includes('function attachDocumentShortcuts()'), 'widget should attach document-level demo shortcuts');
  assert.ok(html.includes('data-easiio-chatbot-start-voice-call'), 'AI Solo demo hero CTA should use widget-managed start shortcut');
  assert.ok(!html.includes('onclick="window.EasiioChatbot'), 'AI Solo demo should not rely on inline onclick handlers that can no-op before widget load');
  assert.ok(!html.includes('    async\n    src="./widget.js'), 'AI Solo demo should not async-load the widget for this interaction-critical page');
  assert.ok(js.includes('if (button.dataset.message) {'), 'voice-call buttons should not be treated as text quick actions');
  assert.ok(js.includes("const text = clone.innerText || clone.textContent || '';"), 'website text snapshot should not break voice-call start when innerText is unavailable');
  assert.ok(html.includes('widget.js?v=20260531-width-rag-fix'), 'AI Solo demo should cache-bust the fixed widget script');
  assert.ok(css.includes('.easiio-chatbot-voice-call-trigger'), 'CSS should style the voice-call trigger');
});
