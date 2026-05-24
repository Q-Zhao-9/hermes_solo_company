const assert = require('assert');
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const ragPath = path.join(root, 'backend', 'docs_rag.py');
const appPath = path.join(root, 'backend', 'app.py');

assert(fs.existsSync(ragPath), 'backend/docs_rag.py should exist');
const rag = fs.readFileSync(ragPath, 'utf8');
const app = fs.readFileSync(appPath, 'utf8');

assert(rag.includes('build_rag_preview'), 'docs_rag.py should expose build_rag_preview');
assert(rag.includes('sync_docs_to_chatbot_rag'), 'docs_rag.py should expose sync_docs_to_chatbot_rag');
assert(rag.includes('EASIIO_CHATBOT_RAG_STORE'), 'docs_rag.py should use chatbot RAG store env var');
assert(rag.includes('easiio-docs:'), 'docs_rag.py should mark synced content_id values with easiio-docs prefix');
assert(rag.includes('requiresSyncApproval'), 'RAG preview/sync responses should require approval');
assert(rag.includes('confirmRagSync'), 'RAG sync should be confirmation gated');
assert(rag.includes('rag_enabled'), 'RAG builder should filter by rag_enabled docs');
assert(rag.includes('visibility') && rag.includes('public'), 'RAG builder should default to public docs');
assert(app.includes('/api/docs/rag/preview'), 'app.py should expose RAG preview endpoint');
assert(app.includes('/api/docs/rag/sync'), 'app.py should expose RAG sync endpoint');
assert(app.includes('docs_rag'), 'app.py should import docs_rag helpers');

console.log('PASS Phase 5 RAG sync helpers and endpoints are wired');
