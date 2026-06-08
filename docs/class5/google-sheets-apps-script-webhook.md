# Class 5 Google Sheets Apps Script Webhook / 第 5 课 Google Sheets Apps Script Webhook

Use this when each student should append their own reviewed Finance Agent rows to **their own Google Sheet** from the Finance Agent Studio UI.

## Why this pattern

- Keeps the Class 5 MVP simple.
- Avoids storing Google OAuth secrets in the static website.
- Lets each student control their own sheet.
- Works alongside student-specific localStorage.

## Sheet columns

Use this header row in `Sheet1`:

```text
Date | Type | Vendor/Customer | Description | Category | Amount | Currency | Tax | Payment Method | Business Purpose | Tax Deductible Likely | Review Needed | Confidence
```

## Apps Script code

In the student Google Sheet:

1. Open **Extensions → Apps Script**.
2. Replace the default code with this script.
3. Update `ALLOWED_SHEET_ID` if you want to hard-lock the webhook to one sheet.
4. Deploy as **Web app**.
5. Access level: only the student (or class demo account) should control the deployment.
6. Copy the `/exec` URL into the Finance Agent Studio field **Apps Script webhook URL**.

```javascript
const DEFAULT_RANGE = 'Sheet1!A:M';
const ALLOWED_SHEET_ID = ''; // optional: paste the student's sheet ID here

function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents || '{}');
    const studentSheet = payload.student_google_sheet || {};
    const sheetId = String(studentSheet.sheet_id || '').trim();
    const range = String(studentSheet.range || DEFAULT_RANGE).trim() || DEFAULT_RANGE;
    const rows = Array.isArray(payload.rows) ? payload.rows : [];

    if (!rows.length) {
      return jsonResponse({ ok: false, error: 'No rows provided.' }, 400);
    }
    if (!sheetId) {
      return jsonResponse({ ok: false, error: 'Missing sheet_id.' }, 400);
    }
    if (ALLOWED_SHEET_ID && sheetId !== ALLOWED_SHEET_ID) {
      return jsonResponse({ ok: false, error: 'Sheet ID not allowed.' }, 403);
    }

    const spreadsheet = SpreadsheetApp.openById(sheetId);
    const targetSheetName = range.split('!')[0].replace(/^'/, '').replace(/'$/, '') || 'Sheet1';
    const sheet = spreadsheet.getSheetByName(targetSheetName) || spreadsheet.getSheets()[0];
    const startRow = sheet.getLastRow() + 1;
    const startColumn = 1;
    const width = rows[0].length;

    sheet.getRange(startRow, startColumn, rows.length, width).setValues(rows);

    return jsonResponse({
      ok: true,
      appended_rows: rows.length,
      student_email: payload.user_email || '',
      range_used: range,
    });
  } catch (error) {
    return jsonResponse({ ok: false, error: error.message || String(error) }, 500);
  }
}

function jsonResponse(payload, status) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}
```

## Finance Agent Studio fields

Each student should save these values under their own logged-in account:

- **Google Sheet URL or Sheet ID**
- **Append range** (default `Sheet1!A:M`)
- **Apps Script webhook URL**

These settings are stored per student account in browser localStorage using a user-specific key.

## Expected payload from the Finance Agent Studio

```json
{
  "source": "finance-agent-studio",
  "user_email": "student@example.com",
  "student_google_sheet": {
    "sheet_url": "https://docs.google.com/spreadsheets/d/.../edit",
    "sheet_id": "spreadsheet-id",
    "range": "Sheet1!A:M"
  },
  "rows": [
    ["2026-06-01", "expense", "OpenAI", "ChatGPT Plus subscription for AI consulting work", "AI Tools", 29.99, "USD", "", "", "AI consulting productivity", true, false, 0.86]
  ]
}
```

## Safety notes

- Do **not** store bank passwords, tax IDs, or payment card secrets in Apps Script.
- Keep this for reviewed educational finance rows only.
- For production accounting integrations, move secrets and access control server-side.
- Remind students this is **not tax, legal, or accounting advice**.
