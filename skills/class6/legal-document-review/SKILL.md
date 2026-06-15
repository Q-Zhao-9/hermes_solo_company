---
name: legal-document-review
description: Review contracts, privacy policies, and terms of service with a structured first-pass risk packet and explicit human-review escalation.
---

# Legal Document Review

## When to use

Use this skill when a user asks Hermes to review a legal or compliance document such as:

- a contract or service agreement
- a privacy policy
- terms of service
- a legal/compliance clause set extracted from one of the above

This skill is for **first-pass review support**.

## Safety boundary

- This is not final legal advice.
- Do not say the document is legally safe or legally compliant as a final conclusion.
- Escalate high-risk, ambiguous, jurisdiction-specific, or business-critical issues to human legal review.

## Input handling

1. If the user pasted the text, review that text directly.
2. If the text is in a local file, read the file first.
3. Preferred local file types for this workflow are:
   - `.md`
   - `.txt`
   - `.pdf`
   - `.docx`
4. If the document type is not stated, infer the best match from the text:
   - `contract`
   - `privacy`
   - `terms`
5. If the input is too short or obviously incomplete, say so and list missing information.

## Hermes MCP tool

Hermes has a dedicated MCP server for this workflow:

- server key: `legal_review`
- primary tool: `mcp_legal_review_review_legal_document`
- helper tool: `mcp_legal_review_get_prompt`

Use the MCP tool when available because it returns a more consistent JSON review packet and supports direct local file-path review.

## Required output format

Return a structured review packet using this schema:

```json
{
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
  "disclaimer": "This is first-pass review support, not final legal advice."
}
```

Keep `human_review_items` as the escalated subset of `findings`.

## Review flow

1. Identify the document family.
2. Scan for core obligations, restrictions, and asymmetries.
3. Quote the relevant clause excerpt.
4. Assign `low`, `medium`, or `high` risk.
5. Explain why it matters in practical business/compliance terms.
6. Suggest a follow-up question, negotiation point, or lawyer/compliance escalation.
7. Mark high-risk or ambiguous items for human review.

## Checklist by document type

### Contracts / service agreements

Check for:
- scope of work
- payment terms
- renewals
- cancellation/termination
- refunds
- IP ownership
- confidentiality
- indemnity
- liability caps or unlimited liability
- governing law/dispute resolution

### Privacy policies

Check for:
- categories of data collected
- purpose of use
- cookies/tracking
- sharing with third parties
- cross-border transfers
- retention period
- security language
- user rights/contact method

### Terms of service

Check for:
- account obligations
- acceptable use
- subscription/renewal terms
- payment/refund rules
- unilateral changes
- suspension/termination
- liability limitations
- governing law/dispute terms

## Human review triggers

Escalate when the text materially affects:
- indemnity
- unlimited or one-sided liability
- privacy/data sharing or retention
- IP ownership or assignment
- automatic renewal without clear notice
- termination rights
- governing law/dispute resolution
- missing legally important details

## Response style

- Be concise but concrete.
- Prefer bullet findings over long prose.
- Quote the relevant clause excerpt whenever possible.
- If the text is incomplete, say that explicitly instead of over-claiming.

## Classroom-compatible reminder

This skill follows the same first-pass review pattern used for Class 6 AI Legal & Compliance Agent work: structured review, risk labeling, and explicit human-review escalation.
