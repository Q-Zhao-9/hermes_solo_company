---
name: legal-compliance-agent
description: Classroom workflow for Class 6 AI legal and compliance review with structured checklist prompts and human-review escalation.
---

# Legal Compliance Agent

## Purpose

Use this skill when a student or teacher needs a first-pass review support workflow for contracts, privacy policies, or terms of service inside the AI Solo Company Class 6 lesson.

## Core boundaries

- This is first-pass review support.
- This is not final legal advice.
- High-risk, ambiguous, or business-critical issues must go to human review.

## Review flow

1. Identify the document type.
2. Choose the correct checklist.
3. Extract the risky clause or section.
4. Label the risk as low, medium, or high.
5. Explain why it matters in business terms.
6. Record missing facts or ambiguity.
7. Recommend the next human review owner.

## Checklist map

- contracts and service agreements → `docs/class6/service-agreement-checklist.md`
- privacy policies → `docs/class6/privacy-policy-checklist.md`
- terms of service → `docs/class6/terms-of-service-checklist.md`
- high-risk clause examples → `docs/class6/high-risk-clause-guide.md`
- escalation packet → `docs/class6/human-review-checklist.md`

## Required output structure

Match the website review packet exactly. The review output should expose these top-level fields:

```json
{
  "audience": "student | admin",
  "document_type": "contract | privacy | terms",
  "summary": "string",
  "overall_risk": "low | medium | high",
  "risk_counts": {
    "low": 0,
    "medium": 0,
    "high": 0
  },
  "findings": [
    {
      "title": "string",
      "risk_level": "low | medium | high",
      "clause_excerpt": "string",
      "why_it_matters": "string",
      "suggested_follow_up": "string",
      "needs_human_review": true
    }
  ],
  "human_review_required": true,
  "human_review_items": [
    {
      "title": "string",
      "risk_level": "low | medium | high",
      "clause_excerpt": "string",
      "why_it_matters": "string",
      "suggested_follow_up": "string",
      "needs_human_review": true
    }
  ],
  "missing_information": ["string"],
  "next_steps": ["string"],
  "disclaimer": "This is first-pass review support, not final legal advice.",
  "generated_at": "ISO-8601 timestamp"
}
```

Keep `human_review_items` as the escalated subset of `findings`, and make sure every high-risk or ambiguous issue sets `needs_human_review` to true.
