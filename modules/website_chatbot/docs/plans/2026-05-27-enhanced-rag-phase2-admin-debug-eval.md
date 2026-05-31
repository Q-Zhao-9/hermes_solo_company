# Enhanced RAG Phase 2 — Admin, Debug, Evaluation, and Feedback

## Purpose

Phase 1 improved local retrieval quality with section-aware chunks, query expansion, hybrid scoring, reranking, grounded answer formatting, and verification.

Phase 2 adds an operational layer so the chatbot owner can manage and improve RAG quality over time.

## Implemented scope

### Backend endpoints

- `POST /api/rag/debug`
  - accepts `site_id`, `question`, optional `page_context`, and optional `language`
  - returns query intent, expanded query plan, candidate scores/reasons, reranked chunks, selected sources/chunks, answer, and confidence

- `GET /api/rag/answer-log?site_id=...`
  - returns sanitized answer-quality logs for one site only
  - stores question, answer, answer source, confidence, sources, fallback flag, and timestamp
  - masks emails and phone numbers

- `POST /api/rag/feedback`
  - records helpful / not-helpful / neutral feedback
  - accepts optional reason/comment and answer log id
  - masks emails and phone numbers

- `GET /api/rag/feedback?site_id=...`
  - lists feedback for one site only

- `POST /api/rag/eval`
  - runs a small golden Q&A set for a site
  - supports `expected_answer_contains` and `expected_source_contains`
  - returns pass/fail summary and per-case results

### Widget feedback

RAG answers now render lightweight feedback controls:

```text
Was this helpful? 👍 👎
```

Feedback posts to `/api/rag/feedback` with `site_id`, question, answer, answer log id, rating, answer source, and confidence.

### Admin customizer

The reusable admin module now includes a **RAG debug + evaluation** card:

- debug a test question
- inspect candidate scores/reasons
- view answer confidence
- load answer logs
- send admin feedback
- run a small sample eval

## Data stores

Default local stores:

```text
/home/jianl/.hermes/tools/website_chatbot/data/rag_answer_log.json
/home/jianl/.hermes/tools/website_chatbot/data/rag_feedback.json
```

Environment overrides:

```bash
EASIIO_CHATBOT_RAG_ANSWER_LOG=/path/to/rag_answer_log.json
EASIIO_CHATBOT_RAG_FEEDBACK_STORE=/path/to/rag_feedback.json
EASIIO_CHATBOT_RAG_ANSWER_LOG_MAX=500
EASIIO_CHATBOT_RAG_FEEDBACK_MAX=500
```

## Safety rules

- No LLM/API/CRM/email secrets are exposed to the browser.
- Logs and feedback are filtered by `site_id`.
- Emails and phone numbers are masked before writing answer logs/feedback.
- HyDE remains retrieval-only and is not cited as evidence.

## Verification commands

```bash
python3 -m py_compile /home/jianl/.hermes/tools/website_chatbot/backend/app.py /home/jianl/.hermes/tools/website_chatbot/backend/site_gateway.py
python3 /home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py -v
node --check /home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.js
node --check /home/jianl/.hermes/tools/website_chatbot/widget/widget.js
node /home/jianl/.hermes/tools/website_chatbot/tests/admin_customizer_static.test.js
node /home/jianl/.hermes/tools/website_chatbot/tests/widget_static.test.js
node /home/jianl/.hermes/tools/website_chatbot/tests/wp_plugin_static.test.js
```

## Suggested Phase 3

Phase 3 should connect more knowledge sources into RAG:

- Easiio Wiki Module pages with `rag_enabled`
- Easiio Docs Module published pages
- WordPress pages/posts via plugin/admin sync
- uploaded PDFs/docs after extraction
- stale-content and sync-status reporting
