# Hermes MCP for WordPress

Reusable WordPress plugin that exposes a controlled MCP-style HTTP endpoint for Hermes Agent.

## Install

Copy this folder into a WordPress site:

```bash
wp-content/plugins/hermes-mcp-wordpress-plugin
```

Activate **Hermes MCP for WordPress** from wp-admin. On multisite installs, you can network-activate it, then configure each site independently.

## Configure A Site

1. Go to **Settings -> Hermes MCP** in the site dashboard.
2. Click **Generate New API Key** and copy the key immediately.
3. Select the WordPress user Hermes should act as.
4. Enable the MCP endpoint.
5. Enable only the tools this site should expose.
6. Save settings.

The plugin shows the site-specific endpoint, usually:

```text
https://example.com/wp-json/hermes-mcp/v1/mcp
```

Health check:

```text
https://example.com/wp-json/hermes-mcp/v1/health
```

## Hermes Config

Add one entry per WordPress site in `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  client_a_wp:
    url: "https://client-a.com/wp-json/hermes-mcp/v1/mcp"
    headers:
      Authorization: "Bearer CLIENT_A_API_KEY"
    timeout: 60

  client_b_wp:
    url: "https://client-b.com/wp-json/hermes-mcp/v1/mcp"
    headers:
      Authorization: "Bearer CLIENT_B_API_KEY"
    timeout: 60
```

Restart Hermes or run `/reload-mcp` in an active Hermes chat.

## Initial Tools

- `list_posts`
- `get_post`
- `create_draft_post`
- `update_post`
- `list_pages`
- `get_page`
- `update_page`
- `upload_media_from_url`
- `list_comments`
- `update_comment_status`

The first version intentionally avoids destructive site administration tools such as plugin installation, theme editing, user deletion, or core updates.

## Security Notes

- Use HTTPS only.
- Generate a different API key per site.
- Select a dedicated WordPress user for the plugin instead of using your personal admin account.
- Leave dangerous tools disabled or unimplemented unless you add explicit approval workflows.
- Use a dedicated WordPress user with the minimum role needed for the workflow.
- Keep audit logging enabled while testing.

## Test With Curl

Replace `TOKEN` and the URL:

```bash
curl -sS https://example.com/wp-json/hermes-mcp/v1/mcp \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer TOKEN' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

Call a tool:

```bash
curl -sS https://example.com/wp-json/hermes-mcp/v1/mcp \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer TOKEN' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"list_pages","arguments":{"limit":10}}}'
```
