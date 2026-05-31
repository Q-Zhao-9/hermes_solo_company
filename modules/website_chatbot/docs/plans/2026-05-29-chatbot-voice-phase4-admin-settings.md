# Website Chatbot Voice Phase 4 — Admin Console Voice Settings

Date: 2026-05-29

## Goal

Phase 4 adds review-first admin controls for the optional chatbot voice playback feature introduced in Phase 3. The public widget still keeps voice disabled by default, but protected/admin-only chatbot customizer pages can now configure safe per-site voice playback settings without exposing TTS provider credentials or backend cache paths.

## Implemented scope

### 1. Backend form-config storage for safe widget settings

The existing per-site `/api/chat/form-config` endpoint now persists a sanitized `widget_config` object alongside lead-form configuration:

```json
{
  "widget_config": {
    "voice_enabled": false,
    "voice_label": "Listen",
    "voice_autoplay": false,
    "voice": "",
    "voice_format": "mp3"
  }
}
```

Only safe public widget settings are stored/returned. Secret-like inputs such as provider API keys and raw cache paths are ignored.

### 2. Public widget consumes saved voice settings

When the widget loads `/api/chat/form-config?site_id=...`, it now also reads `data.form_config.widget_config` and applies:

- `voice_enabled` -> `voiceEnabled`
- `voice_label` -> `voiceLabel`
- `voice_autoplay` -> `voiceAutoplay`
- `voice` -> `voice`
- `voice_format` -> `voiceFormat`

This lets a reviewed backend/admin setting enable the visitor-facing `Listen` button without hard-coding every script tag.

### 3. Reusable admin customizer UI

Added a new **Voice playback settings** card to:

```text
/home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.js
/home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.css
```

The card supports:

- Enable voice playback
- Autoplay generated audio
- Voice button label
- Optional server-side voice id/name
- Audio format: `mp3`, `wav`, or `opus`
- Preview text explaining the current state
- Embed-attribute snippet for manual script-tag review

The admin UI uses the same protected `/api/chat/form-config` storage and same-origin credentials as the rest of the customizer.

### 4. AI Solo deployed copy updated

Copied the reusable admin customizer assets to the AI Solo site copy:

```text
/mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.js
/mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.css
```

## Safety rules preserved

- Voice remains disabled by default.
- WordPress plugin default remains `data-voice-enabled="false"`.
- TTS provider/API credentials stay server-side only.
- Backend responses do not expose raw audio cache paths.
- Admin customizer should only be embedded in protected/admin-only pages.

## Verification

From:

```bash
cd /home/jianl/.hermes/tools/website_chatbot
```

Passed:

```bash
python3 -m py_compile backend/app.py
node --check admin/chatbot-customizer.js
node --check widget/widget.js
node tests/admin_customizer_static.test.js
node tests/widget_static.test.js
node tests/wp_plugin_static.test.js
python3 tests/test_backend.py -v
python3 /mnt/c/Users/jianl/solo-company-class-site/auth_download_static_test.py
```

Backend result:

```text
Ran 46 tests in 13.988s
OK
```

## Main files changed

```text
/home/jianl/.hermes/tools/website_chatbot/backend/app.py
/home/jianl/.hermes/tools/website_chatbot/widget/widget.js
/home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.js
/home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.css
/home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py
/home/jianl/.hermes/tools/website_chatbot/tests/widget_static.test.js
/home/jianl/.hermes/tools/website_chatbot/tests/admin_customizer_static.test.js
/mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.js
/mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.css
```

## Recommended Phase 5 options

1. Add voice settings to the WordPress admin plugin UI beyond the simple enable/label fields.
2. Add live AI Solo admin-console smoke testing for saving voice settings through the gateway.
3. Add speech-to-text voice input so visitors can ask questions with a microphone.
