# Hermes Marketing Agency Student Guide

This guide shows the Hermes AI solo company marketing agency bot workflow.

## What Phase 1 Does

Phase 1 creates the foundation:

- marketing strategy
- ICP and positioning
- priority channels
- funnel stages
- content themes
- SEO and AI answer engine focus
- campaign plan and memory

It does not publish social posts, send emails, run ads, update CRM records, or
reply to customers. Those actions require later integrations and explicit
approval.

## What Phase 2 Adds

Phase 2 adds review-ready content planning:

- weekly content calendars
- campaign-to-channel adaptation
- LinkedIn drafts
- X/Twitter thread drafts
- SEO blog briefs
- YouTube script outlines
- email nurture drafts
- Discord/community announcements

## Common Flow

Create a strategy:

```bash
scripts/marketing_agency.py create-strategy \
  --brand "Acme LiDAR" \
  --business "LiDAR truck volume measurement systems for industrial logistics" \
  --audience "mining companies and aggregate producers" \
  --goal "Generate qualified demo requests" \
  --offer "automated truck volume measurement" \
  --tone "technical and executive"
```

Create a campaign:

```bash
scripts/marketing_agency.py create-campaign \
  --project-dir generated-marketing/acme-lidar \
  --name "Reduce Loading Loss" \
  --objective "reduce loading losses by 5%" \
  --duration "6 weeks" \
  --cta "Book a measurement demo"
```

Return a Discord-friendly status:

```bash
scripts/marketing_agency.py summary --project-dir generated-marketing/acme-lidar
```

Generate a content calendar:

```bash
scripts/marketing_agency.py generate-content-plan \
  --project-dir generated-marketing/acme-lidar \
  --weeks 4 \
  --cadence 3 \
  --channels "LinkedIn,X,SEO blog,Email"
```

Generate review-ready drafts:

```bash
scripts/marketing_agency.py generate-posts \
  --project-dir generated-marketing/acme-lidar \
  --channels "LinkedIn,X,SEO blog,Email,YouTube demos" \
  --count 1 \
  --stage consideration
```

## Generated Files

```text
docs/marketing-strategy.md
docs/campaigns/<campaign-slug>.md
docs/content/<campaign-slug>-content-calendar.md
docs/content/<campaign-slug>-content-calendar.json
docs/content/drafts/<campaign-slug>-drafts.md
docs/content/drafts/<campaign-slug>-drafts.json
```

The state file records strategy, campaign, content calendar, and draft history
so later phases can create lead scorecards, analytics reports, and review
dashboards from the same memory.

## Recommended Bot Behavior

For new marketing requests:

1. Understand the business and offer.
2. Define ICP, pain points, and buying triggers.
3. Pick priority channels.
4. Create funnel stages and campaign themes.
5. Create a campaign tied to a business objective.
6. Wait for review before publishing or sending anything.

## Safety

Draft by default. Ask for explicit approval before:

- publishing social posts
- sending emails or DMs
- replying to comments
- running ads
- writing CRM records
- changing production website, WordPress, or Shopify content

## What Phase 3 Adds

Phase 3 adds SEO/GEO depth:

- keyword clusters
- blog briefs by search intent
- AI answer engine optimization
- schema recommendations
- landing page SEO tasks
- internal linking plan

Generate an SEO/GEO plan:

```bash
scripts/marketing_agency.py generate-seo-plan \
  --project-dir generated-marketing/acme-lidar \
  --focus "truck volume measurement" \
  --pages 6 \
  --region "North America"
```

Generate blog briefs:

```bash
scripts/marketing_agency.py generate-blog-briefs \
  --project-dir generated-marketing/acme-lidar \
  --count 4 \
  --intent commercial
```

Phase 3 writes:

```text
docs/seo/seo-geo-plan.md
docs/seo/seo-geo-plan.json
docs/seo/blog-briefs.md
docs/seo/blog-briefs.json
```

## What Phase 4 Adds

Phase 4 adds lead detection and CRM handoff:

- lead signal definitions
- lead scorecards
- outreach drafts
- CRM-ready JSON/CSV export
- follow-up schedule

Define lead signals:

```bash
scripts/marketing_agency.py define-lead-signals \
  --project-dir generated-marketing/acme-lidar \
  --channels "LinkedIn,Reddit,Industry forums" \
  --signals "looking for volume measurement,asking for truck scale alternatives"
```

Score a lead:

```bash
scripts/marketing_agency.py score-lead \
  --project-dir generated-marketing/acme-lidar \
  --name "Jordan" \
  --company "North Ridge Aggregates" \
  --role "Operations Manager" \
  --source "LinkedIn" \
  --channel "LinkedIn" \
  --text "We are looking for truck volume measurement to reduce loading losses at our aggregate sites."
```

Draft outreach for review:

```bash
scripts/marketing_agency.py draft-outreach \
  --project-dir generated-marketing/acme-lidar \
  --channel email
```

Export CRM-ready rows:

```bash
scripts/marketing_agency.py crm-export \
  --project-dir generated-marketing/acme-lidar \
  --format csv \
  --owner sales
```

Phase 4 writes:

```text
docs/leads/lead-signals.md
docs/leads/lead-signals.json
docs/leads/lead-scorecards.md
docs/leads/lead-scorecards.json
docs/leads/outreach-drafts.md
docs/leads/outreach-drafts.json
docs/leads/crm-export.json
docs/leads/crm-export.csv
docs/hermes-marketing-state.json
```

## Phase 5 Preview

The next phase should add analytics and review dashboards:

- campaign performance snapshots
- content engagement analysis
- lead funnel metrics
- weekly optimization recommendations
- manager review dashboard for all generated artifacts
