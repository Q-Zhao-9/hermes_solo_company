# HubSpot CRM MCP scaffold

Standalone stdio MCP server scaffold for HubSpot CRM.

## Purpose

This module is the next step after the reusable `hubspot-crm` skill. It turns the same review-first HubSpot operations into native MCP tools that Hermes can discover via `mcp_servers`.

## Current tool set

- `hubspot_auth_check`
- `hubspot_list_owners`
- `hubspot_list_pipelines`
- `hubspot_get_object`
- `hubspot_search_objects`
- `hubspot_upsert_contact`
- `hubspot_raw_request`

## Environment

```bash
export HUBSPOT_ACCESS_TOKEN='YOUR_PRIVATE_APP_TOKEN'
export HUBSPOT_BASE_URL='https://api.hubapi.com'
```

## Smoke checks

```bash
python3 modules/hubspot_crm_mcp/server.py --summary
python3 -m unittest modules/hubspot_crm_mcp/tests/test_core.py
python3 -m unittest modules/hubspot_crm_mcp/tests/test_server.py
```

## Example Hermes config snippet

```yaml
mcp_servers:
  hubspot_crm:
    command: python3
    args:
      - /absolute/path/to/modules/hubspot_crm_mcp/server.py
    env:
      HUBSPOT_ACCESS_TOKEN: "${HUBSPOT_ACCESS_TOKEN}"
    timeout: 60
    connect_timeout: 30
```

## Next expansions

- property discovery tools
- company upsert and associations
- deal creation and pipeline-stage aware transitions
- engagement/note creation
- lead-ingestion tools for website/chatbot workflows
