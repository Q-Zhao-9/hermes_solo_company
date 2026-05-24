# Easiio Docs Module Phase 1 Plan

## Goal

Create the reusable backend/content core for a documentation module that can later be embedded into any website and exported to WordPress, Sitelet, Next.js MDX, Docusaurus, MkDocs, Hugo, and VitePress.

## Phase 1 scope

Implemented now:

1. SQLite content store.
2. Per-site document spaces using `site_id`.
3. Document CRUD.
4. Revision history on every upsert.
5. Search/list filters.
6. Status, visibility, content format, framework target normalization.
7. Site summary/count endpoint.
8. Dependency-light Python HTTP API.
9. Unit tests and smoke validation.

## Out of scope for Phase 1

Deferred to later phases:

- embeddable `docs.js` frontend
- WordPress shortcode/plugin
- Sitelet preview renderer
- chatbot RAG sync
- Docusaurus/MkDocs/Hugo/VitePress exporters
- authentication/role protection
- admin UI

## API surface

```text
GET  /health
GET  /api/docs/docs?site_id=...&q=...&status=...&visibility=...
GET  /api/docs/doc?site_id=...&slug=...
POST /api/docs/doc
POST /api/docs/doc/delete
GET  /api/docs/revisions?site_id=...&slug=...
GET  /api/docs/space?site_id=...
```

## Verification

```bash
python3 -m py_compile backend/app.py backend/docs_db.py
python3 tests/test_docs_backend.py -v
```

Runtime smoke passed with temporary DB under `/tmp/easiio-docs-phase1-smoke`.
