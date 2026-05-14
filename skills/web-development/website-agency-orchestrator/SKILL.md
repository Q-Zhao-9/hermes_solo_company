---
name: website-agency-orchestrator
description: Run a professional AI web agency workflow for creating or improving websites: intake, brief, sitemap, design system, platform routing, Codex implementation, preview, QA, revisions, and deployment.
version: 1.1.0
metadata:
  hermes:
    tags: [web-development, website-builder, agency, codex, planning, preview]
    related_skills: [website-brief-generator, website-design-system, website-seo-content, nextjs-site-builder, static-html-site-builder, wordpress-site-builder, shopify-site-builder, website-visual-editor, website-qa-deploy, hermes-proxy-server, sitelet-cloud-render, multi-site-manager]
---

# Website Agency Orchestrator

Use this skill when the user wants Hermes to create, redesign, edit, preview,
QA, or deploy a professional website. Treat Hermes as an AI web agency, not an
HTML snippet generator.

## Production Workflow

Follow this sequence unless the user explicitly asks for a quick patch:

```text
brief -> sitemap -> design system -> content -> code -> QA -> preview -> client review -> revise -> deploy
```

Keep artifacts in the project when practical:

```text
docs/website-brief.md
docs/sitemap.md
docs/design-system.md
docs/content-plan.md
docs/qa-report.md
```

## Intake Policy

Ask at most 3-6 questions when essential information is missing. Otherwise infer
reasonable defaults and state assumptions briefly.

Minimum inputs:

- business or product type
- target audience
- primary conversion goal
- pages or sections needed
- platform preference if any
- brand tone or design reference

## Platform Routing

- **Static HTML**: simple landing pages, class demos, exportable brochure sites.
- **Next.js**: SaaS, AI products, dashboards, portals, auth, database/API needs.
- **WordPress**: content-heavy business sites, blogs, editable marketing pages.
- **Shopify**: ecommerce storefronts, product pages, collections, theme work.

Default to:

- Static HTML for quick landing pages.
- Next.js for custom professional product sites.
- WordPress when the user needs business-owner editing, blogs, content volume,
  plugins, or WooCommerce.
- Shopify when the core job is ecommerce/storefront conversion.

## Build Workflow

1. Use `website-brief-generator` to create the professional requirement brief.
2. Use `website-design-system` to define visual rules.
3. Use `website-seo-content` for content, metadata, CTAs, FAQ, and schema.
4. Route implementation to the selected platform skill:
   - `nextjs-site-builder`
   - `static-html-site-builder`
   - `wordpress-site-builder`
   - `shopify-site-builder`
5. Use Codex-style file edits in the selected project directory.
6. Run build/lint/tests when available.
7. Use `hermes-proxy-server` for local live preview or `sitelet-cloud-render`
   for uploaded HTML previews.
8. Generate the client review dashboard before approval conversations.
9. Use `website-qa-deploy` before publishing.

## Bot Commands To Recognize

Map these user intents to the workflow:

- `/create-site`: full website from business description.
- `/make-landing-page`: one-page site.
- `/add-page`: add service/product/about/contact/blog page.
- `/edit-section`: modify one section by natural language.
- `/change-style`: change brand feeling, color, typography, layout.
- `/seo-optimize`: improve metadata, headings, schema, internal links.
- `/build-preview`: build and expose preview URL.
- `/fix-build`: diagnose and fix build errors.
- `/deploy`: deploy or provide exact deployment steps.
- `/export`: export HTML, Next.js repo, WordPress package, or Shopify theme.
- `/setup-wordpress`: plan or build a WordPress site/page workflow.
- `/setup-shopify`: plan or edit a Shopify storefront/theme workflow.

## Response Pattern

For new sites, summarize:

```text
Plan:
1. Brief and sitemap
2. Design system
3. Build <platform>
4. QA and preview
```

For multi-page generated projects, use:

```bash
scripts/website_agency.py create-site --name "<site>" --description "<business>" --pages home,about,services,contact
scripts/website_agency.py add-page --project-dir "<project dir>" --title FAQ --page-type faq --description "<page purpose>"
scripts/website_agency.py review-build --project-dir "<project dir>" --public-preview-url "<preview url>"
scripts/website_agency.py review-comment --project-dir "<project dir>" --page home --decision revision_requested --comment "<client feedback>"
scripts/website_agency.py shopify-package --project-dir "<project dir>" --package-type product-page --title "<product title>" --handle "<handle>"
```

After implementation, return:

- changed files or project path
- build result
- public preview URL
- review dashboard path when client review is part of the task
- remaining risks or deployment next step

Do not overwhelm the user with every internal detail.
