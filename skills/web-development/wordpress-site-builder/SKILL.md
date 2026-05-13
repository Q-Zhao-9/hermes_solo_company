---
name: wordpress-site-builder
description: Plan, create, preview, edit, QA, and publish WordPress business websites using pages, posts, block themes, plugins, WooCommerce, MCP tools, and Sitelet pre-deploy previews.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, wordpress, gutenberg, block-theme, woocommerce, mcp, sitelet]
    related_skills: [website-agency-orchestrator, website-brief-generator, website-design-system, website-seo-content, sitelet-cloud-render, multi-site-manager]
---

# WordPress Site Builder

Use this skill for business sites, content-heavy sites, blogs, service pages,
editable marketing pages, and WooCommerce storefronts.

## Operating Rule

Never publish directly when preview is possible. Generate a Sitelet preview for
proposed page/post edits first, get user approval, then update WordPress through
the configured WordPress MCP tools or deployment workflow.

## WordPress Planning

For each site, identify:

- site name and production/staging URL
- WordPress MCP server name if available
- theme or block theme
- required pages and posts
- plugins needed: SEO, security, backup, forms, WooCommerce, analytics
- content ownership: generated draft, user-supplied copy, imported content
- publish target: draft, staging, or production

Use `multi-site-manager` when more than one WordPress site exists.

## Build Workflow

1. Use `website-brief-generator` and `website-design-system`.
2. For static/Next.js generated projects, create a WordPress-ready package:

   ```bash
   scripts/website_agency.py wordpress-package --project-dir "<project dir>" --title "<page title>" --slug "<page-slug>" --status draft
   ```

3. Preview the package through Sitelet:

   ```bash
   scripts/website_agency.py wordpress-preview --project-dir "<project dir>" --spec "dist/hermes-wordpress/<page-slug>.json"
   ```

4. Create page/post specs:
   - title
   - slug
   - SEO title/meta
   - Gutenberg/block HTML or clean semantic HTML
   - CTA and internal links
5. Call `wordpress_preview_publish` for pre-deploy preview when content is ready.
6. Share the Sitelet preview URL.
7. After user approval, use the WordPress MCP tools to create/update content.
8. Prefer `draft` or `pending` status unless the user explicitly says publish.
9. Report page ID, status, edit URL/public URL, and preview URL.

## WordPress MCP Pattern

When an MCP site is configured:

1. Resolve active site from `multi-site-manager`.
2. Confirm the MCP tools exist for that site.
3. Read before writing:
   - list pages/posts
   - fetch current page/post
4. Apply minimal changes.
5. Save as draft/staging when possible.

## WooCommerce

For ecommerce requests:

- collect product catalog fields
- product/page SEO
- collections/categories
- shipping/payment assumptions
- trust and return policy content
- product schema suggestions

Do not configure payment gateways, taxes, or checkout-sensitive settings without
explicit user approval.

## QA

Before publish:

- preview page visually
- check mobile readability
- check links and CTAs
- check SEO title/meta/H1
- confirm form/plugin dependencies
- confirm target site and status
