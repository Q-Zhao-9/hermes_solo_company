---
name: website-qa-deploy
description: Run professional website QA and deployment preparation: build, lint, responsive checks, accessibility, SEO, broken links, forms, analytics, preview URLs, GitHub workflow, and deployment steps.
version: 1.1.0
metadata:
  hermes:
    tags: [web-development, qa, deploy, vercel, netlify, github, seo]
    related_skills: [website-agency-orchestrator, hermes-proxy-server, sitelet-cloud-render, wordpress-site-builder, shopify-site-builder, github-pr-workflow]
---

# Website QA Deploy

Use this skill before publishing or when the user asks for build, preview,
deployment, or release readiness.

## QA Checklist

For static HTML and Next.js projects, prefer the deterministic QA helper:

```bash
scripts/website_agency.py qa --project-dir "<project dir>"
```

Add `--run-build` when dependencies are installed and the user wants build
verification:

```bash
scripts/website_agency.py qa --project-dir "<project dir>" --run-build
```

For responsive/source visual checks and optional screenshots, run:

```bash
scripts/website_agency.py visual-qa --project-dir "<project dir>"
```

If Playwright is installed and a preview URL is available:

```bash
scripts/website_agency.py visual-qa --project-dir "<project dir>" --screenshots --url "http://127.0.0.1:3010/"
```

Run what applies to the project:

- install dependencies if needed
- build command
- lint/typecheck/test command
- broken internal links
- responsive layout at mobile and desktop widths
- accessibility: headings, labels, alt text, color contrast, keyboard basics
- SEO: title, meta description, canonical, Open Graph, schema when useful
- forms: action, validation, success/failure behavior
- analytics pixels only when configured by the user
- no secrets in client code or static exports
- platform-specific checks for WordPress and Shopify when applicable

Write findings to:

```text
docs/qa-report.md
docs/visual-qa-report.md
docs/hermes-website-state.json
```

## Preview

- For local apps, use `hermes-proxy-server` to expose a public URL.
- For generated/static HTML, `sitelet-cloud-render` is acceptable.
- Return the public URL and what local target it maps to.

## Deployment Routing

- **Next.js**: prefer Vercel unless the user chooses another host.
- **Static HTML**: Netlify, Vercel static, cPanel, S3, GitHub Pages.
- **WordPress**: staging or production WordPress server after preview approval.
- **Shopify**: theme or app extension workflow; do not modify checkout without
  explicit scope.

## Approval Workflow

For production deployment or WordPress writes, record the approval request and
decision in project state:

```bash
scripts/website_agency.py approval-request --project-dir "<project dir>" --target "<deploy|wordpress-publish>" --reference "<artifact or spec>" --summary "<what the user is approving>"
scripts/website_agency.py approval-record --project-dir "<project dir>" --target "<deploy|wordpress-publish>" --reference "<artifact or spec>" --decision approved
```

Use `revision_requested` when the user asks for changes. Do not proceed with
publish/deploy while the latest matching decision is `revision_requested` or
`rejected`.

## WordPress QA

- preview proposed page/post with `wordpress_preview_publish` before publishing
- verify target site, page/post ID, slug, and status
- check plugin dependencies for forms, SEO, WooCommerce, security, backup
- prefer draft/staging updates before production

## Shopify QA

- use a duplicate/development theme when possible
- check Liquid syntax or theme build tools when available
- verify product variants, add-to-cart flow, price display, image alt text
- do not touch checkout/payment/tax/shipping without explicit approval

## GitHub Workflow

When working in a Git repo:

1. Summarize changed files.
2. Run available checks.
3. Commit only relevant files when the user asks to check in.
4. Do not merge/deploy without approval if production is affected.

## Final Report

Return:

- build/check status
- preview URL
- deployment command or platform steps
- unresolved risks

For Discord-friendly status, use:

```bash
scripts/website_agency.py summary --project-dir "<project dir>"
```
