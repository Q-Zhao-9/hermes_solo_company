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

Phase 1 includes a HubSpot connector under:

```text
connectors/
  base.py
  config.py
  hubspot.py
  sync.py
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

Set the token only in server-side environment, never in browser JavaScript or Git:

```bash
HUBSPOT_PRIVATE_APP_TOKEN=...
```

## Test

```bash
python3 ~/.hermes/tools/solo_crm/tests/test_crm_core.py
python3 ~/.hermes/tools/solo_crm/tests/test_crm_connectors_base.py
python3 ~/.hermes/tools/solo_crm/tests/test_crm_connector_config.py
python3 ~/.hermes/tools/solo_crm/tests/test_crm_connector_hubspot.py
python3 ~/.hermes/tools/solo_crm/tests/test_crm_connector_sync.py
```
