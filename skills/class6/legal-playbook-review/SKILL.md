---
name: legal-playbook-review
description: Review contracts, terms, or privacy docs against a company-specific legal playbook, then return a structured risk packet plus playbook deviations.
version: 1.0.0
author: Hermes Agent
---

# Legal Playbook Review

## When to use

Use this skill when the user wants a document reviewed **against a company's own legal playbook**, not just generic legal red flags.

Examples:
- review a customer contract against our fallback positions
- compare a vendor MSA against our acceptable liability/IP/payment rules
- review terms of service or privacy language against our standard policy expectations

## Safety boundary

- This is first-pass review support, not final legal advice.
- Escalate high-risk, ambiguous, heavily negotiated, or jurisdiction-specific issues to human legal review.
- Never claim a document is legally safe just because it matches the playbook.

## Inputs to gather

You need:
1. the document text or file path
2. a legal playbook
3. if possible, the company role in the document:
   - service provider / agency / software vendor
   - customer / buyer
   - platform operator

If the user does not provide a playbook, use the example reference file in this skill as a starter:
- `references/small-solo-company-playbook.md`

## Review method

### Step 1: Identify document type
Classify as one of:
- contract
- privacy
- terms

### Step 2: Read the playbook first
Extract the company-preferred positions for:
- payment timing
- refunds / credits
- renewals
- termination notice
- liability caps
- indemnity
- IP ownership
- confidentiality
- data/privacy promises
- governing law / dispute resolution
- suspension rights
- subcontractors / third parties

### Step 3: Compare clause-by-clause
For each important clause:
- quote the document language
- identify the matching playbook rule
- mark the clause as:
  - aligned
  - acceptable with note
  - outside playbook
  - high-risk deviation
  - missing key protection

### Step 4: Build the output packet
Return both:
1. the standard legal review packet
2. a playbook comparison section showing deviations from the company's preferred terms

## Required output format

Return a structured JSON-style packet using this schema:

```json
{
  "document_type": "contract | privacy | terms",
  "summary": "string",
  "overall_risk": "low | medium | high",
  "risk_counts": {"low": 0, "medium": 0, "high": 0},
  "findings": [
    {
      "title": "string",
      "risk_level": "low | medium | high",
      "clause_excerpt": "string",
      "why_it_matters": "string",
      "suggested_follow_up": "string",
      "needs_human_review": true,
      "playbook_position": "string",
      "playbook_alignment": "aligned | acceptable_with_note | outside_playbook | high_risk_deviation | missing_key_protection"
    }
  ],
  "human_review_required": true,
  "human_review_items": [],
  "missing_information": [],
  "playbook_summary": {
    "aligned": 0,
    "acceptable_with_note": 0,
    "outside_playbook": 0,
    "high_risk_deviation": 0,
    "missing_key_protection": 0
  },
  "playbook_deviations": [
    {
      "topic": "string",
      "document_position": "string",
      "playbook_position": "string",
      "gap": "string",
      "risk_level": "low | medium | high",
      "recommended_redline": "string"
    }
  ],
  "next_steps": [],
  "disclaimer": "This is first-pass review support based on a company legal playbook, not final legal advice."
}
```

## Suggested checklist by document type

### Contracts
Check especially:
- payment timing and late fees
- auto-renewal
- refund / cancellation
- scope change control
- IP ownership and license-back
- confidentiality
- subcontractor use
- indemnity scope
- liability cap and carve-outs
- termination rights and notice
- governing law / venue

### Privacy
Check especially:
- data categories collected
- purpose limitation
- processors / third parties
- retention promises
- deletion / access rights
- breach/security language
- cross-border transfer statements

### Terms
Check especially:
- subscription and billing
- acceptable use
- unilateral changes
- suspension / termination
- refund rules
- liability limitations
- IP/content license
- dispute resolution

## Escalation triggers

Escalate when the document:
- creates unlimited liability
- imposes broad one-way indemnity
- transfers IP ownership unexpectedly
- allows auto-renew without clear notice or exit
- weakens privacy/data promises below the playbook baseline
- removes key termination or payment protections
- is missing a clause the playbook treats as mandatory

## Response style

- Be concrete and clause-based.
- Prefer business-language explanations.
- Always point out where the document differs from the playbook.
- If the playbook is too generic or incomplete, say so explicitly.

## Example playbook

Use `references/small-solo-company-playbook.md` as a starter when the user has no company-specific playbook yet.
