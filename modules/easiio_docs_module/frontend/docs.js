(function () {
  'use strict';

  if (window.EasiioDocs && window.EasiioDocs.__initialized) return;

  const SCRIPT = document.currentScript || document.querySelector('script[data-easiio-docs]');
  const DEFAULT_ROOT_ID = 'easiio-docs-root';

  const state = {
    config: getConfig(),
    root: null,
    docs: [],
    activeDoc: null,
    space: null
  };

  function getConfig() {
    const script = SCRIPT || document.querySelector('script[data-easiio-docs]');
    const ds = script ? script.dataset : {};
    return {
      apiBase: ds.apiBase || 'http://localhost:8110',
      siteId: ds.siteId || 'default',
      // Admin embeds use data-mode="admin" only on protected pages.
      mode: ds.mode || 'public',
      rootSelector: ds.rootSelector || `#${DEFAULT_ROOT_ID}`,
      title: ds.title || 'Documentation',
      subtitle: ds.subtitle || 'Guides, manuals, and reusable website documentation.',
      status: ds.status || 'published',
      visibility: ds.visibility || '',
      targetFilter: ds.targetFilter || ds.frameworkTarget || '',
      credentialMode: ds.credentialMode || 'same-origin',
      authToken: ds.authToken || '',
      loginRequired: ds.loginRequired === 'true' || ds.requireLogin === 'true',
      contentFormat: ds.contentFormat || 'markdown'
    };
  }

  function mount() {
    state.root = document.querySelector(state.config.rootSelector) || createRoot();
    state.root.className = `${state.root.className || ''} easiio-docs`.trim();
    state.root.innerHTML = shellMarkup();
    state.root.querySelector('.easiio-docs-search').addEventListener('input', event => loadDocs(event.target.value));
    const targetSelect = state.root.querySelector('.easiio-docs-target-filter');
    if (targetSelect) targetSelect.addEventListener('change', event => { state.config.targetFilter = event.target.value; renderDocs(); });
    if (state.config.mode === 'admin') {
      const editor = state.root.querySelector('.easiio-docs-editor-form');
      if (editor) editor.addEventListener('submit', saveDoc);
      const newButton = state.root.querySelector('.easiio-docs-new');
      if (newButton) newButton.addEventListener('click', () => showEditor());
    }
    loadSpace();
    loadDocs();
  }

  function createRoot() {
    const root = document.createElement('div');
    root.id = DEFAULT_ROOT_ID;
    document.body.appendChild(root);
    return root;
  }

  function shellMarkup() {
    return `
      <section class="easiio-docs-shell" data-mode="${escapeAttr(state.config.mode)}">
        <header class="easiio-docs-header">
          <div>
            <div class="easiio-docs-eyebrow">${escapeHtml(state.config.siteId)}</div>
            <h2>${escapeHtml(state.config.title)}</h2>
            <p>${escapeHtml(state.config.subtitle)}</p>
          </div>
          ${state.config.mode === 'admin' ? '<button type="button" class="easiio-docs-new">New doc</button>' : ''}
        </header>
        <div class="easiio-docs-toolbar">
          <input class="easiio-docs-search" placeholder="Search documentation..." aria-label="Search documentation" />
          <select class="easiio-docs-target-filter" aria-label="Filter by integration target">
            <option value="">All targets</option>
            <option value="nextjs-mdx">Next.js MDX</option>
            <option value="wordpress-shortcode">WordPress</option>
            <option value="sitelet">Sitelet</option>
            <option value="docusaurus">Docusaurus</option>
            <option value="mkdocs">MkDocs</option>
            <option value="hugo">Hugo</option>
            <option value="vitepress">VitePress</option>
            <option value="rag">Chatbot RAG</option>
          </select>
        </div>
        <div class="easiio-docs-summary" aria-live="polite"></div>
        <div class="easiio-docs-layout">
          <nav class="easiio-docs-list" aria-live="polite"></nav>
          <article class="easiio-docs-view"><div class="easiio-docs-empty">Select a documentation page.</div></article>
        </div>
        ${state.config.mode === 'admin' ? editorMarkup() : ''}
      </section>`;
  }

  function editorMarkup() {
    return `
      <section class="easiio-docs-editor" hidden>
        <h3>Edit documentation</h3>
        <form class="easiio-docs-editor-form">
          <input name="slug" placeholder="doc-slug" required />
          <input name="title" placeholder="Document title" required />
          <input name="summary" placeholder="Short summary" />
          <input name="category" placeholder="Category" />
          <input name="tags" placeholder="Tags comma separated" />
          <input name="version_label" placeholder="Version label, e.g. 1.0" />
          <select name="status"><option value="published">Published</option><option value="draft">Draft</option><option value="archived">Archived</option></select>
          <select name="visibility"><option value="public">Public</option><option value="private">Private</option><option value="login_required">Login required</option><option value="internal">Internal</option></select>
          <select name="content_format"><option value="markdown">Markdown</option><option value="mdx">MDX</option><option value="html">HTML</option><option value="text">Text</option></select>
          <input name="framework_targets" placeholder="Targets: sitelet, wordpress-shortcode, rag" />
          <label><input type="checkbox" name="rag_enabled" /> Use in chatbot RAG</label>
          <textarea name="content" rows="10" placeholder="Markdown, MDX, HTML, or text content" required></textarea>
          <div class="easiio-docs-editor-actions">
            <button type="submit">Save doc</button>
            <button type="button" class="easiio-docs-delete">Delete doc</button>
          </div>
        </form>
      </section>`;
  }

  async function loadSpace() {
    try {
      const data = await getJSON(`/api/docs/space?site_id=${encodeURIComponent(state.config.siteId)}`);
      state.space = data.space;
      renderSpace();
    } catch (error) {
      renderError(error);
    }
  }

  async function loadDocs(query) {
    const q = query || '';
    try {
      const visibility = state.config.visibility ? `&visibility=${encodeURIComponent(state.config.visibility)}` : '';
      const data = await getJSON(`/api/docs/docs?site_id=${encodeURIComponent(state.config.siteId)}&status=${encodeURIComponent(state.config.status)}&q=${encodeURIComponent(q)}${visibility}`);
      state.docs = data.docs || [];
      renderDocs();
      if (!state.activeDoc && visibleDocs().length) openDoc(visibleDocs()[0].slug);
    } catch (error) {
      renderError(error);
    }
  }

  function visibleDocs() {
    if (!state.config.targetFilter) return state.docs;
    return state.docs.filter(doc => (doc.framework_targets || []).includes(state.config.targetFilter));
  }

  function renderSpace() {
    const summary = state.root && state.root.querySelector('.easiio-docs-summary');
    if (!summary || !state.space) return;
    const counts = state.space.status_counts || {};
    summary.innerHTML = `
      <span>${Number(state.space.total_docs || 0)} docs</span>
      <span>${Number(counts.published || 0)} published</span>
      <span>${(state.space.categories || []).map(escapeHtml).join(' · ') || 'No categories yet'}</span>`;
  }

  function renderDocs() {
    const list = state.root && state.root.querySelector('.easiio-docs-list');
    if (!list) return;
    const docs = visibleDocs();
    if (!docs.length) {
      list.innerHTML = '<div class="easiio-docs-empty">No documentation pages yet.</div>';
      return;
    }
    list.innerHTML = docs.map(doc => `
      <button type="button" class="easiio-docs-link" data-slug="${escapeAttr(doc.slug)}">
        <strong>${escapeHtml(doc.title)}</strong>
        <span>${escapeHtml(doc.summary || doc.category || '')}</span>
        <small>${escapeHtml(doc.version_label || doc.content_format || '')}</small>
      </button>`).join('');
    list.querySelectorAll('.easiio-docs-link').forEach(button => {
      button.addEventListener('click', () => openDoc(button.dataset.slug));
    });
  }

  async function openDoc(slug) {
    if (!slug) return;
    try {
      const data = await getJSON(`/api/docs/doc?site_id=${encodeURIComponent(state.config.siteId)}&slug=${encodeURIComponent(slug)}`);
      state.activeDoc = data.doc;
      renderDoc(data.doc);
      if (state.config.mode === 'admin') showEditor(data.doc);
    } catch (error) {
      renderError(error);
    }
  }

  function renderDoc(doc) {
    const view = state.root && state.root.querySelector('.easiio-docs-view');
    if (!view || !doc) return;
    view.innerHTML = `
      <header class="easiio-docs-doc-header">
        <div class="easiio-docs-category">${escapeHtml(doc.category || 'Docs')}</div>
        <h1>${escapeHtml(doc.title)}</h1>
        <p>${escapeHtml(doc.summary || '')}</p>
        <div class="easiio-docs-meta">
          <span>${escapeHtml(doc.content_format || state.config.contentFormat)}</span>
          <span>${escapeHtml(doc.visibility || 'public')}</span>
          ${doc.version_label ? `<span>v${escapeHtml(doc.version_label)}</span>` : ''}
        </div>
      </header>
      <div class="easiio-docs-content">${renderContent(doc.content || '', doc.content_format || state.config.contentFormat)}</div>
      <footer class="easiio-docs-footer">
        <div class="easiio-docs-tags">${(doc.tags || []).map(tag => `<span>${escapeHtml(tag)}</span>`).join('')}</div>
        <div class="easiio-docs-targets">${(doc.framework_targets || []).map(target => `<span>${escapeHtml(target)}</span>`).join('')}</div>
      </footer>`;
  }

  function renderContent(content, format) {
    if (format === 'html') return content;
    const escaped = escapeHtml(content);
    return escaped
      .replace(/^### (.*)$/gm, '<h4>$1</h4>')
      .replace(/^## (.*)$/gm, '<h3>$1</h3>')
      .replace(/^# (.*)$/gm, '<h2>$1</h2>')
      .replace(/^- (.*)$/gm, '<li>$1</li>')
      .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/\n\n+/g, '</p><p>')
      .replace(/^/, '<p>')
      .replace(/$/, '</p>')
      .replace(/<p><h/g, '<h')
      .replace(/<\/h([234])><\/p>/g, '</h$1>')
      .replace(/<p><ul>/g, '<ul>')
      .replace(/<\/ul><\/p>/g, '</ul>');
  }

  function showEditor(doc) {
    const panel = state.root && state.root.querySelector('.easiio-docs-editor');
    if (!panel) return;
    panel.hidden = false;
    const form = panel.querySelector('.easiio-docs-editor-form');
    if (!form) return;
    const current = doc || { status: 'published', visibility: 'public', content_format: state.config.contentFormat, framework_targets: [] };
    form.elements.slug.value = current.slug || '';
    form.elements.title.value = current.title || '';
    form.elements.summary.value = current.summary || '';
    form.elements.category.value = current.category || '';
    form.elements.tags.value = (current.tags || []).join(', ');
    form.elements.version_label.value = current.version_label || '';
    form.elements.status.value = current.status || 'published';
    form.elements.visibility.value = current.visibility || 'public';
    form.elements.content_format.value = current.content_format || state.config.contentFormat;
    form.elements.framework_targets.value = (current.framework_targets || []).join(', ');
    form.elements.rag_enabled.checked = Boolean(current.rag_enabled);
    form.elements.content.value = current.content || '';
    const deleteButton = form.querySelector('.easiio-docs-delete');
    if (deleteButton) deleteButton.onclick = () => deleteDoc(form.elements.slug.value);
  }

  async function saveDoc(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries());
    const payload = {
      site_id: state.config.siteId,
      slug: data.slug,
      title: data.title,
      summary: data.summary,
      category: data.category,
      tags: String(data.tags || '').split(',').map(tag => tag.trim()).filter(Boolean),
      version_label: data.version_label,
      status: data.status || 'published',
      visibility: data.visibility || 'public',
      content_format: data.content_format || state.config.contentFormat,
      framework_targets: String(data.framework_targets || '').split(',').map(target => target.trim()).filter(Boolean),
      rag_enabled: Boolean(data.rag_enabled),
      content: data.content
    };
    const saved = await postJSON('/api/docs/doc', payload);
    state.activeDoc = saved.doc;
    await loadSpace();
    await loadDocs();
    renderDoc(saved.doc);
  }

  async function deleteDoc(slug) {
    if (!slug) return;
    await postJSON('/api/docs/doc/delete', { site_id: state.config.siteId, slug });
    state.activeDoc = null;
    await loadSpace();
    await loadDocs();
  }

  async function getJSON(path) {
    const response = await fetch(`${state.config.apiBase.replace(/\/$/, '')}${path}`, {
      credentials: state.config.credentialMode,
      headers: Object.assign({ Accept: 'application/json' }, getAuthHeaders())
    });
    if (!response.ok) handleApiError(response);
    return response.json();
  }

  async function postJSON(path, payload) {
    const response = await fetch(`${state.config.apiBase.replace(/\/$/, '')}${path}`, {
      method: 'POST',
      credentials: state.config.credentialMode,
      headers: Object.assign({ 'Content-Type': 'application/json' }, getAuthHeaders()),
      body: JSON.stringify(payload)
    });
    if (!response.ok) handleApiError(response);
    return response.json();
  }

  function getAuthHeaders() {
    return state.config.authToken ? { Authorization: `Bearer ${state.config.authToken}` } : {};
  }

  function handleApiError(response) {
    if (response.status === 401 && state.config.loginRequired) {
      throw new Error('Docs loginRequired: please sign in to view this documentation.');
    }
    throw new Error(`Docs API failed: ${response.status}`);
  }

  function renderError(error) {
    const view = state.root && state.root.querySelector('.easiio-docs-view');
    if (view) view.innerHTML = `<div class="easiio-docs-error">${escapeHtml(error.message || error)}</div>`;
  }

  function escapeHtml(value) {
    return String(value || '').replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
  }

  function escapeAttr(value) {
    return escapeHtml(value).replace(/`/g, '&#96;');
  }

  window.EasiioDocs = {
    __initialized: true,
    mount,
    loadSpace,
    loadDocs,
    openDoc,
    showEditor,
    saveDoc,
    deleteDoc,
    getAuthHeaders,
    getConfig: () => Object.assign({}, state.config),
    _state: state
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
}());
