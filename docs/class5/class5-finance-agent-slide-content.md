# Class 5 Slide Content — AI Finance Agent / 财务 Agent

Use this as source content for PPT generation. Recommended deck length: 22–26 slides.

---

## Slide 1 — Title

**Title:** Class 5: Build Your AI Finance Agent  
**Subtitle:** Receipt → Finance Record → Google Sheets → Monthly Summary → AI CFO Prompt  
**Chinese subtitle:** 第 5 课：搭建你的 AI 财务 Agent

**Visual idea:** Pipeline diagram with five steps: Receipt, Extract, Review, Sheet, CFO.

**Speaker notes:**
Today we build a practical finance automation workflow for a one-person company. The goal is not to replace accountants; the goal is to organize information, reduce manual work, and prepare better records for business decisions.

---

## Slide 2 — Why This Class Matters

**Title:** Every Solo Business Needs Financial Visibility

**Key points:**
- Most solo founders lose track of small expenses, subscriptions, and first revenue.
- Receipts and invoices are messy: screenshots, emails, PDFs, notes, bank lines.
- A finance agent can convert messy information into structured records.
- Good records help with cash flow, pricing, budgeting, and professional review.

**Visual idea:** Before/after: messy receipts on the left, clean dashboard/table on the right.

**Speaker notes:**
Finance is usually boring until cash flow becomes a problem. Our class makes it practical: record expenses, summarize cash flow, and ask better business questions.

---

## Slide 3 — Class Outcome

**Title:** By the End, Students Will Have a Working Finance Workflow

**Students will be able to:**
1. Paste a receipt, invoice, expense note, or income note.
2. Extract structured transaction JSON.
3. Review and save finance rows.
4. Export rows to Google Sheets / CSV.
5. Generate a monthly finance summary.
6. Build an AI CFO prompt for business decisions.
7. Use advanced prompt builders for OCR, integrations, recurring expenses, budgets, and tax review preparation.

**Visual idea:** Checklist with seven completion badges.

---

## Slide 4 — Safety Boundary

**Title:** Important Boundary: This Is Not Accounting or Tax Advice

**Rules:**
- No real bank connection in the classroom MVP.
- No storage of bank credentials, tax IDs, or private payment details in frontend files.
- Every extracted record requires human review.
- `tax_deductible_likely` is only an educational flag.
- Final tax, legal, and accounting decisions require a qualified professional.

**Visual idea:** Shield icon with “Review-first” label.

**Speaker notes:**
This boundary is important. We are teaching safe automation. We organize data and prepare review packets; we do not make final tax or legal decisions.

---

## Slide 5 — The Finance Agent Workflow

**Title:** Receipt-to-Finance-Dashboard Agent

**Flow:**
```text
Messy input → AI extraction → human review → saved transaction → export → summary → CFO prompt
```

**Input examples:**
- Receipt text
- Invoice line
- Payment screenshot text
- Income note
- Subscription email
- Manual transaction description

**Visual idea:** Horizontal process flow with arrows.

---

## Slide 6 — Tool 1: Finance Agent Studio

**Title:** Tool 1 — Finance Agent Studio / 财务 Agent 工作台

**What it does:**
- Local classroom demo inside the admin console.
- Parses messy transaction text.
- Generates structured JSON.
- Saves reviewed classroom rows in browser storage.
- Builds monthly summaries and AI CFO prompts.

**Where to find it:**
```text
Admin Console → Finance Agent Studio
```

**Visual idea:** Screenshot placeholder of admin console panel.

---

## Slide 7 — Tool 2: finance-inbox-agent Skill

**Title:** Tool 2 — finance-inbox-agent Skill

**Skill purpose:**
Turn receipts, invoices, expense notes, and income notes into reviewed finance records.

**Skill file:**
```text
docs/class5/finance-inbox-agent/SKILL.md
```

**Live Hermes skill:**
```text
class5/finance-inbox-agent
```

**Use when:**
A student provides a receipt, invoice, screenshot text, income note, or messy transaction description.

**Visual idea:** Skill card with inputs and outputs.

---

## Slide 8 — Required Transaction Fields

**Title:** What the Agent Extracts

**Required / useful fields:**
- Date
- Type: income or expense
- Vendor or customer
- Description
- Category
- Amount and currency
- Tax/VAT if visible
- Payment method if visible
- Business purpose
- Confidence score
- Review flag

**Visual idea:** Form/table mockup.

---

## Slide 9 — Student-Friendly Categories

**Title:** Simple Categories for Solo Companies

**Categories:**
- Income
- AI Tools
- Software Subscription
- Website / Domain / Hosting
- Marketing
- Contractor / Freelancer
- Travel
- Office / Admin
- Other

**Teaching point:**
Start with simple categories students can understand. Add more categories only when the workflow is stable.

**Visual idea:** Category chips or color-coded tags.

---

## Slide 10 — Review Rules

**Title:** When Should the Agent Flag Review Needed?

Set `review_needed = true` when:
- Amount is missing or ambiguous.
- Date is missing or suspicious.
- Vendor/customer is unclear.
- Category is `Other`.
- Tax/VAT is unclear but important.
- The user asks about deductibility or tax treatment.

**Visual idea:** Traffic-light review system: green = OK, yellow = review, red = missing info.

---

## Slide 11 — Demo Input

**Title:** Demo Input: Messy Transaction Text

**Example:**
```text
I paid $29.99 to OpenAI for ChatGPT Plus on June 1, 2026 for my AI consulting business.
```

**Student task:**
Paste this into Finance Agent Studio and click **Extract transaction**.

**Visual idea:** Text box with highlighted date, vendor, amount, purpose.

---

## Slide 12 — Expected JSON Output

**Title:** Output: Structured Finance Record

**Example fields:**
```json
{
  "date": "2026-06-01",
  "type": "expense",
  "vendor_or_customer": "OpenAI",
  "description": "ChatGPT Plus subscription for AI consulting work",
  "category": "AI Tools",
  "amount": 29.99,
  "currency": "USD",
  "business_purpose": "AI consulting productivity",
  "tax_deductible_likely": true,
  "confidence": 0.86,
  "review_needed": false
}
```

**Visual idea:** Code block plus callouts for category, amount, review flag.

---

## Slide 13 — Human Review Step

**Title:** AI Extracts, Human Approves

**Review checklist:**
- Is the amount correct?
- Is the date correct?
- Is the vendor/customer correct?
- Is the category reasonable?
- Is the business purpose clear?
- Should this be marked for professional review?

**Visual idea:** Person approving a row before export.

---

## Slide 14 — Google Sheets / CSV Export

**Title:** Export to a Simple Finance Tracker

**Recommended columns:**
```text
Date | Type | Vendor/Customer | Description | Category | Amount | Currency | Tax | Payment Method | Business Purpose | Tax Deductible Likely | Review Needed | Confidence
```

**Why Google Sheets first:**
- Easy for students.
- No API credentials required.
- Easy to inspect and correct.
- Can later become the source for dashboards.

**Visual idea:** Spreadsheet table mockup.

---

## Slide 15 — Monthly Summary

**Title:** Turn Rows Into a Monthly Business Summary

**Summary outputs:**
- Total income
- Total expenses
- Estimated profit
- Cash flow note
- Recommended action

**Example question:**
```text
Do I have enough profit to buy another AI tool this month?
```

**Visual idea:** Mini dashboard with income, expenses, profit.

---

## Slide 16 — AI CFO Prompt

**Title:** Ask Better Business Questions With an AI CFO Prompt

**Example CFO question:**
```text
Can I afford to spend $300 on ads this month?
```

**Prompt should include:**
- Saved transaction rows
- Monthly summary
- Business context
- The decision question
- Safety reminder: not tax/legal/accounting advice

**Visual idea:** CFO chat bubble looking at a finance dashboard.

---

## Slide 17 — Advanced Tool 1: Receipt OCR Prompt Builder

**Title:** Advanced Tool 1 — Receipt OCR Prompt Builder

**Purpose:**
Use an AI vision/OCR tool to read receipt images or PDFs, then pass the cleaned text into the Finance Agent.

**Prompt principle:**
- Extract only visible fields.
- Do not guess hidden values.
- Mark uncertain values for review.
- Preserve original merchant, date, total, tax, and line items when visible.

**Future extension:**
Upload receipt images directly into the console and auto-generate extracted text.

**Visual idea:** Receipt image → OCR → cleaned text → finance record.

---

## Slide 18 — Advanced Tool 2: Integration Planner

**Title:** Advanced Tool 2 — Integration Planner

**Safe integration order:**
1. Google Sheets export
2. Gmail receipts search/forwarding
3. Notion / Airtable tracker
4. Stripe / PayPal / Shopify revenue import
5. QuickBooks / Wave after server-side secrets and human approval

**Teaching point:**
Integration planning is a skill. Students learn what data should move, where it should go, and what approval is required.

**Visual idea:** Stair-step roadmap from simple export to accounting tools.

---

## Slide 19 — Advanced Tool 3: Recurring Expense Audit

**Title:** Advanced Tool 3 — Recurring Expense Audit

**Purpose:**
Find repeated vendors and subscription patterns.

**Labels:**
- Keep
- Cancel
- Negotiate
- Review

**Examples:**
- OpenAI subscription
- Domain/hosting renewal
- Design software
- SaaS tools
- Marketing tools

**Future extension:**
Monthly subscription alert and “cost creep” dashboard.

**Visual idea:** Subscription list with keep/cancel tags.

---

## Slide 20 — Advanced Tool 4: Budget Simulator

**Title:** Advanced Tool 4 — Budget Simulator

**Questions it can help answer:**
- Can I spend $300 on ads?
- Can I hire a $500 freelancer?
- Can I buy a $99/month AI tool?
- Can I afford inventory this month?

**Inputs:**
- Current income
- Current expenses
- Estimated profit
- Cash-flow note
- Scenario cost

**Future extension:**
Scenario comparison chart: conservative, normal, aggressive.

**Visual idea:** Slider or scenario cards comparing outcomes.

---

## Slide 21 — Advanced Tool 5: Tax Review Checklist

**Title:** Advanced Tool 5 — Tax Review Checklist

**Purpose:**
Prepare a review packet for CPA/bookkeeper.

**Checklist includes:**
- Missing receipts
- Unclear vendors
- Rows marked `review_needed`
- Deductible-likely educational flags
- Questions for a professional

**Boundary:**
The agent prepares information. It does not give final tax advice.

**Visual idea:** Document packet labeled “For CPA review.”

---

## Slide 22 — Live Class Exercise

**Title:** Student Exercise: Build a Mini Finance Dashboard

**Exercise:**
1. Record one AI tool subscription.
2. Record one website/domain/hosting expense.
3. Record one client payment.
4. Export a Google Sheets row.
5. Generate a monthly summary.
6. Ask: “Which expense should I reduce first?”
7. Build one advanced prompt: OCR, integration, recurring audit, budget, or tax checklist.

**Visual idea:** 30-minute classroom sprint timer.

---

## Slide 23 — How This Fits the AI Solo Company OS

**Title:** Finance Agent Is One Part of the Company OS

**Connected system:**
```text
Website → Chatbot → CRM → Sales → Delivery → Finance → Strategy
```

**Class 5 connection:**
- CRM creates customer/revenue context.
- Website and marketing create expenses.
- Finance Agent turns activity into financial visibility.
- AI CFO prompt helps with decisions.

**Visual idea:** Circular operating system map.

---

## Slide 24 — Future Plan: Near-Term Enhancements

**Title:** Future Plan: What We Can Add Next

**Near-term features:**
- Receipt image upload inside the admin console.
- Better OCR extraction for PDFs/screenshots.
- Editable transaction table with search/filter.
- Category rule customization by student business type.
- Saved monthly dashboard with charts.
- Import/export templates for Google Sheets and Airtable.
- Student sample dataset for practice.

**Visual idea:** Product roadmap: Now → Next → Later.

---

## Slide 25 — Future Plan: Integrations and Automation

**Title:** Future Plan: Real Integrations, Still Review-First

**Potential integrations:**
- Gmail receipt search/forwarding
- Google Sheets API writeback
- Notion / Airtable trackers
- Stripe / PayPal / Shopify revenue import
- QuickBooks / Wave export after secure backend setup
- CRM deal revenue connection
- Scheduled monthly finance digest

**Governance rules:**
- No secrets in frontend files.
- Human approval before writes.
- Audit log for changes.
- Professional review for tax/accounting decisions.

**Visual idea:** Integration hub with approval gate in the center.

---

## Slide 26 — Future Plan: AI CFO Dashboard

**Title:** Future Plan: From Finance Agent to AI CFO Dashboard

**Possible future modules:**
- Cash-flow forecast
- Subscription waste detector
- Profitability by client/project
- Marketing ROI calculator
- Pricing recommendation assistant
- Tax-prep document checklist
- Weekly business health score
- “What should I do next?” decision agent

**Visual idea:** AI CFO dashboard with scorecards.

---

## Slide 27 — Final Takeaway

**Title:** The Goal Is Financial Clarity, Not Full Automation

**Key message:**
A good finance agent helps a solo founder:
- Capture messy records.
- Review and correct data.
- Understand income, expenses, and cash flow.
- Make better spending decisions.
- Prepare cleaner information for professionals.

**Closing line:**
Start simple: manual input, human review, Google Sheets export. Then add automation only when the data model and safety rules are clear.

**Visual idea:** Founder looking at clean dashboard; “Review-first automation” as the final phrase.

---

# Optional PPT Design Direction

**Recommended style:** Modern finance operations dashboard.

**Palette:**
- Primary: deep navy / charcoal
- Secondary: mint green or teal
- Accent: warm yellow for highlights
- Background: light cards on dark or off-white sections

**Motif:**
Use repeated pipeline arrows, spreadsheet cards, and review badges.

**Suggested sections:**
1. Why finance matters
2. MVP workflow
3. Skill + console demo
4. Advanced tools
5. Future roadmap

---

# Optional Classroom Demo Script

1. Open the AI Solo Company website and show the Class 5 Finance Agent Tools section.
2. Open Admin Console → Finance Agent Studio.
3. Paste the OpenAI subscription example.
4. Extract JSON and explain each field.
5. Save the row.
6. Add a hosting expense and one client payment.
7. Generate monthly summary.
8. Ask the AI CFO question: “Can I afford to spend $300 on ads this month?”
9. Show advanced prompt builders:
   - Receipt OCR prompt
   - Integration planner
   - Recurring expense audit
   - Budget simulator
   - Tax review checklist
10. End with safety: review-first, no live bank integration, professional tax/accounting review.
