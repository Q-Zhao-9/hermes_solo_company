---
name: nextjs-site-builder
description: Build, edit, preview, QA, and prepare deployment for professional Next.js websites using real project files, App Router conventions, reusable components, and Codex execution.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, nextjs, react, codex, app-router, vercel]
    related_skills: [website-agency-orchestrator, website-design-system, website-qa-deploy, hermes-proxy-server]
---

# Next.js Site Builder

Use this skill for professional SaaS, AI product, dashboard, portal, and
high-performance custom websites.

## Build Rules

- Inspect the existing project before editing.
- Prefer the repo's existing package manager and component style.
- Use App Router conventions when creating new Next.js apps.
- Create reusable components for nav, hero, cards, pricing, FAQ, forms, footer.
- Keep pages responsive and accessible from the first implementation.
- Avoid landing-page filler. Build the actual requested website.

## Standard Structure

For new App Router projects:

```text
app/
  layout.tsx
  page.tsx
  globals.css
components/
  site-header.tsx
  site-footer.tsx
  sections/
lib/
public/
docs/
```

## Implementation Flow

1. Read `docs/website-brief.md` and `docs/design-system.md` when present.
2. Inspect `package.json`, `app/`, `components/`, `public/`.
3. Implement pages and components.
4. Add metadata for SEO.
5. Run `npm run build` or the repo's build command.
6. Start local server if preview is requested.
7. Use `hermes-proxy-server` to expose the preview publicly.

## Deployment

Default recommendation: Vercel for Next.js. Provide exact environment variables,
build command, output settings, and domain steps. Do not deploy without user
approval when credentials or billing are involved.
