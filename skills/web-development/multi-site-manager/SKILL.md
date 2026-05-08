---
name: multi-site-manager
description: Manage and switch between multiple websites safely, including WordPress MCP sites, local development sites, staging deployments, and production URLs.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, multi-site, wordpress, mcp, website-management]
    related_skills: [discord-website-preview, native-mcp, dogfood]
---

# Multi-Site Manager

Use this skill when the user manages more than one website and wants Hermes to inspect, preview, edit, or publish changes while clearly switching between sites.

This skill defines a lightweight operating model:

- maintain a site registry
- choose an active site
- verify the target before write actions
- route tool calls to the correct MCP server, local project, or deployment URL
- summarize which site was changed

## Core Concepts

### Site Registry

Maintain a small registry in conversation memory or in a project note when the user has multiple sites.

Recommended fields:

```yaml
sites:
  easiio:
    label: Easiio
    production_url: https://www.easiio.com/
    mcp_server: easiio_wp
    platform: wordpress
    default_preview: production

  client_a:
    label: Client A
    production_url: https://client-a.com/
    staging_url: https://staging.client-a.com/
    mcp_server: client_a_wp
    platform: wordpress

  local_blog:
    label: Local Blog
    local_path: ./blog-website
    dev_url: http://localhost:3000/
    platform: nextjs
```

If no registry exists, build one from the user's description and ask for missing essentials only.

### Active Site

The active site is the default target for follow-up requests.

When the user says:

```text
switch to easiio
```

Set the active site to `easiio` and repeat a short confirmation:

```text
Active site: Easiio — https://www.easiio.com/ — MCP server easiio_wp.
```

Do not assume a write target when the user has multiple configured sites and the request is ambiguous.

## Site Switching Rules

1. If the user names a site, switch to that site for the current request.
2. If the user says "use the same site", use the active site from the current conversation.
3. If multiple sites could match, ask a short clarification before any write.
4. Before a destructive or publishing action, restate the site and object:
   ```text
   I am about to update Easiio page 23545 on https://www.easiio.com/.
   ```
5. Read-only actions can proceed with the active site, but the response must name the site used.

## WordPress MCP Routing

For WordPress sites connected through MCP, infer the MCP tool prefix from the registry:

```text
mcp_<mcp_server>_<tool_name>
```

Example for `easiio_wp`:

- `mcp_easiio_wp_list_pages`
- `mcp_easiio_wp_get_page`
- `mcp_easiio_wp_update_page`
- `mcp_easiio_wp_create_draft_post`

Operational pattern:

1. Resolve active site.
2. Confirm the site's MCP server exists in the available MCP tool list.
3. Use read tools first (`list_pages`, `get_page`, `list_posts`, `get_post`).
4. For edits, fetch current content before updating.
5. Prefer draft or pending status for new content unless the user asks to publish.
6. Preview the public URL or draft URL when available.
7. Report the site, content ID, title, URL, and action performed.

## Local Development Routing

For local sites:

1. Resolve active site and `local_path`.
2. Inspect the project to find the dev command.
3. Start or reuse the dev server.
4. Use `discord-website-preview` to capture screenshots.
5. If edits are requested, modify files in the local project and preview again.

Do not start multiple dev servers for the same site unless the existing one is unreachable.

## Deployment Environment Routing

If a site has production and staging:

- Default read-only previews to production unless the user says staging.
- Default edits to local or staging.
- Never edit production when staging exists unless the user explicitly says production.

Use exact environment labels in responses:

```text
Previewed Client A staging: https://staging.client-a.com/pricing
```

## Common Commands The User May Say

### Register A Site

```text
Add easiio as a WordPress MCP site using mcp server easiio_wp and production URL https://www.easiio.com/
```

Action:
- Add it to the working registry.
- Confirm the tools available.
- Optionally run `list_pages` to verify access.

### Switch Active Site

```text
Switch to easiio.
```

Action:
- Set active site to `easiio`.
- Confirm the site and available management surface.

### Read Content

```text
List pages on the active site.
```

Action:
- Use active site MCP/local route.
- Include site name in the answer.

### Edit Content

```text
Update the homepage hero copy on easiio.
```

Action:
1. Resolve `easiio`.
2. Find homepage/page ID.
3. Fetch current page.
4. Apply the requested update.
5. Preview with `discord-website-preview`.
6. Return the screenshot and exact page ID.

### Compare Sites

```text
Compare the homepage design between easiio and client_a.
```

Action:
- Capture screenshots for both sites.
- Summarize visible differences.
- Return both screenshots with clear labels.

## Safety Rules

- Always identify the target site before writes.
- Never edit "the website" when multiple sites are registered unless an active site is clearly set.
- Keep production publishing explicit.
- Prefer draft creation over direct publishing.
- For WordPress MCP, do not use delete/admin/plugin/theme/core actions unless the user explicitly requests them and the tool surface supports them.
- For Discord previews, send screenshots with a real media attachment tag only after verifying the screenshot path exists; include the site label in the visible text.

## Response Template

For read-only operations:

```text
Site: Easiio — https://www.easiio.com/
Action: listed 5 pages
...
```

For write operations:

```text
Site: Easiio — https://www.easiio.com/
Changed: page 23545, "React Javascript Developer"
Preview:
screenshot attached from verified capture path
```

For ambiguity:

```text
Which site should I use: easiio, client_a, or local_blog?
```
