#!/usr/bin/env python3
"""Tests for protected CRM connector configuration."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class CRMConnectorConfigTests(unittest.TestCase):
    def test_load_site_provider_config_resolves_env_token_and_sanitizes_output(self):
        from connectors.config import load_connectors_config, provider_config_for_site, sanitize_connectors_config

        with tempfile.TemporaryDirectory() as td:
            config_path = Path(td) / "connectors.json"
            config_path.write_text(json.dumps({
                "sites": {
                    "ai-solo-company": {
                        "enabled": True,
                        "providers": {
                            "hubspot": {
                                "enabled": True,
                                "mode": "sync_on_lead",
                                "token_env": "HUBSPOT_TEST_PRIVATE_APP_TOKEN",
                                "pipeline_id": "default",
                                "dealstage": "appointmentscheduled",
                                "access_token": "must-not-be-used-or-returned"
                            }
                        }
                    }
                }
            }), encoding="utf-8")
            os.environ["SOLO_CRM_CONNECTORS_CONFIG"] = str(config_path)
            os.environ["HUBSPOT_TEST_PRIVATE_APP_TOKEN"] = "secret-test-token"
            try:
                config = load_connectors_config()
                hubspot = provider_config_for_site(config, "ai-solo-company", "hubspot")
                self.assertTrue(hubspot["enabled"])
                self.assertEqual(hubspot["access_token"], "secret-test-token")
                self.assertEqual(hubspot["pipeline_id"], "default")

                sanitized = sanitize_connectors_config(config)
                provider = sanitized["sites"]["ai-solo-company"]["providers"]["hubspot"]
                self.assertTrue(provider["configured"])
                self.assertEqual(provider["token_env"], "HUBSPOT_TEST_PRIVATE_APP_TOKEN")
                self.assertNotIn("access_token", provider)
                self.assertNotIn("secret-test-token", json.dumps(sanitized))
                self.assertNotIn("must-not-be-used", json.dumps(sanitized))
            finally:
                os.environ.pop("SOLO_CRM_CONNECTORS_CONFIG", None)
                os.environ.pop("HUBSPOT_TEST_PRIVATE_APP_TOKEN", None)

    def test_missing_or_disabled_config_returns_empty_provider(self):
        from connectors.config import provider_config_for_site

        config = {"sites": {"demo": {"enabled": False, "providers": {"hubspot": {"enabled": True}}}}}
        self.assertEqual(provider_config_for_site(config, "demo", "hubspot"), {})
        self.assertEqual(provider_config_for_site(config, "unknown", "hubspot"), {})


if __name__ == "__main__":
    unittest.main()
