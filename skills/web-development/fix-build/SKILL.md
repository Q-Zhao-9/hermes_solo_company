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

1. Reproduce the failure with the existing project command when feasible.
2. Read the first real error and the related source file before editing.
3. Apply the smallest correct fix that matches the project conventions.
4. Re-run the failing command or a narrower equivalent.
5. Summarize the cause, changed files, and verification result.

Do not hide unresolved warnings that affect preview, publish, SEO, forms, auth,
payments, or data integrity.
