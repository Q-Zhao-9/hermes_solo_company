---
name: hubspot-crm
description: Connect Hermes to HubSpot CRM using a private app token, then search, create, and update contacts, companies, deals, owners, and pipelines with a review-first workflow.
version: 0.1.0
author: Nous Research
license: MIT
metadata:
  hermes:
    tags: [HubSpot, CRM, Sales, Contacts, Deals, Companies, Private App, API]
    related_skills: [standalone-mcp-server, native-mcp, class12-crm-update-handoff]
---

# HubSpot CRM

Connect Hermes to HubSpot with a **private app token** and use the HubSpot CRM object APIs in a safe, review-first way.

## References

- `references/object-cheatsheet.md` — common object names, search filters, and starter examples

## Scripts

- `scripts/hubspot_crm.py` — lightweight HubSpot CRM helper CLI for search, get, upsert, owner listing, pipeline listing, and raw API calls

## Templates

- `templates/hubspot-private-app.env.example` — example environment variables for a HubSpot private app token setup

## When to use this skill

Use this skill when the user wants Hermes to:

- connect to HubSpot CRM
- search contacts, companies, or deals
- create or update CRM records
- inspect owners or pipelines
- prepare a review-first CRM handoff workflow
- wire a website/chatbot lead flow into HubSpot later

## Default auth model

Use a **HubSpot private app token** first.

Required environment variable:

```bash
export HUBSPOT_ACCESS_TOKEN='...'
```

Optional base URL override:

```bash
export HUBSPOT_BASE_URL='https://api.hubapi.com'
```

Do not paste the raw token into chat unless the user explicitly asks you to store or inspect it.

## Setup checklist

1. Ask whether the user wants **read-only inspection** or **live CRM writes**.
2. Confirm they have a HubSpot private app token with the needed scopes.
3. Check that `HUBSPOT_ACCESS_TOKEN` is set before calling the API.
4. Search before creating records to avoid duplicates.
5. For writes, summarize the intended mutation before executing it.

## First-time connection check

Set a shorthand:

```bash
HS="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/hubspot-crm/scripts/hubspot_crm.py"
```

Verify the token is present:

```bash
env | grep '^HUBSPOT_ACCESS_TOKEN='
```

Then test with a harmless read:

```bash
$HS owners list
$HS pipelines list deals
```

If the token is missing or the API returns 401/403, stop and fix scopes or auth before doing CRM work.

## Core workflow

### 1. Search before create

Search the relevant object first.

```bash
$HS contacts search --email person@example.com
$HS companies search --domain example.com
$HS objects search deals --filter pipeline=pipeline_id --query "Acme"
```

### 2. Confirm the mutation target

Before creating or updating:

- identify the exact record to change
- confirm the property names
- summarize the intended mutation

### 3. Write only the minimum properties needed

Prefer a minimal payload. Avoid sending giant property blobs unless the user asked for a full sync.

### 4. Re-read after write

After a create or update, fetch the record again or run the same search to confirm the expected state.

## Common commands

### Owners and pipelines

```bash
$HS owners list
$HS pipelines list deals
$HS pipelines list tickets
```

### Generic object reads

```bash
$HS objects get contacts 123 --properties email,firstname,lastname
$HS objects get companies 456 --properties name,domain,phone
$HS objects search contacts --query "alice" --properties email,firstname,lastname
$HS objects search deals --filter pipeline=default --properties dealname,pipeline,dealstage
```

### Contact upsert

```bash
$HS contacts upsert \
  --email person@example.com \
  --firstname Alice \
  --lastname Chen \
  --phone '+1 555 0101' \
  --company 'Acme Labs' \
  --lifecyclestage lead
```

Add `--dry-run` first when you want a payload preview without writing.

### Raw fallback

For unsupported endpoints, use a raw call:

```bash
$HS raw GET /crm/v3/objects/contacts/123
$HS raw POST /crm/v3/objects/deals/search --body-json '{"limit": 5}'
```

## Review-first operating rules

- Search before create.
- Use `--dry-run` before writes when the request is ambiguous or high-risk.
- For destructive actions or bulk writes, get explicit user approval first.
- After writes, re-read the record and summarize what changed.
- Keep a clean audit trail in your response.

## Guardrails

- Do not expose the HubSpot token.
- Do not create duplicate contacts or companies without checking first.
- Do not guess property internal names if the user can provide them.
- Do not bulk update records unless the scope is explicit.
- Do not delete records unless the user clearly asked for deletion.

## Output format

When reporting HubSpot work, prefer:

```text
## Goal
## Auth check
## Search result
## Proposed mutation
## Execution result
## Verification
## Risks / follow-up
```

## Suggested next expansion

If the user wants deeper integration later, upgrade this skill into a dedicated HubSpot MCP server with toolized operations for:

- contacts
- companies
- deals
- notes / engagements
- associations
- property discovery
- pipeline-stage aware updates
