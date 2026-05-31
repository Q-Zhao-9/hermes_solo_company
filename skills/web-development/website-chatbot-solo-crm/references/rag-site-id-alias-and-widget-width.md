# RAG site-id alias and chatbot width troubleshooting

Use this note when the website chatbot:

- answers with a lead-capture/email fallback instead of known website facts; or
- visually cuts off text, quick buttons, or composer buttons.

## Root cause pattern

A common cause is a mismatch between the browser widget `data-site-id` and the keys in `data/rag_content.json`.

Example discovered during the AI Solo Company chatbot fix:

- demo page used `data-site-id="ai-solo-company"`
- existing knowledge was mostly under `ai-solo-company-class`
- backend could not find strong matching RAG content and fell back to sales handoff text

## Reusable fix

1. Inspect the widget/page `data-site-id`.
2. Inspect `/home/jianl/.hermes/tools/website_chatbot/data/rag_content.json` for matching site keys.
3. If the site has known aliases, add a server-side alias in `/home/jianl/.hermes/tools/website_chatbot/backend/app.py`, for example:

```python
"ai-solo-company" -> "ai-solo-company-class"
```

4. Optionally duplicate canonical facts under both site ids when useful for portability.
5. Make the fallback answer reader-friendly. Avoid immediately asking for work email unless the user explicitly wants human follow-up.
6. Verify known factual questions return RAG answers with no lead form.

## Widget width / cut-off fix pattern

Patch `/home/jianl/.hermes/tools/website_chatbot/widget/widget.css`:

```css
width: min(460px, calc(100vw - 32px));
overflow-wrap: anywhere;
```

Also allow quick-action buttons and composer controls to wrap on narrow screens. After changing widget CSS/JS, cache-bust demo URLs, for example:

```html
<script src="widget.js?v=YYYYMMDD-width-rag-fix"></script>
```

## Verification

Run local checks:

```bash
cd /home/jianl/.hermes/tools/website_chatbot
node --check widget/widget.js
node tests/widget_static.test.js
python3 -m py_compile backend/app.py
python3 tests/test_backend.py -v
```

Then run a live API smoke test through Hermes Proxy or the deployed backend. Confirm known site questions return:

```json
{
  "answer_source": "website_rag",
  "show_lead_form": false,
  "confidence": "high"
}
```

For the AI Solo Company course, known smoke questions include:

- `how many lessons are in the AI Solo Company bootcamp?` should answer `14` lessons/classes.
- `What does lesson 3 build?` should answer with the AI lead system, website assistant, RAG/knowledge base, lead form, CRM database, and first follow-up email.
