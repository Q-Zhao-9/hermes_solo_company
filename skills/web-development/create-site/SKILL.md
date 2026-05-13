---
name: create-site
description: Start the professional website agency workflow from a business description and produce a brief, sitemap, design system, implementation plan, preview, and QA path.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, website-builder, agency, command]
    related_skills: [website-agency-orchestrator, website-brief-generator, website-design-system, website-seo-content]
---

# Create Site

Use this skill when the user invokes `/create-site` or asks Hermes to create a
new website from a business idea.

## Workflow

1. Use `website-agency-orchestrator` as the primary workflow.
2. Gather or infer the business type, target audience, conversion goal, pages,
   platform preference, brand tone, and required integrations.
3. Produce the website brief, sitemap, design system, and content plan before
   coding unless the user explicitly asks for a quick prototype.
4. Route implementation to `nextjs-site-builder`, `static-html-site-builder`,
   `wordpress-site-builder`, or `shopify-site-builder`.
5. Build, preview, QA, and summarize changed files or project path.

Default to a professional Next.js site for custom business/product websites,
static HTML for a quick class/demo landing page, WordPress for editable content
sites, and Shopify for ecommerce.
