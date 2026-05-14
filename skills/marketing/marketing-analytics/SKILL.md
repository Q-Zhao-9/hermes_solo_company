---
name: marketing-analytics
description: Create reviewable marketing performance snapshots, lead funnel summaries, optimization recommendations, and manager dashboards from local campaign state.
version: 1.0.0
metadata:
  hermes:
    tags: [marketing, analytics, dashboard, optimization, reporting, ai-solo-company]
    category: marketing
    related_skills: [marketing-agency-orchestrator, create-campaign, content-studio, seo-geo-growth, lead-detection]
---

# Marketing Analytics

Use this skill when the user wants Hermes to review campaign performance,
summarize social or SEO results, analyze lead funnel quality, or create a
manager dashboard for the solo company marketing workflow.

## Workflow

Metrics are local review inputs. Hermes does not connect to ad platforms or
analytics APIs from this skill.

```bash
scripts/marketing_agency.py record-performance \
  --project-dir "<project dir>" \
  --channel "LinkedIn" \
  --period "2026-W20" \
  --metrics "impressions=1000,engagements=80,clicks=35,leads=4,conversions=1,spend=120,revenue=600"

scripts/marketing_agency.py generate-review-dashboard \
  --project-dir "<project dir>" \
  --focus "weekly executive review" \
  --period "2026-W20"
```

## What It Produces

- `docs/analytics/performance-snapshots.md`
- `docs/analytics/performance-snapshots.json`
- `docs/analytics/manager-review-dashboard.md`
- `docs/analytics/manager-review-dashboard.json`

## Metrics

Supported metric keys:

- `impressions`
- `engagements`
- `clicks`
- `leads`
- `conversions`
- `spend`
- `revenue`

Hermes calculates CTR, engagement rate, lead rate, conversion rate, cost per
lead, and ROAS.

## Approval Rules

Do not modify live campaigns, budgets, ads, CRM records, websites, or social
posts from this skill. Treat recommendations as a review artifact until the
user explicitly approves an execution step.
