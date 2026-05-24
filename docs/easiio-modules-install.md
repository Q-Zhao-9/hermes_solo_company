# Easiio Module Installation

This repository includes source-only reusable Easiio modules under `modules/`.

## Quick install

```bash
scripts/install_easiio_modules.sh
```

This installs:

```text
modules/solo_crm            -> ~/.hermes/tools/solo_crm
modules/website_chatbot     -> ~/.hermes/tools/website_chatbot
modules/easiio_docs_module  -> ~/.hermes/tools/easiio_docs_module
```

## Recommended student workflow

```bash
git clone git@github.com:Easiio-Inc/hermes_solo_company.git
cd hermes_solo_company
scripts/install_easiio_modules.sh --dry-run
scripts/install_easiio_modules.sh
```

Then restart Hermes if it is already running.

## What is not installed from Git

The installer intentionally does not copy runtime/private files:

```text
*.db
*.env
data/
dist/
__pycache__/
.pytest_cache/
*.pyc
*.zip
uploaded/downloaded files
```

Each student/operator should have their own local runtime databases and environment files.

## Module purpose

### `solo_crm`

A lightweight SQLite-backed CRM with MCP server support. It tracks contacts, companies, deals, activities, follow-ups, website visitors, website visits, organizations, and websites.

### `website_chatbot`

Embeddable website AI assistant with:

- browser widget
- backend HTTP API
- lightweight RAG/content retrieval by `site_id`
- CRM lead capture integration
- admin customizer
- WordPress chatbot plugin source

### `easiio_docs_module`

Reusable documentation / knowledge-base module with:

- docs backend and SQLite content model
- embeddable frontend docs widget
- admin editor UI
- RAG sync helpers
- Sitelet preview/export helpers
- WordPress shortcode plugin source
- deployment/release helper modules and tests
