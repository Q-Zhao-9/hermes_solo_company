# Class 6 Playbook Sample Review Cases

> These classroom cases show how to review sample legal text **against the AI Solo Company legal playbook**. They are first-pass examples for teaching, not final legal advice.

## Case 1 — Service agreement review

### Sample clause

```text
Customer may terminate this Agreement at any time for convenience upon written notice. Company will continue providing transition support for 60 days at no extra charge. Company’s liability is unlimited, and Customer may withhold any payment it reasonably disputes. All work product, methods, prompts, templates, automations, and tooling developed or used under this Agreement become Customer property upon payment.
```

### Document type
- contract

### Review packet

- **summary:** The clause conflicts with the playbook on liability cap, payment protection, scope/control of transition work, and background IP ownership.
- **overall_risk:** high
- **risk_counts:** low=0, medium=1, high=4
- **human_review_required:** true

### Findings

1. **Unlimited liability**
   - risk_level: high
   - playbook_position: liability should be capped to fees paid in prior 12 months or total fees paid
   - playbook_alignment: high_risk_deviation
   - why_it_matters: unlimited exposure is unrealistic for a solo AI services company and can create business-ending downside
   - suggested_follow_up: redline to a fees-paid cap and exclude indirect/consequential damages

2. **Broad payment withholding**
   - risk_level: high
   - playbook_position: customer should pay undisputed invoices on net 7 or net 14 terms
   - playbook_alignment: high_risk_deviation
   - why_it_matters: broad withholding damages cash flow and creates leverage against a small operator
   - suggested_follow_up: limit withholding to specific documented disputes and require payment of undisputed amounts

3. **Background IP transfer**
   - risk_level: high
   - playbook_position: company retains prompts, templates, workflows, reusable code, systems, and know-how
   - playbook_alignment: high_risk_deviation
   - why_it_matters: the clause transfers the company’s reusable operating assets, not just the final customer deliverables
   - suggested_follow_up: reserve background IP and grant customer rights only in the final paid-for deliverables

4. **Free transition support with no boundary**
   - risk_level: medium
   - playbook_position: out-of-scope work should require written approval or change order
   - playbook_alignment: outside_playbook
   - why_it_matters: extra transition support can expand into unpaid implementation work
   - suggested_follow_up: define the exact transition scope and hours or make extra support billable

5. **Missing suspension right for non-payment**
   - risk_level: high
   - playbook_position: company needs suspension/termination rights for overdue payment or abuse
   - playbook_alignment: missing_key_protection
   - why_it_matters: the company has no operational protection if the customer stops paying but still demands work
   - suggested_follow_up: add suspension rights after notice for overdue undisputed invoices

### Playbook deviations summary

- aligned: 0
- acceptable_with_note: 0
- outside_playbook: 1
- high_risk_deviation: 3
- missing_key_protection: 1

### Recommended next steps

- escalate to human legal review
- redline liability cap, payment withholding, and background IP immediately
- define transition support boundaries before accepting the clause

---

## Case 2 — Privacy policy review

### Sample clause

```text
We collect names, emails, browser activity, device data, uploaded documents, and chatbot conversations. We may share personal data with trusted partners, affiliates, analytics providers, model providers, and service providers as needed to improve our services. We retain information for as long as useful to our business. We use commercially reasonable efforts to protect data and cannot guarantee absolute security.
```

### Document type
- privacy

### Review packet

- **summary:** The clause is partly realistic on security, but it is too broad on sharing and retention, and it lacks specific purpose limitation and user-rights structure.
- **overall_risk:** medium
- **risk_counts:** low=1, medium=3, high=1
- **human_review_required:** true

### Findings

1. **Over-broad sharing language**
   - risk_level: high
   - playbook_position: identify main processors and materially relevant third parties at a practical level
   - playbook_alignment: high_risk_deviation
   - why_it_matters: “trusted partners, affiliates, analytics providers, model providers” is broad enough to feel vague and under-disclosed
   - suggested_follow_up: narrow the categories and describe why each category receives data

2. **Retention is too vague**
   - risk_level: medium
   - playbook_position: retention logic should be described practically, not indefinitely or only for business convenience
   - playbook_alignment: outside_playbook
   - why_it_matters: “as long as useful to our business” is too open-ended and weak for trust/compliance review
   - suggested_follow_up: add category-based retention logic or retention factors

3. **Missing purpose limitation detail**
   - risk_level: medium
   - playbook_position: state the intended purpose for data use
   - playbook_alignment: missing_key_protection
   - why_it_matters: users and reviewers cannot tell which processing is necessary for service delivery versus analytics or improvement
   - suggested_follow_up: map collected data categories to clear purposes

4. **Security language is realistic**
   - risk_level: low
   - playbook_position: avoid unrealistic “absolute security” promises
   - playbook_alignment: aligned
   - why_it_matters: the clause correctly avoids guaranteeing perfect security
   - suggested_follow_up: keep this balanced language but add operational safeguards if available

5. **User rights/contact route not visible**
   - risk_level: medium
   - playbook_position: privacy disclosures should support a practical review of deletion/access/contact rights where relevant
   - playbook_alignment: missing_key_protection
   - why_it_matters: users need to know how to make privacy requests or ask questions
   - suggested_follow_up: add request/contact section or link to request workflow

### Playbook deviations summary

- aligned: 1
- acceptable_with_note: 0
- outside_playbook: 1
- high_risk_deviation: 1
- missing_key_protection: 2

### Recommended next steps

- revise sharing categories and purpose mapping
- add retention logic and privacy-request path
- escalate for human review if the business serves regulated or multi-jurisdiction users

---

## Case 3 — Terms of service review

### Sample clause

```text
Subscriptions renew automatically for successive 12-month terms unless canceled at least 72 hours before renewal. Fees are non-refundable. We may change pricing or these Terms at any time by posting an update on the website. We may suspend any account we believe creates legal, reputational, or operational risk.
```

### Document type
- terms

### Review packet

- **summary:** The clause is partially aligned on suspension rights, but weak on renewal notice and unilateral change fairness.
- **overall_risk:** medium
- **risk_counts:** low=1, medium=3, high=1
- **human_review_required:** true

### Findings

1. **Auto-renew without advance notice language**
   - risk_level: high
   - playbook_position: renewals are acceptable only with clear cadence, notice, and cancellation path
   - playbook_alignment: high_risk_deviation
   - why_it_matters: the cancellation window exists, but there is no promise of reminder or advance notice
   - suggested_follow_up: add renewal reminder timing and clearer cancellation steps

2. **Non-refundable fees need qualification**
   - risk_level: medium
   - playbook_position: refunds/credits should be explicit and not open-ended, but terms should still explain what happens on cancellation or billing error
   - playbook_alignment: acceptable_with_note
   - why_it_matters: a strict non-refundable rule may be acceptable, but only if billing timing and service scope are clear
   - suggested_follow_up: clarify exceptions, billing errors, and any service-period treatment

3. **Unilateral changes at any time**
   - risk_level: medium
   - playbook_position: major commercial changes should not happen with no operational fairness or notice
   - playbook_alignment: outside_playbook
   - why_it_matters: “posting an update on the website” may be too weak for material price or contract changes
   - suggested_follow_up: require notice period for material changes and define when changes take effect

4. **Suspension for legal/operational risk**
   - risk_level: low
   - playbook_position: company should retain suspension rights for legal, security, or abuse risk
   - playbook_alignment: aligned
   - why_it_matters: this supports operational protection for a small company
   - suggested_follow_up: keep, but define examples so the clause is not overly vague

5. **Missing liability cap in this excerpt**
   - risk_level: medium
   - playbook_position: liability cap is mandatory protection
   - playbook_alignment: missing_key_protection
   - why_it_matters: a terms set without limitation-of-liability language leaves an important risk-control gap
   - suggested_follow_up: confirm the full terms include liability limitation and damages disclaimer

### Playbook deviations summary

- aligned: 1
- acceptable_with_note: 1
- outside_playbook: 1
- high_risk_deviation: 1
- missing_key_protection: 1

### Recommended next steps

- add renewal notice language
- define material-change notice process
- confirm liability limitation exists elsewhere in the full terms
- escalate for human review before using as production terms

---

## Teaching note

These sample cases work well in this classroom order:

1. service agreement → strongest redline example
2. privacy policy → website/data handling example
3. terms of service → subscription/platform example

Students should always finish with:
- a risk-labeled summary
- a human-review queue
- playbook deviations
- a redline or follow-up recommendation
