# CRM Connectors Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Add optional outbound connectors from Easiio Solo CRM / website chatbot leads to popular small-business CRMs, starting with HubSpot and a small set of free-tier-friendly CRMs.

**Architecture:** Keep Solo CRM as the local source of truth, then add provider adapters that can sync contacts, companies, deals, notes, and lead activities outward. Connectors must be opt-in per site/organization, store credentials only server-side, and never expose CRM API tokens in browser JavaScript, WordPress shortcodes, or public widget config.

**Tech Stack:** Python stdlib-first connector layer, SQLite-backed Solo CRM, website chatbot backend lead hooks, environment variables / protected config JSON for credentials, unit tests with mocked HTTP clients.

---

## Recommended CRM Targets

Start with CRMs that are popular with small businesses and have either a free plan or a practical free trial / free-entry path. Verify current pricing and API access before production rollout because free-tier API rules can change.

### Phase 1 providers

1. **HubSpot CRM**
   - Best first connector.
   - Very popular with small businesses.
   - Free CRM tier is commonly used for contacts/companies/deals.
   - API model is mature and well documented.

2. **Zoho CRM / Bigin by Zoho CRM**
   - Popular SMB option.
   - Zoho ecosystem is common among small businesses.
   - Good second connector, but OAuth/token setup is more involved.

3. **Bitrix24**
   - Often has a generous free tier.
   - Useful for small teams that want CRM + tasks + collaboration.

4. **Freshsales / Freshworks CRM**
   - Popular SMB sales CRM.
   - Good candidate if API access is available for the desired plan.

### Optional lightweight targets

5. **Airtable**
   - Not a traditional CRM, but many small businesses use it as a lightweight CRM.
   - Great for early-stage users who want a simple table of leads.

6. **Google Sheets**
   - Not a CRM, but extremely useful as a no-cost export/sync target.
   - Good fallback connector for students and very small businesses.

### Later / not first

7. **Pipedrive**
   - Popular CRM, but usually trial-first rather than long-term free.
   - Good later connector for paid SMB users.

8. **Salesforce**
   - Enterprise-heavy; not ideal for first small-business/free connector.
   - Add later only if customer demand exists.

---

## Data Mapping

### Solo CRM to external CRM contact

```text
SoloCRM contact.name      -> external contact first/last/full name
SoloCRM contact.email     -> external email
SoloCRM contact.phone     -> external phone
SoloCRM contact.role      -> external job title
SoloCRM contact.status    -> lifecycle stage / lead status
SoloCRM contact.source    -> lead source
SoloCRM contact.tags      -> tags / labels / custom property
SoloCRM contact.notes     -> notes / description
website.site_id           -> custom property: easiio_site_id
visitor.visitor_key       -> custom property: easiio_visitor_key
```

### Solo CRM company to external CRM company/account

```text
SoloCRM company.name      -> company/account name
SoloCRM company.website   -> website/domain
SoloCRM company.industry  -> industry
SoloCRM company.notes     -> notes
```

### Solo CRM deal to external CRM deal/opportunity

```text
SoloCRM deal.title        -> deal name
SoloCRM deal.value        -> amount
SoloCRM deal.currency     -> currency
SoloCRM deal.stage        -> pipeline stage
SoloCRM deal.probability  -> probability
SoloCRM deal.close_date   -> expected close date
SoloCRM deal.notes        -> deal description / note
```

### Solo CRM activity to external CRM note/task

```text
SoloCRM activity.kind         -> note/call/email/meeting/task
SoloCRM activity.body         -> note body
SoloCRM activity.happened_at  -> activity timestamp
SoloCRM activity.follow_up_at -> task due date
```

---

## Connector Design

### New module layout

Create under:

```text
modules/solo_crm/connectors/
  __init__.py
  base.py
  hubspot.py
  zoho.py
  bitrix24.py
  freshsales.py
  airtable.py
  google_sheets.py
  config.py
  sync.py
```

Tests:

```text
modules/solo_crm/tests/test_crm_connectors_base.py
modules/solo_crm/tests/test_crm_connector_hubspot.py
modules/solo_crm/tests/test_crm_connector_config.py
modules/solo_crm/tests/test_crm_connector_sync.py
```

### Connector interface

All providers should implement the same small interface:

```python
class CRMConnector:
    provider = "base"

    def upsert_contact(self, contact, company=None, website=None, visitor=None):
        raise NotImplementedError

    def upsert_company(self, company):
        raise NotImplementedError

    def upsert_deal(self, deal, contact=None, company=None):
        raise NotImplementedError

    def add_activity(self, activity, contact=None, deal=None):
        raise NotImplementedError

    def test_connection(self):
        raise NotImplementedError
```

### Configuration model

Store connector settings server-side only. Suggested protected config path:

```text
~/.hermes/tools/solo_crm/data/crm_connectors.json
```

Example sanitized structure:

```json
{
  "sites": {
    "ai-solo-company": {
      "enabled": true,
      "providers": {
        "hubspot": {
          "enabled": true,
          "mode": "sync_on_lead",
          "token_env": "HUBSPOT_PRIVATE_APP_TOKEN",
          "pipeline_id": "default",
          "dealstage": "appointmentscheduled"
        }
      }
    }
  }
}
```

Never store raw tokens in repo. Prefer env vars:

```bash
HUBSPOT_PRIVATE_APP_TOKEN=...
ZOHO_CLIENT_ID=...
ZOHO_CLIENT_SECRET=...
BITRIX24_WEBHOOK_URL=...
FRESHSALES_API_KEY=...
AIRTABLE_API_KEY=...
GOOGLE_SERVICE_ACCOUNT_JSON=...
```

---

## Implementation Tasks

### Task 1: Add connector base interface and no-op connector

**Objective:** Create a stable adapter interface and a safe no-op provider for tests and disabled sync.

**Files:**
- Create: `modules/solo_crm/connectors/__init__.py`
- Create: `modules/solo_crm/connectors/base.py`
- Test: `modules/solo_crm/tests/test_crm_connectors_base.py`

**Verification:**

```bash
python3 modules/solo_crm/tests/test_crm_connectors_base.py
```

Expected: connector base tests pass.

### Task 2: Add protected connector config loader

**Objective:** Load per-site connector config without exposing or printing secrets.

**Files:**
- Create: `modules/solo_crm/connectors/config.py`
- Test: `modules/solo_crm/tests/test_crm_connector_config.py`

**Requirements:**
- Default config path uses `SOLO_CRM_CONNECTORS_CONFIG` or `~/.hermes/tools/solo_crm/data/crm_connectors.json`.
- Return sanitized config for UI/API responses.
- Resolve token values from environment variables only.
- Never include raw token values in returned dicts, logs, or exceptions.

**Verification:**

```bash
python3 modules/solo_crm/tests/test_crm_connector_config.py
```

### Task 3: Implement HubSpot connector first

**Objective:** Add contact/company/deal/note sync to HubSpot using private app token auth.

**Files:**
- Create: `modules/solo_crm/connectors/hubspot.py`
- Test: `modules/solo_crm/tests/test_crm_connector_hubspot.py`

**Implementation notes:**
- Use injectable HTTP function/client so tests do not call real HubSpot.
- Support contact upsert by email.
- Support company upsert by domain/name where possible.
- Support deal creation/update using configured pipeline/stage.
- Support note/activity creation.
- Add Easiio custom properties only if already available; otherwise degrade gracefully.

**Verification:**

```bash
python3 modules/solo_crm/tests/test_crm_connector_hubspot.py
```

### Task 4: Add sync orchestration layer

**Objective:** Add one function that website chatbot / Solo CRM can call after lead creation.

**Files:**
- Create: `modules/solo_crm/connectors/sync.py`
- Modify: `modules/solo_crm/crm_core.py` only if needed for helper methods.
- Test: `modules/solo_crm/tests/test_crm_connector_sync.py`

**Function shape:**

```python
def sync_contact_to_enabled_crms(crm, site_id, contact_id, deal_id=None, activity_id=None):
    """Sync one CRM contact/deal/activity to enabled external CRM providers."""
```

**Verification:**

```bash
python3 modules/solo_crm/tests/test_crm_connector_sync.py
```

### Task 5: Connect website chatbot lead flow to external CRM sync

**Objective:** When chatbot captures a lead, optionally sync it to enabled external CRMs after local Solo CRM write succeeds.

**Files:**
- Modify: `modules/website_chatbot/backend/app.py`
- Test: `modules/website_chatbot/tests/test_backend.py`

**Rules:**
- Local Solo CRM write remains the source of truth.
- External sync failure must not break visitor lead submission.
- Response may include sanitized `crm_sync` status, for example:

```json
{
  "crm_sync": {
    "enabled": true,
    "providers": [
      {"provider": "hubspot", "ok": true, "external_contact_id": "123"}
    ]
  }
}
```

No secrets in response.

### Task 6: Add admin settings API for connector status

**Objective:** Let protected admin UI view and update connector enablement without exposing secrets.

**Files:**
- Modify or create backend route in Solo CRM or website gateway.
- Suggested route: `GET /api/admin/crm-connectors?site_id=...`
- Suggested route: `POST /api/admin/crm-connectors`

**Rules:**
- Admin-only.
- Show provider enabled/status fields.
- Show token status as `configured: true/false`, never raw token.

### Task 7: Add connectors after HubSpot

**Objective:** Add providers one at a time only after HubSpot is tested.

Suggested order:

1. Airtable or Google Sheets — easiest for students/small businesses.
2. Zoho CRM / Bigin.
3. Bitrix24.
4. Freshsales.
5. Pipedrive if needed.
6. Salesforce only if explicitly requested.

---

## Security Requirements

- Never expose external CRM tokens in browser JavaScript, WordPress plugin settings rendered to the public page, logs, tests, or API responses.
- Do not commit connector config JSON containing real tokens.
- Do not print request authorization headers.
- Make all external sync failures non-blocking for lead capture.
- Store provider external IDs in local CRM metadata only if needed for future idempotent updates.
- Add retry/backoff later; keep Phase 1 simple.

---

## Acceptance Criteria

Phase 1 is complete when:

1. HubSpot connector can upsert a contact from a Solo CRM contact using mocked tests.
2. Connector config loads from protected local config and env vars.
3. Chatbot lead capture can call sync orchestration without exposing secrets.
4. External sync failure does not fail local lead capture.
5. Tests pass:

```bash
python3 modules/solo_crm/tests/test_crm_core.py
python3 modules/solo_crm/tests/test_crm_connectors_base.py
python3 modules/solo_crm/tests/test_crm_connector_config.py
python3 modules/solo_crm/tests/test_crm_connector_hubspot.py
python3 modules/solo_crm/tests/test_crm_connector_sync.py
python3 modules/website_chatbot/tests/test_backend.py
```

6. Secret scan confirms no tokens/config secrets were committed.

---

## Phase 2 Addendum: Google Sheets Connector

Phase 2 implemented Google Sheets as the first lightweight/free-friendly connector. It uses a server-side Google Apps Script Web App URL stored in an environment variable, then appends sanitized Solo CRM contact/company/deal/activity rows to a sheet. This avoids browser-side credentials and avoids adding Python OAuth dependencies for small-business/student demos.

Additional files:

```text
modules/solo_crm/connectors/google_sheets.py
modules/solo_crm/tests/test_crm_connector_google_sheets.py
```

Additional safe config example:

```json
{
  "sites": {
    "ai-solo-company": {
      "enabled": true,
      "providers": {
        "google_sheets": {
          "enabled": true,
          "mode": "sync_on_lead",
          "webhook_url_env": "GOOGLE_SHEETS_LEADS_WEBHOOK_URL",
          "sheet_name": "Leads",
          "spreadsheet_id": "optional-spreadsheet-id-for-script-routing"
        }
      }
    }
  }
}
```

Server-side environment only:

```bash
GOOGLE_SHEETS_LEADS_WEBHOOK_URL=***
```

Phase 2 acceptance criteria:

1. Google Sheets connector appends contact/company/deal/activity rows through a mocked HTTP client.
2. `webhook_url_env` resolves to `webhook_url` for runtime use, but sanitized config never returns the raw webhook URL.
3. `sync_contact_to_enabled_crms(...)` can call both HubSpot and Google Sheets providers when enabled.
4. Google Sheets failures are non-blocking and return sanitized provider status.
5. Connector tests, chatbot backend tests, static widget/plugin tests, dry-run installer, whitespace check, runtime artifact scan, and secret scan pass.

---

## Recommended Rollout

1. Build HubSpot connector in source-only repo first.
2. Add one demo config using fake env var names only.
3. Add admin UI later for selecting connector provider per site.
4. Validate with a real HubSpot test account only after code review.
5. Add Airtable / Google Sheets connector for small-business and student demos.
6. Add Zoho / Bitrix24 / Freshsales based on user demand.
