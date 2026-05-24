# Easiio Docs Module Phase 3

## Goal

Add Sitelet preview integration so a docs space can be rendered into a Sitelet-compatible payload before publishing or embedding it in a production site.

## Implemented

Files:

```text
/home/jianl/.hermes/tools/easiio_docs_module/backend/docs_sitelet.py
/home/jianl/.hermes/tools/easiio_docs_module/tests/sitelet_preview_static.test.js
```

Updated:

```text
/home/jianl/.hermes/tools/easiio_docs_module/backend/app.py
/home/jianl/.hermes/tools/easiio_docs_module/tests/test_docs_backend.py
/home/jianl/.hermes/tools/easiio_docs_module/README.md
```

## Endpoints

### Build preview payload

```text
GET /api/docs/sitelet-preview?site_id=<site>&target=sitelet
GET /api/docs/sitelet-preview?site_id=<site>&slug=<doc-slug>
```

Returns:

```text
exportType: easiio-docs-sitelet-preview
requiresUploadApproval: true
uploadBlocked: true
siteletPayload: {...}
uploadInstructions: {...}
```

The `siteletPayload` is compatible with the Sitelet `/api/generated` multi-page upload format:

```text
title
source: easiio-docs-module
kind: site
pages: [{path,title,html}]
assets: [{path,contentType,content}]
metadata
```

### Upload preview payload

```text
POST /api/docs/sitelet-preview/upload
```

Upload is intentionally confirmation-gated:

```json
{
  "confirmSiteletUpload": true,
  "site_id": "ai-solo-company"
}
```

Without `confirmSiteletUpload:true`, the endpoint returns HTTP `409` and does not call Sitelet.

## Safety model

- Preview generation is local and read-only.
- Only `published` + `public` docs are included by default.
- Upload remains blocked until explicit confirmation.
- Upload requires server-side environment variables:
  - `SITELET_BASE_URL`
  - `SITELET_API_TOKEN`
- Tokens are never rendered in preview payloads or docs pages.

## Verification

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py
node --check frontend/docs.js
node tests/docs_static.test.js
node tests/sitelet_preview_static.test.js
python3 tests/test_docs_backend.py -v
```

Runtime smoke passed with temporary DB/server:

```text
easiio_docs_phase3_smoke_ok
```

Temporary files were cleaned.

## Next phase

Phase 4 should add WordPress integration:

- shortcode/plugin bridge
- WordPress preview/embed mode
- draft-first content handoff
- no auto-publish without separate approval
