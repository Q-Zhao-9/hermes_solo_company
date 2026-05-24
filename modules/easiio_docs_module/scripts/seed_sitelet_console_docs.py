#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from docs_db import DocsStore  # noqa: E402

SITE_ID = "sitelet-console"
DEFAULT_DB = ROOT / "data" / "easiio_docs.db"
DB_PATH = Path(os.environ.get("EASIIO_DOCS_DB", str(DEFAULT_DB)))
COMMON_TARGETS = ["sitelet", "static-html", "nextjs-mdx", "rag"]

DOCS = [
    {
        "slug": "getting-started",
        "title": "Getting Started with Sitelet",
        "summary": "Understand what Sitelet does and how to use the console.",
        "category": "Sitelet Guide",
        "tags": ["sitelet", "dashboard", "getting-started"],
        "content": """# Getting Started with Sitelet

Sitelet is the Easiio mini-site console for turning generated HTML, multi-page static sites, and WordPress-style previews into reusable preview links.

## Main workflow

- Open the Sitelet dashboard.
- Create or upload a generated page/site through Hermes or the API.
- Review the generated URL and the wrapped Sitelet preview URL.
- Manage the Sitelet from its Control Center.
- Share, collaborate, export, or prepare publish/deployment handoff when ready.

## Important URLs

- `/dashboard` — your generated Sitelet history.
- `/sitelets` — owner Sitelet list.
- `/sitelets/<id>` — Sitelet Control Center.
- `/docs` — this documentation module.

Sitelet is local-first by default and keeps high-risk actions such as publishing, WordPress updates, CRM outreach, DNS, and deployment behind explicit review or confirmation gates.
""",
    },
    {
        "slug": "preview-and-share",
        "title": "Preview and Share Sitelets",
        "summary": "Use generated URLs, Sitelet previews, share links, embeds, and custom slugs.",
        "category": "Preview",
        "tags": ["preview", "share", "embed"],
        "content": """# Preview and Share Sitelets

Sitelet has several URL types:

- `/generated/<id>/` — direct generated content preview.
- `/sitelet?url=<generated-url>` — wrapped Sitelet preview URL for sharing.
- `/s/<id>/` — public share URL.
- `/embed/<id>/` — iframe/embed view.
- `/u/<custom-slug>/` — custom slug route after share settings are configured.

## Best practice

Use the wrapped Sitelet preview or public share URL when sending a link to a client or teammate. Direct generated URLs are useful for debugging, while `/sitelet?url=...` preserves the Sitelet preview frame.

Hosted Sitelet links should use the public host, for example `https://sitelet.easiiodev.ai`, not `localhost`.
""",
    },
    {
        "slug": "dashboard-and-control-center",
        "title": "Dashboard and Sitelet Control Center",
        "summary": "Navigate the dashboard and per-Sitelet management pages.",
        "category": "Console",
        "tags": ["dashboard", "control-center", "versions"],
        "content": """# Dashboard and Sitelet Control Center

The dashboard shows generated Sitelets, quick actions, previews, and owner tools.

The per-Sitelet Control Center at `/sitelets/<id>` provides:

- Identity, status, visibility, and version metadata.
- Version history and restore/rollback references.
- Publish readiness.
- Share, embed, review, and business links.
- Analytics, leads, CRM handoff, permissions, and audit summaries.
- Advanced cleanup and retention plans.

Use the Control Center as the main operational page for each Sitelet.
""",
    },
    {
        "slug": "collaboration-and-review",
        "title": "Collaboration and Review",
        "summary": "Use review links, comments, approvals, and client workspace access safely.",
        "category": "Collaboration",
        "tags": ["review", "approval", "client-workspace"],
        "content": """# Collaboration and Review

Sitelet collaboration supports review links, reviewer tokens, comments, resolution states, and approval status by version.

## Review flow

- Create or update a Sitelet.
- Open the review workspace.
- Invite reviewers with scoped reviewer/client links.
- Collect comments and approvals.
- Publish only after the current version is approved.

Client workspace tokens and owner tokens are redacted from owner UI and audit logs. Do not paste private tokens into public documentation or chat.
""",
    },
    {
        "slug": "export-and-wordpress",
        "title": "Export and WordPress Handoff",
        "summary": "Prepare static exports, WordPress packages, and draft-first WordPress MCP handoffs.",
        "category": "Export",
        "tags": ["export", "wordpress", "draft"],
        "framework_targets": ["sitelet", "wordpress-shortcode", "static-html", "rag"],
        "content": """# Export and WordPress Handoff

Sitelet export workflows are draft-first and review-first.

## Supported handoffs

- Static ZIP export for plain hosting.
- WordPress-ready ZIP export.
- WordPress draft plan for Hermes MCP execution.
- WordPress draft execution handoff and result logging.

## Safety model

Sitelet does not publish to WordPress automatically. WordPress MCP workflows should create drafts only, verify the draft status, and record results back into Sitelet. Publishing requires separate explicit approval.
""",
    },
    {
        "slug": "analytics-leads-and-crm",
        "title": "Analytics, Leads, and CRM",
        "summary": "Track local analytics, capture leads, and prepare CRM sync handoffs.",
        "category": "Growth",
        "tags": ["analytics", "leads", "crm"],
        "content": """# Analytics, Leads, and CRM

Sitelet can track local analytics events and capture leads from public Sitelets.

## Available tools

- Analytics summary and recent events.
- Lead form configuration.
- Lead submission and listing.
- CRM sync plan and result logging.
- Business reports and conversion recommendations.

Raw IP addresses are not stored; visitor/IP identifiers are hashed. CRM outreach remains blocked unless explicitly approved by the operator.
""",
    },
    {
        "slug": "publishing-and-operations",
        "title": "Publishing and Operations",
        "summary": "Understand publish gates, rollback, deploy preparation, audit, and cleanup.",
        "category": "Operations",
        "tags": ["publish", "rollback", "audit", "cleanup"],
        "content": """# Publishing and Operations

Publishing is approval-gated. A Sitelet version must be approved before it can be published.

## Operational workflows

- Publish current approved version.
- Roll back to an earlier version by creating a new current version from history.
- Configure share settings and custom slugs.
- Prepare deployment destination plans.
- Review audit logs.
- Run retention cleanup dry-runs before destructive actions.

DNS, TLS, external deployment, WordPress publish, CRM mutation, billing, and outreach are not executed automatically.
""",
    },
    {
        "slug": "templates-agents-and-interactive-docs",
        "title": "Templates, Agents, and Interactive Docs",
        "summary": "Use remix/template metadata, local agent panels, and safe interactive documents.",
        "category": "Advanced",
        "tags": ["templates", "agents", "interactive"],
        "content": """# Templates, Agents, and Interactive Docs

Sitelet supports advanced local-first capabilities:

- Clone/remix an existing Sitelet into a new draft.
- Mark a Sitelet as a reusable template.
- Configure a per-Sitelet agent panel.
- Add safe interactive document blocks, calculators, knowledge capsules, telemetry previews, and workflow metadata.

These features are preview/configuration layers. They do not call LLMs, submit orders, process payments, control devices, or mutate external systems by default.
""",
    },
    {
        "slug": "admin-and-settings",
        "title": "Admin and Settings",
        "summary": "Manage tokens, organizations, backups, domains, usage, and admin operations.",
        "category": "Admin",
        "tags": ["settings", "admin", "tokens"],
        "content": """# Admin and Settings

The Settings and Admin areas manage operational configuration.

## Settings pages

- Token and API access.
- Organization settings.
- Backup and retention.
- Domains and deployment metadata.

## Admin console

The admin console includes operational monitoring, account/user views, usage metadata, and audit information. Owner/admin surfaces remain protected by owner token, session role, or equivalent local-owner protection.
""",
    },
    {
        "slug": "docs-module-integration",
        "title": "Docs Module Integration in Sitelet",
        "summary": "How the Easiio Docs Module is embedded into the Sitelet console.",
        "category": "Docs Module",
        "tags": ["docs-module", "sitelet-console", "integration"],
        "content": """# Docs Module Integration in Sitelet

The Sitelet console embeds the Easiio Docs Module at `/docs`.

## Integration model

- `site_id`: `sitelet-console`.
- Widget assets: `/docs/docs.js` and `/docs/docs.css`.
- Browser API base: same-origin `.`.
- Proxy route: `/api/docs/*`.
- Docs backend: configured server-side with `EASIIO_DOCS_API_BASE`.

The browser never receives the docs owner token. Public docs reads load published public documents only. Admin/write actions should stay in the protected docs admin UI or be added later behind server-side owner authorization.
""",
    },
]


def seed() -> None:
    store = DocsStore(DB_PATH)
    store.ensure_space(
        SITE_ID,
        name="Sitelet Console Documentation",
        description="Operator and user guide for creating, previewing, sharing, exporting, publishing, and operating Sitelets.",
    )
    for doc in DOCS:
        payload = {
            "site_id": SITE_ID,
            "status": "published",
            "visibility": "public",
            "content_format": "markdown",
            "version_label": "v1",
            "locale": "en",
            "framework_targets": doc.get("framework_targets", COMMON_TARGETS),
            "rag_enabled": True,
            "changed_by": "seed_sitelet_console_docs.py",
            **doc,
        }
        store.upsert_doc(payload)
    print(f"seeded {len(DOCS)} docs for {SITE_ID} into {DB_PATH}")


if __name__ == "__main__":
    seed()
