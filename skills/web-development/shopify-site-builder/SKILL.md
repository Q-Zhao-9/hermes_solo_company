---
name: shopify-site-builder
description: Plan, edit, preview, and QA Shopify storefront work including theme customization, Liquid sections, product and collection pages, SEO copy, app extension guidance, and Hydrogen storefront planning.
version: 1.1.0
metadata:
  hermes:
    tags: [web-development, shopify, ecommerce, liquid, hydrogen, product-pages, seo]
    related_skills: [website-agency-orchestrator, website-brief-generator, website-design-system, website-seo-content, website-qa-deploy]
---

# Shopify Site Builder

Use this skill for ecommerce sites, product pages, collection pages, Shopify
theme customization, Liquid sections, app extension planning, and Hydrogen
headless storefronts.

## Safety Rule

Shopify work can affect revenue and checkout. Do not modify checkout, payment,
tax, shipping, or production theme code without explicit user approval. Prefer a
duplicate theme, development theme, or staging branch.

## Shopify Routing

- **Theme customization**: Liquid templates, JSON templates, sections, snippets,
  assets.
- **Product/collection optimization**: product copy, SEO, media, trust badges,
  reviews, comparison, FAQ.
- **App extensions**: recommend theme app extensions for dynamic blocks that
  should not require merchants to edit Liquid manually.
- **Hydrogen**: use for custom headless storefronts, advanced UX, or custom
  React commerce flows.

## Intake

Collect:

- store URL and theme name
- target products or collections
- conversion goal
- brand references
- available product images/media
- app dependencies
- theme access/deployment workflow

## Theme Editing Workflow

1. Identify the theme files or local theme repo.
2. Read before editing:
   - `templates/*.json`
   - `sections/*.liquid`
   - `snippets/*.liquid`
   - `assets/*`
3. Make isolated changes in a section/snippet when possible.
4. Keep Liquid schema valid.
5. Avoid hard-coded merchant content when a theme setting is better.
6. Preview on a development theme or local theme server when available.
7. Summarize changed files and merchant-editable settings.

For generated Hermes website projects, prepare the Shopify package with:

```bash
scripts/website_agency.py shopify-package --project-dir "<project dir>" --package-type product-page --title "<product or page title>" --handle "<shopify-handle>"
```

This creates a safe handoff under `dist/hermes-shopify/`:

- Liquid section
- JSON page template
- CSS asset
- trust snippet
- local `preview.html`
- install notes
- zipped theme file package

Install the files into a duplicate/development theme first, then collect review
approval before publishing.

## Product Page Optimization

Include:

- benefit-led product title/subtitle
- product description
- feature bullets
- social proof/reviews area
- delivery/returns trust copy
- FAQ
- SEO title/meta
- product schema recommendation
- image alt text

## Hydrogen Workflow

Use Hydrogen only when the user wants a custom headless storefront. Plan:

- routes
- product/collection data requirements
- cart/checkout handoff
- caching strategy
- deployment target

Do not promise checkout customization beyond Shopify platform constraints.

## QA

Check:

- mobile product page flow
- add-to-cart path
- price/variant display
- collection filters
- image sizes and alt text
- SEO metadata
- Liquid syntax/build where tools are available
