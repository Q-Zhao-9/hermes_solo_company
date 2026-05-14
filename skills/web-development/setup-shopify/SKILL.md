---
name: setup-shopify
description: Plan, edit, preview, or prepare Shopify storefront/theme work for ecommerce pages, products, collections, Liquid sections, SEO, and conversion improvements.
version: 1.1.0
metadata:
  hermes:
    tags: [web-development, shopify, ecommerce, command]
    related_skills: [shopify-site-builder, website-seo-content, website-qa-deploy]
---

# Setup Shopify

Use this skill when the user invokes `/setup-shopify` or asks for Shopify store,
theme, product, collection, or storefront work.

## Workflow

1. Use `shopify-site-builder` as the primary skill.
2. Determine whether the task is theme customization, Liquid section editing,
   product/collection optimization, content/SEO, or deployment guidance.
3. Work in a duplicate/development theme unless the user explicitly approves live
   edits.
4. Check product variants, price display, images, cart behavior, SEO metadata,
   and responsive storefront behavior.
5. Do not change checkout, payment, taxes, shipping, or live theme settings
   without clear approval.

For generated website projects, create a Shopify handoff package:

```bash
scripts/website_agency.py shopify-package --project-dir "<project dir>" --package-type theme-section --title "<storefront title>" --handle "<handle>"
```

Return the generated `dist/hermes-shopify/preview.html`, install notes, and zip
path to the user.
