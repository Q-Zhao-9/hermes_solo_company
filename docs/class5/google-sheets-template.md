# Class 5 Google Sheets Template / 第 5 课 Google Sheets 模板

Create a sheet with these columns:

```text
Date | Type | Vendor/Customer | Description | Category | Amount | Currency | Tax | Payment Method | Business Purpose | Tax Deductible Likely | Review Needed | Confidence
```

Recommended first categories:

- Income
- AI Tools
- Software Subscription
- Website / Domain / Hosting
- Marketing
- Contractor / Freelancer
- Travel
- Office / Admin
- Other

## Student Google Sheet setup

Each student should use **their own Google Sheet**, not a shared class sheet.

1. Create a new Google Sheet.
2. Add the header row above to `Sheet1`.
3. Copy the Google Sheet URL.
4. In the Class 5 Finance Agent Studio, paste that URL into **Google Sheet URL or Sheet ID**.
5. Keep the default append range `Sheet1!A:M` unless the header is on a different tab.
6. Optional but recommended: add the student Apps Script webhook URL so reviewed rows can be appended automatically.

## What is stored where

- **LocalStorage**: quick local browser copy for this logged-in student account.
- **Google Sheet**: the student's longer-term record they can reopen later.
- **No bank login required** for this MVP.

## MVP workflow

Finance Agent extracts JSON → student reviews → save reviewed row locally → append latest row or all rows to the student's own Google Sheet → generate monthly summary.

## Local Hermes bot workflow

When using the local Hermes Finance Agent instead of the website UI:

1. Run `finance-inbox-agent` on the receipt/invoice text.
2. Return the `transaction`, `google_sheets_row`, `monthly_summary`, and `ai_cfo_answer`.
3. Save the reviewed row into the same student-owned Google Sheet.
4. Keep the same header order as the sheet above.

If Hermes has Google Workspace access, append directly. Otherwise copy/export CSV and paste it into the student's sheet manually.
