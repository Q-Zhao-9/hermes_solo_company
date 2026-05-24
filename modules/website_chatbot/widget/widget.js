(function () {
  'use strict';

  if (window.EasiioChatbot && window.EasiioChatbot.__initialized) {
    return;
  }

  const SCRIPT = document.currentScript || document.querySelector('script[data-easiio-chatbot]');
  const ROOT_ID = 'easiio-chatbot-root';
  const CSS_ID = 'easiio-chatbot-inline-css';
  const STORAGE_OPENED_KEY = 'easiio_chatbot_auto_opened';
  const STORAGE_VISITOR_KEY = 'easiio_chatbot_visitor_key';
  const STORAGE_CACHE_PREFIX = 'easiio_chatbot_cache_v1';
  const LEAD_PROMPT_PAUSE_MS = 20000;
  const DEFAULT_LEAD_FORM_CONFIG = {
    title: 'Where should we follow up?',
    help_text: 'Optional — close this and keep chatting if you are not ready.',
    submit_label: 'Send to Easiio',
    fields: [
      { name: 'name', label: 'Name', type: 'text', required: false, autocomplete: 'name' },
      { name: 'email', label: 'Work email', type: 'email', required: true, autocomplete: 'email' },
      { name: 'company', label: 'Company', type: 'text', required: false, autocomplete: 'organization' },
      { name: 'message', label: 'Message', type: 'textarea', required: true, autocomplete: '' }
    ]
  };

  const state = {
    config: getConfig(),
    root: null,
    capsule: null,
    panel: null,
    messages: null,
    input: null,
    unread: null,
    greeting: null,
    isOpen: false,
    sessionId: null,
    visitor: {},
    cachedMessages: [],
    questionCount: 0,
    leadPromptTimer: null,
    lastLeadPromptReason: '',
    hasUnread: true,
    leadFormConfig: null
  };

  function getConfig() {
    const script = SCRIPT || document.querySelector('script[data-easiio-chatbot]');
    const ds = script ? script.dataset : {};
    return {
      apiBase: ds.apiBase || 'http://localhost:8099',
      siteId: ds.siteId || 'default',
      organizationName: ds.organizationName || '',
      websiteName: ds.websiteName || '',
      title: ds.title || 'Easiio Assistant',
      primaryColor: ds.primaryColor || '#2563eb',
      position: ds.position || 'bottom-right',
      launcherStyle: ds.launcherStyle || 'bubble',
      launcherSize: ds.launcherSize || 'small',
      avatarUrl: ds.avatarUrl || '',
      greeting: ds.greeting || 'Hi, I can help with AI automation or book a demo.',
      autoOpen: ds.autoOpen === 'true',
      trackPageViews: ds.trackPageViews !== 'false',
      autoOpenDelaySeconds: Number(ds.autoOpenDelaySeconds || 0),
      leadFormsEnabled: ds.leadFormsEnabled === 'true',
      ragAdminEnabled: ds.ragAdmin === 'true' || ds.ragAdminEnabled === 'true',
      // Reads embedded JSON from the script attribute data-lead-form-config.
      leadFormConfig: parseEmbeddedLeadFormConfig(ds.leadFormConfig),
      email: ds.email || '',
      phone: ds.phone || '',
      excludePaths: (ds.excludePaths || '').split(',').map(s => s.trim()).filter(Boolean),
      consentText: ds.consentText || 'By chatting, you agree that we may use your message to follow up about Easiio services.'
    };
  }

  function updateConfig(partial) {
    state.config = Object.assign({}, state.config, partial || {});
    if (partial && partial.leadFormConfig) {
      state.leadFormConfig = normalizeLeadFormConfig(partial.leadFormConfig);
      renderLeadFormFields();
    }
    applyTheme();
    return state.config;
  }

  function parseEmbeddedLeadFormConfig(raw) {
    if (!raw) return null;
    try {
      return normalizeLeadFormConfig(JSON.parse(raw));
    } catch (_error) {
      return null;
    }
  }

  function normalizeLeadFormConfig(config) {
    const base = JSON.parse(JSON.stringify(DEFAULT_LEAD_FORM_CONFIG));
    const source = config && typeof config === 'object' ? config : {};
    const fields = Array.isArray(source.fields) ? source.fields : base.fields;
    const normalized = fields.slice(0, 12).map(field => {
      const name = String(field.name || '').trim();
      const type = String(field.type || 'text').toLowerCase();
      if (!/^[A-Za-z][A-Za-z0-9_-]{0,39}$/.test(name) || !['text', 'email', 'textarea'].includes(type)) return null;
      return {
        name,
        label: String(field.label || field.placeholder || name.replace(/_/g, ' ')).slice(0, 80),
        placeholder: String(field.placeholder || field.label || name.replace(/_/g, ' ')).slice(0, 120),
        type,
        required: Boolean(field.required),
        autocomplete: String(field.autocomplete || '').slice(0, 60)
      };
    }).filter(Boolean);
    return {
      title: String(source.title || base.title).slice(0, 120),
      help_text: String(source.help_text || source.helpText || base.help_text).slice(0, 240),
      submit_label: String(source.submit_label || source.submitLabel || base.submit_label).slice(0, 80),
      fields: normalized.length ? normalized : base.fields
    };
  }

  function currentLeadFormConfig() {
    return state.leadFormConfig || state.config.leadFormConfig || normalizeLeadFormConfig(DEFAULT_LEAD_FORM_CONFIG);
  }

  function getVisitorKey() {
    try {
      let key = localStorage.getItem(STORAGE_VISITOR_KEY);
      if (!key) {
        key = `visitor_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 10)}`;
        localStorage.setItem(STORAGE_VISITOR_KEY, key);
      }
      return key;
    } catch (_error) {
      return `visitor_${Date.now().toString(36)}`;
    }
  }

  function siteStorageKey() {
    return `${STORAGE_CACHE_PREFIX}:${state.config.siteId || 'default'}`;
  }

  function loadCachedState() {
    try {
      const raw = localStorage.getItem(siteStorageKey());
      if (!raw) return { visitor: {}, messages: [] };
      const parsed = JSON.parse(raw);
      return {
        visitor: parsed && typeof parsed.visitor === 'object' ? parsed.visitor : {},
        messages: Array.isArray(parsed && parsed.messages) ? parsed.messages.slice(-30) : []
      };
    } catch (_error) {
      return { visitor: {}, messages: [] };
    }
  }

  function writeCachedState(next) {
    try {
      const current = loadCachedState();
      const value = Object.assign({}, current, next || {}, { updated_at: new Date().toISOString() });
      localStorage.setItem(siteStorageKey(), JSON.stringify(value));
    } catch (_error) {
      // Browser storage may be unavailable in private mode; chat still works.
    }
  }

  function saveCachedVisitor(visitor) {
    const cleaned = Object.assign({}, loadCachedState().visitor, visitor || {});
    writeCachedState({ visitor: cleaned });
  }

  function saveCachedMessage(role, text) {
    const current = loadCachedState();
    const messages = current.messages.concat([{ role, text: String(text || '').slice(0, 2000), at: new Date().toISOString() }]).slice(-30);
    writeCachedState({ messages });
  }

  function hydrateCachedState() {
    const cached = loadCachedState();
    state.visitor = Object.assign({}, cached.visitor || {});
    state.cachedMessages = cached.messages || [];
  }

  function basePayload(extra) {
    return Object.assign({
      site_id: state.config.siteId,
      organization_name: state.config.organizationName,
      website_name: state.config.websiteName,
      visitor_key: getVisitorKey()
    }, extra || {});
  }

  function shouldHideOnThisPage() {
    const path = window.location.pathname || '/';
    return state.config.excludePaths.some(excluded => excluded && path.startsWith(excluded));
  }

  function isMobile() {
    return /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent) ||
      (window.matchMedia && window.matchMedia('(max-width: 769px)').matches);
  }

  function injectCss() {
    if (document.getElementById(CSS_ID)) return;
    const link = document.createElement('link');
    link.id = CSS_ID;
    link.rel = 'stylesheet';
    link.href = resolveAssetUrl('widget.css');
    document.head.appendChild(link);
  }

  function resolveAssetUrl(fileName) {
    if (!SCRIPT || !SCRIPT.src) return fileName;
    return new URL(fileName, SCRIPT.src).toString();
  }

  function createRoot() {
    let existing = document.getElementById(ROOT_ID);
    if (existing) return existing;
    const root = document.createElement('div');
    root.id = ROOT_ID;
    root.setAttribute('aria-live', 'polite');
    document.body.appendChild(root);
    return root;
  }

  function createCapsule() {
    const capsule = document.createElement('div');
    capsule.id = 'easiio-chatbot-capsule';
    capsule.className = `easiio-chatbot-position-${state.config.position} easiio-chatbot-size-${state.config.launcherSize}`;

    const launcher = document.createElement('button');
    launcher.id = 'easiio-chatbot-launcher';
    launcher.type = 'button';
    launcher.className = `easiio-chatbot-launcher-${state.config.launcherStyle}`;
    launcher.setAttribute('aria-label', `Open ${state.config.title}`);
    launcher.innerHTML = launcherContent();
    launcher.addEventListener('click', open);

    const unread = document.createElement('span');
    unread.id = 'easiio-chatbot-unread';
    unread.textContent = '1';
    launcher.appendChild(unread);

    capsule.appendChild(launcher);
    state.unread = unread;

    const quickActions = document.createElement('div');
    quickActions.className = 'easiio-chatbot-quick-actions';
    quickActions.appendChild(quickButton('Chat', open));
    if (state.config.email) {
      quickActions.appendChild(quickLink('Email', `mailto:${state.config.email}`));
    }
    if (state.config.phone) {
      quickActions.appendChild(quickLink('Phone', `tel:${state.config.phone}`));
    }
    capsule.appendChild(quickActions);

    const greeting = document.createElement('button');
    greeting.id = 'easiio-chatbot-greeting';
    greeting.type = 'button';
    greeting.textContent = state.config.greeting;
    greeting.addEventListener('click', open);
    capsule.appendChild(greeting);
    state.greeting = greeting;

    return capsule;
  }

  function launcherContent() {
    if (state.config.launcherStyle === 'avatar' && state.config.avatarUrl) {
      return `<img class="easiio-chatbot-avatar" src="${escapeAttr(state.config.avatarUrl)}" alt="" />`;
    }
    return '<span class="easiio-chatbot-icon">💬</span>';
  }

  function quickButton(label, onClick) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'easiio-chatbot-quick-action';
    btn.textContent = label;
    btn.addEventListener('click', onClick);
    return btn;
  }

  function quickLink(label, href) {
    const link = document.createElement('a');
    link.className = 'easiio-chatbot-quick-action';
    link.href = href;
    link.textContent = label;
    return link;
  }

  function createPanel() {
    const panel = document.createElement('section');
    panel.id = 'easiio-chatbot-panel';
    panel.className = `easiio-chatbot-position-${state.config.position}`;
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', state.config.title);
    panel.setAttribute('aria-hidden', 'true');

    panel.innerHTML = `
      <header class="easiio-chatbot-header">
        <div class="easiio-chatbot-title-wrap">
          <div class="easiio-chatbot-header-avatar">${state.config.avatarUrl ? `<img src="${escapeAttr(state.config.avatarUrl)}" alt="" />` : 'AI'}</div>
          <div>
            <div class="easiio-chatbot-title">${escapeHtml(state.config.title)}</div>
            <div class="easiio-chatbot-subtitle">Typically replies instantly</div>
          </div>
        </div>
        <div class="easiio-chatbot-controls">
          <button type="button" class="easiio-chatbot-minimize" aria-label="Minimize chat">−</button>
          <button type="button" class="easiio-chatbot-close" aria-label="Close chat">×</button>
        </div>
      </header>
      <main class="easiio-chatbot-body">
        <div class="easiio-chatbot-messages" aria-live="polite"></div>
        <div class="easiio-chatbot-actions">
          <button type="button" data-message="I want to book a demo">Book demo</button>
          <button type="button" data-message="Can you tell me about pricing?">Pricing</button>
          <button type="button" data-message="I want to contact sales">Contact sales</button>
          ${state.config.ragAdminEnabled ? '<button type="button" class="easiio-chatbot-rag-open">Knowledge</button>' : ''}
        </div>
        ${state.config.ragAdminEnabled ? ragAdminMarkup() : ''}
        <form id="easiio-chatbot-lead-form" class="easiio-chatbot-lead-form" hidden>
          ${leadFormMarkup()}
        </form>
        <div class="easiio-chatbot-consent">${escapeHtml(state.config.consentText)}</div>
      </main>
      <form class="easiio-chatbot-composer">
        <input class="easiio-chatbot-input" placeholder="Ask about AI agents, automation, demos..." maxlength="2000" />
        <button type="submit">Send</button>
      </form>
    `;

    panel.querySelector('.easiio-chatbot-minimize').addEventListener('click', minimize);
    panel.querySelector('.easiio-chatbot-close').addEventListener('click', close);
    panel.querySelector('.easiio-chatbot-composer').addEventListener('submit', onSubmitMessage);
    panel.querySelector('#easiio-chatbot-lead-form').addEventListener('submit', onSubmitLead);
    panel.querySelector('.easiio-chatbot-lead-dismiss').addEventListener('click', dismissLeadForm);
    if (state.config.ragAdminEnabled) {
      const ragOpen = panel.querySelector('.easiio-chatbot-rag-open');
      const ragForm = panel.querySelector('#easiio-chatbot-rag-form');
      const ragClose = panel.querySelector('.easiio-chatbot-rag-close');
      if (ragOpen) ragOpen.addEventListener('click', openKnowledge);
      if (ragForm) ragForm.addEventListener('submit', onSubmitRagContent);
      if (ragClose) ragClose.addEventListener('click', closeKnowledge);
      loadRagContentList();
    }
    panel.querySelectorAll('.easiio-chatbot-actions button').forEach(button => {
      button.addEventListener('click', () => onQuickAction(button.dataset.message));
    });

    state.messages = panel.querySelector('.easiio-chatbot-messages');
    state.input = panel.querySelector('.easiio-chatbot-input');
    prefillLeadForm(panel);
    return panel;
  }

  function leadFormMarkup() {
    const config = currentLeadFormConfig();
    return `
          <div class="easiio-chatbot-form-header">
            <div class="easiio-chatbot-form-title">${escapeHtml(config.title)}</div>
            <button type="button" class="easiio-chatbot-lead-dismiss" aria-label="Dismiss follow-up form">×</button>
          </div>
          <div class="easiio-chatbot-form-help">${escapeHtml(config.help_text)}</div>
          <div class="easiio-chatbot-lead-fields">${renderLeadFormFields(config)}</div>
          <button type="submit">${escapeHtml(config.submit_label)}</button>`;
  }

  function renderLeadFormFields(config) {
    const formConfig = config || currentLeadFormConfig();
    const markup = formConfig.fields.map(field => {
      const required = field.required ? ' required' : '';
      const autocomplete = field.autocomplete ? ` autocomplete="${escapeAttr(field.autocomplete)}"` : '';
      const common = `name="${escapeAttr(field.name)}" placeholder="${escapeAttr(field.placeholder || field.label)}"${autocomplete}${required}`;
      if (field.type === 'textarea') {
        return `<textarea ${common} rows="3"></textarea>`;
      }
      return `<input ${common} type="${escapeAttr(field.type || 'text')}" />`;
    }).join('');
    const form = state.panel && state.panel.querySelector('#easiio-chatbot-lead-form');
    if (form && !config) {
      form.innerHTML = leadFormMarkup();
      form.addEventListener('submit', onSubmitLead);
      const dismiss = form.querySelector('.easiio-chatbot-lead-dismiss');
      if (dismiss) dismiss.addEventListener('click', dismissLeadForm);
      prefillLeadForm(state.panel);
    }
    return markup;
  }

  function ragAdminMarkup() {
    return `
        <section id="easiio-chatbot-rag-admin" class="easiio-chatbot-rag-admin" hidden>
          <div class="easiio-chatbot-form-header">
            <div>
              <div class="easiio-chatbot-form-title">Website knowledge</div>
              <div class="easiio-chatbot-form-help">Content is saved only for site ID: ${escapeHtml(state.config.siteId || 'default')}</div>
            </div>
            <button type="button" class="easiio-chatbot-rag-close" aria-label="Close knowledge setup">×</button>
          </div>
          <form id="easiio-chatbot-rag-form" class="easiio-chatbot-rag-form">
            <input name="title" placeholder="Knowledge title" required />
            <input name="url" placeholder="Optional source URL" />
            <textarea name="content" placeholder="Paste FAQs, product details, pricing notes, policies, or page content for this website RAG." rows="5" required></textarea>
            <button type="submit">Save to this site's RAG</button>
          </form>
          <div class="easiio-chatbot-rag-list" aria-live="polite"></div>
        </section>`;
  }

  function prefillLeadForm(panel) {
    const form = panel.querySelector('#easiio-chatbot-lead-form');
    if (!form) return;
    const keys = currentLeadFormConfig().fields.map(field => field.name);
    keys.forEach(key => {
      if (state.visitor[key] && form.elements[key]) form.elements[key].value = state.visitor[key];
    });
  }

  function mount() {
    if (shouldHideOnThisPage()) return;
    hydrateCachedState();
    injectCss();
    state.root = createRoot();
    if (!state.capsule) {
      state.capsule = createCapsule();
      state.root.appendChild(state.capsule);
    }
    if (!state.panel) {
      state.panel = createPanel();
      state.root.appendChild(state.panel);
      if (state.cachedMessages.length) {
        state.cachedMessages.forEach(item => addMessage(item.role, item.text, { skipCache: true }));
      } else {
        addMessage('bot', state.config.greeting);
      }
    }
    applyTheme();
    loadLeadFormConfig();
    if (state.config.trackPageViews && state.config.apiBase !== 'mock') {
      ensureSession();
    }
    maybeAutoOpen();
  }

  function applyTheme() {
    if (!state.root) return;
    state.root.style.setProperty('--easiio-chatbot-primary', state.config.primaryColor);
  }

  function maybeAutoOpen() {
    if (!state.config.autoOpen || isMobile()) return;
    if (sessionStorage.getItem(STORAGE_OPENED_KEY) === '1') return;
    sessionStorage.setItem(STORAGE_OPENED_KEY, '1');
    setTimeout(open, Math.max(0, state.config.autoOpenDelaySeconds) * 1000);
  }

  function open() {
    mount();
    ensureSession();
    state.isOpen = true;
    if (state.panel) {
      state.panel.style.display = 'flex';
      state.panel.setAttribute('aria-hidden', 'false');
    }
    if (state.capsule) state.capsule.style.display = 'none';
    if (state.unread) state.unread.hidden = true;
    state.hasUnread = false;
    setTimeout(() => state.input && state.input.focus(), 20);
  }

  function close() {
    state.isOpen = false;
    if (state.panel) {
      state.panel.style.display = 'none';
      state.panel.setAttribute('aria-hidden', 'true');
    }
    if (state.capsule) state.capsule.style.display = 'flex';
  }

  function minimize() {
    close();
  }

  function show() {
    open();
  }

  function openKnowledge() {
    open();
    const panel = state.panel && state.panel.querySelector('#easiio-chatbot-rag-admin');
    if (!panel) return;
    panel.hidden = false;
    loadRagContentList();
  }

  function closeKnowledge() {
    const panel = state.panel && state.panel.querySelector('#easiio-chatbot-rag-admin');
    if (panel) panel.hidden = true;
  }

  function onSubmitMessage(event) {
    event.preventDefault();
    const text = state.input.value.trim();
    if (!text) return;
    state.input.value = '';
    sendMessage(text);
  }

  function onQuickAction(message) {
    if (!message) return;
    sendMessage(message);
    showLeadForm(message, 'quick_action');
  }

  function sendMessage(text) {
    const email = extractEmail(text);
    if (email) {
      state.visitor.email = email;
      saveCachedVisitor({ email });
    }
    state.questionCount += 1;
    clearLeadFormReminder();
    addMessage('user', text);
    setTyping(true);
    callChatApi(text)
      .then(response => {
        setTyping(false);
        addMessage('bot', response.reply || 'Thanks — I saved your message.');
        const shouldPromptForLead = state.config.leadFormsEnabled && !hasContactInfo() && response.show_lead_form;
        if (shouldPromptForLead) {
          showLeadForm(text, 'intent');
        }
      })
      .catch(() => {
        setTyping(false);
        addMessage('bot', 'Sorry, I could not reach the chatbot service. Please try again or email us directly.');
      });
  }

  function setTyping(isTyping) {
    let node = state.messages && state.messages.querySelector('.easiio-chatbot-typing');
    if (isTyping && !node) {
      node = document.createElement('div');
      node.className = 'easiio-chatbot-message easiio-chatbot-message-bot easiio-chatbot-typing';
      node.textContent = 'Typing…';
      state.messages.appendChild(node);
    } else if (!isTyping && node) {
      node.remove();
    }
    scrollMessages();
  }

  function addMessage(role, text, options) {
    if (!state.messages) return;
    const message = document.createElement('div');
    message.className = `easiio-chatbot-message easiio-chatbot-message-${role}`;
    message.textContent = text;
    state.messages.appendChild(message);
    if (!options || !options.skipCache) saveCachedMessage(role, text);
    scrollMessages();
  }

  function scrollMessages() {
    if (state.messages) state.messages.scrollTop = state.messages.scrollHeight;
  }

  function renderRagContentList(items, statusText) {
    const list = state.panel && state.panel.querySelector('.easiio-chatbot-rag-list');
    if (!list) return;
    if (statusText) {
      list.textContent = statusText;
      return;
    }
    const rows = Array.isArray(items) ? items : [];
    if (!rows.length) {
      list.innerHTML = '<div class="easiio-chatbot-rag-empty">No manual knowledge saved for this site yet.</div>';
      return;
    }
    list.innerHTML = rows.map(item => `
      <div class="easiio-chatbot-rag-item" data-content-id="${escapeAttr(item.content_id || '')}">
        <div class="easiio-chatbot-rag-title">${escapeHtml(item.title || 'Knowledge item')}</div>
        <div class="easiio-chatbot-rag-preview">${escapeHtml(item.content || '').slice(0, 180)}</div>
        <button type="button" class="easiio-chatbot-rag-delete">Delete</button>
      </div>`).join('');
    list.querySelectorAll('.easiio-chatbot-rag-delete').forEach(button => {
      button.addEventListener('click', () => deleteRagContent(button.closest('.easiio-chatbot-rag-item').dataset.contentId));
    });
  }

  async function loadLeadFormConfig() {
    if (state.config.leadFormConfig) {
      state.leadFormConfig = normalizeLeadFormConfig(state.config.leadFormConfig);
      renderLeadFormFields();
      return;
    }
    if (state.config.apiBase === 'mock') return;
    try {
      const data = await getJSON(`/api/chat/form-config?site_id=${encodeURIComponent(state.config.siteId || 'default')}`);
      if (data && data.form_config) {
        state.leadFormConfig = normalizeLeadFormConfig(data.form_config);
        renderLeadFormFields();
      }
    } catch (_error) {
      state.leadFormConfig = normalizeLeadFormConfig(DEFAULT_LEAD_FORM_CONFIG);
    }
  }

  async function loadRagContentList() {
    if (!state.config.ragAdminEnabled || state.config.apiBase === 'mock') return;
    try {
      const data = await getJSON(`/api/rag/content?site_id=${encodeURIComponent(state.config.siteId || 'default')}`);
      renderRagContentList(data.items || []);
    } catch (_error) {
      renderRagContentList([], 'Could not load knowledge content.');
    }
  }

  async function onSubmitRagContent(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries());
    renderRagContentList([], 'Saving knowledge...');
    try {
      await postJSON('/api/rag/content', basePayload({
        title: data.title,
        url: data.url,
        content: data.content
      }));
      form.reset();
      await loadRagContentList();
      addMessage('bot', 'Saved that knowledge to this website RAG. You can ask a visitor-style question to test it.');
    } catch (_error) {
      renderRagContentList([], 'Could not save knowledge content.');
    }
  }

  async function deleteRagContent(contentId) {
    if (!contentId) return;
    renderRagContentList([], 'Deleting knowledge...');
    try {
      await postJSON('/api/rag/content/delete', basePayload({ content_id: contentId }));
      await loadRagContentList();
    } catch (_error) {
      renderRagContentList([], 'Could not delete knowledge content.');
    }
  }

  async function ensureSession() {
    if (state.sessionId || state.config.apiBase === 'mock') return state.sessionId;
    try {
      const response = await postJSON('/api/chat/session', basePayload({
        session_id: state.sessionId,
        page_url: window.location.href,
        page_title: document.title,
        referrer: document.referrer,
        page_context: getPageContext()
      }));
      state.sessionId = response.session_id || state.sessionId;
      return state.sessionId;
    } catch (_error) {
      return state.sessionId;
    }
  }

  async function callChatApi(message) {
    if (state.config.apiBase === 'mock') {
      return mockReply(message);
    }
    await ensureSession();
    const payload = basePayload({
      session_id: state.sessionId,
      message,
      visitor: Object.assign({}, state.visitor, { visitor_key: getVisitorKey() }),
      page_context: getPageContext()
    });
    return postJSON('/api/chat/message', payload);
  }

  async function getJSON(path) {
    const response = await fetch(`${state.config.apiBase.replace(/\/$/, '')}${path}`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });
    if (!response.ok) throw new Error(`Chat API failed: ${response.status}`);
    return response.json();
  }

  async function postJSON(path, payload) {
    const response = await fetch(`${state.config.apiBase.replace(/\/$/, '')}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error(`Chat API failed: ${response.status}`);
    return response.json();
  }

  function mockReply(message) {
    const lower = message.toLowerCase();
    const email = extractEmail(message);
    const sales = isSalesIntent(message);
    if (email) {
      state.visitor.email = email;
      return Promise.resolve({
        reply: `Thanks — I captured ${email}. In production this will create/update a Solo CRM contact, add an activity, and create a deal if needed.`,
        lead_captured: true,
        show_lead_form: false
      });
    }
    if (sales || lower.includes('contact')) {
      return Promise.resolve({
        reply: 'I can help with that. Please share your work email, or use the quick form below, and Easiio can follow up.',
        lead_captured: false,
        show_lead_form: true
      });
    }
    return Promise.resolve({
      reply: 'Thanks — this is mock mode. I can answer basic questions now; CRM capture will connect through the backend API next.',
      lead_captured: false
    });
  }

  function isSalesIntent(message) {
    return /demo|pricing|price|quote|proposal|consultation|sales|automation|agent|purchase|buy|contact|human|call|more information|more info|help/i.test(message);
  }

  function hasContactInfo() {
    return Boolean(state.visitor && (state.visitor.email || state.visitor.phone));
  }

  function extractEmail(message) {
    const match = message.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i);
    return match ? match[0] : '';
  }

  function showLeadForm(message, reason) {
    if (!state.config.leadFormsEnabled && reason !== 'quick_action') return;
    if (reason !== 'quick_action' && hasContactInfo()) return;
    open();
    const form = state.panel && state.panel.querySelector('#easiio-chatbot-lead-form');
    if (!form) return;
    clearLeadFormReminder();
    delete form.dataset.dismissedAt;
    form.hidden = false;
    form.removeAttribute('hidden');
    form.dataset.message = message || '';
    form.dataset.reason = reason || 'follow_up';
    state.lastLeadPromptReason = form.dataset.reason;
    scrollMessages();
  }

  function dismissLeadForm() {
    const form = state.panel && state.panel.querySelector('#easiio-chatbot-lead-form');
    if (!form) return;
    form.hidden = true;
    form.dataset.dismissedAt = new Date().toISOString();
    // Let the visitor continue chatting. The form can reappear on the next high
    // intent question, after 3+ questions, or after the 20 second pause timer.
  }

  function clearLeadFormReminder() {
    if (state.leadPromptTimer) {
      clearTimeout(state.leadPromptTimer);
      state.leadPromptTimer = null;
    }
  }

  function scheduleLeadFormReminder(message) {
    if (!state.config.leadFormsEnabled) return;
    if (hasContactInfo()) return;
    clearLeadFormReminder();
    state.leadPromptTimer = setTimeout(() => showLeadForm(message, 'pause_20s'), LEAD_PROMPT_PAUSE_MS);
  }

  function onSubmitLead(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries());
    state.visitor = Object.assign({}, state.visitor, data);
    saveCachedVisitor(state.visitor);
    clearLeadFormReminder();
    form.hidden = true;
    if (state.config.apiBase === 'mock') {
      addMessage('bot', `Thanks ${data.name || 'there'} — I saved your contact details in mock mode. Next step will write this into Solo CRM.`);
      return;
    }
    setTyping(true);
    ensureSession()
      .then(() => postJSON('/api/chat/lead', basePayload(Object.assign({}, data, {
        session_id: state.sessionId,
        message: data.message || form.dataset.message || 'Lead form submitted from website chatbot',
        page_context: getPageContext()
      }))))
      .then(response => {
        setTyping(false);
        addMessage('bot', response.reply || `Thanks ${data.name || 'there'} — I saved your contact details.`);
      })
      .catch(() => {
        setTyping(false);
        addMessage('bot', 'Sorry, I could not save the form right now. Please email us directly.');
      });
  }

  function getPageContext() {
    const params = new URLSearchParams(window.location.search);
    const utm = {};
    for (const [key, value] of params.entries()) {
      if (key.startsWith('utm_')) utm[key.replace(/^utm_/, '')] = value;
    }
    return {
      url: window.location.href,
      title: document.title,
      referrer: document.referrer,
      language: document.documentElement.lang || navigator.language || '',
      content: getWebsiteTextSnapshot(),
      utm
    };
  }

  function getWebsiteTextSnapshot() {
    const main = document.querySelector('main') || document.body;
    const clone = main.cloneNode(true);
    clone.querySelectorAll('script, style, noscript, svg, form, input, button, select, textarea, #easiio-chatbot-root').forEach(node => node.remove());
    return clone.innerText.replace(/\s+/g, ' ').trim().slice(0, 50000);
  }

  function escapeHtml(value) {
    return String(value || '').replace(/[&<>'"]/g, char => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[char]));
  }

  function escapeAttr(value) {
    return escapeHtml(value).replace(/`/g, '&#96;');
  }

  window.EasiioChatbot = {
    __initialized: true,
    set: updateConfig,
    show,
    open,
    close,
    minimize,
    openKnowledge,
    closeKnowledge,
    loadRagContentList,
    getConfig: () => Object.assign({}, state.config),
    _state: state
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
}());
