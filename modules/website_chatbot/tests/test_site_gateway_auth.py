#!/usr/bin/env python3
"""Tests for the AI Solo Company site gateway login/download backend."""
from __future__ import annotations

import http.client
import importlib.util
import json
import tempfile
import threading
import unittest
from http.cookies import SimpleCookie
from pathlib import Path

GATEWAY_PATH = Path(__file__).resolve().parents[1] / 'backend' / 'site_gateway.py'
spec = importlib.util.spec_from_file_location('site_gateway', GATEWAY_PATH)
site_gateway = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(site_gateway)


class GatewayAuthTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.site_dir = self.root / 'site'
        self.site_dir.mkdir()
        (self.site_dir / 'index.html').write_text('hello', encoding='utf-8')
        self.db_path = self.root / 'site.db'
        self.upload_dir = self.root / 'uploads'
        site_gateway.GatewayHandler.api_base = 'http://127.0.0.1:9'
        site_gateway.GatewayHandler.auth_db_path = self.db_path
        site_gateway.GatewayHandler.upload_dir = self.upload_dir
        site_gateway.GatewayHandler.admin_email = 'jian.lin@easiio.com'
        site_gateway.GatewayHandler.admin_password = 'test-password-123'
        site_gateway.initialize_auth_backend(self.db_path, self.upload_dir, 'jian.lin@easiio.com', 'test-password-123')
        handler = lambda *a, **kw: site_gateway.GatewayHandler(*a, directory=str(self.site_dir), **kw)
        self.httpd = site_gateway.ReusableThreadingTCPServer(('127.0.0.1', 0), handler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.tmp.cleanup()

    def request(self, method, path, body=None, headers=None):
        headers = dict(headers or {})
        if isinstance(body, dict):
            body = json.dumps(body).encode('utf-8')
            headers.setdefault('Content-Type', 'application/json')
        conn = http.client.HTTPConnection('127.0.0.1', self.port, timeout=10)
        conn.request(method, path, body=body, headers=headers)
        resp = conn.getresponse()
        data = resp.read()
        conn.close()
        return resp.status, dict(resp.getheaders()), data

    def login_cookie(self):
        status, headers, data = self.request('POST', '/auth/login', {'email': 'jian.lin@easiio.com', 'password': 'test-password-123'})
        self.assertEqual(status, 200, data)
        cookie = SimpleCookie(headers['Set-Cookie'])
        return f"ai_solo_session={cookie['ai_solo_session'].value}"

    def test_seeds_admin_and_login_sets_secure_session_cookie(self):
        status, headers, data = self.request('POST', '/auth/login', {'email': 'jian.lin@easiio.com', 'password': 'test-password-123'})
        self.assertEqual(status, 200, data)
        payload = json.loads(data)
        self.assertEqual(payload['user']['email'], 'jian.lin@easiio.com')
        self.assertEqual(payload['user']['role'], 'admin')
        self.assertIn('HttpOnly', headers['Set-Cookie'])
        self.assertIn('SameSite=Lax', headers['Set-Cookie'])

    def test_invalid_login_is_rejected(self):
        status, _headers, data = self.request('POST', '/auth/login', {'email': 'jian.lin@easiio.com', 'password': 'wrong'})
        self.assertEqual(status, 401, data)

    def test_upload_requires_login_and_authenticated_admin_can_upload_and_list_download(self):
        boundary = '----HermesBoundary'
        body = (
            f'--{boundary}\r\n'
            'Content-Disposition: form-data; name="file"; filename="lesson.pdf"\r\n'
            'Content-Type: application/pdf\r\n\r\n'
            'PDF bytes from Hermes agent\r\n'
            f'--{boundary}--\r\n'
        ).encode('utf-8')
        headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}
        status, _headers, data = self.request('POST', '/admin/upload', body, headers)
        self.assertEqual(status, 401, data)

        cookie = self.login_cookie()
        headers['Cookie'] = cookie
        status, _headers, data = self.request('POST', '/admin/upload', body, headers)
        self.assertEqual(status, 201, data)
        uploaded = json.loads(data)['file']
        self.assertEqual(uploaded['original_name'], 'lesson.pdf')

        status, _headers, data = self.request('GET', '/api/downloads', headers={'Cookie': cookie})
        self.assertEqual(status, 200, data)
        files = json.loads(data)['files']
        self.assertEqual(files[0]['original_name'], 'lesson.pdf')
        download_path = files[0]['download_url']
        status, headers, data = self.request('GET', download_path, headers={'Cookie': cookie})
        self.assertEqual(status, 200)
        self.assertEqual(data, b'PDF bytes from Hermes agent')
        self.assertIn('attachment; filename="lesson.pdf"', headers['Content-Disposition'])


if __name__ == '__main__':
    unittest.main()
