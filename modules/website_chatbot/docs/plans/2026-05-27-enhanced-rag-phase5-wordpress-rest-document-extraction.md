# Enhanced RAG Phase 5 — WordPress REST Pull + Document Extraction

## Goal

Phase 5 turns the Phase 4 WordPress/upload staging layer into a more practical ingestion pipeline:

1. Pull reviewed public WordPress pages/posts through the WordPress REST API.
2. Extract text from uploaded documents and stage it as upload-source knowledge.
3. Keep all ingestion review-first and site-scoped.
4. Avoid exposing WordPress credentials, environment variable values, files, or provider secrets in browser responses.

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

## New backend endpoints

### WordPress REST pull

```text
POST /api/rag/wordpress/pull
```

Example payload:

```json
{
  "site_id": "ai-solo-company-class",
  "base_url": "https://example.com",
  "post_types": ["pages", "posts"],
  "per_page": 20,
  "auth_env": "OPTIONAL_SERVER_SIDE_ENV_VAR_NAME",
  "confirm_pull": true,
  "approved_by": "admin_customizer"
}
```

Behavior:

- Requires `confirm_pull: true`.
- Accepts only public `http`/`https` WordPress URLs.
- Rejects non-HTTP URLs and local loopback URLs.
- Pulls from:

```text
/wp-json/wp/v2/pages
/wp-json/wp/v2/posts
```

- Converts rendered title/excerpt/content HTML to plain text.
- Stages pulled posts as `wordpress` source items in the existing external source store.
- Supports optional Basic Auth through a server-side environment variable name in `auth_env`.
- Never returns the `auth_env` value, raw credential, or approver contact info.

### Uploaded document extraction

```text
POST /api/rag/upload/extract
```

Example payload:

```json
{
  "site_id": "ai-solo-company-class",
  "filename": "course-brochure.docx",
  "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "content_base64": "...",
  "title": "Course Brochure",
  "confirm_extract": true,
  "approved_by": "admin_customizer"
}
```

Behavior:

- Requires `confirm_extract: true`.
- Stages extracted text as `upload` source items.
- Masks PII in returned text previews.
- Supports dependency-free extraction for:
  - `.txt`
  - `.md`
  - `.html` / `.htm`
  - `.docx`
- Supports best-effort PDF extraction if PyMuPDF/fitz is installed.
- Scanned PDFs may still need a separate OCR step.

## Store and sync flow

Phase 5 continues to use the Phase 4 external source store:

```bash
EASIIO_CHATBOT_RAG_EXTERNAL_SOURCES=/path/to/rag_external_sources.json
```

Default:

```text
/home/jianl/.hermes/tools/website_chatbot/data/rag_external_sources.json
```

Typical flow:

1. Pull WordPress or extract document text.
2. Review source counts with:

```text
GET /api/rag/sources?site_id=<site_id>
```

3. Sync approved sources with:

```text
POST /api/rag/sync-sources
```

Example:

```json
{
  "site_id": "ai-solo-company-class",
  "sources": ["wordpress", "upload"],
  "confirm_sync": true
}
```

## Admin UI

The reusable admin customizer now includes:

- **WordPress REST pull** form:
  - WordPress URL
  - post types
  - optional server-side auth env name
- **Document extraction** form:
  - file input for TXT/MD/HTML/DOCX/PDF
  - optional title
  - extract button
- Existing JSON import forms remain available for manual/reviewed imports.

## Safety notes

- The browser never receives WordPress application passwords, env values, API tokens, or database paths.
- `auth_env` is a server-side environment variable name only; the value remains server-side.
- Localhost/loopback WordPress URLs are rejected by the pull endpoint.
- `approved_by` is masked in responses/logs.
- Scanned PDF OCR is intentionally not bundled into the dependency-free backend; use a separate OCR pipeline before staging if needed.

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
easiio_rag_phase5_smoke_ok
```

## Recommended Phase 6

Phase 6 can add an admin review queue and stale-content operations:

1. Diff WordPress/document source changes before sync.
2. Mark stale source items when pages disappear upstream.
3. Add scheduled pull jobs with review-only summaries.
4. Add optional OCR worker for scanned PDFs.
5. Add per-source freshness dashboard and rollback for synced RAG versions.
