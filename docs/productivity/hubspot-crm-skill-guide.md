# HubSpot CRM skill guide

This guide packages a reusable Hermes skill for connecting to HubSpot CRM with a private app token and performing review-first CRM operations.

## Included assets

- `skills/productivity/hubspot-crm/SKILL.md`
- `skills/productivity/hubspot-crm/scripts/hubspot_crm.py`
- `skills/productivity/hubspot-crm/templates/hubspot-private-app.env.example`
- `skills/productivity/hubspot-crm/references/object-cheatsheet.md`
- `skills/productivity/hubspot-crm/tests/test_hubspot_crm.py`

## What the skill supports now

- auth setup via `HUBSPOT_ACCESS_TOKEN`
- owner listing
- pipeline listing
- generic object get/search commands
- contact-specific search
- contact upsert with dry-run support
- raw API fallback for unsupported endpoints

## Safe operating model

1. start with read-only calls
2. search before create
3. preview writes with `--dry-run` when helpful
4. re-read after mutation
5. keep destructive or bulk writes behind explicit user approval

## Suggested next implementation phase

Upgrade this into a dedicated HubSpot MCP server when you need:

- property discovery tools
- notes / engagements creation
- association helpers
- pipeline-stage aware deal transitions
- repeatable website-to-HubSpot lead ingestion workflows
