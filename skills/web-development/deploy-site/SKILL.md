---
name: deploy-site
description: Prepare or perform website deployment for static HTML, Next.js, WordPress, or Shopify with environment variables, build settings, preview approval, and rollback notes.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, deploy, qa, command]
    related_skills: [website-qa-deploy, nextjs-site-builder, wordpress-site-builder, shopify-site-builder, static-html-site-builder]
---

# Deploy Site

Use this skill when the user invokes `/deploy-site` or asks to deploy a website.

## Workflow

1. Use `website-qa-deploy` as the primary skill.
2. For static HTML and Next.js projects, prepare deterministic deployment
   artifacts with:

   ```bash
   scripts/website_agency.py deploy-prep --project-dir "<project dir>" --target auto
   ```

   Supported targets: `static-zip`, `vercel`, `netlify`, `github-pages`.
   This writes deployment notes under `dist/hermes-deploy/` and records history
   in `docs/hermes-website-state.json`.
3. Confirm target platform and credentials before making any external change.
4. Run the relevant build, QA, and preview checks first.
5. Provide exact deployment commands/settings when credentials or billing are not
   available.
6. For WordPress and Shopify, prefer draft, staging, duplicate theme, or preview
   workflows before publishing live changes.

Do not publish to production without clear user approval.
