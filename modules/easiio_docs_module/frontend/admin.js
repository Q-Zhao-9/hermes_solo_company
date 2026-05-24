(function () {
  'use strict';

  const TARGETS = ['nextjs-mdx', 'docusaurus', 'mkdocs', 'hugo', 'vitepress', 'static-html'];
  const EDITOR_TARGETS = ['nextjs-mdx', 'wordpress-shortcode', 'sitelet', 'docusaurus', 'mkdocs', 'hugo', 'vitepress', 'static-html', 'rag'];
  const state = { preview: null, packageResult: null, docs: [], currentDoc: null, importPreview: null, bundlePreview: null, deploymentPreview: null, deploymentHistory: [] };

  function $(id) { return document.getElementById(id); }

  function apiBase() {
    const value = $('docs-admin-api-base') ? $('docs-admin-api-base').value.trim() : '.';
    return value.replace(/\/$/, '') || '.';
  }

  function siteId() { return ($('docs-admin-site-id') ? $('docs-admin-site-id').value.trim() : ''); }

  function target() {
    const value = $('docs-admin-target') ? $('docs-admin-target').value : 'nextjs-mdx';
    return TARGETS.includes(value) ? value : 'nextjs-mdx';
  }

  function localeFilter() { return ($('docs-admin-locale-filter') ? $('docs-admin-locale-filter').value.trim() : ''); } // locale= query filter

  function fallbackLocale() { return ($('docs-admin-fallback-locale') ? $('docs-admin-fallback-locale').value.trim() : 'en') || 'en'; }

  function deploymentEnvironment() { return ($('docs-admin-deploy-environment') ? $('docs-admin-deploy-environment').value : 'preview') || 'preview'; }

  function historyTarget() { return ($('docs-admin-history-target') ? $('docs-admin-history-target').value : '') || ''; }

  function historyEnvironment() { return ($('docs-admin-history-environment') ? $('docs-admin-history-environment').value : '') || ''; }

  function historyLocale() { return ($('docs-admin-history-locale') ? $('docs-admin-history-locale').value.trim() : '') || ''; }

  function deploymentHistoryParams(limit) {
    const params = new URLSearchParams({ site_id: siteId(), limit: String(limit || 25) });
    if (historyTarget()) params.set('target', historyTarget());
    if (historyEnvironment()) params.set('environment', historyEnvironment());
    if (historyLocale()) params.set('locale', historyLocale());
    return params;
  }

  function packageOpsId() { return ($('docs-admin-package-id') ? $('docs-admin-package-id').value.trim() : ''); }

  function compareLeftId() { return ($('docs-admin-compare-left-id') ? $('docs-admin-compare-left-id').value.trim() : ''); }

  function compareRightId() { return ($('docs-admin-compare-right-id') ? $('docs-admin-compare-right-id').value.trim() : ''); }

  function checklistPayload() {
    const raw = $('docs-admin-checklist-json') ? $('docs-admin-checklist-json').value.trim() : '';
    if (!raw) return {};
    return JSON.parse(raw);
  }

  function approvalStatus() { return ($('docs-admin-approval-status') ? $('docs-admin-approval-status').value : 'reviewed') || 'reviewed'; }
  function approvalActor() { return ($('docs-admin-approval-actor') ? $('docs-admin-approval-actor').value.trim() : 'easiio-docs-admin-ui') || 'easiio-docs-admin-ui'; }
  function approvalNote() { return ($('docs-admin-approval-note') ? $('docs-admin-approval-note').value.trim() : '') || ''; }
  function releaseStatusFilter() { return ($('docs-admin-release-status-filter') ? $('docs-admin-release-status-filter').value.trim() : '') || ''; }
  function releaseDashboardQuery(limit) {
    const params = new URLSearchParams({ site_id: siteId(), limit: String(limit || 25) });
    if (historyTarget()) params.set('target', historyTarget());
    if (historyEnvironment()) params.set('environment', historyEnvironment());
    if (historyLocale()) params.set('locale', historyLocale());
    if (releaseStatusFilter()) params.set('approval_status', releaseStatusFilter());
    return params.toString();
  }

  function ownerToken() { return ($('docs-admin-owner-token') ? $('docs-admin-owner-token').value.trim() : ''); }

  function authHeaders(extraHeaders) {
    const headers = Object.assign({}, extraHeaders || {});
    const token = ownerToken();
    if (token) headers.Authorization = `Bearer ${token}`;
    return headers;
  }

  function setStatus(message, kind) {
    const el = $('docs-admin-status');
    if (!el) return;
    el.textContent = message;
    el.dataset.kind = kind || 'info';
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
  }

  function endpoint(path) { return `${apiBase()}${path}`; }

  async function fetchJson(url, options) {
    const response = await fetch(url, options || {});
    const body = await response.json().catch(() => ({}));
    if (!response.ok && !body.error) body.error = `HTTP ${response.status}`;
    return { status: response.status, body };
  }

  function csvToList(value) {
    return String(value || '').split(',').map(item => item.trim()).filter(Boolean);
  }

  function setValue(id, value) {
    const el = $(id);
    if (el) el.value = value == null ? '' : String(value);
  }

  function checkedTargets() {
    const field = $('docs-admin-framework-targets');
    if (!field) return [];
    return Array.from(field.querySelectorAll('input[type="checkbox"]:checked')).map(input => input.value).filter(value => EDITOR_TARGETS.includes(value));
  }

  function setCheckedTargets(targets) {
    const selected = new Set(Array.isArray(targets) ? targets : []);
    const field = $('docs-admin-framework-targets');
    if (!field) return;
    field.querySelectorAll('input[type="checkbox"]').forEach(input => { input.checked = selected.has(input.value); });
  }

  function collectEditorPayload() {
    return {
      site_id: siteId(),
      slug: $('docs-admin-slug') ? $('docs-admin-slug').value.trim() : '',
      title: $('docs-admin-title') ? $('docs-admin-title').value.trim() : '',
      summary: $('docs-admin-summary-field') ? $('docs-admin-summary-field').value : '',
      content: $('docs-admin-content') ? $('docs-admin-content').value : '',
      content_format: $('docs-admin-content-format') ? $('docs-admin-content-format').value : 'markdown',
      status: $('docs-admin-status-field') ? $('docs-admin-status-field').value : 'draft',
      visibility: $('docs-admin-visibility') ? $('docs-admin-visibility').value : 'public',
      category: $('docs-admin-category') ? $('docs-admin-category').value.trim() : '',
      tags: csvToList($('docs-admin-tags') ? $('docs-admin-tags').value : ''),
      version_label: $('docs-admin-version-label') ? $('docs-admin-version-label').value.trim() : '',
      locale: $('docs-admin-locale') ? $('docs-admin-locale').value.trim() : 'en',
      framework_targets: checkedTargets(),
      rag_enabled: Boolean($('docs-admin-rag-enabled') && $('docs-admin-rag-enabled').checked),
      changed_by: $('docs-admin-changed-by') ? $('docs-admin-changed-by').value.trim() : 'easiio-docs-admin-ui',
    };
  }

  function populateEditor(doc) {
    const value = doc || { status: 'draft', visibility: 'public', content_format: 'markdown', locale: 'en', changed_by: 'easiio-docs-admin-ui', framework_targets: ['sitelet', 'static-html'], rag_enabled: false };
    state.currentDoc = value;
    setValue('docs-admin-slug', value.slug || '');
    setValue('docs-admin-title', value.title || '');
    setValue('docs-admin-summary-field', value.summary || '');
    setValue('docs-admin-content', value.content || '');
    setValue('docs-admin-content-format', value.content_format || 'markdown');
    setValue('docs-admin-status-field', value.status || 'draft');
    setValue('docs-admin-visibility', value.visibility || 'public');
    setValue('docs-admin-category', value.category || '');
    setValue('docs-admin-tags', Array.isArray(value.tags) ? value.tags.join(', ') : '');
    setValue('docs-admin-version-label', value.version_label || '');
    setValue('docs-admin-locale', value.locale || 'en');
    setValue('docs-admin-changed-by', value.changed_by || 'easiio-docs-admin-ui');
    setCheckedTargets(value.framework_targets || []);
    const rag = $('docs-admin-rag-enabled');
    if (rag) rag.checked = Boolean(value.rag_enabled);
  }

  function renderDocList(docs) {
    const el = $('docs-admin-doc-list');
    if (!el) return;
    if (!docs || !docs.length) {
      el.className = 'easiio-docs-admin-list-empty';
      el.innerHTML = 'No docs found for this site.';
      return;
    }
    el.className = 'easiio-docs-admin-doc-list-items';
    el.innerHTML = docs.map(doc => `
      <button type="button" data-edit-doc="${escapeHtml(doc.slug)}">
        <strong>${escapeHtml(doc.title || doc.slug)}</strong>
        <span>${escapeHtml(doc.slug)} · ${escapeHtml(doc.status)} · ${escapeHtml(doc.visibility)}</span>
      </button>
    `).join('');
    el.querySelectorAll('[data-edit-doc]').forEach(button => button.addEventListener('click', () => editDoc(button.getAttribute('data-edit-doc') || '')));
  }

  async function loadDocs() {
    const sid = siteId();
    if (!sid) { setStatus('site_id is required before loading docs.', 'error'); return null; }
    setStatus('Loading docs...', 'info');
    const params = new URLSearchParams({ site_id: sid, status: '', visibility: '' });
    if (localeFilter()) params.set('locale', localeFilter());
    const { status, body } = await fetchJson(endpoint(`/api/docs/docs?${params}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Failed to load docs.', 'error'); return null; }
    state.docs = body.docs || [];
    renderDocList(state.docs);
    setStatus(`Loaded ${state.docs.length} docs.`, 'success');
    return state.docs;
  }

  async function editDoc(slug) {
    const sid = siteId();
    if (!sid || !slug) { setStatus('site_id and slug are required to edit.', 'error'); return null; }
    const params = new URLSearchParams({ site_id: sid, slug });
    if (localeFilter()) params.set('locale', localeFilter());
    if (fallbackLocale()) params.set('fallback_locale', fallbackLocale());
    const { status, body } = await fetchJson(endpoint(`/api/docs/doc?${params}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Failed to load doc.', 'error'); return null; }
    populateEditor(body.doc);
    setStatus(`Editing ${body.doc.slug}.`, 'success');
    return body.doc;
  }

  async function saveDoc() {
    const payload = collectEditorPayload();
    if (!payload.site_id || !payload.slug || !payload.title) { setStatus('site_id, slug, and title are required before saving.', 'error'); return null; }
    setStatus('Saving doc revision...', 'info');
    const { status, body } = await fetchJson(endpoint('/api/docs/doc'), {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload),
    });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Save failed.', 'error'); return null; }
    populateEditor(body.doc);
    await loadDocs();
    setStatus(`Saved ${body.doc.slug}. A new revision was recorded.`, 'success');
    return body.doc;
  }

  async function deleteDoc() {
    const payload = collectEditorPayload();
    if (!payload.site_id || !payload.slug) { setStatus('site_id and slug are required before deleting.', 'error'); return null; }
    if (!window.confirm(`Delete ${payload.slug}? This removes the current doc record.`)) { setStatus('Delete cancelled.', 'info'); return null; }
    const { status, body } = await fetchJson(endpoint('/api/docs/doc/delete'), {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ site_id: payload.site_id, slug: payload.slug }),
    });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Delete failed.', 'error'); return null; }
    populateEditor(null);
    await loadDocs();
    setStatus(`Deleted ${payload.slug}.`, 'success');
    return body;
  }

  function renderRevisions(revisions) {
    const el = $('docs-admin-revisions-panel');
    if (!el) return;
    if (!revisions || !revisions.length) { el.innerHTML = 'No revisions found.'; return; }
    el.innerHTML = revisions.map(rev => `
      <article>
        <strong>${escapeHtml(rev.version_label || 'revision')}</strong>
        <span>${escapeHtml(rev.changed_by || 'unknown')} · ${escapeHtml(rev.created_at || '')}</span>
        <p>${escapeHtml((rev.content || '').slice(0, 220))}</p>
      </article>
    `).join('');
  }

  async function loadRevisions() {
    const payload = collectEditorPayload();
    if (!payload.site_id || !payload.slug) { setStatus('site_id and slug are required before loading revisions.', 'error'); return null; }
    const params = new URLSearchParams({ site_id: payload.site_id, slug: payload.slug });
    const { status, body } = await fetchJson(endpoint(`/api/docs/revisions?${params}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Failed to load revisions.', 'error'); return null; }
    renderRevisions(body.revisions || []);
    setStatus(`Loaded ${(body.revisions || []).length} revisions for ${payload.slug}.`, 'success');
    return body.revisions || [];
  }

  function renderSummary(preview) {
    const el = $('docs-admin-summary');
    if (!el) return;
    if (!preview) { el.innerHTML = ''; return; }
    el.innerHTML = `
      <div class="easiio-docs-admin-stat"><strong>${escapeHtml(preview.target)}</strong><span>Target</span></div>
      <div class="easiio-docs-admin-stat"><strong>${escapeHtml(preview.documentCount || 0)}</strong><span>Documents</span></div>
      <div class="easiio-docs-admin-stat"><strong>${escapeHtml(preview.fileCount || 0)}</strong><span>Files</span></div>
      <div class="easiio-docs-admin-stat"><strong>${preview.requiresExportApproval ? 'Required' : 'Not required'}</strong><span>Approval</span></div>
      <div class="easiio-docs-admin-stat"><strong>${preview.packageBlocked ? 'Blocked' : 'Ready'}</strong><span>Package</span></div>
    `;
  }

  function renderFilePreview(file) {
    return `
      <article class="easiio-docs-admin-file">
        <header><strong>${escapeHtml(file.path)}</strong><button type="button" data-copy-path="${escapeHtml(file.path)}">Copy path</button></header>
        <pre><code>${escapeHtml(file.content || '')}</code></pre>
      </article>
    `;
  }

  function renderFiles(files) {
    const el = $('docs-admin-files');
    if (!el) return;
    if (!files || !files.length) { el.innerHTML = '<p class="easiio-docs-admin-empty">No files generated yet.</p>'; return; }
    el.innerHTML = files.map(renderFilePreview).join('');
    el.querySelectorAll('[data-copy-path]').forEach(button => {
      button.addEventListener('click', async () => {
        const path = button.getAttribute('data-copy-path') || '';
        try { await navigator.clipboard.writeText(path); setStatus(`Copied ${path}`, 'success'); }
        catch (_) { setStatus(path, 'info'); }
      });
    });
  }

  async function previewExport() {
    const sid = siteId();
    if (!sid) { setStatus('site_id is required before previewing.', 'error'); return null; }
    setStatus('Loading export preview...', 'info');
    const params = new URLSearchParams({ site_id: sid, target: target() });
    if (localeFilter()) params.set('locale', localeFilter());
    const { status, body } = await fetchJson(endpoint(`/api/docs/export/preview?${params}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Preview failed.', 'error'); return null; }
    state.preview = body;
    renderSummary(body);
    renderFiles(body.files || []);
    setStatus(`Preview ready: ${body.fileCount || 0} files. requiresExportApproval=${Boolean(body.requiresExportApproval)} packageBlocked=${Boolean(body.packageBlocked)}`, 'success');
    return body;
  }

  async function createPackage() {
    const sid = siteId();
    if (!sid) { setStatus('site_id is required before packaging.', 'error'); return null; }
    if (!state.preview || state.preview.site_id !== sid || state.preview.target !== target()) {
      const preview = await previewExport();
      if (!preview) return null;
    }
    const confirmed = window.confirm('Create approved export ZIP for reviewed published public docs?');
    if (!confirmed) { setStatus('Package creation cancelled. confirmExportPackage was not sent.', 'info'); return null; }
    setStatus('Creating approved ZIP package...', 'info');
    const { status, body } = await fetchJson(endpoint('/api/docs/export/package'), {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ site_id: sid, target: target(), locale: localeFilter(), confirmExportPackage: true, approvedBy: 'easiio-docs-admin-ui' }),
    });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Package creation failed.', 'error'); return null; }
    state.packageResult = body;
    setStatus(`ZIP created: ${body.packagePath} (${body.packageSize} bytes)`, 'success');
    downloadPackage(body);
    return body;
  }

  function downloadPackage(result) {
    const el = $('docs-admin-summary');
    if (!el || !result) return;
    const card = document.createElement('div');
    card.className = 'easiio-docs-admin-stat easiio-docs-admin-package';
    card.innerHTML = `<strong>${escapeHtml(result.packageSize || 0)} bytes</strong><span>${escapeHtml(result.packagePath || 'ZIP package created')}</span>`;
    el.appendChild(card);
  }

  function importPayload() {
    let files = [];
    const raw = $('docs-admin-import-files') ? $('docs-admin-import-files').value.trim() : '';
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) files = parsed;
      else if (parsed && typeof parsed === 'object') return {
        site_id: siteId(),
        source_format: 'easiio-bundle',
        bundle: parsed,
        default_status: $('docs-admin-import-status') ? $('docs-admin-import-status').value : 'draft',
        default_visibility: $('docs-admin-import-visibility') ? $('docs-admin-import-visibility').value : 'private',
        locale: localeFilter(),
      };
    }
    return {
      site_id: siteId(),
      source_format: $('docs-admin-import-source-format') ? $('docs-admin-import-source-format').value : 'markdown-folder',
      files,
      default_status: $('docs-admin-import-status') ? $('docs-admin-import-status').value : 'draft',
      default_visibility: $('docs-admin-import-visibility') ? $('docs-admin-import-visibility').value : 'private',
      locale: localeFilter(),
      framework_targets: checkedTargets(),
      rag_enabled: Boolean($('docs-admin-rag-enabled') && $('docs-admin-rag-enabled').checked),
    };
  }

  function renderImportPreview(preview) {
    const el = $('docs-admin-files');
    if (!el) return;
    const docs = preview && preview.documents ? preview.documents : [];
    if (!docs.length) { el.innerHTML = '<p class="easiio-docs-admin-empty">No importable docs detected.</p>'; return; }
    el.innerHTML = docs.map(doc => `
      <article class="easiio-docs-admin-file">
        <header><strong>${escapeHtml(doc.slug)}</strong><span>${doc.conflict ? 'Conflict / update' : 'Create'}</span></header>
        <p>${escapeHtml(doc.title || '')} · ${escapeHtml(doc.status || '')} · ${escapeHtml(doc.visibility || '')} · ${escapeHtml(doc.locale || '')}</p>
        <p>${escapeHtml(doc.path || '')}</p>
      </article>
    `).join('');
  }

  async function previewImport() {
    if (!siteId()) { setStatus('site_id is required before import preview.', 'error'); return null; }
    let payload;
    try { payload = importPayload(); }
    catch (error) { setStatus(`Invalid import JSON: ${error.message}`, 'error'); return null; }
    setStatus('Previewing import and checking slug conflicts...', 'info');
    const { status, body } = await fetchJson(endpoint('/api/docs/import/preview'), {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload),
    });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Import preview failed.', 'error'); return null; }
    state.importPreview = body;
    renderSummary({ target: body.source_format, documentCount: body.documentCount, fileCount: body.documentCount, requiresExportApproval: body.requiresImportApproval, packageBlocked: body.importBlocked });
    renderImportPreview(body);
    setStatus(`Import preview ready: ${body.documentCount || 0} docs, ${body.conflictCount || 0} conflicts.`, 'success');
    return body;
  }

  async function executeImport() {
    let payload;
    try { payload = importPayload(); }
    catch (error) { setStatus(`Invalid import JSON: ${error.message}`, 'error'); return null; }
    const confirmed = window.confirm('Execute approved import? Existing slugs may be updated.');
    if (!confirmed) { setStatus('Import cancelled. confirmImport was not sent.', 'info'); return null; }
    const { status, body } = await fetchJson(endpoint('/api/docs/import/execute'), {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(Object.assign({}, payload, { confirmImport: true, approvedBy: 'easiio-docs-admin-ui' })),
    });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Import failed.', 'error'); return null; }
    setStatus(`Imported ${body.importedCount || 0} docs.`, 'success');
    await loadDocs();
    return body;
  }

  async function previewBundle() {
    const sid = siteId();
    if (!sid) { setStatus('site_id is required before bundle preview.', 'error'); return null; }
    const params = new URLSearchParams({ site_id: sid });
    if (localeFilter()) params.set('locale', localeFilter());
    const { status, body } = await fetchJson(endpoint(`/api/docs/bundle/preview?${params}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Bundle preview failed.', 'error'); return null; }
    state.bundlePreview = body;
    renderSummary({ target: 'portable-bundle', documentCount: body.documentCount, fileCount: 1, requiresExportApproval: body.requiresBundleApproval, packageBlocked: body.bundleBlocked });
    renderFiles([{ path: 'easiio-docs-bundle.json', content: JSON.stringify(body.bundle || {}, null, 2) }]);
    setStatus(`Portable bundle preview ready: ${body.documentCount || 0} docs.`, 'success');
    return body;
  }

  async function packageBundle() {
    const sid = siteId();
    if (!sid) { setStatus('site_id is required before bundle package.', 'error'); return null; }
    if (!window.confirm('Create approved portable Easiio Docs bundle ZIP?')) { setStatus('Bundle package cancelled. confirmBundlePackage was not sent.', 'info'); return null; }
    const { status, body } = await fetchJson(endpoint('/api/docs/bundle/package'), {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ site_id: sid, locale: localeFilter(), confirmBundlePackage: true, approvedBy: 'easiio-docs-admin-ui' }),
    });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Bundle package failed.', 'error'); return null; }
    setStatus(`Portable bundle ZIP created: ${body.packagePath}`, 'success');
    downloadPackage(body);
    return body;
  }

  async function previewDeployment() {
    const sid = siteId();
    if (!sid) { setStatus('site_id is required before deployment handoff preview.', 'error'); return null; }
    const params = new URLSearchParams({ site_id: sid, target: target(), environment: deploymentEnvironment() });
    if (localeFilter()) params.set('locale', localeFilter());
    setStatus('Previewing deployment handoff package...', 'info');
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/preview?${params}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Deployment handoff preview failed.', 'error'); return null; }
    state.deploymentPreview = body;
    renderSummary({ target: body.deploymentTarget, documentCount: body.documentCount, fileCount: body.fileCount, requiresExportApproval: body.requiresDeploymentApproval, packageBlocked: body.deploymentBlocked });
    renderFiles(body.files || []);
    setStatus(`Deployment handoff preview ready: ${body.fileCount || 0} files for ${body.environment}.`, 'success');
    return body;
  }

  async function packageDeployment() {
    const sid = siteId();
    if (!sid) { setStatus('site_id is required before deployment handoff package.', 'error'); return null; }
    const confirmed = window.confirm('Create approved deployment handoff ZIP? This does not publish externally.');
    if (!confirmed) { setStatus('Deployment package cancelled. confirmDeploymentPackage was not sent.', 'info'); return null; }
    const { status, body } = await fetchJson(endpoint('/api/docs/deploy/package'), {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ site_id: sid, target: target(), environment: deploymentEnvironment(), locale: localeFilter(), confirmDeploymentPackage: true, approvedBy: 'easiio-docs-admin-ui' }),
    });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Deployment handoff package failed.', 'error'); return null; }
    setStatus(`Deployment handoff ZIP created: ${body.packagePath}${body.auditRecorded ? ' · audit recorded' : ''}`, 'success');
    downloadPackage(body);
    await loadDeploymentHistory();
    return body;
  }

  function renderDeploymentHistory(history) {
    const el = $('docs-admin-files');
    if (!el) return;
    const rows = Array.isArray(history) ? history : [];
    if (!rows.length) { el.innerHTML = '<p class="easiio-docs-admin-empty">No deployment history yet.</p>'; return; }
    el.innerHTML = rows.map(item => `
      <article class="easiio-docs-admin-file">
        <header><strong>${escapeHtml(item.deploymentTarget || '')} · ${escapeHtml(item.environment || '')}</strong><span>${escapeHtml(item.event_type || 'deployment_package_created')}</span></header>
        <p>${escapeHtml(item.site_id || '')} · ${escapeHtml(item.locale || 'all')} · ${escapeHtml(item.documentCount || 0)} docs · ${escapeHtml(item.fileCount || 0)} files · ${escapeHtml(item.packageSize || 0)} bytes</p>
        <p>${escapeHtml(item.packagePath || '')}</p>
        <p>Approved by ${escapeHtml(item.approvedBy || 'unknown')} · ${escapeHtml(item.created_at || '')}</p>
      </article>
    `).join('');
  }

  function renderDeploymentSummary(summary) {
    const el = $('docs-admin-summary');
    if (!el) return;
    const totals = summary && summary.totals ? summary.totals : {};
    const counts = summary && summary.counts ? summary.counts : { targets: {}, environments: {}, locales: {} };
    const listCounts = obj => Object.keys(obj || {}).map(key => `${escapeHtml(key)}: ${escapeHtml(obj[key])}`).join(' · ') || 'none';
    el.innerHTML = `
      <article class="easiio-docs-admin-card">
        <strong>Deployment audit summary</strong>
        <p>${escapeHtml(totals.count || 0)} packages · ${escapeHtml(totals.packageSize || 0)} bytes · ${escapeHtml(totals.documentCount || 0)} docs · ${escapeHtml(totals.fileCount || 0)} files</p>
        <p>Targets: ${listCounts(counts.targets)}</p>
        <p>Environments: ${listCounts(counts.environments)}</p>
        <p>Locales: ${listCounts(counts.locales)}</p>
      </article>
    `;
  }

  async function loadDeploymentSummary() {
    const sid = siteId();
    if (!sid) { setStatus('site_id is required before loading audit summary.', 'error'); return null; }
    const params = deploymentHistoryParams(10);
    setStatus('Loading deployment audit summary...', 'info');
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/summary?${params}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Deployment summary failed.', 'error'); return null; }
    renderDeploymentSummary(body);
    renderDeploymentHistory(body.latest || []);
    setStatus(`Loaded audit summary for ${body.totals ? body.totals.count : 0} package(s).`, 'success');
    return body;
  }

  async function loadDeploymentHistory() {
    const sid = siteId();
    if (!sid) { setStatus('site_id is required before loading deployment history.', 'error'); return null; }
    const params = deploymentHistoryParams(25);
    setStatus('Loading deployment history...', 'info');
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/history?${params}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Deployment history failed.', 'error'); return null; }
    state.deploymentHistory = body.history || [];
    renderDeploymentHistory(state.deploymentHistory);
    setStatus(`Loaded ${body.count || 0} deployment history record(s).`, 'success');
    return body;
  }

  async function exportDeploymentHistoryCsv() {
    const sid = siteId();
    if (!sid) { setStatus('site_id is required before exporting deployment history CSV.', 'error'); return null; }
    const params = deploymentHistoryParams(500);
    setStatus('Exporting deployment history CSV...', 'info');
    const response = await fetch(endpoint(`/api/docs/deploy/history.csv?${params}`), { headers: authHeaders() });
    if (!response.ok) { setStatus(`Deployment history CSV failed: HTTP ${response.status}`, 'error'); return null; }
    const csv = await response.text();
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${sid}-deployment-history.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    setStatus('Deployment history CSV exported.', 'success');
    return csv;
  }

  function renderDeploymentPackageDetail(detail) {
    const el = $('docs-admin-files');
    if (!el) return;
    const pkg = detail && detail.package ? detail.package : {};
    const checklist = detail && detail.checklist ? detail.checklist : {};
    const checklistRows = Object.keys(checklist).map(key => {
      const item = checklist[key] || {};
      return `<li>${escapeHtml(key)}: ${item.completed ? 'done' : 'pending'}${item.note ? ` — ${escapeHtml(item.note)}` : ''}</li>`;
    }).join('');
    el.innerHTML = `
      <article class="easiio-docs-admin-file">
        <header><strong>Package #${escapeHtml(pkg.id || '')}</strong><span>${escapeHtml(pkg.deploymentTarget || '')} · ${escapeHtml(pkg.environment || '')}</span></header>
        <p>${escapeHtml(pkg.packagePath || '')}</p>
        <p>${escapeHtml(pkg.documentCount || 0)} docs · ${escapeHtml(pkg.fileCount || 0)} files · ${escapeHtml(pkg.packageSize || 0)} bytes · exists: ${detail.packageExists ? 'yes' : 'no'}</p>
        <p>Manifest files: ${(detail.manifestFiles || []).map(escapeHtml).join(', ')}</p>
        <ul>${checklistRows}</ul>
      </article>
    `;
  }

  async function loadDeploymentPackageDetail() {
    const id = packageOpsId();
    if (!id) { setStatus('Package audit ID is required.', 'error'); return null; }
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/package?id=${encodeURIComponent(id)}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Package detail failed.', 'error'); return null; }
    renderDeploymentPackageDetail(body);
    setStatus(`Loaded package #${id}.`, 'success');
    return body;
  }

  async function downloadDeploymentPackage() {
    const id = packageOpsId();
    if (!id) { setStatus('Package audit ID is required before download.', 'error'); return null; }
    const response = await fetch(endpoint(`/api/docs/deploy/package/download?id=${encodeURIComponent(id)}`), { headers: authHeaders() });
    if (!response.ok) { setStatus(`Package download failed: HTTP ${response.status}`, 'error'); return null; }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `easiio-docs-deployment-${id}.zip`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    setStatus(`Downloaded package #${id}.`, 'success');
    return blob;
  }

  async function compareDeploymentPackages() {
    const left = compareLeftId();
    const right = compareRightId();
    if (!left || !right) { setStatus('Both compare package IDs are required.', 'error'); return null; }
    const params = new URLSearchParams({ left_id: left, right_id: right });
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/compare?${params}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Package comparison failed.', 'error'); return null; }
    const el = $('docs-admin-files');
    if (el) {
      const diff = body.fileDiff || {};
      el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Compare #${escapeHtml(left)} → #${escapeHtml(right)}</strong><span>manifest diff</span></header><p>Only left: ${(diff.onlyInLeft || []).map(escapeHtml).join(', ') || 'none'}</p><p>Only right: ${(diff.onlyInRight || []).map(escapeHtml).join(', ') || 'none'}</p><p>Shared: ${(diff.shared || []).length}</p></article>`;
    }
    setStatus(`Compared package #${left} and #${right}.`, 'success');
    return body;
  }

  async function updateDeploymentChecklist() {
    const id = packageOpsId();
    if (!id) { setStatus('Package audit ID is required before checklist update.', 'error'); return null; }
    let checklist;
    try { checklist = checklistPayload(); }
    catch (error) { setStatus(`Invalid checklist JSON: ${error.message}`, 'error'); return null; }
    const { status, body } = await fetchJson(endpoint('/api/docs/deploy/checklist'), {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ id, checklist, updatedBy: 'easiio-docs-admin-ui' }),
    });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Checklist update failed.', 'error'); return null; }
    renderDeploymentPackageDetail({ package: body.package, checklist: body.checklist, packageExists: true, manifestFiles: body.package.filePaths || [] });
    setStatus(`Updated checklist for package #${id}.`, 'success');
    return body;
  }

  async function updateDeploymentApproval() {
    const id = packageOpsId();
    if (!id) { setStatus('Package audit ID is required before approval update.', 'error'); return null; }
    const payload = { id, status: approvalStatus(), actor: approvalActor(), note: approvalNote() };
    const { status, body } = await fetchJson(endpoint('/api/docs/deploy/approval'), {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload),
    });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Approval update failed.', 'error'); return null; }
    renderDeploymentApprovalHistory(body);
    setStatus(`Updated approval for package #${id} to ${body.approvalStatus}.`, 'success');
    return body;
  }

  async function loadDeploymentReleaseNotes() {
    const id = packageOpsId();
    if (!id) { setStatus('Package audit ID is required before loading release notes.', 'error'); return null; }
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/release-notes?id=${encodeURIComponent(id)}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Release notes failed.', 'error'); return null; }
    const el = $('docs-admin-files');
    if (el) {
      const notes = body.releaseNotes || {};
      el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Release notes #${escapeHtml(id)}</strong><span>${escapeHtml(body.approvalStatus || 'draft')}</span></header><pre>${escapeHtml(notes.markdown || '')}</pre></article>`;
    }
    setStatus(`Loaded release notes for package #${id}.`, 'success');
    return body;
  }

  async function loadDeploymentApprovalHistory() {
    const id = packageOpsId();
    if (!id) { setStatus('Package audit ID is required before loading approval history.', 'error'); return null; }
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/approvals?id=${encodeURIComponent(id)}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Approval history failed.', 'error'); return null; }
    renderDeploymentApprovalHistory(body);
    setStatus(`Loaded approval history for package #${id}.`, 'success');
    return body;
  }

  function renderDeploymentApprovalHistory(body) {
    const el = $('docs-admin-files');
    if (!el) return;
    const history = body.approvalHistory || [];
    el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Approval history #${escapeHtml(body.id || packageOpsId())}</strong><span>${escapeHtml(body.approvalStatus || 'draft')} · ${body.packageLocked ? 'locked' : 'unlocked'}</span></header><ul>${history.map(item => `<li><strong>${escapeHtml(item.status)}</strong> by ${escapeHtml(item.actor)} — ${escapeHtml(item.note || '')}</li>`).join('') || '<li>No approval events yet.</li>'}</ul></article>`;
  }

  function renderReleaseDashboard(body) {
    const el = $('docs-admin-files');
    if (!el) return;
    const releases = body.releases || [];
    const totals = body.totals || {};
    el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Release dashboard</strong><span>${escapeHtml(totals.count || 0)} package(s)</span></header><p>Approved: ${escapeHtml(totals.approved || 0)} · Released: ${escapeHtml(totals.released || 0)} · Ready: ${escapeHtml(totals.readyForOperatorHandoff || 0)}</p><ul>${releases.map(item => `<li>#${escapeHtml(item.id)} ${escapeHtml(item.deploymentTarget)} · ${escapeHtml(item.environment)} · ${escapeHtml(item.approvalStatus)} · readiness ${escapeHtml(item.readiness ? item.readiness.score : 0)}/100</li>`).join('') || '<li>No release packages found.</li>'}</ul></article>`;
  }

  async function loadReleaseDashboard() {
    const sid = siteId();
    if (!sid) { setStatus('site_id is required before loading release dashboard.', 'error'); return null; }
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/releases?${releaseDashboardQuery(25)}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Release dashboard failed.', 'error'); return null; }
    renderReleaseDashboard(body);
    setStatus(`Loaded release dashboard with ${body.totals ? body.totals.count : 0} package(s).`, 'success');
    return body;
  }

  async function loadOperatorHandoffReport() {
    const id = packageOpsId();
    if (!id) { setStatus('Package audit ID is required before loading operator handoff report.', 'error'); return null; }
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/handoff-report?id=${encodeURIComponent(id)}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Operator handoff report failed.', 'error'); return null; }
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Operator handoff report #${escapeHtml(id)}</strong><span>readiness ${escapeHtml(body.readiness ? body.readiness.score : 0)}/100</span></header><pre>${escapeHtml(body.markdown || '')}</pre></article>`;
    setStatus(`Loaded operator handoff report for package #${id}.`, 'success');
    return body;
  }


  function renderReleaseArchiveIndex(body) {
    const el = $('docs-admin-files');
    if (!el) return;
    const archive = body.archive || [];
    el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Release archive index</strong><span>${escapeHtml(body.count || 0)} archived release(s)</span></header><ul>${archive.map(item => `<li>#${escapeHtml(item.auditRecordId)} ${escapeHtml(item.site_id)} · ${escapeHtml(item.deploymentTarget)} · ${escapeHtml(item.environment)} · ${escapeHtml((item.packageSha256 || '').slice(0, 12))}</li>`).join('') || '<li>No archived releases found.</li>'}</ul></article>`;
  }

  async function createReleaseArchive() {
    const id = packageOpsId();
    if (!id) { setStatus('Package audit ID is required before creating release archive.', 'error'); return null; }
    if (!window.confirm(`Create local release archive and attestation for package #${id}?`)) { setStatus('Release archive cancelled.', 'info'); return null; }
    const { status, body } = await fetchJson(endpoint('/api/docs/deploy/archive'), {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ id, confirmArchiveRelease: true, createdBy: 'easiio-docs-admin-ui' }),
    });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Release archive creation failed.', 'error'); return null; }
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Release archive #${escapeHtml(id)}</strong><span>${escapeHtml(body.archive ? body.archive.archiveStatus : 'archived')}</span></header><p>Package SHA-256: ${escapeHtml(body.attestation ? body.attestation.packageSha256 : '')}</p><p>Manifest SHA-256: ${escapeHtml(body.attestation ? body.attestation.manifestSha256 : '')}</p><p>Report SHA-256: ${escapeHtml(body.attestation ? body.attestation.handoffReportSha256 : '')}</p></article>`;
    setStatus(`Created release archive for package #${id}.`, 'success');
    return body;
  }

  async function loadReleaseArchiveIndex() {
    const sid = siteId();
    if (!sid) { setStatus('site_id is required before loading release archive index.', 'error'); return null; }
    const params = deploymentHistoryParams(25);
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/archive?${params}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Release archive index failed.', 'error'); return null; }
    renderReleaseArchiveIndex(body);
    setStatus(`Loaded ${body.count || 0} archived release(s).`, 'success');
    return body;
  }

  async function loadReleaseAttestation() {
    const id = packageOpsId();
    if (!id) { setStatus('Package audit ID is required before loading release attestation.', 'error'); return null; }
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/attestation?id=${encodeURIComponent(id)}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Release attestation failed.', 'error'); return null; }
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Release attestation #${escapeHtml(id)}</strong><span>SHA-256 verified metadata</span></header><pre>${escapeHtml(JSON.stringify(body.attestation || {}, null, 2))}</pre></article>`;
    setStatus(`Loaded release attestation for package #${id}.`, 'success');
    return body;
  }

  async function downloadReleaseReport() {
    const id = packageOpsId();
    if (!id) { setStatus('Package audit ID is required before downloading release report.', 'error'); return null; }
    const response = await fetch(endpoint(`/api/docs/deploy/report/download?id=${encodeURIComponent(id)}`), { headers: authHeaders() });
    if (!response.ok) { setStatus(`Release report download failed: HTTP ${response.status}`, 'error'); return null; }
    const text = await response.text();
    const blob = new Blob([text], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `easiio-docs-operator-handoff-${id}.md`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    setStatus(`Downloaded archived operator report for package #${id}.`, 'success');
    return text;
  }


  function rollbackPreviousId() {
    const el = $('docs-admin-rollback-previous-id');
    return el ? el.value.trim() : '';
  }

  function connectorType() {
    const el = $('docs-admin-connector-type');
    return el ? (el.value || 'sitelet') : 'sitelet';
  }

  function connectorConfigPayload() {
    const raw = $('docs-admin-connector-config') ? $('docs-admin-connector-config').value.trim() : '';
    if (!raw) return {};
    return JSON.parse(raw);
  }

  function connectorProfileId() {
    const el = $('docs-admin-connector-profile-id');
    return el ? el.value.trim() : '';
  }

  function connectorProfileName() {
    const el = $('docs-admin-connector-profile-name');
    return el ? el.value.trim() : '';
  }

  function connectorProfilePayload() {
    return {
      site_id: siteId(),
      name: connectorProfileName() || `${connectorType()} profile`,
      connector: connectorType(),
      environment: deploymentEnvironment(),
      target: connectorType() === 'static-hosting' ? 'static-html' : connectorType(),
      connectorConfig: connectorConfigPayload(),
      confirmSaveConnectorProfile: true,
      requestedBy: 'easiio-docs-admin-ui',
    };
  }

  async function verifyReleaseIntegrity() {
    const id = packageOpsId();
    if (!id) { setStatus('Package audit ID is required before verifying archive integrity.', 'error'); return null; }
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/archive/integrity?id=${encodeURIComponent(id)}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Archive integrity verification failed.', 'error'); return null; }
    const integrity = body.integrity || {};
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Archive integrity #${escapeHtml(id)}</strong><span>${integrity.verified ? 'verified' : 'blocked'}</span></header><p>Package SHA-256: ${escapeHtml(integrity.packageSha256 || '')}</p><pre>${escapeHtml(JSON.stringify(integrity.checks || [], null, 2))}</pre></article>`;
    setStatus(`Archive integrity ${integrity.verified ? 'verified' : 'failed'} for package #${id}.`, integrity.verified ? 'success' : 'error');
    return body;
  }

  async function loadRollbackPlan() {
    const id = packageOpsId();
    if (!id) { setStatus('Current package audit ID is required before loading rollback plan.', 'error'); return null; }
    const previous = rollbackPreviousId();
    const query = `id=${encodeURIComponent(id)}${previous ? `&previous_id=${encodeURIComponent(previous)}` : ''}`;
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/rollback-plan?${query}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Rollback plan failed.', 'error'); return null; }
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Rollback plan #${escapeHtml(id)}</strong><span>target #${escapeHtml(body.rollbackTarget ? body.rollbackTarget.auditRecordId : '')}</span></header><pre>${escapeHtml(body.rollbackPlanMarkdown || '')}</pre></article>`;
    setStatus(`Loaded rollback plan for package #${id}.`, 'success');
    return body;
  }

  async function prepareRestorePackage() {
    const id = packageOpsId();
    if (!id) { setStatus('Current package audit ID is required before preparing restore package.', 'error'); return null; }
    const previous = rollbackPreviousId();
    if (!window.confirm(`Prepare local restore package for #${id}${previous ? ` rolling back to #${previous}` : ''}?`)) { setStatus('Restore package preparation cancelled.', 'info'); return null; }
    const { status, body } = await fetchJson(endpoint('/api/docs/deploy/restore-package'), {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ id, previous_id: previous, confirmPrepareRestore: true, createdBy: 'easiio-docs-admin-ui' }),
    });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Restore package preparation failed.', 'error'); return null; }
    const pkg = body.restorePackage || {};
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Restore package #${escapeHtml(id)}</strong><span>local-only</span></header><p>${escapeHtml(pkg.packagePath || '')}</p><p>SHA-256: ${escapeHtml(pkg.packageSha256 || '')}</p><pre>${escapeHtml(body.rollbackPlanMarkdown || '')}</pre></article>`;
    setStatus(`Prepared local restore package for #${id}.`, 'success');
    return body;
  }

  function renderConnectorCatalog(body) {
    const el = $('docs-admin-files');
    if (!el) return;
    const connectors = body.connectors || [];
    el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Connector catalog</strong><span>${escapeHtml(connectors.length)} dry-run connector(s)</span></header><ul>${connectors.map(item => `<li><strong>${escapeHtml(item.id)}</strong> — ${escapeHtml(item.description || '')}</li>`).join('') || '<li>No connectors available.</li>'}</ul></article>`;
  }

  async function loadConnectorCatalog() {
    const { status, body } = await fetchJson(endpoint('/api/docs/deploy/connectors'), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Connector catalog failed.', 'error'); return null; }
    renderConnectorCatalog(body);
    setStatus(`Loaded ${body.connectors ? body.connectors.length : 0} deployment connector dry-run adapter(s).`, 'success');
    return body;
  }

  async function saveConnectorProfile() {
    let payload;
    try { payload = connectorProfilePayload(); }
    catch (error) { setStatus(`Invalid connector profile JSON: ${error.message}`, 'error'); return null; }
    if (!window.confirm(`Save ${payload.connector} Connector profiles placeholder set for ${payload.site_id}?`)) { setStatus('Connector profile save cancelled.', 'info'); return null; }
    const { status, body } = await fetchJson(endpoint('/api/docs/deploy/connector/profile'), {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload),
    });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Connector profile save failed.', 'error'); return null; }
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Connector profile #${escapeHtml(body.profile.id)}</strong><span>secret placeholders only</span></header><p>${escapeHtml(body.profile.name)} · ${escapeHtml(body.profile.connector)}</p><pre>${escapeHtml(JSON.stringify(body.profile.redactedConfig || {}, null, 2))}</pre></article>`;
    setStatus(`Saved connector profile #${body.profile.id}.`, 'success');
    return body;
  }

  async function loadConnectorProfiles() {
    const query = `site_id=${encodeURIComponent(siteId())}&connector=${encodeURIComponent(connectorType())}`;
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/connector/profiles?${query}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Connector profiles failed.', 'error'); return null; }
    const profiles = body.profiles || [];
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Connector profiles</strong><span>${escapeHtml(profiles.length)} profile(s)</span></header><ul>${profiles.map(item => `<li>#${escapeHtml(item.id)} <strong>${escapeHtml(item.name)}</strong> — ${escapeHtml(item.connector)} (${escapeHtml(item.environment || '')})</li>`).join('') || '<li>No connector profiles saved.</li>'}</ul></article>`;
    setStatus(`Loaded ${profiles.length} connector profile(s).`, 'success');
    return body;
  }

  async function loadConnectorDryRunHistory() {
    const query = `site_id=${encodeURIComponent(siteId())}&connector=${encodeURIComponent(connectorType())}`;
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/connector/dry-runs?${query}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Connector dry-run history failed.', 'error'); return null; }
    const dryRuns = body.dryRuns || [];
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Connector dry-run history</strong><span>${escapeHtml(dryRuns.length)} run(s)</span></header><ul>${dryRuns.map(item => `<li>#${escapeHtml(item.id)} package #${escapeHtml(item.auditRecordId)} · profile #${escapeHtml(item.profileId)} · ${item.passed ? 'passed' : 'needs review'} · ${escapeHtml(item.readinessScore)}/100</li>`).join('') || '<li>No connector dry-runs recorded.</li>'}</ul></article>`;
    setStatus(`Loaded ${dryRuns.length} connector dry-run record(s).`, 'success');
    return body;
  }

  async function runConnectorPreflight() {
    const id = packageOpsId();
    if (!id) { setStatus('Package audit ID is required before connector preflight.', 'error'); return null; }
    let connectorConfig;
    try { connectorConfig = connectorConfigPayload(); }
    catch (error) { setStatus(`Invalid connector config JSON: ${error.message}`, 'error'); return null; }
    if (!window.confirm(`Run local-only ${connectorType()} connector dry-run preflight for package #${id}?`)) { setStatus('Connector dry-run cancelled.', 'info'); return null; }
    const { status, body } = await fetchJson(endpoint('/api/docs/deploy/connector/preflight'), {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ id, connector: connectorType(), profileId: connectorProfileId(), connectorConfig, confirmConnectorDryRun: true, requestedBy: 'easiio-docs-admin-ui' }),
    });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Connector preflight failed.', 'error'); return null; }
    const preflight = body.preflight || {};
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Connector preflight #${escapeHtml(id)}</strong><span>${preflight.passed ? 'passed' : 'needs review'}</span></header><p>${escapeHtml(body.connector ? body.connector.label : connectorType())}</p><p>Dry-run record: #${escapeHtml(body.dryRunRecord ? body.dryRunRecord.id : '')}</p><p>Readiness: ${escapeHtml(preflight.readinessScore || 0)}/100 · package exists: ${preflight.packageExists ? 'yes' : 'no'}</p><pre>${escapeHtml(JSON.stringify(body.redactedConfig || {}, null, 2))}</pre></article>`;
    setStatus(`Connector dry-run preflight ${preflight.passed ? 'passed' : 'needs review'} for package #${id}.`, preflight.passed ? 'success' : 'error');
    return body;
  }

  function connectorRunbookId() {
    const el = $('docs-admin-connector-runbook-id');
    return el ? el.value.trim() : '';
  }

  function connectorCompareLeftId() {
    const el = $('docs-admin-connector-compare-left-id');
    return el ? el.value.trim() : '';
  }

  function connectorCompareRightId() {
    const el = $('docs-admin-connector-compare-right-id');
    return el ? el.value.trim() : '';
  }

  async function loadConnectorRunbook() {
    const id = connectorRunbookId();
    if (!id) { setStatus('Connector dry-run ID is required before loading a runbook.', 'error'); return null; }
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/connector/runbook?id=${encodeURIComponent(id)}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Connector runbook failed.', 'error'); return null; }
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Connector runbook #${escapeHtml(id)}</strong><span>local-only</span></header><pre>${escapeHtml(body.runbookMarkdown || '')}</pre></article>`;
    setStatus(`Loaded connector runbook for dry-run #${id}.`, 'success');
    return body;
  }

  async function compareConnectorDryRuns() {
    const left = connectorCompareLeftId();
    const right = connectorCompareRightId();
    if (!left || !right) { setStatus('Two connector dry-run IDs are required before comparison.', 'error'); return null; }
    const query = `left_id=${encodeURIComponent(left)}&right_id=${encodeURIComponent(right)}`;
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/connector/dry-run-compare?${query}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Connector dry-run comparison failed.', 'error'); return null; }
    const diffs = body.checkDiffs || [];
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Connector dry-run comparison</strong><span>${escapeHtml(diffs.length)} diff(s)</span></header><p>Score delta: ${escapeHtml(body.scoreDelta || 0)}</p><pre>${escapeHtml(JSON.stringify(body.summary || {}, null, 2))}</pre><ul>${diffs.map(item => `<li>${escapeHtml(item.name)}: ${item.leftPassed ? 'pass' : 'review'} → ${item.rightPassed ? 'pass' : 'review'}</li>`).join('') || '<li>No check differences.</li>'}</ul></article>`;
    setStatus(`Compared connector dry-runs #${left} and #${right}.`, 'success');
    return body;
  }

  function operatorPlaybookId() {
    const el = $('docs-admin-operator-playbook-id');
    return el ? el.value.trim() : '';
  }

  function operatorPlaybookTarget() {
    const el = $('docs-admin-operator-playbook-target');
    return el ? el.value : 'sitelet';
  }

  async function loadOperatorPlaybookCatalog() {
    const { status, body } = await fetchJson(endpoint('/api/docs/deploy/operator-playbooks'), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Operator playbook catalog failed.', 'error'); return null; }
    const playbooks = body.playbooks || [];
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Operator playbook catalog</strong><span>${escapeHtml(playbooks.length)} target(s)</span></header><ul>${playbooks.map(item => `<li><strong>${escapeHtml(item.title)}</strong> — ${escapeHtml(item.target)}<br>${escapeHtml(item.description || '')}</li>`).join('')}</ul></article>`;
    setStatus(`Loaded ${playbooks.length} operator playbook target(s).`, 'success');
    return body;
  }

  async function loadOperatorReleasePlaybook() {
    const id = operatorPlaybookId() || packageOpsId();
    if (!id) { setStatus('Deployment package/audit ID is required before loading an operator playbook.', 'error'); return null; }
    const query = `id=${encodeURIComponent(id)}&target=${encodeURIComponent(operatorPlaybookTarget())}`;
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/operator-playbook?${query}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Operator release playbook failed.', 'error'); return null; }
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Operator release playbook #${escapeHtml(id)}</strong><span>${escapeHtml(body.target || '')}</span></header><pre>${escapeHtml(body.playbookMarkdown || '')}</pre></article>`;
    setStatus(`Loaded ${operatorPlaybookTarget()} operator release playbook for package #${id}.`, 'success');
    return body;
  }

  function onboardingSiteId() {
    const el = $('docs-admin-onboarding-site-id');
    return el && el.value.trim() ? el.value.trim() : siteId();
  }

  function onboardingIntegration() {
    const el = $('docs-admin-onboarding-integration');
    return el ? el.value : 'sitelet';
  }

  async function loadOnboardingGuide() {
    const query = `site_id=${encodeURIComponent(onboardingSiteId())}&integration=${encodeURIComponent(onboardingIntegration())}`;
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/onboarding-guide?${query}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Onboarding guide failed.', 'error'); return null; }
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Packaging and onboarding guide</strong><span>${escapeHtml(body.integration || '')}</span></header><pre>${escapeHtml(body.installMarkdown || '')}</pre></article>`;
    setStatus(`Loaded onboarding guide for ${body.siteId || onboardingSiteId()}.`, 'success');
    return body;
  }

  async function loadOnboardingChecklist() {
    const query = `site_id=${encodeURIComponent(onboardingSiteId())}&integration=${encodeURIComponent(onboardingIntegration())}`;
    const { status, body } = await fetchJson(endpoint(`/api/docs/deploy/onboarding-checklist?${query}`), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'Onboarding checklist failed.', 'error'); return null; }
    const checklist = body.checklist || [];
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Onboarding checklist</strong><span>${escapeHtml(checklist.length)} item(s)</span></header><ul>${checklist.map(item => `<li>[${item.done ? 'x' : ' '}] <strong>${escapeHtml(item.label)}</strong> — ${escapeHtml(item.detail || '')}</li>`).join('')}</ul></article>`;
    setStatus(`Loaded onboarding checklist for ${body.siteId || onboardingSiteId()}.`, 'success');
    return body;
  }

  async function loadV1ReleaseSummary() {
    const { status, body } = await fetchJson(endpoint('/api/docs/deploy/v1-release-summary'), { headers: authHeaders() });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'V1 release summary failed.', 'error'); return null; }
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>Final QA and v1 release summary</strong><span>${escapeHtml(body.version || '')}</span></header><pre>${escapeHtml(body.releaseMarkdown || '')}</pre></article>`;
    setStatus(`Loaded Easiio Docs Module ${body.version || 'v1'} release summary.`, 'success');
    return body;
  }

  async function createV1ReleasePackage() {
    if (!confirm('Create a local-only Easiio Docs Module v1 release package? No external deployment will run.')) { return null; }
    const payload = { confirmV1ReleasePackage: true, approvedBy: 'admin-ui' };
    const { status, body } = await fetchJson(endpoint('/api/docs/deploy/v1-release-package'), { method: 'POST', headers: authHeaders(), body: JSON.stringify(payload) });
    if (status !== 200 || !body.ok) { setStatus(body.error || 'V1 release package failed.', 'error'); return null; }
    const el = $('docs-admin-files');
    if (el) el.innerHTML = `<article class="easiio-docs-admin-file"><header><strong>V1 release package</strong><span>${escapeHtml(body.packageFileName || '')}</span></header><p>${escapeHtml(body.packagePath || '')}</p><pre>${escapeHtml(JSON.stringify(body.manifest || {}, null, 2))}</pre></article>`;
    setStatus(`Created local v1 release package ${body.packageFileName || ''}.`, 'success');
    return body;
  }

  function init(root) {
    root = root || document.querySelector('[data-easiio-docs-admin]') || document;
    const previewButton = $('docs-admin-preview');
    const packageButton = $('docs-admin-package');
    const loadButton = $('docs-admin-load-docs');
    const newButton = $('docs-admin-new-doc');
    const saveButton = $('docs-admin-save-doc');
    const deleteButton = $('docs-admin-delete-doc');
    const revisionsButton = $('docs-admin-revisions');
    const importPreviewButton = $('docs-admin-import-preview');
    const importExecuteButton = $('docs-admin-import-execute');
    const bundlePreviewButton = $('docs-admin-bundle-preview');
    const bundlePackageButton = $('docs-admin-bundle-package');
    const deployPreviewButton = $('docs-admin-deploy-preview');
    const deployPackageButton = $('docs-admin-deploy-package');
    const deploySummaryButton = $('docs-admin-deploy-summary');
    const deployHistoryButton = $('docs-admin-deploy-history');
    const deployHistoryCsvButton = $('docs-admin-deploy-history-csv');
    const packageDetailButton = $('docs-admin-package-detail');
    const packageDownloadButton = $('docs-admin-package-download');
    const packageCompareButton = $('docs-admin-package-compare');
    const checklistUpdateButton = $('docs-admin-checklist-update');
    const approvalUpdateButton = $('docs-admin-approval-update');
    const releaseNotesButton = $('docs-admin-release-notes');
    const approvalHistoryButton = $('docs-admin-approval-history');
    const releaseDashboardButton = $('docs-admin-release-dashboard');
    const handoffReportButton = $('docs-admin-handoff-report');
    const releaseArchiveCreateButton = $('docs-admin-release-archive-create');
    const releaseArchiveIndexButton = $('docs-admin-release-archive-index');
    const releaseAttestationButton = $('docs-admin-release-attestation');
    const releaseReportDownloadButton = $('docs-admin-release-report-download');
    const archiveIntegrityButton = $('docs-admin-archive-integrity');
    const rollbackPlanButton = $('docs-admin-rollback-plan');
    const restorePackageButton = $('docs-admin-restore-package');
    const connectorCatalogButton = $('docs-admin-connector-catalog');
    const connectorProfileSaveButton = $('docs-admin-connector-profile-save');
    const connectorProfileListButton = $('docs-admin-connector-profile-list');
    const connectorDryRunHistoryButton = $('docs-admin-connector-dry-run-history');
    const connectorRunbookButton = $('docs-admin-connector-runbook');
    const connectorDryRunCompareButton = $('docs-admin-connector-dry-run-compare');
    const operatorPlaybookCatalogButton = $('docs-admin-operator-playbook-catalog');
    const operatorPlaybookLoadButton = $('docs-admin-operator-playbook-load');
    const onboardingGuideButton = $('docs-admin-onboarding-guide');
    const onboardingChecklistButton = $('docs-admin-onboarding-checklist');
    const v1ReleaseSummaryButton = $('docs-admin-v1-release-summary');
    const v1ReleasePackageButton = $('docs-admin-v1-release-package');
    const connectorPreflightButton = $('docs-admin-connector-preflight');
    if (previewButton) previewButton.addEventListener('click', previewExport);
    if (packageButton) packageButton.addEventListener('click', createPackage);
    if (importPreviewButton) importPreviewButton.addEventListener('click', previewImport);
    if (importExecuteButton) importExecuteButton.addEventListener('click', executeImport);
    if (bundlePreviewButton) bundlePreviewButton.addEventListener('click', previewBundle);
    if (bundlePackageButton) bundlePackageButton.addEventListener('click', packageBundle);
    if (deployPreviewButton) deployPreviewButton.addEventListener('click', previewDeployment);
    if (deployPackageButton) deployPackageButton.addEventListener('click', packageDeployment);
    if (deploySummaryButton) deploySummaryButton.addEventListener('click', loadDeploymentSummary);
    if (deployHistoryButton) deployHistoryButton.addEventListener('click', loadDeploymentHistory);
    if (deployHistoryCsvButton) deployHistoryCsvButton.addEventListener('click', exportDeploymentHistoryCsv);
    if (packageDetailButton) packageDetailButton.addEventListener('click', loadDeploymentPackageDetail);
    if (packageDownloadButton) packageDownloadButton.addEventListener('click', downloadDeploymentPackage);
    if (packageCompareButton) packageCompareButton.addEventListener('click', compareDeploymentPackages);
    if (checklistUpdateButton) checklistUpdateButton.addEventListener('click', updateDeploymentChecklist);
    if (approvalUpdateButton) approvalUpdateButton.addEventListener('click', updateDeploymentApproval);
    if (releaseNotesButton) releaseNotesButton.addEventListener('click', loadDeploymentReleaseNotes);
    if (approvalHistoryButton) approvalHistoryButton.addEventListener('click', loadDeploymentApprovalHistory);
    if (releaseDashboardButton) releaseDashboardButton.addEventListener('click', loadReleaseDashboard);
    if (handoffReportButton) handoffReportButton.addEventListener('click', loadOperatorHandoffReport);
    if (releaseArchiveCreateButton) releaseArchiveCreateButton.addEventListener('click', createReleaseArchive);
    if (releaseArchiveIndexButton) releaseArchiveIndexButton.addEventListener('click', loadReleaseArchiveIndex);
    if (releaseAttestationButton) releaseAttestationButton.addEventListener('click', loadReleaseAttestation);
    if (releaseReportDownloadButton) releaseReportDownloadButton.addEventListener('click', downloadReleaseReport);
    if (archiveIntegrityButton) archiveIntegrityButton.addEventListener('click', verifyReleaseIntegrity);
    if (rollbackPlanButton) rollbackPlanButton.addEventListener('click', loadRollbackPlan);
    if (restorePackageButton) restorePackageButton.addEventListener('click', prepareRestorePackage);
    if (connectorCatalogButton) connectorCatalogButton.addEventListener('click', loadConnectorCatalog);
    if (connectorProfileSaveButton) connectorProfileSaveButton.addEventListener('click', saveConnectorProfile);
    if (connectorProfileListButton) connectorProfileListButton.addEventListener('click', loadConnectorProfiles);
    if (connectorDryRunHistoryButton) connectorDryRunHistoryButton.addEventListener('click', loadConnectorDryRunHistory);
    if (connectorRunbookButton) connectorRunbookButton.addEventListener('click', loadConnectorRunbook);
    if (connectorDryRunCompareButton) connectorDryRunCompareButton.addEventListener('click', compareConnectorDryRuns);
    if (operatorPlaybookCatalogButton) operatorPlaybookCatalogButton.addEventListener('click', loadOperatorPlaybookCatalog);
    if (operatorPlaybookLoadButton) operatorPlaybookLoadButton.addEventListener('click', loadOperatorReleasePlaybook);
    if (onboardingGuideButton) onboardingGuideButton.addEventListener('click', loadOnboardingGuide);
    if (onboardingChecklistButton) onboardingChecklistButton.addEventListener('click', loadOnboardingChecklist);
    if (v1ReleaseSummaryButton) v1ReleaseSummaryButton.addEventListener('click', loadV1ReleaseSummary);
    if (v1ReleasePackageButton) v1ReleasePackageButton.addEventListener('click', createV1ReleasePackage);
    if (connectorPreflightButton) connectorPreflightButton.addEventListener('click', runConnectorPreflight);
    if (loadButton) loadButton.addEventListener('click', loadDocs);
    if (newButton) newButton.addEventListener('click', () => { populateEditor(null); setStatus('New draft ready.', 'info'); });
    if (saveButton) saveButton.addEventListener('click', saveDoc);
    if (deleteButton) deleteButton.addEventListener('click', deleteDoc);
    if (revisionsButton) revisionsButton.addEventListener('click', loadRevisions);
    populateEditor(null);
    renderDocList([]);
    renderFiles([]);
  }

  window.EasiioDocsAdmin = { init, previewExport, createPackage, renderFilePreview, downloadPackage, ownerToken, authHeaders, localeFilter, fallbackLocale, deploymentEnvironment, historyTarget, historyEnvironment, historyLocale, deploymentHistoryParams, releaseStatusFilter, releaseDashboardQuery, packageOpsId, compareLeftId, compareRightId, checklistPayload, approvalStatus, approvalActor, approvalNote, loadDocs, editDoc, saveDoc, deleteDoc, loadRevisions, collectEditorPayload, populateEditor, renderDocList, renderRevisions, previewImport, executeImport, previewBundle, packageBundle, previewDeployment, packageDeployment, loadDeploymentSummary, renderDeploymentSummary, loadDeploymentHistory, renderDeploymentHistory, exportDeploymentHistoryCsv, loadDeploymentPackageDetail, downloadDeploymentPackage, compareDeploymentPackages, updateDeploymentChecklist, updateDeploymentApproval, loadDeploymentReleaseNotes, loadDeploymentApprovalHistory, renderDeploymentApprovalHistory, loadReleaseDashboard, renderReleaseDashboard, loadOperatorHandoffReport, createReleaseArchive, loadReleaseArchiveIndex, renderReleaseArchiveIndex, loadReleaseAttestation, downloadReleaseReport, rollbackPreviousId, verifyReleaseIntegrity, loadRollbackPlan, prepareRestorePackage, connectorType, connectorConfigPayload, connectorProfileId, connectorProfileName, connectorProfilePayload, saveConnectorProfile, loadConnectorProfiles, loadConnectorDryRunHistory, connectorRunbookId, connectorCompareLeftId, connectorCompareRightId, loadConnectorRunbook, compareConnectorDryRuns, operatorPlaybookId, operatorPlaybookTarget, loadOperatorPlaybookCatalog, loadOperatorReleasePlaybook, onboardingSiteId, onboardingIntegration, loadOnboardingGuide, loadOnboardingChecklist, loadV1ReleaseSummary, createV1ReleasePackage, loadConnectorCatalog, renderConnectorCatalog, runConnectorPreflight, renderDeploymentPackageDetail, importPayload, renderImportPreview };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => init());
  else init();
})();
