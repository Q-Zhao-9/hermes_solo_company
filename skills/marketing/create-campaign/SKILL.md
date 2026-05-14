---
name: create-campaign
description: Create a marketing campaign plan from an existing Hermes marketing strategy project, including objective, channels, themes, weekly plan, CTA, and success metrics.
version: 1.0.0
metadata:
  hermes:
    tags: [marketing, campaign, content-calendar, growth]
    category: marketing
    related_skills: [marketing-agency-orchestrator, marketing-strategy]
---

# Create Campaign

Use this skill when the user asks for a marketing campaign, launch campaign,
growth campaign, content campaign, social campaign, or SEO campaign.

Campaigns must connect to a business objective. Do not create isolated posts.

## Helper

```bash
scripts/marketing_agency.py create-campaign \
  --project-dir "<project dir>" \
  --name "<campaign name>" \
  --objective "<objective>" \
  --channels "LinkedIn,SEO blog,YouTube demos,Email" \
  --duration "4 weeks" \
  --cta "<call to action>"
```

If channels are not provided, use the latest strategy's recommended channels.

## Output Expectations

Return:

- campaign artifact path
- audience
- objective
- selected channels
- weekly plan
- success metrics
- approval note

The campaign is a plan and content brief. Publishing, email sending, ad spend,
and CRM updates require explicit approval.

After the campaign is created, use Phase 2 helpers:

```bash
scripts/marketing_agency.py generate-content-plan --project-dir "<project dir>" --campaign "<campaign-slug>"
scripts/marketing_agency.py generate-posts --project-dir "<project dir>" --campaign "<campaign-slug>" --channels "LinkedIn,X,SEO blog,Email"
```
