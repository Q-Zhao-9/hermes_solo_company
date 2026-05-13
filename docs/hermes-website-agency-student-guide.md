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
scripts/website_agency.py create-site --name "Acme Dental" --description "Family dental clinic" --platform static
scripts/website_agency.py create-site --name "Acme Bistro" --description "Neighborhood restaurant with seasonal menu" --template restaurant
scripts/website_agency.py preview-share --project-dir generated-sites/acme-dental --prefer hermesproxy
scripts/website_agency.py list-sections --project-dir generated-sites/acme-dental
scripts/website_agency.py edit-section --project-dir generated-sites/acme-dental --section top --heading "Premium dental care"
scripts/website_agency.py change-style --project-dir generated-sites/acme-dental --preset luxury
scripts/website_agency.py qa --project-dir generated-sites/acme-dental
scripts/website_agency.py visual-qa --project-dir generated-sites/acme-dental
scripts/website_agency.py deploy-prep --project-dir generated-sites/acme-dental --target auto
scripts/website_agency.py summary --project-dir generated-sites/acme-dental
scripts/website_agency.py wordpress-package --project-dir generated-sites/acme-dental --title "Home" --slug home
scripts/website_agency.py wordpress-preview --project-dir generated-sites/acme-dental --spec dist/hermes-wordpress/home.json
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
- preview links
- QA reports
- visual QA reports
- edit/style revisions
- deployment preparation
- WordPress package and preview events

## WordPress

Prepare a generated site/page for WordPress:

```bash
scripts/website_agency.py wordpress-package --project-dir generated-sites/acme-dental --title "Home" --slug home --status draft
```

Preview it through Sitelet before publishing:

```bash
scripts/website_agency.py wordpress-preview --project-dir generated-sites/acme-dental --spec dist/hermes-wordpress/home.json
```

This creates Gutenberg-style content in `dist/hermes-wordpress/`, records the
event in `docs/hermes-website-state.json`, and keeps production publishing as a
separate approval step.

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

## Deployment Prep

`deploy-prep` does not publish production changes by itself. It prepares
deployment artifacts and notes:

- static HTML: `dist/hermes-deploy/static-site.zip`
- Vercel/Netlify: settings and command notes
- GitHub Pages: static package and setup notes

Production deployment still requires user approval and the correct account or
hosting credentials.
