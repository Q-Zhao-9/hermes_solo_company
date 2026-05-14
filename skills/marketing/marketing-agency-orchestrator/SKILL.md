---
name: marketing-agency-orchestrator
description: Run a professional AI solo company marketing agency workflow: strategy, campaign planning, content pipeline, SEO/GEO, social channels, lead detection, competitor intelligence, analytics, and approval-safe execution.
version: 1.0.0
metadata:
  hermes:
    tags: [marketing, seo, social-media, growth, campaigns, ai-solo-company]
    category: marketing
    related_skills: [marketing-strategy, website-agency-orchestrator, website-seo-content, seo-optimize, xurl, youtube-content, himalaya]
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

## Routing

- **Strategy**: use `marketing-strategy` and `create-strategy`.
- **Campaign planning**: use `create-campaign`.
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
