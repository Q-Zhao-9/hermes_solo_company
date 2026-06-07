# Class 5 Advanced Feature Prompts / 第 5 课高级功能提示词

These advanced Finance Agent additions are recommended after the MVP works. They are classroom-safe because they generate prompts and plans first instead of directly connecting real bank accounts.

## 01. Receipt OCR prompt builder

Use an AI vision/OCR tool to read receipt images or PDFs, then pass clean extracted text into the Finance Agent. Do not guess hidden values.

Prompt:

```text
Read this receipt image/PDF. Extract date, vendor, amount, currency, tax/VAT, payment method, line items, and unclear fields. Return clean text and a transaction JSON candidate for finance-inbox-agent. Do not guess hidden fields.
```

## 02. Integration planner

Plan a safe path from Google Sheets export to Gmail receipts, Notion / Airtable tracker, Stripe / PayPal / Shopify revenue import, then QuickBooks / Wave only after server-side secrets and approval.

Recommended connector order:

1. Student-owned Google Sheets export / append
2. Gmail receipts search/forwarding
3. Notion / Airtable tracker
4. Stripe / PayPal / Shopify revenue import
5. QuickBooks / Wave only after review and server-side secret storage

Classroom rule: Google Sheets should be configured per student, and the same workflow should also work from local Hermes when a student wants the result saved to their own sheet.

## 03. Recurring expense audit

Group repeated vendors and subscriptions, then label each item as keep, cancel, negotiate, or review.

Prompt:

```text
Group transactions by vendor and category. Find recurring subscriptions, estimate monthly cost, and label each keep/cancel/negotiate/review.
```

## 04. Budget simulator

Use saved sample rows and monthly summaries to answer questions like whether the business can afford ads, a contractor, inventory, or a new AI tool.

Prompt:

```text
Based on this month income, expenses, and estimated profit, can I afford [new expense]? Give conservative max spend, risk level, ROI assumptions, and a safer test plan.
```

## 05. Tax review checklist

Prepare a CPA/bookkeeper review packet: missing receipts, unclear vendors, review_needed rows, deductible-likely items, and questions for a professional. This is not tax, legal, or accounting advice.

Prompt:

```text
Prepare a CPA/bookkeeper review checklist. Flag missing receipts, unclear categories, deductible-likely items, income to verify, and questions to ask a professional. Do not give final tax advice.
```

## How to use the Class 5 Finance Agent

1. Open the Finance Agent Studio in the admin console.
2. Paste a receipt, invoice, expense note, or income note.
3. Click Extract transaction, review the JSON, then save the reviewed row.
4. Export the Google Sheets row or download CSV for the classroom finance tracker.
5. Generate a monthly summary and build an AI CFO prompt.
6. Use the advanced prompt builders for OCR, integrations, subscriptions, budget simulation, and tax review preparation.

Classroom docs: `docs/class5/finance-inbox-agent/SKILL.md` and `docs/class5/advanced-feature-prompts.md`.

Class 5 rule: demo the automation path, but keep money movement, tax filing, and production accounting decisions under human/professional review.
