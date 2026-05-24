# Easiio Docs Module Phase 4

## Goal

Add WordPress integration so Easiio Docs spaces can be embedded into WordPress pages and handed off as draft WordPress content without automatic publishing.

## Implemented files

```text
backend/docs_wordpress.py
wordpress-plugin/easiio-docs/easiio-docs.php
wordpress-plugin/easiio-docs/README.md
tests/wp_plugin_static.test.js
dist/easiio-docs-wordpress-plugin.zip
```

Updated:

```text
backend/app.py
tests/test_docs_backend.py
README.md
```

## WordPress shortcode plugin

Install package:

```text
/home/jianl/.hermes/tools/easiio_docs_module/dist/easiio-docs-wordpress-plugin.zip
```

Basic shortcode:

```text
[easiio_docs site_id="ai-solo-company" api_base="https://docs.example.com" title="AI Solo Company Docs"]
```

Protected docs shortcode:

```text
[easiio_docs site_id="ai-solo-company" require_login="true" credential_mode="include"]
```

Admin/editor shortcode for protected admin pages only:

```text
[easiio_docs site_id="ai-solo-company" mode="admin" require_login="true"]
```

## Backend endpoints

```text
GET  /api/docs/wordpress/shortcode
GET  /api/docs/wordpress/draft-plan
POST /api/docs/wordpress/draft-execution
```

`draft-plan` returns a reviewable WordPress draft handoff package for Hermes MCP tools. It does not call WordPress directly.

`draft-execution` is confirmation-gated with:

```json
{"confirmDraftCreation": true}
```

It returns a `hermes-mcp-handoff` payload for:

```text
mcp_easiio_wp_create_draft_post
```

## Safety rules

- No automatic publishing.
- Draft creation is blocked until explicit confirmation.
- Publishing requires separate human approval after draft verification.
- Shortcode output escapes WordPress attributes.
- `require_login="true"` blocks rendering for logged-out visitors.
- Admin mode should only appear on protected pages.
- Secrets/tokens must remain server-rendered and redacted in docs.

## Verification

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_db.py backend/docs_sitelet.py backend/docs_wordpress.py
node --check frontend/docs.js
node tests/docs_static.test.js
node tests/sitelet_preview_static.test.js
node tests/wp_plugin_static.test.js
python3 tests/test_docs_backend.py -v
```

Runtime smoke passed:

```text
easiio_docs_phase4_smoke_ok
```
