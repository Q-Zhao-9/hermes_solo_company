# Easiio Docs Module Phase 2

## Goal

Create the embeddable frontend widget for the Easiio Docs Module so documentation can be displayed inside static websites, future Sitelet previews, WordPress pages, and Next.js/app pages.

## Implemented files

```text
frontend/docs.js
frontend/docs.css
frontend/demo.html
tests/docs_static.test.js
```

Updated:

```text
backend/app.py
tests/test_docs_backend.py
README.md
```

## Widget embed

```html
<link rel="stylesheet" href="http://localhost:8110/docs/docs.css" />
<div id="easiio-docs-root"></div>
<script
  src="http://localhost:8110/docs/docs.js"
  data-easiio-docs
  data-api-base="http://localhost:8110"
  data-site-id="ai-solo-company"
  data-mode="public"
  data-root-selector="#easiio-docs-root"
  data-title="AI Solo Company Documentation">
</script>
```

## Supported data attributes

```text
data-api-base
data-site-id
data-mode: public | admin
data-root-selector
data-title
data-subtitle
data-status
data-visibility
data-target-filter
data-framework-target
data-credential-mode
data-auth-token
data-login-required
data-require-login
data-content-format
```

## Frontend capabilities

- public reader mode
- admin/editor mode
- search
- framework/integration target filter
- site summary display
- document open/read flow
- create/update/delete flow in admin mode
- credential forwarding for protected pages
- basic safe Markdown/MDX-ish rendering for non-HTML content
- explicit HTML passthrough only for `content_format='html'`

## Backend asset routes

```text
GET /docs/docs.js
GET /docs/docs.css
GET /docs/demo.html
```

All include permissive CORS headers for embeddable use.

## Verification

```bash
cd /home/jianl/.hermes/tools/easiio_docs_module
python3 -m py_compile backend/app.py backend/docs_db.py
node --check frontend/docs.js
node tests/docs_static.test.js
python3 tests/test_docs_backend.py -v
```

Runtime smoke passed using a temporary DB on port `8111`:

```text
easiio_docs_phase2_smoke_ok
```

## Next phase

Phase 3 should render docs spaces into Sitelet preview payloads, allowing generated documentation pages or full documentation portals to be previewed before publishing to WordPress/static/Next.js.
