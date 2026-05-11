---
name: hermes-proxy-server
description: Configure and operate the Hermes cloud reverse proxy and local connector so a public cloud URL can tunnel to a local Hermes API, Sitelet server, or website dev server.
version: 1.0.0
metadata:
  hermes:
    tags: [devops, proxy, tunnel, sitelet, local-development, cloud]
---

# Hermes Proxy Server

Use this skill when the user wants a public URL that tunnels back to a local
Hermes machine, Sitelet instance, or website dev server. This is the Hermes
managed alternative to ngrok-style access.

## Architecture

- Cloud server: `hermes_proxy/proxy-server/cloud_server.py`
- Local connector: `hermes_proxy/proxy-server/local_connector.py`
- The local connector opens an outbound WebSocket to:
  `https://PUBLIC_HOST/_tunnel/connect`
- Authenticated requests to the public host are forwarded to
  `LOCAL_PROXY_TARGET`, such as:
  - `http://127.0.0.1:8642` for Hermes API server
  - `http://127.0.0.1:3020` for Sitelet
  - `http://127.0.0.1:3000` for a local website

## Required Configuration

Cloud server environment:

```bash
CLOUD_PROXY_TOKEN=shared-secret
CLOUD_PROXY_HOST=0.0.0.0
CLOUD_PROXY_PORT=8787
```

Local connector environment:

```bash
CLOUD_PROXY_URL=https://proxy.example.com
CLOUD_PROXY_TOKEN=shared-secret
LOCAL_PROXY_TARGET=http://127.0.0.1:3020
```

The token must match on both sides.

## Cloud Deploy

```bash
git clone git@github.com:Easiio-Inc/hermes_proxy.git
cd hermes_proxy/proxy-server
export CLOUD_PROXY_TOKEN="$(openssl rand -hex 32)"
docker compose up -d --build
```

Put Caddy/nginx/Cloudflare in front of the cloud server for HTTPS.

## Local Connector

Run manually:

```bash
cd hermes_proxy/proxy-server
python3 -m pip install -r requirements.txt
export CLOUD_PROXY_URL="https://proxy.example.com"
export CLOUD_PROXY_TOKEN="same-token-as-cloud"
export LOCAL_PROXY_TARGET="http://127.0.0.1:3020"
python3 local_connector.py
```

Run as a local service:

```bash
sudo cp hermes-local-proxy.service.example /etc/systemd/system/hermes-local-proxy@.service
sudo mkdir -p /opt/hermes-cloud-proxy
sudo cp local_connector.py requirements.txt local-connector.env.example /opt/hermes-cloud-proxy/
sudo cp /opt/hermes-cloud-proxy/local-connector.env.example /opt/hermes-cloud-proxy/local-connector.env
sudo nano /opt/hermes-cloud-proxy/local-connector.env
sudo systemctl daemon-reload
sudo systemctl enable --now hermes-local-proxy@$USER.service
```

## Health Check

Cloud proxy:

```bash
curl https://proxy.example.com/_health
```

Proxied local target:

```bash
curl -H "Authorization: Bearer $CLOUD_PROXY_TOKEN" https://proxy.example.com/
```

## Safety Rules

- Do not expose admin dashboards, private customer data, logged-in browser
  sessions, API keys, database consoles, or internal-only services unless the
  user explicitly confirms the risk.
- Prefer a dedicated `CLOUD_PROXY_TOKEN` per class, user, or deployment.
- Use HTTPS on the public cloud endpoint.
- Keep `LOCAL_PROXY_TARGET` scoped to the specific local service needed for the
  task.
- Rotate the token if it was printed in chat or logs.

## Troubleshooting

- `/_health` says `connector_connected: false`: start or restart the local
  connector and verify `CLOUD_PROXY_URL` and token.
- Public request returns `401`: the caller is missing
  `Authorization: Bearer <CLOUD_PROXY_TOKEN>`.
- Public request returns `503`: the cloud server is running but no local
  connector is connected.
- Public request returns `502`: the local target is down or rejected the
  forwarded request.
- Browser shows a blank page: check the local target directly first, then try
  the same path through the public proxy with curl.
