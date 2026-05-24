import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class SoloCRMTests(unittest.TestCase):
    def test_contact_deal_activity_workflow(self):
        from crm_core import SoloCRM

        with tempfile.TemporaryDirectory() as td:
            crm = SoloCRM(Path(td) / "crm.db")
            company = crm.create_company(name="Easiio", website="https://www.easiio.com")
            contact = crm.create_contact(
                name="Jian",
                email="jian@example.com",
                company_id=company["id"],
                tags=["founder", "ai-solo-company"],
                notes="Interested in Hermes CRM",
            )
            deal = crm.create_deal(
                title="AI Solo Company CRM",
                contact_id=contact["id"],
                company_id=company["id"],
                value=5000,
                stage="qualified",
            )
            activity = crm.add_activity(
                contact_id=contact["id"],
                deal_id=deal["id"],
                kind="note",
                body="Discuss MCP-powered CRM workflow",
                follow_up_at="2030-01-02",
            )

            self.assertGreater(contact["id"], 0)
            self.assertEqual(crm.get_contact(contact["id"])["email"], "jian@example.com")
            self.assertEqual(crm.search_contacts(query="Hermes")[0]["id"], contact["id"])
            self.assertEqual(crm.list_deals(stage="qualified")[0]["id"], deal["id"])
            self.assertEqual(crm.list_activities(contact_id=contact["id"])[0]["id"], activity["id"])
            self.assertEqual(crm.next_followups(limit=5)[0]["contact_name"], "Jian")
            self.assertEqual(crm.summary()["open_deals"], 1)

    def test_mcp_stdio_lists_and_calls_tools(self):
        server = ROOT / "server.py"
        with tempfile.TemporaryDirectory() as td:
            env = os.environ.copy()
            env["SOLO_CRM_DB"] = str(Path(td) / "crm.db")
            proc = subprocess.Popen(
                [sys.executable, str(server)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )
            try:
                requests = [
                    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}}},
                    {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
                    {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "crm_create_contact", "arguments": {"name": "Ada Lovelace", "email": "ada@example.com", "tags": ["lead"]}}},
                    {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "crm_search_contacts", "arguments": {"query": "Ada"}}},
                ]
                for req in requests:
                    proc.stdin.write(json.dumps(req) + "\n")
                    proc.stdin.flush()

                responses = [json.loads(proc.stdout.readline()) for _ in requests]
            finally:
                if proc.stdin:
                    proc.stdin.close()
                if proc.stdout:
                    proc.stdout.close()
                if proc.stderr:
                    proc.stderr.close()
                proc.terminate()
                proc.wait(timeout=5)

        self.assertEqual(responses[0]["result"]["serverInfo"]["name"], "solo-crm")
        tool_names = {tool["name"] for tool in responses[1]["result"]["tools"]}
        self.assertIn("crm_create_contact", tool_names)
        self.assertIn("crm_search_contacts", tool_names)
        created_payload = json.loads(responses[2]["result"]["content"][0]["text"])
        self.assertEqual(created_payload["email"], "ada@example.com")
        search_payload = json.loads(responses[3]["result"]["content"][0]["text"])
        self.assertEqual(search_payload[0]["name"], "Ada Lovelace")


if __name__ == "__main__":
    unittest.main()
