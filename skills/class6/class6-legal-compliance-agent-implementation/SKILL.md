---
name: class6-legal-compliance-agent-implementation
description: Reusable workflow for implementing or extending Class 6 AI Legal & Compliance Agent on Jian's AI Solo Company class site, including student/admin UI, docs, static-test-first validation, and legal-safety classroom guardrails.
---

# Class 6 Legal & Compliance Agent Implementation

## When to use

Use this skill when preparing or extending **Class 6 — AI Legal & Compliance Agent** for the AI Solo Company class site, especially when the work includes:

- student-facing Class 6 workspace UI
- admin/teacher Class 6 console UI
- classroom docs and demo inputs
- static regression tests for Class 6 markers
- legal/compliance teaching guardrails
- prompt-builder or output scaffolding for first-pass legal/compliance review

Primary site root observed:

```text
/mnt/c/Users/jianl/solo-company-class-site
```

## Core class constraints

Do not drift from the user-corrected Class 6 scope. The lesson must stay focused on:

- **AI Legal & Compliance Agent**
- building a compliance checklist
- reviewing contracts, terms of service, and privacy policies
- flagging high-risk clauses for **human review**
- producing a compliance review workflow

The classroom copy must clearly say:

- this is **first-pass review support**
- this is **not final legal advice**
- high-risk or ambiguous clauses must be **escalated to human review**

Do not imply the AI provides final legal advice.

## Recommended workflow

1. **Inspect existing site structure before editing**
   - Read the current classroom UI files first:
     - `student-workspace.html`
     - `admin.html`
     - `site-auth.js`
     - `styles.css`
   - Inspect current tests to match project conventions, for example:
     - `release_b_test.py`
     - `release_c_test.py`
     - `release_d_test.py`
     - `auth_download_static_test.py`
     - `portal_static_test.py`
   - Inspect nearby class docs such as `docs/class4/test-checklist.md` or existing class folders to match naming/style.

2. **Use static-test-first before implementation**
   - Create a dedicated test such as:
     ```text
     class6_legal_compliance_static_test.py
     ```
   - Make it fail first by asserting markers in:
     - `student-workspace.html`
     - `admin.html`
     - `site-auth.js`
     - `styles.css`
     - `docs/class6/*`
   - Good markers to require:
     - `data-student-panel-target="legal-compliance-agent"`
     - `data-admin-panel-target="legal-compliance-agent"`
     - `student-panel-legal-compliance-agent`
     - `admin-panel-legal-compliance-agent`
     - `first-pass review`
     - `human review`
     - `high-risk`
     - doc references for `service agreement`, `privacy policy`, and `terms of service`

3. **Add the student workspace slice**
   - Add a new left-nav target in `student-workspace.html` using the existing student panel conventions:
     ```html
     data-student-panel-target="legal-compliance-agent"
     ```
   - Add a dashboard/feature card that opens the same panel.
   - Add a full panel section such as:
     ```html
     <section id="student-panel-legal-compliance-agent" ...>
     ```
   - Include:
     - class overview
     - first-pass review boundary statement
     - human-review escalation note
     - checklist/demo/workflow cards
     - structured output guidance

4. **Add the admin/teacher slice**
   - In `admin.html`, add a matching nav target:
     ```html
     data-admin-panel-target="legal-compliance-agent"
     ```
   - Add a feature card pointing to the same panel.
   - Add a full admin panel section such as:
     ```html
     <section id="admin-panel-legal-compliance-agent" class="backend-panel" data-admin-panel="legal-compliance-agent" ...>
     ```
   - Include:
     - teaching overview
     - demo flow
     - classroom configuration/checklist guidance
     - human-review packet or escalation instructions
     - links to docs

5. **Wire panel behavior in `site-auth.js`**
   - Reuse the existing student/admin panel switching pattern.
   - Extend the student workspace panel initialization so the new Class 6 target can be opened from both nav and dashboard cards.
   - If the page uses status cards or default-state text, add Class 6 support there too.
  - For an MVP, prefer static or prompt-helper behavior rather than a real backend legal review API unless explicitly requested.
  - Once a real backend legal review API is requested, do not duplicate heuristic review rules in the site gateway. Route Class 6 review endpoints through the shared engine at `/home/jianl/.hermes/tools/legal_review/core.py` so the website UI and Hermes chat return the same structured review packet.
  - If the Class 6 website has both the repo copy and the Hermes runtime copy of `site_gateway.py`, update both so tests and the live gateway stay in sync.
  - When adding **custom company playbook** support, keep the flow consistent across student, admin, preview, frontend JS, and gateway payload handling:
    - add a third selector option alongside `standard` and `small-solo-company`, for example `custom-company-playbook`
    - show extra inputs only when that option is selected:
      - upload `.md` / `.txt` playbook file
      - or enter a gateway-local playbook path
      - or pick a **saved / recent company playbook** from a secondary dropdown populated by the gateway
    - localize the new selector labels, field labels, help text, refresh button text, and validation errors in both EN and ZH inside `class6ComplianceUiTextByLanguage`
    - add panel-local JS helpers such as:
      - `renderClass6CompliancePlaybookSelection(panel)` to toggle custom fields and relabel selector options when the language changes
      - `renderClass6ComplianceSavedPlaybookOptions(panel, playbooks)` to populate the saved/recent dropdown
      - `loadClass6ComplianceSavedPlaybooks(panel, { force })` to fetch `/api/student/compliance/playbooks` or `/api/admin/compliance/playbooks`
      - `readClass6TextFile(file, language)` to validate and load uploaded `.md/.txt` playbook text
      - `resolveClass6CompliancePlaybookPayload(panel)` to return one of:
        - `{ playbook_id: 'standard' }`
        - `{ playbook_id: 'small-solo-company' }`
        - `{ playbook_id: 'custom-company-playbook', playbook_path: '...' }`
        - `{ playbook_id: 'custom-company-playbook', playbook_text: '...' }`
        - `{ playbook_id: '<saved-playbook-id>' }`
    - clear the saved-playbook selection when the user types a local path or picks a new file, and clear the path/file inputs when the user chooses a saved playbook
    - wire both structured-text review and uploaded-document review so they forward `playbook_id`, and when needed `playbook_path` or `playbook_text`
    - persist uploaded/path-based custom playbooks in the gateway so later reviews can reuse them by id; a proven pattern is:
      - store text files under `/home/jianl/.hermes/tools/website_chatbot/data/class6_saved_playbooks/`
      - maintain an `index.json` there with `id`, `title`, `sha256`, `source_kind`, `source_path`, `stored_path`, `uploaded_by_email`, and timestamps
      - deduplicate by content hash **per owner** rather than globally, so one student's save cannot become another student's mutable/shared record by accident
      - update `last_used_at` when a saved playbook is reused, but do **not** overwrite immutable ownership fields during read/reuse flows
    - expose a lightweight list endpoint from both student and admin surfaces via `_handle_compliance_playbooks_list(...)`
      - student responses must be filtered to the acting user's own saved playbooks
      - admin responses may list all entries and may include `source_path`; student responses should not leak gateway-local `source_path`
    - if you add rename/delete actions for saved playbooks, use one shared authorization helper such as `_can_manage_saved_compliance_playbook(entry, user)` and enforce it consistently for:
      - list visibility
      - resolve/reuse of saved playbook ids
      - rename
      - delete
    - update backend `_resolve_compliance_playbook(...)` so it can:
      - persist inline/path-based custom playbooks
      - resolve saved playbook ids back to stored files only when the acting user is allowed to access that entry
      - still preserve built-in behavior for `small-solo-company`
    - attach `saved_playbook` metadata to the review response after persistence/reuse so the frontend can auto-select the just-saved entry
      - if rename/delete endpoints also return a refreshed `playbooks` array, that array must be generated with the same user/admin scoping as the list endpoint or the frontend cache will be cleared incorrectly after a successful mutation
    - update multipart upload handling so `playbook_path` and `playbook_text` are forwarded into `_build_compliance_review(...)`
  - When continuing the next phase after the base panel exists, the most reusable feature slices are:
- demo loaders for `contract`, `privacy`, and `terms`
     - copy actions for `structured summary` and `human review packet`
     - bilingual EN/ZH helper text and linked docs
   - Recommended JS helpers for those slices:
     - `parseClass6DemoLibrary(markdown)` + `fetchClass6DemoLibrary(language)` to read `docs/class6/demo-inputs.md` or `docs/class6/demo-inputs-zh.md` instead of hardcoding demo text inline
     - `loadClass6ComplianceDemo(kind, panel)` to set document type, load the matching Markdown-backed demo text, refresh the prompt, and show a localized status message
     - `copyClass6ComplianceSummary(panel)` to copy the rendered summary output
     - `buildClass6HumanReviewPacket(review, language)` + `copyClass6HumanReviewPacket(panel)` to turn JSON review output into a clean escalation packet in the active panel language
    - `downloadClass6HumanReviewPacket(panel)` to export the current escalation packet as a `.md` file for classroom handoff
    - `buildClass6StructuredSummaryPacket(review, language)` + `downloadClass6ComplianceSummary(panel)` to export the structured summary itself as a `.md` handout
    - `getClass6ComplianceLanguage(panel)` + `setClass6ComplianceLanguage(panel, language)` to drive a panel-local EN/ZH toggle that switches helper copy, doc lists, demo-library source, prompt templates, and summary placeholders
    - `class6ComplianceUiTextByLanguage` + `renderClass6ComplianceOutputLanguage(panel)` to keep status strings, action-button labels, empty states, and rendered review text aligned with EN/ZH mode
    - `renderClass6CompliancePromptTemplateLabel(panel)` to relabel the prompt-copy buttons when the panel switches between EN and ZH
    - when the classroom experience needs a teacher-friendly walkthrough, add a true **presentation mode** instead of only a static slide grid:
      - keep a small storyboard data model in JS
      - render a single focused slide by default with `Previous`, `Next`, and `Show all slides` / `Focus current slide` controls
      - include a progress label such as `Slide 2 of 8`
      - keep the existing multi-slide overview available as the secondary mode, not the default
      - use browser QA to verify both focused mode and show-all mode, because regressions often only appear when toggling between them
    - for review output, prefer a presentation-friendly packet/shell layout for the rendered summary and human-review handoff, while keeping raw Markdown/JSON available inside collapsible sections for export/debugging
- Keep these actions panel-local so student/admin views stay synchronized without cross-panel state bugs.
- For browser QA without the login gate, a standalone fixture like `class6-browser-preview.html` can opt in with `data-class6-preview-root`, and `site-auth.js` can safely call `initClass6ComplianceWorkspace()` only for that preview page.
- Any saved-playbook actions that require authenticated gateway APIs (refresh, rename, delete) must be preview-aware:
  - guard them with the same capability check used for list loading, such as `canFetchClass6CompliancePlaybooks()`
  - hide or disable those controls in standalone/file preview mode so the preview page does not expose server-only actions that immediately fail

6. **Add minimal dedicated CSS**
   - Follow existing card/grid styling instead of inventing a new visual system.
   - Useful selectors include:
     - `.compliance-agent-hero`
     - `.compliance-agent-grid`
     - `.compliance-agent-card`
   - Add responsive rules for mobile layouts.

7. **Create Class 6 docs**
   - Use a folder such as:
     ```text
     docs/class6/
     ```
   - Recommended files:
     - `test-checklist.md`
     - `demo-inputs.md`
     - `human-review-checklist.md`
     - `service-agreement-checklist.md`
     - `privacy-policy-checklist.md`
     - `terms-of-service-checklist.md`
     - `high-risk-clause-guide.md`
   - When the lesson needs a **company-specific legal playbook** and a reusable demo/presentation flow, also add:
     - `ai-solo-company-legal-playbook.md`
     - `playbook-sample-review-cases.md`
     - `class6-company-playbook-presentation.md`
   - For the next bilingual phase, mirror the classroom handouts with:
     - `demo-inputs-zh.md`
     - `service-agreement-checklist-zh.md`
     - `privacy-policy-checklist-zh.md`
     - `terms-of-service-checklist-zh.md`
     - `high-risk-clause-guide-zh.md`
     - `human-review-checklist-zh.md`
   - Suggested contents:
     - checklist that confirms high-risk clauses are explicitly marked
     - demo inputs for:
       - `service agreement`
       - `privacy policy`
       - `terms of service`
     - human-review packet fields such as clause text, risk label, missing facts, and reviewer notes
   - Add the EN and ZH doc links in both `student-workspace.html` and `admin.html` so the two surfaces stay aligned.
   - If you add playbook-specific docs, also add a dedicated **presentation/demo card** in student/admin UI and in `class6-browser-preview.html` with direct links to the playbook, sample review cases, and presentation pack. This keeps Discord walkthroughs and web walkthroughs synchronized.

8. **Be careful with exact test strings**
   - If the static test checks exact strings, keep the docs synchronized with those exact forms.
   - A real lesson from implementation: title capitalization can break tests. If the test expects lowercase strings like:
     - `service agreement`
     - `privacy policy`
     - `terms of service`
     - `high-risk clauses are explicitly marked.`
     then the docs must use those exact strings.
   - Prefer stable, explicit marker text over loose phrasing when writing tests for static classroom content.

9. **Run verification after implementation**
   - Recommended commands:
     ```bash
     cd /mnt/c/Users/jianl/solo-company-class-site
     node --check site-auth.js
     python3 class6_legal_compliance_static_test.py
     python3 class6_legal_compliance_ui_smoke_test.py
     python3 -m pytest modules/website_chatbot/tests/test_compliance_review.py -q
     python3 class6_legal_compliance_phase2_test.py
     python3 release_d_test.py
     python3 auth_download_static_test.py
     python3 portal_static_test.py
     python3 release_b_test.py
     python3 release_c_test.py
     ```
  - For simple UI-only checks, serving the repo locally with something like `python3 -m http.server 8765` is enough. But for **upload review** or **local document path review**, prefer a temporary preview server that serves the static site **and** proxies the real auth/review endpoints, then open `class6-browser-preview.html` there (a proven local URL was `http://127.0.0.1:8787/class6-browser-preview.html`). A plain static server is not enough for end-to-end review flow validation.
  - Recommended browser QA sequence for the full review workflow:
    1. log in through the preview server
    2. open `class6-browser-preview.html`
    3. run **local-path review** with a temporary high-risk sample file such as `/tmp/class6-browser-local-path.txt`
    4. verify the panel shows structured summary, source/path metadata, findings, and a rendered human-review packet
    5. run **uploaded-file review** too; if direct browser file-picker automation is awkward, inject a `File` object into the file input from browser JS and trigger the upload action
    6. rerun the original structured text review to confirm the new renderer did not break the old path
    7. switch to `zh` and confirm packet title, button labels, status text, summary headings, and any playbook-specific section titles / empty states / alignment labels localize correctly
    8. clear/read browser console and confirm there are no JS errors
  - When the preview server is only for local QA, keep it temporary and shut it down after validation so you do not leave stale background processes around.
  - If Hermes browser automation fails with missing NSS/NSPR libraries, verify the Playwright Chrome binary under `~/.cache/ms-playwright/chromium-*/chrome-linux64/` can run via a local wrapper script plus copied `libnspr4/libnss3` family `.so` files extracted from `apt download libnspr4 libnss3`.
  - If you extend the backend rule engine, add or update a focused pytest file under:
     ```text
     modules/website_chatbot/tests/test_compliance_review.py
     ```
   - For custom playbook support, add at least one focused pytest that calls `_build_compliance_review(...)` with inline `playbook_text` plus a custom `playbook_id` and asserts the returned review keeps that custom playbook metadata and emits non-empty `playbook_summary` / `playbook_deviations`.
   - Extend `class6_legal_compliance_ui_smoke_test.py` with tokens for the custom selector option and custom playbook field markers so static regressions are caught before browser QA.
    - If you add playbook/presentation docs to the UI, also extend both `class6_legal_compliance_static_test.py` and `class6_legal_compliance_ui_smoke_test.py` to assert the new doc links are present in `student-workspace.html`, `admin.html`, and `class6-browser-preview.html`.
   - If you add or change storyboard / presentation-mode UI, update both `class6_legal_compliance_static_test.py` and `class6_legal_compliance_ui_smoke_test.py` in the same pass so tokens like slide labels, toggle text, and presentation controls do not drift from the implementation.
   - Important preview-language pitfall: the Class 6 EN/ZH language toggle is panel-local. Any doc/link sections placed **outside** the `[data-student-compliance-panel]` root in `class6-browser-preview.html` will not automatically switch when the panel language changes. For preview-only header/asset sections, either (a) keep bilingual content visible at once, or (b) move the content inside the panel root instead of relying on hidden `data-class6-language-block` nodes outside the panel.
- Verify helper functions referenced by backend review payloads actually exist. A real bug found during implementation was a missing `utc_timestamp()` helper referenced by the compliance review response.
   - If the new Class 6 test fails after implementation, inspect exact string mismatches before making broader UI changes.

## Implementation notes

- Prefer a **static classroom MVP** first when the user asks for UI + docs + test, instead of immediately adding a real backend compliance-review API.
- Reuse the existing site conventions:
  - `data-student-panel-target`
  - `data-admin-panel-target`
  - `backend-panel`
- Use targeted file edits and keep the scope local to the Class 6 slice.
- Keep legal/compliance safety language explicit in both student and admin surfaces.
- Avoid creating copy that suggests AI can replace a lawyer or compliance reviewer.

## Pitfalls learned

- The class topic for this lesson may have been corrected by the user. Do not accidentally revert to a different theme such as student Hermes connection work.
- Static tests for docs are often stricter than expected; exact case and punctuation may matter.
- When a new test fails the second time after implementation, check the docs for marker mismatches before changing JS or HTML again.

## Downloadable teacher/demo guide workflow

When the user asks for **Class 6 demo instructions** or a teacher-facing runbook, do not summarize from memory. Build it from the real class assets first.

## Student-ready legal quick-start document workflow

When the user asks for a student-facing legal handout such as **website disclaimer + ToS quick-start templates**, build it from the actual Class 6 legal materials instead of inventing a generic template from scratch.

### Source files to inspect first

Read these before drafting:
- `docs/class6/terms-of-service-checklist-zh.md` or the EN version as appropriate
- `docs/class6/privacy-policy-checklist-zh.md` or the EN version
- `docs/class6/service-agreement-checklist-zh.md` when service language matters
- `docs/class6/ai-solo-company-legal-playbook.md` or the downloadable copy in `/home/jianl/Downloads/`
- any existing Class 6 playbook presentation or demo docs if the handout needs classroom framing

### What the student handout should include

A good student-ready quick-start document should include:
- a clear teaching boundary: first-pass template, not final legal advice
- a short "how to use this" section
- a pre-fill business-info checklist with placeholders such as company name, domain, email, services, refund policy, subscription status, AI usage, and third-party tools
- a simple website disclaimer template
- a simple website ToS template
- AI-output limitation language
- payment / refund / subscription placeholder guidance
- privacy / third-party tool / IP / liability sections in plain language
- a short pre-launch checklist
- common high-risk mistakes students make
- a "when to escalate to human legal review" section
- optional short footer legal text for students who do not yet have a full legal page

### Delivery pattern

Prefer writing both formats:
- Markdown: `/home/jianl/Downloads/<student-doc-name>.md`
- Word-compatible file: `/home/jianl/Downloads/<student-doc-name>.docx`

If `pandoc` is unavailable, generate the `.docx` with Python `docx` support if installed.

### Style guidance

Keep the student version:
- practical
- short-paragraph and checklist friendly
- explicit about placeholders to replace
- conservative about promises (no absolute security, no guaranteed results, no overbroad AI claims)
- clearly separated between website-level disclaimer language and ToS language

### Source files to inspect

Read these before drafting the guide:
- `docs/class6/demo-inputs.md`
- `docs/class6/class6-company-playbook-presentation.md`
- `docs/class6/playbook-sample-review-cases.md`
- `docs/class6/ai-solo-company-legal-playbook.md`
- `docs/class6/test-checklist.md`
- `docs/class6/human-review-checklist.md`
- `skills/class6/legal-compliance-agent/SKILL.md`
- `class6-browser-preview.html`
- `site-auth.js`

### Repo skill-file placement

If you create or maintain a repo-local Class 6 teaching skill, keep the skill file under the top-level repo `skills/` tree, not under `docs/`.

Use:
- `skills/class6/legal-compliance-agent/SKILL.md`

Do not leave the canonical skill only at:
- `docs/class6/.../SKILL.md`

Treat `docs/` as classroom handouts/content and `skills/` as executable procedural assets.

### What the guide should cover

A good downloadable guide should include:
- class goal and safety boundary
- prep/setup steps
- recommended live demo order
- the slide/presentation walkthrough
- the three built-in review demos:
  - service agreement
  - privacy policy
  - terms of service
- custom company playbook flow
- saved playbook selection flow
- upload-file review flow
- local-document-path review flow
- structured JSON / findings / human review packet walkthrough
- short demo version and full class version
- troubleshooting notes

### Important implementation detail

`class6-browser-preview.html` and `site-auth.js` are the fastest way to verify what is actually demoable in the browser UI. Use them to confirm the real panel structure, buttons, output regions, and presentation controls instead of relying only on prose docs.

### Delivery pattern

Write the guide to a downloadable file such as:
- `/home/jianl/Downloads/class6-demo-instructions.md`

If the user wants a Word-compatible file and `pandoc` is unavailable, check whether Python `docx` support exists and generate:
- `/home/jianl/Downloads/class6-demo-instructions.docx`

## Final response checklist

Summarize:

- files changed
- student/admin panel additions
- docs created
- static test path
- exact verification commands and pass/fail result
- whether the implementation is UI/docs-only or includes a real backend review API
- downloadable guide paths when documentation deliverables were requested
