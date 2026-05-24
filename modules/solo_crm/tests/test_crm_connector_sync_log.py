#!/usr/bin/env python3
"""Tests for CRM connector sync logging and retry queue."""
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


class CRMConnectorSyncLogTests(unittest.TestCase):
    def _setup_crm_and_config(self, td: str):
        from crm_core import SoloCRM

        crm = SoloCRM(Path(td) / "crm.db")
        website = crm.create_website(site_id="ai-solo-company", name="AI Solo Company")
        contact = crm.create_contact("Jian", email="jian@example.com", website_id=website["id"])
        deal = crm.create_deal("Website chatbot - Demo", contact_id=contact["id"], website_id=website["id"])
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
        return crm, contact, deal, activity

    def tearDown(self):
        os.environ.pop("SOLO_CRM_CONNECTORS_CONFIG", None)
        os.environ.pop("SOLO_CRM_SYNC_LOG", None)
        os.environ.pop("HUBSPOT_TEST_TOKEN", None)

    def test_failed_provider_sync_is_logged_without_secret_values(self):
        from connectors.sync import sync_contact_to_enabled_crms
        from connectors.sync_log import list_sync_events

        with tempfile.TemporaryDirectory() as td:
            crm, contact, deal, activity = self._setup_crm_and_config(td)
            with patch("connectors.sync.HubSpotConnector") as hubspot_cls:
                hubspot_cls.return_value.upsert_contact.side_effect = RuntimeError("token secret-token failed")
                result = sync_contact_to_enabled_crms(crm, "ai-solo-company", contact["id"], deal_id=deal["id"], activity_id=activity["id"])

            self.assertFalse(result["ok"])
            events = list_sync_events(site_id="ai-solo-company")
            self.assertEqual(len(events), 1)
            event = events[0]
            self.assertEqual(event["provider"], "hubspot")
            self.assertEqual(event["status"], "failed")
            self.assertTrue(event["retryable"])
            self.assertEqual(event["contact_id"], contact["id"])
            self.assertEqual(event["deal_id"], deal["id"])
            self.assertEqual(event["activity_id"], activity["id"])
            self.assertNotIn("secret-token", json.dumps(events))

    def test_failed_sync_event_can_be_retried_for_same_provider(self):
        from connectors.sync import retry_sync_event, sync_contact_to_enabled_crms
        from connectors.sync_log import get_sync_event, list_sync_events

        with tempfile.TemporaryDirectory() as td:
            crm, contact, deal, activity = self._setup_crm_and_config(td)
            with patch("connectors.sync.HubSpotConnector") as hubspot_cls:
                hubspot_cls.return_value.upsert_contact.side_effect = RuntimeError("provider unavailable")
                sync_contact_to_enabled_crms(crm, "ai-solo-company", contact["id"], deal_id=deal["id"], activity_id=activity["id"])

            failed_event = list_sync_events(status="failed")[0]
            with patch("connectors.sync.HubSpotConnector") as hubspot_cls:
                hubspot_cls.return_value.upsert_contact.return_value = {"provider": "hubspot", "ok": True, "external_contact_id": "hs-123"}
                retry_result = retry_sync_event(crm, failed_event["id"])

            self.assertTrue(retry_result["ok"])
            original = get_sync_event(failed_event["id"])
            self.assertEqual(original["retry_status"], "retried")
            events = list_sync_events(site_id="ai-solo-company")
            self.assertEqual(len(events), 2)
            self.assertEqual(events[0]["status"], "success")
            self.assertEqual(events[0]["retry_of"], failed_event["id"])


if __name__ == "__main__":
    unittest.main()
