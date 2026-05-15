---
name: multi-brand-workspace
description: Manage a local multi-brand marketing workspace with brand registry, governance defaults, portfolio summaries, and cross-brand digests.
version: 1.0.0
metadata:
  hermes:
    tags: [marketing, portfolio, multi-brand, governance, reporting]
    category: marketing
    related_skills: [marketing-agency-orchestrator, monitoring-automation, marketing-analytics, campaign-execution]
---

# Multi-Brand Workspace

Use this skill when the user manages multiple brands, clients, products, or
business units and wants Hermes to summarize them together.

This skill is local-only. It reads registered marketing project folders and
writes workspace artifacts. It does not call social APIs, publish content,
send messages, update CRM records, or grant real platform permissions.

## Commands

Register an existing brand project:

```bash
scripts/marketing_agency.py register-brand \
  --workspace-dir "<workspace dir>" \
  --project-dir "<brand project dir>" \
  --owner "<owner>" \
  --channels "LinkedIn,SEO blog,Email"
```

Update brand governance defaults:

```bash
scripts/marketing_agency.py brand-governance \
  --workspace-dir "<workspace dir>" \
  --brand-id "<brand id>" \
  --approval-policy "Founder approval required before publishing."
```

Generate portfolio summary:

```bash
scripts/marketing_agency.py portfolio-summary \
  --workspace-dir "<workspace dir>" \
  --period "2026-W20"
```

Generate cross-brand digest:

```bash
scripts/marketing_agency.py cross-brand-digest \
  --workspace-dir "<workspace dir>" \
  --period "2026-W20" \
  --audience "executive team"
```

## Artifacts

The workflow writes:

- `docs/hermes-marketing-workspace.json`
- `docs/portfolio/brand-registry.md`
- `docs/portfolio/brand-registry.json`
- `docs/portfolio/brand-governance.md`
- `docs/portfolio/brand-governance.json`
- `docs/portfolio/portfolio-summary.md`
- `docs/portfolio/portfolio-summary.json`
- `docs/portfolio/cross-brand-digest.md`
- `docs/portfolio/cross-brand-digest.json`

## Routing Rules

- Use `register-brand` after each brand has a strategy project.
- Use `brand-governance` to document allowed local actions, default channels,
  and approval policy.
- Use `portfolio-summary` for operational review across all registered
  brands.
- Use `cross-brand-digest` for an executive update combining alerts, leads,
  campaign status, and recent performance.

## Safety

Workspace governance is documentation only. It does not create real platform
permissions and does not override approval rules. External publishing, sending,
CRM writes, ad changes, or production website edits still require explicit user
approval.
