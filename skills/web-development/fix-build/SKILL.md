---
name: fix-build
description: Diagnose and fix website build, lint, runtime, dependency, route, hydration, WordPress preview, Shopify theme, or deployment errors.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, qa, build-fix, command]
    related_skills: [website-qa-deploy, nextjs-site-builder, wordpress-site-builder, shopify-site-builder]
---

# Fix Build

Use this skill when the user invokes `/fix-build` or asks Hermes to repair a
website build or preview failure.

## Workflow

1. Start with the deterministic QA helper when the project is static HTML or
   Next.js:

   ```bash
   scripts/website_agency.py qa --project-dir "<project dir>" --run-build
   ```

2. Reproduce the failure with the existing project command when feasible.
3. Read the first real error and the related source file before editing.
4. Apply the smallest correct fix that matches the project conventions.
5. Re-run the failing command or a narrower equivalent.
6. Summarize the cause, changed files, and verification result.

Do not hide unresolved warnings that affect preview, publish, SEO, forms, auth,
payments, or data integrity.
