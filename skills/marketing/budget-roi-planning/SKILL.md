---
name: budget-roi-planning
description: Plan marketing budgets, record spend/result snapshots, summarize ROI/CAC, and review portfolio budget performance.
version: 1.0.0
metadata:
  hermes:
    tags: [marketing, budget, roi, cac, finance, analytics]
    category: marketing
    related_skills: [marketing-agency-orchestrator, marketing-analytics, experiment-management, multi-brand-workspace]
---

# Budget ROI Planning

Use this skill when the user wants campaign budget planning, channel allocation,
spend tracking, ROI/CAC summaries, or portfolio budget review.

This skill creates local planning and reporting artifacts only. It does not
change ad budgets, publish ads, call ad platform APIs, or modify billing.

## Commands

Create a budget plan:

```bash
scripts/marketing_agency.py create-budget-plan \
  --project-dir "<project dir>" \
  --budget 3000 \
  --period "2026-Q2" \
  --channels "LinkedIn,SEO blog,Email"
```

Record spend and result metrics:

```bash
scripts/marketing_agency.py record-spend \
  --project-dir "<project dir>" \
  --plan-id "<budget plan id>" \
  --channel LinkedIn \
  --metrics "spend=500,revenue=1200,leads=6,conversions=2"
```

Generate a budget report:

```bash
scripts/marketing_agency.py budget-report \
  --project-dir "<project dir>" \
  --plan-id "<budget plan id>" \
  --period "2026-Q2"
```

Generate portfolio budget review:

```bash
scripts/marketing_agency.py portfolio-budget-review \
  --workspace-dir "<workspace dir>" \
  --period "2026-Q2"
```

## Artifacts

Brand project artifacts:

- `docs/budget/budget-plans.md`
- `docs/budget/budget-plans.json`
- `docs/budget/spend-snapshots.md`
- `docs/budget/spend-snapshots.json`
- `docs/budget/budget-report.md`
- `docs/budget/budget-report.json`

Portfolio artifacts:

- `docs/portfolio/budget-review.md`
- `docs/portfolio/budget-review.json`

## Safety

Budget plans and reports are recommendations only. Ask for explicit approval
before changing live ad spend, billing settings, campaign budgets, or external
platform configuration.
