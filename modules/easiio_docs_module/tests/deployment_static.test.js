const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');
const app = fs.readFileSync(path.join(root, 'backend', 'app.py'), 'utf8');
const deploy = fs.existsSync(path.join(root, 'backend', 'docs_deploy.py')) ? fs.readFileSync(path.join(root, 'backend', 'docs_deploy.py'), 'utf8') : '';
const adminHtml = fs.readFileSync(path.join(root, 'frontend', 'admin.html'), 'utf8');
const adminJs = fs.readFileSync(path.join(root, 'frontend', 'admin.js'), 'utf8');
const readme = fs.readFileSync(path.join(root, 'README.md'), 'utf8');

[
  'build_deployment_handoff_preview',
  'build_deployment_handoff_package',
  '/api/docs/deploy/preview',
  '/api/docs/deploy/package',
  'confirmDeploymentPackage',
  '17-release-dashboard',
].forEach(token => assert(app.includes(token), `${token} should be wired in app.py`));

[
  'DEPLOYMENTS_DIR',
  'easiio-docs-deployment-manifest.json',
  'requiresDeploymentApproval',
  'deploymentBlocked',
  'deploymentTarget',
  'confirmDeploymentPackage',
  'dist/easiio-docs-deployments',
].forEach(token => assert(deploy.includes(token), `${token} should exist in docs_deploy.py`));

[
  'docs-admin-deploy-preview',
  'docs-admin-deploy-package',
  'docs-admin-deploy-environment',
  'Deployment handoff',
].forEach(token => assert(adminHtml.includes(token), `${token} should be present in admin.html`));

[
  'previewDeployment',
  'packageDeployment',
  '/api/docs/deploy/preview',
  '/api/docs/deploy/package',
  'confirmDeploymentPackage: true',
  'localeFilter()',
].forEach(token => assert(adminJs.includes(token), `${token} should be present in admin.js`));

assert(readme.includes('Phase 12'), 'README should document Phase 12');
assert(readme.includes('deployment handoff'), 'README should mention deployment handoff');

console.log('PASS Phase 12 deployment handoff assets and routes are wired');
