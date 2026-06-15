# Class 6 Legal & Compliance Agent Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Add a Class 6 Legal & Compliance Agent to the AI Solo Company class site so instructors and students can review contracts, terms of service, and privacy policies with checklist-driven risk flagging and explicit human-review escalation.

**Architecture:** Start with a classroom-safe MVP that works inside the existing static/admin/student workspace using structured checklist templates, rule-based risk flags, and AI prompt-builder output. Then add a backend review endpoint that returns structured JSON for richer AI-assisted analysis. The UX must make clear that this is first-pass compliance review, not final legal advice.

**Tech Stack:** Static HTML, `site-auth.js`, `styles.css`, Python gateway backend, existing auth/session flow, static Python regression tests, optional backend unit tests.

---

## Product scope

### MVP scope for Class 6

Build these user-visible capabilities:

1. **Legal & Compliance Agent panel** in `admin.html`
2. **Student-facing Class 6 section** in `student-workspace.html`
3. **Document type selector**
4. **Checklist-driven review UI**
5. **Risk flag panel** with `low / medium / high`
6. **Human review required** section
7. **Compliance summary export/copy area**
8. **Sample document/demo inputs** for class
9. **Class 6 docs folder** with examples and checklist files
10. **Static regression test** for all UI markers

### Phase 2 backend enhancement

Add a backend endpoint that can return structured review JSON for pasted text:

- `POST /api/student/compliance/review`
- `POST /api/admin/compliance/review`

Do not start with automatic legal drafting or automatic approval.

---

## Guardrails

These rules must appear in both UI and implementation:

- Never present results as legal advice.
- Always prefer `needs human review` over false confidence.
- High-risk categories must include at least:
  - liability
  - indemnity
  - privacy/data handling
  - IP ownership/transfer
  - termination/cancellation
  - governing law/dispute resolution
- Exported summaries must include a human-review recommendation field.

---

## Files to use

### Existing files to modify

- Modify: `/mnt/c/Users/jianl/solo-company-class-site/admin.html`
- Modify: `/mnt/c/Users/jianl/solo-company-class-site/student-workspace.html`
- Modify: `/mnt/c/Users/jianl/solo-company-class-site/site-auth.js`
- Modify: `/mnt/c/Users/jianl/solo-company-class-site/styles.css`
- Modify: `/mnt/c/Users/jianl/solo-company-class-site/modules/website_chatbot/backend/site_gateway.py`

### New files to create

- Create: `/mnt/c/Users/jianl/solo-company-class-site/class6_legal_compliance_static_test.py`
- Create: `/mnt/c/Users/jianl/solo-company-class-site/docs/class6/service-agreement-checklist.md`
- Create: `/mnt/c/Users/jianl/solo-company-class-site/docs/class6/privacy-policy-checklist.md`
- Create: `/mnt/c/Users/jianl/solo-company-class-site/docs/class6/terms-of-service-checklist.md`
- Create: `/mnt/c/Users/jianl/solo-company-class-site/docs/class6/high-risk-clause-guide.md`
- Create: `/mnt/c/Users/jianl/solo-company-class-site/docs/class6/demo-inputs.md`
- Create: `/mnt/c/Users/jianl/solo-company-class-site/docs/class6/test-checklist.md`
- Create: `/mnt/c/Users/jianl/solo-company-class-site/docs/class6/legal-compliance-agent/SKILL.md`

### Optional backend tests

- Create: `/mnt/c/Users/jianl/solo-company-class-site/modules/website_chatbot/tests/test_compliance_review.py`

---

# Task 1: Inspect current Class 5/Class 4 patterns before editing

**Objective:** Reuse the existing classroom panel and test patterns instead of inventing a new UI structure.

**Files:**
- Read: `/mnt/c/Users/jianl/solo-company-class-site/admin.html`
- Read: `/mnt/c/Users/jianl/solo-company-class-site/student-workspace.html`
- Read: `/mnt/c/Users/jianl/solo-company-class-site/site-auth.js`
- Read: `/mnt/c/Users/jianl/solo-company-class-site/styles.css`
- Read: `/mnt/c/Users/jianl/solo-company-class-site/class5_finance_static_test.py`

**Step 1: Identify the existing menu/panel marker pattern**

Confirm these existing patterns:

```text
data-admin-panel-target="..."
data-admin-panel="..."
backend-feature-card
```

**Step 2: Identify student workspace panel pattern**

Look for student workspace sections and source-badge classes so Class 6 matches the site.

**Step 3: Identify JS init pattern**

Find how `site-auth.js` initializes:

- admin panels
- student workspace panels
- translation keys
- existing finance/skill utilities

**Step 4: Inspect the Class 5 static test style**

Reuse its marker-based test style for the new Class 6 test.

**Step 5: Commit notes only if needed**

No code change yet; this is context gathering.

---

# Task 2: Write the failing Class 6 static regression test first

**Objective:** Create a marker-based test that will fail until the Class 6 lesson assets exist.

**Files:**
- Create: `/mnt/c/Users/jianl/solo-company-class-site/class6_legal_compliance_static_test.py`

**Step 1: Write failing test assertions**

Check for these markers in `admin.html`:

```text
data-admin-panel-target="legal-compliance"
data-admin-panel="legal-compliance"
Legal & Compliance Agent
```

Check for these markers in `student-workspace.html`:

```text
data-legal-compliance-studio
data-compliance-document-type
data-compliance-input
data-compliance-run-review
data-compliance-risk-output
data-compliance-human-review
data-compliance-summary
```

Check for docs:

```text
docs/class6/service-agreement-checklist.md
docs/class6/privacy-policy-checklist.md
docs/class6/terms-of-service-checklist.md
docs/class6/high-risk-clause-guide.md
docs/class6/demo-inputs.md
docs/class6/test-checklist.md
docs/class6/legal-compliance-agent/SKILL.md
```

Check for CSS selectors in `styles.css`:

```text
.legal-compliance-hero-card
.legal-compliance-studio
.compliance-risk-grid
.compliance-summary-card
.compliance-human-review-card
```

Check for JS markers/functions in `site-auth.js`:

```text
initLegalComplianceStudio
buildComplianceChecklistReview
renderComplianceRiskFlags
buildComplianceSummary
```

Check for disclaimer text somewhere in UI or docs:

```text
This is not legal advice
需要人工复核
```

**Step 2: Run test to verify failure**

Run:

```bash
cd /mnt/c/Users/jianl/solo-company-class-site
python3 class6_legal_compliance_static_test.py
```

Expected: FAIL — missing Class 6 markers/assets.

**Step 3: Commit the failing test**

```bash
git add class6_legal_compliance_static_test.py
git commit -m "test: add failing Class 6 compliance static test"
```

---

# Task 3: Add Class 6 docs and teaching skill

**Objective:** Create the teaching/checklist assets before wiring the UI.

**Files:**
- Create: `/mnt/c/Users/jianl/solo-company-class-site/docs/class6/service-agreement-checklist.md`
- Create: `/mnt/c/Users/jianl/solo-company-class-site/docs/class6/privacy-policy-checklist.md`
- Create: `/mnt/c/Users/jianl/solo-company-class-site/docs/class6/terms-of-service-checklist.md`
- Create: `/mnt/c/Users/jianl/solo-company-class-site/docs/class6/high-risk-clause-guide.md`
- Create: `/mnt/c/Users/jianl/solo-company-class-site/docs/class6/demo-inputs.md`
- Create: `/mnt/c/Users/jianl/solo-company-class-site/docs/class6/test-checklist.md`
- Create: `/mnt/c/Users/jianl/solo-company-class-site/docs/class6/legal-compliance-agent/SKILL.md`

**Step 1: Write the service agreement checklist**

Include sections like:

- scope of work
- payment terms
- refund/cancellation
- timeline/delivery
- IP ownership
- confidentiality
- termination
- liability limitation
- dispute/governing law

**Step 2: Write the privacy policy checklist**

Include sections like:

- data collected
- purpose of collection
- cookies/tracking
- third-party tools
- user rights/contact method
- retention/security

**Step 3: Write the terms of service checklist**

Include sections like:

- acceptable use
- payment/refunds
- account or user obligations
- liability limitation
- warranty disclaimer
- dispute/governing law
- change notice

**Step 4: Write the high-risk clause guide**

Document at least these high-risk clause families:

- unlimited liability
- one-sided indemnity
- broad IP transfer
- missing privacy disclosure
- missing confidentiality
- unclear termination/cancellation
- no governing law/dispute clause

**Step 5: Write demo inputs**

Prepare short sample texts for:

- a flawed service agreement
- a weak privacy policy
- an incomplete terms of service

**Step 6: Write test checklist**

Add a teacher-friendly list:

- can the user pick a document type?
- does checklist coverage render?
- are high-risk items highlighted?
- is human review clearly labeled?
- can the summary be copied/exported?

**Step 7: Write teaching skill**

The skill should explain:

- when to use
- required inputs
- output format
- risk categories
- escalation rules
- example prompt
- example output
- “not legal advice” warning

**Step 8: Commit docs/skill**

```bash
git add docs/class6/
git commit -m "docs: add Class 6 legal compliance teaching assets"
```

---

# Task 4: Add the admin menu item and dashboard card

**Objective:** Make the new Class 6 panel discoverable in the admin console.

**Files:**
- Modify: `/mnt/c/Users/jianl/solo-company-class-site/admin.html`

**Step 1: Add left-sidebar menu item**

Add a new button near Finance Agent / Skill Studio:

```html
<button class="backend-menu-item" type="button" data-admin-panel-target="legal-compliance" aria-controls="admin-panel-legal-compliance">
  <span class="backend-menu-icon">⚖</span>
  <span>Legal & Compliance Agent</span>
</button>
```

**Step 2: Add dashboard feature card**

Add a dashboard card in the main card grid:

```html
<button class="backend-feature-card" type="button" data-admin-panel-target="legal-compliance">
  <span>⚖</span>
  <strong>Legal & Compliance Agent</strong>
  <small>Prepare Class 6: review contracts, privacy policies, and terms of service with checklist-driven risk flags and human-review escalation.</small>
</button>
```

**Step 3: Run static test**

Run:

```bash
python3 class6_legal_compliance_static_test.py
```

Expected: still FAIL, but fewer missing markers.

**Step 4: Commit**

```bash
git add admin.html
git commit -m "feat: add Class 6 compliance entry points to admin console"
```

---

# Task 5: Add the admin Legal & Compliance Agent panel markup

**Objective:** Create the main Class 6 admin teaching panel.

**Files:**
- Modify: `/mnt/c/Users/jianl/solo-company-class-site/admin.html`

**Step 1: Add the panel shell**

Create a new section:

```html
<section id="admin-panel-legal-compliance" class="backend-panel" data-admin-panel="legal-compliance" hidden>
```

**Step 2: Add panel header content**

Include:

- title: `Legal & Compliance Agent / 法律与合规 Agent`
- subtitle explaining first-pass review
- explicit warning: `This is not legal advice.`

**Step 3: Add form controls**

Include these markers:

```html
<select data-compliance-document-type>...</select>
<textarea data-compliance-input></textarea>
<button data-compliance-load-demo>Load demo text</button>
<button data-compliance-run-review>Run compliance review</button>
```

**Step 4: Add output sections**

Include:

- checklist coverage area
- risk flag area
- human review area
- compliance summary area

Use markers:

```html
data-compliance-checklist-output
data-compliance-risk-output
data-compliance-human-review
data-compliance-summary
```

**Step 5: Add human review disclaimer card**

Include bilingual copy such as:

```text
This is a first-pass review workflow. High-risk items must be reviewed by a human.
这是首轮审查流程，高风险条款必须人工复核。
```

**Step 6: Commit**

```bash
git add admin.html
git commit -m "feat: add Class 6 compliance admin panel shell"
```

---

# Task 6: Add the student workspace Class 6 panel

**Objective:** Expose a student-safe version of the same lesson in `student-workspace.html`.

**Files:**
- Modify: `/mnt/c/Users/jianl/solo-company-class-site/student-workspace.html`

**Step 1: Add a Class 6 section/card**

Add a section titled:

```text
Legal & Compliance Agent
```

**Step 2: Add a simplified student version of the panel**

Required markers:

```html
data-legal-compliance-studio
data-compliance-document-type
data-compliance-input
data-compliance-run-review
data-compliance-risk-output
data-compliance-human-review
data-compliance-summary
```

**Step 3: Add source explanation**

Make it clear this is a classroom review workflow, not legal signoff.

**Step 4: Add docs links**

Link to:

- `docs/class6/demo-inputs.md`
- `docs/class6/high-risk-clause-guide.md`
- `docs/class6/test-checklist.md`

**Step 5: Commit**

```bash
git add student-workspace.html
git commit -m "feat: add Class 6 compliance panel to student workspace"
```

---

# Task 7: Add JS checklist logic and output formatting

**Objective:** Make the Class 6 panel functional before backend AI integration.

**Files:**
- Modify: `/mnt/c/Users/jianl/solo-company-class-site/site-auth.js`

**Step 1: Add document-type checklist definitions**

Define in JS a structured config object like:

```js
const complianceTemplates = {
  service_agreement: { ... },
  privacy_policy: { ... },
  terms_of_service: { ... },
  contractor_agreement: { ... }
};
```

Each should include:

- checklist items
- high-risk topics
- default human-review triggers
- demo input text

**Step 2: Add `initLegalComplianceStudio()`**

This function should:

- find all `data-legal-compliance-studio` roots
- bind selector/input/buttons
- load demo text
- run checklist/risk rendering

**Step 3: Add `buildComplianceChecklistReview()`**

For MVP, use deterministic heuristics:

- keyword/topic detection
- missing-section detection
- category coverage

Return a structured object like:

```js
{
  documentType,
  checklistCoverage: [...],
  riskFlags: [...],
  missingSections: [...],
  humanReview: [...],
  summaryMarkdown
}
```

**Step 4: Add `renderComplianceRiskFlags()`**

Render low/medium/high issue cards.

Each issue should include:

- topic
- risk level
- why it matters
- suggested follow-up
- human review required

**Step 5: Add `buildComplianceSummary()`**

Build a copyable/exportable summary.

Suggested sections:

- document type
- checklist coverage
- top risks
- missing sections
- human review recommendations
- next actions

**Step 6: Wire into page init**

Ensure the function runs for:

- admin panel
- student workspace panel

**Step 7: Run syntax check**

Run:

```bash
cd /mnt/c/Users/jianl/solo-company-class-site
node --check site-auth.js
```

Expected: PASS.

**Step 8: Commit**

```bash
git add site-auth.js
git commit -m "feat: add Class 6 compliance checklist workflow JS"
```

---

# Task 8: Add CSS for the new compliance lesson UI

**Objective:** Style the panel using the existing class-site design language.

**Files:**
- Modify: `/mnt/c/Users/jianl/solo-company-class-site/styles.css`

**Step 1: Add core selectors**

Add selectors like:

```css
.legal-compliance-hero-card
.legal-compliance-studio
.compliance-risk-grid
.compliance-risk-card
.compliance-summary-card
.compliance-human-review-card
.compliance-checklist-grid
.compliance-disclaimer
```

**Step 2: Style risk levels visually**

Use visible classes for:

- low
- medium
- high

Example:

- green/blue accent for low
- amber for medium
- red for high

**Step 3: Add mobile layout support**

Ensure the panel works on narrower screens.

**Step 4: Run static test**

```bash
python3 class6_legal_compliance_static_test.py
```

Expected: fewer missing selectors, maybe still failing until backend/UI is complete.

**Step 5: Commit**

```bash
git add styles.css
git commit -m "feat: style Class 6 compliance lesson UI"
```

---

# Task 9: Make the static test pass

**Objective:** Finish remaining missing markers/assets until the Class 6 regression test passes.

**Files:**
- Modify: any missing file identified by the test

**Step 1: Run the Class 6 static test**

```bash
cd /mnt/c/Users/jianl/solo-company-class-site
python3 class6_legal_compliance_static_test.py
```

**Step 2: Fix missing markers**

Patch the exact remaining gaps.

**Step 3: Re-run until PASS**

Expected output:

```text
PASS
```

**Step 4: Commit**

```bash
git add admin.html student-workspace.html site-auth.js styles.css class6_legal_compliance_static_test.py docs/class6/
git commit -m "test: pass Class 6 compliance static regression"
```

---

# Task 10: Run the existing regression set

**Objective:** Verify Class 6 did not break prior lessons or auth flows.

**Files:**
- Test only

**Step 1: Run targeted checks**

```bash
cd /mnt/c/Users/jianl/solo-company-class-site
python3 class6_legal_compliance_static_test.py
python3 auth_download_static_test.py
python3 class5_finance_static_test.py
python3 portal_static_test.py
python3 video_meeting_static_test.py
node --check site-auth.js
```

**Step 2: Record any failures**

If a prior test fails because it expected a fixed card count or exact text ordering, patch the test or UI minimally without weakening the actual goal.

**Step 3: Commit only if fixes were needed**

```bash
git add ...
git commit -m "fix: preserve existing class site regressions after Class 6"
```

---

# Task 11: Add optional backend structured review endpoint

**Objective:** Upgrade from rule-based classroom review to backend-assisted structured JSON review.

**Files:**
- Modify: `/mnt/c/Users/jianl/solo-company-class-site/modules/website_chatbot/backend/site_gateway.py`
- Optional Test: `/mnt/c/Users/jianl/solo-company-class-site/modules/website_chatbot/tests/test_compliance_review.py`

**Step 1: Write failing backend test**

If adding backend review, first create a test that asserts:

- authenticated request required
- `document_type` required
- `document_text` required
- response returns JSON with:
  - `document_type`
  - `checklist_coverage`
  - `risk_flags`
  - `missing_sections`
  - `human_review_required`
  - `summary_markdown`

**Step 2: Add endpoint skeleton**

Add routes such as:

```text
POST /api/student/compliance/review
POST /api/admin/compliance/review
```

**Step 3: Implement classroom-safe review logic**

For first backend phase, structured heuristic logic is acceptable.

If later using LLM calls, keep strict output schema and preserve the disclaimer field.

**Step 4: Wire frontend to backend optionally**

If endpoint is reachable, `site-auth.js` can prefer it; otherwise, it can fall back to local checklist logic.

**Step 5: Run backend tests**

Run:

```bash
cd /mnt/c/Users/jianl/solo-company-class-site
python3 -m pytest modules/website_chatbot/tests/test_compliance_review.py -q
```

Expected: PASS.

**Step 6: Commit**

```bash
git add modules/website_chatbot/backend/site_gateway.py modules/website_chatbot/tests/test_compliance_review.py site-auth.js
git commit -m "feat: add backend structured review for Class 6 compliance agent"
```

---

# Task 12: Verify through the local/public class flow

**Objective:** Confirm the lesson is visible in the real teaching environment.

**Files:**
- Test only

**Step 1: Verify local HTML markers if browser automation is unavailable**

If browser testing in WSL is blocked, rely on:

- static marker checks
- JS syntax checks
- optional HTTP fetches of HTML markers

**Step 2: If the local/public gateway is up, confirm the panel is present**

Check the proxied/public site for Class 6 markers such as:

```text
Legal & Compliance Agent
data-admin-panel-target="legal-compliance"
data-legal-compliance-studio
```

**Step 3: Verify demo flow manually**

- pick a document type
- load demo text
- run review
- see checklist coverage
- see at least one high-risk flag
- see a human review recommendation
- copy/export summary

**Step 4: Commit only if final UI tweaks were required**

```bash
git add ...
git commit -m "fix: polish Class 6 compliance demo verification"
```

---

# Recommended demo workflow for the class

Use this exact flow in the lesson:

1. Open **Legal & Compliance Agent**.
2. Select **Client Service Agreement**.
3. Click **Load demo text**.
4. Click **Run compliance review**.
5. Explain checklist coverage.
6. Highlight one `high risk` item and why it needs human review.
7. Switch to **Privacy Policy**.
8. Repeat a shorter review focused on data collection disclosure.
9. Copy/export the compliance summary.

---

# Recommended output format

The final summary shown to students should look like this:

```text
Document type: Client Service Agreement
Checklist coverage:
- Scope of work: Found
- Payment terms: Found but unclear
- Cancellation/refund: Missing
- Liability limitation: Missing
- IP ownership: Unclear

Top risks:
1. Liability limitation — High risk
2. IP ownership ambiguity — High risk
3. Payment timing clarity — Medium risk

Human review required:
- Liability language
- IP ownership wording
- Governing law/dispute language

Next actions:
1. Add cancellation clause
2. Clarify payment due dates
3. Add lawyer-reviewed liability limitation
4. Route to human review
```

---

# Pitfalls

- Do not present outputs as final legal advice.
- Do not build automatic “approved/compliant” language into the MVP.
- Do not overfit to a single jurisdiction.
- Do not rely only on AI text generation without checklists.
- Do not remove existing Class 4/Class 5 panel markers while editing the console.
- Do not break student workspace login/auth markers.

---

# Success criteria

The implementation is successful when:

1. `admin.html` contains a visible **Legal & Compliance Agent** entry and panel.
2. `student-workspace.html` contains a student-safe Class 6 lesson section.
3. The user can select a document type, paste/load text, and run a review.
4. The system shows checklist coverage, risk flags, and human-review guidance.
5. Class docs and a teaching skill exist under `docs/class6/`.
6. `class6_legal_compliance_static_test.py` passes.
7. Existing regression checks still pass.
