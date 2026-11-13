#!/usr/bin/env python3
"""Standalone MCP stdio server scaffold for HubSpot CRM."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Callable

from core import HubSpotClient, HubSpotError, parse_filter_pairs


def schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {'type': 'object', 'properties': properties, 'required': required or []}


def prop(type_: str, description: str, **extra: Any) -> dict[str, Any]:
    item = {'type': type_, 'description': description}
    item.update(extra)
    return item


TOOLS: dict[str, dict[str, Any]] = {
    'hubspot_auth_check': {
        'description': 'Check HubSpot auth by performing a small read-only owners call.',
        'inputSchema': schema({}),
    },
    'hubspot_list_owners': {
        'description': 'List HubSpot owners.',
        'inputSchema': schema({'limit': prop('integer', 'Maximum owners to return', default=100)}),
    },
    'hubspot_list_pipelines': {
        'description': 'List pipelines for a HubSpot CRM object type such as deals or tickets.',
        'inputSchema': schema({'object_type': prop('string', 'CRM object type, for example deals')}, ['object_type']),
    },
    'hubspot_get_object': {
        'description': 'Get one HubSpot CRM object by type and id.',
        'inputSchema': schema({
            'object_type': prop('string', 'CRM object type such as contacts or companies'),
            'object_id': prop('string', 'Object id'),
            'properties': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Optional property names'},
        }, ['object_type', 'object_id']),
    },
    'hubspot_search_objects': {
        'description': 'Search HubSpot CRM objects by type, query, filters, and selected properties.',
        'inputSchema': schema({
            'object_type': prop('string', 'CRM object type such as contacts, companies, or deals'),
            'query': prop('string', 'Optional free-text query'),
            'filters': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Filter strings in property=value format'},
            'properties': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Optional property names'},
            'limit': prop('integer', 'Maximum rows to return', default=10),
        }, ['object_type']),
    },
    'hubspot_upsert_contact': {
        'description': 'Create or update one HubSpot contact by email.',
        'inputSchema': schema({
            'email': prop('string', 'Contact email'),
            'firstname': prop('string', 'First name'),
            'lastname': prop('string', 'Last name'),
            'phone': prop('string', 'Phone number'),
            'company': prop('string', 'Company name'),
            'website': prop('string', 'Website URL'),
            'lifecyclestage': prop('string', 'Lifecycle stage'),
            'jobtitle': prop('string', 'Job title'),
            'dry_run': prop('boolean', 'Preview payload only without writing', default=False),
        }, ['email']),
    },
    'hubspot_raw_request': {
        'description': 'Call an arbitrary HubSpot endpoint path for advanced cases.',
        'inputSchema': schema({
            'method': prop('string', 'HTTP method such as GET or POST'),
            'path': prop('string', 'API path such as /crm/v3/objects/contacts/search'),
            'body': {'type': 'object', 'description': 'Optional JSON request body'},
        }, ['method', 'path']),
    },
}


def clean_args(args: dict[str, Any] | None) -> dict[str, Any]:
    return {k: v for k, v in (args or {}).items() if v is not None}


def dispatch(client: HubSpotClient, tool_name: str, args: dict[str, Any]) -> Any:
    args = clean_args(args)
    handlers: dict[str, Callable[..., Any]] = {
        'hubspot_auth_check': client.auth_check,
        'hubspot_list_owners': client.list_owners,
        'hubspot_list_pipelines': client.list_pipelines,
        'hubspot_get_object': client.get_object,
        'hubspot_search_objects': lambda object_type, query=None, filters=None, properties=None, limit=10: client.search_objects(
            object_type,
            query=query,
            filters=parse_filter_pairs(filters),
            properties=properties,
            limit=limit,
        ),
        'hubspot_upsert_contact': client.upsert_contact,
        'hubspot_raw_request': lambda method, path, body=None: client.request(method, path, body=body),
    }
    if tool_name not in handlers:
        raise HubSpotError(f'Unknown tool: {tool_name}')
    return handlers[tool_name](**args)


def tool_result(payload: Any) -> dict[str, Any]:
    return {'content': [{'type': 'text', 'text': json.dumps(payload, ensure_ascii=False, indent=2)}]}


def handle_message(client: HubSpotClient, message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get('method')
    request_id = message.get('id')
    if method == 'initialize':
        return {
            'jsonrpc': '2.0',
            'id': request_id,
            'result': {
                'protocolVersion': '2025-03-26',
                'serverInfo': {'name': 'hubspot-crm-mcp', 'version': '0.1.0'},
                'capabilities': {'tools': {}},
            },
        }
    if method == 'notifications/initialized':
        return None
    if method == 'tools/list':
        return {'jsonrpc': '2.0', 'id': request_id, 'result': {'tools': [dict({'name': name}, **meta) for name, meta in TOOLS.items()]}}
    if method == 'tools/call':
        params = message.get('params') or {}
        name = params.get('name')
        arguments = params.get('arguments') or {}
        try:
            return {'jsonrpc': '2.0', 'id': request_id, 'result': tool_result(dispatch(client, name, arguments))}
        except Exception as exc:
            return {'jsonrpc': '2.0', 'id': request_id, 'error': {'code': -32000, 'message': str(exc)}}
    return {'jsonrpc': '2.0', 'id': request_id, 'error': {'code': -32601, 'message': f'Method not found: {method}'}}


def run_stdio(client: HubSpotClient) -> int:
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            message = json.loads(raw)
        except json.JSONDecodeError as exc:
            response = {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32700, 'message': f'Invalid JSON: {exc}'}}
        else:
            response = handle_message(client, message)
        if response is not None:
            sys.stdout.write(json.dumps(response) + '\n')
            sys.stdout.flush()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Standalone HubSpot CRM MCP scaffold')
    parser.add_argument('--summary', action='store_true', help='Print non-secret server summary and exit')
    args = parser.parse_args(argv)
    client = HubSpotClient()
    if args.summary:
        print(json.dumps({
            'server': 'hubspot-crm-mcp',
            'version': '0.1.0',
            'base_url': client.base_url,
            'tool_count': len(TOOLS),
            'tools': sorted(TOOLS),
        }, indent=2))
        return 0
    return run_stdio(client)


if __name__ == '__main__':
    raise SystemExit(main())
