---
name: export
description: Export a website project, HTML package, WordPress content/package, or Shopify-ready assets for handoff or deployment.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, export, command]
    related_skills: [export-site, website-agency-orchestrator]
---

# Export

Use this skill when the user invokes `/export`.

Follow `export-site`. Identify the target format, collect the right files, run
basic validation when practical, and return the export path plus deployment or
handoff notes.

For static HTML and Next.js handoff, prefer:

```bash
scripts/website_agency.py deploy-prep --project-dir "<project dir>" --target auto
```
