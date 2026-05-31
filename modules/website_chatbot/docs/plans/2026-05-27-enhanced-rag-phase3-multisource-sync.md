# Enhanced RAG Phase 3 — Multi-source Knowledge Sync

## Goal

Phase 3 connects the website chatbot RAG store to reusable Easiio content modules so the chatbot can answer from more than ad-hoc page snapshots and manual knowledge entries.

The implementation remains local-first and dependency-free in the chatbot backend.

## Implemented scope

### Backend

Updated:

```text
/home/jianl/.hermes/tools/website_chatbot/backend/app.py
```

New endpoints:

```text
GET  /api/rag/sources?site_id=<site_id>
POST /api/rag/sync-sources
```

`GET /api/rag/sources` reports:

- existing stored manual/synced knowledge count
- eligible Easiio Docs documents
- eligible Website Wiki pages
- WordPress/upload placeholders for future payload-driven sync
- last sync summary

`POST /api/rag/sync-sources` accepts:

```json
{
  "site_id": "ai-solo-company-class",
  "sources": ["docs", "wiki"],
  "confirm_sync": true,
  "approved_by": "admin_customizer"
}
```

It syncs only safe public knowledge:

- Easiio Docs: `status='published'`, `visibility='public'`, `rag_enabled=1`, and `framework_targets` empty or containing `rag`
- Website Wiki: `status='published'`, `rag_enabled=1`

It preserves manual knowledge entries and replaces only previously synced entries for the selected source prefixes.

### Sync prefixes

```text
easiio-docs:<site_id>:<slug>
easiio-wiki:<site_id>:<slug>
wordpress:<site_id>:<slug>
upload:<site_id>:<slug>
```

### New environment variables

```bash
EASIIO_DOCS_DB=/path/to/easiio_docs.db
EASIIO_WIKI_DB=/path/to/website_wiki.db
EASIIO_CHATBOT_RAG_SYNC_LOG=/path/to/rag_sync_log.json
```

Defaults:

```text
/home/jianl/.hermes/tools/easiio_docs_module/data/easiio_docs.db
/home/jianl/.hermes/tools/website_wiki_module/data/website_wiki.db
/home/jianl/.hermes/tools/website_chatbot/data/rag_sync_log.json
```

### Admin customizer

Updated:

```text
/home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.js
/home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.css
```

Added a new admin card:

```text
RAG source sync
```

Admin can:

- refresh source status
- see Docs/Wiki eligible counts
- select Easiio Docs and/or Website Wiki
- sync selected sources
- see summary of synced/kept items

Copied to AI Solo site admin assets:

```text
/mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.js
/mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.css
```

## Tests added

Updated:

```text
/home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py
/home/jianl/.hermes/tools/website_chatbot/tests/admin_customizer_static.test.js
```

New backend coverage:

1. `test_rag_sync_sources_imports_docs_and_wiki_without_leaking_private_content`
   - seeds temporary Docs/Wiki SQLite DBs
   - verifies private/draft/disabled pages do not sync
   - verifies manual knowledge is preserved
   - verifies synced content powers chat answers
   - verifies approver email is masked

2. `test_rag_sources_endpoint_reports_multisource_status_and_last_sync`
   - verifies source counts before sync
   - verifies last sync after sync

## Verification

Run from any directory:

```bash
python3 -m py_compile \
  /home/jianl/.hermes/tools/website_chatbot/backend/app.py \
  /home/jianl/.hermes/tools/website_chatbot/backend/site_gateway.py

python3 /home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py -v
node --check /home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.js
node /home/jianl/.hermes/tools/website_chatbot/tests/admin_customizer_static.test.js
```

Expected backend result after Phase 3:

```text
Ran 30 tests
OK
```

Smoke script used during implementation:

```text
/tmp/easiio_rag_phase3_smoke.py
```

Expected smoke marker:

```text
easiio_rag_phase3_smoke_ok
```

## Safety rules

- Do not sync draft docs.
- Do not sync private docs unless a future explicit private/admin mode is designed.
- Do not expose Docs/Wiki database file paths to public visitor widgets.
- Admin UI should be embedded only inside protected/admin pages.
- `confirm_sync: true` is required before writing synced content.
- Approver/contact info in sync logs is PII-masked.

## Future Phase 4 candidates

1. WordPress pull/sync adapter through a protected server-side connector.
2. Uploaded PDF/DOCX text extraction sync.
3. Stale-content detection and per-source diff preview before sync.
4. Scheduled sync jobs with safe admin review.
5. Per-source delete/rollback controls.
