"""Core HubSpot CRM helper logic for a standalone MCP server scaffold."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

DEFAULT_BASE_URL = "https://api.hubapi.com"


class HubSpotError(RuntimeError):
    pass


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


class HubSpotClient:
    def __init__(self, access_token: str | None = None, base_url: str | None = None, timeout: float = 30.0):
        self.access_token = _clean(access_token or os.environ.get('HUBSPOT_ACCESS_TOKEN'))
        self.base_url = _clean(base_url or os.environ.get('HUBSPOT_BASE_URL')) or DEFAULT_BASE_URL
        self.timeout = float(timeout)

    def _headers(self) -> dict[str, str]:
        if not self.access_token:
            raise HubSpotError('HUBSPOT_ACCESS_TOKEN is not set.')
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def request(self, method: str, path: str, *, body: dict[str, Any] | None = None,
                query: dict[str, Any] | None = None) -> dict[str, Any]:
        normalized = path if path.startswith('/') else f'/{path}'
        url = self.base_url.rstrip('/') + normalized
        if query:
            url += '?' + urllib.parse.urlencode(query, doseq=True)
        payload = None if body is None else json.dumps(body).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers=self._headers(), method=method.upper())
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:  # noqa: S310
                raw = response.read().decode('utf-8')
        except urllib.error.HTTPError as exc:
            body_text = exc.read().decode('utf-8', errors='replace')
            raise HubSpotError(f'HTTP {exc.code} for {method.upper()} {normalized}: {body_text[:500]}') from exc
        except urllib.error.URLError as exc:
            raise HubSpotError(f'Network error for {method.upper()} {normalized}: {exc.reason}') from exc
        return json.loads(raw) if raw else {}

    def auth_check(self) -> dict[str, Any]:
        owners = self.list_owners(limit=1)
        return {'ok': True, 'base_url': self.base_url, 'owners_count_sample': len(owners.get('results', []))}

    def list_owners(self, limit: int = 100) -> dict[str, Any]:
        return self.request('GET', '/crm/v3/owners/', query={'limit': int(limit)})

    def list_pipelines(self, object_type: str) -> dict[str, Any]:
        return self.request('GET', f'/crm/v3/pipelines/{object_type}')

    def search_objects(self, object_type: str, *, query: str | None = None,
                       filters: list[tuple[str, str]] | None = None,
                       properties: list[str] | None = None,
                       limit: int = 10) -> dict[str, Any]:
        payload: dict[str, Any] = {'limit': int(limit)}
        if query:
            payload['query'] = query
        if properties:
            payload['properties'] = properties
        if filters:
            payload['filterGroups'] = [{
                'filters': [
                    {'propertyName': name, 'operator': 'EQ', 'value': value}
                    for name, value in filters
                ]
            }]
        return self.request('POST', f'/crm/v3/objects/{object_type}/search', body=payload)

    def get_object(self, object_type: str, object_id: str, properties: list[str] | None = None) -> dict[str, Any]:
        query = {'properties': ','.join(properties)} if properties else None
        return self.request('GET', f'/crm/v3/objects/{object_type}/{object_id}', query=query)

    def upsert_contact(self, *, email: str, firstname: str | None = None, lastname: str | None = None,
                       phone: str | None = None, company: str | None = None, website: str | None = None,
                       lifecyclestage: str | None = None, jobtitle: str | None = None,
                       dry_run: bool = False) -> dict[str, Any]:
        email = _clean(email)
        if not email:
            raise HubSpotError('email is required')
        properties = {
            'email': email,
            'firstname': _clean(firstname),
            'lastname': _clean(lastname),
            'phone': _clean(phone),
            'company': _clean(company),
            'website': _clean(website),
            'lifecyclestage': _clean(lifecyclestage),
            'jobtitle': _clean(jobtitle),
        }
        properties = {k: v for k, v in properties.items() if v}
        preview = {'search_email': email, 'properties': properties}
        if dry_run:
            return {'dry_run': True, 'preview': preview}
        found = self.search_objects('contacts', filters=[('email', email)], properties=['email'], limit=1)
        results = found.get('results', []) if isinstance(found, dict) else []
        if results:
            contact_id = _clean(results[0].get('id'))
            updated = self.request('PATCH', f'/crm/v3/objects/contacts/{contact_id}', body={'properties': properties})
            return {'action': 'updated', 'contact_id': contact_id, 'result': updated}
        created = self.request('POST', '/crm/v3/objects/contacts', body={'properties': properties})
        return {'action': 'created', 'result': created}


def parse_filter_pairs(filter_strings: list[str] | None) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for raw in filter_strings or []:
        if '=' not in raw:
            raise HubSpotError(f'Invalid filter {raw!r}; expected property=value.')
        name, value = raw.split('=', 1)
        name = _clean(name)
        value = _clean(value)
        if not name:
            raise HubSpotError(f'Invalid filter {raw!r}; property name is empty.')
        items.append((name, value))
    return items
