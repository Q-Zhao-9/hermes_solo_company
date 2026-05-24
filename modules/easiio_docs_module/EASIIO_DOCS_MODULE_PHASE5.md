# Easiio Docs Module Phase 5

## Goal

Add chatbot/RAG sync so approved Easiio Docs content can become manual knowledge for the reusable website chatbot backend.

## Implemented files

```text
backend/docs_rag.py
tests/rag_sync_static.test.js
```

Updated:

```text
backend/app.py
tests/test_docs_backend.py
README.md
```

## Backend endpoints

```text
GET  /api/docs/rag/preview
POST /api/docs/rag/sync
```

## Preview

```bash
curl -s 'http://127.0.0.1:8110/api/docs/rag/preview?site_id=ai-solo-company'
```

The preview returns:

```text
exportType: easiio-docs-rag-preview
documentCount
chunkCount
chunks
requiresSyncApproval: true
syncBlocked: true
storePath
```

## Sync

```bash
curl -s http://127.0.0.1:8110/api/docs/rag/sync \
  -H 'Content-Type: application/json' \
  -d '{"confirmRagSync":true,"site_id":"ai-solo-company","approvedBy":"reviewer"}'
```

Sync writes to the chatbot manual RAG store:

```text
/home/jianl/.hermes/tools/website_chatbot/data/rag_content.json
```

Override with:

```bash
EASIIO_CHATBOT_RAG_STORE=/path/to/rag_content.json
```

## Default filtering

Phase 5 syncs only docs matching:

```text
status = published
visibility = public
rag_enabled = true
framework_targets includes rag
```

Private/internal/login-required docs are excluded by default. They should only be synced through an explicit protected/admin workflow.

## Store behavior

- Preserves existing manual/external chatbot knowledge items.
- Preserves other `site_id` entries.
- Replaces old Easiio Docs-generated chunks for the same `site_id`.
- Writes content IDs with prefix:

```text
easiio-docs:<site_id>:<doc_slug>
```

## Verification

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py backend/docs_wordpress.py backend/docs_rag.py
node --check frontend/docs.js
node tests/docs_static.test.js
node tests/sitelet_preview_static.test.js
node tests/wp_plugin_static.test.js
node tests/rag_sync_static.test.js
python3 tests/test_docs_backend.py -v
```

Runtime smoke passed:

```text
easiio_docs_phase5_smoke_ok
```
