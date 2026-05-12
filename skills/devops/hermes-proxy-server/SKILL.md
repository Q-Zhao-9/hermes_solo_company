---
name: hermes-proxy-server
description: Start one or more local Hermes proxy connectors for local websites, Sitelet instances, or Hermes API servers, then return public preview URLs from the Hermes cloud proxy.
version: 1.2.0
metadata:
  hermes:
    tags: [devops, proxy, tunnel, sitelet, local-development, cloud]
---

# Hermes Proxy Server

Use this skill when the user wants a public URL that tunnels back to a local
Hermes machine, Sitelet instance, or website dev server. This is the Hermes
managed alternative to ngrok-style access.

## Current Architecture

- Cloud proxy dashboard: `HERMES_PROXY_BASE_URL`
- Local connector token: `HERMES_PROXY_TOKEN`
- Local connector implementation: `hermes_proxy/proxy-server/local_connector.py`
- Helper script for Hermes: `scripts/start_hermes_proxy_connector.py`
- Public preview URL shape:

```text
https://proxy.example.com/p/<tunnel-id>/
```

The user creates a proxy token in the cloud proxy dashboard. The local Hermes
machine uses that token to connect outward to the cloud proxy over WebSocket.
Browser requests to `/p/<tunnel-id>/...` are forwarded to the local service.
One proxy token can expose multiple local services at the same time. Each
connector should use a different `--site` name, which creates a different
public URL.

## Required Local Configuration

Read these from the environment, normally `~/.hermes/.env`:

```bash
HERMES_PROXY_BASE_URL=https://hermesproxy.easiiodev.ai
HERMES_PROXY_TOKEN=hpxy_...
HERMES_PROXY_REPO_DIR=/tmp/hermes_proxy
```

Do not commit real `HERMES_PROXY_TOKEN` values.

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
```

The helper prints JSON with:

- `pid`
- `target`
- `site`
- `tunnelId`
- `publicUrl`
- `logFile`

Return `publicUrl` to the user.

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
