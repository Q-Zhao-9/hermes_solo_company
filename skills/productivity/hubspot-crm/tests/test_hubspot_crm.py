import pathlib
import sys
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / 'scripts'))

import hubspot_crm  # noqa: E402


class HubSpotCliTests(unittest.TestCase):
    def test_parse_filters(self):
        self.assertEqual(
            hubspot_crm.parse_filters(['email=person@example.com', 'lifecyclestage=lead']),
            [('email', 'person@example.com'), ('lifecyclestage', 'lead')],
        )

    def test_build_search_payload(self):
        payload = hubspot_crm.build_search_payload(
            query='Acme',
            filters=[('pipeline', 'default')],
            properties=['dealname', 'dealstage'],
            limit=5,
        )
        self.assertEqual(payload['query'], 'Acme')
        self.assertEqual(payload['limit'], 5)
        self.assertEqual(payload['properties'], ['dealname', 'dealstage'])
        self.assertEqual(payload['filterGroups'][0]['filters'][0]['propertyName'], 'pipeline')

    def test_build_contact_properties(self):
        class Args:
            email = 'person@example.com'
            firstname = 'Alice'
            lastname = ''
            phone = None
            company = 'Acme'
            website = 'https://example.com'
            lifecyclestage = 'lead'
            jobtitle = 'Founder'

        properties = hubspot_crm.build_contact_properties(Args())
        self.assertEqual(properties['email'], 'person@example.com')
        self.assertEqual(properties['firstname'], 'Alice')
        self.assertEqual(properties['company'], 'Acme')
        self.assertNotIn('lastname', properties)
        self.assertNotIn('phone', properties)

    def test_redact_headers(self):
        headers = hubspot_crm.build_headers('super-secret-token')
        safe = hubspot_crm.redact_headers(headers)
        self.assertEqual(safe['Authorization'], 'Bearer [REDACTED]')
        self.assertEqual(safe['Content-Type'], 'application/json')

    def test_build_url_uses_default_base(self):
        original = hubspot_crm.os.environ.pop('HUBSPOT_BASE_URL', None)
        try:
            url = hubspot_crm.build_url('/crm/v3/owners/')
        finally:
            if original is not None:
                hubspot_crm.os.environ['HUBSPOT_BASE_URL'] = original
        self.assertEqual(url, 'https://api.hubapi.com/crm/v3/owners/')


if __name__ == '__main__':
    unittest.main()
