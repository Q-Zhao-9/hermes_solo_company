---
name: add-page
description: Add a new website page such as service, product, about, contact, blog, FAQ, pricing, WordPress page, or Shopify page while preserving the existing design system.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, website-editing, page-builder, command]
    related_skills: [website-agency-orchestrator, website-seo-content, nextjs-site-builder, wordpress-site-builder, shopify-site-builder]
---

# Add Page

Use this skill when the user invokes `/add-page` or asks to add a website page.

## Workflow

1. Inspect the existing project, routes, content model, and style conventions.
2. Clarify the page type and target CTA only if missing.
3. Use `website-seo-content` for page title, meta description, headings, FAQ,
   and schema where useful.
4. For generated static/Next.js agency projects, prefer the deterministic helper:

   ```bash
   scripts/website_agency.py add-page --project-dir "<project dir>" --title "<Page title>" --page-type "<about|services|contact|faq|pricing|blog>" --description "<page purpose>" --goal "<CTA>"
   ```

   This creates the page, updates navigation, and records page history in
   `docs/hermes-website-state.json`.
5. Implement through the platform skill when the helper is not enough:
   - `nextjs-site-builder` for Next.js routes and components.
   - `static-html-site-builder` for standalone pages.
   - `wordpress-site-builder` for WordPress draft/page workflows.
   - `shopify-site-builder` for Shopify theme pages/templates.
6. Update navigation and internal links when appropriate.
7. Run available build or validation checks.
