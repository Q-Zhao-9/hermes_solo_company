#!/usr/bin/env python3
"""Tests for syncing Solo CRM records to enabled external CRMs."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class CRMConnectorSyncTests(unittest.TestCase):
    def test_sync_contact_to_enabled_crms_uses_site_config_and_never_raises_provider_errors(self):
        from crm_core import SoloCRM
        from connectors.sync import sync_contact_to_enabled_crms

        with tempfile.TemporaryDirectory() as td:
            crm = SoloCRM(Path(td) / "crm.db")
            website = crm.create_website(site_id="ai-solo-company", name="AI Solo Company")
            company = crm.create_company("Easiio", website="https://easiio.com", website_id=website["id"])
            contact = crm.create_contact("Jian", email="jian@example.com", company_id=company["id"], website_id=website["id"])
            deal = crm.create_deal("Website chatbot - Demo", contact_id=contact["id"], company_id=company["id"], website_id=website["id"])
            activity = crm.add_activity(contact_id=contact["id"], deal_id=deal["id"], kind="lead", body="Demo request", website_id=website["id"])

            config_path = Path(td) / "connectors.json"
            config_path.write_text(json.dumps({
                "sites": {
                    "ai-solo-company": {
                        "enabled": True,
                        "providers": {"hubspot": {"enabled": True, "token_env": "HUBSPOT_TEST_TOKEN"}}
                    }
                }
            }), encoding="utf-8")
            os.environ["SOLO_CRM_CONNECTORS_CONFIG"] = str(config_path)
            os.environ["SOLO_CRM_SYNC_LOG"] = str(Path(td) / "sync-log.json")
            os.environ["HUBSPOT_TEST_TOKEN"] = "secret-token"
            try:
                with patch("connectors.sync.HubSpotConnector") as hubspot_cls:
                    instance = hubspot_cls.return_value
                    instance.upsert_contact.side_effect = RuntimeError("HubSpot unavailable and token must not leak secret-token")
                    result = sync_contact_to_enabled_crms(crm, "ai-solo-company", contact["id"], deal_id=deal["id"], activity_id=activity["id"])
                self.assertTrue(result["enabled"])
                self.assertFalse(result["ok"])
                self.assertEqual(result["providers"][0]["provider"], "hubspot")
                self.assertFalse(result["providers"][0]["ok"])
                self.assertNotIn("secret-token", json.dumps(result))
            finally:
                os.environ.pop("SOLO_CRM_CONNECTORS_CONFIG", None)
                os.environ.pop("SOLO_CRM_SYNC_LOG", None)
                os.environ.pop("HUBSPOT_TEST_TOKEN", None)

    def test_sync_contact_to_google_sheets_when_enabled(self):
        from crm_core import SoloCRM
        from connectors.sync import sync_contact_to_enabled_crms

        with tempfile.TemporaryDirectory() as td:
            crm = SoloCRM(Path(td) / "crm.db")
            website = crm.create_website(site_id="ai-solo-company", name="AI Solo Company")
            contact = crm.create_contact("Ada", email="ada@example.com", website_id=website["id"])
            config_path = Path(td) / "connectors.json"
            config_path.write_text(json.dumps({
                "sites": {
                    "ai-solo-company": {
                        "enabled": True,
                        "providers": {"google_sheets": {"enabled": True, "webhook_url_env": "GOOGLE_SHEETS_TEST_WEBHOOK", "sheet_name": "Leads"}}
                    }
                }
            }), encoding="utf-8")
            os.environ["SOLO_CRM_CONNECTORS_CONFIG"] = str(config_path)
            os.environ["SOLO_CRM_SYNC_LOG"] = str(Path(td) / "sync-log.json")
            os.environ["GOOGLE_SHEETS_TEST_WEBHOOK"] = "https://script.google.com/macros/s/secret-webhook/exec"
            try:
                with patch("connectors.sync.GoogleSheetsConnector") as sheets_cls:
                    instance = sheets_cls.return_value
                    instance.upsert_contact.return_value = {"provider": "google_sheets", "ok": True, "external_contact_id": "row-1"}
                    result = sync_contact_to_enabled_crms(crm, "ai-solo-company", contact["id"])
                self.assertTrue(result["enabled"])
                self.assertTrue(result["ok"])
                self.assertEqual(result["providers"][0]["provider"], "google_sheets")
                self.assertEqual(result["providers"][0]["external_contact_id"], "row-1")
                self.assertNotIn("secret-webhook", json.dumps(result))
            finally:
                os.environ.pop("SOLO_CRM_CONNECTORS_CONFIG", None)
                os.environ.pop("SOLO_CRM_SYNC_LOG", None)
                os.environ.pop("GOOGLE_SHEETS_TEST_WEBHOOK", None)

    def test_sync_disabled_site_returns_safe_skipped_status(self):
        from crm_core import SoloCRM
        from connectors.sync import sync_contact_to_enabled_crms

        with tempfile.TemporaryDirectory() as td:
            crm = SoloCRM(Path(td) / "crm.db")
            contact = crm.create_contact("Ada", email="ada@example.com")
            result = sync_contact_to_enabled_crms(crm, "unknown-site", contact["id"])
            self.assertFalse(result["enabled"])
            self.assertEqual(result["providers"], [])


if __name__ == "__main__":
    unittest.main()
