---
name: marketing-strategy
description: Create professional marketing strategy for AI solo company clients: ICP, positioning, channels, funnel, content themes, brand voice, SEO/GEO focus, and campaign direction.
version: 1.0.0
metadata:
  hermes:
    tags: [marketing, strategy, icp, positioning, funnel, campaigns, seo, geo]
    category: marketing
    related_skills: [marketing-agency-orchestrator, website-brief-generator, website-seo-content]
---

# Marketing Strategy

Use this skill when the user needs strategic marketing planning before content,
posting, SEO, ads, or lead generation.

Do not start with posts. Start with market logic:

```text
ICP -> pain points -> offer -> positioning -> channels -> funnel -> campaign themes
```

## Phase 1 Helper

Create a strategy project and persistent marketing state:

```bash
scripts/marketing_agency.py create-strategy \
  --brand "<brand>" \
  --business "<business/product>" \
  --audience "<ideal customer profile>" \
  --goal "<primary marketing goal>" \
  --offer "<core offer>" \
  --tone "<brand tone>" \
  --region "<target market>"
```

Create the first campaign:

```bash
scripts/marketing_agency.py create-campaign \
  --project-dir "<project dir>" \
  --name "<campaign name>" \
  --objective "<business objective>" \
  --duration "4 weeks" \
  --cta "<call to action>"
```

## Strategy Quality Bar

A useful strategy must include:

- target ICP and industries
- pain points and buying triggers
- positioning statement
- priority channels
- funnel stages
- campaign/content themes
- brand voice rules
- SEO and AI answer engine focus

For B2B or industrial clients, prioritize LinkedIn, SEO, YouTube demos,
industry forums, distributor/channel partner outreach, and email nurture.

For ecommerce clients, prioritize Instagram, TikTok, Shopify blog, email,
influencer outreach, product education, buying guides, and social proof.

For local businesses, prioritize Google Business Profile, local SEO, reviews,
Instagram/Facebook, and appointment/quote CTAs.
