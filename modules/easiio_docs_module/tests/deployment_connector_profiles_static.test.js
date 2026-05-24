const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const read = rel => fs.readFileSync(path.join(root, rel), 'utf8');

const app = read('backend/app.py');
const connectors = read('backend/docs_connectors.py');
const adminHtml = read('frontend/admin.html');
const adminJs = read('frontend/admin.js');
const readme = read('README.md');
const phaseDocPath = path.join(root, 'EASIIO_DOCS_MODULE_PHASE21.md');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(app.includes('21-connector-profiles'), 'health marker must identify Phase 21');
assert(app.includes('/api/docs/deploy/connector/profiles'), 'connector profiles list endpoint must be wired');
assert(app.includes('/api/docs/deploy/connector/profile'), 'connector profile save endpoint must be wired');
assert(app.includes('/api/docs/deploy/connector/dry-runs'), 'connector dry-run history endpoint must be wired');
assert(app.includes('build_connector_profiles_response'), 'app must use connector profiles helper');
assert(app.includes('build_connector_profile_save_response'), 'app must use connector profile save helper');
assert(app.includes('build_connector_dry_run_history_response'), 'app must use dry-run history helper');

assert(connectors.includes('docs_connector_profiles'), 'connector module must persist connector profiles table');
assert(connectors.includes('docs_connector_dry_runs'), 'connector module must persist connector dry-run history table');
assert(connectors.includes('confirmSaveConnectorProfile'), 'profile save must require explicit confirmation');
assert(connectors.includes('profileId'), 'preflight must support profileId/profile_id');
assert(connectors.includes('record_connector_dry_run'), 'preflight must record dry-run history');
assert(connectors.includes('secretPlaceholdersOnly'), 'profiles must store secret placeholders only');
assert(connectors.includes('redactedConfig'), 'profiles/dry-runs must return redacted config only');

assert(adminHtml.includes('Connector profiles'), 'admin UI must include connector profiles panel');
assert(adminHtml.includes('docs-admin-connector-profile-name'), 'admin UI must include connector profile name input');
assert(adminHtml.includes('docs-admin-connector-profile-save'), 'admin UI must include connector profile save button');
assert(adminHtml.includes('docs-admin-connector-profile-list'), 'admin UI must include connector profile list button');
assert(adminHtml.includes('docs-admin-connector-dry-run-history'), 'admin UI must include dry-run history button');

assert(adminJs.includes('connectorProfilePayload'), 'admin JS must build connector profile payload');
assert(adminJs.includes('saveConnectorProfile'), 'admin JS must save connector profiles');
assert(adminJs.includes('loadConnectorProfiles'), 'admin JS must load connector profiles');
assert(adminJs.includes('loadConnectorDryRunHistory'), 'admin JS must load connector dry-run history');
assert(adminJs.includes('confirmSaveConnectorProfile'), 'admin JS must send profile save confirmation flag');
assert(adminJs.includes('/api/docs/deploy/connector/profile'), 'admin JS must call profile save endpoint');
assert(adminJs.includes('/api/docs/deploy/connector/profiles'), 'admin JS must call profile list endpoint');
assert(adminJs.includes('/api/docs/deploy/connector/dry-runs'), 'admin JS must call dry-run history endpoint');

assert(readme.includes('Phase 21'), 'README must document Phase 21');
assert(readme.includes('21-connector-profiles'), 'README must document Phase 21 health marker');
assert(readme.includes('/api/docs/deploy/connector/profiles'), 'README must document profiles endpoint');
assert(readme.includes('/api/docs/deploy/connector/dry-runs'), 'README must document dry-run history endpoint');
assert(readme.includes('confirmSaveConnectorProfile'), 'README must document connector profile confirmation gate');
assert(fs.existsSync(phaseDocPath), 'dedicated Phase 21 doc must exist');
const phaseDoc = fs.readFileSync(phaseDocPath, 'utf8');
assert(phaseDoc.includes('Phase 21'), 'Phase 21 doc must identify the phase');
assert(phaseDoc.includes('easiio_docs_phase21_smoke_ok'), 'Phase 21 doc must include smoke marker');
assert(phaseDoc.includes('secret placeholders'), 'Phase 21 doc must describe secret placeholder safety');
assert(phaseDoc.includes('dry-run history'), 'Phase 21 doc must describe dry-run history');

console.log('PASS Phase 21 connector profiles and dry-run history assets are wired');
