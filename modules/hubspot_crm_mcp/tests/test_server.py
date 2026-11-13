import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / 'server.py'


class ServerSmokeTests(unittest.TestCase):
    def test_initialize_and_list_tools(self):
        env = dict(os.environ)
        env['HUBSPOT_ACCESS_TOKEN'] = '***'
        input_text = '\n'.join([
            json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {}}),
            json.dumps({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}}),
        ]) + '\n'
        result = subprocess.run(
            [sys.executable, str(SERVER)],
            input=input_text,
            capture_output=True,
            text=True,
            env=env,
            timeout=5,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(result.stderr, '')
        responses = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
        self.assertEqual(responses[0]['result']['serverInfo']['name'], 'hubspot-crm-mcp')
        tool_names = [tool['name'] for tool in responses[1]['result']['tools']]
        self.assertIn('hubspot_auth_check', tool_names)
        self.assertIn('hubspot_upsert_contact', tool_names)


if __name__ == '__main__':
    unittest.main()
