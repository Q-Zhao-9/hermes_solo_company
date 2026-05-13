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
2. Build or start the dev/preview server using the project convention.
3. For local browser access, bind to `0.0.0.0` when needed and provide the local
   URL plus any Windows/WSL access note.
4. Use `hermes-proxy-server` for public preview of a local server.
5. Use `sitelet-cloud-render` for uploaded static HTML or WordPress pre-deploy
   preview history.
6. If the build fails, switch to `fix-build`.

Return the preview URL and the command/process status.
