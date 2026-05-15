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

## What Phase 5 Adds

Phase 5 adds analytics and review dashboards:

- campaign performance snapshots
- content engagement analysis
- lead funnel metrics
- weekly optimization recommendations
- manager review dashboard for all generated artifacts

Record performance metrics:

```bash
scripts/marketing_agency.py record-performance \
  --project-dir generated-marketing/acme-lidar \
  --channel LinkedIn \
  --period "2026-W20" \
  --metrics "impressions=1000,engagements=80,clicks=35,leads=4,conversions=1,spend=120,revenue=600" \
  --notes "ROI post outperformed technical post"
```

Generate a manager dashboard:

```bash
scripts/marketing_agency.py generate-review-dashboard \
  --project-dir generated-marketing/acme-lidar \
  --focus "weekly executive review" \
  --period "2026-W20"
```

Phase 5 writes:

```text
docs/analytics/performance-snapshots.md
docs/analytics/performance-snapshots.json
docs/analytics/manager-review-dashboard.md
docs/analytics/manager-review-dashboard.json
docs/hermes-marketing-state.json
```

The dashboard summarizes artifact counts, campaign metrics, lead funnel
quality, pending review queues, and optimization recommendations. It is a
review artifact only; changing budgets, publishing content, or editing live
campaigns still requires explicit approval.

## What Phase 6 Adds

Phase 6 adds competitor intelligence:

- competitor profile memory
- competitor content/event tracking
- positioning gap analysis
- response campaign recommendations
- market trend watch reports

Add a competitor profile:

```bash
scripts/marketing_agency.py add-competitor \
  --project-dir generated-marketing/acme-lidar \
  --name "MeasureMax" \
  --positioning "Truck measurement dashboards for aggregates" \
  --strengths "customer proof,YouTube demos" \
  --weaknesses "limited workflow ROI content" \
  --channels "LinkedIn,SEO blog,YouTube"
```

Track a competitor move:

```bash
scripts/marketing_agency.py track-competitor \
  --project-dir generated-marketing/acme-lidar \
  --competitor measuremax \
  --event-type "case study" \
  --channel LinkedIn \
  --summary "Published a new quarry case study emphasizing loading accuracy" \
  --impact high \
  --tags "case study,accuracy,aggregates"
```

Generate a competitor intelligence report:

```bash
scripts/marketing_agency.py competitor-report \
  --project-dir generated-marketing/acme-lidar \
  --focus "weekly competitor watch" \
  --period "2026-W20"
```

Phase 6 writes:

```text
docs/competitors/competitor-profiles.md
docs/competitors/competitor-profiles.json
docs/competitors/competitor-observations.md
docs/competitors/competitor-observations.json
docs/competitors/competitor-intelligence-report.md
docs/competitors/competitor-intelligence-report.json
docs/hermes-marketing-state.json
```

The report summarizes competitor profiles, recent observations, positioning
gaps, market trend topics, and response campaign ideas. It does not browse the
internet or publish response content by itself.

## What Phase 7 Adds

Phase 7 adds campaign execution planning:

- approval packages for publish/send/deploy steps
- channel-specific execution checklists
- asset-to-channel publishing queue
- post-approval change log
- handoff package for human operators

Create an approval package:

```bash
scripts/marketing_agency.py create-approval-package \
  --project-dir generated-marketing/acme-lidar \
  --channels "LinkedIn,Email,SEO blog" \
  --owner "marketing lead" \
  --due "2026-05-20"
```

Record an approval decision:

```bash
scripts/marketing_agency.py record-approval \
  --project-dir generated-marketing/acme-lidar \
  --decision approved \
  --approver "Jane" \
  --notes "Approved for LinkedIn and email execution"
```

Generate a human operator handoff:

```bash
scripts/marketing_agency.py operator-handoff \
  --project-dir generated-marketing/acme-lidar \
  --operator "ops team"
```

Phase 7 writes:

```text
docs/execution/approval-package.md
docs/execution/approval-package.json
docs/execution/publishing-queue.json
docs/execution/approval-change-log.md
docs/execution/approval-change-log.json
docs/execution/operator-handoff.md
docs/execution/operator-handoff.json
docs/hermes-marketing-state.json
```

These files prepare execution, but they do not execute it. Publishing posts,
sending email, deploying pages, changing ads, or updating CRM records still
requires explicit approval and the correct platform integration.

## What Phase 8 Adds

Phase 8 adds platform integration handoff adapters:

- approved social publishing adapters
- email campaign provider handoff
- website/WordPress publishing bridge
- CRM import mapping
- execution evidence capture

Prepare a platform handoff after approval:

```bash
scripts/marketing_agency.py prepare-integration-handoff \
  --project-dir generated-marketing/acme-lidar \
  --platform social \
  --provider LinkedIn \
  --destination "company page"
```

Capture execution evidence:

```bash
scripts/marketing_agency.py capture-execution-evidence \
  --project-dir generated-marketing/acme-lidar \
  --item-id "<queue item id>" \
  --platform LinkedIn \
  --status published \
  --url "https://linkedin.example/post/1" \
  --screenshot "screenshots/post-1.png" \
  --operator "ops team"
```

Phase 8 writes:

```text
docs/integrations/<platform-provider>-handoff.md
docs/integrations/<platform-provider>-handoff.json
docs/integrations/execution-evidence.md
docs/integrations/execution-evidence.json
docs/hermes-marketing-state.json
```

Phase 8 still does not call platform APIs. It prepares approved queue items for
manual operators or future API integrations, then records evidence after a human
or approved external tool performs the action.

## What Phase 9 Adds

Phase 9 adds monitoring automation handoffs:

- saved brand, competitor, lead, keyword, and hashtag queries
- local monitor job definitions
- alert reports
- weekly digest generation

Create a saved monitor query:

```bash
scripts/marketing_agency.py create-monitor-query \
  --project-dir generated-marketing/acme-lidar \
  --name "High intent lead watch" \
  --type lead \
  --query "\"looking for truck volume measurement\"" \
  --channels "LinkedIn,X,Reddit" \
  --priority high
```

Create local monitor job handoffs:

```bash
scripts/marketing_agency.py schedule-monitor \
  --project-dir generated-marketing/acme-lidar \
  --cadence weekly \
  --owner "marketing ops" \
  --destination "weekly digest"
```

Record an alert:

```bash
scripts/marketing_agency.py record-monitor-alert \
  --project-dir generated-marketing/acme-lidar \
  --query-id high-intent-lead-watch \
  --title "Aggregate operator asks for vendor recommendations" \
  --summary "A procurement manager asked for truck volume measurement vendor recommendations" \
  --severity high \
  --source LinkedIn \
  --url "https://linkedin.example/post/lead" \
  --tags "lead,aggregates,vendor"
```

Generate a weekly digest:

```bash
scripts/marketing_agency.py weekly-digest \
  --project-dir generated-marketing/acme-lidar \
  --period "2026-W20" \
  --audience "founder and marketing team"
```

Phase 9 writes:

```text
docs/monitoring/monitor-queries.md
docs/monitoring/monitor-queries.json
docs/monitoring/monitor-jobs.md
docs/monitoring/monitor-jobs.json
docs/monitoring/monitor-alerts.md
docs/monitoring/monitor-alerts.json
docs/monitoring/weekly-digest.md
docs/monitoring/weekly-digest.json
docs/hermes-marketing-state.json
```

The monitor schedule is a local handoff file only. Phase 9 does not browse,
start a real scheduler, call social APIs, reply to comments, send outreach, or
update CRM records.

## What Phase 10 Adds

Phase 10 adds multi-brand workspace support:

- brand/account registry
- portfolio-level campaign summary
- cross-brand weekly digest
- brand-specific permissions and defaults

Register a brand project:

```bash
scripts/marketing_agency.py register-brand \
  --workspace-dir generated-marketing \
  --project-dir generated-marketing/acme-lidar \
  --owner "Jane" \
  --channels "LinkedIn,SEO blog,Email" \
  --approval-policy "Jane approval required before external action"
```

Update brand governance:

```bash
scripts/marketing_agency.py brand-governance \
  --workspace-dir generated-marketing \
  --brand-id acme-lidar \
  --channels "LinkedIn,YouTube demos" \
  --permissions "draft_content,capture_manual_evidence" \
  --approval-policy "Founder approval required before publishing"
```

Generate portfolio summary:

```bash
scripts/marketing_agency.py portfolio-summary \
  --workspace-dir generated-marketing \
  --period "2026-W20"
```

Generate cross-brand digest:

```bash
scripts/marketing_agency.py cross-brand-digest \
  --workspace-dir generated-marketing \
  --period "2026-W20" \
  --audience "executive team"
```

Phase 10 writes:

```text
docs/hermes-marketing-workspace.json
docs/portfolio/brand-registry.md
docs/portfolio/brand-registry.json
docs/portfolio/brand-governance.md
docs/portfolio/brand-governance.json
docs/portfolio/portfolio-summary.md
docs/portfolio/portfolio-summary.json
docs/portfolio/cross-brand-digest.md
docs/portfolio/cross-brand-digest.json
```

The workspace reads local brand project state and summarizes it. Governance is
documentation only; it does not grant real platform permissions or bypass
approval requirements.

## What Phase 11 Adds

Phase 11 adds campaign experiment management:

- A/B test plans
- experiment hypotheses
- variant tracking
- winner recommendations
- experiment history per brand and portfolio

Create an experiment plan:

```bash
scripts/marketing_agency.py create-experiment \
  --project-dir generated-marketing/acme-lidar \
  --name "CTA test" \
  --hypothesis "ROI CTA will create more demo leads than technical CTA" \
  --metric lead_rate \
  --channel LinkedIn \
  --variants "Technical CTA,ROI CTA"
```

Record variant results:

```bash
scripts/marketing_agency.py record-experiment-result \
  --project-dir generated-marketing/acme-lidar \
  --experiment-id "<experiment id>" \
  --variant "ROI CTA" \
  --metrics "impressions=1000,clicks=55,leads=8" \
  --notes "ROI message outperformed technical message"
```

Generate an experiment report:

```bash
scripts/marketing_agency.py experiment-report \
  --project-dir generated-marketing/acme-lidar \
  --experiment-id "<experiment id>" \
  --period "2026-W21"
```

Generate portfolio experiment history:

```bash
scripts/marketing_agency.py portfolio-experiment-history \
  --workspace-dir generated-marketing \
  --period "2026-W21"
```

Phase 11 writes:

```text
docs/experiments/experiment-plans.md
docs/experiments/experiment-plans.json
docs/experiments/experiment-results.md
docs/experiments/experiment-results.json
docs/experiments/experiment-report.md
docs/experiments/experiment-report.json
docs/portfolio/experiment-history.md
docs/portfolio/experiment-history.json
docs/hermes-marketing-state.json
docs/hermes-marketing-workspace.json
```

Experiment reports recommend winners from local metrics only. They do not
publish variants, modify ads, edit production pages, send emails, or change
external campaign settings.

## What Phase 12 Adds

Phase 12 adds budget and ROI planning:

- campaign budget plans
- channel allocation recommendations
- spend/result snapshots
- ROI and CAC summaries
- portfolio budget review

Create a campaign budget plan:

```bash
scripts/marketing_agency.py create-budget-plan \
  --project-dir generated-marketing/acme-lidar \
  --name "Q2 demand budget" \
  --budget 3000 \
  --period "2026-Q2" \
  --channels "LinkedIn,SEO blog,Email"
```

Record spend and results:

```bash
scripts/marketing_agency.py record-spend \
  --project-dir generated-marketing/acme-lidar \
  --plan-id "<budget plan id>" \
  --channel LinkedIn \
  --period "2026-W21" \
  --metrics "spend=1000,revenue=2400,leads=8,conversions=2"
```

Generate a budget report:

```bash
scripts/marketing_agency.py budget-report \
  --project-dir generated-marketing/acme-lidar \
  --plan-id "<budget plan id>" \
  --period "2026-Q2"
```

Generate portfolio budget review:

```bash
scripts/marketing_agency.py portfolio-budget-review \
  --workspace-dir generated-marketing \
  --period "2026-Q2"
```

Phase 12 writes:

```text
docs/budget/budget-plans.md
docs/budget/budget-plans.json
docs/budget/spend-snapshots.md
docs/budget/spend-snapshots.json
docs/budget/budget-report.md
docs/budget/budget-report.json
docs/portfolio/budget-review.md
docs/portfolio/budget-review.json
docs/hermes-marketing-state.json
docs/hermes-marketing-workspace.json
```

Budget reports recommend allocation changes from local metrics only. They do
not change live ad budgets, billing, external campaign settings, or platform
configuration.

## Phase 13 Preview

The next large phase can add CRM pipeline and revenue attribution:

- opportunity stage tracking
- campaign-to-lead attribution
- revenue influence reports
- follow-up SLA review
- portfolio sales pipeline summary
