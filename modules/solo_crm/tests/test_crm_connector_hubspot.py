#!/usr/bin/env python3
"""Tests for HubSpot CRM connector request mapping."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class FakeHTTP:
    def __init__(self):
        self.calls = []

    def __call__(self, method, url, *, headers=None, json_body=None, timeout=15):
        self.calls.append({
            "method": method,
            "url": url,
            "headers": dict(headers or {}),
            "json_body": json_body,
            "timeout": timeout,
        })
        if url.endswith("/crm/v3/objects/contacts/search"):
            return {"total": 0, "results": []}
        if url.endswith("/crm/v3/objects/contacts"):
            return {"id": "hubspot-contact-1", "properties": json_body.get("properties", {})}
        if url.endswith("/crm/v3/objects/companies"):
            return {"id": "hubspot-company-1", "properties": json_body.get("properties", {})}
        if url.endswith("/crm/v3/objects/deals"):
            return {"id": "hubspot-deal-1", "properties": json_body.get("properties", {})}
        if url.endswith("/crm/v3/objects/notes"):
            return {"id": "hubspot-note-1", "properties": json_body.get("properties", {})}
        return {"ok": True}


class HubSpotConnectorTests(unittest.TestCase):
    def test_upsert_contact_searches_by_email_then_creates_with_safe_properties(self):
        from connectors.hubspot import HubSpotConnector

        fake = FakeHTTP()
        connector = HubSpotConnector({"access_token": "secret-token"}, http_client=fake)
        result = connector.upsert_contact(
            {"id": 7, "name": "Ada Lovelace", "email": "ada@example.com", "phone": "555-123-4567", "role": "Founder", "source": "website_chatbot", "tags": ["lead", "ai"]},
            company={"name": "Analytical Engines", "website": "https://example.com"},
            website={"site_id": "ai-solo-company"},
            visitor={"visitor_key": "visitor-123"},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["provider"], "hubspot")
        self.assertEqual(result["external_contact_id"], "hubspot-contact-1")
        self.assertNotIn("secret-token", json.dumps(result))
        self.assertEqual(fake.calls[0]["method"], "POST")
        self.assertTrue(fake.calls[0]["url"].endswith("/crm/v3/objects/contacts/search"))
        create = fake.calls[1]
        self.assertTrue(create["url"].endswith("/crm/v3/objects/contacts"))
        props = create["json_body"]["properties"]
        self.assertEqual(props["email"], "ada@example.com")
        self.assertEqual(props["firstname"], "Ada")
        self.assertEqual(props["lastname"], "Lovelace")
        self.assertEqual(props["phone"], "555-123-4567")
        self.assertEqual(props["jobtitle"], "Founder")
        self.assertEqual(props["company"], "Analytical Engines")
        self.assertEqual(props["website"], "https://example.com")
        self.assertEqual(props["easiio_site_id"], "ai-solo-company")
        self.assertEqual(props["easiio_visitor_key"], "visitor-123")
        self.assertNotIn("secret-token", json.dumps(create["json_body"]))
        self.assertTrue(create["headers"]["Authorization"].startswith("Bearer "))

    def test_create_deal_and_activity_use_configured_pipeline_stage(self):
        from connectors.hubspot import HubSpotConnector

        fake = FakeHTTP()
        connector = HubSpotConnector({"access_token": "secret-token", "pipeline_id": "sales", "dealstage": "qualified"}, http_client=fake)
        deal_result = connector.upsert_deal({"title": "Website chatbot - Demo", "value": 2500, "currency": "USD", "stage": "new"})
        note_result = connector.add_activity({"kind": "lead", "body": "Lead asked for demo", "happened_at": "2026-05-23T00:00:00+00:00"})

        self.assertEqual(deal_result["external_deal_id"], "hubspot-deal-1")
        self.assertEqual(note_result["external_activity_id"], "hubspot-note-1")
        deal_props = next(call["json_body"]["properties"] for call in fake.calls if call["url"].endswith("/crm/v3/objects/deals"))
        self.assertEqual(deal_props["dealname"], "Website chatbot - Demo")
        self.assertEqual(deal_props["amount"], "2500")
        self.assertEqual(deal_props["pipeline"], "sales")
        self.assertEqual(deal_props["dealstage"], "qualified")
        note_props = next(call["json_body"]["properties"] for call in fake.calls if call["url"].endswith("/crm/v3/objects/notes"))
        self.assertIn("Lead asked for demo", note_props["hs_note_body"])


if __name__ == "__main__":
    unittest.main()
