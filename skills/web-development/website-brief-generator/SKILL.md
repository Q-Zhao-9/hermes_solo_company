---
name: website-brief-generator
description: Convert a business idea or existing website request into a professional website brief with audience, positioning, sitemap, conversion goals, SEO keywords, page requirements, and implementation assumptions.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, website-brief, strategy, sitemap, planning]
    related_skills: [website-agency-orchestrator, website-seo-content]
---

# Website Brief Generator

Use this skill before coding a new website or major redesign.

## Output Artifact

Create or update:

```text
docs/website-brief.md
```

## Brief Structure

Include these sections:

```markdown
# Website Brief

## Business Summary
## Target Audience
## Brand Positioning
## Primary Conversion Goal
## Secondary Goals
## Competitors Or References
## Sitemap
## Page Requirements
## SEO Keywords
## Tone And Messaging
## Functional Requirements
## Platform Recommendation
## Assumptions And Open Questions
```

## Sitemap Rules

For landing pages, define sections:

```text
nav, hero, value props, services/features, proof, process, pricing/offer, FAQ, CTA, footer
```

For multi-page sites, define page routes:

```text
/, /about, /services, /services/<service>, /case-studies, /blog, /contact
```

## Question Policy

Ask only for missing information that changes the result materially. Good
questions:

- What is the main conversion goal?
- Who is the target customer?
- Do you prefer static HTML, Next.js, WordPress, or Shopify?
- Any brand references or competitors?

If the user is in a hurry, infer defaults and mark them as assumptions.
