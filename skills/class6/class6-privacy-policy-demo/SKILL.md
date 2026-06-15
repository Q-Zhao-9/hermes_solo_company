---
name: class6-privacy-policy-demo
description: Run Class 6 Demo 2 using a website privacy policy excerpt with missing data-disclosure details, undisclosed AI/API cross-border sharing, and an overlong deletion-response window.
version: 1.0.0
author: Hermes Agent
---

# Class 6 Privacy Policy Demo

## When to use

Use this skill when the user wants to present or rehearse **Class 6 Demo 2 / 平台隐私**, especially the slide showing:

- incomplete data collection disclosure
- missing AI / API / cross-border sharing disclosure
- overlong privacy/deletion response timelines
- an AI review result that escalates to **HARD_BLOCK** before publication

## Teaching goal

Show students that the AI legal/compliance agent can inspect a privacy-policy draft and catch the gap between:

1. what the website actually does
2. what the policy claims it does
3. what a user/regulator would expect to be disclosed

The demo should teach that privacy review is not generic copywriting. It must reflect the real business, real tools, and real data flows.

## Safety boundary

- This is first-pass review support, not final legal advice.
- Do not claim the sample policy is compliant just because issues were identified.
- Real privacy policy publication, especially for cross-border or multi-jurisdiction use, should go to human legal/privacy review.

## Reuse vs. existing skills

You can still use the broader Class 6 skills:
- `class6/legal-playbook-review`
- `docs/class6/legal-compliance-agent/SKILL.md`

This demo skill exists because the classroom slide needs a **specific privacy-policy scenario and expected findings**, not just the generic review workflow.

## Demo assets

Primary sample document:
- `references/class6-demo2-privacy-policy-sample-zh.md`

## Recommended live demo flow

### Step 1 — frame the scenario
Tell the audience:

> The business website is already live and collecting leads. The founder copied a privacy policy template from somewhere else, changed a few lines, and assumed it was good enough.

### Step 2 — load the privacy-policy sample
Use the sample excerpt from `references/class6-demo2-privacy-policy-sample-zh.md`.

The audience should notice three suspicious areas:
- the policy only names email and payment info
- the policy hides or glosses over external AI/API handling
- user deletion / response timing is too slow for an export-oriented scenario

### Step 3 — classify as a privacy review
Document type should be:
- `privacy`

### Step 4 — compare text to real business behavior
Explain that the platform may actually involve:
- lead collection
- cookies
- device/IP logging
- uploaded invoice or document images
- analytics
- third-party AI/model APIs
- cross-border processing or vendor access

### Step 5 — expected findings
The demo should reliably surface these findings:

1. **信息数据收集披露不全（缺失指标）**
   - risk level: `medium`
   - why it matters: actual platform data flows include more than email/payment data
   - expected follow-up: enumerate automatically collected and uploaded data categories

2. **未公示 AI 接口境外共享披露**
   - risk level: `medium`
   - why it matters: external AI/model/API providers may process user/business data and cross-border transfer cannot be ignored
   - expected follow-up: disclose provider categories, purposes, and processing scope

3. **数据彻底遗忘删除响应过长**
   - risk level: `high`
   - why it matters: deletion/account-closure handling with slow response promises can create material privacy/compliance exposure
   - expected follow-up: shorten response window and establish an account/data deletion workflow

### Step 6 — expected final response posture
The safest teaching outcome is:
- `overall_risk: high`
- `human_review_required: true`
- `response_result: HARD_BLOCK`
- block publication and recommend replacement with a reviewed template or human rewrite

## Suggested teacher talk track

Use business-language commentary such as:

- “The problem is not that the policy sounds formal. The problem is that it does not describe the real product.”
- “If your website uses AI vendors, uploaded files, tracking, and lead capture, your privacy policy cannot pretend it only touches email.”
- “The AI agent helps stop fake-compliant text from shipping.”

## Good output shape

A strong demo output should include:
- short summary
- overall risk
- risk counts
- 3 findings with clause excerpts
- human review queue
- suggested rewrite/redline directions
- final publication block recommendation

## Pitfalls

- Do not turn the deletion-response issue into a low-priority wording comment; keep it as the red-line finding.
- Do not promise specific jurisdictional compliance unless the legal basis has actually been reviewed.
- Do not let the demo suggest that mentioning one or two data types is enough.
- Do not omit the human-review boundary.

## Related references

- `class6/legal-playbook-review`
- `class6/class6-legal-compliance-agent-implementation`
