---
name: discord-website-preview
description: Capture local, staged, or modified website previews and deliver screenshots or preview links to Discord without requiring the user to remote into the server.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, discord, preview, screenshot, browser, qa]
    related_skills: [dogfood, popular-web-designs]
---

# Discord Website Preview

Use this skill when the user wants to see how a local, staged, modified, or WordPress-managed website looks from the Hermes interface, especially through Discord.

The default output is a screenshot delivered as a real `MEDIA:` tag that points to an existing absolute file path. Only create a public tunnel when the user asks for an interactive preview link or when a screenshot is insufficient.

## Goals

- Render a local or remote webpage as Hermes sees it.
- Render a generated page through Sitelet when the page was created during the conversation.
- Capture desktop and, when useful, mobile screenshots.
- Send the preview back to Discord as an image attachment.
- Optionally expose a temporary preview URL through a tunnel.
- Avoid requiring the user to SSH, remote desktop, or log into the server just to inspect visual changes.

## Inputs To Collect

Ask only for missing essentials:

1. Target URL or local project path.
2. Page or route to preview.
3. Whether they want desktop, mobile, or both.
4. Whether they want a screenshot only or an interactive temporary URL.

If the user is already in Discord and asks to "show me the site", assume screenshot-only unless they explicitly ask for a link.

## Default Screenshot Workflow

1. Identify the target:
   - Remote URL: use it directly.
   - Local static HTML: serve the directory with a local HTTP server.
   - Local app: detect the existing dev command from the repo (`package.json`, `pyproject.toml`, framework docs) and start it in the background.
   - Generated HTML/page: post the generated HTML to Sitelet's `/api/generated`, then preview the returned `siteletUrl`.
   - WordPress MCP content: fetch or update the page through MCP first, then preview the public URL.

2. Start or reuse the local server:
   - Prefer the project's existing dev command.
   - If static files are enough, use a simple local static server.
   - Record the port and PID/session so it can be stopped later.

3. Open the page with browser tools:
   - Use `browser_navigate(url="<target>")`.
   - Use `browser_console(clear=true)` after navigation.
   - Use `browser_vision(question="Capture a clean screenshot of this webpage and briefly describe visible layout issues.", annotate=false)`.

4. Save the screenshot path returned by `browser_vision`.

5. Send the result to Discord:
   - Only include a `MEDIA:` tag after verifying the file exists.
   - Use the literal media tag prefix followed by the actual absolute path, for example a real screenshot saved under `/tmp/hermes-preview/`.
   - Never output placeholder media tags, fake paths, or example paths.
   - If sending to another Discord channel, use `send_message` with the Discord target and include only the verified real media path.

6. Briefly report:
   - URL previewed
   - viewport used
   - screenshot attachment
   - any visible layout issues
   - console errors, if present

## Generated Website Page Workflow

Use this when Hermes generated a webpage or website draft and the user wants to see it in Discord.

1. Ensure Sitelet is running.
2. POST the generated HTML to Sitelet:
   ```bash
   curl -sS http://localhost:<sitelet_port>/api/generated \
     -H 'Content-Type: application/json' \
     -d '{"title":"Generated Page","source":"hermes","html":"<!doctype html>..."}'
   ```
3. Read the returned `siteletUrl`.
4. Navigate to that `siteletUrl` with browser tools.
5. Capture a screenshot with `browser_vision`.
6. Return the screenshot with a media attachment tag only after verifying the screenshot file exists. Do not include example or placeholder media tags.
7. Include the `generatedUrl` and `siteletUrl` only if the user asks for a clickable preview link. For Discord-first review, the screenshot is usually enough.

For local-only Sitelet URLs, a Discord user can see the screenshot without needing network access to the server. Use a tunnel only when the user asks to interact with the preview directly.

## Responsive Preview Workflow

When the user asks for mobile or responsive preview:

1. Capture a desktop screenshot first.
2. Capture a mobile viewport screenshot if browser tooling supports viewport changes.
3. If viewport resizing is not available through the current browser toolset, explain that the desktop screenshot was captured and offer to run a Playwright-based capture from the terminal if the project has Playwright or Chromium available.
4. Return both screenshots with separate labels, each followed by a real verified media attachment tag. Do not include example or placeholder media tags.

## Interactive Link Workflow

Only use this when requested.

1. Ensure the site is running locally.
2. Prefer an existing tunnel tool if installed (`cloudflared`, `ngrok`, or a project-provided preview command).
3. For `cloudflared`, use a quick tunnel:
   ```
   cloudflared tunnel --config /dev/null --url http://localhost:<port> --no-autoupdate --protocol http2
   ```
4. Capture and share:
   - tunnel URL
   - local URL
   - warning that the tunnel is temporary
   - screenshot preview via a real media attachment tag after the screenshot exists

Never expose admin pages, logged-in sessions, API keys, database consoles, or private dashboards through a tunnel unless the user explicitly confirms the exposure risk.

## WordPress / MCP Preview Pattern

When previewing a WordPress site connected through MCP:

1. Use MCP tools to list or fetch the target page/post.
2. If modifying content, prefer draft or non-destructive edits first.
3. Use the public permalink from the MCP result for browser preview.
4. Capture a screenshot and send it to Discord.
5. Include the WordPress post/page ID in the response so the user can request follow-up edits precisely.

Example response shape:

```text
Previewed easiio.com page 23545 at desktop width.
Screenshot attached from the verified browser capture path.
Console: no critical errors found.
```

## Safety Rules

- Do not send screenshots of admin dashboards, credentials, tokens, private customer data, or unpublished confidential content unless the user explicitly asks and is authorized.
- Do not create public tunnels for private or local-only admin surfaces by default.
- Prefer screenshots over tunnels for routine visual checks.
- Keep preview artifacts under `/tmp/hermes-preview/` or a project-local preview output directory.
- Clean up temporary servers and tunnels when the user is done, unless they ask to keep them running.

## Troubleshooting

- If `browser_navigate` cannot open `localhost`, check whether the browser toolset allows private URLs. If blocked, use a terminal-driven screenshot tool such as Playwright if available, or ask the user whether to enable local browser access.
- If the page is blank, check server logs and `browser_console()`.
- If CSS or assets are missing, verify the app's base URL, proxy config, and build mode.
- If Discord does not show the image, ensure the final response contains a literal media attachment tag with a real absolute path and that the file exists on disk.
