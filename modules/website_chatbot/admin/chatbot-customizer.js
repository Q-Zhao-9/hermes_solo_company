(() => {
  // Embed with data-easiio-chatbot-customizer, data-site-id, data-api-base, and data-root-selector.
  // The default field set intentionally excludes phone and uses a required message textarea.
  const DEFAULT_FORM_CONFIG = {
    title: 'Where should we follow up?',
    help_text: 'Optional — close this and keep chatting if you are not ready. Phone is not collected by default.',
    submit_label: 'Send to Easiio',
    fields: [
      { name: 'name', label: 'Name', type: 'text', required: false, autocomplete: 'name' },
      { name: 'email', label: 'Work email', type: 'email', required: true, autocomplete: 'email' },
      { name: 'company', label: 'Company', type: 'text', required: false, autocomplete: 'organization' },
      { name: 'message', label: 'Message', type: 'textarea', required: true, autocomplete: '' }
    ]
  };

  const DEFAULT_WIDGET_CONFIG = {
    voice_enabled: false,
    voice_label: 'Listen',
    voice_autoplay: false,
    voice: '',
    voice_format: 'mp3',
    voice_input_enabled: false,
    voice_input_label: 'Speak',
    voice_input_language: 'auto',
    voice_call_enabled: false,
    voice_call_label: 'Call AI Assistant',
    voice_call_api_base: '',
    voice_call_consent_text: 'This AI assistant may transcribe your voice to answer your question and follow up if you share contact details.'
  };

  const DEFAULT_NOTIFICATION_EMAIL_CONFIG = {
    enabled: false,
    provider: 'brevo',
    send_welcome_email: true,
    send_owner_notification: true,
    owner_recipients: [],
    from_email: '',
    from_name: 'Easiio Website Assistant',
    welcome_subject: 'Welcome to {{site_name}}',
    welcome_body: 'Hi {{name}},\n\nThanks for contacting {{site_name}}. We received your information and will follow up soon.\n\nYour message:\n{{message}}\n\nBest,\n{{site_name}} Team',
    owner_subject: 'New website lead from {{site_name}}: {{name}}',
    owner_body: 'A new website lead was captured.\n\nName: {{name}}\nEmail: {{email}}\nPhone: {{phone}}\nCompany: {{company}}\nSite ID: {{site_id}}\nPage: {{page_url}}\nLead score: {{lead_score}}\n\nMessage:\n{{message}}'
  };

  const FIELD_TYPES = ['text', 'email', 'textarea'];
  const EMAIL_PROVIDERS = ['brevo', 'smtp', 'outbox'];
  const VOICE_FORMATS = ['mp3', 'wav', 'opus'];
  const stateByRoot = new WeakMap();

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[char]));
  }

  function apiUrl(apiBase, path) {
    const cleanPath = String(path || '').replace(/^\/+/, '');
    if (!apiBase || apiBase === '.') return cleanPath;
    return `${apiBase.replace(/\/$/, '')}/${cleanPath}`;
  }

  function status(root, message, tone = '') {
    const element = root.querySelector('[data-chatbot-status]');
    if (!element) return;
    element.textContent = message || '';
    element.dataset.tone = tone;
  }

  function normalizeField(field, index) {
    const name = String(field && field.name || `field_${index + 1}`).trim().toLowerCase().replace(/[^a-z0-9_]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 40) || `field_${index + 1}`;
    const type = FIELD_TYPES.includes(field && field.type) ? field.type : 'text';
    return {
      name,
      label: String(field && field.label || name.replace(/_/g, ' ')).trim().slice(0, 80),
      type,
      required: Boolean(field && field.required),
      autocomplete: String(field && field.autocomplete || '').trim().slice(0, 80)
    };
  }

  function normalizeConfig(config) {
    const source = config && typeof config === 'object' ? config : DEFAULT_FORM_CONFIG;
    const fields = Array.isArray(source.fields) ? source.fields.map(normalizeField).filter((field) => field.name) : [];
    return {
      title: String(source.title || DEFAULT_FORM_CONFIG.title).slice(0, 120),
      help_text: String(source.help_text || DEFAULT_FORM_CONFIG.help_text).slice(0, 240),
      submit_label: String(source.submit_label || DEFAULT_FORM_CONFIG.submit_label).slice(0, 80),
      fields: fields.length ? fields : DEFAULT_FORM_CONFIG.fields.map(normalizeField)
    };
  }

  function normalizeWidgetConfig(config) {
    const source = config && typeof config === 'object' ? config : DEFAULT_WIDGET_CONFIG;
    const voiceFormat = VOICE_FORMATS.includes(String(source.voice_format || source.voiceFormat || '').toLowerCase())
      ? String(source.voice_format || source.voiceFormat).toLowerCase()
      : DEFAULT_WIDGET_CONFIG.voice_format;
    return {
      voice_enabled: Boolean(source.voice_enabled || source.voiceEnabled),
      voice_label: String(source.voice_label || source.voiceLabel || DEFAULT_WIDGET_CONFIG.voice_label).slice(0, 80),
      voice_autoplay: Boolean(source.voice_autoplay || source.voiceAutoplay),
      voice: String(source.voice || '').slice(0, 80),
      voice_format: voiceFormat,
      voice_input_enabled: Boolean(source.voice_input_enabled || source.voiceInputEnabled),
      voice_input_label: String(source.voice_input_label || source.voiceInputLabel || DEFAULT_WIDGET_CONFIG.voice_input_label).slice(0, 80),
      voice_input_language: String(source.voice_input_language || source.voiceInputLanguage || DEFAULT_WIDGET_CONFIG.voice_input_language).slice(0, 32),
      voice_call_enabled: Boolean(source.voice_call_enabled || source.voiceCallEnabled),
      voice_call_label: String(source.voice_call_label || source.voiceCallLabel || DEFAULT_WIDGET_CONFIG.voice_call_label).slice(0, 80),
      voice_call_api_base: String(source.voice_call_api_base || source.voiceCallApiBase || DEFAULT_WIDGET_CONFIG.voice_call_api_base).slice(0, 500),
      voice_call_consent_text: String(source.voice_call_consent_text || source.voiceCallConsentText || DEFAULT_WIDGET_CONFIG.voice_call_consent_text).slice(0, 240)
    };
  }

  function emailsToText(value) {
    if (Array.isArray(value)) return value.join(', ');
    return String(value || '');
  }

  function splitEmails(value) {
    const seen = new Set();
    return String(value || '').split(/[\s,;]+/).map((item) => item.trim().toLowerCase()).filter((item) => {
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(item) || seen.has(item)) return false;
      seen.add(item);
      return true;
    }).slice(0, 20);
  }

  function normalizeNotificationEmailConfig(config) {
    const source = config && typeof config === 'object' ? config : DEFAULT_NOTIFICATION_EMAIL_CONFIG;
    const provider = EMAIL_PROVIDERS.includes(String(source.provider || '').toLowerCase()) ? String(source.provider).toLowerCase() : DEFAULT_NOTIFICATION_EMAIL_CONFIG.provider;
    return {
      enabled: Boolean(source.enabled),
      provider,
      send_welcome_email: source.send_welcome_email !== false && source.sendWelcomeEmail !== false,
      send_owner_notification: source.send_owner_notification !== false && source.sendOwnerNotification !== false,
      owner_recipients: splitEmails(source.owner_recipients || source.ownerRecipients || []),
      from_email: splitEmails(source.from_email || source.fromEmail || '')[0] || '',
      from_name: String(source.from_name || source.fromName || DEFAULT_NOTIFICATION_EMAIL_CONFIG.from_name).slice(0, 120),
      welcome_subject: String(source.welcome_subject || source.welcomeSubject || DEFAULT_NOTIFICATION_EMAIL_CONFIG.welcome_subject).slice(0, 200),
      welcome_body: String(source.welcome_body || source.welcomeBody || DEFAULT_NOTIFICATION_EMAIL_CONFIG.welcome_body).slice(0, 5000),
      owner_subject: String(source.owner_subject || source.ownerSubject || DEFAULT_NOTIFICATION_EMAIL_CONFIG.owner_subject).slice(0, 200),
      owner_body: String(source.owner_body || source.ownerBody || DEFAULT_NOTIFICATION_EMAIL_CONFIG.owner_body).slice(0, 5000)
    };
  }

  function currentState(root) {
    return stateByRoot.get(root);
  }

  function render(root) {
    const existing = currentState(root) || {};
    const script = root.closest('[data-easiio-chatbot-customizer]') || document.currentScript;
    const dataset = script ? script.dataset : {};
    const siteId = root.dataset.siteId || dataset.siteId || 'default';
    const apiBase = root.dataset.apiBase || dataset.apiBase || '.';
    const state = {
      apiBase,
      siteId,
      formConfig: normalizeConfig(existing.formConfig || DEFAULT_FORM_CONFIG),
      widgetConfig: normalizeWidgetConfig(existing.widgetConfig || DEFAULT_WIDGET_CONFIG),
      notificationEmailConfig: normalizeNotificationEmailConfig(existing.notificationEmailConfig || DEFAULT_NOTIFICATION_EMAIL_CONFIG),
      ragItems: existing.ragItems || [],
      ragDebug: existing.ragDebug || null,
      ragAnswerLog: existing.ragAnswerLog || [],
      ragFeedback: existing.ragFeedback || [],
      ragSources: existing.ragSources || null,
      ragReview: existing.ragReview || null,
      ragSync: existing.ragSync || null,
      ragEval: existing.ragEval || null
    };
    stateByRoot.set(root, state);
    root.classList.add('easiio-chatbot-customizer');
    root.innerHTML = `
      <section class="chatbot-customizer-shell">
        <div class="chatbot-customizer-toolbar">
          <div>
            <p class="chatbot-eyebrow">Chatbot customization module</p>
            <h2>Lead form + RAG customization</h2>
            <p class="muted small">Customize the chatbot lead form and manually add or modify knowledge base entries for this site_id.</p>
          </div>
          <label class="chatbot-site-field">Site ID
            <input data-chatbot-site-id type="text" value="${escapeHtml(siteId)}" />
          </label>
        </div>
        <p class="chatbot-status" data-chatbot-status role="status"></p>
        <div class="chatbot-customizer-grid">
          <article class="chatbot-admin-card chatbot-widget-config-card">
            <div class="chatbot-card-header">
              <div>
                <h3>Voice playback settings</h3>
                <p class="muted small">Enable the visitor-facing Listen button only after the backend voice endpoint and server-side TTS provider are reviewed. Provider keys remain server-side.</p>
              </div>
              <button class="button" type="button" data-reload-widget-config>Reload</button>
            </div>
            <form data-widget-config-editor class="chatbot-editor-form">
              <div class="chatbot-widget-config-grid">
                <label class="chatbot-checkbox"><input name="voice_enabled" data-widget-voice-enabled type="checkbox" /> Enable voice playback</label>
                <label class="chatbot-checkbox"><input name="voice_autoplay" type="checkbox" /> Autoplay generated audio</label>
                <label>Voice button label<input name="voice_label" type="text" maxlength="80" placeholder="Listen" /></label>
                <label>Voice name<input name="voice" type="text" maxlength="80" placeholder="optional server-side voice id" /></label>
                <label>Audio format<select name="voice_format">${VOICE_FORMATS.map((format) => `<option value="${format}">${format}</option>`).join('')}</select></label>
              </div>
              <div class="chatbot-widget-config-grid chatbot-widget-voice-input-settings">
                <label class="chatbot-checkbox"><input name="voice_input_enabled" data-widget-voice-input-enabled type="checkbox" /> Enable voice input</label>
                <label>Voice input button label<input name="voice_input_label" type="text" maxlength="80" placeholder="Speak" /></label>
                <label>Voice input language<input name="voice_input_language" type="text" maxlength="32" placeholder="auto, en-US, zh-CN" /></label>
              </div>
              <p class="muted small"><strong>Voice input settings:</strong> uses the visitor browser SpeechRecognition/webkitSpeechRecognition API when available. No microphone audio is sent to Easiio unless the browser speech API transcribes it into text.</p>
              <div class="chatbot-widget-config-grid chatbot-widget-voice-call-settings">
                <label class="chatbot-checkbox"><input name="voice_call_enabled" data-widget-voice-call-enabled type="checkbox" /> Enable browser AI voice call</label>
                <label>Voice call button label<input name="voice_call_label" type="text" maxlength="80" placeholder="Call AI Assistant" /></label>
                <label>Voice-call API base URL<input name="voice_call_api_base" data-widget-voice-call-api-base type="url" maxlength="500" placeholder="https://voice.example.com or http://localhost:8120" /></label>
                <label>Voice call consent text<textarea name="voice_call_consent_text" rows="2" maxlength="240"></textarea></label>
              </div>
              <p class="muted small"><strong>Voice call settings:</strong> uses the separate voice_call_bot service for turn-based microphone recording. STT/TTS keys stay server-side.</p>
              <div data-widget-voice-preview class="chatbot-widget-voice-preview"></div>
              <pre class="chatbot-widget-embed-snippet" aria-label="Widget embed voice attributes"></pre>
              <div class="chatbot-actions">
                <button class="button primary" type="submit">Save widget voice settings</button>
              </div>
            </form>
          </article>
          <article class="chatbot-admin-card chatbot-notification-card">
            <div class="chatbot-card-header">
              <div>
                <h3>Notification email settings</h3>
                <p class="muted small">Configure who receives customer inquiries and whether visitors receive an automatic welcome email. API keys stay server-side only.</p>
              </div>
              <button class="button" type="button" data-reload-notification-email>Reload</button>
            </div>
            <form data-notification-email-editor class="chatbot-editor-form">
              <div class="chatbot-notification-grid">
                <label class="chatbot-checkbox"><input name="enabled" type="checkbox" /> Enable email notifications</label>
                <label>Provider<select name="provider">${EMAIL_PROVIDERS.map((provider) => `<option value="${provider}">${provider}</option>`).join('')}</select></label>
                <label>From email<input name="from_email" type="email" placeholder="verified-sender@example.com" autocomplete="email" /></label>
                <label>From name<input name="from_name" type="text" maxlength="120" /></label>
              </div>
              <label>Notification recipients
                <input name="owner_recipients" data-notification-email-recipients type="text" placeholder="owner@example.com, sales@example.com" autocomplete="email" />
              </label>
              <div class="chatbot-notification-grid">
                <label class="chatbot-checkbox"><input name="send_owner_notification" type="checkbox" /> Owner notification email</label>
                <label class="chatbot-checkbox"><input name="send_welcome_email" type="checkbox" /> Welcome email to visitor</label>
              </div>
              <label>Owner notification subject<input name="owner_subject" type="text" maxlength="200" /></label>
              <label>Owner notification body<textarea name="owner_body" rows="7"></textarea></label>
              <label>Welcome subject<input name="welcome_subject" type="text" maxlength="200" /></label>
              <label>Welcome body<textarea name="welcome_body" rows="6"></textarea></label>
              <p class="muted small chatbot-notification-preview">Placeholders: {{name}}, {{email}}, {{phone}}, {{company}}, {{site_id}}, {{site_name}}, {{message}}, {{page_url}}, {{lead_score}}.</p>
              <div class="chatbot-actions">
                <button class="button primary" type="submit">Save notification emails</button>
              </div>
            </form>
          </article>
          <article class="chatbot-admin-card">
            <div class="chatbot-card-header">
              <div>
                <h3>Lead form editor</h3>
                <p class="muted small">Default fields are name, email, company, and message. Add custom text/email/textarea fields as needed.</p>
              </div>
              <button class="button" type="button" data-reload-form>Reload</button>
            </div>
            <form data-lead-form-editor class="chatbot-editor-form">
              <label>Form title<input name="title" type="text" maxlength="120" /></label>
              <label>Help text<textarea name="help_text" rows="2" maxlength="240"></textarea></label>
              <label>Submit button label<input name="submit_label" type="text" maxlength="80" /></label>
              <div class="chatbot-editor-subheader">
                <strong>Fields</strong>
                <button class="button" type="button" data-add-field>+ Add field</button>
              </div>
              <div data-field-list class="chatbot-field-list"></div>
              <div class="chatbot-actions">
                <button class="button primary" type="submit">Save lead form</button>
                <button class="button" type="button" data-reset-defaults>Reset defaults</button>
              </div>
            </form>
          </article>
          <article class="chatbot-admin-card">
            <div class="chatbot-card-header">
              <div>
                <h3>Live form preview</h3>
                <p class="muted small">Preview updates before saving. The public widget will load this config from the backend.</p>
              </div>
            </div>
            <div data-form-preview class="chatbot-preview-form"></div>
          </article>
          <article class="chatbot-admin-card chatbot-kb-card">
            <div class="chatbot-card-header">
              <div>
                <h3>RAG knowledge base</h3>
                <p class="muted small">Add or modify manual knowledge entries used by the chatbot for this site_id.</p>
              </div>
              <button class="button" type="button" data-reload-kb>Reload</button>
            </div>
            <form data-kb-editor class="chatbot-editor-form">
              <input name="content_id" type="hidden" />
              <label>Title<input name="title" type="text" required maxlength="160" /></label>
              <label>URL or source<input name="url" type="text" maxlength="240" placeholder="https://example.com/faq or manual://pricing" /></label>
              <label>Knowledge content<textarea name="content" rows="8" required placeholder="Paste services, pricing, FAQ, process, policies, or contact details..."></textarea></label>
              <div class="chatbot-actions">
                <button class="button primary" type="submit">Save knowledge item</button>
                <button class="button" type="button" data-clear-kb-form>New item</button>
              </div>
            </form>
            <div data-kb-list class="chatbot-kb-list" aria-live="polite"></div>
          </article>
          <article class="chatbot-admin-card chatbot-rag-sync-card">
            <div class="chatbot-card-header">
              <div>
                <h3>RAG source sync</h3>
                <p class="muted small">Sync published Easiio Docs, Wiki pages, WordPress exports, and uploaded document text into this site's chatbot knowledge while preserving manual entries.</p>
              </div>
              <button class="button" type="button" data-load-rag-sources>Refresh sources</button>
            </div>
            <div class="chatbot-rag-source-list" data-rag-source-list></div>
            <div class="chatbot-rag-sync-options">
              <label class="chatbot-checkbox"><input type="checkbox" data-rag-sync-source="docs" checked /> Easiio Docs</label>
              <label class="chatbot-checkbox"><input type="checkbox" data-rag-sync-source="wiki" checked /> Website Wiki</label>
              <label class="chatbot-checkbox"><input type="checkbox" data-rag-sync-source="wordpress" /> WordPress</label>
              <label class="chatbot-checkbox"><input type="checkbox" data-rag-sync-source="upload" /> Uploads</label>
            </div>
            <div class="chatbot-actions">
              <button class="button primary" type="button" data-sync-rag-sources>Sync selected sources</button>
              <button class="button" type="button" data-preview-rag-sync>Preview changes</button>
              <button class="button" type="button" data-load-rag-review>Load review queue</button>
            </div>
            <div class="chatbot-rag-sync-results" data-rag-sync-results></div>
            <div class="chatbot-rag-review-panel">
              <div class="chatbot-card-header compact">
                <div>
                  <h4>RAG review queue</h4>
                  <p class="muted small">Review new, changed, unchanged, and deleted_upstream items before syncing. Use rollback only after review.</p>
                </div>
                <button class="button danger" type="button" data-rollback-rag-sync>Rollback last sync</button>
              </div>
              <div data-rag-review-results class="chatbot-rag-review-results"></div>
            </div>
            <div class="chatbot-rag-schedule-card">
              <div class="chatbot-card-header compact">
                <div>
                  <h4>RAG schedule + notifications</h4>
                  <p class="muted small">Configure periodic source refresh previews, stale-source alerts, and review notifications.</p>
                </div>
                <button class="button" type="button" data-load-rag-notifications>Load notifications</button>
                <button class="button" type="button" data-mark-rag-notifications-read>Mark read</button>
              </div>
              <form data-rag-schedule-form class="chatbot-rag-schedule-form">
                <label class="chatbot-checkbox"><input name="enabled" type="checkbox" /> Enable scheduled refresh</label>
                <label>Interval minutes<input name="interval_minutes" type="number" min="5" value="1440" /></label>
                <label>Stale alert minutes<input name="stale_after_minutes" type="number" min="5" value="2880" /></label>
                <label>Notification recipients<input name="notify_recipients" type="text" placeholder="owner@example.com, ops@example.com" /></label>
                <label class="chatbot-checkbox"><input name="notify_on_changes" type="checkbox" checked /> Notify when changes are found</label>
                <label class="chatbot-checkbox"><input name="auto_sync" type="checkbox" /> Auto-sync scheduled changes after preview</label>
                <div class="chatbot-actions">
                  <button class="button" type="button" data-save-rag-schedule>Save schedule</button>
                  <button class="button" type="button" data-run-rag-scheduled-refresh>Run scheduled refresh now</button>
                  <button class="button" type="button" data-load-rag-due>Check due sites</button>
                </div>
              </form>
              <div class="chatbot-rag-notification-list" data-rag-notifications></div>
            </div>
            <div class="chatbot-rag-external-grid">
              <form class="chatbot-rag-source-import" data-rag-source-import="wordpress">
                <h4>WordPress import</h4>
                <p class="muted small">Paste reviewed public WordPress page/post JSON. Private or draft content is ignored during sync.</p>
                <textarea name="items_json" rows="6" placeholder='[{"slug":"homepage","title":"Homepage","status":"publish","visibility":"public","content":"..."}]'></textarea>
                <div class="chatbot-actions">
                  <button class="button" type="submit">Save WordPress source</button>
                </div>
              </form>
              <form class="chatbot-rag-pipeline-form" data-rag-wordpress-pull>
                <h4>WordPress REST pull</h4>
                <p class="muted small">Pull public posts/pages from a WordPress REST API. Optional auth env name stays server-side and is never returned.</p>
                <label>WordPress URL<input name="base_url" type="url" placeholder="https://example.com" /></label>
                <label>Post types<input name="post_types" type="text" placeholder="pages, posts" value="pages, posts" /></label>
                <label>Auth env name<input name="auth_env" type="text" placeholder="Optional server env var name" /></label>
                <div class="chatbot-actions"><button class="button" type="submit">Pull WordPress content</button></div>
              </form>
              <form class="chatbot-rag-source-import" data-rag-source-import="upload">
                <h4>Uploaded document import</h4>
                <p class="muted small">Paste reviewed extracted text from PDF/DOCX/TXT uploads. Keep only public, approved text.</p>
                <textarea name="items_json" rows="6" placeholder='[{"slug":"course-brochure","filename":"brochure.pdf","status":"published","visibility":"public","content":"..."}]'></textarea>
                <div class="chatbot-actions">
                  <button class="button" type="submit">Save upload source</button>
                </div>
              </form>
              <form class="chatbot-rag-pipeline-form" data-rag-upload-extract>
                <h4>Document extraction</h4>
                <p class="muted small">Extract and stage TXT/HTML/DOCX/PDF text for review. Scanned PDFs may need a separate OCR step.</p>
                <label>Document file<input name="document_file" type="file" accept=".txt,.md,.html,.htm,.docx,.pdf,text/plain,text/markdown,text/html,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" /></label>
                <label>Title<input name="title" type="text" placeholder="Optional document title" /></label>
                <div class="chatbot-actions"><button class="button" type="submit">Extract document text</button></div>
              </form>
            </div>
          </article>
          <article class="chatbot-admin-card chatbot-rag-debug-card">
            <div class="chatbot-card-header">
              <div>
                <h3>RAG debug + evaluation</h3>
                <p class="muted small">Test questions, inspect retrieval candidates, review answer logs, and run small golden Q&A checks.</p>
              </div>
              <button class="button" type="button" data-load-rag-answer-log>Load logs</button>
            </div>
            <form data-rag-debug-form class="chatbot-editor-form">
              <label>Test question<textarea name="question" rows="3" placeholder="What does lesson 3 build?"></textarea></label>
              <div class="chatbot-actions">
                <button class="button primary" type="submit">Debug retrieval</button>
                <button class="button" type="button" data-run-rag-eval>Run sample eval</button>
              </div>
            </form>
            <div class="chatbot-rag-debug-results" data-rag-debug-results></div>
            <div class="chatbot-rag-eval-results" data-rag-eval-results></div>
            <div class="chatbot-rag-feedback-row">
              <button class="button" type="button" data-send-rag-feedback="helpful">Mark helpful</button>
              <button class="button" type="button" data-send-rag-feedback="not_helpful">Mark not helpful</button>
            </div>
            <div class="chatbot-rag-answer-log" data-rag-answer-log></div>
          </article>
        </div>
      </section>`;
    bind(root);
    fillForm(root);
    fillWidgetConfigForm(root);
    fillNotificationEmailForm(root);
    renderFieldRows(root);
    renderPreview(root);
    loadFormConfig(root);
    loadNotificationEmailConfig(root);
    loadKnowledgeBase(root);
    loadRagSources(root);
    loadRagSchedule(root);
    loadRagNotifications(root);
  }

  function readSiteId(root) {
    const state = currentState(root);
    const input = root.querySelector('[data-chatbot-site-id]');
    state.siteId = String(input && input.value || state.siteId || 'default').trim() || 'default';
    return state.siteId;
  }

  function fillForm(root) {
    const state = currentState(root);
    const form = root.querySelector('[data-lead-form-editor]');
    if (!form) return;
    form.elements.title.value = state.formConfig.title;
    form.elements.help_text.value = state.formConfig.help_text;
    form.elements.submit_label.value = state.formConfig.submit_label;
  }

  function fillNotificationEmailForm(root) {
    const state = currentState(root);
    const form = root.querySelector('[data-notification-email-editor]');
    if (!form) return;
    const config = state.notificationEmailConfig || normalizeNotificationEmailConfig(DEFAULT_NOTIFICATION_EMAIL_CONFIG);
    form.elements.enabled.checked = Boolean(config.enabled);
    form.elements.provider.value = config.provider || 'brevo';
    form.elements.from_email.value = config.from_email || '';
    form.elements.from_name.value = config.from_name || '';
    form.elements.owner_recipients.value = emailsToText(config.owner_recipients);
    form.elements.send_owner_notification.checked = Boolean(config.send_owner_notification);
    form.elements.send_welcome_email.checked = Boolean(config.send_welcome_email);
    form.elements.owner_subject.value = config.owner_subject || '';
    form.elements.owner_body.value = config.owner_body || '';
    form.elements.welcome_subject.value = config.welcome_subject || '';
    form.elements.welcome_body.value = config.welcome_body || '';
  }

  function fillWidgetConfigForm(root) {
    const state = currentState(root);
    const form = root.querySelector('[data-widget-config-editor]');
    if (!form) return;
    const config = state.widgetConfig || normalizeWidgetConfig(DEFAULT_WIDGET_CONFIG);
    form.elements.voice_enabled.checked = Boolean(config.voice_enabled);
    form.elements.voice_autoplay.checked = Boolean(config.voice_autoplay);
    form.elements.voice_label.value = config.voice_label || 'Listen';
    form.elements.voice.value = config.voice || '';
    form.elements.voice_format.value = config.voice_format || 'mp3';
    form.elements.voice_input_enabled.checked = Boolean(config.voice_input_enabled);
    form.elements.voice_input_label.value = config.voice_input_label || 'Speak';
    form.elements.voice_input_language.value = config.voice_input_language || 'auto';
    form.elements.voice_call_enabled.checked = Boolean(config.voice_call_enabled);
    form.elements.voice_call_label.value = config.voice_call_label || 'Call AI Assistant';
    form.elements.voice_call_api_base.value = config.voice_call_api_base || '';
    form.elements.voice_call_consent_text.value = config.voice_call_consent_text || DEFAULT_WIDGET_CONFIG.voice_call_consent_text;
    renderWidgetVoicePreview(root);
  }

  function widgetConfigPayloadFromForm(root) {
    const state = currentState(root);
    const form = root.querySelector('[data-widget-config-editor]');
    const config = normalizeWidgetConfig({
      voice_enabled: form.elements.voice_enabled.checked,
      voice_autoplay: form.elements.voice_autoplay.checked,
      voice_label: form.elements.voice_label.value,
      voice: form.elements.voice.value,
      voice_format: form.elements.voice_format.value,
      voice_input_enabled: form.elements.voice_input_enabled.checked,
      voice_input_label: form.elements.voice_input_label.value,
      voice_input_language: form.elements.voice_input_language.value,
      voice_call_enabled: form.elements.voice_call_enabled.checked,
      voice_call_label: form.elements.voice_call_label.value,
      voice_call_api_base: form.elements.voice_call_api_base.value,
      voice_call_consent_text: form.elements.voice_call_consent_text.value
    });
    state.widgetConfig = config;
    return config;
  }

  function renderWidgetVoicePreview(root) {
    const state = currentState(root);
    const preview = root.querySelector('[data-widget-voice-preview]');
    const snippet = root.querySelector('.chatbot-widget-embed-snippet');
    if (!preview) return;
    const config = state.widgetConfig || normalizeWidgetConfig(DEFAULT_WIDGET_CONFIG);
    preview.innerHTML = config.voice_enabled
      ? `<strong>Voice enabled:</strong> bot replies show a “${escapeHtml(config.voice_label || 'Listen')}” button. Audio requests use server-side TTS only.`
      : '<strong>Voice disabled:</strong> public widgets will not render the Listen button.';
    preview.innerHTML += config.voice_input_enabled
      ? `<br /><strong>Voice input enabled:</strong> visitors can click “${escapeHtml(config.voice_input_label || 'Speak')}” and use browser speech recognition (${escapeHtml(config.voice_input_language || 'auto')}).`
      : '<br /><strong>Voice input disabled:</strong> public widgets will not render the microphone button.';
    preview.innerHTML += config.voice_call_enabled
      ? `<br /><strong>Voice call enabled:</strong> visitors can click “${escapeHtml(config.voice_call_label || 'Call AI Assistant')}” and record turn-based microphone audio through the voice_call_bot service.`
      : '<br /><strong>Voice call disabled:</strong> public widgets will not render the AI call button.';
    if (snippet) {
      snippet.textContent = [
        `data-voice-enabled="${config.voice_enabled ? 'true' : 'false'}"`,
        `data-voice-label="${config.voice_label || 'Listen'}"`,
        `data-voice-autoplay="${config.voice_autoplay ? 'true' : 'false'}"`,
        config.voice ? `data-voice="${config.voice}"` : '',
        `data-voice-format="${config.voice_format || 'mp3'}"`,
        `data-voice-input-enabled="${config.voice_input_enabled ? 'true' : 'false'}"`,
        `data-voice-input-label="${config.voice_input_label || 'Speak'}"`,
        `data-voice-input-language="${config.voice_input_language || 'auto'}"`,
        `data-voice-call-enabled="${config.voice_call_enabled ? 'true' : 'false'}"`,
        `data-voice-call-label="${config.voice_call_label || 'Call AI Assistant'}"`,
        config.voice_call_api_base ? `data-voice-call-api-base="${config.voice_call_api_base}"` : '',
        `data-voice-call-consent-text="${config.voice_call_consent_text || DEFAULT_WIDGET_CONFIG.voice_call_consent_text}"`
      ].filter(Boolean).join('\n');
    }
  }

  function notificationEmailPayloadFromForm(root) {
    const state = currentState(root);
    const form = root.querySelector('[data-notification-email-editor]');
    const config = normalizeNotificationEmailConfig({
      enabled: form.elements.enabled.checked,
      provider: form.elements.provider.value,
      from_email: form.elements.from_email.value,
      from_name: form.elements.from_name.value,
      owner_recipients: form.elements.owner_recipients.value,
      send_owner_notification: form.elements.send_owner_notification.checked,
      send_welcome_email: form.elements.send_welcome_email.checked,
      owner_subject: form.elements.owner_subject.value,
      owner_body: form.elements.owner_body.value,
      welcome_subject: form.elements.welcome_subject.value,
      welcome_body: form.elements.welcome_body.value
    });
    state.notificationEmailConfig = config;
    return config;
  }

  function readFormEditor(root) {
    const state = currentState(root);
    const form = root.querySelector('[data-lead-form-editor]');
    const fields = Array.from(root.querySelectorAll('[data-field-row]')).map((row, index) => normalizeField({
      name: row.querySelector('[name="field_name"]').value,
      label: row.querySelector('[name="field_label"]').value,
      type: row.querySelector('[name="field_type"]').value,
      required: row.querySelector('[name="field_required"]').checked,
      autocomplete: row.querySelector('[name="field_autocomplete"]').value
    }, index));
    state.formConfig = normalizeConfig({
      title: form.elements.title.value,
      help_text: form.elements.help_text.value,
      submit_label: form.elements.submit_label.value,
      fields
    });
    return state.formConfig;
  }

  function renderFieldRows(root) {
    const state = currentState(root);
    const list = root.querySelector('[data-field-list]');
    if (!list) return;
    list.innerHTML = state.formConfig.fields.map((field, index) => `
      <div class="chatbot-field-row" data-field-row>
        <label>Name<input name="field_name" type="text" value="${escapeHtml(field.name)}" /></label>
        <label>Label<input name="field_label" type="text" value="${escapeHtml(field.label)}" /></label>
        <label>Type<select name="field_type">${FIELD_TYPES.map((type) => `<option value="${type}" ${field.type === type ? 'selected' : ''}>${type}</option>`).join('')}</select></label>
        <label>Autocomplete<input name="field_autocomplete" type="text" value="${escapeHtml(field.autocomplete)}" /></label>
        <label class="chatbot-checkbox"><input name="field_required" type="checkbox" ${field.required ? 'checked' : ''} /> Required</label>
        <button class="button danger" type="button" data-remove-field="${index}">Remove</button>
      </div>`).join('');
  }

  function renderPreview(root) {
    const state = currentState(root);
    const preview = root.querySelector('[data-form-preview]');
    if (!preview) return;
    preview.innerHTML = `
      <form>
        <h3>${escapeHtml(state.formConfig.title)}</h3>
        <p class="muted small">${escapeHtml(state.formConfig.help_text)}</p>
        ${state.formConfig.fields.map((field) => `
          <label>${escapeHtml(field.label)}${field.required ? ' *' : ''}
            ${field.type === 'textarea'
              ? `<textarea name="${escapeHtml(field.name)}" rows="3" ${field.required ? 'required' : ''}></textarea>`
              : `<input name="${escapeHtml(field.name)}" type="${escapeHtml(field.type)}" ${field.required ? 'required' : ''} autocomplete="${escapeHtml(field.autocomplete)}" />`}
          </label>`).join('')}
        <button class="button primary" type="button">${escapeHtml(state.formConfig.submit_label)}</button>
      </form>`;
  }

  function addFormField(root) {
    const state = currentState(root);
    readFormEditor(root);
    state.formConfig.fields.push(normalizeField({ name: 'custom_field', label: 'Custom field', type: 'text', required: false }, state.formConfig.fields.length));
    renderFieldRows(root);
    renderPreview(root);
  }

  function removeFormField(root, index) {
    const state = currentState(root);
    readFormEditor(root);
    state.formConfig.fields.splice(Number(index), 1);
    if (!state.formConfig.fields.length) state.formConfig.fields = DEFAULT_FORM_CONFIG.fields.map(normalizeField);
    renderFieldRows(root);
    renderPreview(root);
  }

  async function loadFormConfig(root) {
    const state = currentState(root);
    try {
      const siteId = encodeURIComponent(readSiteId(root));
      const response = await fetch(apiUrl(state.apiBase, `/api/chat/form-config?site_id=${siteId}`), { credentials: 'same-origin' });
      const body = await response.json();
      if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to load lead form config');
      state.formConfig = normalizeConfig(body.form_config);
      state.widgetConfig = normalizeWidgetConfig(body.form_config && body.form_config.widget_config);
      fillForm(root);
      fillWidgetConfigForm(root);
      renderFieldRows(root);
      renderPreview(root);
      status(root, `Loaded lead form for ${state.siteId}`, 'success');
    } catch (error) {
      status(root, `Using local defaults: ${error.message}`, 'warning');
    }
  }

  async function saveFormConfig(root) {
    const state = currentState(root);
    const formConfig = readFormEditor(root);
    renderFieldRows(root);
    renderPreview(root);
    const response = await fetch(apiUrl(state.apiBase, '/api/chat/form-config'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ site_id: readSiteId(root), form_config: Object.assign({}, formConfig, { widget_config: state.widgetConfig || normalizeWidgetConfig(DEFAULT_WIDGET_CONFIG) }) })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to save form config');
    state.formConfig = normalizeConfig(body.form_config || formConfig);
    fillForm(root);
    renderFieldRows(root);
    renderPreview(root);
    status(root, `Saved lead form for ${state.siteId}`, 'success');
  }

  async function saveWidgetConfig(root) {
    const state = currentState(root);
    const widgetConfig = widgetConfigPayloadFromForm(root);
    const formConfig = Object.assign({}, state.formConfig || normalizeConfig(DEFAULT_FORM_CONFIG), { widget_config: widgetConfig });
    const response = await fetch(apiUrl(state.apiBase, '/api/chat/form-config'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ site_id: readSiteId(root), form_config: formConfig })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to save widget voice settings');
    state.formConfig = normalizeConfig(body.form_config || formConfig);
    state.widgetConfig = normalizeWidgetConfig((body.form_config && body.form_config.widget_config) || widgetConfig);
    fillWidgetConfigForm(root);
    status(root, `Saved widget voice settings for ${state.siteId}`, 'success');
  }

  async function loadWidgetConfig(root) {
    await loadFormConfig(root);
    fillWidgetConfigForm(root);
    status(root, `Loaded widget voice settings for ${currentState(root).siteId}`, 'success');
  }

  async function loadNotificationEmailConfig(root) {
    const state = currentState(root);
    try {
      const siteId = encodeURIComponent(readSiteId(root));
      const response = await fetch(apiUrl(state.apiBase, `/api/email-agent/config?site_id=${siteId}`), { credentials: 'same-origin' });
      const body = await response.json();
      if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to load notification email config');
      state.notificationEmailConfig = normalizeNotificationEmailConfig(body.email_config);
      fillNotificationEmailForm(root);
      status(root, `Loaded notification email settings for ${state.siteId}`, 'success');
    } catch (error) {
      status(root, `Notification email settings unavailable: ${error.message}`, 'warning');
    }
  }

  async function saveNotificationEmailConfig(root) {
    const state = currentState(root);
    const emailConfig = notificationEmailPayloadFromForm(root);
    const response = await fetch(apiUrl(state.apiBase, '/api/email-agent/config'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ site_id: readSiteId(root), email_config: emailConfig })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to save notification email config');
    state.notificationEmailConfig = normalizeNotificationEmailConfig(body.email_config || emailConfig);
    fillNotificationEmailForm(root);
    status(root, `Saved notification email settings for ${state.siteId}`, 'success');
  }

  async function loadKnowledgeBase(root) {
    const state = currentState(root);
    try {
      const response = await fetch(apiUrl(state.apiBase, `/api/rag/content?site_id=${encodeURIComponent(readSiteId(root))}`), { credentials: 'same-origin' });
      const body = await response.json();
      if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to load knowledge base');
      state.ragItems = Array.isArray(body.items) ? body.items : [];
      renderKnowledgeList(root);
      status(root, `Loaded ${state.ragItems.length} knowledge items for ${state.siteId}`, 'success');
    } catch (error) {
      status(root, `Knowledge load failed: ${error.message}`, 'warning');
    }
  }

  function renderKnowledgeList(root) {
    const state = currentState(root);
    const list = root.querySelector('[data-kb-list]');
    if (!list) return;
    if (!state.ragItems.length) {
      list.innerHTML = '<p class="muted small">No manual RAG knowledge items yet.</p>';
      return;
    }
    list.innerHTML = state.ragItems.map((item) => `
      <article class="chatbot-kb-item" data-content-id="${escapeHtml(item.content_id)}">
        <div>
          <strong>${escapeHtml(item.title || 'Untitled')}</strong>
          <small>${escapeHtml(item.url || 'manual source')}</small>
          <p>${escapeHtml(String(item.content || '').slice(0, 180))}${String(item.content || '').length > 180 ? '…' : ''}</p>
        </div>
        <div class="chatbot-kb-actions">
          <button class="button" type="button" data-edit-kb="${escapeHtml(item.content_id)}">Edit</button>
          <button class="button danger" type="button" data-delete-kb="${escapeHtml(item.content_id)}">Delete</button>
        </div>
      </article>`).join('');
  }

  function clearKnowledgeForm(root) {
    const form = root.querySelector('[data-kb-editor]');
    if (form) form.reset();
  }

  function editKnowledgeItem(root, contentId) {
    const state = currentState(root);
    const item = state.ragItems.find((entry) => String(entry.content_id) === String(contentId));
    const form = root.querySelector('[data-kb-editor]');
    if (!item || !form) return;
    form.elements.content_id.value = item.content_id || '';
    form.elements.title.value = item.title || '';
    form.elements.url.value = item.url || '';
    form.elements.content.value = item.content || '';
    form.elements.title.focus();
  }

  async function saveKnowledgeItem(root) {
    const state = currentState(root);
    const form = root.querySelector('[data-kb-editor]');
    const payload = {
      site_id: readSiteId(root),
      content_id: form.elements.content_id.value || undefined,
      title: form.elements.title.value,
      url: form.elements.url.value,
      content: form.elements.content.value
    };
    const response = await fetch(apiUrl(state.apiBase, '/api/rag/content'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify(payload)
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to save knowledge item');
    clearKnowledgeForm(root);
    await loadKnowledgeBase(root);
    status(root, `Saved knowledge item for ${state.siteId}`, 'success');
  }

  async function deleteKnowledgeItem(root, contentId) {
    const state = currentState(root);
    const response = await fetch(apiUrl(state.apiBase, '/api/rag/content/delete'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ site_id: readSiteId(root), content_id: contentId })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to delete knowledge item');
    await loadKnowledgeBase(root);
    status(root, `Deleted knowledge item for ${state.siteId}`, 'success');
  }

  function renderRagSources(root) {
    const state = currentState(root);
    const target = root.querySelector('[data-rag-source-list]');
    if (!target) return;
    const sources = state.ragSources && state.ragSources.sources || {};
    const rows = ['manual', 'docs', 'wiki', 'wordpress', 'upload'].map((name) => {
      const source = sources[name] || {};
      const count = source.eligible_count != null ? source.eligible_count : source.stored_count || 0;
      return `<div class="chatbot-rag-source-row"><strong>${escapeHtml(name)}</strong><span>${escapeHtml(String(count))}</span><small>${source.requires_payload ? 'payload/manual import' : source.db_configured === false ? 'not configured' : 'ready'}</small></div>`;
    }).join('');
    const lastSync = state.ragSources && state.ragSources.last_sync && state.ragSources.last_sync.synced_items != null
      ? `<p class="muted small">Last sync: ${escapeHtml(String(state.ragSources.last_sync.synced_items))} items from ${(state.ragSources.last_sync.sources || []).map(escapeHtml).join(', ')}</p>`
      : '<p class="muted small">No source sync has run yet for this site.</p>';
    target.innerHTML = `${rows}${lastSync}`;
  }

  async function loadRagSources(root) {
    const state = currentState(root);
    try {
      const response = await fetch(apiUrl(state.apiBase, `/api/rag/sources?site_id=${encodeURIComponent(readSiteId(root))}`), { credentials: 'same-origin' });
      const body = await response.json();
      if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to load RAG sources');
      state.ragSources = body;
      renderRagSources(root);
      return body;
    } catch (error) {
      const target = root.querySelector('[data-rag-source-list]');
      if (target) target.innerHTML = `<p class="muted small">RAG source status unavailable: ${escapeHtml(error.message)}</p>`;
      return null;
    }
  }

  async function saveExternalSourceItems(root, form) {
    const state = currentState(root);
    const source = form && form.dataset.ragSourceImport;
    if (!source) throw new Error('Missing source type');
    let items;
    try {
      items = JSON.parse(form.elements.items_json.value || '[]');
    } catch (error) {
      throw new Error('Source JSON must be a valid array');
    }
    if (!Array.isArray(items)) throw new Error('Source JSON must be an array of items');
    const response = await fetch(apiUrl(state.apiBase, '/api/rag/source-items'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ site_id: readSiteId(root), source, items, approved_by: 'admin_customizer' })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || `Failed to save ${source} source items`);
    form.elements.items_json.value = '';
    await loadRagSources(root);
    status(root, `Saved ${body.eligible_count || 0} eligible ${source} source items`, 'success');
  }

  function fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result || '').split(',').pop() || '');
      reader.onerror = () => reject(reader.error || new Error('Could not read file'));
      reader.readAsDataURL(file);
    });
  }

  async function pullWordPressSource(root, form) {
    const state = currentState(root);
    const postTypes = String(form.elements.post_types.value || 'pages, posts').split(',').map((item) => item.trim()).filter(Boolean);
    const response = await fetch(apiUrl(state.apiBase, '/api/rag/wordpress/pull'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({
        site_id: readSiteId(root),
        base_url: form.elements.base_url.value,
        post_types: postTypes,
        auth_env: form.elements.auth_env.value,
        confirm_pull: true,
        approved_by: 'admin_customizer'
      })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to pull WordPress content');
    await loadRagSources(root);
    status(root, `Pulled ${body.eligible_count || 0} eligible WordPress items`, 'success');
  }

  async function extractUploadDocument(root, form) {
    const state = currentState(root);
    const file = form.elements.document_file.files && form.elements.document_file.files[0];
    if (!file) throw new Error('Choose a document file first');
    const contentBase64 = await fileToBase64(file);
    const response = await fetch(apiUrl(state.apiBase, '/api/rag/upload/extract'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({
        site_id: readSiteId(root),
        filename: file.name,
        mime_type: file.type || 'application/octet-stream',
        title: form.elements.title.value || file.name,
        content_base64: contentBase64,
        confirm_extract: true,
        approved_by: 'admin_customizer'
      })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to extract document');
    form.reset();
    await loadRagSources(root);
    status(root, `Extracted ${body.extraction_method || 'document'} text for ${body.slug}`, 'success');
  }

  function selectedRagSources(root) {
    return Array.from(root.querySelectorAll('[data-rag-sync-source]:checked')).map((input) => input.dataset.ragSyncSource).filter(Boolean);
  }

  function emailsToArray(text) {
    return String(text || '').split(/[;,\s]+/).map((item) => item.trim()).filter(Boolean);
  }

  function fillRagScheduleForm(root) {
    const state = currentState(root);
    const form = root.querySelector('[data-rag-schedule-form]');
    if (!form || !state.ragSchedule) return;
    const schedule = state.ragSchedule.schedule || state.ragSchedule;
    form.elements.enabled.checked = Boolean(schedule.enabled);
    form.elements.interval_minutes.value = schedule.interval_minutes || 1440;
    form.elements.stale_after_minutes.value = schedule.stale_after_minutes || 2880;
    form.elements.notify_recipients.value = (schedule.notify_recipients || []).join(', ');
    form.elements.notify_on_changes.checked = schedule.notify_on_changes !== false;
    form.elements.auto_sync.checked = Boolean(schedule.auto_sync);
  }

  async function loadRagSchedule(root) {
    const state = currentState(root);
    const response = await fetch(apiUrl(state.apiBase, `/api/rag/refresh-schedule?site_id=${encodeURIComponent(readSiteId(root))}`), { credentials: 'same-origin' });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to load RAG refresh schedule');
    state.ragSchedule = body;
    fillRagScheduleForm(root);
    return body;
  }

  async function saveRagSchedule(root) {
    const state = currentState(root);
    const form = root.querySelector('[data-rag-schedule-form]');
    if (!form) throw new Error('Missing RAG schedule form');
    const response = await fetch(apiUrl(state.apiBase, '/api/rag/refresh-schedule'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({
        site_id: readSiteId(root),
        schedule: {
          enabled: form.elements.enabled.checked,
          sources: selectedRagSources(root),
          interval_minutes: Number(form.elements.interval_minutes.value || 1440),
          stale_after_minutes: Number(form.elements.stale_after_minutes.value || 2880),
          notify_recipients: emailsToArray(form.elements.notify_recipients.value),
          notify_on_changes: form.elements.notify_on_changes.checked,
          auto_sync: form.elements.auto_sync.checked
        }
      })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to save RAG schedule');
    state.ragSchedule = body;
    fillRagScheduleForm(root);
    status(root, 'Saved RAG refresh schedule', 'success');
  }

  function renderRagNotifications(root) {
    const state = currentState(root);
    const target = root.querySelector('[data-rag-notifications]');
    if (!target) return;
    const items = state.ragNotifications && Array.isArray(state.ragNotifications.items) ? state.ragNotifications.items.slice(0, 8) : [];
    const unread = state.ragNotifications && state.ragNotifications.unread_count || 0;
    target.innerHTML = `<p class="muted small">Unread notifications: ${escapeHtml(String(unread))}</p>${items.map((item) => `<div class="chatbot-rag-notification-row" data-unread="${item.unread ? 'true' : 'false'}"><strong>${escapeHtml(item.message || 'RAG refresh notification')}</strong><small>${escapeHtml(item.action || '')} · ${escapeHtml((item.sources || []).join(', '))}</small><p>${escapeHtml(JSON.stringify(item.review_summary || {}))}</p></div>`).join('') || '<p class="muted small">No RAG notifications yet.</p>'}`;
  }

  async function loadRagNotifications(root) {
    const state = currentState(root);
    const response = await fetch(apiUrl(state.apiBase, `/api/rag/notifications?site_id=${encodeURIComponent(readSiteId(root))}`), { credentials: 'same-origin' });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to load RAG notifications');
    state.ragNotifications = body;
    renderRagNotifications(root);
    return body;
  }

  async function loadRagDue(root) {
    const state = currentState(root);
    const response = await fetch(apiUrl(state.apiBase, '/api/rag/refresh-due'), { credentials: 'same-origin' });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to check due RAG refresh jobs');
    status(root, `${body.count || 0} RAG refresh schedules are due`, 'success');
  }

  async function markRagNotificationsRead(root) {
    const state = currentState(root);
    const response = await fetch(apiUrl(state.apiBase, '/api/rag/notifications/read'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ site_id: readSiteId(root), mark_all: true })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to mark RAG notifications read');
    await loadRagNotifications(root);
    status(root, `Marked ${body.updated || 0} RAG notifications read`, 'success');
  }

  async function runScheduledRefresh(root) {
    const state = currentState(root);
    const response = await fetch(apiUrl(state.apiBase, '/api/rag/run-scheduled-refresh'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ site_id: readSiteId(root), dry_run: false })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to run scheduled RAG refresh');
    await loadRagSources(root);
    await loadRagNotifications(root);
    status(root, `Scheduled refresh finished for ${body.results && body.results.length || 0} site(s)`, 'success');
  }

  function renderRagReview(root) {
    const state = currentState(root);
    const target = root.querySelector('[data-rag-review-results]');
    if (!target) return;
    const review = state.ragReview;
    if (!review) {
      target.innerHTML = '<p class="muted small">No review loaded yet. Preview changes before syncing.</p>';
      return;
    }
    const summary = review.summary || {};
    const rows = Array.isArray(review.items) ? review.items.slice(0, 12) : [];
    target.innerHTML = `
      <p class="muted small">Queue: new=${escapeHtml(String(summary.new || 0))}, changed=${escapeHtml(String(summary.changed || 0))}, unchanged=${escapeHtml(String(summary.unchanged || 0))}, deleted_upstream=${escapeHtml(String(summary.deleted_upstream || 0))}</p>
      ${rows.map((item) => `<div class="chatbot-rag-review-row"><span class="chatbot-rag-review-status" data-status="${escapeHtml(item.review_status || '')}">${escapeHtml(item.review_status || '')}</span><strong>${escapeHtml(item.title || item.content_id || '')}</strong><small>${escapeHtml(item.source || '')}</small>${item.diff_preview ? `<pre class="chatbot-rag-diff-preview">${escapeHtml(item.diff_preview)}</pre>` : `<p>${escapeHtml(item.text_preview || '')}</p>`}</div>`).join('') || '<p class="muted small">No source changes detected.</p>'}`;
  }

  async function loadRagReview(root) {
    const state = currentState(root);
    const response = await fetch(apiUrl(state.apiBase, `/api/rag/review?site_id=${encodeURIComponent(readSiteId(root))}`), { credentials: 'same-origin' });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to load RAG review queue');
    state.ragReview = body;
    renderRagReview(root);
    status(root, `Loaded RAG review queue for ${state.siteId}`, 'success');
  }

  async function previewRagSync(root) {
    const state = currentState(root);
    const sources = selectedRagSources(root);
    if (!sources.length) throw new Error('Select at least one RAG source to preview');
    const response = await fetch(apiUrl(state.apiBase, '/api/rag/sync-preview'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ site_id: readSiteId(root), sources, approved_by: 'admin_customizer' })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to preview RAG sync');
    state.ragReview = body;
    renderRagReview(root);
    status(root, `Previewed ${body.summary && body.summary.total || 0} RAG source changes`, 'success');
  }

  async function rollbackRagSync(root) {
    const state = currentState(root);
    const lastSync = state.ragSources && state.ragSources.last_sync || {};
    const rollbackId = lastSync.rollback_id || (state.ragSync && state.ragSync.summary && state.ragSync.summary.rollback_id) || '';
    if (!rollbackId) throw new Error('No rollback snapshot is available yet');
    const response = await fetch(apiUrl(state.apiBase, '/api/rag/rollback'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ site_id: readSiteId(root), rollback_id: rollbackId, confirm_rollback: true, approved_by: 'admin_customizer' })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to rollback RAG sync');
    await loadKnowledgeBase(root);
    await loadRagSources(root);
    await loadRagReview(root);
    status(root, `Rolled back RAG sync ${rollbackId}`, 'success');
  }

  async function syncRagSources(root) {
    const state = currentState(root);
    const sources = selectedRagSources(root);
    if (!sources.length) throw new Error('Select at least one RAG source to sync');
    const response = await fetch(apiUrl(state.apiBase, '/api/rag/sync-sources'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ site_id: readSiteId(root), sources, confirm_sync: true, approved_by: 'admin_customizer' })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to sync RAG sources');
    state.ragSync = body;
    const target = root.querySelector('[data-rag-sync-results]');
    if (target) {
      const summary = body.summary || {};
      target.innerHTML = `<strong>Synced ${escapeHtml(String(summary.synced_items || 0))} items.</strong><p class="muted small">Kept ${escapeHtml(String(summary.kept_manual_items || 0))} existing items. Sources: ${Object.entries(summary.source_counts || {}).map(([key, value]) => `${escapeHtml(key)}=${escapeHtml(String(value))}`).join(', ')}</p>`;
    }
    await loadKnowledgeBase(root);
    await loadRagSources(root);
    status(root, `Synced RAG sources for ${state.siteId}`, 'success');
  }

  function renderRagDebug(root) {
    const state = currentState(root);
    const target = root.querySelector('[data-rag-debug-results]');
    if (!target) return;
    const debug = state.ragDebug;
    if (!debug) {
      target.innerHTML = '<p class="muted small">Run a debug question to see query plan, scores, sources, and answer confidence.</p>';
      return;
    }
    const candidates = Array.isArray(debug.candidates) ? debug.candidates.slice(0, 5) : [];
    target.innerHTML = `
      <h4>Retrieval debug</h4>
      <p class="muted small">Intent: ${escapeHtml(debug.query_plan && debug.query_plan.intent || '')} · Confidence: ${escapeHtml(debug.answer && debug.answer.confidence || '')}</p>
      <p>${escapeHtml(debug.answer && debug.answer.reply || '')}</p>
      ${candidates.map((item) => `<div class="chatbot-rag-debug-row"><strong>${escapeHtml(item.chunk && item.chunk.title || item.chunk && item.chunk.section || 'Candidate')}</strong><span>${escapeHtml(String(item.score || ''))}</span><small>${escapeHtml((item.reasons || []).join(', '))}</small><p>${escapeHtml(item.chunk && item.chunk.text_preview || '')}</p></div>`).join('')}`;
  }

  async function loadRagDebug(root) {
    const state = currentState(root);
    const form = root.querySelector('[data-rag-debug-form]');
    const question = form && form.elements.question.value || '';
    const response = await fetch(apiUrl(state.apiBase, '/api/rag/debug'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ site_id: readSiteId(root), question })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to debug RAG');
    state.ragDebug = body;
    renderRagDebug(root);
    status(root, `Debugged RAG question for ${state.siteId}`, 'success');
  }

  async function loadRagAnswerLog(root) {
    const state = currentState(root);
    const response = await fetch(apiUrl(state.apiBase, `/api/rag/answer-log?site_id=${encodeURIComponent(readSiteId(root))}`), { credentials: 'same-origin' });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to load RAG answer log');
    state.ragAnswerLog = Array.isArray(body.items) ? body.items : [];
    const target = root.querySelector('[data-rag-answer-log]');
    if (target) target.innerHTML = state.ragAnswerLog.length ? state.ragAnswerLog.slice(0, 8).map((item) => `<div class="chatbot-rag-log-item"><strong>${escapeHtml(item.confidence || 'unknown')}</strong><p>${escapeHtml(item.question || '')}</p><small>${escapeHtml(item.answer_source || '')}</small></div>`).join('') : '<p class="muted small">No RAG answer logs yet.</p>';
  }

  async function sendRagFeedback(root, rating) {
    const state = currentState(root);
    const debug = state.ragDebug || {};
    const answer = debug.answer || {};
    const form = root.querySelector('[data-rag-debug-form]');
    const response = await fetch(apiUrl(state.apiBase, '/api/rag/feedback'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ site_id: readSiteId(root), rating, question: form && form.elements.question.value || '', answer: answer.reply || '', reason: 'admin_debug_feedback' })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to save RAG feedback');
    status(root, `Saved ${rating} RAG feedback`, 'success');
  }

  async function runRagEval(root) {
    const state = currentState(root);
    const form = root.querySelector('[data-rag-debug-form]');
    const question = form && form.elements.question.value || 'What does this website offer?';
    const response = await fetch(apiUrl(state.apiBase, '/api/rag/eval'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ site_id: readSiteId(root), cases: [{ question, expected_answer_contains: [], expected_source_contains: [] }] })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to run RAG eval');
    state.ragEval = body;
    const target = root.querySelector('[data-rag-eval-results]');
    if (target) target.innerHTML = `<strong>Eval:</strong> ${escapeHtml(body.summary && body.summary.passed || 0)} / ${escapeHtml(body.summary && body.summary.total || 0)} passed`;
  }

  function bind(root) {
    root.addEventListener('input', (event) => {
      if (event.target.closest('[data-lead-form-editor]')) {
        readFormEditor(root);
        renderPreview(root);
      }
      if (event.target.closest('[data-widget-config-editor]')) {
        widgetConfigPayloadFromForm(root);
        renderWidgetVoicePreview(root);
      }
    });
    root.addEventListener('click', async (event) => {
      const target = event.target;
      if (!(target instanceof Element)) return;
      try {
        if (target.matches('[data-add-field]')) { event.preventDefault(); addFormField(root); }
        if (target.matches('[data-remove-field]')) { event.preventDefault(); removeFormField(root, target.dataset.removeField); }
        if (target.matches('[data-reset-defaults]')) { event.preventDefault(); currentState(root).formConfig = normalizeConfig(DEFAULT_FORM_CONFIG); fillForm(root); renderFieldRows(root); renderPreview(root); }
        if (target.matches('[data-reload-form]')) { event.preventDefault(); await loadFormConfig(root); }
        if (target.matches('[data-reload-widget-config]')) { event.preventDefault(); await loadWidgetConfig(root); }
        if (target.matches('[data-reload-notification-email]')) { event.preventDefault(); await loadNotificationEmailConfig(root); }
        if (target.matches('[data-reload-kb]')) { event.preventDefault(); await loadKnowledgeBase(root); }
        if (target.matches('[data-load-rag-sources]')) { event.preventDefault(); await loadRagSources(root); }
        if (target.matches('[data-preview-rag-sync]')) { event.preventDefault(); await previewRagSync(root); }
        if (target.matches('[data-load-rag-review]')) { event.preventDefault(); await loadRagReview(root); }
        if (target.matches('[data-rollback-rag-sync]')) { event.preventDefault(); await rollbackRagSync(root); }
        if (target.matches('[data-sync-rag-sources]')) { event.preventDefault(); await syncRagSources(root); }
        if (target.matches('[data-save-rag-schedule]')) { event.preventDefault(); await saveRagSchedule(root); }
        if (target.matches('[data-run-rag-scheduled-refresh]')) { event.preventDefault(); await runScheduledRefresh(root); }
        if (target.matches('[data-load-rag-due]')) { event.preventDefault(); await loadRagDue(root); }
        if (target.matches('[data-load-rag-notifications]')) { event.preventDefault(); await loadRagNotifications(root); }
        if (target.matches('[data-mark-rag-notifications-read]')) { event.preventDefault(); await markRagNotificationsRead(root); }
        if (target.matches('[data-clear-kb-form]')) { event.preventDefault(); clearKnowledgeForm(root); }
        if (target.matches('[data-edit-kb]')) { event.preventDefault(); editKnowledgeItem(root, target.dataset.editKb); }
        if (target.matches('[data-delete-kb]')) { event.preventDefault(); await deleteKnowledgeItem(root, target.dataset.deleteKb); }
        if (target.matches('[data-load-rag-answer-log]')) { event.preventDefault(); await loadRagAnswerLog(root); }
        if (target.matches('[data-send-rag-feedback]')) { event.preventDefault(); await sendRagFeedback(root, target.dataset.sendRagFeedback); }
        if (target.matches('[data-run-rag-eval]')) { event.preventDefault(); await runRagEval(root); }
      } catch (error) {
        status(root, error.message, 'error');
      }
    });
    root.querySelector('[data-lead-form-editor]').addEventListener('submit', async (event) => {
      event.preventDefault();
      try { await saveFormConfig(root); } catch (error) { status(root, error.message, 'error'); }
    });
    root.querySelector('[data-widget-config-editor]').addEventListener('submit', async (event) => {
      event.preventDefault();
      try { await saveWidgetConfig(root); } catch (error) { status(root, error.message, 'error'); }
    });
    root.querySelector('[data-notification-email-editor]').addEventListener('submit', async (event) => {
      event.preventDefault();
      try { await saveNotificationEmailConfig(root); } catch (error) { status(root, error.message, 'error'); }
    });
    root.querySelector('[data-kb-editor]').addEventListener('submit', async (event) => {
      event.preventDefault();
      try { await saveKnowledgeItem(root); } catch (error) { status(root, error.message, 'error'); }
    });
    root.querySelector('[data-rag-debug-form]').addEventListener('submit', async (event) => {
      event.preventDefault();
      try { await loadRagDebug(root); } catch (error) { status(root, error.message, 'error'); }
    });
    root.querySelectorAll('[data-rag-source-import]').forEach((form) => {
      form.addEventListener('submit', async (event) => {
        event.preventDefault();
        try { await saveExternalSourceItems(root, form); } catch (error) { status(root, error.message, 'error'); }
      });
    });
    const wordpressPullForm = root.querySelector('[data-rag-wordpress-pull]');
    if (wordpressPullForm) wordpressPullForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      try { await pullWordPressSource(root, wordpressPullForm); } catch (error) { status(root, error.message, 'error'); }
    });
    const uploadExtractForm = root.querySelector('[data-rag-upload-extract]');
    if (uploadExtractForm) uploadExtractForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      try { await extractUploadDocument(root, uploadExtractForm); } catch (error) { status(root, error.message, 'error'); }
    });
  }

  function mountAll() {
    document.querySelectorAll('[data-easiio-chatbot-customizer]').forEach((script) => {
      const selector = script.dataset.rootSelector || '#easiio-chatbot-customizer-root';
      const root = document.querySelector(selector);
      if (!root || root.dataset.chatbotCustomizerReady === 'true') return;
      root.dataset.chatbotCustomizerReady = 'true';
      root.dataset.siteId = script.dataset.siteId || root.dataset.siteId || 'default';
      root.dataset.apiBase = script.dataset.apiBase || root.dataset.apiBase || '.';
      render(root);
    });
  }

  window.EasiioChatbotCustomizer = {
    mount: render,
    loadFormConfig: (root) => loadFormConfig(root),
    saveFormConfig: (root) => saveFormConfig(root),
    loadWidgetConfig: (root) => loadWidgetConfig(root),
    saveWidgetConfig: (root) => saveWidgetConfig(root),
    widgetConfigPayloadFromForm: (root) => widgetConfigPayloadFromForm(root),
    fillWidgetConfigForm: (root) => fillWidgetConfigForm(root),
    renderWidgetVoicePreview: (root) => renderWidgetVoicePreview(root),
    loadNotificationEmailConfig: (root) => loadNotificationEmailConfig(root),
    saveNotificationEmailConfig: (root) => saveNotificationEmailConfig(root),
    notificationEmailPayloadFromForm: (root) => notificationEmailPayloadFromForm(root),
    addFormField: (root) => addFormField(root),
    removeFormField: (root, index) => removeFormField(root, index),
    loadKnowledgeBase: (root) => loadKnowledgeBase(root),
    saveKnowledgeItem: (root) => saveKnowledgeItem(root),
    deleteKnowledgeItem: (root, contentId) => deleteKnowledgeItem(root, contentId),
    loadRagSources: (root) => loadRagSources(root),
    renderRagSources: (root) => renderRagSources(root),
    syncRagSources: (root) => syncRagSources(root),
    saveExternalSourceItems: (root, form) => saveExternalSourceItems(root, form),
    pullWordPressSource: (root, form) => pullWordPressSource(root, form),
    extractUploadDocument: (root, form) => extractUploadDocument(root, form),
    loadRagSchedule: (root) => loadRagSchedule(root),
    saveRagSchedule: (root) => saveRagSchedule(root),
    runScheduledRefresh: (root) => runScheduledRefresh(root),
    loadRagDue: (root) => loadRagDue(root),
    loadRagNotifications: (root) => loadRagNotifications(root),
    renderRagNotifications: (root) => renderRagNotifications(root),
    markRagNotificationsRead: (root) => markRagNotificationsRead(root),
    loadRagDebug: (root) => loadRagDebug(root),
    renderRagDebug: (root) => renderRagDebug(root),
    sendRagFeedback: (root, rating) => sendRagFeedback(root, rating),
    renderPreview: (root) => renderPreview(root),
    defaults: DEFAULT_FORM_CONFIG
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountAll);
  } else {
    mountAll();
  }
})();
