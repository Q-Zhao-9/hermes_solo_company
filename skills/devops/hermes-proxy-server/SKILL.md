---
name: hermes-proxy-server
description: Start and manage one or more simultaneous local Hermes proxy connectors from one bot/server, assigning each local website a unique site name and public preview URL.
version: 1.3.0
metadata:
  hermes:
    tags: [devops, proxy, tunnel, sitelet, local-development, cloud]
---

# Hermes Proxy Server

Use this skill when the user wants public URLs that tunnel back to one or more
local websites on the same Hermes machine. Treat multi-site support as the
default: one Hermes bot/server can expose several local services at the same
time through the same `HERMES_PROXY_BASE_URL` and `HERMES_PROXY_TOKEN`.

## Current Architecture

- Cloud proxy dashboard: `HERMES_PROXY_BASE_URL`
- Local connector token: `HERMES_PROXY_TOKEN`
- Local connector implementation: `hermes_proxy/proxy-server/local_connector.py`
- Helper script for Hermes: `scripts/start_hermes_proxy_connector.py`
- Public preview URL shape for each site:

```text
https://proxy.example.com/p/<base-tunnel-id>-<site>/
```

The user creates a proxy token in the cloud proxy dashboard. The local Hermes
machine uses that token to connect outward to the cloud proxy over WebSocket.
Browser requests to `/p/<tunnel-id>/...` are forwarded to the matching local
service. One proxy token can expose multiple local services at the same time.
Each connector must use a different `--site` name, which creates a different
public URL. Reusing a `--site` name intentionally replaces that site's existing
connector.

## Required Local Configuration

Read these from the environment, normally `~/.hermes/.env`:

```bash
HERMES_PROXY_BASE_URL=https://hermesproxy.easiiodev.ai
HERMES_PROXY_TOKEN=hpxy_...
HERMES_PROXY_REPO_DIR=/tmp/hermes_proxy
```

Do not commit real `HERMES_PROXY_TOKEN` values.

## Multi-Site Operating Rules

- Always choose a stable, unique `--site` key for each local website, such as
  `sitelet`, `crm`, `marketing`, `student-demo`, or `wp-preview`.
- Do not start a new connector with a site key that is already in use unless the
  user wants to replace that site's target.
- Use one helper invocation per local service. Multiple helper processes can
  run at the same time.
- If the user asks to expose several local websites, start all requested
  connectors and return a compact list or table of `site`, `target`, and
  `publicUrl`.
- If the user only says "expose the website", infer a site key from the app
  name or port, for example `sitelet` for port `3020` or `local-8002` for port
  `8002`.

## Start A Public Preview

When a user asks to expose a local service, first identify the local target URL:

- Sitelet: `http://127.0.0.1:3020`
- local website dev server: usually `http://127.0.0.1:3000`, `:3001`, or `:8002`
- Hermes API server: `http://127.0.0.1:8642`

Then run:

```bash
python3 scripts/start_hermes_proxy_connector.py \
  --target http://127.0.0.1:3020 \
  --site sitelet
```

For multiple simultaneous websites, run the helper once per local service with
a unique `--site` value:

```bash
python3 scripts/start_hermes_proxy_connector.py --target http://127.0.0.1:3000 --site app
python3 scripts/start_hermes_proxy_connector.py --target http://127.0.0.1:8002 --site marketing
python3 scripts/start_hermes_proxy_connector.py --target http://127.0.0.1:3020 --site sitelet
```

The helper prints JSON with:

- `pid`
- `target`
- `site`
- `tunnelId`
- `publicUrl`
- `logFile`

Return `publicUrl` to the user. For multiple sites, return one line per site:

```text
sitelet   http://127.0.0.1:3020   https://proxy.example.com/p/<id>-sitelet/
marketing http://127.0.0.1:8002   https://proxy.example.com/p/<id>-marketing/
```

## Manual Connector Command

If the helper is unavailable, run the connector directly:

```bash
cd /tmp/hermes_proxy/proxy-server
export CLOUD_PROXY_URL="$HERMES_PROXY_BASE_URL"
export HERMES_PROXY_TOKEN="$HERMES_PROXY_TOKEN"
export LOCAL_PROXY_TARGET="http://127.0.0.1:3020"
export HERMES_PROXY_SITE="sitelet"
python3 local_connector.py
```

Keep the process running while the public preview URL is needed.

## Health Check

Cloud proxy:

```bash
curl "$HERMES_PROXY_BASE_URL/_health"
```

The response should show an active tunnel:

```json
{"status":"ok","active_tunnels":2,"tunnels":["..."],"activeTunnels":[...]}
```

Public preview:

```bash
curl -I "$HERMES_PROXY_BASE_URL/p/<tunnel-id>/"
```

For multi-site debugging, inspect `activeTunnels`; each item includes
`tunnelId`, `baseTunnelId`, `site`, and `target`.

## Safety Rules

- Do not expose admin dashboards, private customer data, logged-in browser
  sessions, API keys, database consoles, or internal-only services unless the
  user explicitly confirms the risk.
- Keep `LOCAL_PROXY_TARGET` scoped to the specific local service needed for the
  task.
- Use the generated `hpxy_...` proxy token only in local environment files or
  process environment variables.
- Rotate the token if it was printed in public logs or committed accidentally.
- Use a unique `--site` name for each simultaneous local service. Reusing the
  same site name intentionally replaces the previous connector for that site.

## Troubleshooting

- `/_health` shows no active tunnels: start or restart the local connector and
  verify `HERMES_PROXY_BASE_URL`, `HERMES_PROXY_TOKEN`, and network access.
- Public URL returns `503`: the cloud proxy is running but the local connector
  is not connected for that tunnel.
- Public URL returns `502`: the local target is down or rejected the forwarded
  request.
- Browser shows a blank page: check the local target directly first, then curl
  the public preview URL. If the page uses absolute asset paths, reload once so
  the proxy tunnel cookie is set.
