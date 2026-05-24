# Solo CRM MCP Server

A lightweight, standalone CRM for the AI solo company project. It stores data in SQLite and exposes an MCP stdio server so Hermes can use it directly as tools.

## Location

`~/.hermes/tools/solo_crm/`

Default database:

`~/.hermes/tools/solo_crm/solo_crm.db`

Override database path with `SOLO_CRM_DB=/path/to/crm.db` or `server.py --db /path/to/crm.db`.

## MCP tools exposed

- `crm_create_company`
- `crm_create_contact`
- `crm_search_contacts`
- `crm_get_contact`
- `crm_update_contact`
- `crm_create_deal`
- `crm_update_deal`
- `crm_list_deals`
- `crm_add_activity`
- `crm_list_activities`
- `crm_complete_activity`
- `crm_next_followups`
- `crm_summary`

## Run standalone

```bash
python3 ~/.hermes/tools/solo_crm/server.py --summary
python3 ~/.hermes/tools/solo_crm/server.py
```

The second command starts stdio MCP mode.

## Hermes MCP config

Add this to `~/.hermes/config.yaml` under `mcp_servers`:

```yaml
mcp_servers:
  solo_crm:
    command: "python3"
    args: ["/home/jianl/.hermes/tools/solo_crm/server.py"]
    timeout: 60
    connect_timeout: 30
```

Restart Hermes or use `/reload-mcp` in CLI after adding the config. Tools will appear as `mcp_solo_crm_crm_create_contact`, `mcp_solo_crm_crm_search_contacts`, etc.

## Optional external CRM connectors

Solo CRM can optionally sync locally saved chatbot leads to external CRMs. Local SQLite remains the source of truth; connector failures do not block lead capture.

Phase 1 includes a HubSpot connector. Phase 2 adds a Google Sheets connector for students and very small businesses that want a simple shared lead table. Phase 3 adds an admin-safe configuration API and reusable chatbot customizer UI controls so operators can enable providers per site without editing JSON by hand. Phase 4 adds a local sync log and retry queue so failed external CRM sync attempts can be reviewed and retried from the admin UI while local Solo CRM remains the source of truth.

```text
connectors/
  base.py
  config.py
  google_sheets.py
  hubspot.py
  sync.py
  sync_log.py
```

Protected connector config defaults to:

```text
~/.hermes/tools/solo_crm/data/crm_connectors.json
```

Override with:

```bash
SOLO_CRM_CONNECTORS_CONFIG=/path/to/crm_connectors.json
```

Example HubSpot config using an environment variable for the private app token:

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

Example Google Sheets config using an environment variable for a private Google Apps Script Web App URL:

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

The Google Sheets connector posts sanitized contact/company/deal/activity rows to an Apps Script webhook. Keep the webhook URL server-side only; do not expose it in widget JavaScript, WordPress settings, logs, or commits.

Phase 3 admin configuration endpoints are exposed by the chatbot backend and protected by the site gateway admin session when used with the hosted/admin site:

```text
GET  /api/crm-connectors/config?site_id=ai-solo-company
POST /api/crm-connectors/config
```

The admin customizer module (`modules/website_chatbot/admin/chatbot-customizer.js`) now includes a **CRM connectors** card. It saves only safe provider settings such as `token_env`, `webhook_url_env`, `pipeline_id`, `dealstage`, `sheet_name`, and `spreadsheet_id`. It intentionally does not collect raw HubSpot `access_token` values or raw Google Sheets `webhook_url` values.

Phase 4 sync logging defaults to:

```text
~/.hermes/tools/solo_crm/data/crm_sync_log.json
```

Override with:

```bash
SOLO_CRM_SYNC_LOG=/path/to/crm_sync_log.json
```

The chatbot backend exposes admin-safe sync operations through the protected gateway:

```text
GET  /api/crm-connectors/sync-log?site_id=ai-solo-company&limit=25
POST /api/crm-connectors/retry
```

`/api/crm-connectors/sync-log` returns sanitized events only: provider name, status, local contact/deal/activity IDs, retry state, timestamps, and safe provider result IDs. It does not return raw provider tokens, webhook URLs, or env values. `/api/crm-connectors/retry` accepts `{ "event_id": "..." }` and retries only the provider from that failed event.

Example POST body:

```json
{
  "site_id": "ai-solo-company",
  "site_config": {
    "enabled": true,
    "providers": {
      "hubspot": {
        "enabled": true,
        "mode": "sync_on_lead",
        "token_env": "HUBSPOT_PRIVATE_APP_TOKEN",
        "pipeline_id": "default",
        "dealstage": "appointmentscheduled"
      },
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
```

Set secrets only in server-side environment, never in browser JavaScript or Git:

```bash
HUBSPOT_PRIVATE_APP_TOKEN=***
GOOGLE_SHEETS_LEADS_WEBHOOK_URL=***
```

## Test

```bash
python3 ~/.hermes/tools/solo_crm/tests/test_crm_core.py
python3 ~/.hermes/tools/solo_crm/tests/test_crm_connectors_base.py
python3 ~/.hermes/tools/solo_crm/tests/test_crm_connector_config.py
python3 ~/.hermes/tools/solo_crm/tests/test_crm_connector_google_sheets.py
python3 ~/.hermes/tools/solo_crm/tests/test_crm_connector_hubspot.py
python3 ~/.hermes/tools/solo_crm/tests/test_crm_connector_sync.py
python3 ~/.hermes/tools/solo_crm/tests/test_crm_connector_sync_log.py
```
