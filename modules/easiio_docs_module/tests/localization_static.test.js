const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');
const app = fs.readFileSync(path.join(root, 'backend', 'app.py'), 'utf8');
const db = fs.readFileSync(path.join(root, 'backend', 'docs_db.py'), 'utf8');
const exporters = fs.readFileSync(path.join(root, 'backend', 'docs_exporters.py'), 'utf8');
const importers = fs.readFileSync(path.join(root, 'backend', 'docs_importers.py'), 'utf8');
const adminHtml = fs.readFileSync(path.join(root, 'frontend', 'admin.html'), 'utf8');
const adminJs = fs.readFileSync(path.join(root, 'frontend', 'admin.js'), 'utf8');

[
  '17-release-dashboard',
  'locale=',
  'fallback_locale',
  'get_doc_localized',
].forEach((needle) => assert(app.includes(needle) || db.includes(needle), `${needle} should be wired in backend`));

[
  'locale_counts',
  'available_locales',
  'list_locales',
  'fallbackUsed',
].forEach((needle) => assert(db.includes(needle) || app.includes(needle), `${needle} should be supported for localized docs`));

[
  'locale',
  'fallback_locale',
  'localizedPath',
].forEach((needle) => assert(exporters.includes(needle), `${needle} should be supported by localized exporters`));

[
  'locale_from_path',
  'localized import',
].forEach((needle) => assert(importers.includes(needle), `${needle} should be supported by importers`));

[
  'docs-admin-locale-filter',
  'docs-admin-fallback-locale',
  'Locale filter',
].forEach((needle) => assert(adminHtml.includes(needle), `${needle} should exist in admin localization UI`));

[
  'localeFilter',
  'fallbackLocale',
  'fallback_locale',
  'locale=',
].forEach((needle) => assert(adminJs.includes(needle), `${needle} should be wired in admin localization JS`));

console.log('PASS Phase 11 localization assets and routes are wired');
