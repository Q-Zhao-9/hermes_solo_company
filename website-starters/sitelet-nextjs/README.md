# Sitelet Next.js Cloud Starter

Sitelet is a small Next.js web server that lets Hermes preview and operate another website through a browser-rendered proxy. This version can run locally or in the cloud and includes user login plus per-user API tokens for Hermes uploads.

It is designed for remote review workflows:

- Hermes can open a local or remote page inside Sitelet.
- Hermes can post generated HTML into Sitelet with a bearer token and receive a preview URL.
- The server fetches the target page.
- The client browser renders the proxied page in an iframe.
- Links and basic forms are rewritten to stay inside Sitelet.
- The user can view the result from Discord screenshots or a temporary preview link.

## Features

- Email/password account creation
- Signed HTTP-only session cookie for dashboard access
- Per-user API tokens for Hermes agents
- Token-authenticated generated page upload at `/api/generated`
- Public generated page and `/sitelet` preview URLs for sharing in Discord
- File-backed storage under `.sitelet/` by default

## Run

```bash
cd website-starters/sitelet-nextjs
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

Create an account at:

```text
http://localhost:3000/register
```

Then open the token dashboard:

```text
http://localhost:3000/dashboard
```

Preview a site directly:

```text
http://localhost:3000/sitelet?url=https://www.easiio.com/
```

## Cloud Deploy

Set these environment variables in the cloud host:

```bash
SITELET_AUTH_SECRET=replace-with-at-least-32-random-characters
SITELET_DATA_DIR=/persistent/sitelet-data
SITELET_GENERATED_DIR=/persistent/sitelet-data/generated
```

`SITELET_DATA_DIR` and `SITELET_GENERATED_DIR` must point to persistent storage. If the host has an ephemeral filesystem, use a mounted volume or swap `lib/sitelet-store.ts` and `lib/generated-store.ts` to a database-backed implementation.

Build and run:

```bash
npm run build
npm run start
```

## Generated Page Preview

Sitelet can store generated HTML and return a URL that Hermes can preview and screenshot. The cloud upload endpoint requires either a logged-in browser session or a bearer token.

Create a generated page:

```bash
curl -sS https://your-sitelet-domain.example/api/generated \
  -H "Authorization: Bearer $SITELET_API_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Landing Page Draft",
    "source": "hermes",
    "html": "<!doctype html><html><body><h1>Hello from Sitelet</h1></body></html>"
  }'
```

Response:

```json
{
  "ok": true,
  "id": "generated-id",
  "generatedUrl": "http://localhost:3000/generated/generated-id",
  "siteletUrl": "http://localhost:3000/sitelet?url=http%3A%2F%2Flocalhost%3A3000%2Fgenerated%2Fgenerated-id"
}
```

Send `siteletUrl` directly to Discord, or open it in the browser tool and return a screenshot.

## Hermes Configuration

Generate a token from `/dashboard`, then store these values where the Hermes gateway can read them:

```bash
SITELET_BASE_URL=https://your-sitelet-domain.example
SITELET_API_TOKEN=stlt_your_token_here
```

Use the `sitelet-cloud-render` skill. Hermes should POST generated HTML to `$SITELET_BASE_URL/api/generated` with `Authorization: Bearer $SITELET_API_TOKEN`, then share the returned `siteletUrl`.

## How It Works

The route handler at `/sitelet` accepts `GET`, `POST`, `PUT`, `PATCH`, and `DELETE`.

For HTML responses it:

- rewrites `href`, `src`, `action`, and `srcset` references
- forwards form bodies to the target URL
- injects a small toolbar banner
- strips frame-blocking CSP headers on the proxied response

For non-HTML responses it streams the upstream asset response back to the browser.

## Hermes / Discord Usage

Use the `sitelet-cloud-render` skill when Hermes needs to upload generated HTML to this cloud service and return a link. Use `discord-website-preview` when the user asks for a screenshot attachment instead of a clickable link.

For generated website drafts, use `/api/generated` first, then preview the returned `siteletUrl`.

## Safety

Sitelet is a development and review tool, not a hardened production reverse proxy.

Do not expose admin dashboards, credentials, customer data, private staging sites, or logged-in sessions through a public tunnel unless you explicitly understand the risk.

Recommended usage:

- preview public pages first
- upload generated mockups through `/api/generated`
- use per-user tokens and revoke old tokens
- use screenshots for private material
- avoid exposing admin pages, credentials, logged-in sessions, or unpublished confidential content
