---
name: competitor-intelligence
description: Track competitor profiles, market observations, positioning gaps, trend watch topics, and response campaign recommendations from local notes.
version: 1.0.0
metadata:
  hermes:
    tags: [marketing, competitors, intelligence, positioning, trends, ai-solo-company]
    category: marketing
    related_skills: [marketing-agency-orchestrator, marketing-strategy, create-campaign, content-studio, seo-geo-growth, marketing-analytics]
---

# Competitor Intelligence

Use this skill when the user wants Hermes to track competitors, summarize market
moves, compare positioning, identify gaps, or recommend response campaigns.

This skill does not browse or monitor the internet by itself. It turns
user-supplied competitor notes into structured local memory and reports.

## Workflow

```bash
scripts/marketing_agency.py add-competitor \
  --project-dir "<project dir>" \
  --name "<competitor>" \
  --positioning "<observed positioning>" \
  --strengths "<comma-separated strengths>" \
  --weaknesses "<comma-separated weaknesses>"

scripts/marketing_agency.py track-competitor \
  --project-dir "<project dir>" \
  --competitor "<competitor id or name>" \
  --event-type "case study" \
  --channel "LinkedIn" \
  --summary "<observed market move>" \
  --impact high \
  --tags "case study,proof,pricing"

scripts/marketing_agency.py competitor-report \
  --project-dir "<project dir>" \
  --period "<period>"
```

## What It Produces

- `docs/competitors/competitor-profiles.md`
- `docs/competitors/competitor-profiles.json`
- `docs/competitors/competitor-observations.md`
- `docs/competitors/competitor-observations.json`
- `docs/competitors/competitor-intelligence-report.md`
- `docs/competitors/competitor-intelligence-report.json`

## Report Sections

- competitor profile memory
- recent competitor observations
- positioning gaps
- market trend topics
- response campaign recommendations

## Approval Rules

Do not attack competitors, publish comparison pages, change campaigns, run ads,
or contact leads from this skill without explicit user approval. Keep
recommendations factual and based on supplied observations.
