# AI Solo Company voice chat + voice call Sitelet integration

Use this note when adding or repairing the voice-enabled chatbot experience on the AI Solo Company live/static site.

## Live/static site reference

```text
Static source: /mnt/c/Users/jianl/solo-company-class-site/
Live proxy: https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-ai-solo/
Chatbot API: https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-chatbot-api
Voice API: https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-voice-api
```

## Files usually changed

```text
/mnt/c/Users/jianl/solo-company-class-site/index.html
/mnt/c/Users/jianl/solo-company-class-site/styles.css
/mnt/c/Users/jianl/solo-company-class-site/chatbot/widget.js
/mnt/c/Users/jianl/solo-company-class-site/chatbot/widget.css
```

## Integration pattern

1. Add visible entry points on the page, typically hero buttons such as **Open AI Chat** and **Start Voice Call**.
2. Add a short section explaining the AI Voice Assistant capabilities: text chat, browser voice call, course/site RAG knowledge, and CRM/lead behavior if applicable.
3. Load the voice-capable chatbot widget from the site's local `chatbot/widget.js` asset and cache-bust the script URL after updates.
4. Ensure the embed uses the public proxy API URLs, not localhost paths.
5. Enable voice attributes on the embed:

```html
data-voice-enabled="true"
data-voice-input-enabled="true"
data-voice-call-enabled="true"
```

6. Keep the browser widget calling the backend HTTP APIs only; it must not call MCP directly.

## Verification checklist

Before reporting completion, verify:

```text
AI Solo Company site local HTTP: 200
AI Solo Company live proxy HTTP: 200
Remote widget JS: 200
Public chatbot API health: 200
Public voice API health: 200
```

Also verify static markers in the generated HTML/JS/CSS and ask one RAG-backed question through the public chatbot API, e.g.:

```text
What does lesson 3 build?
```

A good completion marker from the prior working run was:

```text
ai_solo_voice_static_checks_ok
ai_solo_voice_local_http_ok
ai_solo_remote_voice_markers_ok
ai_solo_remote_widget_voice_ok
ai_solo_public_api_health_ok
ai_solo_public_chat_rag_ok
```

## Pitfalls

- If the old widget appears, cache-bust `chatbot/widget.js` and test with hard refresh/incognito.
- Confirm both the chatbot API and voice API are public proxy URLs; localhost URLs will fail for live visitors.
- Voice call testing may require browser microphone permission and HTTPS.
- RAG lead forms for AI Solo Company are normally disabled by default; factual questions should be answered directly.
