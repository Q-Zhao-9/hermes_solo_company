---
name: website-qa-deploy
description: Run professional website QA and deployment preparation: build, lint, responsive checks, accessibility, SEO, broken links, forms, analytics, preview URLs, GitHub workflow, and deployment steps.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, qa, deploy, vercel, netlify, github, seo]
    related_skills: [website-agency-orchestrator, hermes-proxy-server, sitelet-cloud-render, github-pr-workflow]
---

# Website QA Deploy

Use this skill before publishing or when the user asks for build, preview,
deployment, or release readiness.

## QA Checklist

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

Write findings to:

```text
docs/qa-report.md
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
