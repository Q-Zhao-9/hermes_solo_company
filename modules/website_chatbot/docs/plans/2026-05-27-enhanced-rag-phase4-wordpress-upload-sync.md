# Enhanced RAG Phase 4 — WordPress and Uploaded Document Knowledge Sync

## Goal

Extend the Website Chatbot RAG operations layer so admin users can stage reviewed WordPress page/post exports and uploaded document text, then sync those approved sources into the per-site chatbot knowledge base.

This phase builds on Phase 3 multi-source sync:

- Phase 3: Easiio Docs + Website Wiki + payload placeholders.
- Phase 4: persisted WordPress/upload source stores, admin import UI, source status counts, sync into RAG, and regression tests.

## Implemented files

```text
/home/jianl/.hermes/tools/website_chatbot/backend/app.py
/home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py
/home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.js
/home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.css
/home/jianl/.hermes/tools/website_chatbot/tests/admin_customizer_static.test.js
/mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.js
/mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.css
```

## New store

```bash
EASIIO_CHATBOT_RAG_EXTERNAL_SOURCES=/path/to/rag_external_sources.json
```

Default:

```text
/home/jianl/.hermes/tools/website_chatbot/data/rag_external_sources.json
```

The store is site-scoped and source-scoped. It stores reviewed external items from:

- `wordpress`
- `upload`

It does not store API keys, WordPress credentials, email settings, tokens, or raw connector secrets.

## New endpoints

### List staged external source items

```text
GET /api/rag/source-items?site_id=<site_id>&source=wordpress
GET /api/rag/source-items?site_id=<site_id>&source=upload
```

Returns source items only for the requested `site_id` and `source`, plus `eligible_count`.

### Save staged source items

```text
POST /api/rag/source-items
```

Example WordPress payload:

```json
{
  "site_id": "ai-solo-company-class",
  "source": "wordpress",
  "items": [
    {
      "slug": "homepage",
      "title": "Homepage",
      "url": "https://example.com/",
      "status": "publish",
      "visibility": "public",
      "content": "Reviewed public WordPress page text..."
    }
  ]
}
```

Example upload payload:

```json
{
  "site_id": "ai-solo-company-class",
  "source": "upload",
  "items": [
    {
      "slug": "course-brochure",
      "title": "Course Brochure",
      "filename": "course-brochure.pdf",
      "mime_type": "application/pdf",
      "status": "published",
      "visibility": "public",
      "content": "Reviewed extracted document text..."
    }
  ]
}
```

### Delete staged external source item

```text
POST /api/rag/source-items/delete
```

Payload:

```json
{
  "site_id": "ai-solo-company-class",
  "source": "wordpress",
  "slug": "homepage"
}
```

## Sync behavior

Existing endpoint now supports persisted WordPress/upload sources:

```text
POST /api/rag/sync-sources
```

Example:

```json
{
  "site_id": "ai-solo-company-class",
  "sources": ["wordpress", "upload"],
  "confirm_sync": true,
  "approved_by": "admin_customizer"
}
```

Rules:

- `confirm_sync: true` is required.
- Manual RAG entries are preserved.
- Only selected synced prefixes are replaced:
  - `wordpress:`
  - `upload:`
  - plus existing `easiio-docs:` and `easiio-wiki:` prefixes for those sources.
- Approver/contact fields in sync summaries are masked.

## Eligibility rules

### WordPress

Eligible only when:

```text
status = publish or published
visibility = public or blank
rag_enabled is not false
sync_to_rag is not false
content is non-empty
```

Private/draft WordPress content is not synced.

### Uploaded documents

Eligible only when:

```text
status = published, publish, ready, or active
visibility = public or blank
rag_enabled is not false
sync_to_rag is not false
content is non-empty
```

Draft/private uploaded text is not synced.

## Admin UI

The reusable admin customizer now includes WordPress/upload import controls inside the RAG source sync card:

- checkbox: WordPress
- checkbox: Uploads
- `WordPress import` JSON textarea
- `Uploaded document import` JSON textarea
- Save buttons that call `POST /api/rag/source-items`
- Source refresh shows eligible/stored counts through `GET /api/rag/sources`

The deployed AI Solo admin customizer copy was updated too.

## Verification

Commands run:

```bash
python3 -m py_compile \
  /home/jianl/.hermes/tools/website_chatbot/backend/app.py \
  /home/jianl/.hermes/tools/website_chatbot/backend/site_gateway.py

python3 /home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py -v
node --check /home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.js
node /home/jianl/.hermes/tools/website_chatbot/tests/admin_customizer_static.test.js
node --check /home/jianl/.hermes/tools/website_chatbot/widget/widget.js
node /home/jianl/.hermes/tools/website_chatbot/tests/widget_static.test.js
node /home/jianl/.hermes/tools/website_chatbot/tests/wp_plugin_static.test.js
python3 /mnt/c/Users/jianl/solo-company-class-site/auth_download_static_test.py
node --check /mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.js
```

Runtime smoke marker:

```text
easiio_rag_phase4_smoke_ok
```

## Next phase ideas

Phase 5 can add direct connectors/import helpers:

1. WordPress REST API pull with application-password or server-side token stored only in protected env/config.
2. PDF/DOCX/TXT extraction pipeline for uploaded files.
3. Admin review queue before source items become eligible.
4. Stale-content detection and diff previews.
5. Scheduled source refresh with review-only sync summaries.

