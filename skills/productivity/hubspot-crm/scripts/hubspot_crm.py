#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, Iterable, List, Optional, Tuple

DEFAULT_BASE_URL = 'https://api.hubapi.com'


class HubSpotCliError(RuntimeError):
    pass


def require_access_token() -> str:
    token = os.environ.get('HUBSPOT_ACCESS_TOKEN', '').strip()
    if not token:
        raise HubSpotCliError('HUBSPOT_ACCESS_TOKEN is not set.')
    return token


def base_url() -> str:
    return os.environ.get('HUBSPOT_BASE_URL', DEFAULT_BASE_URL).rstrip('/')


def build_headers(token: str) -> Dict[str, str]:
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }


def redact_headers(headers: Dict[str, str]) -> Dict[str, str]:
    safe = dict(headers)
    auth = safe.get('Authorization')
    if auth and auth.startswith('Bearer '):
        safe['Authorization'] = 'Bearer [REDACTED]'
    return safe


def parse_properties(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]


def parse_filters(items: Iterable[str]) -> List[Tuple[str, str]]:
    parsed: List[Tuple[str, str]] = []
    for item in items:
        if '=' not in item:
            raise HubSpotCliError(f'Invalid filter {item!r}; expected property=value.')
        name, value = item.split('=', 1)
        name = name.strip()
        value = value.strip()
        if not name:
            raise HubSpotCliError(f'Invalid filter {item!r}; property name is empty.')
        parsed.append((name, value))
    return parsed


def build_search_payload(
    *,
    query: Optional[str] = None,
    filters: Optional[List[Tuple[str, str]]] = None,
    properties: Optional[List[str]] = None,
    limit: int = 10,
    after: Optional[str] = None,
) -> Dict[str, object]:
    payload: Dict[str, object] = {'limit': limit}
    if query:
        payload['query'] = query
    if properties:
        payload['properties'] = properties
    if filters:
        payload['filterGroups'] = [{
            'filters': [
                {
                    'propertyName': name,
                    'operator': 'EQ',
                    'value': value,
                }
                for name, value in filters
            ]
        }]
    if after:
        payload['after'] = after
    return payload


def build_contact_properties(args: argparse.Namespace) -> Dict[str, str]:
    mapping = {
        'email': args.email,
        'firstname': args.firstname,
        'lastname': args.lastname,
        'phone': args.phone,
        'company': args.company,
        'website': args.website,
        'lifecyclestage': args.lifecyclestage,
        'jobtitle': args.jobtitle,
    }
    return {key: value for key, value in mapping.items() if value not in (None, '')}


def build_url(path: str, query: Optional[Dict[str, str]] = None) -> str:
    normalized = path if path.startswith('/') else f'/{path}'
    url = f'{base_url()}{normalized}'
    if query:
        return f'{url}?{urllib.parse.urlencode(query, doseq=True)}'
    return url


def api_request(method: str, path: str, *, body: Optional[Dict[str, object]] = None, query: Optional[Dict[str, str]] = None) -> object:
    token = require_access_token()
    data = None if body is None else json.dumps(body).encode('utf-8')
    request = urllib.request.Request(
        build_url(path, query),
        data=data,
        headers=build_headers(token),
        method=method.upper(),
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = response.read().decode('utf-8')
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode('utf-8', errors='replace')
        raise HubSpotCliError(f'HTTP {exc.code} for {method.upper()} {path}: {raw}') from exc
    except urllib.error.URLError as exc:
        raise HubSpotCliError(f'Network error for {method.upper()} {path}: {exc.reason}') from exc

    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return {'raw': payload}


def cmd_objects_get(args: argparse.Namespace) -> object:
    query = {}
    properties = parse_properties(args.properties)
    if properties:
        query['properties'] = ','.join(properties)
    return api_request('GET', f'/crm/v3/objects/{args.object_type}/{args.object_id}', query=query or None)


def cmd_objects_search(args: argparse.Namespace) -> object:
    payload = build_search_payload(
        query=args.query,
        filters=parse_filters(args.filter or []),
        properties=parse_properties(args.properties),
        limit=args.limit,
        after=args.after,
    )
    return api_request('POST', f'/crm/v3/objects/{args.object_type}/search', body=payload)


def cmd_contacts_search(args: argparse.Namespace) -> object:
    filters: List[Tuple[str, str]] = []
    if args.email:
        filters.append(('email', args.email))
    payload = build_search_payload(
        query=args.query,
        filters=filters,
        properties=parse_properties(args.properties) or ['email', 'firstname', 'lastname', 'phone', 'company'],
        limit=args.limit,
    )
    return api_request('POST', '/crm/v3/objects/contacts/search', body=payload)


def cmd_companies_search(args: argparse.Namespace) -> object:
    filters: List[Tuple[str, str]] = []
    if args.domain:
        filters.append(('domain', args.domain))
    payload = build_search_payload(
        query=args.query,
        filters=filters,
        properties=parse_properties(args.properties) or ['name', 'domain', 'phone', 'website'],
        limit=args.limit,
    )
    return api_request('POST', '/crm/v3/objects/companies/search', body=payload)


def cmd_contacts_upsert(args: argparse.Namespace) -> object:
    properties = build_contact_properties(args)
    if 'email' not in properties:
        raise HubSpotCliError('--email is required for contact upsert.')
    preview = {
        'operation': 'contact_upsert',
        'search_email': args.email,
        'properties': properties,
    }
    if args.dry_run:
        return {'dry_run': True, 'preview': preview}

    search_payload = build_search_payload(filters=[('email', args.email)], properties=['email'], limit=1)
    search_result = api_request('POST', '/crm/v3/objects/contacts/search', body=search_payload)
    existing = (search_result or {}).get('results', []) if isinstance(search_result, dict) else []
    if existing:
        contact_id = existing[0]['id']
        updated = api_request('PATCH', f'/crm/v3/objects/contacts/{contact_id}', body={'properties': properties})
        return {
            'action': 'updated',
            'contact_id': contact_id,
            'result': updated,
        }
    created = api_request('POST', '/crm/v3/objects/contacts', body={'properties': properties})
    return {
        'action': 'created',
        'result': created,
    }


def cmd_owners_list(args: argparse.Namespace) -> object:
    query = {'limit': str(args.limit)}
    return api_request('GET', '/crm/v3/owners/', query=query)


def cmd_pipelines_list(args: argparse.Namespace) -> object:
    return api_request('GET', f'/crm/v3/pipelines/{args.object_type}')


def cmd_raw(args: argparse.Namespace) -> object:
    body = None
    if args.body_json:
        body = json.loads(args.body_json)
    return api_request(args.method, args.path, body=body)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='HubSpot CRM helper CLI for Hermes skills.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    objects_parser = subparsers.add_parser('objects')
    objects_sub = objects_parser.add_subparsers(dest='objects_command', required=True)

    get_parser = objects_sub.add_parser('get')
    get_parser.add_argument('object_type')
    get_parser.add_argument('object_id')
    get_parser.add_argument('--properties')
    get_parser.set_defaults(handler=cmd_objects_get)

    search_parser = objects_sub.add_parser('search')
    search_parser.add_argument('object_type')
    search_parser.add_argument('--query')
    search_parser.add_argument('--filter', action='append')
    search_parser.add_argument('--properties')
    search_parser.add_argument('--limit', type=int, default=10)
    search_parser.add_argument('--after')
    search_parser.set_defaults(handler=cmd_objects_search)

    contacts_parser = subparsers.add_parser('contacts')
    contacts_sub = contacts_parser.add_subparsers(dest='contacts_command', required=True)

    contacts_search = contacts_sub.add_parser('search')
    contacts_search.add_argument('--email')
    contacts_search.add_argument('--query')
    contacts_search.add_argument('--properties')
    contacts_search.add_argument('--limit', type=int, default=10)
    contacts_search.set_defaults(handler=cmd_contacts_search)

    contacts_upsert = contacts_sub.add_parser('upsert')
    contacts_upsert.add_argument('--email', required=True)
    contacts_upsert.add_argument('--firstname')
    contacts_upsert.add_argument('--lastname')
    contacts_upsert.add_argument('--phone')
    contacts_upsert.add_argument('--company')
    contacts_upsert.add_argument('--website')
    contacts_upsert.add_argument('--lifecyclestage')
    contacts_upsert.add_argument('--jobtitle')
    contacts_upsert.add_argument('--dry-run', action='store_true')
    contacts_upsert.set_defaults(handler=cmd_contacts_upsert)

    companies_parser = subparsers.add_parser('companies')
    companies_sub = companies_parser.add_subparsers(dest='companies_command', required=True)
    companies_search = companies_sub.add_parser('search')
    companies_search.add_argument('--domain')
    companies_search.add_argument('--query')
    companies_search.add_argument('--properties')
    companies_search.add_argument('--limit', type=int, default=10)
    companies_search.set_defaults(handler=cmd_companies_search)

    owners_parser = subparsers.add_parser('owners')
    owners_sub = owners_parser.add_subparsers(dest='owners_command', required=True)
    owners_list = owners_sub.add_parser('list')
    owners_list.add_argument('--limit', type=int, default=100)
    owners_list.set_defaults(handler=cmd_owners_list)

    pipelines_parser = subparsers.add_parser('pipelines')
    pipelines_sub = pipelines_parser.add_subparsers(dest='pipelines_command', required=True)
    pipelines_list = pipelines_sub.add_parser('list')
    pipelines_list.add_argument('object_type')
    pipelines_list.set_defaults(handler=cmd_pipelines_list)

    raw_parser = subparsers.add_parser('raw')
    raw_parser.add_argument('method')
    raw_parser.add_argument('path')
    raw_parser.add_argument('--body-json')
    raw_parser.set_defaults(handler=cmd_raw)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.handler(args)
    except HubSpotCliError as exc:
        print(json.dumps({'error': str(exc)}))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
