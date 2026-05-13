---
name: deploy
description: Deploy or prepare deployment for a website after preview and QA, routing to the correct static HTML, Next.js, WordPress, or Shopify workflow.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, deploy, command]
    related_skills: [deploy-site, website-qa-deploy]
---

# Deploy

Use this skill when the user invokes `/deploy`.

Follow `deploy-site` and `website-qa-deploy`. Confirm the target host and get
clear approval before production changes, credential use, billing actions, or
publishing WordPress/Shopify changes live.

For static HTML and Next.js preparation, prefer:

```bash
scripts/website_agency.py deploy-prep --project-dir "<project dir>" --target auto
```
