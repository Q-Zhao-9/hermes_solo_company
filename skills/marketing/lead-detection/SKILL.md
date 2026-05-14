---
name: lead-detection
description: Detect, score, and prepare review-only outreach for marketing and sales leads without sending messages or writing live CRM records.
version: 1.0.0
metadata:
  hermes:
    tags: [marketing, leads, crm, outreach, sdr, ai-solo-company]
    category: marketing
    related_skills: [marketing-agency-orchestrator, marketing-strategy, create-campaign, content-studio, seo-geo-growth]
---

# Lead Detection

Use this skill when the user wants Hermes to identify buying intent, score a
lead, draft outreach, or prepare CRM-ready handoff files.

## Workflow

Run this after a marketing strategy exists:

```bash
scripts/marketing_agency.py define-lead-signals --project-dir "<project dir>"
scripts/marketing_agency.py score-lead --project-dir "<project dir>" --name "<lead>" --company "<company>" --text "<lead text>"
scripts/marketing_agency.py draft-outreach --project-dir "<project dir>" --channel email
scripts/marketing_agency.py crm-export --project-dir "<project dir>" --format json
```

## What It Produces

- `docs/leads/lead-signals.md`
- `docs/leads/lead-signals.json`
- `docs/leads/lead-scorecards.md`
- `docs/leads/lead-scorecards.json`
- `docs/leads/outreach-drafts.md`
- `docs/leads/outreach-drafts.json`
- `docs/leads/crm-export.json` or `docs/leads/crm-export.csv`

## Scoring Guidance

Treat these as positive signals:

- explicit need for the offer
- vendor evaluation
- demo, pricing, or recommendation requests
- ICP industry or role fit
- pain points already defined in the strategy

Treat these as negative signals:

- student research
- job applications
- free-only requests
- statements that the problem is already solved
- unrelated competitor hiring or market chatter

## Approval Rules

Never send outreach, reply to DMs, post comments, or write CRM records from this
skill. The commands only create review artifacts. Ask for explicit approval
before using any email, social, CRM, or browser automation integration.
