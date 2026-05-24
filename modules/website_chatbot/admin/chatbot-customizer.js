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

  const FIELD_TYPES = ['text', 'email', 'textarea'];
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
      ragItems: existing.ragItems || [],
      crmConnectors: existing.crmConnectors || { enabled: false, providers: {} }
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
                <h3>CRM connectors</h3>
                <p class="muted small">Enable server-side outbound sync after local Solo CRM lead capture. Store only environment variable names here — never raw tokens, access_token values, or webhook_url values.</p>
              </div>
              <button class="button" type="button" data-reload-crm-connectors>Reload</button>
            </div>
            <form data-crm-connectors-editor class="chatbot-editor-form">
              <label class="chatbot-checkbox"><input name="connectors_enabled" type="checkbox" /> Enable external CRM sync for this site</label>
              <div class="chatbot-connector-grid">
                <fieldset class="chatbot-connector-card">
                  <legend>HubSpot</legend>
                  <label class="chatbot-checkbox"><input name="hubspot_enabled" type="checkbox" /> Enable HubSpot</label>
                  <label>HubSpot token_env<input name="hubspot_token_env" type="text" placeholder="HUBSPOT_PRIVATE_APP_TOKEN" /></label>
                  <label>Pipeline ID<input name="hubspot_pipeline_id" type="text" placeholder="default" /></label>
                  <label>Deal stage<input name="hubspot_dealstage" type="text" placeholder="appointmentscheduled" /></label>
                  <p class="muted small" data-hubspot-status></p>
                </fieldset>
                <fieldset class="chatbot-connector-card">
                  <legend>Google Sheets</legend>
                  <label class="chatbot-checkbox"><input name="google_sheets_enabled" type="checkbox" /> Enable Google Sheets</label>
                  <label>Google Sheets webhook_url_env<input name="google_sheets_webhook_url_env" type="text" placeholder="GOOGLE_SHEETS_LEADS_WEBHOOK_URL" /></label>
                  <label>Sheet name<input name="google_sheets_sheet_name" type="text" placeholder="Leads" /></label>
                  <label>Spreadsheet ID<input name="google_sheets_spreadsheet_id" type="text" placeholder="optional routing id" /></label>
                  <p class="muted small" data-google-sheets-status></p>
                </fieldset>
              </div>
              <div class="chatbot-actions">
                <button class="button primary" type="submit">Save CRM connectors</button>
              </div>
            </form>
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
        </div>
      </section>`;
    bind(root);
    fillForm(root);
    renderFieldRows(root);
    renderPreview(root);
    loadFormConfig(root);
    loadCrmConnectors(root);
    loadKnowledgeBase(root);
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
      fillForm(root);
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
      body: JSON.stringify({ site_id: readSiteId(root), form_config: formConfig })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to save form config');
    state.formConfig = normalizeConfig(body.form_config || formConfig);
    fillForm(root);
    renderFieldRows(root);
    renderPreview(root);
    status(root, `Saved lead form for ${state.siteId}`, 'success');
  }

  function fillCrmConnectors(root) {
    const state = currentState(root);
    const form = root.querySelector('[data-crm-connectors-editor]');
    if (!form) return;
    const cfg = state.crmConnectors || { enabled: false, providers: {} };
    const hubspot = (cfg.providers && cfg.providers.hubspot) || {};
    const sheets = (cfg.providers && cfg.providers.google_sheets) || {};
    form.elements.connectors_enabled.checked = Boolean(cfg.enabled);
    form.elements.hubspot_enabled.checked = Boolean(hubspot.enabled);
    form.elements.hubspot_token_env.value = hubspot.token_env || '';
    form.elements.hubspot_pipeline_id.value = hubspot.pipeline_id || '';
    form.elements.hubspot_dealstage.value = hubspot.dealstage || '';
    form.elements.google_sheets_enabled.checked = Boolean(sheets.enabled);
    form.elements.google_sheets_webhook_url_env.value = sheets.webhook_url_env || '';
    form.elements.google_sheets_sheet_name.value = sheets.sheet_name || '';
    form.elements.google_sheets_spreadsheet_id.value = sheets.spreadsheet_id || '';
    const hubspotStatus = root.querySelector('[data-hubspot-status]');
    const sheetsStatus = root.querySelector('[data-google-sheets-status]');
    if (hubspotStatus) hubspotStatus.textContent = hubspot.enabled ? (hubspot.configured ? 'Configured from server environment.' : 'Enabled but env var is not set on server.') : 'Disabled';
    if (sheetsStatus) sheetsStatus.textContent = sheets.enabled ? (sheets.configured ? 'Configured from server environment.' : 'Enabled but env var is not set on server.') : 'Disabled';
  }

  function readCrmConnectors(root) {
    const form = root.querySelector('[data-crm-connectors-editor]');
    return {
      enabled: Boolean(form.elements.connectors_enabled.checked),
      providers: {
        hubspot: {
          enabled: Boolean(form.elements.hubspot_enabled.checked),
          mode: 'sync_on_lead',
          token_env: form.elements.hubspot_token_env.value,
          pipeline_id: form.elements.hubspot_pipeline_id.value,
          dealstage: form.elements.hubspot_dealstage.value
        },
        google_sheets: {
          enabled: Boolean(form.elements.google_sheets_enabled.checked),
          mode: 'sync_on_lead',
          webhook_url_env: form.elements.google_sheets_webhook_url_env.value,
          sheet_name: form.elements.google_sheets_sheet_name.value,
          spreadsheet_id: form.elements.google_sheets_spreadsheet_id.value
        }
      }
    };
  }

  async function loadCrmConnectors(root) {
    const state = currentState(root);
    try {
      const response = await fetch(apiUrl(state.apiBase, `/api/crm-connectors/config?site_id=${encodeURIComponent(readSiteId(root))}`), { credentials: 'same-origin' });
      const body = await response.json();
      if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to load CRM connectors');
      state.crmConnectors = body.site_config || { enabled: false, providers: {} };
      fillCrmConnectors(root);
      status(root, `Loaded CRM connectors for ${state.siteId}`, 'success');
    } catch (error) {
      status(root, `CRM connector load failed: ${error.message}`, 'warning');
    }
  }

  async function saveCrmConnectors(root) {
    const state = currentState(root);
    const siteConfig = readCrmConnectors(root);
    const response = await fetch(apiUrl(state.apiBase, '/api/crm-connectors/config'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ site_id: readSiteId(root), site_config: siteConfig })
    });
    const body = await response.json();
    if (!response.ok || body.ok === false) throw new Error(body.error || 'Failed to save CRM connectors');
    state.crmConnectors = body.site_config || siteConfig;
    fillCrmConnectors(root);
    status(root, `Saved CRM connectors for ${state.siteId}`, 'success');
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

  function bind(root) {
    root.addEventListener('input', (event) => {
      if (event.target.closest('[data-lead-form-editor]')) {
        readFormEditor(root);
        renderPreview(root);
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
        if (target.matches('[data-reload-crm-connectors]')) { event.preventDefault(); await loadCrmConnectors(root); }
        if (target.matches('[data-reload-kb]')) { event.preventDefault(); await loadKnowledgeBase(root); }
        if (target.matches('[data-clear-kb-form]')) { event.preventDefault(); clearKnowledgeForm(root); }
        if (target.matches('[data-edit-kb]')) { event.preventDefault(); editKnowledgeItem(root, target.dataset.editKb); }
        if (target.matches('[data-delete-kb]')) { event.preventDefault(); await deleteKnowledgeItem(root, target.dataset.deleteKb); }
      } catch (error) {
        status(root, error.message, 'error');
      }
    });
    root.querySelector('[data-lead-form-editor]').addEventListener('submit', async (event) => {
      event.preventDefault();
      try { await saveFormConfig(root); } catch (error) { status(root, error.message, 'error'); }
    });
    root.querySelector('[data-crm-connectors-editor]').addEventListener('submit', async (event) => {
      event.preventDefault();
      try { await saveCrmConnectors(root); } catch (error) { status(root, error.message, 'error'); }
    });
    root.querySelector('[data-kb-editor]').addEventListener('submit', async (event) => {
      event.preventDefault();
      try { await saveKnowledgeItem(root); } catch (error) { status(root, error.message, 'error'); }
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
    loadCrmConnectors: (root) => loadCrmConnectors(root),
    saveCrmConnectors: (root) => saveCrmConnectors(root),
    addFormField: (root) => addFormField(root),
    removeFormField: (root, index) => removeFormField(root, index),
    loadKnowledgeBase: (root) => loadKnowledgeBase(root),
    saveKnowledgeItem: (root) => saveKnowledgeItem(root),
    deleteKnowledgeItem: (root, contentId) => deleteKnowledgeItem(root, contentId),
    renderPreview: (root) => renderPreview(root),
    defaults: DEFAULT_FORM_CONFIG
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountAll);
  } else {
    mountAll();
  }
})();
