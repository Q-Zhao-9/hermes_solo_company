---
name: seo-optimize
description: Improve website SEO with keyword intent, page titles, meta descriptions, headings, schema, internal links, image alt text, and content quality.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, seo, content, command]
    related_skills: [website-seo-content, website-agency-orchestrator, website-qa-deploy]
---

# SEO Optimize

Use this skill when the user invokes `/seo-optimize` or asks to improve SEO for
a website or page.

## Workflow

1. Use `website-seo-content` as the primary skill.
2. Identify the page purpose, audience, location if relevant, keyword intent,
   and conversion goal.
3. Update title, meta description, headings, body copy, FAQ, schema, alt text,
   and internal links as appropriate for the platform.
4. Preserve natural language quality; do not keyword-stuff.
5. Run the website QA helper when working on static HTML or Next.js:

   ```bash
   scripts/website_agency.py qa --project-dir "<project dir>"
   ```

6. Summarize the SEO changes and any remaining QA warnings.
