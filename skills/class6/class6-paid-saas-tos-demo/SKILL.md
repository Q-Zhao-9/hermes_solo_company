---
name: class6-paid-saas-tos-demo
description: Run Class 6 Demo 3 using a paid SaaS Terms of Service excerpt with weak refund defenses, missing dispute venue language, and a dangerous AI-official-guidance claim.
version: 1.0.0
author: Hermes Agent
---

# Class 6 Paid SaaS ToS Demo

## When to use

Use this skill when the user wants to present or rehearse **Class 6 Demo 3 / 平台条款**, especially the slide showing:

- weak or missing refund-defense language
- missing dispute venue / governing-law protection
- AI output incorrectly framed as official platform guidance
- an AI review result that escalates to **HARD_BLOCK** before launch

## Teaching goal

Show students that the AI legal/compliance agent can review a paid SaaS platform's ToS and catch the exact places where the founder failed to protect the business.

This demo should teach that a short or “friendly” ToS is not automatically safer. In many cases it is more dangerous because key defense clauses are missing.

## Safety boundary

- This is first-pass review support, not final legal advice.
- Do not say the sample ToS is legally safe.
- Real launch, billing, and dispute terms should go to human legal review before production use.

## Reuse vs. existing skills

The broader Class 6 skills still apply:
- `class6/legal-playbook-review`
- `docs/class6/legal-compliance-agent/SKILL.md`

This demo skill exists because the slide requires a **specific paid-platform ToS scenario and expected findings**.

## Demo assets

Primary sample document:
- `references/class6-demo3-paid-saas-tos-sample-zh.md`

## Recommended live demo flow

### Step 1 — frame the scenario
Tell the audience:

> A solo founder launches a paid SaaS platform quickly and writes a short ToS just to get the checkout page online. The text sounds harmless, but it is missing the exact clauses the company would need once users dispute charges, demand refunds, or rely too heavily on AI answers.

### Step 2 — load the sample ToS excerpt
Use the sample excerpt from `references/class6-demo3-paid-saas-tos-sample-zh.md`.

The audience should notice three suspicious areas:
- subscription/payment language with no real refund-defense structure
- dispute language that only says “friendly consultation”
- AI answers described as official guidance

### Step 3 — classify as a terms review
Document type should be:
- `terms`

### Step 4 — compare against a small-company playbook
Preferred positions to explain:
- refunds for digital/AI services should be narrow, explicit, and tied to actual usage/consumption
- dispute venue and governing law should be practical for the small operator
- AI outputs should be framed as assistive information, not formal professional advice

### Step 5 — expected findings
The demo should reliably surface these findings:

1. **缺失强硬的无理由退款限制规则**
   - risk level: `medium`
   - why it matters: malicious users can consume API/model resources and then seek refunds or chargebacks
   - expected follow-up: add a narrow refund policy with consumption-based limits and billing-error exceptions

2. **缺失特定纠纷唯一的法庭管辖声明**
   - risk level: `medium`
   - why it matters: without venue protection, the founder may face distant or costly disputes
   - expected follow-up: add governing-law and venue language tied to the operator's practical location

3. **将 AI 回答误写为“官方指导意见”**
   - risk level: `high`
   - why it matters: it upgrades model output and hallucinations into the platform's own formal representation
   - expected follow-up: add a hard AI disclaimer and require human/professional review for high-risk decisions

### Step 6 — expected final response posture
The safest teaching outcome is:
- `overall_risk: high`
- `human_review_required: true`
- `response_result: HARD_BLOCK`
- block launch until the missing defensive clauses are added

## Suggested teacher talk track

Use business-language commentary such as:

- “A paid SaaS business does not fail only because of bugs. It can also fail because its terms never created a defense perimeter.”
- “If the platform lets users pay, dispute, charge back, and rely on AI outputs, the ToS has to define limits clearly.”
- “The AI agent helps catch the exact self-inflicted legal gaps before they go live.”

## Good output shape

A strong demo output should include:
- short summary
- overall risk
- risk counts
- 3 findings with clause excerpts
- human review queue
- suggested rewrite/redline directions
- final launch-block recommendation

## Pitfalls

- Do not reduce the AI-official-guidance issue to a small wording fix; it is the red-line issue.
- Do not present “friendly negotiation” as a substitute for dispute venue language.
- Do not assume paid AI services can safely offer broad no-questions-asked refunds after resource consumption.
- Do not omit the human-review boundary.

## Related references

- `class6/legal-playbook-review`
- `class6/class6-legal-compliance-agent-implementation`
