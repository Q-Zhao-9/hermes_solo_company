# Easiio Chatbot WordPress Plugin

This WordPress plugin injects the Easiio chatbot widget into a WordPress site and lets a WordPress admin configure safe public widget options from the dashboard.

The browser widget talks to the Easiio chatbot backend, which handles RAG knowledge retrieval, AI answer formatting, lead capture, Solo CRM writes, email automation, and optional external CRM sync.

## Current status

Class-ready local package implementation. Review the public backend URL before activating on a production site.

Packaged ZIP:

```text
/home/jianl/.hermes/tools/website_chatbot/dist/easiio-chatbot-wordpress-plugin.zip
```

## Install by WordPress admin upload

1. In WordPress admin, go to:

   ```text
   Plugins → Add New → Upload Plugin
   ```

2. Upload:

   ```text
   easiio-chatbot-wordpress-plugin.zip
   ```

3. Activate the plugin.
4. Open:

   ```text
   Settings → Easiio Chatbot
   ```

5. Configure the public widget options.
6. Click **Check backend health**.
7. View the public site and confirm the chatbot appears.

## Settings → Easiio Chatbot

The settings page supports:

```text
API base URL
Widget script URL
Site ID
Organization name
Website name
Chat title
Greeting
Primary color
Position
Launcher style
Launcher size
Auto open
Track page views
Enable automatic lead forms
Enable RAG admin on public pages
Enable voice playback
Voice button label
Enable voice input
Voice input button label
Voice input language
Public contact email
Excluded paths
Consent text
```

Default backend/widget URL:

```text
https://chat.easiio.com/widget.js
```

Default script configuration:

```text
data-site-id="easiio-main"
data-api-base="https://chat.easiio.com"
data-position="bottom-right"
data-title="Easiio Assistant"
data-primary-color="#2563eb"
data-launcher-style="bubble"
data-launcher-size="small"
data-auto-open="false"
data-rag-admin="false"
data-lead-forms-enabled="false"
data-voice-enabled="false"
data-voice-label="Listen"
data-voice-input-enabled="false"
data-voice-input-label="Speak"
data-voice-input-language="auto"
```

Voice playback is optional and off by default. When enabled, the widget shows a **Listen** button under bot replies and calls the backend `POST /api/chat/voice` endpoint. TTS provider credentials stay server-side on the chatbot backend; the WordPress plugin only outputs public flags such as `data-voice-enabled` and `data-voice-label`.

Voice input is also optional and off by default. When enabled, the widget shows a **Speak** microphone button in supported browsers using the browser `SpeechRecognition` / `webkitSpeechRecognition` API. No server-side speech API key is stored or rendered by the WordPress plugin.

## Health check

The **Health check** button in `Settings → Easiio Chatbot` calls the backend `/health` endpoint from the WordPress server using `wp_remote_get()`.

It returns only sanitized status such as:

```text
Backend reachable: HTTP 200
```

It does not display backend response bodies, API keys, tokens, CRM paths, or credentials.

## Safe production rules

- LLM keys are server-side only.
- CRM tokens are server-side only.
- HubSpot tokens are server-side only.
- Google Sheets webhook URLs are server-side only.
- SMTP/Brevo keys are server-side only.
- MCP details and local database paths are server-side only.
- The WordPress plugin should only render public widget configuration.
- Keep `data-rag-admin="false"` on public visitor pages.
- Keep `data-auto-open="false"` unless the owner explicitly wants proactive opening.
- Keep automatic lead forms disabled unless the site needs them.
- Keep voice playback disabled unless the backend `/api/chat/voice` endpoint and server-side TTS provider have been reviewed.
- Keep voice input disabled unless the site owner has reviewed browser microphone UX and consent expectations.

## Recommended class setup

For AI Solo Company class demos:

1. Pick one stable `site_id`, for example:

   ```text
   ai-solo-demo
   ```

2. Configure the plugin with that `site_id`.
3. Make sure the chatbot backend is running.
4. Add page content or manual RAG knowledge for the same `site_id`.
5. Ask the chatbot one factual question.
6. Test one high-intent message:

   ```text
   I want a demo for AI agents. My email is founder@example.com
   ```

7. Verify Solo CRM has a contact, activity, and possible deal.

## Editing configuration in code

Most users should use the settings page. Developers can still review defaults inside:

```text
wordpress-plugin/easiio-chatbot/easiio-chatbot.php
```

## Packaging

From the module root:

```bash
cd /home/jianl/.hermes/tools/website_chatbot
rm -f dist/easiio-chatbot-wordpress-plugin.zip
mkdir -p dist
cd wordpress-plugin
zip -r ../dist/easiio-chatbot-wordpress-plugin.zip easiio-chatbot -x '*.DS_Store' '__MACOSX/*'
```

## Verification

Run:

```bash
node /home/jianl/.hermes/tools/website_chatbot/tests/wp_plugin_static.test.js
php -l /home/jianl/.hermes/tools/website_chatbot/wordpress-plugin/easiio-chatbot/easiio-chatbot.php
```

If PHP is not installed in WSL, run the Node static test and perform PHP lint in a WordPress/PHP environment before production activation.


## Optional browser AI voice call

The settings page includes safe public options for the Phase 3 browser AI voice-call prototype:

- Enable browser AI voice call
- Voice call button label
- Voice-call API base URL
- Voice call consent text

These settings only render public widget attributes such as `data-voice-call-enabled` and `data-voice-call-api-base`. STT/TTS/Twilio/provider keys must stay on the protected server and must never be stored in WordPress options or rendered in page HTML.

Recommended production default: keep voice call disabled until the voice backend, CORS, consent, and provider costs are reviewed.
