---
name: experiment-management
description: Plan campaign experiments, record variant metrics, recommend winners, and summarize experiment history for brand and portfolio marketing workflows.
version: 1.0.0
metadata:
  hermes:
    tags: [marketing, experiments, ab-testing, optimization, analytics]
    category: marketing
    related_skills: [marketing-agency-orchestrator, marketing-analytics, campaign-execution, multi-brand-workspace]
---

# Experiment Management

Use this skill when the user wants A/B tests, campaign experiments, variant
tracking, winner recommendations, or portfolio experiment history.

This skill creates local planning and reporting artifacts only. It does not
publish variants, change ads, modify landing pages, send emails, or call
external analytics systems.

## Commands

Create an experiment plan:

```bash
scripts/marketing_agency.py create-experiment \
  --project-dir "<project dir>" \
  --name "<experiment name>" \
  --hypothesis "<test hypothesis>" \
  --metric ctr \
  --variants "Control,Variant A"
```

Record variant metrics:

```bash
scripts/marketing_agency.py record-experiment-result \
  --project-dir "<project dir>" \
  --experiment-id "<experiment id>" \
  --variant "Variant A" \
  --metrics "impressions=1000,clicks=50,leads=6,conversions=2"
```

Generate a winner recommendation:

```bash
scripts/marketing_agency.py experiment-report \
  --project-dir "<project dir>" \
  --experiment-id "<experiment id>" \
  --period "2026-W21"
```

Generate portfolio experiment history:

```bash
scripts/marketing_agency.py portfolio-experiment-history \
  --workspace-dir "<workspace dir>" \
  --period "2026-W21"
```

## Artifacts

Brand project artifacts:

- `docs/experiments/experiment-plans.md`
- `docs/experiments/experiment-plans.json`
- `docs/experiments/experiment-results.md`
- `docs/experiments/experiment-results.json`
- `docs/experiments/experiment-report.md`
- `docs/experiments/experiment-report.json`

Portfolio artifacts:

- `docs/portfolio/experiment-history.md`
- `docs/portfolio/experiment-history.json`

## Safety

Experiment plans and reports are recommendations only. Ask for explicit
approval before publishing variants, changing live ads, editing production
pages, sending email variants, or changing external campaign settings.
