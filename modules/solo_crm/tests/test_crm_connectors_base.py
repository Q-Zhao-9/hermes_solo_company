#!/usr/bin/env python3
"""Tests for reusable CRM connector base objects."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class CRMConnectorBaseTests(unittest.TestCase):
    def test_noop_connector_returns_sanitized_disabled_results(self):
        from connectors.base import NoopConnector

        connector = NoopConnector(provider="disabled")
        self.assertEqual(connector.provider, "disabled")
        self.assertEqual(connector.test_connection(), {"provider": "disabled", "ok": True, "disabled": True})
        self.assertEqual(connector.upsert_contact({"email": "lead@example.com"}), {"provider": "disabled", "ok": True, "skipped": True})
        self.assertNotIn("token", str(connector.upsert_contact({"email": "lead@example.com"})).lower())


if __name__ == "__main__":
    unittest.main()
