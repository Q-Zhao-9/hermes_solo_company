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
2. For shareable previews, use Hermes proxy as the main path:

   ```bash
   scripts/website_agency.py preview-share --project-dir "<project dir>" --port 3010 --prefer hermesproxy
   ```

   This starts the local preview server, starts the Hermes proxy connector,
   returns the public URL, and records preview history in
   `docs/hermes-website-state.json`.
3. For local-only preview planning, use:

   ```bash
   scripts/website_agency.py build-preview --project-dir "<project dir>" --port 3010
   ```

   Add `--start` when the user explicitly wants the local preview server started.
4. Build or start the dev/preview server using the project convention.
5. For local browser access, bind to `0.0.0.0` when needed and provide the local
   URL plus any Windows/WSL access note.
6. Use `sitelet-cloud-render` only as fallback for static HTML or HTML export
   when Hermes proxy is not configured or unavailable.
7. If the build fails, switch to `fix-build`.

Return the preview URL and the command/process status.

After creating a preview, run QA when the user asks for readiness or before
publishing:

```bash
scripts/website_agency.py qa --project-dir "<project dir>"
```
