---
name: website-chatbot-solo-crm
description: Build and extend Jian's Easiio website chatbot integrated with the local Solo CRM MCP/SQLite tool. Use when working on the website chatbot widget, backend API bridge, WordPress footer plugin, or Next.js integration.
---

# Website Chatbot + Solo CRM

## Context

Project path:

```bash
/home/jianl/.hermes/tools/website_chatbot
```

Related CRM path:

```bash
/home/jianl/.hermes/tools/solo_crm
```

The browser chatbot must **not** call MCP directly. The architecture is:

```text
WordPress / Next.js page
  -> embedded browser widget script
  -> backend HTTP API
  -> Solo CRM core / MCP bridge
  -> SQLite CRM database
```

## Important files

```text
/home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.js
/home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.css
/home/jianl/.hermes/tools/website_chatbot/widget/widget.js
/home/jianl/.hermes/tools/website_chatbot/widget/widget.css
/home/jianl/.hermes/tools/website_chatbot/widget/demo.html
/home/jianl/.hermes/tools/website_chatbot/backend/app.py
/home/jianl/.hermes/tools/website_chatbot/backend/site_gateway.py
/home/jianl/.hermes/tools/website_chatbot/wordpress-plugin/easiio-chatbot/easiio-chatbot.php
/home/jianl/.hermes/tools/website_chatbot/wordpress-plugin/easiio-chatbot/README.md
/home/jianl/.hermes/tools/website_chatbot/dist/easiio-chatbot-wordpress-plugin.zip
/home/jianl/.hermes/tools/website_chatbot/tests/widget_static.test.js
/home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py
/home/jianl/.hermes/tools/website_chatbot/tests/wp_plugin_static.test.js
/home/jianl/.hermes/tools/website_chatbot/CHATBOT_CRM_IMPLEMENTATION_PLAN.md
/home/jianl/.hermes/tools/website_chatbot/AI_CHAT_AGENT_UI_NOTES.md
```

## Existing implementation

### Widget

The widget is a direct DOM embeddable script, not iframe-first. It supports:

- `window.EasiioChatbot` global controller
- floating launcher/capsule
- unread badge
- pulse animation
- proactive greeting bubble
- popup chat panel
- quick actions
- optional voice playback for bot replies using `data-voice-enabled="true"`; the widget renders a `Listen` button, calls `POST /api/chat/voice`, resolves returned relative `audio_url` through the configured `data-api-base`, and plays it with browser `Audio`. Keep disabled by default on production/WordPress until the backend TTS provider is reviewed.
- optional browser voice input using `data-voice-input-enabled="true"`; the widget renders a microphone button, uses browser `SpeechRecognition` / `webkitSpeechRecognition` when available, inserts the final transcript into the composer, and submits through the normal `/api/chat/message` text flow. Keep disabled by default until microphone UX/consent is reviewed.
- lead capture form code that can be dismissed without blocking chat
- configurable lead form fields: default fields are `name`, `email`, `company`, and required `message` textarea; phone is not shown by default. Widget supports embedded JSON via `data-lead-form-config` and backend-loaded per-site config via `/api/chat/form-config`.
- lead capture popups from normal typed chat are currently disabled by default; automatic widget prompts only run if `data-lead-forms-enabled="true"` is explicitly set and backend lead forms are enabled
- quick-action buttons (`Book demo`, `Pricing`, `Contact sales`) are an exception: clicking them should immediately open the lead form via `onQuickAction(...); showLeadForm(message, 'quick_action')`, while ordinary factual questions keep answering without form interruption. Quick actions must show the dialog even when cached visitor email/phone exists, so `showLeadForm()` should only apply `hasContactInfo()` blocking when `reason !== 'quick_action'`. If the visitor dismisses the form, the next quick-action click must reopen it by clearing `form.dataset.dismissedAt`, setting `form.hidden = false`, and removing the `hidden` attribute.
- mock mode via `data-api-base="mock"`
- remembers visitor contact fields and recent conversation messages in browser `localStorage` using a per-website key
- sends visible page text as `page_context.content` so each website can build its own lightweight RAG index
- optional per-site RAG admin UI enabled with `data-rag-admin="true"`; keep disabled for public visitors unless the page is protected/admin-only

### RAG answer-quality lesson

For AI Solo Company chatbot questions such as “做市场/Marketing 的功能有哪些能力”, do not let the fallback return a raw hero/course chunk. The backend should first try the LLM formatter, then use question-specific deterministic fallback helpers (for example marketing capability synthesis) that answer directly and concisely from retrieved keywords. If retrieval scores are low but semantically relevant for a capability question, use a lower threshold for that intent and pass the broader selected context to the fallback instead of only the top chunk. Regression test location: `/home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py` with `test_message_uses_concise_marketing_capability_fallback_when_llm_unavailable`.

### Voice-call demo no-op debugging

If a public demo voice-call button appears to do nothing, first separate extension noise (`contentscript.js`, `inpage.js`, MetaMask, ObjectMultiplex) from widget errors. Avoid inline `onclick="window.EasiioChatbot..."` plus `async` widget scripts for interaction-critical demo CTAs; use widget-managed data attributes (`data-easiio-chatbot-open`, `data-easiio-chatbot-start-voice-call`) and delegated listeners (`attachDocumentShortcuts`, `onPanelClick`). Dynamic panel buttons should route `[data-voice-call-start]`, `[data-voice-call-record]`, and `[data-voice-call-end]` through panel delegation. Page snapshots must not assume `innerText`; use `clone.innerText || clone.textContent || ''`. Cache-bust live demos after fixes and verify live HTML/JS markers with `curl`, plus `node --check widget/widget.js`, `node tests/widget_static.test.js`, chatbot backend tests, voice_call_bot tests, live `/api/voice-call/session`, and a changed-file secret scan.

Public controller methods include:

```js
window.EasiioChatbot.set(...)
window.EasiioChatbot.show()
window.EasiioChatbot.open()
window.EasiioChatbot.startVoiceCall()
window.EasiioChatbot.minimize()
window.EasiioChatbot.openKnowledge()
window.EasiioChatbot.closeKnowledge()
window.EasiioChatbot.loadRagContentList()
window.EasiioChatbot.close()
```

### Admin customizer module

Reusable backend-console assets:

```text
/home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.js
/home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.css
```

Embed on a protected/admin-only website backend console with:

```html
<link rel="stylesheet" href="chatbot-admin/chatbot-customizer.css" />
<div id="site-chatbot-customizer-root"></div>
<script
  src="chatbot-admin/chatbot-customizer.js"
  data-easiio-chatbot-customizer
  data-api-base="."
  data-site-id="stable-site-id"
  data-root-selector="#site-chatbot-customizer-root"></script>
```

The module manages the lead form, safe widget voice playback/input settings, customer-inquiry notification email settings, and manual chatbot knowledge for the selected `site_id` using `GET/POST /api/chat/form-config`, `GET/POST /api/email-agent/config`, `GET/POST /api/rag/content`, and `POST /api/rag/content/delete`. Voice settings are stored under `form_config.widget_config` with safe public keys only (`voice_enabled`, `voice_label`, `voice_autoplay`, `voice`, `voice_format`, `voice_input_enabled`, `voice_input_label`, `voice_input_language`); TTS providers/API keys/cache paths and speech provider secrets remain server-side only. Voice playback and voice input stay disabled by default. Notification email settings expose only safe per-site configuration such as enabled state, provider name, recipients, sender display fields, and templates; Brevo/SMTP/API credentials remain server-side only. It uses same-origin credentials by default and should only be embedded in a protected/backend/admin console. For the AI Solo site, the deployed copy is:

```text
/mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.js
/mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.css
```

When fixing admin customizer layout/overflow issues, patch the reusable CSS first, then copy it to the deployed site copy. The lead form editor can overflow narrow admin columns if field rows use a fixed multi-column grid; prefer a wrapping grid such as `grid-template-columns: repeat(auto-fit, minmax(140px, 1fr))`, plus containment rules on `.easiio-chatbot-customizer` and card/grid children: `box-sizing: border-box`, `min-width: 0`, `max-width: 100%`, and appropriate `overflow` handling. Add an earlier breakpoint around `@media (max-width: 1200px)` to stack editor and preview columns before they overlap. Extend `/home/jianl/.hermes/tools/website_chatbot/tests/admin_customizer_static.test.js` with CSS marker assertions, then verify the reusable and deployed CSS both contain the markers.

`site_gateway.py` must proxy `/api/rag/*` as well as `/api/chat/*` to the chatbot backend when this module is used behind Hermes Proxy.

### Backend

The backend is dependency-free stdlib Python HTTP server at:

```bash
/home/jianl/.hermes/tools/website_chatbot/backend/app.py
```

Endpoints:

```text
GET  /health
POST /api/chat/session
POST /api/chat/message
POST /api/chat/lead
POST /api/chat/voice
GET  /api/chat/voice/<audio_id>
GET  /api/chat/form-config?site_id=...
POST /api/chat/form-config
GET  /api/email-agent/config?site_id=...
POST /api/email-agent/config
GET  /api/rag/content?site_id=...
POST /api/rag/content
POST /api/rag/content/delete
```

`POST /api/chat/voice` uses the reusable voice response module at `/home/jianl/.hermes/tools/voice_response` and returns safe cached audio metadata such as `audio_id` and relative `audio_url`; it must not expose provider API keys or raw cache paths. Test with `VOICE_RESPONSE_PROVIDER=mock` and a temp `EASIIO_CHATBOT_VOICE_CACHE_DIR` unless intentionally doing a cloud TTS smoke. `GET /api/chat/voice/<audio_id>` serves only filename-pattern-matched files under the configured voice cache directory.

It handles session creation, page/visitor tracking, per-site website-content RAG retrieval plus optional OpenAI-compatible LLM answer formatting, basic intent extraction, email/phone extraction, lead scoring, CRM contact/company/deal creation or updates, activity logging, and optional email-agent automation. The widget sends a visible-text page snapshot in `page_context.content`; the backend chunks/indexes it by `site_id`, retrieves only relevant chunks, asks an LLM to format a concise answer when `EASIIO_CHATBOT_LLM_API_KEY` or `OPENAI_API_KEY` is configured, and otherwise uses a concise extractive fallback instead of dumping full page content.

Enhanced RAG Phase 1 is implemented in `backend/app.py`: section-aware chunks with summaries/metadata/neighbor links, deterministic query intent + expansion, optional HyDE retrieval queries, local hybrid candidate scoring, reranking, neighbor expansion that avoids unrelated lesson chunks, source/confidence metadata, and verification that rejects unsupported LLM numbers/details before falling back to extractive evidence. Key functions: `build_enhanced_rag_chunks`, `build_rag_query_plan`, `call_llm_hyde_queries`, `retrieve_rag_candidates`, `rerank_rag_candidates`, `expand_rag_context`, `format_rag_context`, and `verify_grounded_answer`. Feature flags include `EASIIO_CHATBOT_RAG_MODE`, `EASIIO_CHATBOT_RAG_DEBUG`, `EASIIO_CHATBOT_RAG_HYDE_ENABLED`, `EASIIO_CHATBOT_RAG_VERIFY_ENABLED`, `EASIIO_CHATBOT_RAG_MAX_CANDIDATES`, and `EASIIO_CHATBOT_RAG_MAX_SELECTED`. HyDE is retrieval-only and must never be cited as evidence.

Enhanced RAG Phase 2 adds the operations layer: admin debug endpoint/UI, answer-quality logs, helpful/not-helpful feedback, and golden Q&A eval runner. Backend endpoints are `POST /api/rag/debug`, `GET /api/rag/answer-log?site_id=...`, `POST /api/rag/feedback`, `GET /api/rag/feedback?site_id=...`, and `POST /api/rag/eval`. Stores default to `/home/jianl/.hermes/tools/website_chatbot/data/rag_answer_log.json` and `/home/jianl/.hermes/tools/website_chatbot/data/rag_feedback.json`, overridable by `EASIIO_CHATBOT_RAG_ANSWER_LOG` and `EASIIO_CHATBOT_RAG_FEEDBACK_STORE`. Logs/feedback must mask emails and phone numbers, remain site-specific, and never store secrets. The widget renders `Was this helpful?` controls for website_rag answers, and the reusable admin customizer has a RAG debug + evaluation card. Phase 2 plan/docs: `/home/jianl/.hermes/tools/website_chatbot/docs/plans/2026-05-27-enhanced-rag-phase2-admin-debug-eval.md`.

Enhanced RAG Phase 3 adds multi-source knowledge sync. Backend endpoints are `GET /api/rag/sources?site_id=...` and `POST /api/rag/sync-sources` with `confirm_sync: true`. It syncs published public `rag_enabled` docs from Easiio Docs (`EASIIO_DOCS_DB`, default `/home/jianl/.hermes/tools/easiio_docs_module/data/easiio_docs.db`) and published `rag_enabled` pages from Website Wiki (`EASIIO_WIKI_DB`, default `/home/jianl/.hermes/tools/website_wiki_module/data/website_wiki.db`) into the chatbot manual RAG store, preserving manual items and replacing only known synced prefixes (`easiio-docs:`, `easiio-wiki:`, `wordpress:`, `upload:`). Sync summaries are stored in `EASIIO_CHATBOT_RAG_SYNC_LOG` (default `/home/jianl/.hermes/tools/website_chatbot/data/rag_sync_log.json`) with PII masking. The admin customizer has a `RAG source sync` card with Docs/Wiki source status and sync button. Phase 3 plan/docs: `/home/jianl/.hermes/tools/website_chatbot/docs/plans/2026-05-27-enhanced-rag-phase3-multisource-sync.md`.

Enhanced RAG Phase 4 adds persisted WordPress/upload source staging. Backend endpoints are `GET /api/rag/source-items?site_id=...&source=wordpress|upload`, `POST /api/rag/source-items`, and `POST /api/rag/source-items/delete`. The source store defaults to `/home/jianl/.hermes/tools/website_chatbot/data/rag_external_sources.json`, overridable with `EASIIO_CHATBOT_RAG_EXTERNAL_SOURCES`. WordPress items sync only when `status` is `publish`/`published`, `visibility` is public/blank, `rag_enabled` is not false, `sync_to_rag` is not false, and content is non-empty. Upload items sync only when `status` is `published`/`publish`/`ready`/`active` with the same visibility and opt-in rules. Admin customizer now has WordPress and Uploaded document JSON import forms plus source checkboxes. Phase 4 plan/docs: `/home/jianl/.hermes/tools/website_chatbot/docs/plans/2026-05-27-enhanced-rag-phase4-wordpress-upload-sync.md`.

Enhanced RAG Phase 5 adds direct ingestion helpers on top of Phase 4 staging. Backend endpoints are `POST /api/rag/wordpress/pull` and `POST /api/rag/upload/extract`. WordPress pull requires `confirm_pull: true`, accepts only public http(s) base URLs, pulls public `/wp-json/wp/v2/pages|posts`, converts rendered HTML to text, and may use an optional server-side `auth_env` variable name for Basic Auth without returning the env name/value or secrets. Upload extraction requires `confirm_extract: true`, accepts base64 document content, stages extracted text as `upload`, supports TXT/MD/HTML/DOCX dependency-free, and best-effort PDF text extraction if PyMuPDF/fitz is installed; scanned PDFs still need separate OCR. Admin customizer has `WordPress REST pull` and `Document extraction` forms. Phase 5 plan/docs: `/home/jianl/.hermes/tools/website_chatbot/docs/plans/2026-05-27-enhanced-rag-phase5-wordpress-rest-document-extraction.md`.

Enhanced RAG Phase 6 adds review-first source operations. Backend endpoints are `POST /api/rag/sync-preview`, `GET /api/rag/review?site_id=...`, and `POST /api/rag/rollback`; `POST /api/rag/sync-sources` now returns a public `rollback_id` and records before/after snapshots in `EASIIO_CHATBOT_RAG_SYNC_LOG`. Review statuses are `new`, `changed`, `unchanged`, and `deleted_upstream`; changed/deleted items include diff previews. `GET /api/rag/sources` includes `review_summary` for source freshness dashboards. Rollback requires `confirm_rollback: true`, is scoped by `site_id`, and must not expose raw approver contact details or secrets. Admin customizer has `Preview changes`, `Load review queue`, `Rollback last sync`, and a `RAG review queue` panel. Phase 6 plan/docs: `/home/jianl/.hermes/tools/website_chatbot/docs/plans/2026-05-27-enhanced-rag-phase6-review-rollback-operations.md`.

Enhanced RAG Phase 7 adds scheduled refresh and admin notifications on top of Phase 6. Backend endpoints are `GET/POST /api/rag/refresh-schedule`, `GET /api/rag/refresh-due`, `POST /api/rag/run-scheduled-refresh`, `GET /api/rag/notifications`, and `POST /api/rag/notifications/read`. Stores default to `EASIIO_CHATBOT_RAG_REFRESH_SCHEDULE=/home/jianl/.hermes/tools/website_chatbot/data/rag_refresh_schedule.json` and `EASIIO_CHATBOT_RAG_NOTIFICATIONS=/home/jianl/.hermes/tools/website_chatbot/data/rag_notifications.json`. `run-scheduled-refresh` builds the Phase 6 review summary, creates safe notifications when new/changed/deleted items are found, can dry-run as `preview_only`, and can auto-sync when `auto_sync` is true while preserving rollback IDs. Notification API responses must not expose raw recipient lists, provider secrets, or email outbox paths. Admin customizer has `RAG schedule + notifications`, save schedule, run scheduled refresh now, check due sites, load notifications, and mark read controls. Phase 7 plan/docs: `/home/jianl/.hermes/tools/website_chatbot/docs/plans/2026-05-27-enhanced-rag-phase7-scheduled-refresh-notifications.md`.

Email-agent configuration is isolated by `site_id` and stored by default at:

```text
/home/jianl/.hermes/tools/website_chatbot/data/email_agent_config.json
```

Use `GET /api/email-agent/config?site_id=...` to fetch the sanitized effective config and `POST /api/email-agent/config` with `{site_id, email_config: {...}}` to save it. The AI Solo gateway protects `/api/email-agent/*` as admin-only, so admin consoles can manage recipients and templates without exposing this control to public visitors. The email agent runs when a **new** CRM contact is created through `/api/chat/lead` or conversational `/api/chat/message`; it does not resend for repeat submissions from an existing email. It can send:

- a welcome email to the new user
- an owner/manager notification to one or more configured recipient emails

Supported template placeholders include `{name}`, `{email}`, `{phone}`, `{company}`, `{site_id}`, `{message}`, `{page_url}`, `{lead_score}`, `{contact_id}`, and `{deal_id}`. Brevo is the preferred production email provider. Configure it server-side only in `~/.hermes/.env` or the protected service env — never in browser JS:

```bash
EASIIO_EMAIL_PROVIDER=brevo
EASIIO_BREVO_API_KEY=...        # Brevo SMTP & API > API Keys
EASIIO_EMAIL_FROM=hello@example.com  # must be a verified Brevo sender
EASIIO_EMAIL_FROM_NAME="Easiio Website Assistant"
```

The backend sends through Brevo's transactional email API (`POST https://api.brevo.com/v3/smtp/email`) when `EASIIO_BREVO_API_KEY` is present. Normal `/api/chat/message` calls must not become CRM lead captures just because the widget sends cached `visitor.email`/`visitor.phone` after a previous lead-form submission; only contact info typed in the current message, or an explicit `/api/chat/lead` form submission, should write lead CRM activities. This preserves RAG/LLM answers for factual follow-up questions such as “how many classes you have?” after the visitor already submitted contact info. Legacy SMTP fallback is still supported server-side only:

```bash
EASIIO_EMAIL_PROVIDER=smtp
EASIIO_SMTP_HOST=...
EASIIO_SMTP_PORT=587
EASIIO_SMTP_USERNAME=...
EASIIO_SMTP_PASSWORD=...
EASIIO_SMTP_STARTTLS=true
EASIIO_EMAIL_FROM=hello@example.com
EASIIO_EMAIL_FROM_NAME="Easiio Website Assistant"
```

If Brevo/SMTP is not configured, the backend writes sanitized email records to the JSON outbox directory instead of failing the lead flow. Never print Brevo keys, SMTP credentials, or `.env` values.

When troubleshooting “Brevo key updated but no email received”, check these in order before changing code:

1. Confirm the running chatbot backend process has actually loaded the new env without printing secrets:
   ```bash
   ss -ltnp | grep -E ':(8099|8020)\\b' || true
   python3 - <<'PY'
   import os
   pid = int(os.environ.get('CHATBOT_PID', '0'))  # or use the PID from ss/process list
   raw = open(f'/proc/{pid}/environ','rb').read().split(b'\\0')
   env = dict(item.split(b'=',1) for item in raw if b'=' in item)
   for key in ['EASIIO_EMAIL_PROVIDER','EASIIO_BREVO_API_KEY','EASIIO_EMAIL_FROM','EASIIO_EMAIL_FROM_NAME']:
       value = env.get(key.encode())
       if value is None:
           print(key, 'MISSING')
       elif b'KEY' in key.encode():
           print(key, 'PRESENT len=' + str(len(value)))
       else:
           print(key, 'PRESENT')
   PY
   ```
   If keys are missing, restart `backend/app.py`; the process reads `~/.hermes/.env` at startup, not dynamically after every edit.
2. Fetch the sanitized per-site config and confirm `enabled: true`, `provider: brevo`, owner recipients, and a verified sender domain:
   ```text
   GET http://127.0.0.1:8099/api/email-agent/config?site_id=<site_id>
   ```
   Saving the Brevo API key alone is not enough; each site’s Email Agent can still be disabled in `/home/jianl/.hermes/tools/website_chatbot/data/email_agent_config.json`.
3. Reproduce with a brand-new test email address. The Email Agent intentionally sends welcome/owner notifications only when a new CRM contact is created; repeat submissions with an existing email do not resend.
4. Inspect the `email_agent` object in the `/api/chat/lead` or `/api/chat/message` response. A working Brevo send returns results like `provider: brevo`, `status: sent`, and Brevo `response_status: 201`. If Brevo is not configured, expect JSON outbox fallback instead of an exception.

Lead form configuration is isolated by `site_id` and stored by default at:

```text
/home/jianl/.hermes/tools/website_chatbot/data/form_config.json
```

Use `GET /api/chat/form-config?site_id=...` to fetch the effective config and `POST /api/chat/form-config` with `{site_id, form_config: {title, help_text, submit_label, fields}}` to save it. Allowed field types are `text`, `email`, and `textarea`; invalid names/types are sanitized out. The default config intentionally removes phone and adds a required `message` textarea.

Manual RAG content is also isolated by `site_id` and stored by default at:

```text
/home/jianl/.hermes/tools/website_chatbot/data/rag_content.json
```

Override the store location with:

```bash
EASIIO_CHATBOT_RAG_STORE=/path/to/rag_content.json
```

Use `POST /api/rag/content` to add or update `{site_id,title,url,content,content_id?}`, `GET /api/rag/content?site_id=...` to list one site's manual knowledge, and `POST /api/rag/content/delete` with `{site_id,content_id}` to delete only that site's item. Tests should verify that content for one `site_id` cannot answer questions for another `site_id`.

#Optional LLM answer formatting environment variables:

```bash
# OpenAI-compatible defaults
EASIIO_CHATBOT_LLM_API_KEY=...
EASIIO_CHATBOT_LLM_BASE_URL=https://api.openai.com/v1
EASIIO_CHATBOT_LLM_MODEL=gpt-4o-mini

# Also accepted as fallbacks
OPENAI_API_KEY=...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

The backend loads `~/.hermes/.env` automatically and never exposes these values to the browser. If no key is configured or the LLM call fails, it returns a short extractive answer from the retrieved chunks. When configuring the LLM formatter, make sure `EASIIO_CHATBOT_LLM_API_KEY` is an actual OpenAI-compatible LLM key for the configured `EASIIO_CHATBOT_LLM_BASE_URL`; do not accidentally reuse the Brevo email key (`xkeysib-...`) because OpenAI will return `401 invalid_api_key` and answers will keep falling back to `answer_source: "website_rag"`. Keep Brevo only in `EASIIO_BREVO_API_KEY`. Quote any `.env` values containing spaces, for example `EASIIO_EMAIL_FROM_NAME="Easiio Website Assistant"`; otherwise `source ~/.hermes/.env` may print errors like `Website: command not found` and the service environment can be partially wrong. The `.env` file is a protected credential file, so Hermes patch/write tools may refuse to edit it; ask Jian to edit it manually instead of trying to bypass protection. For backend restarts, prefer `python3 /home/jianl/.hermes/tools/website_chatbot/backend/app.py --host 127.0.0.1 --port 8099` because `app.py` loads `~/.hermes/.env` itself, avoiding shell `source` parse errors from unrelated `.env` lines. After restart, verify the running process environment from `/proc/<pid>/environ` without printing key values, then make a tiny direct OpenAI-compatible `/chat/completions` call using the process env (`Reply with exactly: ok`) before blaming RAG formatting. A successful direct call should return HTTP 200; then `/api/rag/debug` should show `llm_status.configured: true` and answer objects should use `answer_source: "website_rag_llm"`.

When troubleshooting vague/non-specific chatbot answers, first check whether the running backend process actually has LLM env loaded without printing secrets:

```bash
pid=$(ss -ltnp | sed -n 's/.*127.0.0.1:8099.*pid=\([0-9]*\).*/\1/p' | head -1)
python3 - <<'PY'
from pathlib import Path
import os
pid = os.environ.get('CHATBOT_PID') or ''
if not pid:
    raise SystemExit('set CHATBOT_PID to the backend pid')
raw = Path(f'/proc/{pid}/environ').read_bytes().split(b'\0')
env = dict(item.split(b'=', 1) for item in raw if b'=' in item)
for key in [b'EASIIO_CHATBOT_LLM_API_KEY', b'OPENAI_API_KEY', b'EASIIO_CHATBOT_LLM_BASE_URL', b'OPENAI_BASE_URL', b'EASIIO_CHATBOT_LLM_MODEL', b'OPENAI_MODEL']:
    value = env.get(key)
    if value is None:
        print(key.decode(), 'MISSING')
    elif b'KEY' in key:
        print(key.decode(), 'PRESENT len=' + str(len(value)))
    else:
        print(key.decode(), 'PRESENT')
PY
```

Then call `/api/rag/debug` for the exact `site_id` and question. If the answer object reports `answer_source: "website_rag"`, the response is deterministic fallback/extractive. If it reports `answer_source: "website_rag_llm"`, the retrieved chunks and user question were sent to the OpenAI-compatible chat API through `call_llm_answer_formatter(question, formatted_context, language)`. The prompt includes both `Question: ...` and `Website sources: ...`. The fallback can still retrieve the right chunk but sound generic; fix either by loading/restarting with LLM env or by improving `concise_extractive_answer()` with a regression test for question-specific wording.

When doing public live-smoke checks through Hermes Proxy, parse chatbot message responses using the `reply` field, not `answer`; `/api/chat/message` usually does not include an `ok` boolean. A passing smoke should assert a non-empty `reply`, `lead_captured: false` for factual questions, `show_lead_form: false` unless intentionally testing lead capture, and `answer_source` such as `website_rag` or `website_rag_llm`. If a specific factual smoke question fails because the current RAG corpus does not contain that fact (for example asking about SEO lessons when no lesson content is indexed), do not treat service reachability as failed; switch to a generic known-covered question for live smoke and separately log the content/retrieval gap.

## Optional external CRM connectors

The `hermes_solo_company` repo now includes outbound CRM connector support under `modules/solo_crm/connectors/`: Phase 1 HubSpot was committed at `0f5265ffd965d4326b626ddf028fec97918763b2` (`feat: add HubSpot CRM connector`), Phase 2 Google Sheets was committed at `ee0a62c90cdb3f568f10ea56fe364dabd4720c4f` (`feat: add Google Sheets CRM connector`), and Phase 3 admin connector configuration was committed at `3431edc8a0c567bbc7dc3a2c02cddddd4356966b` (`feat: add CRM connector admin configuration`). Phase 4 sync log/retry queue was committed at `b23c53a44667cc79c5cd0e137ee33af4bf99dcfa` (`feat: add CRM sync log retry queue`). Keep Solo CRM as the local source of truth; external CRM sync must be optional and non-blocking.

Key files in the source-only repo:

```text
/home/jianl/github-work/hermes_solo_company/modules/solo_crm/connectors/base.py
/home/jianl/github-work/hermes_solo_company/modules/solo_crm/connectors/config.py
/home/jianl/github-work/hermes_solo_company/modules/solo_crm/connectors/google_sheets.py
/home/jianl/github-work/hermes_solo_company/modules/solo_crm/connectors/hubspot.py
/home/jianl/github-work/hermes_solo_company/modules/solo_crm/connectors/sync.py
/home/jianl/github-work/hermes_solo_company/docs/plans/2026-05-23-crm-connectors.md
```

Protected connector config defaults to `~/.hermes/tools/solo_crm/data/crm_connectors.json` and can be overridden with `SOLO_CRM_CONNECTORS_CONFIG`. Store only env var names in config, such as `token_env: HUBSPOT_PRIVATE_APP_TOKEN` or `webhook_url_env: GOOGLE_SHEETS_LEADS_WEBHOOK_URL`; raw CRM API tokens/webhook URLs must stay in server-side environment and never appear in browser JS, WordPress plugin output, logs, tests, commits, or API responses. Chatbot lead capture calls `sync_contact_to_enabled_crms(...)` after local contact/deal/activity creation; if HubSpot, Google Sheets, or another provider fails, local lead capture still returns success and may include sanitized `crm_sync` status only when sync is enabled. Phase 3 also exposes admin-safe chatbot backend endpoints `GET/POST /api/crm-connectors/config` and adds a CRM connectors card to `admin/chatbot-customizer.js`; the AI Solo gateway must protect `/api/crm-connectors/*` as admin-only using the same pattern as `/api/email-agent/*`. Phase 4 adds `connectors/sync_log.py`, default sync log path `~/.hermes/tools/solo_crm/data/crm_sync_log.json` overridable with `SOLO_CRM_SYNC_LOG`, backend endpoints `GET /api/crm-connectors/sync-log` and `POST /api/crm-connectors/retry`, and a Sync log / Retry sync section in the admin customizer. Sync log events must remain sanitized: provider/status/local IDs/retry state only, never raw tokens, webhook URLs, env values, or sensitive provider config.

Verification for connector changes:

```bash
cd /home/jianl/github-work/hermes_solo_company
python3 -m py_compile modules/solo_crm/connectors/*.py modules/website_chatbot/backend/app.py modules/website_chatbot/backend/site_gateway.py
python3 modules/solo_crm/tests/test_crm_core.py
python3 modules/solo_crm/tests/test_crm_connectors_base.py
python3 modules/solo_crm/tests/test_crm_connector_config.py
python3 modules/solo_crm/tests/test_crm_connector_google_sheets.py
python3 modules/solo_crm/tests/test_crm_connector_hubspot.py
python3 modules/solo_crm/tests/test_crm_connector_sync.py
python3 modules/solo_crm/tests/test_crm_connector_sync_log.py
python3 modules/website_chatbot/tests/test_backend.py
node modules/website_chatbot/tests/admin_customizer_static.test.js
scripts/install_easiio_modules.sh --dry-run --target /tmp/easiio-crm-connectors-install-test
git diff --check
```

## Multi-site CRM tracking

Solo CRM now supports multiple organizations and websites/tenants. The SQLite schema includes:

```text
organizations
websites
website_visitors
website_visits
contacts.organization_id / website_id / visitor_id
deals.organization_id / website_id
activities.organization_id / website_id / visitor_id
```

The widget sends:

```html
data-site-id="stable-site-id"
data-organization-name="Organization Name"
data-website-name="Website Name"
data-track-page-views="true"
```

The backend records a visitor/page view on `/api/chat/session` and attributes leads/deals/activities to the matching `site_id`. Use distinct `data-site-id` values for each website so each website can list its own visitors/customers while still sharing the same Hermes Bot CRM database.

### WordPress plugin

The plugin source is at:

```bash
/home/jianl/.hermes/tools/website_chatbot/wordpress-plugin/easiio-chatbot/easiio-chatbot.php
```

Packaged ZIP:

```bash
/home/jianl/.hermes/tools/website_chatbot/dist/easiio-chatbot-wordpress-plugin.zip
```

If the `zip` CLI is not installed in WSL, package with Python instead:

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

The improved plugin includes a WordPress Settings page under `Settings → Easiio Chatbot`, safe sanitized public widget options, backend health check, and defaults that keep `data-auto-open`, `data-rag-admin`, and `data-lead-forms-enabled` false unless explicitly enabled. It still must not store/render LLM keys, CRM tokens, webhook URLs, SMTP/Brevo secrets, MCP details, or database paths.

It injects the script through:

```php
add_action('wp_footer', 'easiio_chatbot_footer_script', 100);
```

Conservative defaults:

- `data-auto-open="false"`
- `data-rag-admin="false"`; enable only on protected/admin-only pages because it exposes a manual knowledge editor for the configured `site_id`
- `data-voice-enabled="false"`; enable only after the backend `/api/chat/voice` endpoint and server-side TTS provider are reviewed
- excludes `/wp-admin,/wp-login.php,/cart,/checkout,/my-account`
- uses `esc_url()` and `esc_attr()`
- no secrets or CRM/MCP internals exposed
- points at `https://chat.easiio.com/widget.js` / `https://chat.easiio.com` for production deployment

Do not install/activate on production until the public widget/backend are deployed and reviewed.

## AI Solo Company Class 3 workflow

Use this skill for Class 3 of the AI Solo Company course: **Website AI Assistant + Lead Collection**. The class goal is to turn a website into a simple AI salesperson:

```text
Website visitor
  -> website chatbot / AI assistant
  -> company knowledge base answers
  -> lead qualification questions
  -> lead form or conversational lead capture
  -> Solo CRM / SQLite record
  -> first follow-up email draft
  -> owner notification / next action
```

When creating Class 3 teaching materials or a PPT layout, target about **24–29 slides** so there is still time for a live demo. A reusable structure that matched Jian's expectation is:

1. Opening + business goal: Class 3 positioning, highlights, and the visitor-to-lead business problem.
2. Software stack foundation: explain frontend/web, backend/API, database/CRM storage, caching/CDN/backend cache, RAG/knowledge base, authentication/admin, integrations, and hosting/deployment.
3. Stack selection guidance: static HTML for fast demos/landing pages, WordPress for blogs and non-technical editing, Next.js for app-like/SaaS flows, Postgres/Supabase for production, SQLite/Solo CRM for local class demos.
4. Current bot implementation: website building skills, Sitelet preview, chatbot widget, Python backend API, per-site RAG by `site_id`, Solo CRM SQLite, Email Agent/owner notification, WordPress chatbot plugin, and WordPress content tools for draft blogs/page edits.
5. Student workflow: company knowledge worksheet, assistant config, prompt pack, acceptance checklist.
6. Demo + wrap-up: live demo runbook, common mistakes, and final takeaways.

A generated reference document was saved at `/mnt/c/Users/jianl/solo-company-class-site/docs/class-3-ppt-layout-website-ai-assistant.md`.

For class handouts about setting up AI chatbot + RAG + CRM, create both editable Markdown and Word `.docx` versions on the Windows Desktop so Jian can distribute them directly. A reusable document pair was generated at:

```text
/mnt/c/Users/jianl/Desktop/AI_Solo_Company_Chatbot_RAG_CRM_Setup_Instructions.md
/mnt/c/Users/jianl/Desktop/AI_Solo_Company_Chatbot_RAG_CRM_Setup_Instructions.docx
/mnt/c/Users/jianl/Desktop/AI_Solo_Company_Chatbot_RAG_CRM_Setup_Instructions_Chinese.md
/mnt/c/Users/jianl/Desktop/AI_Solo_Company_Chatbot_RAG_CRM_Setup_Instructions_Chinese.docx
```

When generating these handouts, include: architecture overview, `site_id` selection, backend startup, widget embed code, RAG setup methods, LLM server-side env variables, chatbot Q&A tests, lead capture tests, CRM verification, WordPress plugin setup, optional external CRM sync, troubleshooting, class demo runbook, student exercise/worksheet, acceptance checklist, safe production rules, and a dedicated “Hermes Bot Prompt Pack” section with copy-paste prompts for creating a site, adding chatbot, adding RAG entries, configuring lead capture, verifying CRM, WordPress integration, class demo generation, troubleshooting, worksheet generation, and final reporting. For Chinese versions, provide a full localized document rather than a short summary. Verify `.docx` outputs by opening them as ZIP packages, checking required Word parts, parsing `word/document.xml`, and checking markers such as `Hermes Bot Prompt Pack` / `Hermes Bot 提示词包`.

Recommended agents for the class:

1. **Website Sales Assistant Agent** — answers services/pricing/FAQ/process questions from the company knowledge base and invites high-intent visitors to share contact info.
2. **Lead Qualification Agent** — extracts `name`, `email`, `phone`, `company`, `need`, `budget`, `timeline`, `service_interest`, scores the lead, and asks for missing fields.
3. **CRM Agent** — creates/updates contact, company, deal, activity, and follow-up task using Solo CRM tools.
4. **Follow-up Email Agent** — drafts the first personalized email from lead data and chat summary.
5. **Owner Notification Agent** — summarizes lead score, interest, timeline, and next action for the business owner.

Recommended class deliverables:

```text
/home/jianl/ai-solo-company-class-3/
  lesson-plan.md
  student-worksheet.md
  demo-company/company_knowledge.md
  demo-company/assistant_config.json
  demo-site/index.html
  prompts/website_sales_assistant.md
  prompts/lead_qualification_agent.md
  prompts/follow_up_email_agent.md
  verification-checklist.md
```

Minimum acceptance criteria for the class demo:

- Website page loads.
- Chatbot appears.
- Chatbot answers one company FAQ from provided knowledge.
- Chatbot asks for contact info after detecting buying intent.
- Lead submission creates/updates CRM contact.
- CRM contains an activity/deal/follow-up.
- Follow-up email draft is generated.

A planning document for this class was created at:

```text
/home/jianl/ai-solo-company-class-3-agent-skill-plan.md
```

## AI Solo Company Class 4 workflow

Use this skill for Class 4 of the AI Solo Company course when planning or preparing **Hermes Skill Studio / Build Your First Custom AI Business Skill**. The class should build directly on Class 3's website chatbot + CRM lead flow:

```text
Class 3: Website visitor -> Chatbot -> RAG answer -> Lead capture -> Solo CRM
Class 4: Lead data -> Custom Hermes Skill -> Follow-up email + CRM note + next action
```

Recommended Class 4 title:

```text
Class 4: Hermes Skill Studio — Build Your First Custom AI Business Skill
```

Core teaching message: a solo company is not only using AI tools; it builds reusable AI skills that encode repeatable business processes.

Relevant reference skills to load when preparing Class 4:

```text
web-development/website-chatbot-solo-crm
autonomous-ai-agents/hermes-agent
autonomous-ai-agents/codex
web-development/create-site
web-development/add-page
web-development/edit-section
web-development/sitelet-cloud-render
productivity/easiio-wordpress-blog-posting
productivity/easiiodev-wordpress-editor
marketing/marketing-strategy
marketing/content-studio
marketing/seo-geo-growth
```

Recommended 90-minute flow:

1. 0–8 min — opening: why skills matter after lead capture.
2. 8–20 min — what is a Hermes Skill: input, rules, tools, output, logs.
3. 20–35 min — tour existing skills: website/chatbot/CRM, WordPress, marketing, Hermes Agent, Codex.
4. 35–50 min — run a simple lead follow-up skill before customization.
5. 50–65 min — manually customize tone, CTA, scoring rules, and CRM note format.
6. 65–80 min — use Codex for a narrow controlled skill edit and review the diff.
7. 80–88 min — test, inspect logs, explain rollback/backups.
8. 88–90 min — wrap-up with each student’s customized skill deliverable.

Recommended student/demo skill:

```text
/home/jianl/.hermes/skills/class4/student-lead-followup/SKILL.md
```

Purpose:

```text
Input: website lead information
Action: qualify the lead and write follow-up
Output: lead summary, qualification score, follow-up email, CRM note, next action
```

Sample lead for live demo:

```text
Name: Sarah Chen
Business: local dental clinic
Need: wants AI chatbot for appointment questions
Budget: $1500/month
Timeline: this month
Email: sarah@example.com
```

Good Class 4 Codex demo prompt:

```text
Read this Hermes skill:
/home/jianl/.hermes/skills/class4/student-lead-followup/SKILL.md

Modify it so the output includes:
- lead_score from 1 to 5
- score_reason
- next_action

Keep the follow-up email warm and consultative.
Show me the diff before applying.
```

Recommended assets before teaching:

```text
/mnt/c/Users/jianl/solo-company-class-site/docs/class-4-hermes-skill-studio-outline.md
/mnt/c/Users/jianl/solo-company-class-site/docs/class4/
  lead-input-example.md
  skill-output-before.md
  skill-output-after-tone-change.md
  skill-output-after-json-change.md
  codex-demo-prompts.md
  test-checklist.md
```

If adding a visible admin console entry for Class 4, create a dedicated `Skill Studio / 技能工作台` panel rather than burying it inside an existing manual. Use the same three-layer admin-console pattern: left sidebar menu button, dashboard feature card, and matching `<section data-admin-panel="skill-studio" id="admin-panel-skill-studio">`. Include bilingual explanation of Skill anatomy, demo skill path, Codex safe workflow, test prompts, logs, and rollback.

A generated Class 4 outline was saved at:

```text
/mnt/c/Users/jianl/solo-company-class-site/docs/class-4-hermes-skill-studio-outline.md
```

## AI voice call prototype

A standalone Phase 1/2/3 browser voice-call prototype lives at:

```text
/home/jianl/.hermes/tools/voice_call_bot
```

Use it when Jian asks for AI voice calls, browser call demos, or future Twilio/VoIP integration. The architecture keeps the existing website chatbot as the business brain: browser audio -> `voice_to_text` -> website chatbot backend/RAG/CRM -> `voice_response` -> browser audio reply. Important files:

```text
/home/jianl/.hermes/tools/voice_call_bot/backend/call_state.py
/home/jianl/.hermes/tools/voice_call_bot/backend/chatbot_bridge.py
/home/jianl/.hermes/tools/voice_call_bot/backend/audio_pipeline.py
/home/jianl/.hermes/tools/voice_call_bot/backend/app.py
/home/jianl/.hermes/tools/voice_call_bot/demo/browser-call.html
/home/jianl/.hermes/tools/voice_call_bot/tests/test_voice_call_bot.py
```

Run local mock backend:

```bash
cd /home/jianl/.hermes/tools/voice_call_bot
VOICE_TO_TEXT_PROVIDER=mock \
VOICE_TO_TEXT_MOCK_TRANSCRIPT='I want a demo for AI agents. My email is founder@example.com' \
VOICE_RESPONSE_PROVIDER=mock \
python3 backend/app.py --host 127.0.0.1 --port 8120
```

Serve demo:

```bash
python3 -m http.server 8088 -d /home/jianl/.hermes/tools/voice_call_bot/demo
```

Open `http://127.0.0.1:8088/browser-call.html`. Browser microphone requires localhost/HTTPS and a real browser. Verify with:

```bash
cd /home/jianl/.hermes/tools/voice_call_bot
python3 -m py_compile backend/*.py
python3 tests/test_voice_call_bot.py -v
node --check demo/browser-call.js
```

Keep voice-call features disabled by default in production widget/WordPress until reviewed. Do not expose STT/TTS/Twilio provider keys in browser JS, WordPress output, tests, logs, or API responses. Raw audio is not stored in call state; returned APIs should expose safe `audio_url` only, not server audio paths.

Phase 3 adds optional integration with the reusable chatbot widget, admin customizer, and WordPress plugin. Safe public attributes/settings are `data-voice-call-enabled`, `data-voice-call-label`, `data-voice-call-api-base`, and `data-voice-call-consent-text`; the values are stored under `form_config.widget_config` as `voice_call_enabled`, `voice_call_label`, `voice_call_api_base`, and `voice_call_consent_text`. Local demo can use `data-voice-call-api-base="http://localhost:8120"`. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase3-widget-admin-wordpress-integration.md`. After changes, verify website_chatbot static/backend/plugin tests plus voice_call_bot tests.

Phase 4 adds Twilio Programmable Voice phone-call support in `/home/jianl/.hermes/tools/voice_call_bot/backend/twilio_adapter.py` with dependency-free TwiML endpoints `POST /api/voice-call/twilio/incoming`, `/gather`, and `/status`. The adapter uses Twilio `<Gather input="speech dtmf">`, sends `SpeechResult`/DTMF turns through `ChatbotBridge` into website_chatbot RAG/CRM, returns `<Say>` replies, masks phone/email PII in TwiML speech, masks caller phones in JSON call state, and ends calls from status callbacks. Production should set server-side `VOICE_CALL_PUBLIC_BASE_URL`, `VOICE_CALL_TWILIO_SITE_ID`, and `VOICE_CALL_TWILIO_AUTH_TOKEN`; when the auth token is set, `X-Twilio-Signature` is enforced. Never expose Twilio tokens in browser JS, WordPress output, logs, tests, or docs. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase4-twilio-phone-integration.md`.

Phase 5 adds a Twilio Media Streams foundation in `/home/jianl/.hermes/tools/voice_call_bot/backend/media_streams.py`. New endpoints are `POST /api/voice-call/twilio/incoming-stream` for TwiML `<Connect><Stream>` generation and `POST /api/voice-call/twilio/media-stream/event` for local/edge event simulation. The stdlib backend is not a WebSocket server; production needs a WSS-capable edge to receive Twilio start/media/stop events and call `process_media_stream_event(...)`. The Phase 5 processor converts public base URLs to `ws://`/`wss://`, tracks streamSid and media chunk counts, never stores raw media payloads, and accepts transcript/speech events that flow through `ChatbotBridge` into website_chatbot RAG/CRM. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase5-twilio-media-streams-foundation.md`.

Phase 6 adds the WebSocket-edge-compatible runtime in `/home/jianl/.hermes/tools/voice_call_bot/backend/websocket_edge.py` plus a minimal dependency-free local RFC 6455 text-frame server at `/home/jianl/.hermes/tools/voice_call_bot/backend/websocket_edge_server.py`. New internal/test endpoint: `POST /api/voice-call/twilio/websocket-edge/event`. It handles `start`, `media`, `flush`/`speech_final`, and `stop`; buffers only decoded audio byte/chunk counts, never raw base64 payloads; uses mock streaming STT via `VOICE_CALL_STREAMING_STT_PROVIDER=mock`; sends final transcript through `ChatbotBridge`; synthesizes assistant audio through `voice_response`; returns safe `audio_url` and Twilio `mark` messages; supports optional `VOICE_CALL_EDGE_SHARED_SECRET` through `X-Easiio-Edge-Secret`. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase6-websocket-edge-streaming-runtime.md`.

Phase 7 adds deployment-readiness tooling in `/home/jianl/.hermes/tools/voice_call_bot/backend/deployment.py` and `GET /api/voice-call/deploy/readiness`. The helper generates safe reviewable nginx and systemd snippets for `voice-call-http.service`, `voice-call-websocket-edge.service`, and `/etc/nginx/sites-available/easiio-voice-call`; it also reports production readiness for public HTTPS base URL, Twilio signature token presence, WebSocket edge secret presence, non-mock streaming STT, and non-mock TTS. CLI commands: `python3 backend/deployment.py readiness`, `python3 backend/deployment.py plan`, and `python3 backend/deployment.py health --url http://127.0.0.1:8120/health`. It must never print raw Twilio/STT/TTS/edge secrets; only report present/redacted. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase7-deployment-readiness-runbook.md`.

Phase 8 adds provider-adapter readiness and a safe ops dashboard. Key files: `/home/jianl/.hermes/tools/voice_call_bot/backend/streaming_stt_adapters.py` and `/home/jianl/.hermes/tools/voice_call_bot/backend/ops_dashboard.py`. New endpoints: `GET /api/voice-call/providers/readiness` and `GET /api/voice-call/ops/dashboard?site_id=...`. Supported streaming STT provider keys are `mock`, `deepgram`, `openai_realtime`, `azure`, and `twilio` with aliases for `openai`, `openai-realtime`, `azure_speech`, and `azure-speech`. The dependency-free runtime reports real providers as configured/missing/adapter-ready but does not expose secrets. Ops dashboard responses must remain sanitized: safe counts/recent-call summaries only, no raw audio, full emails, raw phones, provider payloads, secrets, or server paths. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase8-provider-adapters-ops-dashboard.md`.

Phase 9 adds Deepgram plus OpenAI Realtime provider wiring. `streaming_stt_adapters.build_provider_connection_plan(provider)` returns sanitized Deepgram WSS/HTTPS-flush plans and OpenAI Realtime WSS/session-event plans without secret values. `websocket_edge.py` now keeps Twilio media bytes in in-process ephemeral buffers only, pops them on `flush`/`speech_final`, and clears them on `stop`; raw base64/media is still never persisted to call-state JSON. Safe local provider simulation uses `VOICE_CALL_STREAMING_STT_TEST_TRANSCRIPT`; reviewed Deepgram HTTPS flush transcription can be enabled with `VOICE_CALL_STREAMING_STT_LIVE_NETWORK=1`. Recommended Deepgram env: `VOICE_CALL_STREAMING_STT_PROVIDER=deepgram`, `DEEPGRAM_API_KEY`, `DEEPGRAM_MODEL=nova-3`, `DEEPGRAM_LANGUAGE=en-US`, `DEEPGRAM_ENCODING=mulaw`, `DEEPGRAM_SAMPLE_RATE=8000`. Recommended OpenAI Realtime env: `VOICE_CALL_STREAMING_STT_PROVIDER=openai_realtime`, `OPENAI_API_KEY`, `OPENAI_REALTIME_MODEL=gpt-4o-realtime-preview`, `OPENAI_REALTIME_TRANSCRIPTION_MODEL=gpt-4o-mini-transcribe`, `OPENAI_REALTIME_INPUT_AUDIO_FORMAT=g711_ulaw`. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase9-deepgram-openai-realtime-provider-wiring.md`.

Phase 10 adds review-first staging live Deepgram support in `/home/jianl/.hermes/tools/voice_call_bot/backend/staging_live.py`. New endpoints are `GET /api/voice-call/staging/readiness` and `POST /api/voice-call/staging/deepgram-smoke`. Readiness returns safe Twilio staging console values for `incoming-stream`, `status`, and WSS `/api/voice-call/twilio/media-stream` plus checks for public HTTPS, Twilio signature token, edge secret, Deepgram config, live-network gate, and TTS provider. The Deepgram smoke is blocked unless `confirm_live_smoke: true`; real network calls also require `VOICE_CALL_STREAMING_STT_LIVE_NETWORK=1`, while safe simulation can use `VOICE_CALL_STREAMING_STT_TEST_TRANSCRIPT`. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase10-staging-live-deepgram-runbook.md`.

Phase 11 adds review-first call transcript summaries and owner notification drafts in `/home/jianl/.hermes/tools/voice_call_bot/backend/call_review.py`. New endpoints are `POST /api/voice-call/review/create` and `GET /api/voice-call/review/list?site_id=...`. The review builder stores safe records in `VOICE_CALL_REVIEW_STORE` (default `/home/jianl/.hermes/tools/voice_call_bot/data/voice_call_reviews.json`), masks emails/phones before API response and persistence, calculates lead score/score reason/next action, includes CRM IDs, and drafts an owner notification with only recipient count from `VOICE_CALL_REVIEW_NOTIFICATION_RECIPIENTS` — never raw recipient addresses. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase11-call-review-notifications.md`.

Phase 12 adds the admin/operator call review workflow plus approved owner-notification queueing. New endpoint: `POST /api/voice-call/review/notify` with `confirm_send: true`; it accepts `review_id` or `call_id`, requires human approval, then queues a safe `json_outbox` delivery record in `VOICE_CALL_REVIEW_NOTIFICATION_OUTBOX` (default `/home/jianl/.hermes/tools/voice_call_bot/data/voice_call_notification_outbox.json`). The browser demo includes `adminReviewPanel` to load site reviews and queue approved owner notifications. Outbox/API records expose only delivery ID, review/call/site IDs, provider/status, subject/body preview, and recipient count; never raw recipients, caller PII, provider secrets, raw audio, or server paths. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase12-admin-call-review-notifications.md`.

Phase 13 adds protected admin routes and a reviewed delivery worker. When `VOICE_CALL_ADMIN_TOKEN` is set, review routes require `X-Easiio-Admin-Token`; responses never include the token. New endpoints: `POST /api/voice-call/review/deliver` with `confirm_deliver: true` to process queued notifications, and `GET /api/voice-call/review/deliveries?site_id=...` to inspect safe delivery logs. Delivery log path is `VOICE_CALL_REVIEW_DELIVERY_LOG` (default `/home/jianl/.hermes/tools/voice_call_bot/data/voice_call_delivery_log.json`); delivery provider defaults to safe `mock`/`json_outbox` style processing via `VOICE_CALL_DELIVERY_PROVIDER`. Logs expose safe IDs/status/provider/recipient_count/subject/body_preview only — never raw recipients, caller PII, provider secrets, raw audio, or server paths. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase13-protected-admin-delivery-worker.md`.

Phase 14 adds reviewed Brevo delivery and retry/backoff to the same protected delivery worker. Set `VOICE_CALL_DELIVERY_PROVIDER=brevo`, `VOICE_CALL_BREVO_API_KEY` or `EASIIO_BREVO_API_KEY`, `VOICE_CALL_BREVO_FROM_EMAIL`, optional `VOICE_CALL_BREVO_FROM_NAME`, and `VOICE_CALL_REVIEW_NOTIFICATION_RECIPIENTS` server-side only. Local verification can set `VOICE_CALL_BREVO_DRY_RUN=1`; reviewed live Brevo sending requires `VOICE_CALL_BREVO_LIVE_NETWORK=1`. Retry settings are `VOICE_CALL_DELIVERY_RETRY_BASE_MS` and `VOICE_CALL_DELIVERY_MAX_ATTEMPTS`; failed Brevo attempts become `retry_scheduled` until max attempts, then `failed`. Safe logs include attempt/retry metadata and response status but never raw recipients, sender addresses, caller PII, Brevo keys, provider payloads, raw audio, admin tokens, or server paths. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase14-brevo-delivery-retry.md`.

Phase 15 adds an operator retry dashboard and selected retry API. `GET /api/voice-call/review/deliveries` now accepts safe filters `site_id`, `status`, `provider`, `since_ms`, `until_ms`, and `limit`. New protected endpoint `POST /api/voice-call/review/retry` requires `confirm_retry: true` plus `delivery_ids`, retries only selected `queued`/`retry_scheduled`/`failed` records, ignores already sent records, appends a safe delivery-log attempt, and updates the outbox item. The browser demo contains `operatorRetryDashboard`, `deliveryStatusFilter`, `deliveryProviderFilter`, `loadDeliveries`, and `retrySelectedDeliveries`. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase15-operator-retry-dashboard.md`.

Phase 16 adds operator notes, assignment, and resolution tracking for delivery failures. New protected endpoint `POST /api/voice-call/review/delivery-update` requires `confirm_update: true`, `delivery_id`, and `operator_status` (`acknowledged`, `assigned`, `skipped`, or `resolved`). It updates the selected outbox item with safe `operator_status`, masked operator notes, safe assignment label, appends a Phase 16 audit entry to the delivery log, and never exposes raw assignee emails, operator IDs, owner recipients, caller PII, Brevo keys, admin tokens, provider payloads, raw audio, or server paths. The browser demo contains `deliveryOperatorStatus`, `deliveryAssignedTo`, `deliveryOperatorNote`, and `updateSelectedDelivery`. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase16-operator-notes-assignment.md`.

Phase 17 adds a protected delivery failure queue summary and SLA view. New protected endpoint `GET /api/voice-call/review/failure-summary?site_id=...&limit=50` summarizes current `VOICE_CALL_REVIEW_NOTIFICATION_OUTBOX` state with safe `counts_by_status`, `counts_by_operator_status`, `counts_by_provider`, `sla_buckets` (`under_1h`, `between_1h_24h`, `over_24h`), `oldest_unresolved`, and a bounded `unresolved_items` list. Unresolved deliveries are `queued`, `retry_scheduled`, or `failed` unless operator status is `resolved` or `skipped`. The browser demo contains `failureQueueSummary`, `loadFailureSummary`, and `failureSummaryCards`. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase17-delivery-failure-summary-sla.md`. Responses must remain sanitized: no raw recipients, caller PII, assignee/operator emails, Brevo keys, admin tokens, provider payloads, raw audio, or server paths.

Phase 18 adds review-first operator follow-up tasks and escalation rules. New protected endpoints: `GET /api/voice-call/review/escalations?site_id=...&limit=50` and `POST /api/voice-call/review/follow-up-task`. Escalation reasons are `overdue_24h` (unresolved older than 24h), `retry_blocked` (failed at max attempts), and `unassigned` (no safe assignment). Follow-up task creation requires `confirm_create: true`, selected `delivery_ids`, and stores sanitized `follow_up_task` metadata plus masked operator notes on the delivery record and safe Phase 18 audit log entries. The browser demo contains `escalationTaskPanel`, `loadEscalationTasks`, `createEscalationTasks`, `escalationTaskNote`, and `escalationTaskCards`. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase18-operator-followup-escalations.md`. Responses/audit entries must remain sanitized: no raw recipients, caller PII, assignee/operator emails, Brevo keys, admin tokens, provider payloads, raw audio, or server paths.

Phase 19 adds reviewed CRM handoff for Phase 18 follow-up tasks. New protected endpoint: `POST /api/voice-call/review/crm-handoff`. It requires `confirm_create: true`, selected `delivery_ids`, and an existing open/recommended Phase 18 `follow_up_task`; then it creates a local Solo CRM `task` activity linked to safe `contact_id`/`deal_id` from the related Phase 11 review when available, stores `crm_handoff.activity_id` metadata on the delivery follow-up task, and appends a safe Phase 19 audit log entry. The browser demo contains `crmHandoffPanel`, `crmHandoffNote`, `crmHandoffFollowUpAt`, and `createCrmHandoff`. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase19-crm-followup-handoff.md`. Responses, CRM activity bodies, and audit entries must remain sanitized: no raw recipients, caller PII, assignee/operator emails, Brevo keys, admin tokens, provider payloads, raw audio, or server paths.

Phase 20 adds the protected CRM follow-up dashboard and completion sync. New endpoints: `GET /api/voice-call/review/crm-followups?site_id=...` and `POST /api/voice-call/review/crm-followup-complete`. The dashboard lists Phase 19 `crm_handoff.activity_id` tasks with live Solo CRM activity completion state and masked previews. Completion requires `confirm_complete: true`, marks the Solo CRM activity complete via `complete_activity(activity_id)`, sets delivery `follow_up_task.task_status` to `crm_followup_completed`, marks `operator_status` as `resolved`, stores safe completion metadata, and appends a Phase 20 audit entry. Browser demo markers are `crmFollowupDashboard`, `crmFollowupCompletionNote`, `loadCrmFollowups`, `crmFollowupCards`, and `completeCrmFollowup`. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase20-crm-followup-dashboard-completion.md`. Responses and audit logs must remain sanitized: no raw recipients, caller PII, assignee/operator emails, Brevo keys, admin tokens, provider payloads, raw audio, or server paths.

Phase 21 adds the protected Calendar / Reminder Handoff after Phase 20 completion. New endpoints: `GET /api/voice-call/review/reminder-handoffs?site_id=...` and `POST /api/voice-call/review/reminder-handoff`. Handoff creation requires `confirm_create: true`, a selected completed CRM follow-up delivery, and `reminder_at`; it writes sanitized records to `VOICE_CALL_REMINDER_HANDOFF_QUEUE` (default `/home/jianl/.hermes/tools/voice_call_bot/data/voice_call_reminder_handoffs.json`), creates a local Solo CRM reminder task, stores `follow_up_task.reminder_handoff`, and appends a Phase 21 audit entry. It performs no automatic external calendar mutation. Browser demo markers are `calendarReminderPanel`, `reminderHandoffTitle`, `reminderHandoffAt`, `reminderHandoffSchedulingUrl`, `reminderHandoffNote`, `loadReminderHandoffs`, `createReminderHandoff`, and `reminderHandoffCards`. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase21-calendar-reminder-handoff.md`. Responses, queue records, and audit logs must remain sanitized: no raw recipients, caller PII, assignee/operator emails, Brevo keys, admin tokens, external calendar credentials, provider payloads, raw audio, or server paths.

Phase 22 adds protected Reminder Completion / Cancellation after Phase 21. New endpoint: `POST /api/voice-call/review/reminder-handoff-update`. It requires `confirm_update: true`, `reminder_id`, and `action` (`complete` or `cancel`). Completion updates the reminder queue, syncs related delivery `follow_up_task.reminder_handoff`, marks the linked local Solo CRM reminder task activity completed when `crm.reminder_activity_id` is present, and appends a Phase 22 audit entry. Cancellation only closes local queue/delivery metadata and does not mutate external calendars. Browser demo markers are `reminderLifecyclePanel`, `reminderLifecycleNote`, `completeReminderHandoff`, and `cancelReminderHandoff`. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase22-reminder-completion-cancellation.md`. Responses, queue records, and audit logs must remain sanitized: no raw recipients, caller PII, assignee/operator emails, Brevo keys, admin tokens, external calendar credentials, provider payloads, raw audio, or server paths.

Phase 23 adds protected Reminder SLA Dashboard / Due Reminder Queue after Phase 22. New endpoint: `GET /api/voice-call/review/reminder-sla?site_id=...&limit=50`. It reads `VOICE_CALL_REMINDER_HANDOFF_QUEUE`, requires admin token when configured, and returns safe `status_counts`, `sla_buckets` (`overdue`, `due_today`, `upcoming_7d`, `future`, `unscheduled`, `closed`), `oldest_due`, and `next_action_queue`. Browser demo markers are `reminderSlaDashboard`, `loadReminderSlaDashboard`, and `reminderSlaCards`. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase23-reminder-sla-dashboard.md`. It performs no automatic external calendar mutation and responses remain sanitized: no raw recipients, caller PII, assignee/operator emails, Brevo keys, admin tokens, external calendar credentials, provider payloads, raw audio, or server paths.

Phase 24 adds protected Reminder Reschedule / Snooze after the Phase 23 due reminder queue. New endpoint: `POST /api/voice-call/review/reminder-handoff-reschedule`. It requires `confirm_update: true`, `reminder_id`, and `action` (`reschedule` with `new_reminder_at`, or `snooze` with `snooze_minutes`). It updates only local `VOICE_CALL_REMINDER_HANDOFF_QUEUE`, linked delivery `follow_up_task.reminder_handoff`, and local Solo CRM reminder task `follow_up_at` when `crm.reminder_activity_id` is present; it performs no external calendar mutation. Browser demo markers are `reminderReschedulePanel`, `reminderRescheduleAt`, `reminderSnoozeMinutes`, `rescheduleReminderHandoff`, and `snoozeReminderHandoff`. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase24-reminder-reschedule-snooze.md`. Responses and audit entries remain sanitized: no raw recipients, caller PII, assignee/operator emails, Brevo keys, admin tokens, external calendar credentials, provider payloads, raw audio, or server paths.

Phase 25 adds protected Reminder Audit Timeline / Reminder History Dashboard after Phase 24. New endpoint: `GET /api/voice-call/review/reminder-history?site_id=...&reminder_id=...&limit=50`. It is read-only, requires admin token when configured, and returns sanitized `current`, `timeline`, `timeline_count`, `audit_log_count`, `lifecycle_counts`, and `action_counts` for created/rescheduled/snoozed/completed/cancelled lifecycle history. Browser demo markers are `reminderAuditTimelinePanel`, `loadReminderAuditTimeline`, and `reminderAuditTimelineCards`. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase25-reminder-audit-timeline.md`. It performs no external calendar mutation and responses remain sanitized: no raw recipients, caller PII, assignee/operator emails, Brevo keys, admin tokens, external calendar credentials, provider payloads, raw audio, or server paths.

Phase 26 adds protected Reminder Analytics / Operator Performance Dashboard after Phase 25. New endpoint: `GET /api/voice-call/review/reminder-analytics?site_id=...&limit=50`. It is read-only, requires admin token when configured, and returns sanitized operational metrics including `status_counts`, `completion_rate`, `overdue_rate_open`, `average_completion_time_ms`, `reschedule_summary`, `action_counts`, `operator_workload`, `site_health`, `overdue_queue`, `recent_reminders`, and `export_snapshot`. Browser demo markers are `reminderAnalyticsDashboard`, `loadReminderAnalytics`, and `reminderAnalyticsCards`. Documentation: `/home/jianl/.hermes/tools/voice_call_bot/docs/phase26-reminder-analytics-dashboard.md`. It performs no external calendar mutation and responses remain sanitized: no raw recipients, caller PII, assignee/operator emails, Brevo keys, admin tokens, external calendar credentials, provider payloads, raw audio, or server paths.

Verify voice-call changes with `cd /home/jianl/.hermes/tools/voice_call_bot && python3 -m py_compile backend/*.py && python3 tests/test_voice_call_bot.py -v && node --check demo/browser-call.js`, plus local form-urlencoded/JSON curl smokes for incoming/gather/status, incoming-stream/media-stream/event, websocket-edge/event, deploy/readiness, providers/readiness, ops/dashboard, staging/readiness, reminder-history, reminder-analytics, or staging/deepgram-smoke depending on which routing changed. For Phase 6/7/8/9/10, also smoke the local WebSocket server with a RFC 6455 handshake and start/media/flush text frames when WebSocket behavior changes, run `python3 backend/deployment.py readiness && python3 backend/deployment.py plan` when deployment tooling changes, smoke `/api/voice-call/providers/readiness` + `/api/voice-call/ops/dashboard?site_id=<site>` when provider/ops code changes, and for Phase 10 staging live work explicitly verify `/api/voice-call/staging/readiness`, blocked smoke without `confirm_live_smoke`, safe simulated Deepgram smoke with `VOICE_CALL_STREAMING_STT_TEST_TRANSCRIPT`, no listeners left on test ports, and no high-confidence secret markers in changed docs/tests.

## Verification commands

Run widget static tests:

```bash
node /home/jianl/.hermes/tools/website_chatbot/tests/widget_static.test.js
```

Run backend tests:

```bash
python3 -m unittest /home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py
```

Run WordPress plugin static tests:

```bash
node /home/jianl/.hermes/tools/website_chatbot/tests/wp_plugin_static.test.js
```

Syntax checks:

```bash
node --check /home/jianl/.hermes/tools/website_chatbot/widget/widget.js
python3 -m py_compile /home/jianl/.hermes/tools/website_chatbot/backend/app.py
```

PHP may not be installed in this WSL environment; if available, check:

```bash
php -l /home/jianl/.hermes/tools/website_chatbot/wordpress-plugin/easiio-chatbot/easiio-chatbot.php
```

## Local demo

Terminal 1 — backend:

```bash
python3 /home/jianl/.hermes/tools/website_chatbot/backend/app.py --host 0.0.0.0 --port 8099
```

Terminal 2 — static widget demo:

```bash
python3 -m http.server 8088 -d /home/jianl/.hermes/tools/website_chatbot/widget
```

Open:

```text
http://localhost:8088/demo.html
```

For Hermes Proxy previews that need both static files and `/api/chat/*` through one public tunnel, use the gateway:

```bash
python3 /home/jianl/.hermes/tools/website_chatbot/backend/site_gateway.py \
  --host 0.0.0.0 \
  --port 8020 \
  --site-dir /mnt/c/Users/jianl/solo-company-class-site \
  --api-base http://127.0.0.1:8099
```

Then point Hermes Proxy `LOCAL_PROXY_TARGET` at `http://127.0.0.1:8020` and set the embedded widget `data-api-base="."` so public `/p/<tunnel-id>/api/chat/*` requests route through the same tunnel. If a Sitelet-generated page on `https://sitelet.easiiodev.ai/generated/...` embeds a widget/API base on `https://hermesproxy.easiiodev.ai/p/<tunnel-id>/...`, verify CORS as part of the smoke test. The gateway should return `Access-Control-Allow-Origin: https://sitelet.easiiodev.ai` on `/api/chat/*` preflight and JSON responses; otherwise the visible chatbot UI can load but all chat/session requests fail in the browser.

### Restart AI Solo local website behind Hermes Proxy

When Jian says the local AI Solo Company site is down, a student cannot log in, or the public login page returns 503, do not assume the user account is missing. First check the login DB, local services, and the managed tunnel:

```bash
ss -ltnp | grep -E ':(8020|8099)\\b' || true
/home/jianl/.hermes/tools/hermes_proxy/site_proxy_manager.py list || true
ps -ef | grep -F local_connector.py | grep -v grep || true
curl -sS -o /tmp/ai_backend_health.json -w 'backend %{http_code}\\n' http://127.0.0.1:8099/health || true
curl -sS -o /tmp/ai_gateway_home.html -w 'gateway %{http_code}\\n' http://127.0.0.1:8020/ || true
curl -sS -L -o /tmp/ai_solo_public_login.html -w 'public_login %{http_code}\\n' https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-ai-solo/login.html || true
curl -sS https://hermesproxy.easiiodev.ai/_health || true
```

For a specific student, query `/home/jianl/.hermes/tools/website_chatbot/data/ai_solo_site.db` by normalized lowercase email and nearby `user_number`, but do not print password hashes. Verify the roster formula password by reimplementing `site_gateway.py`'s `pbkdf2_sha256$200000$salt_hex$digest_hex` check using `bytes.fromhex(salt_hex)`; a common mistake is treating the hex salt as UTF-8 text, which falsely reports password mismatch. Then verify `POST /auth/login` locally or publicly and print only sanitized outcome fields (`HTTP`, `ok`, `role`, email match), never cookies/session tokens or plaintext passwords.

If `site_proxy_manager.py list` shows `ai-solo` stopped and public login returns 503 while local `8099`/`8020` are also down, restart the chatbot backend and gateway as tracked background processes, then restart the manager connector. If the manager says `Connector not found: /tmp/hermes_proxy/proxy-server/local_connector.py`, use the checked-out connector path explicitly:

```bash
/home/jianl/.hermes/tools/hermes_proxy/.venv/bin/python \
  /home/jianl/.hermes/tools/hermes_proxy/site_proxy_manager.py start \
  --site ai-solo \
  --restart \
  --connector /home/jianl/github-work/hermes_proxy/proxy-server/local_connector.py
```

The connector can stay running if it still targets `http://127.0.0.1:8020`.

Backend:

```bash
python3 /home/jianl/.hermes/tools/website_chatbot/backend/app.py --host 127.0.0.1 --port 8099
```

Gateway, with protected env loaded but never printed:

```bash
bash -lc 'set -a; [ -f /home/jianl/.hermes/.env ] && source /home/jianl/.hermes/.env; [ -f /home/jianl/.hermes/tools/website_chatbot/data/ai_solo_admin.env ] && source /home/jianl/.hermes/tools/website_chatbot/data/ai_solo_admin.env; set +a; python3 /home/jianl/.hermes/tools/website_chatbot/backend/site_gateway.py --host 127.0.0.1 --port 8020 --site-dir /mnt/c/Users/jianl/solo-company-class-site --api-base http://127.0.0.1:8099'
```

Verify all three layers before reporting success:

```bash
curl -sS http://127.0.0.1:8099/health
curl -sS http://127.0.0.1:8020/ | grep -E 'AI Solo Company|footerInquiryForm|Easiio'
curl -sS -L https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-ai-solo/ | grep -E 'AI Solo Company|footerInquiryForm|Easiio'
curl -sS 'https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-ai-solo/api/chat/form-config?site_id=ai-solo-company-class'
```

DNS for `hermesproxy.easiiodev.ai` can fail transiently even when the connector is healthy; retry public URL checks once or twice before concluding the proxy is down.

The gateway also supports the AI Solo Company site's lightweight SQLite login/download backend:

```text
POST /auth/login          JSON login; sets ai_solo_session HttpOnly cookie
POST /auth/logout         clears session
GET  /auth/me             current logged-in user
POST /admin/upload        admin-only multipart file upload
GET  /api/downloads       login-required download metadata
GET  /download/<file>     login-required file download or external/Drive redirect
```

For the AI Solo site, the downloads page itself is login-only. Keep the frontend and server-side guards together:

- `/mnt/c/Users/jianl/solo-company-class-site/downloads.html` body should include `data-auth-required="true" data-login-next="downloads.html"`.
- `site_gateway.py` should redirect anonymous `GET /downloads.html` to `login.html?next=downloads.html`.
- `_handle_downloads()` and `_serve_download()` should call `_require_logged_in()` before returning metadata, local files, or Drive/external redirects.
- Add/keep static regression assertions for these tokens in `/mnt/c/Users/jianl/solo-company-class-site/auth_download_static_test.py`.

Verification pattern after changing chatbot backend RAG/session behavior:

```bash
python3 /home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py
python3 -m py_compile /home/jianl/.hermes/tools/website_chatbot/backend/app.py
```

When planning or implementing RAG accuracy upgrades from an external RAG design document, first extract the document with the `ocr-and-documents` skill, then inspect the current backend RAG helpers in `/home/jianl/.hermes/tools/website_chatbot/backend/app.py` before proposing infrastructure. Prefer an incremental Phase 1 that keeps the dependency-free Python backend stable: enhanced section-aware chunks with metadata/summaries, deterministic query expansion, optional LLM HyDE/simulated-answer retrieval, hybrid scoring, reranking, neighboring context expansion, grounded answers with citations, and verification/anti-hallucination fallback. HyDE text is retrieval-only and must never be cited as evidence. A detailed plan was saved at `/home/jianl/.hermes/tools/website_chatbot/docs/plans/2026-05-27-enhanced-rag-chatbot-accuracy-plan.md`; use it as the baseline for future implementation.

For crashes in `/api/chat/session` with page-context RAG, reproduce with the same `site_id`, `url`, `title`, and `content` sent twice. A single first session can pass while the second crashes if stale chunk replacement only runs when existing chunks are present. In `update_site_rag_index()`, use the sanitized `url`/`title` already stored on `new_chunks[0]`; do not reference local variables from `_rag_chunks_from_page_context()` because they are out of scope.

For course/curriculum RAG questions like “Do we teach SEO and in which class?”, verify both reachability and answer quality. The failure can be a stale backend/gateway process, but it can also be retrieval ranking: generic manual/wiki content may outrank the specific page lesson chunk when the page uses Chinese lesson labels such as `第 8 课`. Add a regression test in `tests/test_backend.py` that seeds generic manual content plus a Chinese curriculum page and asserts `rerank_rag_candidates()` puts the matching SEO lesson first. Then run `python3 tests/test_backend.py -v`, restart both `backend/app.py` and `backend/site_gateway.py`, and smoke `POST /api/chat/message` through the public Hermes Proxy URL.

Verification pattern after changing gateway auth behavior:

```bash
python3 -m py_compile /home/jianl/.hermes/tools/website_chatbot/backend/site_gateway.py
python3 /mnt/c/Users/jianl/solo-company-class-site/auth_download_static_test.py
node --check /mnt/c/Users/jianl/solo-company-class-site/site-auth.js
```

Then restart the long-running gateway process (the running process serves old code until restarted) and verify:

```text
anonymous /downloads.html -> 302 Location: login.html?next=downloads.html
anonymous /api/downloads  -> 401 {"ok": false, "error": "login_required"}
anonymous /download/*     -> 401 {"ok": false, "error": "login_required"}
logged-in /downloads.html -> 200
logged-in /api/downloads  -> 200 and includes expected Drive/local entries
```

To verify logged-in access without printing or passing plaintext passwords through a long curl command, create a short-lived session token directly in the SQLite `sessions` table for an existing user, then send `Cookie: ai_solo_session=$TOKEN` in local/public curl checks. Avoid echoing tokens or credential values in output.

Default local data paths:

```text
/home/jianl/.hermes/tools/website_chatbot/data/ai_solo_site.db
/home/jianl/.hermes/tools/website_chatbot/data/ai_solo_downloads/
/home/jianl/.hermes/tools/website_chatbot/data/ai_solo_admin.env  # chmod 600; contains admin password env var; do not commit or print
```

Start it with `AI_SOLO_ADMIN_PASSWORD` set, or source the protected admin env file, before launching `site_gateway.py`. The admin account is seeded/updated at startup.

When adding frontend JS for this gateway behind Hermes Proxy, do **not** use root-relative browser URLs like `fetch('/auth/login')`, `fetch('/api/downloads')`, or download hrefs beginning with `/download/...`. The public site is mounted under `/p/<tunnel-id>/`, so root-relative URLs escape the tunnel path and may return the proxy site's HTML, causing browser errors like `Unexpected token '<' ... is not valid JSON`. Use path-relative URLs instead, e.g. `fetch('auth/login')`, `fetch('api/downloads')`, and normalize backend-returned `/download/<file>` links to `download/<file>` before rendering them.

For AI Solo website login behavior, non-admin users must not default-redirect to admin-only pages after successful login. The login handler in `/mnt/c/Users/jianl/solo-company-class-site/site-auth.js` should choose a role-aware target: admins can default to `admin.html`; normal users should default to a user-accessible page such as `wiki.html`. If a normal user logs in with `next=admin.html` or `next=wiki-admin.html`, redirect them to `wiki.html` to avoid the observed flash-and-return login loop caused by `admin.html` immediately rejecting non-admin users. Protected public pages such as `downloads.html` and `wiki.html` may keep a static anonymous `href="login.html"` nav link, but `site-auth.js` should run `initAuthNav()` to call `auth/me` and replace that Login link with a Logout button (`auth-logout-button`) for logged-in users; logout should POST to path-relative `auth/logout`.

The AI Solo admin/backend console (`/mnt/c/Users/jianl/solo-company-class-site/admin.html`) should behave like a WordPress-style admin: a persistent left sidebar/menu with right-side feature panels. Current console panels include Dashboard, Wiki, Downloads, Shared Drive, CRM, and Web Agency Manual. The Wiki panel embeds the reusable wiki admin widget in `data-mode="admin"` with `data-root-selector="#ai-solo-wiki-admin-root"`; the Downloads panel contains the admin upload form and `#adminDownloads`; the Shared Drive panel contains the logged-in user-style shared upload form (`#shareUploadForm`, `#shareFile`, `#shareDescription`) plus `#adminSharedDownloads`; the CRM panel contains `#adminCrmSummary`, `#adminCrmCustomers`, `#adminCrmSubmissions`, `#adminCrmVisitors`, and `#adminCrmDeals`. `site-auth.js` owns tab switching through `initAdminConsoleMenu()` / `showAdminPanel()` and should keep using hash targets like `#wiki`, `#downloads`, `#shared-drive`, `#crm`, and `#web-agency-manual` without root-relative URLs.

For the AI Solo admin CRM module, keep the browser UI admin-only and fetch CRM data through `site_gateway.py` rather than exposing CRM/MCP details directly. `GET /api/admin/crm` should call `_require_admin()`, accept optional `site_id` and `limit`, read from `/home/jianl/.hermes/tools/solo_crm/solo_crm.db` via `SoloCRM`, and return `{ok, site_id, summary, customers, submissions, visitors, visits, deals}`. Include summary aliases such as `customers`, `submissions`, `visitors`, and `open_deals` because the frontend cards expect those keys. If the UI needs a clickable details/table popup for Contacts, Submissions, Visitors, Visits, and Open deals, add the modal markup to `admin.html` (`#adminCrmDetailModal`, `[data-crm-detail-title]`, `[data-crm-detail-table]`, `[data-crm-detail-close]`), render summary cards as `<button class="crm-summary-button" data-crm-detail="customers|submissions|visitors|visits|deals">`, add per-section “View table” buttons, and implement `adminCrmData`, `crmDetailColumns`, `renderCrmDetailTable()`, `openCrmDetailModal()`, and Escape/overlay/close handling in `site-auth.js`. For Visits specifically, `site_gateway.py` may need an explicit SQL join on `website_visits` + `website_visitors` + `websites` so the frontend can show page URL/title, session, visitor key, user agent, referrer, and timestamp; existing SoloCRM helper methods may only return visitor summaries. Add CSS for `.crm-summary-button`, `.crm-card-header`, `.crm-detail-overlay`, `.crm-detail-modal`, `.crm-detail-table-wrap`, and `.crm-detail-table`. Add CRM marker assertions to `auth_download_static_test.py`, then verify unauthenticated `/api/admin/crm` returns `401`, admin-authenticated `/api/admin/crm` returns lists including `visits`, and `admin.html#crm` contains the CRM panel/modal markers. After editing `site_gateway.py`, restart the long-running AI Solo gateway process; otherwise the public/local tunnel continues serving old backend code even if static HTML/JS/CSS changes are live.

When adding new AI Solo backend portal panels/manual pages, update all three layers together: add a left-sidebar `.backend-menu-item` button with `data-admin-panel-target="<panel-id>"`, add a dashboard `.backend-feature-card` with the same target, and add a matching `<section data-admin-panel="<panel-id>" id="admin-panel-<panel-id>">`. Usually no JS change is needed because `site-auth.js` discovers `data-admin-panel-target` and `data-admin-panel` automatically. Add CSS for any new panel components in `styles.css`, extend `/mnt/c/Users/jianl/solo-company-class-site/auth_download_static_test.py` with HTML/CSS marker checks, then verify with `python3 auth_download_static_test.py`, `node --check site-auth.js`, and a small HTML parser check that every `data-admin-panel-target` has a matching `data-admin-panel`. If the Hermes Proxy tunnel is running, also fetch `admin.html` and `styles.css` through `https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-ai-solo/` and check for the new markers.

For AI Solo Email Agent automation, keep control admin-only. The admin panel should use `GET/POST api/email-agent/config` path-relative URLs through `site_gateway.py`, and the gateway should require admin for `/api/email-agent/*` before proxying to the chatbot backend. Store per-site config in the backend, not browser localStorage, so the same welcome/owner notification rules apply to all widgets for that `site_id`. Extend `/home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py` with backend tests for config sanitization and “new contact sends welcome + owner notification once”, extend `/mnt/c/Users/jianl/solo-company-class-site/auth_download_static_test.py` with admin UI/API markers, then verify with:

```bash
python3 /home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py
python3 /mnt/c/Users/jianl/solo-company-class-site/auth_download_static_test.py
node --check /mnt/c/Users/jianl/solo-company-class-site/site-auth.js
python3 -m py_compile /home/jianl/.hermes/tools/website_chatbot/backend/app.py /home/jianl/.hermes/tools/website_chatbot/backend/site_gateway.py
```

If SMTP is not configured, expected behavior is outbox fallback at `EASIIO_EMAIL_OUTBOX` (or default data outbox) while lead capture still succeeds. Do not expose SMTP credentials in frontend JS, tests, logs, or final summaries.

For public AI Solo footer/static-page inquiry forms that should save to CRM and notify the same owner email, reuse the chatbot backend instead of creating a second form backend. Add semantic footer form markup in `/mnt/c/Users/jianl/solo-company-class-site/index.html` (`#footerInquiryForm`, `data-inquiry-form`, fields for name/email/phone/company/message, `#inquiryStatus`), post path-relative to `api/chat/lead` so Hermes Proxy `/p/<tunnel-id>/` routing stays intact, and include `site_id: 'ai-solo-company-class'`, `organization_name: 'AI Solo Company'`, `website_name: 'AI Solo Company Class Website'`, page URL/title, visitor/session IDs, and a marker such as `source: 'footer_inquiry_form'` in the JSON payload. Add bilingual `inquiry.*` keys to the existing index-page i18n dictionary and keep the UI progressive: disable the submit button while sending, show localized success/error/required messages, and never include owner recipient addresses or email-provider secrets in frontend code. Add responsive styles in `styles.css` using `.inquiry-panel`, `.inquiry-form`, `.inquiry-grid`, and `.inquiry-status`. Extend `auth_download_static_test.py` with HTML/JS/CSS marker assertions, verify the inline `<script>` in `index.html` by extracting it to a temp file and running `node --check`, then run `python3 auth_download_static_test.py`, `python3 portal_static_test.py`, `node --check site-auth.js`, and `git diff --check`. For a live smoke, submit a brand-new test email to local `/api/chat/lead`; expect `lead_captured: true`, CRM contact/activity/deal IDs, and `email_agent.results` showing sanitized provider/status such as Brevo `sent`. Do not print real owner recipients, test tokens, or secrets; mask test emails in logs/final summaries. Finally verify the public Hermes Proxy URL contains `footerInquiryForm`, `api/chat/lead`, and the inquiry CSS markers before committing/pushing.

When converting a static homepage CTA such as `咨询 / 报名` / `Ask / Enroll` from a placeholder mailto link into a real lead path, implement it as a modal that reuses the same `/api/chat/lead` endpoint rather than adding another backend. Replace the CTA anchor with a button marked `data-open-enroll-modal`, add `[data-enroll-modal]`, `#askEnrollForm`, `#askEnrollStatus`, `data-ask-enroll-submit`, and fields for name/email/phone/company/message plus an `interest_type` select. Use a distinct CRM marker such as `source: 'ask_enroll_modal'` and preserve page URL/title/language in `page_context`. To avoid duplicating logic, refactor the existing footer form submitter into a shared helper like `submitLeadForm(form, options)` and wrap it with `submitFooterInquiry()` and `submitAskEnrollForm()`. Add modal JS (`initAskEnrollModal`, `openEnrollModal`, `closeEnrollModal`), Escape/backdrop/Cancel close behavior, and localized `enroll.*` i18n keys. Add CSS markers `.enroll-modal`, `.enroll-modal-card`, `.enroll-modal-backdrop`, `.enroll-actions`, and `body.enroll-modal-open`. Extend `auth_download_static_test.py` to assert the modal/source/i18n/CSS markers, then verify: static tests, extracted inline `index.html` script with `node --check`, local `http://127.0.0.1:8020/` marker fetch, and public Hermes Proxy marker fetch. Confirm the old placeholder `mailto:hello@example.com` is absent locally and publicly.

When the user asks to route the `Ask / Enroll` modal emails to a specific owner address via Brevo, do not change frontend code if the modal already posts to `api/chat/lead` with `source: 'ask_enroll_modal'`; instead configure and verify the per-site Email Agent for `site_id='ai-solo-company-class'`. Use `GET/POST http://127.0.0.1:8099/api/email-agent/config?site_id=ai-solo-company-class` to confirm/save `enabled: true`, `provider: 'brevo'`, `send_owner_notification: true`, and `owner_recipients` containing the requested owner email. Check the running backend process has Brevo env loaded without printing secrets (`EASIIO_EMAIL_PROVIDER`, `EASIIO_BREVO_API_KEY` present length only, `EASIIO_EMAIL_FROM`, `EASIIO_EMAIL_FROM_NAME`). Verify the website markers locally through the gateway (`data-open-enroll-modal`, `askEnrollForm`, `source: 'ask_enroll_modal'`, `fetch(apiPath('api/chat/lead'))`, and `site_id: 'ai-solo-company-class'`). For live smoke, submit a brand-new test lead to `http://127.0.0.1:8020/api/chat/lead` with `source: 'ask_enroll_modal'`; success should show `lead_captured: true`, `email_agent.enabled: true`, `provider: brevo`, Brevo `response_status: 201`, and an owner-notification result addressed to the configured owner. Mask or avoid exposing real test lead addresses when summarizing; never print the Brevo API key.

For AI Solo backend console bilingual UI, keep translation logic in `/mnt/c/Users/jianl/solo-company-class-site/site-auth.js` and markup hooks in `admin.html`: use `data-i18n` for text, `data-i18n-placeholder` for placeholders, and `data-i18n-attr="aria-label:key"` for accessibility labels. The console language selector is `#consoleLanguageSelect`, persists to `localStorage` key `aiSoloConsoleLanguage`, and should set `document.documentElement.lang` to `en` or `zh-Hans`. When extending translated content, add matching English and Chinese keys to `consoleTranslations`, include dynamic rendered text such as downloads/shared-drive labels in `translate(...)`, and re-render download lists after language changes. Avoid raw multi-line single-quoted JS translation strings; use escaped `\n` or template literals, then verify with `node --check site-auth.js`. Also run `auth_download_static_test.py`, a key-coverage check comparing all admin `data-i18n*` keys to `consoleTranslations`, a small Node DOM simulation for switching English→Chinese, and public Hermes Proxy marker checks for `admin.html`, `site-auth.js`, and `styles.css`.

When extending the AI Solo Web Agency Manual with chatbot/knowledge-base instructions, first decide whether the user expects content inside the existing Web Agency Manual or a visible new console feature. If they ask for a “guide”, “setup guide”, or later say they do not see a new menu, create a dedicated backend console panel instead of only adding cards inside the existing manual. Update all three admin-console layers together: add a left-sidebar `.backend-menu-item` with `data-admin-panel-target="chatbot-kb-guide"`, add a dashboard `.backend-feature-card` with the same target, and add a matching `<section data-admin-panel="chatbot-kb-guide" id="admin-panel-chatbot-kb-guide">` in `/mnt/c/Users/jianl/solo-company-class-site/admin.html`. Add matching English and Chinese `menu.*`, `card.*`, and `chatkb.*` keys in `site-auth.js`, and extend `auth_download_static_test.py` with markers for the new menu target, panel target, titles/examples/checklist items, and translation keys. Recommended content should explain that new websites can request the Easiio chatbot during site creation, every site needs a stable `site_id`, page-view tracking is optional, lead forms stay disabled unless explicitly requested, and chatbot knowledge can come from visible page text, manual RAG entries, or wiki pages published with `rag_enabled` and `sync_to_rag`. Verify with `python3 auth_download_static_test.py`, `node --check site-auth.js`, an i18n key-coverage script comparing admin `data-i18n*` keys to both translation dictionaries, a panel-target coverage check, and public Hermes Proxy marker checks for `admin.html` and `site-auth.js` through `https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-ai-solo/`.

When adding an AI Solo backend console user menu for the marketing solution, treat it as a dedicated visible feature panel, not just text inside another manual. Use panel id `marketing-solution`: add a left sidebar button with `data-admin-panel-target="marketing-solution"`, a dashboard `.backend-feature-card` with the same target, and `<section id="admin-panel-marketing-solution" data-admin-panel="marketing-solution">` in `/mnt/c/Users/jianl/solo-company-class-site/admin.html`. Content should map the marketing skill workflow into a user-facing menu: strategy + campaign planning, content calendar/content studio, SEO/GEO + blog briefs, lead detection + CRM handoff, analytics + competitor intelligence, and budget/ROI + multi-brand review. Add English and Chinese `menu.marketingSolution`, `card.marketing.*`, and `marketing.*` translation keys in `site-auth.js`, using escaped `\n` for multi-line prompt examples. Add optional accent CSS markers such as `.marketing-hero-card`, `.marketing-workflow-card`, and `.marketing-checklist` in `styles.css`. Extend `auth_download_static_test.py` with menu/panel/i18n/content/CSS marker assertions, then verify with `python3 auth_download_static_test.py`, `node --check site-auth.js`, an HTML parser check that all `data-admin-panel-target` values have matching `data-admin-panel` sections, an i18n coverage check for both languages, and Hermes Proxy marker fetches for `admin.html`, `site-auth.js`, and `styles.css` if the tunnel is running.

AI Solo local shared-drive behavior: `/api/share/upload` is a login-required multipart upload endpoint in `site_gateway.py` that stores files in the existing upload directory/downloads SQLite table with `source="user_share"`. Files appear in `/api/downloads` alongside `source="local"` admin uploads and `source="google_drive"` folder links, and download through the existing login-required `/download/<stored_name>` route. The public `downloads.html` includes a Google Drive-style workspace (`.drive-workspace`, `.drive-sidebar`, `.drive-main`, `.drive-toolbar`, `.drive-filter-row`, `.drive-upload-card`, `.drive-drop-zone`, `.drive-file-browser`) plus `#shareUploadForm`, `#shareFile`, optional `#shareDescription`, and `#publicDownloads`. `site-auth.js` renders folder cards/search/filter/file cards through `folderCards()`, `bindDriveControls()`, and `initDriveUploadDropZone()`. Keep `ai-solo-welcome-download.txt` as the local-download example and update its content/DB size if using it as documentation for the shared-drive feature.

When adding course users directly to the AI Solo SQLite login database (`/home/jianl/.hermes/tools/website_chatbot/data/ai_solo_site.db`), use the same `pbkdf2_sha256$200000$salt$digest` password hash format implemented in `site_gateway.py`, set role to `user`, and verify both the hash locally and `POST /auth/login` through the local gateway or public Hermes Proxy. Optional profile columns (`user_number`, `first_name`, `last_name`) can be added with `ALTER TABLE users ADD COLUMN` without breaking existing auth code. Normalize roster emails by trimming/lowercasing and removing accidental spaces (for example `support @domain.com` -> `support@domain.com`). For requested student passwords, use `FirstnameLastname123` with capitalized first letters; if a student has no last name, use `Firstname123`. If the requested `user_number` is already occupied by another account, preserve the existing account and assign the new student the next available user number; report the reassignment clearly. After upserting, verify the whole roster, not only new rows: no missing emails, all roles are `user`, all password hashes use the expected format, formula-password verification passes, and `POST /auth/login` succeeds for every roster account.

Add/keep a static regression test for this behavior in the site repo (currently `/mnt/c/Users/jianl/solo-company-class-site/auth_download_static_test.py`) that rejects root-relative auth/download fetches, checks the login page's centered/two-column `auth-layout` markup, and asserts the role-aware login redirect guard is present.

For AI Solo login-page UI changes such as password visibility toggles, keep the behavior progressive and frontend-only unless authentication rules change: add semantic HTML controls in `login.html`, implement the DOM behavior in `site-auth.js`, add matching CSS in `styles.css`, and extend `auth_download_static_test.py` with HTML/JS/CSS token checks. Verify with `python3 auth_download_static_test.py`, `node --check site-auth.js`, and a small Node DOM simulation for the interaction when browser automation is unavailable. If the public Hermes Proxy tunnel is already running, also fetch `login.html`, `site-auth.js`, and `styles.css` through the `/p/<tunnel-id>-ai-solo/` URL and check for the expected markers.

For AI Solo admin-console account-menu changes, keep the logout/auth flow centralized in `site-auth.js` and reuse the existing `/auth/me` user object instead of adding backend profile APIs unless needed. In `admin.html`, replace standalone logout areas with a semantic menu wrapper such as `data-console-user-menu`, a toggle like `#userMenuButton`, display hooks (`data-user-display`, `data-user-avatar`), a profile action/details area (`data-profile-action`, `data-profile-details`), and preserve the existing logout marker `data-auth-logout="true"`. Add user-display/initials helpers and menu open/close/Escape/outside-click handling in `site-auth.js`, refresh dynamic text when `applyConsoleLanguage()` changes language, and add CSS for the menu, avatar, dropdown, and profile details in `styles.css`. Extend `auth_download_static_test.py` with HTML/JS/CSS marker assertions, verify with `python3 auth_download_static_test.py`, `node --check site-auth.js`, a small Node DOM simulation for menu/profile/language interactions, and public Hermes Proxy marker fetches for `admin.html`, `site-auth.js`, and `styles.css` through the suffixed `/p/<tunnel-id>-ai-solo/` URL.

For AI Solo profile password changes, implement the feature in the gateway auth layer instead of the chatbot backend. Add authenticated `POST /auth/change-password` in `site_gateway.py` using `_require_logged_in()`, require `current_password`, `new_password`, and `confirm_password`, verify the current password with `_verify_password`, enforce a minimum length such as 8 characters, hash with `_hash_password`, and update only the logged-in user's `users.password_hash` / `updated_at`. Preserve changed admin passwords across restarts: `_ensure_admin_user` should not overwrite an existing admin password just because `AI_SOLO_ADMIN_PASSWORD` is present; require an explicit reset flag such as `AI_SOLO_RESET_ADMIN_PASSWORD=1` for intentional reset. Add the UI inside the existing account/profile menu (`#changePasswordForm`, `#currentPassword`, `#newPassword`, `#confirmPassword`, `#changePasswordStatus`) and handle submission in `site-auth.js` with path-relative `fetch(apiPath('auth/change-password'))`, client-side mismatch/length validation, and localized English/Chinese status strings. Extend `auth_download_static_test.py` with UI/API/handler/CSS markers, then verify with `python3 auth_download_static_test.py`, `node --check site-auth.js`, `python3 -m py_compile /home/jianl/.hermes/tools/website_chatbot/backend/site_gateway.py`, backend unit tests, an isolated temporary-auth-DB password-change flow, and live checks that anonymous `/auth/change-password` returns 401 while admin login still works. Do not perform an automated real admin password change against the production/local auth DB during smoke tests unless the user explicitly asks.

Test message:

```text
I want a demo for AI agents. My email is founder@example.com
```

Expected effect: CRM contact, possible company, deal, activity, website visitor, and website visit are created/updated.

## Pitfalls

- Do not expose CRM SQLite path, MCP server details, or secrets in browser JavaScript.
- Do not hard-code old implementation URLs like `chatbot.easiiodev.ai`.
- Keep production WordPress changes conservative; package locally first and review before activating.
- Browser automation in this WSL environment may fail because Chromium is missing `libnspr4.so`; use Node/HTTP/static tests unless dependencies are fixed.
- Avoid leaving demo servers running after smoke tests.
