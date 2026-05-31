# AI Voice Call Bot + VoIP Integration Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build a prototype AI voice-call layer for Easiio website/backend chatbot that can support browser voice calls first, then VoIP providers such as Twilio.

**Architecture:** Keep the existing website chatbot backend as the business brain: RAG answers, lead capture, CRM, email notifications, and per-site config stay in `/home/jianl/.hermes/tools/website_chatbot`. Add a separate voice-call adapter layer that converts real-time or near-real-time audio into text, sends text turns into the existing chatbot pipeline, converts responses back to speech, and records safe call metadata into Solo CRM. Provider-specific channels such as Twilio should be adapters, not core logic.

**Tech Stack:** Python stdlib backend where possible, existing `voice_to_text` and `voice_response` tools, existing website chatbot backend, Solo CRM SQLite/MCP, optional Twilio Voice webhooks/Media Streams, browser WebRTC/MediaRecorder prototype, JSON call/session state stores.

---

## Feasibility Summary

Yes, this is possible inside the Hermes framework.

Hermes already has most pieces:

```text
Website/chat widget
  -> backend app.py
  -> RAG / LLM response formatting
  -> Solo CRM lead/customer/activity/deal tracking
  -> email-agent notification
  -> voice_to_text reusable tool
  -> voice_response reusable TTS tool
```

The missing piece is a **voice-call orchestration layer**:

```text
Voice channel audio
  -> STT transcript
  -> chatbot text turn
  -> TTS audio response
  -> play back to caller
  -> CRM call activity + transcript summary
```

Recommended path: build a staged prototype instead of starting with full telephony streaming.

---

## Recommended Architecture

### Core idea

Do not build a second AI bot. Reuse the existing text chatbot as the single business brain.

```text
Browser voice call / Twilio phone call
        ↓
voice_call adapter
        ↓
STT: voice_to_text
        ↓
Existing /api/chat/message equivalent
        ↓
RAG + lead qualification + CRM
        ↓
TTS: voice_response
        ↓
Audio reply to browser or phone caller
```

### New module location

Create a new local module:

```text
/home/jianl/.hermes/tools/voice_call_bot
```

Suggested files:

```text
/home/jianl/.hermes/tools/voice_call_bot/
  README.md
  backend/
    app.py
    call_state.py
    chatbot_bridge.py
    audio_pipeline.py
    providers/
      browser.py
      twilio.py
  tests/
    test_call_state.py
    test_chatbot_bridge.py
    test_twilio_webhooks.py
    test_audio_pipeline.py
```

Why separate from `website_chatbot`:

- Keeps telephony/webhook/provider complexity isolated.
- Allows browser-call and Twilio-call prototypes to share one voice pipeline.
- Avoids destabilizing current website chatbot and WordPress plugin.
- Can later be merged into `website_chatbot` if stable.

---

## Phase 0 — Design Boundaries and Safety

### Objective

Define the safe scope for the prototype.

### Key decisions

1. Keep voice call disabled by default.
2. Store only safe metadata by default:
   - call id
   - site id
   - channel: `browser` or `twilio`
   - caller number masked when applicable
   - transcript text only if configured
   - summary
   - lead/contact/deal/activity IDs
3. Never expose provider credentials to browser JS, WordPress content, logs, or API responses.
4. Put Twilio credentials only in server-side environment:

```bash
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_VOICE_FROM_NUMBER=...
TWILIO_WEBHOOK_SECRET=...
```

5. Start with turn-based voice, not full duplex real-time streaming.

### Acceptance criteria

- Written README explicitly says prototype is disabled by default.
- Secrets are server-side only.
- Browser and Twilio adapters use shared core pipeline.

---

## Phase 1 — Local Voice Call Core, No Twilio Yet

### Objective

Build the call state and text-turn bridge using mock audio/STT/TTS first.

### Files

Create:

```text
/home/jianl/.hermes/tools/voice_call_bot/backend/call_state.py
/home/jianl/.hermes/tools/voice_call_bot/backend/chatbot_bridge.py
/home/jianl/.hermes/tools/voice_call_bot/backend/audio_pipeline.py
/home/jianl/.hermes/tools/voice_call_bot/tests/test_call_state.py
/home/jianl/.hermes/tools/voice_call_bot/tests/test_chatbot_bridge.py
```

### Core data model

```json
{
  "call_id": "call_...",
  "site_id": "ai-solo-company-class",
  "channel": "browser",
  "status": "active",
  "visitor_key": "voice_...",
  "caller": {
    "phone_masked": "+1******1234"
  },
  "turns": [
    {
      "role": "caller",
      "text": "I want a demo for AI agents"
    },
    {
      "role": "assistant",
      "text": "Sure. What is your email?"
    }
  ],
  "crm": {
    "contact_id": null,
    "deal_id": null,
    "activity_id": null
  }
}
```

### API prototype

```text
POST /api/voice-call/session
POST /api/voice-call/turn
POST /api/voice-call/end
GET  /api/voice-call/session?call_id=...
```

### Verification

```bash
cd /home/jianl/.hermes/tools/voice_call_bot
python3 -m py_compile backend/*.py
python3 tests/test_call_state.py -v
python3 tests/test_chatbot_bridge.py -v
```

---

## Phase 2 — Browser Voice Call Prototype

### Objective

Add a browser-call demo so website visitors can press `Call AI Assistant` and speak turn-by-turn.

### User experience

1. Visitor clicks `Call AI Assistant`.
2. Browser asks microphone permission.
3. Visitor records a short message.
4. Backend transcribes the audio.
5. Backend sends transcript into existing chatbot pipeline.
6. Backend generates a TTS reply.
7. Browser plays the reply.
8. Visitor can continue or end call.

### Why turn-based first

Turn-based browser calls are much easier and safer than full real-time calls:

- Works with existing `voice_to_text` file transcription.
- Works with existing `voice_response` TTS output.
- Easier to test.
- Better for prototype demos and class use.

### New endpoints

```text
POST /api/voice-call/browser/audio-turn
```

Request:

```text
multipart/form-data:
  call_id
  site_id
  audio_file
```

Response:

```json
{
  "ok": true,
  "call_id": "call_123",
  "transcript": "I want a demo for AI agents",
  "reply": "Sure. What kind of business is this for?",
  "audio_url": "/api/voice-call/audio/reply_123.mp3",
  "crm": {
    "contact_id": 12,
    "deal_id": 3
  }
}
```

### Frontend prototype

Add separate demo first:

```text
/home/jianl/.hermes/tools/voice_call_bot/demo/browser-call.html
/home/jianl/.hermes/tools/voice_call_bot/demo/browser-call.js
/home/jianl/.hermes/tools/voice_call_bot/demo/browser-call.css
```

Later integrate into chatbot widget as optional config:

```html
<script
  src="/widget.js"
  data-ai-voice-call-enabled="true"
  data-ai-voice-call-label="Call AI Assistant">
</script>
```

### Verification

- Static JS check.
- Backend unit tests with mock STT/TTS.
- HTTP smoke using generated test audio or mock transcript.
- Confirm CRM activity created as `kind=call`.

---

## Phase 3 — CRM and Admin Console Integration

### Objective

Record voice calls as CRM activities and expose safe admin settings.

### CRM behavior

For each call:

- Create or update visitor session.
- If caller provides email/phone/name, create/update contact.
- Add CRM activity:

```text
kind: call
body: transcript summary + safe call metadata
```

- Optional follow-up task if call intent is high.

### Admin settings

Extend existing chatbot admin customizer later with safe public settings:

```json
{
  "voice_call_enabled": false,
  "voice_call_label": "Call AI Assistant",
  "voice_call_channel": "browser",
  "voice_call_record_transcript": true,
  "voice_call_consent_text": "This AI assistant may transcribe your voice to answer your question."
}
```

Do not expose:

- Twilio auth token
- provider keys
- cache directories
- raw webhook secrets

### Verification

Run existing chatbot tests plus new voice-call tests:

```bash
cd /home/jianl/.hermes/tools/website_chatbot
python3 tests/test_backend.py -v
node tests/admin_customizer_static.test.js
```

```bash
cd /home/jianl/.hermes/tools/voice_call_bot
python3 tests/test_*.py -v
```

---

## Phase 4 — Twilio Voice Webhook Prototype, Non-Streaming

### Objective

Support phone calls through Twilio using webhook/TwiML gather first.

### Recommended first Twilio approach

Use Twilio `<Gather input="speech">` for turn-based speech recognition.

Flow:

```text
Caller phones Twilio number
  -> Twilio POST /api/voice-call/twilio/incoming
  -> backend returns TwiML greeting + speech gather
  -> caller speaks
  -> Twilio POST /api/voice-call/twilio/gather with SpeechResult
  -> backend sends text to chatbot bridge
  -> backend returns TwiML <Say> reply + next gather
  -> caller hangs up
  -> Twilio POST /api/voice-call/twilio/status
  -> backend records final CRM activity
```

### Why TwiML Gather first

- Much simpler than WebSocket Media Streams.
- Twilio handles telephony audio and speech recognition.
- Easy to prototype and test with HTTP requests.
- Good enough for a first phone-call AI assistant.

### Endpoints

```text
POST /api/voice-call/twilio/incoming
POST /api/voice-call/twilio/gather
POST /api/voice-call/twilio/status
```

### Example TwiML response

```xml
<Response>
  <Gather input="speech" action="/api/voice-call/twilio/gather" method="POST" speechTimeout="auto">
    <Say voice="alice">Hello, this is the Easiio AI assistant. How can I help?</Say>
  </Gather>
  <Say>I did not hear anything. Please call again later.</Say>
</Response>
```

### Security

Validate Twilio request signatures before trusting webhooks.

Server env only:

```bash
TWILIO_AUTH_TOKEN=...
```

Do not log full phone numbers unless explicitly enabled. Prefer masked phone display.

### Local development requirement

Twilio needs a public HTTPS URL. Options:

1. Use Hermes Proxy if it supports external POST webhooks reliably.
2. Use ngrok/cloudflared for the prototype.
3. Deploy the voice-call backend to a small HTTPS server later.

### Verification

- Unit-test TwiML generation.
- Unit-test webhook parsing.
- Unit-test request signature validation with known fixtures.
- Manual Twilio sandbox call after endpoint is public HTTPS.

---

## Phase 5 — Twilio Media Streams / Real-Time Voice, Later

### Objective

Add low-latency streaming voice only after the turn-based prototype works.

### Flow

```text
Twilio phone audio stream
  -> WebSocket /api/voice-call/twilio/stream
  -> streaming STT
  -> LLM/chatbot response
  -> streaming TTS
  -> Twilio audio playback
```

### Additional requirements

This phase likely requires more dependencies and infrastructure:

- WebSocket server support.
- Streaming STT provider.
- Streaming TTS provider.
- Latency monitoring.
- Barge-in / interruption handling.
- Call recording consent rules.

### Recommendation

Do not start here. Build Phases 1–4 first.

---

## Phase 6 — WordPress and Website Integration

### Objective

Let WordPress/site owners enable AI voice call from settings.

### WordPress plugin settings

Add conservative settings to:

```text
/home/jianl/.hermes/tools/website_chatbot/wordpress-plugin/easiio-chatbot/easiio-chatbot.php
```

Public options:

```text
Enable AI voice call
Voice call button label
Voice call consent text
Voice call channel: browser only / phone callback later
```

Injected attributes:

```html
data-voice-call-enabled="false"
data-voice-call-label="Call AI Assistant"
data-voice-call-consent-text="This AI assistant may transcribe your voice."
```

### Verification

```bash
cd /home/jianl/.hermes/tools/website_chatbot
node tests/wp_plugin_static.test.js
python3 -m py_compile backend/app.py
```

Package ZIP after review:

```bash
python3 - <<'PY'
from pathlib import Path
import zipfile
root = Path('/home/jianl/.hermes/tools/website_chatbot')
plugin_dir = root / 'wordpress-plugin' / 'easiio-chatbot'
out = root / 'dist' / 'easiio-chatbot-wordpress-plugin.zip'
out.parent.mkdir(parents=True, exist_ok=True)
if out.exists():
    out.unlink()
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in plugin_dir.rglob('*'):
        if path.is_file() and path.name != '.DS_Store' and '__MACOSX' not in path.parts:
            z.write(path, path.relative_to(plugin_dir.parent).as_posix())
PY
```

---

## Implementation Order

Recommended staged order:

1. `voice_call_bot` local call-state core.
2. Mock STT/TTS text-turn tests.
3. Browser turn-based voice-call demo.
4. CRM call activity integration.
5. Admin settings, disabled by default.
6. Twilio TwiML Gather webhook prototype.
7. WordPress plugin settings.
8. Optional callback flow.
9. Optional real-time Twilio Media Streams.

---

## MVP Acceptance Criteria

The first usable prototype is complete when:

1. A visitor can click `Call AI Assistant` in a browser demo.
2. The visitor records a spoken question.
3. Backend transcribes speech to text.
4. Existing chatbot/RAG answers the question.
5. Backend generates a spoken reply.
6. Browser plays the reply.
7. The call turn is saved as a CRM call activity.
8. No provider secrets are exposed to browser/API responses.
9. Feature is disabled by default in production embed/plugin settings.

Twilio prototype is complete when:

1. Twilio incoming call webhook returns valid TwiML.
2. Caller speech result is processed through the chatbot bridge.
3. Twilio reads the answer back using `<Say>`.
4. Repeated turns work until hangup.
5. Status callback records a final call activity.
6. Twilio signatures are validated.
7. Phone numbers are masked in logs/API responses unless explicitly allowed.

---

## Testing Strategy

### Unit tests

- call state create/update/end
- phone masking
- transcript sanitization
- chatbot bridge request/response mapping
- CRM activity creation behavior
- TwiML generation
- Twilio request validation

### Static checks

```bash
python3 -m py_compile /home/jianl/.hermes/tools/voice_call_bot/backend/*.py
```

### Integration smoke

Browser prototype:

```bash
VOICE_TO_TEXT_PROVIDER=mock \
VOICE_RESPONSE_PROVIDER=mock \
python3 /home/jianl/.hermes/tools/voice_call_bot/backend/app.py --host 127.0.0.1 --port 8120
```

Then POST a mock turn and expect:

```json
{
  "ok": true,
  "transcript": "...",
  "reply": "...",
  "audio_url": "..."
}
```

Twilio prototype:

- Use local HTTP tests for TwiML.
- Use public HTTPS only for real call testing.

---

## Risks and Mitigations

### Risk: Real-time voice is complex

Mitigation: use turn-based browser and Twilio Gather first.

### Risk: Provider secrets leak

Mitigation: env-only credentials, sanitized API responses, static tests rejecting secret keys in public JS/plugin output.

### Risk: Audio files accumulate

Mitigation: cache with TTL, filename allowlist, cleanup job, no raw audio retention by default.

### Risk: Bad phone UX from slow response

Mitigation: keep first phone prototype simple; use short prompts; later add streaming if needed.

### Risk: Legal/consent requirements

Mitigation: add configurable consent text, do not record raw audio by default, store transcript only when enabled.

---

## Recommended Next Immediate Task

Implement **Phase 1 + Phase 2 browser prototype** first.

This gives a visible demo without requiring Twilio setup:

```text
Visitor opens website
  -> clicks Call AI Assistant
  -> speaks a question
  -> hears AI answer
  -> call saved into CRM
```

After that works, implement Twilio Gather as the first VoIP adapter.
