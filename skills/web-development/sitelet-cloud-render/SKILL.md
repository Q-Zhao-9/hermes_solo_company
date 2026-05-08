---
name: sitelet-cloud-render
description: Upload generated or modified website HTML to a cloud Sitelet server with a user API token, then return the Sitelet preview URL to Discord or another chat.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, sitelet, discord, preview, cloud, token]
    related_skills: [discord-website-preview, multi-site-manager]
---

# Sitelet Cloud Render

Use this skill when the user wants Hermes to render a generated, modified, or local website page through a cloud-hosted Sitelet server and share the preview URL in Discord or another chat.

## Configuration

The Sitelet cloud service uses:

- `SITELET_BASE_URL`: base URL of the deployed Sitelet app, for example `https://sitelet.example.com`
- `SITELET_API_TOKEN`: user token from the Sitelet dashboard

When the user asks to set the Sitelet URL or token, update `~/.hermes/.env` with these values. Do not print the token back to chat. Restart the gateway if the running bot needs to pick up the new environment.

## Upload Workflow

1. Confirm `SITELET_BASE_URL` and `SITELET_API_TOKEN` are configured.
2. Prepare the page HTML:
   - For generated pages, use the generated HTML directly.
   - For modified website files, read the final HTML file or render the app route and capture the HTML when practical.
   - Do not include secrets, admin cookies, private customer data, or hidden environment values in the uploaded HTML.
3. POST the page to Sitelet:
   ```bash
   curl -sS "$SITELET_BASE_URL/api/generated" \
     -H "Authorization: Bearer $SITELET_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title":"Preview","source":"hermes","html":"<!doctype html>..."}'
   ```
4. Parse the JSON response. A successful response includes:
   - `generatedUrl`
   - `siteletUrl`
   - `id`
5. Send `siteletUrl` to the current chat or target Discord channel.
6. If the user asks for a screenshot, open `siteletUrl` with browser tools, capture a screenshot, verify the image path exists, then send it as a media attachment.

## Chat Response Pattern

Keep the response short:

```text
Sitelet preview is ready:
<siteletUrl>
Generated page ID: <id>
```

For Discord, a local `localhost` URL is not useful unless Discord is on the same machine. Prefer the deployed HTTPS `SITELET_BASE_URL` for shared links.

## Troubleshooting

- `401`: token is missing, invalid, or revoked. Ask the user to create a new token in the Sitelet dashboard.
- `SITELET_AUTH_SECRET` error on the server: the cloud deployment is missing a production auth secret.
- Empty or broken preview: verify the uploaded HTML contains complete markup and absolute asset URLs when assets are external.
- Forms and navigation inside `/sitelet` are best-effort. For complex apps, share screenshots or deploy a staging build.
