---
name: make-landing-page
description: Create a focused one-page landing page with positioning, sections, conversion copy, SEO metadata, implementation, preview, and QA.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, landing-page, website-builder, command]
    related_skills: [website-agency-orchestrator, static-html-site-builder, nextjs-site-builder, website-seo-content]
---

# Make Landing Page

Use this skill when the user invokes `/make-landing-page` or asks for a one-page
marketing site.

## Workflow

1. Identify the offer, target customer, primary CTA, credibility proof, and
   contact or lead-capture requirement.
2. For a fast static or Next.js first draft, use:

   ```bash
   scripts/website_agency.py create-site --name "<offer/site name>" --description "<landing page offer>" --audience "<target customer>" --goal "<CTA>" --platform static --template auto
   ```

3. Use `website-agency-orchestrator` for structure and platform routing.
4. Use `website-seo-content` for headline, sections, FAQ, metadata, and schema.
5. Implement with `static-html-site-builder` for simple exportable pages or
   `nextjs-site-builder` when the project is already React/Next.js.
6. Run available checks and provide a preview URL when requested.

Prefer a complete usable landing page over placeholder content.
