# Hermes Marketing Agency Student Guide

This guide shows the Phase 1 workflow for the Hermes AI solo company marketing
agency bot.

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
docs/hermes-marketing-state.json
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

## Phase 3 Preview

The next phase should add SEO/GEO depth:

- keyword clusters
- blog briefs by search intent
- AI answer engine optimization
- schema recommendations
- landing page SEO tasks
- internal linking plan
