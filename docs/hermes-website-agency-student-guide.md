# Hermes Website Agency Student Guide

This guide shows the recommended class workflow for the Hermes AI web agency
bot skills.

## Common Flow

Create a site:

```text
/create-site build a professional website for a local dental office
```

Preview and share it:

```text
/build-preview generated-sites/dental-office
```

Ask for edits:

```text
/edit-section make the hero more premium and change the CTA to "Book today"
/change-style make the site feel luxury
```

Run QA:

```text
/seo-optimize homepage
/fix-build generated-sites/dental-office
```

Prepare deployment or export:

```text
/deploy-site generated-sites/dental-office
/export-site generated-sites/dental-office
```

## Helper Commands

Hermes skills may use these deterministic helpers:

```bash
scripts/website_agency.py create-site --name "Acme Dental" --description "Family dental clinic" --platform static --pages home,about,services,contact
scripts/website_agency.py create-site --name "Acme Bistro" --description "Neighborhood restaurant with seasonal menu" --template restaurant
scripts/website_agency.py add-page --project-dir generated-sites/acme-dental --title FAQ --page-type faq --description "Common questions from new patients"
scripts/website_agency.py media-plan --project-dir generated-sites/acme-dental --style "bright clinical"
scripts/website_agency.py media-apply --project-dir generated-sites/acme-dental
scripts/website_agency.py preview-share --project-dir generated-sites/acme-dental --prefer hermesproxy
scripts/website_agency.py list-sections --project-dir generated-sites/acme-dental
scripts/website_agency.py edit-section --project-dir generated-sites/acme-dental --section top --heading "Premium dental care"
scripts/website_agency.py change-style --project-dir generated-sites/acme-dental --preset luxury
scripts/website_agency.py qa --project-dir generated-sites/acme-dental
scripts/website_agency.py visual-qa --project-dir generated-sites/acme-dental
scripts/website_agency.py review-build --project-dir generated-sites/acme-dental --client-name "Acme Team"
scripts/website_agency.py review-comment --project-dir generated-sites/acme-dental --page home --decision revision_requested --comment "Make the hero more premium"
scripts/website_agency.py deploy-prep --project-dir generated-sites/acme-dental --target auto
scripts/website_agency.py deploy-run --project-dir generated-sites/acme-dental --target static-dir --destination /tmp/acme-deploy
scripts/website_agency.py summary --project-dir generated-sites/acme-dental
scripts/website_agency.py wordpress-package --project-dir generated-sites/acme-dental --title "Home" --slug home
scripts/website_agency.py wordpress-preview --project-dir generated-sites/acme-dental --spec dist/hermes-wordpress/home.json
scripts/website_agency.py approval-request --project-dir generated-sites/acme-dental --target wordpress-publish --reference dist/hermes-wordpress/home.json --summary "Approve WordPress Home draft"
scripts/website_agency.py approval-record --project-dir generated-sites/acme-dental --target wordpress-publish --reference dist/hermes-wordpress/home.json --decision approved
scripts/website_agency.py wordpress-publish --project-dir generated-sites/acme-dental --spec dist/hermes-wordpress/home.json
scripts/website_agency.py shopify-package --project-dir generated-sites/acme-store --package-type product-page --title "Acme Travel Kit" --handle travel-kit
```

## Preview Sharing

The main preview path is Hermes proxy:

```text
local website -> local Hermes proxy connector -> cloud hermesproxy -> public URL
```

For static HTML, Sitelet can be used as a fallback if Hermes proxy is not
configured.

## Project History

Generated projects keep workflow history in:

```text
docs/hermes-website-state.json
```

This records:

- project creation
- generated pages and page additions
- media plans, alt text, and asset additions
- preview links
- QA reports
- visual QA reports
- edit/style revisions
- deployment preparation
- WordPress package and preview events
- Shopify theme section/template packages
- approval requests and decisions
- client review dashboard builds and comments

## Client Review Dashboard

Generate a static agency dashboard and a client-facing review page from the
project history:

```bash
scripts/website_agency.py review-build --project-dir generated-sites/acme-dental --public-preview-url https://preview.example/acme --client-name "Acme Team"
```

This writes:

```text
dist/hermes-review/index.html
dist/hermes-review/client-review.html
dist/hermes-review/state.json
```

Use `client-review.html` when sharing the latest preview with a client. Record
their decision or revision notes back into the project state:

```bash
scripts/website_agency.py review-comment --project-dir generated-sites/acme-dental --page home --author "client" --decision revision_requested --comment "Make the hero more premium"
```

## Multi-Page Sites

Generate common site pages during creation:

```bash
scripts/website_agency.py create-site --name "Acme Dental" --description "Family dental clinic" --platform static --pages home,about,services,contact,faq
```

Add a page later and update navigation/history:

```bash
scripts/website_agency.py add-page --project-dir generated-sites/acme-dental --title Pricing --page-type pricing --description "Simple package options" --goal "Request pricing"
```

## Media Assets

Create a page-by-page media plan with accessible alt text and local placeholders:

```bash
scripts/website_agency.py media-plan --project-dir generated-sites/acme-dental --style "bright clinical"
scripts/website_agency.py media-apply --project-dir generated-sites/acme-dental
```

Record a real asset supplied by the user:

```bash
scripts/website_agency.py media-add --project-dir generated-sites/acme-dental --file /path/to/photo.jpg --page home --slot hero --alt-text "Dental team welcoming a family"
```

For WordPress, upload public media URLs through the Hermes MCP WordPress plugin:

```bash
scripts/website_agency.py wordpress-media-upload --project-dir generated-sites/acme-dental --asset-id home-hero
```

## Approval Workflow

Before writing to WordPress or deploying production changes, record the approval
request and final decision:

```bash
scripts/website_agency.py approval-request --project-dir generated-sites/acme-dental --target wordpress-publish --reference dist/hermes-wordpress/home.json --summary "Approve WordPress Home draft"
scripts/website_agency.py approval-record --project-dir generated-sites/acme-dental --target wordpress-publish --reference dist/hermes-wordpress/home.json --decision approved --approver "client"
```

Use `--decision revision_requested` when the user wants changes. The project
state tracks `approval_requested`, `approved_for_publish`,
`revision_requested`, and `published`.

## WordPress

Prepare a generated site/page for WordPress:

```bash
scripts/website_agency.py wordpress-package --project-dir generated-sites/acme-dental --title "Home" --slug home --status draft
```

Preview it through Sitelet before publishing:

```bash
scripts/website_agency.py wordpress-preview --project-dir generated-sites/acme-dental --spec dist/hermes-wordpress/home.json
```

After the preview is approved, publish or update the WordPress page through the
Hermes MCP WordPress plugin:

```bash
export WORDPRESS_MCP_URL="https://example.com/wp-json/hermes-mcp/v1/mcp"
export WORDPRESS_MCP_TOKEN="your-plugin-token"
scripts/website_agency.py wordpress-publish --project-dir generated-sites/acme-dental --spec dist/hermes-wordpress/home.json
```

This creates Gutenberg-style content in `dist/hermes-wordpress/`, records the
event in `docs/hermes-website-state.json`, and requires a recorded approval or
the explicit `--approved` override before writing to WordPress.

## Shopify

Prepare a Shopify theme package from a generated ecommerce site:

```bash
scripts/website_agency.py create-site --name "Acme Goods" --description "Ecommerce store for curated travel accessories" --template ecommerce --pages home,about,contact
scripts/website_agency.py shopify-package --project-dir generated-sites/acme-goods --package-type product-page --title "Acme Travel Kit" --handle travel-kit --theme-name "Hermes Duplicate"
```

This writes:

```text
dist/hermes-shopify/theme/sections/hermes-<handle>.liquid
dist/hermes-shopify/theme/templates/page.<handle>.json
dist/hermes-shopify/theme/assets/hermes-<handle>.css
dist/hermes-shopify/theme/snippets/hermes-trust-badges.liquid
dist/hermes-shopify/preview.html
dist/hermes-shopify/shopify-package.json
dist/hermes-shopify/<handle>-shopify-theme.zip
```

Install Shopify packages only on a duplicate/development theme first. Do not
change checkout, payment, taxes, shipping, or live theme settings without clear
approval.

## Templates

The generator supports these first-draft templates:

- `local-service`
- `restaurant`
- `saas`
- `consultant`
- `ecommerce`
- `portfolio`

Use `--template auto` to infer the template from the business description, or
pass an explicit template:

```bash
scripts/website_agency.py create-site --name "Acme Bistro" --description "Neighborhood restaurant with seasonal menu" --template restaurant
```

## Discord Summary

Use the summary helper when you want a compact response to paste or send back
to Discord:

```bash
scripts/website_agency.py summary --project-dir generated-sites/acme-dental
```

It includes the latest preview URL, QA result, visual QA result, latest edit,
and deployment artifact when available.

## Visual QA

Run source-based responsive checks:

```bash
scripts/website_agency.py visual-qa --project-dir generated-sites/acme-dental
```

If Playwright is installed and the local preview is running, screenshots can be
captured:

```bash
scripts/website_agency.py visual-qa --project-dir generated-sites/acme-dental --screenshots --url http://127.0.0.1:3010/
```

## Deployment

`deploy-prep` does not publish production changes by itself. It prepares
deployment artifacts and notes:

- static HTML: `dist/hermes-deploy/static-site.zip`
- Vercel/Netlify: settings and command notes
- GitHub Pages: static package and setup notes

`deploy-run` creates an executable deployment plan by default:

```bash
scripts/website_agency.py deploy-run --project-dir generated-sites/acme-dental --target static-dir --destination /tmp/acme-deploy
```

After approval, execute the deployment:

```bash
scripts/website_agency.py approval-record --project-dir generated-sites/acme-dental --target deploy --reference deploy-static-dir --decision approved
scripts/website_agency.py deploy-run --project-dir generated-sites/acme-dental --target static-dir --destination /tmp/acme-deploy --execute
```

Supported run targets are `static-dir`, `github-pages`, `vercel`, and
`netlify`. Production deployment still requires user approval and the correct
account or hosting credentials.
