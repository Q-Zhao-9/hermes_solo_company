# Class 6 Skills

This folder contains reusable skills for **Class 6 — AI Legal & Compliance Agent** in the Hermes Solo Company materials.

## Purpose

These skills define repeatable workflows for:
- first-pass legal and compliance review
- classroom demos for contracts, privacy policies, and terms of service
- structured risk labeling and human-review escalation
- implementation guidance for the Class 6 website experience

These are workflow assets, not final legal advice.

## Folder layout

```text
skills/class6/
  README.md
  class6-commercial-contract-demo/
  class6-legal-compliance-agent-implementation/
  class6-paid-saas-tos-demo/
  class6-privacy-policy-demo/
  legal-compliance-agent/
  legal-compliance-review-workflow/
  legal-document-review/
  legal-playbook-review/
```

## Current skills

### `class6-commercial-contract-demo`
Demo workflow for reviewing a commercial contract / service agreement example.

### `class6-legal-compliance-agent-implementation`
Implementation workflow for building or extending the Class 6 student/admin experience, tests, docs, and guardrails.

### `class6-paid-saas-tos-demo`
Demo workflow for reviewing a paid SaaS Terms of Service example.

### `class6-privacy-policy-demo`
Demo workflow for reviewing a privacy policy example.

### `legal-compliance-agent`
Repo-local Class 6 classroom workflow for first-pass legal/compliance review.

### `legal-compliance-review-workflow`
Structured review packet workflow matching the Class 6 website review schema.

### `legal-document-review`
General first-pass legal document review skill for contracts, privacy policies, and terms.

### `legal-playbook-review`
Workflow for reviewing documents against a company-specific legal playbook.

## How to use these skills

Use these skills when you need to:
- teach or demo Class 6 legal/compliance review
- review risky example documents
- generate structured findings and escalation packets
- align website behavior with the classroom workflow

Most Class 6 skills pair with supporting materials under:
- `docs/class6/`

## Skill vs docs

Use `skills/class6/` for:
- repeatable procedures
- review workflows
- implementation instructions
- output schemas and guardrails

Use `docs/class6/` for:
- lesson handouts
- playbooks
- demo inputs
- slide decks
- presenter guides
- checklists and templates

## Notes

- Keep skill content reusable and stable.
- Do not put secrets, credentials, or environment-specific tokens into skill files.
- Keep the legal safety boundary explicit: first-pass review support only, with human review for high-risk or ambiguous issues.
