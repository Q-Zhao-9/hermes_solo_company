#!/usr/bin/env python3
"""Standalone MCP stdio server for the Solo Company CRM.

This intentionally avoids external Python dependencies. It implements the MCP
JSON-RPC methods Hermes needs for stdio discovery and tool calls:
initialize, notifications/initialized, tools/list, and tools/call.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable

from crm_core import DEFAULT_DB, SoloCRM


def schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {"type": "object", "properties": properties, "required": required or []}


def prop(type_: str, description: str, **extra: Any) -> dict[str, Any]:
    out = {"type": type_, "description": description}
    out.update(extra)
    return out


TOOLS: dict[str, dict[str, Any]] = {

    "crm_create_organization": {
        "description": "Create or update an organization/tenant so multiple websites can keep separate CRM data.",
        "inputSchema": schema({
            "name": prop("string", "Organization/account name"),
            "slug": prop("string", "Stable organization slug"),
            "website": prop("string", "Primary organization website"),
            "notes": prop("string", "Free-form notes"),
        }, ["name"]),
    },
    "crm_list_organizations": {
        "description": "List organizations/tenants in the CRM.",
        "inputSchema": schema({"limit": prop("integer", "Maximum organizations to return", default=50)}),
    },
    "crm_create_website": {
        "description": "Create or update a tracked website for an organization.",
        "inputSchema": schema({
            "site_id": prop("string", "Stable website identifier used by widget data-site-id"),
            "name": prop("string", "Website display name"),
            "organization_id": prop("integer", "Related organization id"),
            "domain": prop("string", "Website domain"),
            "url": prop("string", "Website URL"),
            "notes": prop("string", "Free-form notes"),
        }, ["site_id"]),
    },
    "crm_list_websites": {
        "description": "List tracked websites, optionally filtered by organization.",
        "inputSchema": schema({
            "organization_id": prop("integer", "Optional organization id filter"),
            "limit": prop("integer", "Maximum websites to return", default=50),
        }),
    },
    "crm_record_website_visit": {
        "description": "Record a website visitor/page view for analytics and CRM attribution.",
        "inputSchema": schema({
            "site_id": prop("string", "Website identifier"),
            "visitor_key": prop("string", "Stable visitor identifier"),
            "session_id": prop("string", "Chat/session identifier"),
            "page_url": prop("string", "Page URL"),
            "page_title": prop("string", "Page title"),
            "referrer": prop("string", "Referrer URL"),
            "user_agent": prop("string", "Browser user agent"),
            "ip_address": prop("string", "Visitor IP address if available"),
            "utm": {"type": "object", "description": "UTM parameters"},
            "organization_name": prop("string", "Organization name to create if needed"),
            "website_name": prop("string", "Website name to create if needed"),
            "domain": prop("string", "Website domain"),
        }),
    },
    "crm_list_website_visitors": {
        "description": "List website visitors by website or organization.",
        "inputSchema": schema({
            "site_id": prop("string", "Optional website identifier filter"),
            "organization_id": prop("integer", "Optional organization id filter"),
            "limit": prop("integer", "Maximum visitors to return", default=50),
        }),
    },
    "crm_list_website_customers": {
        "description": "List CRM contacts/customers attributed to a website or organization.",
        "inputSchema": schema({
            "site_id": prop("string", "Optional website identifier filter"),
            "organization_id": prop("integer", "Optional organization id filter"),
            "limit": prop("integer", "Maximum customers to return", default=50),
        }),
    },
    "crm_website_summary": {
        "description": "Return website/organization analytics counts: websites, visitors, visits, contacts, open deals.",
        "inputSchema": schema({
            "site_id": prop("string", "Optional website identifier filter"),
            "organization_id": prop("integer", "Optional organization id filter"),
        }),
    },
    "crm_create_company": {
        "description": "Create or update a company/account in the solo-company CRM.",
        "inputSchema": schema({
            "name": prop("string", "Company/account name"),
            "website": prop("string", "Company website URL"),
            "industry": prop("string", "Industry or segment"),
            "notes": prop("string", "Free-form notes"),
        }, ["name"]),
    },
    "crm_create_contact": {
        "description": "Create a CRM contact/lead/customer.",
        "inputSchema": schema({
            "name": prop("string", "Contact full name"),
            "email": prop("string", "Email address"),
            "phone": prop("string", "Phone number"),
            "company_id": prop("integer", "Related company id"),
            "role": prop("string", "Job title/role"),
            "status": prop("string", "lead, prospect, customer, partner, inactive", default="lead"),
            "source": prop("string", "Lead source"),
            "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags such as founder, investor, ai-solo-company"},
            "notes": prop("string", "Free-form notes"),
        }, ["name"]),
    },
    "crm_search_contacts": {
        "description": "Search CRM contacts by text, status, or tag.",
        "inputSchema": schema({
            "query": prop("string", "Search text across name, email, phone, company, and notes"),
            "status": prop("string", "Optional contact status filter"),
            "tag": prop("string", "Optional tag filter"),
            "limit": prop("integer", "Maximum contacts to return", default=20),
        }),
    },
    "crm_get_contact": {
        "description": "Get one CRM contact by id.",
        "inputSchema": schema({"contact_id": prop("integer", "Contact id")}, ["contact_id"]),
    },
    "crm_update_contact": {
        "description": "Update fields on a CRM contact.",
        "inputSchema": schema({
            "contact_id": prop("integer", "Contact id"),
            "name": prop("string", "Contact full name"),
            "email": prop("string", "Email address"),
            "phone": prop("string", "Phone number"),
            "company_id": prop("integer", "Related company id"),
            "role": prop("string", "Job title/role"),
            "status": prop("string", "lead, prospect, customer, partner, inactive"),
            "source": prop("string", "Lead source"),
            "tags": {"type": "array", "items": {"type": "string"}, "description": "Replacement tag list"},
            "notes": prop("string", "Free-form notes"),
        }, ["contact_id"]),
    },
    "crm_create_deal": {
        "description": "Create a deal/opportunity in the pipeline.",
        "inputSchema": schema({
            "title": prop("string", "Deal title"),
            "contact_id": prop("integer", "Related contact id"),
            "company_id": prop("integer", "Related company id"),
            "value": prop("number", "Deal value"),
            "currency": prop("string", "Currency code", default="USD"),
            "stage": prop("string", "Pipeline stage: new, qualified, proposal, won, lost", default="new"),
            "probability": prop("integer", "Close probability percent"),
            "close_date": prop("string", "Expected close date YYYY-MM-DD"),
            "notes": prop("string", "Free-form notes"),
        }, ["title"]),
    },
    "crm_update_deal": {
        "description": "Update a deal/opportunity.",
        "inputSchema": schema({
            "deal_id": prop("integer", "Deal id"),
            "title": prop("string", "Deal title"),
            "contact_id": prop("integer", "Related contact id"),
            "company_id": prop("integer", "Related company id"),
            "value": prop("number", "Deal value"),
            "currency": prop("string", "Currency code"),
            "stage": prop("string", "Pipeline stage"),
            "probability": prop("integer", "Close probability percent"),
            "close_date": prop("string", "Expected close date YYYY-MM-DD"),
            "notes": prop("string", "Free-form notes"),
        }, ["deal_id"]),
    },
    "crm_list_deals": {
        "description": "List deals, optionally filtered by stage or contact.",
        "inputSchema": schema({
            "stage": prop("string", "Optional pipeline stage filter"),
            "contact_id": prop("integer", "Optional contact id filter"),
            "limit": prop("integer", "Maximum deals to return", default=50),
        }),
    },
    "crm_add_activity": {
        "description": "Add a note, call, email, meeting, task, or follow-up activity.",
        "inputSchema": schema({
            "contact_id": prop("integer", "Related contact id"),
            "deal_id": prop("integer", "Related deal id"),
            "kind": prop("string", "note, call, email, meeting, task", default="note"),
            "body": prop("string", "Activity details"),
            "happened_at": prop("string", "When it happened; ISO timestamp or YYYY-MM-DD"),
            "follow_up_at": prop("string", "Follow-up date/time; ISO timestamp or YYYY-MM-DD"),
            "completed": prop("boolean", "Whether the activity/follow-up is completed"),
        }, ["body"]),
    },
    "crm_list_activities": {
        "description": "List activities for a contact, deal, or all recent activities.",
        "inputSchema": schema({
            "contact_id": prop("integer", "Optional contact id filter"),
            "deal_id": prop("integer", "Optional deal id filter"),
            "limit": prop("integer", "Maximum activities to return", default=50),
        }),
    },
    "crm_complete_activity": {
        "description": "Mark an activity/follow-up as completed.",
        "inputSchema": schema({"activity_id": prop("integer", "Activity id")}, ["activity_id"]),
    },
    "crm_next_followups": {
        "description": "List open follow-ups ordered by date.",
        "inputSchema": schema({"limit": prop("integer", "Maximum follow-ups to return", default=10)}),
    },
    "crm_summary": {
        "description": "Return CRM counts, open pipeline value, follow-up count, and database path.",
        "inputSchema": schema({}),
    },
}


def clean_args(args: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in (args or {}).items() if v is not None}


def dispatch(crm: SoloCRM, tool_name: str, args: dict[str, Any]) -> Any:
    args = clean_args(args)
    handlers: dict[str, Callable[..., Any]] = {
        "crm_create_organization": crm.create_organization,
        "crm_list_organizations": crm.list_organizations,
        "crm_create_website": crm.create_website,
        "crm_list_websites": crm.list_websites,
        "crm_record_website_visit": crm.record_website_visit,
        "crm_list_website_visitors": crm.list_website_visitors,
        "crm_list_website_customers": crm.list_website_customers,
        "crm_website_summary": crm.website_summary,
        "crm_create_company": crm.create_company,
        "crm_create_contact": crm.create_contact,
        "crm_search_contacts": crm.search_contacts,
        "crm_get_contact": lambda contact_id: crm.get_contact(int(contact_id)),
        "crm_update_contact": lambda contact_id, **kw: crm.update_contact(int(contact_id), **kw),
        "crm_create_deal": crm.create_deal,
        "crm_update_deal": lambda deal_id, **kw: crm.update_deal(int(deal_id), **kw),
        "crm_list_deals": crm.list_deals,
        "crm_add_activity": crm.add_activity,
        "crm_list_activities": crm.list_activities,
        "crm_complete_activity": lambda activity_id: crm.complete_activity(int(activity_id)),
        "crm_next_followups": crm.next_followups,
        "crm_summary": crm.summary,
    }
    if tool_name not in handlers:
        raise ValueError(f"Unknown tool: {tool_name}")
    return handlers[tool_name](**args)


def tool_result(payload: Any) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=2)}]}


def handle_request(crm: SoloCRM, request: dict[str, Any]) -> dict[str, Any] | None:
    method = request.get("method")
    req_id = request.get("id")
    if method == "notifications/initialized":
        return None
    try:
        if method == "initialize":
            result = {
                "protocolVersion": request.get("params", {}).get("protocolVersion", "2024-11-05"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "solo-crm", "version": "0.1.0"},
            }
        elif method == "tools/list":
            result = {"tools": [{"name": name, **meta} for name, meta in TOOLS.items()]}
        elif method == "tools/call":
            params = request.get("params") or {}
            result = tool_result(dispatch(crm, params.get("name", ""), params.get("arguments") or {}))
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}
        return {"jsonrpc": "2.0", "id": req_id, "result": result}
    except Exception as exc:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(exc)}}


def serve_stdio(db_path: str | Path = DEFAULT_DB) -> None:
    crm = SoloCRM(db_path)
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            response = handle_request(crm, request)
        except Exception as exc:
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {exc}"}}
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description="Solo Company CRM MCP server")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite DB path (default: ~/.hermes/tools/solo_crm/solo_crm.db)")
    parser.add_argument("--summary", action="store_true", help="Print CRM summary and exit")
    args = parser.parse_args()
    if args.summary:
        print(json.dumps(SoloCRM(args.db).summary(), indent=2))
        return 0
    serve_stdio(args.db)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
