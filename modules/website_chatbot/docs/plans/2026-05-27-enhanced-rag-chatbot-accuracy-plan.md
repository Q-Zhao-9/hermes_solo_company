# Enhanced RAG Chatbot Accuracy Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Improve the AI Solo Company website chatbot answer accuracy by upgrading the current lightweight keyword RAG into a practical enhanced RAG pipeline based on the uploaded `Enhanced_RAG_solution.docx`: semantic chunking, query rewriting, HyDE-style retrieval, hybrid scoring, reranking, context expansion, grounded generation, and verification.

**Architecture:** Keep the current dependency-light chatbot backend as the production baseline and add an incremental, test-driven enhanced RAG layer inside `/home/jianl/.hermes/tools/website_chatbot/backend/app.py`. Phase 1 should not require Qdrant/OpenSearch or new external services; it should implement local semantic metadata, keyword/BM25-like scoring, query expansion, optional LLM HyDE/verification when an API key is configured, deterministic fallbacks when no key is available, and citations/sources in responses. Later phases can move vector retrieval to Qdrant/pgvector and keyword search to OpenSearch/Postgres FTS.

**Tech Stack:** Python stdlib HTTP backend, local JSON RAG content store, in-memory per-site RAG index, existing optional OpenAI-compatible LLM API, Solo CRM SQLite, existing frontend widget and admin customizer.

---

## 1. Current State Summary

Current key file:

```text
/home/jianl/.hermes/tools/website_chatbot/backend/app.py
```

Current RAG behavior:

1. The browser widget sends visible page text in `page_context.content`.
2. `update_site_rag_index(site_id, page_context)` chunks page text and stores chunks in `SITE_RAG_INDEX`.
3. Manual knowledge entries are stored in:

```text
/home/jianl/.hermes/tools/website_chatbot/data/rag_content.json
```

4. `answer_from_site_rag(site_id, message, language)` retrieves chunks by simple token overlap.
5. Optional LLM formatting uses `call_llm_answer_formatter(question, context, language)`.
6. Fallback answer uses `concise_extractive_answer(...)`.
7. Current tests already cover page-context RAG, manual RAG, site isolation, LLM formatting, fallback extraction, and lead-form suppression for factual questions.

Current limitations:

- Chunking is sentence/lesson aware but not truly section/metadata/summary aware.
- Retrieval is mostly token overlap, not hybrid multi-query retrieval.
- No HyDE/simulated-answer retrieval.
- No formal reranking stage.
- Context expansion is limited to a few selected chunks; it does not track previous/next/parent section relationships.
- Final answers do not include robust citations/confidence.
- No verification step to remove unsupported claims when LLM formatting is used.

---

## 2. Target Enhanced RAG Pipeline

Based on the uploaded document, the target pipeline is:

```text
Ingestion
  -> structured document/page parsing
  -> semantic section-aware chunking
  -> chunk metadata + summaries
  -> local hybrid index

Question
  -> intent classification
  -> query rewrite
  -> HyDE simulated answer generation, optional LLM
  -> original-query retrieval
  -> expanded-query retrieval
  -> HyDE retrieval
  -> keyword/BM25 retrieval
  -> summary/title retrieval
  -> merge + deduplicate
  -> rerank
  -> context expansion with neighboring chunks
  -> grounded answer generation with citations
  -> verification / confidence
```

Important rule from the document:

```text
HyDE simulated answers are retrieval aids only. They must never be treated as evidence.
```

---

## 3. Implementation Phases

### Phase 1 — Local Enhanced RAG, no new infrastructure

**Objective:** Improve accuracy while keeping the current backend deployable with stdlib Python and optional LLM.

Add:

- section-aware chunk model
- chunk metadata: `chunk_id`, `site_id`, `source`, `content_id`, `url`, `title`, `section`, `chunk_index`, `prev_id`, `next_id`, `tokens`, `summary`, `search_text`
- deterministic summary fallback from heading + first sentence
- lightweight query intent classification
- deterministic query expansion synonyms for website/course/business questions
- optional LLM query rewrite and HyDE answer generation
- hybrid candidate retrieval from:
  - original query tokens
  - expanded query tokens
  - HyDE tokens
  - chunk summary/title/section tokens
  - exact phrase and number matches
- reranking function with direct-answer/evidence scoring
- neighboring chunk expansion
- grounded answer prompt with citations
- verification function that strips unsupported LLM answers or falls back to extractive answer
- response metadata: `sources`, `confidence`, `retrieval_debug` only in tests/dev if enabled

### Phase 2 — Admin + ingestion quality

**Objective:** Improve manual knowledge quality and admin visibility.

Add admin fields/options:

- title
- URL/source
- category/section
- tags
- last updated
- `rag_enabled`
- chunk preview
- answer test panel: ask a question and show selected chunks/sources/confidence

### Phase 3 — Persistent advanced retrieval backend

**Objective:** Move beyond in-memory/local JSON when site knowledge grows.

Options:

- Qdrant local path for vectors
- SQLite FTS5 or Postgres FTS for keyword index
- pgvector if moving to Postgres
- persistent chunk metadata table

This should be optional and behind env flags.

### Phase 4 — Full document ingestion

**Objective:** Support uploaded PDF/DOCX/HTML/email knowledge with structured extraction.

Use:

- DOCX parser
- HTML parser
- PDF text parser
- table extraction when needed
- Easiio Docs Module sync
- wiki page sync

---

## 4. Detailed Phase 1 Tasks

### Task 1: Add enhanced RAG tests for semantic chunk metadata

**Objective:** Lock in the new chunk structure before changing code.

**Files:**

- Modify: `/home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py`
- Modify: `/home/jianl/.hermes/tools/website_chatbot/backend/app.py`

**Test to add:**

```python
def test_enhanced_rag_chunks_preserve_sections_neighbors_and_summaries(self):
    content = """
    AI Solo Company Bootcamp

    Curriculum
    Lesson 1: Foundation. Install tools and define the business.
    Lesson 2: Website. Build the public website.
    Lesson 3: Website Assistant. Add chatbot, RAG knowledge, CRM, and follow-up email.

    Pricing
    The bootcamp includes 14 lessons.
    """
    chunks = self.app.build_enhanced_rag_chunks(
        site_id="ai-solo-company-class",
        page_context={"url": "https://example.com", "title": "AI Solo", "content": content},
        source="page",
    )
    self.assertGreaterEqual(len(chunks), 3)
    lesson3 = next(chunk for chunk in chunks if "Lesson 3" in chunk["text"])
    self.assertEqual(lesson3["section"], "Curriculum")
    self.assertIn("summary", lesson3)
    self.assertIn("tokens", lesson3)
    self.assertIn("chunk_id", lesson3)
    self.assertTrue(lesson3.get("prev_id") or lesson3.get("next_id"))
```

**Run to verify failure:**

```bash
python3 /home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py -k enhanced_rag_chunks
```

Expected: fail because `build_enhanced_rag_chunks` does not exist.

---

### Task 2: Implement section-aware chunk creation

**Objective:** Replace blind small chunks with structured chunks that preserve document hierarchy.

**Files:**

- Modify: `/home/jianl/.hermes/tools/website_chatbot/backend/app.py`

**Implementation notes:**

Add helpers near existing RAG helpers:

```python
def detect_section_heading(line: str) -> str:
    text = normalize_whitespace(line)
    if not text:
        return ""
    if re.match(r"^(lesson\s+\d+|第\s*\d+\s*课)\b", text, re.I):
        return text[:120]
    if len(text) <= 80 and not re.search(r"[.!?。！？]$", text):
        return text
    return ""


def summarize_chunk(title: str, section: str, text: str) -> str:
    sentences = split_rag_units(text)
    first = sentences[0] if sentences else normalize_whitespace(text)[:180]
    prefix = " / ".join(part for part in [title, section] if part)
    return normalize_whitespace(f"{prefix}: {first}" if prefix else first)[:300]
```

Add `build_enhanced_rag_chunks(...)` that:

1. preserves blank-line paragraph boundaries before normalization when possible;
2. detects short heading lines as sections;
3. starts a new chunk for lesson headings or section changes;
4. targets roughly 300–900 tokens or about 600–2600 chars for current stdlib implementation;
5. assigns stable-ish `chunk_id` using `content_id/source/url/index` or `uuid`;
6. links `prev_id` and `next_id` for same source/URL.

Keep `chunk_website_content(...)` as compatibility fallback if useful, but route `_rag_chunks_from_page_context(...)` through the new enhanced chunker.

**Run:**

```bash
python3 /home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py -k enhanced_rag_chunks
```

Expected: pass.

---

### Task 3: Add query intent and query expansion tests

**Objective:** Ensure questions are rewritten into stronger retrieval forms without requiring an LLM.

**Files:**

- Modify: `/home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py`
- Modify: `/home/jianl/.hermes/tools/website_chatbot/backend/app.py`

**Test to add:**

```python
def test_enhanced_rag_query_plan_expands_course_question(self):
    plan = self.app.build_rag_query_plan("How many classes do you have and what does lesson 3 build?", language="en")
    self.assertEqual(plan["intent"], "fact_lookup")
    combined = " ".join(plan["queries"] + plan["keywords"])
    self.assertIn("lesson", combined.lower())
    self.assertIn("class", combined.lower())
    self.assertIn("course", combined.lower())
    self.assertIn("3", combined)
```

**Implementation notes:**

Add:

```python
def classify_rag_intent(question: str) -> str:
    # fact_lookup, procedure, comparison, summary, troubleshooting, extraction, reasoning
```

Add deterministic query expansion map:

```python
RAG_QUERY_SYNONYMS = {
    "class": ["lesson", "course", "module", "curriculum"],
    "lesson": ["class", "course", "module", "curriculum"],
    "price": ["pricing", "cost", "fee", "tuition"],
    "enroll": ["register", "signup", "join", "报名"],
    "chatbot": ["website assistant", "AI assistant", "RAG", "knowledge base"],
}
```

Add `build_rag_query_plan(question, language)` returning:

```python
{
  "intent": "fact_lookup",
  "queries": [original, expanded_query, metadata_query],
  "keywords": [...],
  "hyde": ""  # filled later when optional LLM is enabled
}
```

---

### Task 4: Add optional HyDE generation

**Objective:** Use the uploaded document’s simulated-answer retrieval idea safely.

**Files:**

- Modify: `/home/jianl/.hermes/tools/website_chatbot/backend/app.py`
- Modify: `/home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py`

**Rules:**

- HyDE is optional: only run if `EASIIO_CHATBOT_LLM_API_KEY` or `OPENAI_API_KEY` is present.
- HyDE text is stored only in the query plan, never as evidence.
- If the LLM call fails, retrieval continues without HyDE.
- Keep timeout short.

**Function:**

```python
def call_llm_hyde_queries(question: str, language: str = "") -> list[str]:
    """Return up to 3 hypothetical answer/query texts for retrieval only."""
```

Prompt requirements:

```text
Generate up to 3 short hypothetical answer-style retrieval queries. Do not invent exact numbers, prices, dates, or guarantees. These will be used only for retrieval, not as evidence.
```

**Test approach:** patch this function to return deterministic HyDE strings and verify they influence retrieval in Task 5.

---

### Task 5: Implement hybrid candidate retrieval

**Objective:** Retrieve better chunks from original query, expanded query, HyDE, summaries, titles/sections, exact keywords, and numeric matches.

**Files:**

- Modify: `/home/jianl/.hermes/tools/website_chatbot/backend/app.py`
- Modify: `/home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py`

**Core function:**

```python
def retrieve_rag_candidates(site_id: str, query_plan: dict[str, Any], *, limit: int = 50) -> list[dict[str, Any]]:
    ...
```

**Scoring formula for local Phase 1:**

```text
final_score =
  0.35 * original token overlap
+ 0.20 * expanded query overlap
+ 0.15 * HyDE token overlap
+ 0.15 * title/section/summary overlap
+ 0.10 * exact phrase / number match
+ 0.05 * metadata/source boost
```

This approximates the document’s formula without vector embeddings.

**Candidate payload:**

```python
{
  "chunk": chunk,
  "score": score,
  "reasons": ["original_overlap", "summary_overlap", "exact_number"],
}
```

**Test to add:**

```python
def test_hybrid_retrieval_uses_summary_and_hyde_to_find_answer_chunk(self):
    # Create chunks where the raw text says "website AI assistant" but the question says "chatbot".
    # Patch call_llm_hyde_queries to include "AI assistant lead capture CRM".
    # Verify Lesson 3 is selected above unrelated lessons.
```

---

### Task 6: Implement reranking and context expansion

**Objective:** Keep only the best evidence chunks and include neighbors when needed.

**Files:**

- Modify: `/home/jianl/.hermes/tools/website_chatbot/backend/app.py`
- Modify: `/home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py`

**Functions:**

```python
def rerank_rag_candidates(question: str, candidates: list[dict[str, Any]], *, keep: int = 8) -> list[dict[str, Any]]:
    ...


def expand_rag_context(site_id: str, ranked: list[dict[str, Any]], *, max_chars: int = MAX_RAG_LLM_CONTEXT_CHARS) -> list[dict[str, Any]]:
    ...
```

Reranking boosts:

- direct answer words in same chunk
- exact lesson number / price / date / name matches
- title/section relevance
- manual source over transient page source when both match equally
- question type match: procedure questions prefer chunks with step/process language

Context expansion rules:

- include previous/next chunk only if same URL/content source and same/compatible section
- do not exceed max context chars
- do not pull unrelated neighboring lesson chunks

---

### Task 7: Grounded answer generation with citations

**Objective:** Make answers cite their evidence and say “not found” when no evidence exists.

**Files:**

- Modify: `/home/jianl/.hermes/tools/website_chatbot/backend/app.py`
- Modify: `/home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py`

**Change `call_llm_answer_formatter(...)`:**

Instead of passing plain concatenated context, pass source-tagged context:

```text
[Source 1]
Title: AI Solo Company Bootcamp
Section: Curriculum / Lesson 3
URL: https://example.com
Text: Lesson 3: Website Assistant...
```

System prompt should say:

```text
Answer only from the provided sources. Cite sources inline as [Source 1]. If the answer is not in the sources, say you do not see it in the current website knowledge. Do not use hypothetical retrieval text as evidence.
```

Response should include:

```python
{
  "reply": answer,
  "answer_source": "website_rag_llm" or "website_rag",
  "sources": [{"title": ..., "url": ..., "section": ..., "source_id": "Source 1"}],
  "confidence": "high|medium|low",
}
```

For public widget UI, citations can stay as text initially; later the widget can render source chips.

---

### Task 8: Add verification / anti-hallucination guard

**Objective:** Reduce unsupported LLM answers.

**Files:**

- Modify: `/home/jianl/.hermes/tools/website_chatbot/backend/app.py`
- Modify: `/home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py`

**Local deterministic verification:**

```python
def verify_grounded_answer(answer: str, selected_chunks: list[dict[str, Any]], question: str) -> dict[str, Any]:
    ...
```

Minimum local checks:

- If answer contains important numbers not found in selected chunks, mark unsupported.
- If answer contains source citations that do not exist, mark unsupported.
- If answer has too little token overlap with evidence and contains strong claims, mark low confidence.
- If unsupported, return fallback extractive answer.

Optional LLM verification can come later.

**Test:**

Patch `call_llm_answer_formatter` to return an unsupported hallucination like “The bootcamp has 30 lessons.” when evidence says 14 lessons. Verify final reply does not contain `30` and falls back to evidence.

---

### Task 9: Wire enhanced pipeline into `answer_from_site_rag(...)`

**Objective:** Replace the simple overlap retrieval with the enhanced pipeline while preserving existing API behavior.

**Current function:**

```text
answer_from_site_rag(site_id, message, language)
```

**New internal flow:**

```python
refresh_manual_rag_index(site_id)
query_plan = build_rag_query_plan(message, language)
query_plan["hyde_queries"] = call_llm_hyde_queries(...) if enabled else []
candidates = retrieve_rag_candidates(site_id, query_plan, limit=50)
ranked = rerank_rag_candidates(message, candidates, keep=8)
selected = expand_rag_context(site_id, ranked, max_chars=MAX_RAG_LLM_CONTEXT_CHARS)
answer = direct_count_answer(...) or grounded_llm_or_extractive_answer(...)
verified = verify_grounded_answer(...)
return response
```

**Compatibility requirements:**

Existing tests must still pass:

- factual course questions must not trigger lead form
- cached visitor email must not create a new lead on normal factual chat
- site-specific RAG isolation must remain intact
- manual RAG delete must remain site-scoped
- no secrets in responses

---

### Task 10: Add docs and operational toggles

**Objective:** Make enhanced RAG controllable and documented.

**Files:**

- Modify: `/home/jianl/.hermes/tools/website_chatbot/README.md` if present, otherwise create it
- Modify: `/home/jianl/.hermes/tools/website_chatbot/CHATBOT_CRM_IMPLEMENTATION_PLAN.md` if still maintained
- Modify: `/home/jianl/.hermes/skills/web-development/website-chatbot-solo-crm/SKILL.md` after implementation succeeds

**Environment flags:**

```bash
EASIIO_CHATBOT_RAG_MODE=enhanced          # simple|enhanced, default enhanced after tests pass
EASIIO_CHATBOT_RAG_DEBUG=false           # if true, include retrieval_debug in API response for local/admin debugging only
EASIIO_CHATBOT_RAG_HYDE_ENABLED=true     # only active if LLM key exists
EASIIO_CHATBOT_RAG_VERIFY_ENABLED=true
EASIIO_CHATBOT_RAG_MAX_CANDIDATES=50
EASIIO_CHATBOT_RAG_MAX_SELECTED=8
```

Do not expose LLM keys or internal paths to the browser.

---

## 5. Verification Commands

Run after each implementation batch:

```bash
python3 -m py_compile /home/jianl/.hermes/tools/website_chatbot/backend/app.py
python3 /home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py
node /home/jianl/.hermes/tools/website_chatbot/tests/widget_static.test.js
node /home/jianl/.hermes/tools/website_chatbot/tests/wp_plugin_static.test.js
```

If changing the AI Solo deployed website copy or gateway:

```bash
python3 /mnt/c/Users/jianl/solo-company-class-site/auth_download_static_test.py
node --check /mnt/c/Users/jianl/solo-company-class-site/site-auth.js
python3 -m py_compile /home/jianl/.hermes/tools/website_chatbot/backend/site_gateway.py
```

Live smoke after backend restart:

```bash
curl -sS http://127.0.0.1:8099/health
curl -sS -X POST http://127.0.0.1:8099/api/chat/message \
  -H 'Content-Type: application/json' \
  -d '{
    "site_id":"ai-solo-company-class",
    "session_id":"rag_accuracy_test",
    "message":"How many classes are in the bootcamp and what does lesson 3 build?",
    "page_context":{
      "language":"en",
      "url":"https://example.com/ai-solo-company/",
      "title":"AI Solo Company Bootcamp",
      "content":"AI Solo Company Bootcamp. Build Your AI Solo Company Operating System in 14 Lessons. Lesson 1: Foundation. Lesson 2: Website. Lesson 3: Website Assistant and Lead Capture. Configure the website AI assistant, knowledge base, lead form, CRM database, and generate the first follow-up email. Output: AI lead system."
    }
  }'
```

Expected:

- status 200
- answer mentions 14 lessons
- answer mentions Lesson 3 / website assistant / lead capture / CRM / follow-up email
- `lead_captured` is false
- `show_lead_form` is false
- sources are present
- no unsupported numbers

---

## 6. Success Criteria

Phase 1 is successful when:

1. All existing chatbot backend tests pass.
2. New enhanced RAG tests pass.
3. Factual questions answer from the correct site-specific source.
4. Similar wording questions work, e.g. “chatbot” retrieves “website AI assistant”.
5. HyDE, when enabled, improves retrieval but is never cited as evidence.
6. LLM hallucinated numbers/details are rejected or replaced by extractive evidence.
7. No lead form appears for normal factual questions.
8. Manual RAG knowledge remains isolated by `site_id`.
9. API responses do not expose secrets, local DB paths, API keys, or raw internal env values.

---

## 7. Recommended Implementation Order

1. Add tests for enhanced chunks.
2. Implement enhanced chunk metadata.
3. Add tests for query plan and query expansion.
4. Implement query plan.
5. Add tests for hybrid retrieval.
6. Implement hybrid retrieval.
7. Add tests for reranking and context expansion.
8. Implement reranking/context expansion.
9. Add hallucination/verification test.
10. Implement verification fallback.
11. Wire into `answer_from_site_rag`.
12. Run full backend tests.
13. Restart local backend and smoke test public AI Solo site if needed.
14. Update skill notes after implementation.

---

## 8. Later Production Upgrade Path

After Phase 1 is stable, consider this infrastructure path:

```text
Small sites / class demos:
  current local enhanced stdlib RAG

Medium sites:
  SQLite FTS5 keyword index + local embedding cache

Large sites / customer production:
  Qdrant or pgvector for vectors
  PostgreSQL/OpenSearch for keyword search
  metadata table for documents/chunks/revisions
  background ingestion jobs
  admin retrieval-debug panel
```

This avoids overbuilding now while leaving a clean path to the full architecture recommended in the uploaded document.
