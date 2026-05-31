const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const exportersPath = path.join(root, 'backend', 'docs_exporters.py');
const appPath = path.join(root, 'backend', 'app.py');

assert(fs.existsSync(exportersPath), 'backend/docs_exporters.py should exist');
const exporters = fs.readFileSync(exportersPath, 'utf8');
const app = fs.readFileSync(appPath, 'utf8');

for (const expected of [
  'build_export_preview',
  'build_export_package',
  'EXPORT_TARGETS',
  'nextjs-mdx',
  'docusaurus',
  'mkdocs',
  'hugo',
  'vitepress',
  'static-html',
  'confirmExportPackage',
  'requiresExportApproval',
  'easiio-docs-framework-export',
]) {
  assert(exporters.includes(expected), `docs_exporters.py should include ${expected}`);
}

assert(app.includes('docs_exporters'), 'app.py should import docs_exporters helpers');
assert(app.includes('/api/docs/export/preview'), 'app.py should expose framework export preview endpoint');
assert(app.includes('/api/docs/export/package'), 'app.py should expose confirmation-gated framework package endpoint');

console.log('PASS Phase 6 framework exporter helpers and endpoints are wired');
