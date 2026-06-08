---
name: class5-finance-agent-studio-implementation
description: Reusable workflow for implementing Class 5 AI Finance Agent Studio MVP on Jian's AI Solo Company class site, including admin-console UI, finance teaching skill, docs, static tests, and verification.
---

# Class 5 Finance Agent Studio Implementation

## When to use

Use this skill when preparing or extending **Class 5 — AI 财务 Agent** for the AI Solo Company bootcamp site, especially when adding a classroom-safe finance workflow such as:

- receipt/invoice/expense text extraction
- transaction categorization
- Google Sheets/CSV export
- monthly summary generation
- AI CFO prompt generation
- advanced prompt/planning builders such as Receipt OCR, Integration planner, Recurring expense audit, Budget simulator, and Tax review checklist
- Class 5 teaching docs and Hermes skill assets

Primary site root observed:

```text
/mnt/c/Users/jianl/solo-company-class-site
```

Live Hermes teaching skill path used:

```text
/home/jianl/.hermes/skills/class5/finance-inbox-agent/SKILL.md
```

Repo/classroom skill copy path:

```text
<site-root>/docs/class5/finance-inbox-agent/SKILL.md
```

## Recommended workflow

1. **Inspect the existing class site**
   - Check `admin.html`, `site-auth.js`, `styles.css`, and existing static tests.
   - Look at Class 4 patterns before implementing Class 5:
     - `docs/class4/...`
     - admin panel sections using `data-admin-panel-target` and `data-admin-panel`
     - translation keys in `site-auth.js`
     - CSS patterns such as `manual-hero-card`, `manual-card`, `manual-section-grid`.

2. **Use test-first static marker checks**
   - Add a dedicated test like:
     ```text
     class5_finance_static_test.py
     ```
   - Make it fail first by checking for:
     - `data-admin-panel-target="finance-agent"`
     - `data-admin-panel="finance-agent"`
     - `Finance Agent Studio / 财务 Agent 工作台`
     - `data-finance-agent-studio`
     - `data-finance-parse`, `data-finance-save`, `data-finance-summary`
     - `data-finance-cfo-question`, `data-finance-cfo-prompt`
     - docs under `docs/class5/`
     - teaching skill copy under `docs/class5/finance-inbox-agent/SKILL.md`
     - disclaimer: `This is not tax, legal, or accounting advice`
   - Run the new test and confirm it fails because files/markers are missing.

3. **Add the admin-console panel**
   - Add a sidebar menu item before or near Skill Studio:
     ```html
     data-admin-panel-target="finance-agent"
     ```
   - Add a dashboard card pointing to the same target.
   - Add a full backend panel before Class 4 Skill Studio:
     ```html
     <section id="admin-panel-finance-agent" class="backend-panel" data-admin-panel="finance-agent" ...>
     ```
   - Include a classroom MVP flow:
     ```text
     Receipt text -> structured JSON -> saved transaction -> monthly summary -> AI CFO prompt
     ```
   - Keep it safe: no bank integration in the MVP.

4. **Implement simple local-only JavaScript behavior**
   - Add frontend functions to `site-auth.js`, not backend routes, for the MVP:
     - `initFinanceAgentStudio`
     - `parseFinanceTransaction`
     - `classifyFinanceCategory`
     - `renderFinanceTransactions`
     - `generateFinanceMonthlySummary`
     - `buildFinanceCfoPrompt`
     - `exportFinanceCsv`
  - Store classroom demo rows in browser localStorage under a user-scoped key derived from the logged-in email, for example:
    ```text
    aiSoloFinanceTransactions:<lowercased-user-email>
    ```
  - Store student Google Sheet connection settings in a second user-scoped localStorage key, for example:
    ```text
    aiSoloFinanceSheetConfig:<lowercased-user-email>
    ```
  - The student sheet config should include:
    - Google Sheet URL or Sheet ID
    - append range such as `Sheet1!A:M`
    - Apps Script webhook URL for reviewed-row append
  - Do not reuse one shared finance localStorage key across all users, or students on the same browser can see each other's demo data or sheet settings.
  - Support both paths:
    1. website UI: save locally, then append latest/all reviewed rows to the student's own Google Sheet
    2. local Hermes flow: run the same Class 5 finance task and produce a Google Sheets append plan for the student's own sheet
- Use simple category rules for:
     - AI Tools
     - Software Subscription
     - Website / Domain / Hosting
     - Marketing
     - Contractor / Freelancer
     - Travel
     - Office / Admin
     - Income
     - Other
   - Output fields should include:
     - `date`
     - `type`
     - `vendor_or_customer`
     - `description`
     - `category`
     - `amount`
     - `currency`
     - `tax`
     - `payment_method`
     - `business_purpose`
     - `tax_deductible_likely`
     - `confidence`
     - `review_needed`
   - Initialize `initFinanceAgentStudio()` inside `initAdmin()` after admin login setup.

5. **Add bilingual translations**
   - Add English and Chinese keys in `consoleTranslations`:
     - `menu.financeAgent`
     - `card.financeAgent.title`
     - `card.financeAgent.desc`
     - `financeAgent.*`
   - Include Chinese labels for the admin console, but keep sample prompts in English when useful for classroom copy/paste.

6. **Add CSS using existing design patterns**
   - Add selectors such as:
     - `.finance-agent-hero-card`
     - `.finance-agent-studio`
     - `.finance-agent-grid`
     - `.finance-agent-form`
     - `.finance-agent-output`
     - `.finance-transaction-list`
     - `.finance-summary-card`
     - `.finance-cfo-card`
     - `.finance-disclaimer`
   - Follow existing card/grid styling and add a mobile breakpoint.

7. **Create Class 5 docs and teaching skill**
   - Create:
     ```text
     docs/class5/finance-input-examples.md
     docs/class5/finance-output-example.md
     docs/class5/google-sheets-template.md
     docs/class5/test-checklist.md
     docs/class5/finance-inbox-agent/SKILL.md
     ```
   - Also create/update live Hermes skill:
     ```text
     /home/jianl/.hermes/skills/class5/finance-inbox-agent/SKILL.md
     ```
   - Teaching skill should clearly state it is not tax/legal/accounting advice.
   - Recommended Google Sheets columns:
     ```text
     Date | Type | Vendor/Customer | Description | Category | Amount | Currency | Tax | Payment Method | Business Purpose | Tax Deductible Likely | Review Needed | Confidence
     ```

8. **Advanced feature extension pattern**
   - For safe advanced Class 5 features, prefer prompt/demo builders instead of live financial integrations.
   - Extend `class5_finance_static_test.py` before implementation to require:
     - docs file such as `docs/class5/advanced-feature-prompts.md`
     - UI markers like `Advanced Finance Automations`, `data-finance-advanced-panel`, `data-finance-receipt-ocr-prompt`, `data-finance-integration-plan`
     - JS builder functions such as `buildReceiptOcrPrompt`, `buildFinanceIntegrationPlan`, `buildRecurringExpenseAudit`, `buildBudgetSimulator`, `buildTaxReviewChecklist`
     - CSS markers like `.finance-advanced-panel`, `.finance-advanced-grid`, `.finance-advanced-card`, `.finance-prompt-output`
     - updated live and repo skill text for the advanced features
   - Recommended advanced classroom builders:
     1. Receipt OCR prompt — use AI vision/OCR for receipt images/PDFs, then pass reviewed text into the finance agent.
     2. Integration planner — safe staged roadmap: Google Sheets, Gmail receipts, Notion/Airtable, Stripe/PayPal/Shopify revenue import, then QuickBooks/Wave only after server-side secrets and human approval.
     3. Recurring expense audit — group vendors/categories and suggest keep/cancel/negotiate/review.
     4. Budget simulator — answer affordability questions for ads, contractors, inventory, or new AI tools from saved rows.
     5. Tax review checklist — prepare CPA/bookkeeper packets; never present final tax advice.
   - Add/update `docs/class5/advanced-feature-prompts.md`, `docs/class5/finance-inbox-agent/SKILL.md`, and `/home/jianl/.hermes/skills/class5/finance-inbox-agent/SKILL.md` so the site docs and live Hermes skill stay aligned.

9. **Expose Class 5 tools/how-to on the public website and console**
   - When the user asks to add Class 5 tools/skill usage to the AI Solo Company website, update both `index.html` and `admin.html` instead of only the admin panel.
   - Add a public website section near the curriculum/tools area with:
     - `id="class5-finance-tools"`
     - `data-class5-finance-tools`
     - title `Class 5 Finance Agent Tools`
     - `finance-inbox-agent skill` explanation
     - cards for Receipt OCR prompt builder, Integration planner, Recurring expense audit, Budget simulator, and Tax review checklist
     - `How to use the Class 5 Finance Agent` ordered steps
     - references to `docs/class5/finance-inbox-agent/SKILL.md` and `docs/class5/advanced-feature-prompts.md`
     - a CTA back to `admin.html` / Finance Agent Studio
   - Add a nav link to `#class5-finance-tools` if the public page has a top navigation.
   - Add an admin-console how-to guide inside the finance panel with:
     - `data-finance-how-to-guide`
     - heading `Class 5 tools and skill guide`
     - `How to use the Class 5 Finance Agent`
     - `finance-inbox-agent skill`
     - classroom documentation list
     - recommended demo order
     - link labeled `Open Website Class 5 tools section` pointing to `index.html#class5-finance-tools`
   - Add CSS markers such as `.class5-finance-tools`, `.class5-finance-tool-grid`, `.class5-finance-demo-flow`, and `.finance-how-to-guide`.
   - Extend `class5_finance_static_test.py` to check public website markers as well as admin-console markers before implementation, then verify it fails and passes after implementation.

10. **Verification**
   - Run:
     ```bash
     cd /mnt/c/Users/jianl/solo-company-class-site
     python3 class5_finance_static_test.py
     python3 auth_download_static_test.py
     node --check site-auth.js
     python3 portal_static_test.py
     python3 video_meeting_static_test.py
     ```
   - Load the live Hermes teaching skill:
     ```text
     skill_view("class5/finance-inbox-agent")
     ```
   - If browser verification fails in WSL with Chromium missing `libnspr4.so`, report that browser verification was unavailable and rely on static/syntax checks plus HTTP marker checks if reachable.
   - If proxy/public HTTP checks time out, do not keep retrying blocked curl commands; report local static verification instead.

## Class demo flow

Use this live demo sequence:

1. Open Admin Console.
2. Navigate to `Finance Agent Studio / 财务 Agent 工作台`.
3. Paste:
   ```text
   I paid $29.99 to OpenAI for ChatGPT Plus on June 1, 2026 for my AI consulting business.
   ```
4. Click **Extract transaction** and review JSON.
5. Click **Save reviewed row**.
6. Add two more sample rows:
   - a domain/hosting expense
   - a first client payment
7. Click **Generate monthly summary**.
8. Ask:
   ```text
   Can I afford to spend $300 on ads this month?
   ```
9. Click **Build AI CFO prompt**.
10. Export/copy the Google Sheets CSV row.

## Pitfalls learned

- Existing `auth_download_static_test.py` may enforce Class 4 skill markers. If it fails for an existing Class 4 phrase such as `warm and consultative`, patch the Class 4 skill copy minimally rather than changing the test goal.
- The site may already have many unrelated modified/untracked files. Do not assume a clean git state; report only the files touched for Class 5.
- Keep Class 5 MVP local/demo-only. Avoid bank account, Stripe, PayPal, or accounting-software writes unless explicitly requested and reviewed.
- Do not expose backend paths, credentials, bank details, tax IDs, or secrets in frontend code or docs.

## Final response checklist

Summarize:

- admin menu/panel added
- finance workflow implemented
- live and repo skill paths
- docs created
- exact verification commands and results
- browser/proxy limitations, if any
- suggested Class 5 classroom demo flow
