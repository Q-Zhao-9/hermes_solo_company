---
name: campaign-execution
description: Prepare approval packages, publishing queues, execution checklists, approval change logs, and human operator handoffs for marketing campaigns.
version: 1.0.0
metadata:
  hermes:
    tags: [marketing, execution, approval, publishing, handoff, ai-solo-company]
    category: marketing
    related_skills: [marketing-agency-orchestrator, content-studio, seo-geo-growth, lead-detection, marketing-analytics, competitor-intelligence]
---

# Campaign Execution

Use this skill when the user wants Hermes to prepare campaign assets for human
approval and execution.

This skill does not publish, send, deploy, or modify live systems. It creates
operator-ready local files.

## Workflow

```bash
scripts/marketing_agency.py create-approval-package \
  --project-dir "<project dir>" \
  --channels "LinkedIn,Email,SEO blog" \
  --owner "<approver>" \
  --due "<due date>"

scripts/marketing_agency.py record-approval \
  --project-dir "<project dir>" \
  --decision approved \
  --approver "<name>" \
  --notes "<approval notes>"

scripts/marketing_agency.py operator-handoff \
  --project-dir "<project dir>" \
  --operator "<operator or team>"
```

## What It Produces

- `docs/execution/approval-package.md`
- `docs/execution/approval-package.json`
- `docs/execution/publishing-queue.json`
- `docs/execution/approval-change-log.md`
- `docs/execution/approval-change-log.json`
- `docs/execution/operator-handoff.md`
- `docs/execution/operator-handoff.json`

## Approval Rules

Never execute the queue automatically. The handoff is for a human operator or a
separate approved execution tool. If the user asks to actually publish, send,
deploy, or update a CRM, confirm explicit approval and use the correct platform
skill or integration.
