---
name: export-site
description: Export a website as static HTML, a Next.js project, WordPress package/content plan, or Shopify theme-ready assets with clear deployment notes.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, export, handoff, command]
    related_skills: [website-agency-orchestrator, static-html-site-builder, nextjs-site-builder, wordpress-site-builder, shopify-site-builder]
---

# Export Site

Use this skill when the user invokes `/export-site` or asks to export website
files for handoff or deployment.

## Workflow

1. Identify the desired export target: static HTML, Next.js repo, WordPress,
   Shopify theme/assets, or content package.
2. For static HTML or Next.js handoff, use:

   ```bash
   scripts/website_agency.py deploy-prep --project-dir "<project dir>" --target auto
   ```

3. Build or collect the necessary files without unrelated generated clutter.
4. Include environment variable, build, hosting, and upload notes.
5. Run basic validation when practical.
6. Return the export path and any limitations.
