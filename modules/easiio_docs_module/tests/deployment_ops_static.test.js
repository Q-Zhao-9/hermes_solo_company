const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');
const app = fs.readFileSync(path.join(root, 'backend', 'app.py'), 'utf8');
const audit = fs.readFileSync(path.join(root, 'backend', 'docs_audit.py'), 'utf8');
const adminHtml = fs.readFileSync(path.join(root, 'frontend', 'admin.html'), 'utf8');
const adminJs = fs.readFileSync(path.join(root, 'frontend', 'admin.js'), 'utf8');
const readme = fs.readFileSync(path.join(root, 'README.md'), 'utf8');

[
  '17-release-dashboard',
  '/api/docs/deploy/summary',
  '/api/docs/deploy/history.csv',
  'build_deployment_summary_response',
  'build_deployment_history_csv_response',
].forEach(token => assert(app.includes(token), `${token} should be wired in app.py`));

[
  'summarize_deployment_history',
  'deployment_history_to_csv',
  'filter_deployment_history',
  'counts',
  'totalPackageSize',
].forEach(token => assert(audit.includes(token), `${token} should exist in docs_audit.py`));

[
  'docs-admin-history-target',
  'docs-admin-history-environment',
  'docs-admin-history-locale',
  'docs-admin-deploy-summary',
  'docs-admin-deploy-history-csv',
  'Deployment audit operations',
].forEach(token => assert(adminHtml.includes(token), `${token} should be present in admin.html`));

[
  'deploymentHistoryParams',
  'loadDeploymentSummary',
  'exportDeploymentHistoryCsv',
  'renderDeploymentSummary',
  '/api/docs/deploy/summary',
  '/api/docs/deploy/history.csv',
].forEach(token => assert(adminJs.includes(token), `${token} should be present in admin.js`));

assert(readme.includes('Phase 14'), 'README should document Phase 14');
assert(readme.includes('audit operations'), 'README should mention audit operations');

console.log('PASS Phase 14 deployment audit operations assets and routes are wired');
