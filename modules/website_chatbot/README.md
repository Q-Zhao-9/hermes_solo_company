# Easiio Website Chatbot

Embeddable website chatbot widget for Easiio pages. The widget captures leads and connects them to the Solo CRM backend created at:

```text
/home/jianl/.hermes/tools/solo_crm
```

Current status: **v2 local backend + Solo CRM bridge implemented**.

## Files

```text
/home/jianl/.hermes/tools/website_chatbot/
  README.md
  CHATBOT_CRM_IMPLEMENTATION_PLAN.md
  AI_CHAT_AGENT_UI_NOTES.md
  backend/
    app.py
  widget/
    widget.js
    widget.css
    demo.html
  wordpress-plugin/
    easiio-chatbot/
      easiio-chatbot.php
      README.md
  dist/
    easiio-chatbot-wordpress-plugin.zip
  tests/
    test_backend.py
    widget_static.test.js
    wp_plugin_static.test.js
```

## What works now

- Floating website chatbot popup widget.
- Mock mode still works with `data-api-base="mock"`.
- Backend mode works with `data-api-base="http://localhost:8099"`.
- `GET /health`.
- `POST /api/chat/session`.
- `POST /api/chat/message`.
- `POST /api/chat/lead`.
- Per-site RAG content store and APIs:
  - `GET /api/rag/content?site_id=...`
  - `POST /api/rag/content`
  - `POST /api/rag/content/delete`
- Optional chatbot UI knowledge setup panel with `data-rag-admin="true"`.
- Deterministic email/phone extraction.
- Demo/pricing/sales intent detection.
- Solo CRM writes:
  - create/update company;
  - create/update contact;
  - create deal for demo/pricing/sales intent;
  - add activity for chat message or lead form.

## Run local backend

```bash
python3 /home/jianl/.hermes/tools/website_chatbot/backend/app.py --host 0.0.0.0 --port 8099
```

Optional custom CRM database for testing:

```bash
SOLO_CRM_DB=/tmp/easiio-chatbot-crm.db \
python3 /home/jianl/.hermes/tools/website_chatbot/backend/app.py --host 0.0.0.0 --port 8099
```

Health check:

```bash
curl http://localhost:8099/health
```

Expected:

```json
{"ok": true, "service": "easiio-website-chatbot"}
```

## Run local widget demo

In a second terminal:

```bash
python3 -m http.server 8088 -d /home/jianl/.hermes/tools/website_chatbot/widget
```

Open:

```text
http://localhost:8088/demo.html
```

The demo points to:

```html
data-api-base="http://localhost:8099"
```

Ask something like:

```text
I want a demo for AI agents. My email is founder@example.com
```

That should create a Solo CRM contact, deal, and activity.

## Embed snippet

```html
<script
  async
  src="https://chat.easiio.com/widget.js"
  data-easiio-chatbot
  data-site-id="easiio-main"
  data-api-base="https://chat.easiio.com"
  data-position="bottom-right"
  data-title="Easiio Assistant"
  data-primary-color="#2563eb"
  data-launcher-style="bubble"
  data-launcher-size="small"
  data-auto-open="false"
  data-rag-admin="false"
  data-greeting="Hi, I can help with AI automation or book a demo.">
</script>
```

For local mock-only UI testing without a backend, use:

```html
data-api-base="mock"
```

## Backend API

### `GET /health`

Returns service health.

### `POST /api/chat/session`

Example:

```bash
curl -s http://localhost:8099/api/chat/session \
  -H 'Content-Type: application/json' \
  -d '{"site_id":"easiio-main","page_url":"https://www.easiio.com/"}'
```

### `POST /api/chat/message`

Example:

```bash
curl -s http://localhost:8099/api/chat/message \
  -H 'Content-Type: application/json' \
  -d '{
    "site_id":"easiio-main",
    "session_id":"chat_manual",
    "message":"I want a demo for AI agents. My email is founder@example.com",
    "visitor":{"name":"Founder","company":"Example Co"},
    "page_context":{"url":"https://www.easiio.com/pricing/","title":"Pricing"}
  }'
```

### `POST /api/chat/lead`

Explicit lead form endpoint. Requires email or phone.

### Per-site RAG content API

The RAG index is isolated by `site_id`, so each website can have its own knowledge base. Page visits still contribute page text automatically through `page_context`; manual knowledge can be managed with these endpoints.

List content for one site:

```bash
curl -s 'http://localhost:8099/api/rag/content?site_id=factory-site'
```

Add or update content for one site:

```bash
curl -s http://localhost:8099/api/rag/content \
  -H 'Content-Type: application/json' \
  -d '{
    "site_id":"factory-site",
    "title":"Factory capabilities",
    "url":"https://example.com/capabilities",
    "content":"This factory supports CNC machining, mold components, copper parts, aluminum parts, and inspection."
  }'
```

Delete one content item from one site:

```bash
curl -s http://localhost:8099/api/rag/content/delete \
  -H 'Content-Type: application/json' \
  -d '{"site_id":"factory-site","content_id":"rag_xxx"}'
```

To enable the setup UI inside the chatbot panel, set:

```html
data-rag-admin="true"
```

Keep this off for normal public visitors unless the page is protected, because it allows editing that site's chatbot knowledge.

## Browser controller

The widget auto-initializes from script data attributes and also exposes:

```js
window.EasiioChatbot.set({ title: 'Easiio Assistant' })
window.EasiioChatbot.show()
window.EasiioChatbot.open()
window.EasiioChatbot.minimize()
window.EasiioChatbot.openKnowledge()
window.EasiioChatbot.closeKnowledge()
window.EasiioChatbot.loadRagContentList()
window.EasiioChatbot.close()
```

## Test

Backend tests:

```bash
python3 /home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py
```

Widget static tests:

```bash
node /home/jianl/.hermes/tools/website_chatbot/tests/widget_static.test.js
```

Widget syntax check:

```bash
node --check /home/jianl/.hermes/tools/website_chatbot/widget/widget.js
```

## WordPress plugin package

A local WordPress footer plugin package is available here:

```text
/home/jianl/.hermes/tools/website_chatbot/dist/easiio-chatbot-wordpress-plugin.zip
```

Source files:

```text
/home/jianl/.hermes/tools/website_chatbot/wordpress-plugin/easiio-chatbot/easiio-chatbot.php
/home/jianl/.hermes/tools/website_chatbot/wordpress-plugin/easiio-chatbot/README.md
```

It injects the widget with `wp_footer` using reviewed defaults and `data-auto-open="false"`. Do not activate it on production until `https://chat.easiio.com/widget.js` and the backend API are deployed and reviewed.

## Security notes before production deployment

- Put the backend behind HTTPS, e.g. `https://chat.easiio.com`.
- Keep CORS allowlist restricted with `EASIIO_CHATBOT_ALLOWED_ORIGINS`.
- Add stronger rate limiting before public traffic.
- Do not expose CRM DB paths, MCP server paths, prompts, or secrets in browser JavaScript.
- Add privacy/consent text if collecting personal data on production pages.
- Review WordPress deployment before inserting into `wp_footer` on the live site.

## Next step

Package the WordPress footer plugin and/or add a Next.js component once the local backend and widget flow are reviewed.
