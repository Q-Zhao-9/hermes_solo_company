---
name: setup-wordpress
description: Plan, build, preview, or publish WordPress pages and site changes using Hermes website workflow, WordPress preview, plugin guidance, and safe draft/staging practices.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, wordpress, cms, command]
    related_skills: [wordpress-site-builder, sitelet-cloud-render, multi-site-manager, website-qa-deploy]
---

# Setup WordPress

Use this skill when the user invokes `/setup-wordpress` or asks for a WordPress
website, page, editing workflow, preview, or publish setup.

## Workflow

1. Use `wordpress-site-builder` as the primary skill.
2. Determine whether the task is site planning, page creation, plugin setup,
   WordPress MCP editing, Sitelet preview, or publishing.
3. Use `sitelet-cloud-render` and `wordpress_preview_publish` for pre-deploy
   preview HTML and history when available.
4. Use `multi-site-manager` when the user has multiple WordPress sites.
5. Prefer draft or staging status before live publishing.
6. Run `website-qa-deploy` checks before production changes.
