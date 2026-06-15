---
name: legal-compliance-review-workflow
description: Run Class 6 first-pass legal and compliance reviews for contracts, privacy policies, and terms of service with explicit human-review escalation.
---

# Legal Compliance Review Workflow

## When to use

Use this skill when the AI Solo Company Class 6 workflow needs a structured first-pass review of:

- service agreements or contracts
- privacy policies
- terms of service

## Safety boundary

- This is first-pass review support.
- This is not final legal advice.
- High-risk, ambiguous, or business-critical issues must go to human review.

## Required output

Match the website review packet exactly. The skill output should use this schema:

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

Keep `human_review_items` as the escalated subset of `findings`. Any high-risk or ambiguous issue should set `needs_human_review` to `true` and be included in the escalation packet.

## Review flow

1. Identify the document family.
2. Select the matching checklist.
3. Quote or summarize the risky clause.
4. Label the issue low, medium, or high risk.
5. Explain the practical business/compliance risk.
6. Identify missing information.
7. Escalate high-risk items to human review.

## Checklist focus by document type

### Service agreements / contracts

Check:
- scope of work
- payment terms
- refund/cancellation
- IP ownership
- confidentiality
- termination
- liability limitation
- dispute/governing law

### Privacy policies

Check:
- data collected
- purpose of collection
- cookies/tracking
- third-party tools or sharing
- user rights/contact method
- retention/security

### Terms of service

Check:
- acceptable use
- payment/refunds
- account or user obligations
- subscription/renewal
- suspension/termination
- liability limitation
- update/notice process

## High-risk triggers

Escalate when the clause materially affects:
- liability
- indemnity
- privacy/data handling
- IP ownership/transfer
- termination/cancellation rights
- governing law/dispute resolution

## Classroom reminder

Trust the workflow more than a one-off answer. The goal is a repeatable compliance review process, not an AI lawyer.
