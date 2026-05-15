---
name: marketing-agency-orchestrator
description: Run a professional AI solo company marketing agency workflow: strategy, campaign planning, content pipeline, SEO/GEO, social channels, lead detection, competitor intelligence, analytics, and approval-safe execution.
version: 1.0.0
metadata:
  hermes:
    tags: [marketing, seo, social-media, growth, campaigns, ai-solo-company]
    category: marketing
    related_skills: [marketing-strategy, create-campaign, social-calendar, content-studio, seo-geo-growth, lead-detection, marketing-analytics, competitor-intelligence, campaign-execution, platform-integration-handoff, monitoring-automation, website-agency-orchestrator, website-seo-content, seo-optimize, xurl, youtube-content, himalaya]
---

# Marketing Agency Orchestrator

Use this skill when the user wants Hermes to act as a marketing agency, growth
team, SEO strategist, social media manager, content studio, lead detection
assistant, CRM follow-up assistant, or competitor intelligence analyst.

Treat this as an AI marketing operating system, not a random post generator.

## Workflow

Use this sequence unless the user explicitly asks for a small one-off task:

```text
business goal -> strategy -> campaign -> content plan -> channel adaptation -> review -> approved execution -> analytics loop
```

Phase 1 supports strategy and campaign memory through:

```bash
scripts/marketing_agency.py create-strategy --brand "<brand>" --business "<business>" --audience "<ICP>" --goal "<goal>" --offer "<offer>"
scripts/marketing_agency.py create-campaign --project-dir "<project dir>" --name "<campaign>" --objective "<objective>"
scripts/marketing_agency.py summary --project-dir "<project dir>"
```

Phase 2 supports content calendars and review-ready drafts:

```bash
scripts/marketing_agency.py generate-content-plan --project-dir "<project dir>" --weeks 4 --cadence 3
scripts/marketing_agency.py generate-posts --project-dir "<project dir>" --channels "LinkedIn,X,SEO blog,Email"
```

Phase 3 supports SEO/GEO planning and blog briefs:

```bash
scripts/marketing_agency.py generate-seo-plan --project-dir "<project dir>" --focus "<offer>" --pages 6
scripts/marketing_agency.py generate-blog-briefs --project-dir "<project dir>" --count 4
```

Phase 4 supports lead detection and CRM handoff artifacts:

```bash
scripts/marketing_agency.py define-lead-signals --project-dir "<project dir>"
scripts/marketing_agency.py score-lead --project-dir "<project dir>" --name "<lead>" --company "<company>" --text "<lead text>"
scripts/marketing_agency.py draft-outreach --project-dir "<project dir>" --channel email
scripts/marketing_agency.py crm-export --project-dir "<project dir>" --format json
```

Phase 5 supports analytics snapshots and manager review dashboards:

```bash
scripts/marketing_agency.py record-performance --project-dir "<project dir>" --channel LinkedIn --metrics "impressions=1000,engagements=80,clicks=35,leads=4"
scripts/marketing_agency.py generate-review-dashboard --project-dir "<project dir>" --period "<period>"
```

Phase 6 supports competitor intelligence:

```bash
scripts/marketing_agency.py add-competitor --project-dir "<project dir>" --name "<competitor>" --positioning "<positioning>"
scripts/marketing_agency.py track-competitor --project-dir "<project dir>" --competitor "<competitor>" --summary "<market move>"
scripts/marketing_agency.py competitor-report --project-dir "<project dir>" --period "<period>"
```

Phase 7 supports approval and execution handoff:

```bash
scripts/marketing_agency.py create-approval-package --project-dir "<project dir>" --channels "LinkedIn,Email,SEO blog"
scripts/marketing_agency.py record-approval --project-dir "<project dir>" --decision approved --approver "<name>"
scripts/marketing_agency.py operator-handoff --project-dir "<project dir>" --operator "<team>"
```

Phase 8 supports platform integration handoff and evidence capture:

```bash
scripts/marketing_agency.py prepare-integration-handoff --project-dir "<project dir>" --platform social --provider LinkedIn
scripts/marketing_agency.py capture-execution-evidence --project-dir "<project dir>" --item-id "<item>" --platform LinkedIn --status published --url "<url>"
```

Phase 9 supports monitoring automation handoffs, alert capture, and weekly
digests:

```bash
scripts/marketing_agency.py create-monitor-query --project-dir "<project dir>" --name "<watch name>" --type lead --query "<saved query>"
scripts/marketing_agency.py schedule-monitor --project-dir "<project dir>" --cadence weekly --owner "<owner>"
scripts/marketing_agency.py record-monitor-alert --project-dir "<project dir>" --title "<alert>" --summary "<summary>" --severity high
scripts/marketing_agency.py weekly-digest --project-dir "<project dir>" --period "<period>"
```

## Routing

- **Strategy**: use `marketing-strategy` and `create-strategy`.
- **Campaign planning**: use `create-campaign`.
- **Content calendar**: use `social-calendar` and `generate-content-plan`.
- **Content drafts**: use `content-studio` and `generate-posts`.
- **SEO/GEO**: use `seo-geo-growth`, `generate-seo-plan`, and
  `generate-blog-briefs`.
- **Lead detection and CRM handoff**: use `lead-detection`,
  `define-lead-signals`, `score-lead`, `draft-outreach`, and `crm-export`.
- **Analytics and review dashboards**: use `marketing-analytics`,
  `record-performance`, and `generate-review-dashboard`.
- **Competitor intelligence**: use `competitor-intelligence`,
  `add-competitor`, `track-competitor`, and `competitor-report`.
- **Approval and execution handoff**: use `campaign-execution`,
  `create-approval-package`, `record-approval`, and `operator-handoff`.
- **Platform handoff and execution evidence**: use
  `platform-integration-handoff`, `prepare-integration-handoff`, and
  `capture-execution-evidence`.
- **Monitoring automation and digests**: use `monitoring-automation`,
  `create-monitor-query`, `schedule-monitor`, `record-monitor-alert`, and
  `weekly-digest`.
- **Website or landing page changes**: use `website-agency-orchestrator`.
- **SEO and GEO**: use `website-seo-content` and `seo-optimize` for website
  work; use future marketing SEO commands for campaign-level SEO.
- **X/Twitter**: use `xurl` only after content is approved.
- **YouTube**: use `youtube-content` for video scripts, metadata, and channel
  planning.
- **Email**: use email skills only after approval to send or manage real mail.

## Required Inputs

Infer reasonable defaults when possible, but collect these if missing:

- brand or company name
- business/product description
- ideal customer profile
- primary marketing goal
- core offer
- target region
- brand tone

## Approval Rules

Draft by default. Do not publish social posts, send emails, reply to DMs, run
ads, update CRM records, or modify live website/Shopify/WordPress production
content without explicit user approval.

## Response Pattern

For strategy/campaign work, return:

- project directory
- strategy or campaign artifact path
- target audience
- channels
- next recommended step

Keep Discord responses concise and include the `summary` output when useful.
