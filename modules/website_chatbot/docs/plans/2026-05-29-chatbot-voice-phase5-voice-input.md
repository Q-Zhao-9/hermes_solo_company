# Chatbot Voice Phase 5 — Browser Voice Input

Date: 2026-05-29

## Summary

Phase 5 adds optional visitor-side voice input to the Easiio website chatbot. The feature is off by default and can be enabled from safe widget configuration, the reusable admin customizer, or the WordPress plugin settings page.

This is intentionally browser-first: it uses the browser `SpeechRecognition` / `webkitSpeechRecognition` API when available. The widget receives transcribed text and submits it through the existing `/api/chat/message` flow. No raw microphone audio, speech API key, cache path, or provider credential is stored in WordPress or exposed to the browser by Easiio.

## Scope implemented

### Backend safe config

`backend/app.py` now includes these public-safe widget config fields under `form_config.widget_config`:

```json
{
  "voice_input_enabled": false,
  "voice_input_label": "Speak",
  "voice_input_language": "auto"
}
```

Sanitization accepts snake_case and camelCase input:

```text
voice_input_enabled / voiceInputEnabled
voice_input_label / voiceInputLabel
voice_input_language / voiceInputLanguage
```

Unsafe keys such as speech API keys or raw transcript/audio paths are not persisted or returned.

### Widget

`widget/widget.js` now supports:

```html
data-voice-input-enabled="true"
data-voice-input-label="Speak"
data-voice-input-language="auto"
```

When enabled, the composer renders a microphone button:

```text
[data-voice-input]
```

Behavior:

1. Visitor clicks the microphone button.
2. Widget checks `window.SpeechRecognition || window.webkitSpeechRecognition`.
3. If supported, browser microphone permission + transcription is handled by the browser.
4. Final transcript is inserted into the chat input.
5. Existing message submit flow sends the text to `/api/chat/message`.
6. If unsupported or unclear, the widget asks the visitor to type instead.

Relevant functions:

```text
renderVoiceInputControl
refreshVoiceInputControl
startVoiceInput
getSpeechRecognitionConstructor
updateVoiceInputStatus
```

### Admin customizer

`admin/chatbot-customizer.js` now includes Voice input settings inside the widget voice card:

- Enable voice input
- Voice input button label
- Voice input language
- Embed snippet preview with the `data-voice-input-*` attributes

The deployed AI Solo admin copy was updated at:

```text
/mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.js
/mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.css
```

### WordPress plugin

The WordPress plugin now includes safe public settings:

- Enable voice input
- Voice input button label
- Voice input language

The footer script outputs:

```html
data-voice-input-enabled="false"
data-voice-input-label="Speak"
data-voice-input-language="auto"
```

Defaults remain conservative:

```text
voice playback: disabled
voice input: disabled
lead forms: disabled
RAG admin: disabled
```

Packaged ZIP:

```text
/home/jianl/.hermes/tools/website_chatbot/dist/easiio-chatbot-wordpress-plugin.zip
```

## Verification

Commands run from `/home/jianl/.hermes/tools/website_chatbot`:

```bash
python3 -m py_compile backend/app.py backend/site_gateway.py
node --check widget/widget.js
node --check admin/chatbot-customizer.js
node tests/widget_static.test.js
node tests/admin_customizer_static.test.js
node tests/wp_plugin_static.test.js
python3 tests/test_backend.py -v
python3 /mnt/c/Users/jianl/solo-company-class-site/auth_download_static_test.py
```

Result:

```text
Ran 47 tests in 13.464s
OK
PASS widget static checks
PASS chatbot customizer admin module static checks
PASS wordpress plugin static checks
auth/download static checks passed
```

## Future follow-up

1. Live browser smoke test in Chrome/Edge because microphone permissions cannot be fully tested with static checks.
2. Optional server-side audio upload/transcription flow if browser SpeechRecognition coverage is not enough.
3. Optional admin UX note explaining browser compatibility and HTTPS requirements.
