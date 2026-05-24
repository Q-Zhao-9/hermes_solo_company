const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');
const app = fs.readFileSync(path.join(root, 'backend', 'app.py'), 'utf8');
const audit = fs.existsSync(path.join(root, 'backend', 'docs_audit.py')) ? fs.readFileSync(path.join(root, 'backend', 'docs_audit.py'), 'utf8') : '';
const deploy = fs.readFileSync(path.join(root, 'backend', 'docs_deploy.py'), 'utf8');
const adminHtml = fs.readFileSync(path.join(root, 'frontend', 'admin.html'), 'utf8');
const adminJs = fs.readFileSync(path.join(root, 'frontend', 'admin.js'), 'utf8');
const readme = fs.readFileSync(path.join(root, 'README.md'), 'utf8');

[
  '17-release-dashboard',
  'docs_audit',
  '/api/docs/deploy/history',
  'build_deployment_history_response',
].forEach(token => assert(app.includes(token), `${token} should be wired in app.py`));

[
  'class DocsAuditStore',
  'docs_deployment_audit',
  'record_deployment_package',
  'list_deployment_history',
  'deployment_package_created',
  'packagePath',
  'approvedBy',
].forEach(token => assert(audit.includes(token), `${token} should exist in docs_audit.py`));

[
  'audit_store',
  'auditRecorded',
  'auditRecordId',
].forEach(token => assert(deploy.includes(token), `${token} should be present in docs_deploy.py`));

[
  'docs-admin-deploy-history',
  'docs-admin-deployment-history-panel',
  'Deployment history',
].forEach(token => assert(adminHtml.includes(token), `${token} should be present in admin.html`));

[
  'loadDeploymentHistory',
  'renderDeploymentHistory',
  '/api/docs/deploy/history',
  'deploymentHistory',
].forEach(token => assert(adminJs.includes(token), `${token} should be present in admin.js`));

assert(readme.includes('Phase 13'), 'README should document Phase 13');
assert(readme.includes('deployment history'), 'README should mention deployment history');

console.log('PASS Phase 13 deployment history audit assets and routes are wired');
