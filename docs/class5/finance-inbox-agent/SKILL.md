---
name: finance-inbox-agent
description: Class 5 AI Solo Company skill for turning receipts, invoices, expense notes, and income notes into reviewed finance records, Google Sheets rows, monthly summaries, and AI CFO prompts.
---

# Finance Inbox Agent — Receipt-to-Finance-Dashboard Agent

## When to use

Use this skill in Class 5 when a student provides a receipt, invoice, payment screenshot text, income note, or messy transaction description and wants a clean finance record for a one-person company.

This skill is for organization and education only. It is **not tax, legal, or accounting advice**.

## Required input

Ask for or infer when visible:

- Date
- Type: income or expense
- Vendor or customer
- Description
- Amount and currency
- Category
- Business purpose
- Payment method if visible
- Tax/VAT if visible

## Categories

Use student-friendly categories:

- Income
- AI Tools
- Software Subscription
- Website / Domain / Hosting
- Marketing
- Contractor / Freelancer
- Travel
- Office / Admin
- Other

## Review rules

Set `review_needed=true` when:

- amount is missing or ambiguous
- date is missing or suspicious
- vendor/customer is unclear
- category is Other
- tax/VAT is unclear but needed
- the user asks about tax treatment or deductibility

Use `tax_deductible_likely` only as an educational flag. Do not claim final deductibility.

## Output format

Return this structure:

```json
{
  "transaction": {
    "date": "YYYY-MM-DD",
    "type": "income|expense",
    "vendor_or_customer": "",
    "description": "",
    "category": "AI Tools|Software Subscription|Website / Domain / Hosting|Marketing|Contractor / Freelancer|Travel|Office / Admin|Income|Other",
    "amount": 0,
    "currency": "USD",
    "tax": null,
    "payment_method": "",
    "business_purpose": "",
    "tax_deductible_likely": true,
    "confidence": 0.0,
    "review_needed": true
  },
  "google_sheets_row": ["Date", "Type", "Vendor/Customer", "Description", "Category", "Amount", "Currency", "Tax", "Payment Method", "Business Purpose", "Tax Deductible Likely", "Review Needed", "Confidence"],
  "student_google_sheet": {
    "sheet_url": "",
    "sheet_id": "",
    "range": "Sheet1!A:M"
  },
  "google_sheets_append_plan": {
    "method": "direct_append|csv_copy|manual_paste",
    "steps": [""],
    "notes": ""
  },
  "monthly_summary": {
    "income": 0,
    "expenses": 0,
    "estimated_profit": 0,
    "cash_flow_note": "",
    "recommended_action": ""
  },
  "ai_cfo_answer": ""
}
```

## Example input

```text
I paid $29.99 to OpenAI for ChatGPT Plus on June 1, 2026 for my AI consulting business.
```

## Example output style

```json
{
  "transaction": {
    "date": "2026-06-01",
    "type": "expense",
    "vendor_or_customer": "OpenAI",
    "description": "ChatGPT Plus subscription for AI consulting work",
    "category": "AI Tools",
    "amount": 29.99,
    "currency": "USD",
    "tax": null,
    "payment_method": "",
    "business_purpose": "AI consulting productivity",
    "tax_deductible_likely": true,
    "confidence": 0.86,
    "review_needed": false
  },
  "google_sheets_row": ["2026-06-01", "expense", "OpenAI", "ChatGPT Plus subscription for AI consulting work", "AI Tools", 29.99, "USD", "", "", "AI consulting productivity", true, false, 0.86],
  "student_google_sheet": {
    "sheet_url": "https://docs.google.com/spreadsheets/d/student-sheet-id/edit",
    "sheet_id": "student-sheet-id",
    "range": "Sheet1!A:M"
  },
  "google_sheets_append_plan": {
    "method": "direct_append",
    "steps": [
      "Open the student's own Google Sheet.",
      "Append the reviewed row to Sheet1!A:M.",
      "Keep localStorage as a browser-side backup for the same student account."
    ],
    "notes": "If direct Google Sheets append is unavailable, fall back to CSV copy or manual paste."
  },
  "monthly_summary": {
    "income": 0,
    "expenses": 29.99,
    "estimated_profit": -29.99,
    "cash_flow_note": "This sample period is negative because no income has been recorded yet.",
    "recommended_action": "Record at least one revenue transaction before deciding whether to add new subscriptions."
  },
  "ai_cfo_answer": "The expense is small and probably useful for delivery, but review total AI tool subscriptions monthly. This is not tax, legal, or accounting advice."
}
```

## Google Sheets handoff

Use these columns:

```text
Date | Type | Vendor/Customer | Description | Category | Amount | Currency | Tax | Payment Method | Business Purpose | Tax Deductible Likely | Review Needed | Confidence
```

Each student should have a **separate Google Sheet** plus a **separate localStorage bucket** tied to their login email.

Always include a `student_google_sheet` object and a `google_sheets_append_plan` in the output whenever the sheet destination is known.

Recommended append order:

1. Save the reviewed row locally for the logged-in student.
2. Append the reviewed row to the student's own Google Sheet.
3. Rebuild the monthly summary from the reviewed row set.
4. Keep CSV copy/manual paste as fallback when direct append is unavailable.

If the user is running Hermes locally, use the `google-workspace` workflow when available so the same Class 5 finance tasks can be completed from Hermes and then written to the student's sheet.

## Student exercises

1. Record one AI tool subscription.
2. Record one website/domain/hosting expense.
3. Record one client payment.
4. Generate a monthly summary.
5. Ask an AI CFO question such as: "Can I afford to spend $300 on ads this month?"

## Local Hermes usage

Use this same skill when working in the local Hermes bot, not only in the website UI.

Recommended local workflow:

1. Parse the receipt/invoice/expense note into the reviewed `transaction` object.
2. Produce the `google_sheets_row` in the exact sheet column order.
3. Include `student_google_sheet` destination details when the user provides their sheet URL or Sheet ID.
4. Include a `google_sheets_append_plan` describing whether to append directly, copy CSV, or paste manually.
5. If Google Workspace access is available, append the reviewed row to the user-owned sheet immediately after human review.
6. Recompute the monthly summary after the row set changes.

## How to use the Class 5 Finance Agent

1. Open the Finance Agent Studio in the admin console.
2. Paste a receipt, invoice, expense note, or income note.
3. Click Extract transaction, review the JSON, then save the reviewed row.
4. Export the Google Sheets row or download CSV for the classroom finance tracker.
5. Generate a monthly summary and build an AI CFO prompt.
6. Use the advanced prompt builders for OCR, integrations, subscriptions, budget simulation, and tax review preparation.

Classroom docs: `docs/class5/finance-inbox-agent/SKILL.md` and `docs/class5/advanced-feature-prompts.md`.

## Safety checklist

- Do not connect real bank accounts in the MVP.
- Do not store bank credentials, tax IDs, or private customer payment details in frontend files.
- Use manual review before exporting to accounting software.
- Remind students: this is not tax, legal, or accounting advice.


## Advanced features

After the MVP works, teach these extensions as prompt/planning builders first:

### Receipt OCR prompt

Use an AI vision/OCR tool to read receipt images or PDFs, extract visible fields, and pass clean text into this skill. Do not guess hidden values.

### Integration planner

Plan third-party connections in this safe order:

1. Google Sheets export
2. Gmail receipts search/forwarding
3. Notion / Airtable tracker
4. Stripe / PayPal / Shopify revenue import
5. QuickBooks / Wave only after server-side secret storage and human approval

### Recurring expense audit

Group transactions by vendor/category and label each likely subscription as keep, cancel, negotiate, or review.

### Budget simulator

Use saved rows and monthly summaries to answer questions like whether the owner can afford ads, a contractor, inventory, or a new AI tool.

### Tax review checklist

Prepare a CPA/bookkeeper review packet: missing receipts, unclear vendors, review_needed rows, deductible-likely items, and questions for a professional. Do not give final tax advice.
