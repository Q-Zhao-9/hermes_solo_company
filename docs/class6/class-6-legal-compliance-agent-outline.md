# AI Solo Company Class 6 Outline — AI Legal & Compliance Agent

**Class 6 working title:** Build Your First AI Legal & Compliance Review Workflow  
**Chinese title:** 第 6 课：AI 法律与合规 Agent  
**Theme:** Use AI to create a first-pass compliance review workflow for contracts, terms of service, and privacy policies, while clearly escalating high-risk items to human review.  
**Recommended duration:** 90 minutes  
**Target deliverable:** 合规检查流程 / compliance checking workflow

---

## 1. Class 6 positioning

Class 3 taught students how to turn a website into an AI assistant + lead capture system.

Class 4 taught students how to customize business behavior with Hermes Skills.

Class 5 taught students how to structure finance review and export workflows.

Class 6 should teach students how to use AI as a **first-pass legal and compliance reviewer**.

The key message:

> AI should not replace a lawyer. AI should help founders review documents systematically, detect missing sections, flag risky clauses, and route high-risk issues to human review.

---

## 2. Learning goals

By the end of Class 6, students should be able to:

1. Explain what an AI legal/compliance agent should and should not do.
2. Separate:
   - checklist review
   - clause/risk scanning
   - business-policy review
   - human/legal escalation
3. Review three core document families:
   - contracts / agreements
   - privacy policy
   - terms of service
4. Use a simple risk rubric:
   - low risk
   - medium risk
   - high risk
5. Produce a structured compliance output containing:
   - checklist coverage
   - flagged issues
   - missing sections
   - human review recommendations
6. Turn document review into a reusable compliance workflow for a solo company.

---

## 3. Current setup we should use in class

Use the current AI Solo Company class site as the teaching surface:

### Website/class site

```text
/mnt/c/Users/jianl/solo-company-class-site
```

### Existing console/workspace surfaces

Relevant files:

```text
admin.html
student-workspace.html
site-auth.js
styles.css
```

These already support prior lessons such as:

- Finance Agent
- Hermes Skill Studio
- Student Hermes Connection

Class 6 should extend the same product story by adding:

```text
Legal & Compliance Agent / 法律与合规 Agent
```

### Existing backend pattern

The site already uses a local gateway + backend pattern for authenticated tools:

```text
modules/website_chatbot/backend/site_gateway.py
modules/website_chatbot/tests/test_site_gateway_auth.py
```

Class 6 should follow the same safe pattern:

- structured review workflow
- clear role labels
- no final legal advice claims
- explicit human-review gating

---

## 4. Recommended class story arc

### Big story

Class 6 should start from a founder problem, not from legal theory:

> A small company signs client agreements, hires contractors, runs a website, and collects user data. Most founders do not know what is missing, what is risky, or when a lawyer must review something. AI can help organize that review.

### Before Class 6

Students already saw:

```text
Website traffic → lead capture → CRM → follow-up
Skill editing → business workflow customization
Finance review → structured business records
```

### During Class 6

Students learn:

```text
Document text
  → document type selection
  → compliance checklist
  → clause/risk scan
  → missing-section detection
  → human-review escalation
  → compliance summary
```

### After Class 6

Students should be able to say:

```text
I can use AI to run a first-pass compliance review workflow before sending high-risk issues to a human reviewer.
```

---

## 5. Recommended 90-minute teaching flow

| Time | Segment | Goal |
|---:|---|---|
| 0–8 min | Opening: why compliance matters | Connect websites, contracts, and data handling to real business risk |
| 8–18 min | What an AI legal/compliance agent is | Define scope: review assistant, not final legal authority |
| 18–30 min | The compliance workflow | Teach intake → checklist → risk flags → escalation |
| 30–45 min | Demo 1: service agreement review | Show missing sections and high-risk clauses |
| 45–58 min | Demo 2: privacy policy review | Show website/data compliance review |
| 58–70 min | Demo 3: terms of service review | Show platform/website legal page review |
| 70–82 min | Student exercise | Students review one sample document and produce top findings |
| 82–88 min | Human review boundary | Explain lawyer/founder escalation rules |
| 88–90 min | Wrap-up | Deliverable, workflow recap, and next-class bridge |

---

## 6. Slide-by-slide PPT outline

### Slide 1 — Title

**Class 6: AI Legal & Compliance Agent**

Subtitle:

```text
Review contracts, terms of service, and privacy policies with AI — then route high-risk issues to human review.
```

Visual:

```text
Document → Checklist → Risk Flags → Human Review → Compliance Summary
```

---

### Slide 2 — Where Class 6 fits in the 14-class bootcamp

Show the 14-class journey with Class 6 highlighted.

Earlier classes:

- website foundation
- AI assistant + lead capture
- Hermes skill customization
- finance workflow

Class 6:

- AI legal/compliance review workflow

Later classes:

- sales automation
- support automation
- marketing operations
- launch and business systems

Speaker point:

> Class 6 teaches students how to reduce risk and review business documents systematically.

---

### Slide 3 — The founder problem

Most small businesses must review:

- client service agreements
- contractor/freelancer agreements
- privacy policies
- terms of service
- refund/cancellation language
- data collection disclosures

But founders often do not know:

- what is missing
- what is risky
- what requires human review

Speaker point:

> Many founders do not need a full legal department — but they do need a repeatable way to spot risk early.

---

### Slide 4 — What the AI agent should do

**AI can help with:**

- checklist review
- missing section detection
- clause summarization
- risk flagging
- follow-up question generation
- escalation preparation

**AI should not do:**

- claim final legal approval
- replace lawyer review
- pretend uncertain clauses are safe
- give jurisdiction-specific final legal advice

Speaker point:

> The class is about first-pass review, not final legal signoff.

---

### Slide 5 — The Class 6 workflow

Large pipeline diagram:

```text
Document intake
→ Document type detection
→ Checklist selection
→ Clause scan
→ Risk flagging
→ Missing section detection
→ Human review escalation
→ Compliance summary
```

This is the core class deliverable.

---

### Slide 6 — Three core document types

Split into three panels:

1. **Contracts / agreements**
   - service agreement
   - contractor agreement
   - NDA
   - partnership terms

2. **Website policies**
   - privacy policy
   - terms of service
   - refund policy
   - consent language

3. **Internal compliance checklist**
   - data collection
   - customer disclosures
   - confidentiality
   - liability

Speaker point:

> These are the most common legal/compliance surfaces for an AI solo company.

---

### Slide 7 — How checklist review works

Explain that each document type should have its own checklist.

Examples:

**Service agreement checklist**
- scope of work
- payment terms
- refund/cancellation
- delivery timeline
- IP ownership
- confidentiality
- termination
- liability limitation
- dispute/governing law

**Privacy policy checklist**
- what data is collected
- why data is collected
- cookies/tracking
- third-party tools
- user rights/contact method
- retention/security language

---

### Slide 8 — Risk scoring model

Teach a simple 3-level rubric.

**Low risk**
- formatting issue
- minor wording cleanup
- small missing detail

**Medium risk**
- ambiguous payment terms
- weak refund language
- unclear ownership
- incomplete privacy wording

**High risk**
- unlimited liability
- one-sided indemnity
- no data/privacy disclosures
- no governing law / dispute clause
- no confidentiality where needed
- broad IP transfer

Speaker point:

> A simple risk framework makes AI review understandable and actionable.

---

### Slide 9 — Human review gate

Show a decision tree:

```text
If issue is high risk
  → send to human/legal review
If issue affects liability, privacy, IP, or dispute handling
  → send to human/legal review
If issue is wording clarity only
  → revise internally first
```

Add a warning:

```text
AI review is a first-pass operational tool, not final legal advice.
```

---

### Slide 10 — Demo system on the AI Solo class website

Show the planned Class 6 UI:

- Legal & Compliance Agent panel
- document type selector
- input area for pasted text
- checklist results
- risk flags
- human-review section
- export summary

Speaker point:

> We are turning legal/compliance review into a repeatable founder workflow, not just a prompt.

---

### Slide 11 — Demo 1: service agreement review

Use a sample agreement with issues such as:

- unclear payment timeline
- no cancellation clause
- no liability limitation
- weak IP ownership wording

Expected output:

- checklist coverage
- missing sections
- top risks
- review recommendations

---

### Slide 12 — Demo 2: privacy policy review

Use a sample website privacy policy.

Check for:

- data types collected
- cookie/tracking disclosure
- third-party services
- user rights/contact path
- retention/security wording

Expected output:

- missing items
- medium/high risk flags
- website compliance next steps

---

### Slide 13 — Demo 3: terms of service review

Use a sample ToS.

Check for:

- acceptable use
- refund/cancellation language
- liability limitation
- dispute/governing law
- change/update notice

Expected output:

- flagged business risk
- missing clauses
- founder review checklist

---

### Slide 14 — Example structured output

Show the output format students should aim for:

```text
Document type
Checklist coverage
Flagged clauses
Risk level
Missing sections
Human review required
Next actions
```

Optional table columns:

- clause/topic
- status
- risk level
- why it matters
- suggested follow-up
- human review required

---

### Slide 15 — Why this matters for AI solo companies

Tie back to real business operations:

- client work
- contractors
- website policies
- user data collection
- partner agreements
- founder protection

Speaker point:

> A solo company that automates growth but ignores compliance is building on weak foundations.

---

### Slide 16 — Student exercise

Each student chooses one document type:

- service agreement
- privacy policy
- terms of service
- contractor agreement

Then submits:

1. checklist coverage
2. top 3 risks
3. missing sections
4. human review items
5. compliance next-step plan

---

### Slide 17 — Common mistakes to avoid

- treating AI output as final legal approval
- ignoring jurisdiction-specific rules
- marking high-risk items as resolved without human review
- using vague prompts with no checklist
- reviewing only wording but not missing sections

---

### Slide 18 — Final takeaway

Main message:

> The goal is not to build an AI lawyer. The goal is to build a repeatable compliance review workflow that helps a founder detect risk earlier and escalate the right issues.

Closing deliverable:

```text
合规检查流程
```

---

## 7. Recommended live demo flow

Use this sequence in class:

1. Open the Class 6 Legal & Compliance Agent panel.
2. Select `Client Service Agreement`.
3. Paste a sample agreement with 3–4 intentional issues.
4. Run the review and show checklist coverage.
5. Highlight the high-risk items and explain why they require human review.
6. Switch to `Privacy Policy` and repeat a shorter review.
7. Export the compliance summary.

---

## 8. Recommended student exercise

Prompt students to complete this template:

```text
Document type:
Checklist coverage:
Top 3 risks:
Missing sections:
Needs human/legal review for:
Next actions:
```

This becomes the class deliverable.

---

## 9. Teaching guardrails

Always repeat these constraints:

- This tool is for review support, not final legal advice.
- High-risk clauses must be routed to human review.
- Privacy, liability, IP, and dispute language should be treated conservatively.
- The system should prefer `flag for review` over false confidence.

---

## 10. Suggested next-class bridge

Possible bridge to the next class:

- connect compliance outputs into CRM/project workflows
- turn review findings into operational tasks
- create reusable business policy templates
