---
name: student-lead-followup
description: Class 4 teaching skill that turns website lead data into a warm follow-up email, CRM note, qualification score, and next action.
---

# Student Lead Follow-up Skill

## When to use

Use this skill in AI Solo Company Class 4 when a website visitor or chatbot conversation produces a lead and the student needs a repeatable business follow-up package.

This skill connects the Class 3 workflow:

```text
Website visitor -> Chatbot -> Lead capture -> Solo CRM
```

to the Class 4 workflow:

```text
Lead data -> Hermes Skill -> Follow-up email + CRM note + next action
```

## Inputs

Ask for or infer these fields when available:

- `name`
- `email`
- `phone` optional
- `company` or `business_type`
- `need`
- `budget`
- `timeline`
- `service_interest`
- `source`, such as `website_chatbot`, `ask_enroll_modal`, or `footer_inquiry_form`

If a field is missing, do not invent it. Mark it as `Unknown` and include it in the next action if important.

## Business rules

1. Be warm and consultative, not pushy.
2. Treat the lead as a real business owner who needs practical help.
3. Score the lead from 1 to 5 using budget, urgency, fit, and clarity of need.
4. Keep the follow-up short enough to send after small edits.
5. Make the CRM note copy-paste ready.
6. Never include secrets, API keys, backend paths, or private implementation details.
7. If the lead is low fit, still be helpful and suggest a light next step.

## Qualification score

Use this lead_score guide:

- `5` — urgent need, clear business fit, budget is realistic, timeline is now/this month.
- `4` — strong fit and clear need, but one factor is less certain.
- `3` — possible fit, but budget, urgency, or problem clarity is incomplete.
- `2` — weak fit or unclear business need.
- `1` — not enough information or unlikely fit.

Always include `score_reason` in plain language.

## Output format

Return Markdown using exactly these sections:

```markdown
## Lead summary
- Name:
- Email:
- Business / company:
- Need:
- Budget:
- Timeline:
- Source:

## Qualification score
- lead_score: 1-5
- score_reason:

## Follow-up email
Subject: ...

Hi ...,
...

## CRM note
- Lead source:
- Problem / need:
- Fit:
- Budget / timeline:
- Recommended next action:

## Next action
...
```

## Example input

```text
Name: Sarah Chen
Email: sarah@example.com
Business: local dental clinic
Need: wants AI chatbot for appointment questions
Budget: $1500/month
Timeline: this month
Source: website chatbot
```

## Example output style

The output should sound like:

- practical
- clear
- friendly
- founder-to-founder
- focused on the next useful step

Avoid vague phrases such as:

- "revolutionize your business"
- "unlock your full potential"
- "cutting-edge synergy"

## Class 4 customization exercises

Students can customize this skill by changing:

1. Email tone: warmer, more direct, more premium, more casual.
2. Lead scoring rules: change budget or urgency weighting.
3. Output format: Markdown for humans or JSON for software integration.
4. CRM note style: bullets, table, or structured fields.
5. Next action rules: call, email, demo, audit, or nurture sequence.

## Testing checklist

After editing this skill, test with the same sample lead before and after the change.

Check that:

- Lead summary is complete.
- Qualification score is present.
- `lead_score` is between 1 and 5.
- `score_reason` explains the score.
- Follow-up email is warm and consultative.
- CRM note is copy-paste ready.
- Next action is specific.
- Output format did not accidentally change unless the exercise requested it.
