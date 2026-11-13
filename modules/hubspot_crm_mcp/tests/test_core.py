import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core import HubSpotClient, HubSpotError, parse_filter_pairs


class FakeClient(HubSpotClient):
    def __init__(self):
        super().__init__(access_token='***')
        self.calls = []

    def request(self, method, path, *, body=None, query=None):
        self.calls.append({'method': method, 'path': path, 'body': body, 'query': query})
        if path == '/crm/v3/owners/':
            return {'results': [{'id': '1'}]}
        if path == '/crm/v3/objects/contacts/search':
            return {'results': []}
        if path == '/crm/v3/objects/contacts':
            return {'id': 'contact-1'}
        return {'ok': True}


class CoreTests(unittest.TestCase):
    def test_parse_filter_pairs(self):
        self.assertEqual(parse_filter_pairs(['email=a@example.com', 'pipeline=default']), [('email', 'a@example.com'), ('pipeline', 'default')])

    def test_parse_filter_pairs_rejects_invalid(self):
        with self.assertRaises(HubSpotError):
            parse_filter_pairs(['broken-filter'])

    def test_auth_check_uses_owners_call(self):
        client = FakeClient()
        result = client.auth_check()
        self.assertTrue(result['ok'])
        self.assertEqual(client.calls[0]['path'], '/crm/v3/owners/')

    def test_upsert_contact_creates_when_missing(self):
        client = FakeClient()
        result = client.upsert_contact(email='ada@example.com', firstname='Ada', company='Analytical Engines')
        self.assertEqual(result['action'], 'created')
        self.assertEqual(client.calls[0]['path'], '/crm/v3/objects/contacts/search')
        self.assertEqual(client.calls[1]['path'], '/crm/v3/objects/contacts')
        self.assertEqual(client.calls[1]['body']['properties']['firstname'], 'Ada')

    def test_upsert_contact_dry_run(self):
        client = FakeClient()
        result = client.upsert_contact(email='ada@example.com', firstname='Ada', dry_run=True)
        self.assertTrue(result['dry_run'])
        self.assertEqual(client.calls, [])


if __name__ == '__main__':
    unittest.main()
