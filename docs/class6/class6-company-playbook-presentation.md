# Class 6 Company Playbook Presentation Pack

> Use this pack to present the Class 6 example in Discord chat, in the student/admin web UI, or during a live walkthrough. This is a teaching script, not final legal advice.

## 1. Presentation goal

Show students how an **AI Legal & Compliance Agent** can:

- review legal text in a structured way
- compare clauses against a **company legal playbook**
- flag deviations and missing protections
- create a **human review queue** instead of pretending to replace a lawyer

## 2. Recommended presentation flow

### Slide / message 1 — Why this matters

**Headline:** Small companies sign risky documents before they are ready.

**Talk track:**
- Founders often review service agreements, privacy policies, and terms of service without a repeatable method.
- AI can help organize the review, classify risk, and highlight what must go to human legal review.
- The safe promise is **first-pass review support**, not final legal advice.

### Slide / message 2 — The Class 6 workflow

**Headline:** Document → playbook → risk labels → human review packet

**Talk track:**
1. Identify the document family.
2. Compare the clause against the company playbook.
3. Label the issue low / medium / high risk.
4. Explain why it matters in business language.
5. Escalate high-risk or unclear issues to human review.

### Slide / message 3 — The company legal playbook

**Headline:** A company playbook defines our fallback positions.

**Show:**
- payment timing
- refunds / credits
- renewals
- scope control
- liability cap
- indemnity
- background IP
- privacy / data promises
- termination / suspension rights

**Key line:**
> Without a company playbook, AI can only find generic red flags. With a playbook, AI can compare the document against the company’s actual preferred terms.

### Slide / message 4 — Sample review case 1

**Headline:** Service agreement with unlimited liability and IP transfer

**Talk track:**
- Unlimited liability = high-risk deviation
- Broad payment withholding = high-risk deviation
- Transfer of prompts, templates, and tools = high-risk deviation
- Missing suspension rights for non-payment = missing key protection

**Lesson:** Students learn that AI should recommend redlines and escalation, not blind approval.

### Slide / message 5 — Sample review case 2

**Headline:** Privacy policy with vague retention and broad sharing

**Talk track:**
- Broad sharing language is too vague
- Retention period is under-defined
- Purpose limitation is weak
- Security language is realistic and closer to aligned

**Lesson:** Some clauses are partly good and partly risky; the model should separate those.

### Slide / message 6 — Sample review case 3

**Headline:** Terms of service with auto-renew and unilateral changes

**Talk track:**
- Auto-renew without advance notice = high-risk deviation
- Non-refundable language may be acceptable with note
- Unilateral changes need notice and fairness
- Suspension rights can be aligned with the playbook

**Lesson:** AI can compare mixed-quality terms instead of calling the whole document simply good or bad.

### Slide / message 7 — Human review boundary

**Headline:** What must go to a lawyer or qualified reviewer?

**Escalate when you see:**
- unlimited liability
- broad one-way indemnity
- unclear data/privacy obligations
- background IP transfer
- missing termination or payment protections
- important ambiguity in a real customer-facing contract

### Slide / message 8 — Student deliverable

**Headline:** What students should produce

Students should output:
- document type
- short summary
- risk counts
- flagged findings
- playbook deviations
- human review queue
- next-step recommendation

## 3. Discord-ready short presentation

Copy/paste this directly into Discord when you want a compact walkthrough:

```md
## Class 6 — AI Legal & Compliance Agent

**Goal:** teach AI first-pass legal review, not final legal advice.

### Workflow
Document -> company playbook -> risk labels -> human review queue

### Why the playbook matters
A legal playbook gives the AI our fallback positions on:
- payment terms
- refunds / credits
- renewals
- liability cap
- indemnity
- background IP
- privacy / data handling
- termination / suspension rights

### Sample case 1 — Service agreement
- unlimited liability -> high-risk deviation
- broad payment withholding -> high-risk deviation
- transfer of prompts/templates/tools -> high-risk deviation
- missing non-payment suspension right -> missing key protection

### Sample case 2 — Privacy policy
- broad third-party sharing -> high-risk deviation
- vague retention -> outside playbook
- missing purpose limitation / request path -> missing key protection
- realistic security wording -> aligned

### Sample case 3 — Terms of service
- auto-renew without notice -> high-risk deviation
- unilateral changes by website posting only -> outside playbook
- non-refundable fees -> acceptable with note
- suspension for legal/operational risk -> aligned

### Core rule
High-risk or ambiguous issues must go to human review.
```

## 4. Web UI assets to open during the demo

Open these in the Class 6 web UI docs list:

- `docs/class6/ai-solo-company-legal-playbook.md`
- `docs/class6/playbook-sample-review-cases.md`
- `docs/class6/demo-inputs.md`
- `docs/class6/human-review-checklist.md`

## 5. Suggested live demo order in the web UI

1. Open the **Legal & Compliance Agent** panel.
2. Show the company playbook link first.
3. Load the service agreement demo and explain the strongest red flags.
4. Load the privacy demo and compare vague sharing/retention language.
5. Load the terms demo and show renewal/change-control issues.
6. End by copying the human review packet and reminding students this is **not final legal advice**.
