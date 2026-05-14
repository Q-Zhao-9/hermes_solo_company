---
name: social-calendar
description: Create weekly social/content calendars from Hermes marketing campaign state, including channels, funnel stage, theme, format, angle, CTA, and approval status.
version: 1.0.0
metadata:
  hermes:
    tags: [marketing, content-calendar, social-media, campaign-planning]
    category: marketing
    related_skills: [marketing-agency-orchestrator, create-campaign, content-studio]
---

# Social Calendar

Use this skill when the user asks for a weekly content plan, monthly content
calendar, social media schedule, campaign calendar, or platform cadence.

Calendars should be tied to campaign strategy and review status.

## Helper

```bash
scripts/marketing_agency.py generate-content-plan \
  --project-dir "<project dir>" \
  --weeks 4 \
  --cadence 3 \
  --channels "LinkedIn,X,SEO blog,Email"
```

If channels are omitted, the helper uses the latest campaign channels.

## Output Expectations

Return:

- content calendar artifact path
- weeks and cadence
- channels
- themes
- funnel stages
- CTA
- approval status

The content calendar is a planning artifact. Publishing and scheduling require
explicit approval.
