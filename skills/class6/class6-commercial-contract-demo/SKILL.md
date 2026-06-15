---
name: class6-commercial-contract-demo
description: Run Class 6 Demo 1 using a commercial customer service agreement (MSA) excerpt that exposes vague payment terms, one-way termination, and unlimited liability.
version: 1.0.0
author: Hermes Agent
---

# Class 6 Commercial Contract Demo

## When to use

Use this skill when the user wants to present or rehearse **Class 6 Demo 1 / 商业合同**, especially the slide showing:

- vague payment timing
- client unilateral termination rights
- unlimited liability / damages exposure
- an AI review result that escalates to **HARD_BLOCK** and human review

This is designed for the polished classroom slide where a solo company receives a customer MSA from a larger client.

## Teaching goal

Show students that the AI legal/compliance agent is not replacing a lawyer. Its job is to:

1. identify business-critical contract traps early
2. explain them in founder-friendly business language
3. compare them to small-company fallback positions
4. block unsafe auto-acceptance
5. escalate high-risk items to human review

## Safety boundary

- This is first-pass review support, not final legal advice.
- Do not say the sample contract is legally approved.
- Any real agreement should go to human legal review before signature.

## Demo assets

Primary sample document:
- `references/class6-demo1-commercial-msa-sample-zh.md`

Optional student-downloadable copies created during prep may live in Downloads, but the canonical reusable classroom reference should stay inside this skill.

## Recommended live demo flow

### Step 1 — frame the scenario
Tell the audience:

> A solo AI services company receives a standard customer framework agreement from a bigger client. The language looks normal, but several clauses could damage cash flow or create existential liability.

### Step 2 — paste or load the sample excerpt
Use the sample excerpt from `references/class6-demo1-commercial-msa-sample-zh.md`.

Focus the audience on these three clauses:
- payment after invoice with no hard deadline
- customer termination for convenience with no compensation
- unlimited damages / liability exposure

### Step 3 — classify as a contract review
Document type should be:
- `contract`

### Step 4 — review against a small-company playbook
Preferred fallback positions to explain:
- payment should be net 7 / net 14 / net 30, not indefinite
- termination for convenience should not strand the service provider with unrecovered costs
- liability should be capped, usually to fees paid or similar bounded exposure

### Step 5 — expected findings
The demo should reliably surface these findings:

1. **付款条款账期极其模糊**
   - risk level: `medium`
   - why it matters: client can delay payment and damage small-company cash flow
   - expected redline: payment due within 30 days of invoice; uncontested amounts still payable

2. **客户拥有单方任意解约特权**
   - risk level: `medium`
   - why it matters: the solo company may already have committed labor, tools, or subcontractor cost
   - expected redline: if not terminated for provider breach, customer should pay incurred costs and agreed termination compensation

3. **无限赔偿导致无限责任敞口**
   - risk level: `high`
   - why it matters: one claim could exceed the entire economics of the project and threaten the company
   - expected redline: cumulative liability cap tied to fees paid under the agreement plus exclusion of indirect/consequential damages

### Step 6 — expected final response posture
The safest teaching outcome is:
- `overall_risk: high`
- `human_review_required: true`
- `response_result: HARD_BLOCK`
- auto-escalate to founder / teacher / legal reviewer

## Suggested teacher talk track

Use business-language commentary such as:

- “The dangerous part is not the legal jargon. It is the combination of delayed payment, no-cost customer exit, and uncapped liability.”
- “For a solo company, one bad clause can matter more than ten pages of harmless boilerplate.”
- “The AI agent’s value is early interception and structured escalation, not pretending to replace a lawyer.”

## Good output shape

A strong demo output should include:
- short summary
- overall risk
- risk counts
- 3 findings with clause excerpts
- human review queue
- suggested redlines
- final escalation / block recommendation

## Pitfalls

- Do not soften the unlimited liability issue to medium; it should remain the red-line risk.
- Do not present vague payment timing as harmless just because payment is mentioned.
- Do not let the audience think a “standard client template” is automatically fair.
- Do not omit the human-review boundary.

## Related references

- `class6/legal-playbook-review`
- `class6/class6-legal-compliance-agent-implementation`
