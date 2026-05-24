#!/usr/bin/env python3
"""Tests for Google Sheets CRM connector request mapping."""
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
        return {"ok": True, "row_id": f"row-{len(self.calls)}"}


class GoogleSheetsConnectorTests(unittest.TestCase):
    def test_upsert_contact_posts_safe_lead_row_to_apps_script_webhook(self):
        from connectors.google_sheets import GoogleSheetsConnector

        fake = FakeHTTP()
        connector = GoogleSheetsConnector({
            "webhook_url": "https://script.google.com/macros/s/example/exec",
            "sheet_name": "Leads",
            "spreadsheet_id": "spreadsheet-public-id",
        }, http_client=fake)
        result = connector.upsert_contact(
            {"id": 7, "name": "Ada Lovelace", "email": "ada@example.com", "phone": "555-123-4567", "role": "Founder", "status": "lead", "source": "website_chatbot", "tags": ["lead", "ai"]},
            company={"name": "Analytical Engines", "website": "https://example.com"},
            website={"site_id": "ai-solo-company", "domain": "example.com"},
            visitor={"visitor_key": "visitor-123"},
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["provider"], "google_sheets")
        self.assertEqual(result["external_contact_id"], "row-1")
        self.assertNotIn("script.google.com", json.dumps(result))
        self.assertEqual(fake.calls[0]["method"], "POST")
        self.assertEqual(fake.calls[0]["url"], "https://script.google.com/macros/s/example/exec")
        self.assertEqual(fake.calls[0]["headers"]["Content-Type"], "application/json")
        body = fake.calls[0]["json_body"]
        self.assertEqual(body["sheet_name"], "Leads")
        self.assertEqual(body["spreadsheet_id"], "spreadsheet-public-id")
        self.assertEqual(body["record_type"], "contact")
        row = body["row"]
        self.assertEqual(row["name"], "Ada Lovelace")
        self.assertEqual(row["email"], "ada@example.com")
        self.assertEqual(row["company"], "Analytical Engines")
        self.assertEqual(row["site_id"], "ai-solo-company")
        self.assertEqual(row["visitor_key"], "visitor-123")
        self.assertEqual(row["tags"], "lead, ai")
        self.assertNotIn("webhook_url", row)

    def test_deal_and_activity_append_rows_with_record_type(self):
        from connectors.google_sheets import GoogleSheetsConnector

        fake = FakeHTTP()
        connector = GoogleSheetsConnector({"webhook_url": "https://script.google.com/macros/s/example/exec"}, http_client=fake)
        deal_result = connector.upsert_deal({"id": 22, "title": "Website chatbot - Demo", "value": 2500, "currency": "USD", "stage": "new"})
        activity_result = connector.add_activity({"id": 33, "kind": "lead", "body": "Lead asked for demo"})

        self.assertEqual(deal_result["external_deal_id"], "row-1")
        self.assertEqual(activity_result["external_activity_id"], "row-2")
        self.assertEqual(fake.calls[0]["json_body"]["record_type"], "deal")
        self.assertEqual(fake.calls[0]["json_body"]["row"]["deal_title"], "Website chatbot - Demo")
        self.assertEqual(fake.calls[1]["json_body"]["record_type"], "activity")
        self.assertIn("Lead asked for demo", fake.calls[1]["json_body"]["row"]["activity_body"])

    def test_missing_webhook_url_is_reported_without_leaking_config(self):
        from connectors.google_sheets import GoogleSheetsConnector

        connector = GoogleSheetsConnector({"webhook_url": ""})
        with self.assertRaises(RuntimeError) as ctx:
            connector.upsert_contact({"name": "Ada", "email": "ada@example.com"})
        self.assertEqual(str(ctx.exception), "google_sheets_not_configured")


if __name__ == "__main__":
    unittest.main()
