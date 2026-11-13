# HubSpot object cheatsheet

Common CRM object names used by the v3 object APIs:

- `contacts`
- `companies`
- `deals`
- `tickets`
- `leads` (if enabled in the account)

Useful search patterns:

```bash
# Contact by email
python hubspot_crm.py contacts search --email person@example.com

# Company by domain
python hubspot_crm.py companies search --domain example.com

# Deal search by free text plus selected properties
python hubspot_crm.py objects search deals --query "Acme" --properties dealname,pipeline,dealstage
```

Generic filter syntax in the CLI:

```bash
--filter property=value
```

Examples:

- `--filter pipeline=default`
- `--filter hs_lead_status=NEW`
- `--filter lifecyclestage=lead`

Use the `raw` command when the skill does not yet expose a dedicated shortcut for an endpoint.
