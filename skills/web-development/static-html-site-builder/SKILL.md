---
name: static-html-site-builder
description: Build, edit, preview, export, and QA static HTML/CSS/JS websites for landing pages, class demos, simple business sites, and portable static hosting.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, html, css, static-site, landing-page, export]
    related_skills: [website-agency-orchestrator, website-design-system, website-qa-deploy, sitelet-cloud-render, hermes-proxy-server]
---

# Static HTML Site Builder

Use this skill for simple landing pages, brochure sites, class demos, and
portable sites that can be hosted anywhere.

## Build Rules

- Use semantic HTML, responsive CSS, and minimal JavaScript.
- Include SEO metadata, Open Graph tags, and accessible alt text.
- Keep assets in predictable folders: `assets/`, `images/`, `css/`, `js/`.
- For one-file demos, inline CSS is acceptable. For multi-page sites, separate
  shared CSS.
- Make navigation and footer consistent across pages.

## Standard Structure

```text
index.html
about.html
services.html
contact.html
assets/
  images/
  css/
  js/
docs/
```

## Implementation Flow

1. Read the brief and design system when present.
2. Create or edit HTML/CSS files.
3. Serve locally with `python3 -m http.server <port>` when preview is needed.
4. Use `hermes-proxy-server` for public preview, or `sitelet-cloud-render` for a
   generated HTML preview.
5. Check mobile layout and links before delivery.

## Contact Forms

Do not fake working backend behavior. Use a clear placeholder or integrate the
chosen provider only when the user supplies details.
