---
name: platform-integration-handoff
description: Prepare approved marketing execution queues for social, email, website, WordPress, or CRM platform handoff, and capture execution evidence.
version: 1.0.0
metadata:
  hermes:
    tags: [marketing, integrations, social, email, wordpress, crm, evidence]
    category: marketing
    related_skills: [marketing-agency-orchestrator, campaign-execution, content-studio, lead-detection, marketing-analytics]
---

# Platform Integration Handoff

Use this skill after an approval package has been approved and the user wants to
prepare queue items for a specific platform or record evidence after execution.

This skill does not call platform APIs. It prepares clean handoff files for
manual operators or future approved API integrations.

## Workflow

```bash
scripts/marketing_agency.py prepare-integration-handoff \
  --project-dir "<project dir>" \
  --platform social \
  --provider LinkedIn \
  --destination "company page"

scripts/marketing_agency.py capture-execution-evidence \
  --project-dir "<project dir>" \
  --item-id "<queue item id>" \
  --platform LinkedIn \
  --status published \
  --url "<published URL>" \
  --operator "<operator>"
```

Supported platform categories:

- `social`
- `email`
- `website`
- `wordpress`
- `crm`

## What It Produces

- `docs/integrations/<platform-provider>-handoff.md`
- `docs/integrations/<platform-provider>-handoff.json`
- `docs/integrations/execution-evidence.md`
- `docs/integrations/execution-evidence.json`

## Approval Rules

Only prepare normal handoffs for approved packages. Use `--force` only for a
draft planning handoff. Do not publish, send, import, deploy, or update records
unless the user explicitly approves a separate execution step.
