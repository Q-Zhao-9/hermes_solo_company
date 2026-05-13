---
name: build-preview
description: Build a website and create a local, proxy, or Sitelet preview URL so the user can inspect the current version before publishing.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, preview, build, command]
    related_skills: [website-qa-deploy, hermes-proxy-server, sitelet-cloud-render, nextjs-site-builder, static-html-site-builder]
---

# Build Preview

Use this skill when the user invokes `/build-preview` or asks to see the current
website in a browser.

## Workflow

1. Inspect the project type and package scripts.
2. For static HTML and Next.js projects, prefer the deterministic helper:

   ```bash
   scripts/website_agency.py build-preview --project-dir "<project dir>" --port 3010
   ```

   Add `--start` when the user explicitly wants the local preview server started.
3. Build or start the dev/preview server using the project convention.
4. For local browser access, bind to `0.0.0.0` when needed and provide the local
   URL plus any Windows/WSL access note.
5. Use `hermes-proxy-server` for public preview of a local server.
6. Use `sitelet-cloud-render` for uploaded static HTML or WordPress pre-deploy
   preview history.
7. If the build fails, switch to `fix-build`.

Return the preview URL and the command/process status.
