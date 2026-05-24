#!/usr/bin/env python3
"""Tiny local gateway: serves a static site, auth/download APIs, and proxies chatbot API calls.

Used for Hermes Proxy previews where the public URL can expose only one local
HTTP target. Static files are served from --site-dir, /api/chat/* and /health
are forwarded to the chatbot backend on --api-base, and lightweight SQLite auth
+ downloads are handled locally for the AI Solo Company site.
"""
from __future__ import annotations

import argparse
import cgi
import hashlib
import hmac
import http.cookies
import http.server
import json
import mimetypes
import os
import secrets
import shutil
import socketserver
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from urllib.parse import parse_qs, urljoin

SOLO_CRM_ROOT = Path(__file__).resolve().parents[2] / "solo_crm"
if str(SOLO_CRM_ROOT) not in sys.path:
    sys.path.insert(0, str(SOLO_CRM_ROOT))

from crm_core import SoloCRM  # noqa: E402

SESSION_COOKIE = "ai_solo_session"
SESSION_TTL_SECONDS = 60 * 60 * 24 * 7
MAX_UPLOAD_BYTES = 100 * 1024 * 1024


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return f"pbkdf2_sha256$200000${salt.hex()}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations))
        return hmac.compare_digest(digest.hex(), digest_hex)
    except Exception:
        return False


def db_connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def initialize_auth_backend(db_path: Path, upload_dir: Path, admin_email: str, admin_password: str) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    upload_dir.mkdir(parents=True, exist_ok=True)
    with db_connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              email TEXT NOT NULL UNIQUE,
              password_hash TEXT NOT NULL,
              role TEXT NOT NULL DEFAULT 'user',
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS sessions (
              token TEXT PRIMARY KEY,
              user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
              created_at INTEGER NOT NULL,
              expires_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS downloads (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              original_name TEXT NOT NULL,
              stored_name TEXT NOT NULL UNIQUE,
              content_type TEXT,
              size INTEGER NOT NULL,
              uploaded_by INTEGER REFERENCES users(id),
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        download_cols = {row[1] for row in conn.execute("PRAGMA table_info(downloads)").fetchall()}
        for col_name, ddl in [
            ("source", "ALTER TABLE downloads ADD COLUMN source TEXT NOT NULL DEFAULT 'local'"),
            ("external_url", "ALTER TABLE downloads ADD COLUMN external_url TEXT"),
            ("drive_file_id", "ALTER TABLE downloads ADD COLUMN drive_file_id TEXT"),
            ("description", "ALTER TABLE downloads ADD COLUMN description TEXT"),
        ]:
            if col_name not in download_cols:
                conn.execute(ddl)
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (admin_email.lower(),)).fetchone()
        password_hash = hash_password(admin_password)
        if existing:
            if os.environ.get("AI_SOLO_RESET_ADMIN_PASSWORD") == "1":
                conn.execute(
                    "UPDATE users SET password_hash = ?, role = 'admin', updated_at = CURRENT_TIMESTAMP WHERE email = ?",
                    (password_hash, admin_email.lower()),
                )
            else:
                conn.execute(
                    "UPDATE users SET role = 'admin', updated_at = CURRENT_TIMESTAMP WHERE email = ?",
                    (admin_email.lower(),),
                )
        else:
            conn.execute(
                "INSERT INTO users (email, password_hash, role) VALUES (?, ?, 'admin')",
                (admin_email.lower(), password_hash),
            )
        conn.commit()


class ReusableThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


class GatewayHandler(http.server.SimpleHTTPRequestHandler):
    api_base = "http://127.0.0.1:8099"
    wiki_api_base = "http://127.0.0.1:8105"
    auth_db_path = Path("/home/jianl/.hermes/tools/website_chatbot/data/ai_solo_site.db")
    upload_dir = Path("/home/jianl/.hermes/tools/website_chatbot/data/ai_solo_downloads")
    crm_db_path = Path("/home/jianl/.hermes/tools/solo_crm/solo_crm.db")
    admin_email = "jian.lin@easiio.com"
    admin_password = ""

    def _send_json(self, status: int, payload: dict, headers: dict[str, str] | None = None) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or "0")
        if not length:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _current_user(self) -> dict | None:
        cookie_header = self.headers.get("Cookie", "")
        cookies = http.cookies.SimpleCookie(cookie_header)
        morsel = cookies.get(SESSION_COOKIE)
        if not morsel:
            return None
        now = int(time.time())
        with db_connect(self.auth_db_path) as conn:
            row = conn.execute(
                """
                SELECT users.id, users.email, users.role
                FROM sessions
                JOIN users ON users.id = sessions.user_id
                WHERE sessions.token = ? AND sessions.expires_at > ?
                """,
                (morsel.value, now),
            ).fetchone()
        return dict(row) if row else None

    def _require_logged_in(self) -> dict | None:
        user = self._current_user()
        if not user:
            self._send_json(401, {"ok": False, "error": "login_required"})
            return None
        return user

    def _require_admin(self) -> dict | None:
        user = self._current_user()
        if not user or user.get("role") != "admin":
            self._send_json(401, {"ok": False, "error": "login_required"})
            return None
        return user

    def _redirect_to_login(self, next_page: str) -> None:
        self.send_response(302)
        self.send_header("Location", f"login.html?next={urllib.parse.quote(next_page)}")
        self.end_headers()

    def _handle_login(self) -> None:
        try:
            payload = self._read_json()
        except Exception:
            self._send_json(400, {"ok": False, "error": "invalid_json"})
            return
        email = str(payload.get("email") or "").strip().lower()
        password = str(payload.get("password") or "")
        with db_connect(self.auth_db_path) as conn:
            user = conn.execute("SELECT id, email, role, password_hash FROM users WHERE email = ?", (email,)).fetchone()
            if not user or not verify_password(password, user["password_hash"]):
                self._send_json(401, {"ok": False, "error": "invalid_credentials"})
                return
            token = secrets.token_urlsafe(32)
            now = int(time.time())
            conn.execute(
                "INSERT INTO sessions (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
                (token, user["id"], now, now + SESSION_TTL_SECONDS),
            )
            conn.commit()
        cookie = http.cookies.SimpleCookie()
        cookie[SESSION_COOKIE] = token
        cookie[SESSION_COOKIE]["path"] = "/"
        cookie[SESSION_COOKIE]["httponly"] = True
        cookie[SESSION_COOKIE]["samesite"] = "Lax"
        self._send_json(
            200,
            {"ok": True, "user": {"email": user["email"], "role": user["role"]}},
            {"Set-Cookie": cookie.output(header="").strip()},
        )

    def _handle_change_password(self) -> None:
        user = self._require_logged_in()
        if not user:
            return
        try:
            payload = self._read_json()
        except Exception:
            self._send_json(400, {"ok": False, "error": "invalid_json"})
            return
        current_password = str(payload.get("current_password") or "")
        new_password = str(payload.get("new_password") or "")
        confirm_password = str(payload.get("confirm_password") or "")
        if len(new_password) < 8:
            self._send_json(400, {"ok": False, "error": "password_too_short"})
            return
        if new_password != confirm_password:
            self._send_json(400, {"ok": False, "error": "password_mismatch"})
            return
        with db_connect(self.auth_db_path) as conn:
            row = conn.execute("SELECT id, password_hash FROM users WHERE id = ?", (user["id"],)).fetchone()
            if not row or not verify_password(current_password, row["password_hash"]):
                self._send_json(401, {"ok": False, "error": "invalid_current_password"})
                return
            conn.execute(
                "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (hash_password(new_password), user["id"]),
            )
            conn.commit()
        self._send_json(200, {"ok": True, "user": {"email": user["email"], "role": user["role"]}})

    def _handle_logout(self) -> None:
        cookie_header = self.headers.get("Cookie", "")
        cookies = http.cookies.SimpleCookie(cookie_header)
        token = cookies.get(SESSION_COOKIE)
        if token:
            with db_connect(self.auth_db_path) as conn:
                conn.execute("DELETE FROM sessions WHERE token = ?", (token.value,))
                conn.commit()
        self._send_json(200, {"ok": True}, {"Set-Cookie": f"{SESSION_COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax"})

    def _handle_me(self) -> None:
        user = self._current_user()
        if not user:
            self._send_json(401, {"ok": False, "error": "login_required"})
            return
        self._send_json(200, {"ok": True, "user": {"email": user["email"], "role": user["role"]}})

    @staticmethod
    def _safe_download_name(name: str) -> str:
        base = Path(name).name.strip().replace("\x00", "")
        safe = "".join(ch if ch.isalnum() or ch in {".", "-", "_", " ", "(" , ")"} else "_" for ch in base)
        return safe[:160] or "download.bin"

    def _file_rows(self) -> list[dict]:
        with db_connect(self.auth_db_path) as conn:
            rows = conn.execute(
                """
                SELECT downloads.id, downloads.original_name, downloads.stored_name, downloads.content_type, downloads.size,
                       downloads.created_at, COALESCE(downloads.source, 'local') AS source, downloads.external_url,
                       downloads.drive_file_id, downloads.description, users.email AS uploaded_by_email
                FROM downloads
                LEFT JOIN users ON users.id = downloads.uploaded_by
                ORDER BY downloads.id DESC
                """
            ).fetchall()
        files = []
        for row in rows:
            source = row["source"] or "local"
            external_url = row["external_url"]
            files.append(
                {
                    "id": row["id"],
                    "original_name": row["original_name"],
                    "content_type": row["content_type"],
                    "size": row["size"],
                    "created_at": row["created_at"],
                    "source": source,
                    "description": row["description"],
                    "uploaded_by_email": row["uploaded_by_email"],
                    "drive_file_id": row["drive_file_id"],
                    "download_url": external_url if source == "google_drive" and external_url else f"/download/{urllib.parse.quote(row['stored_name'])}",
                }
            )
        return files

    def _handle_downloads(self) -> None:
        if not self._require_logged_in():
            return
        self._send_json(200, {"ok": True, "files": self._file_rows()})

    def _handle_file_upload(self, user: dict, source: str = "local", default_description: str | None = None) -> None:
        length = int(self.headers.get("Content-Length") or "0")
        if length <= 0 or length > MAX_UPLOAD_BYTES:
            self._send_json(413, {"ok": False, "error": "file_too_large"})
            return
        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self._send_json(400, {"ok": False, "error": "multipart_required"})
            return
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": content_type})
        file_item = form["file"] if "file" in form else None
        if file_item is None or not getattr(file_item, "filename", None):
            self._send_json(400, {"ok": False, "error": "missing_file"})
            return
        original_name = self._safe_download_name(file_item.filename)
        suffix = Path(original_name).suffix
        stored_name = f"{int(time.time())}-{secrets.token_hex(8)}{suffix}"
        target = self.upload_dir / stored_name
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as out:
            shutil.copyfileobj(file_item.file, out)
        size = target.stat().st_size
        detected_type = file_item.type or mimetypes.guess_type(original_name)[0] or "application/octet-stream"
        raw_description = form.getfirst("description", "") if hasattr(form, "getfirst") else ""
        description = str(raw_description or default_description or "").strip()[:500]
        with db_connect(self.auth_db_path) as conn:
            cur = conn.execute(
                """
                INSERT INTO downloads (original_name, stored_name, content_type, size, uploaded_by, source, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (original_name, stored_name, detected_type, size, user["id"], source, description or None),
            )
            conn.commit()
            file_id = cur.lastrowid
        self._send_json(
            201,
            {
                "ok": True,
                "file": {
                    "id": file_id,
                    "original_name": original_name,
                    "content_type": detected_type,
                    "size": size,
                    "source": source,
                    "description": description or None,
                    "download_url": f"/download/{urllib.parse.quote(stored_name)}",
                },
            },
        )

    def _handle_upload(self) -> None:
        user = self._require_admin()
        if not user:
            return
        self._handle_file_upload(user, source="local")

    def _handle_share_upload(self) -> None:
        user = self._require_logged_in()
        if not user:
            return
        self._handle_file_upload(user, source="user_share", default_description=f"Shared by {user['email']}")

    def _serve_download(self) -> None:
        if not self._require_logged_in():
            return
        stored_name = urllib.parse.unquote(self.path.split("/download/", 1)[1].split("?", 1)[0])
        with db_connect(self.auth_db_path) as conn:
            row = conn.execute(
                "SELECT original_name, stored_name, content_type, size, COALESCE(source, 'local') AS source, external_url FROM downloads WHERE stored_name = ?",
                (stored_name,),
            ).fetchone()
        if not row:
            self.send_error(404, "download not found")
            return
        if row["source"] == "google_drive" and row["external_url"]:
            self.send_response(302)
            self.send_header("Location", row["external_url"])
            self.end_headers()
            return
        path = self.upload_dir / row["stored_name"]
        if not path.exists():
            self.send_error(404, "file missing")
            return
        self.send_response(200)
        self.send_header("Content-Type", row["content_type"] or "application/octet-stream")
        self.send_header("Content-Length", str(path.stat().st_size))
        self.send_header("Content-Disposition", f"attachment; filename=\"{row['original_name']}\"")
        self.end_headers()
        with path.open("rb") as src:
            shutil.copyfileobj(src, self.wfile)

    def _proxy(self, base_url: str | None = None) -> None:
        target = urljoin((base_url or self.api_base).rstrip("/") + "/", self.path.lstrip("/"))
        body = None
        if self.command in {"POST", "PUT", "PATCH"}:
            length = int(self.headers.get("Content-Length") or "0")
            body = self.rfile.read(length) if length else None
        headers = {k: v for k, v in self.headers.items() if k.lower() not in {"host", "content-length", "connection"}}
        req = urllib.request.Request(target, data=body, headers=headers, method=self.command)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                self.send_response(resp.status)
                for key, value in resp.headers.items():
                    if key.lower() not in {"connection", "transfer-encoding"}:
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as exc:
            data = exc.read()
            self.send_response(exc.code)
            self.send_header("Content-Type", exc.headers.get("Content-Type", "application/json"))
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as exc:
            data = f"gateway proxy error: {exc}\n".encode()
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    def _crm_rows(self, conn: sqlite3.Connection, query: str, params: tuple = ()) -> list[dict]:
        return [dict(row) for row in conn.execute(query, params).fetchall()]

    def _handle_admin_crm(self) -> None:
        if not self._require_admin():
            return
        query = parse_qs(urllib.parse.urlparse(self.path).query)
        site_id = str((query.get("site_id") or ["ai-solo-company-class"])[0] or "ai-solo-company-class")[:100]
        try:
            limit = max(1, min(int((query.get("limit") or [50])[0]), 100))
        except Exception:
            limit = 50
        crm = SoloCRM(self.crm_db_path)
        summary = crm.website_summary(site_id=site_id)
        customers = crm.list_website_customers(site_id=site_id, limit=limit)
        visitors = crm.list_website_visitors(site_id=site_id, limit=limit)
        with crm.connect() as conn:
            submissions = self._crm_rows(
                conn,
                """
                SELECT activities.*, contacts.name AS contact_name, contacts.email AS contact_email,
                       contacts.phone AS contact_phone, companies.name AS company_name,
                       deals.title AS deal_title, websites.site_id, websites.name AS website_name
                FROM activities
                LEFT JOIN contacts ON contacts.id = activities.contact_id
                LEFT JOIN companies ON companies.id = contacts.company_id
                LEFT JOIN deals ON deals.id = activities.deal_id
                LEFT JOIN websites ON websites.id = activities.website_id
                WHERE websites.site_id = ? AND activities.kind IN ('lead', 'chat', 'email', 'note')
                ORDER BY activities.happened_at DESC, activities.id DESC
                LIMIT ?
                """,
                (site_id, limit),
            )
            deals = self._crm_rows(
                conn,
                """
                SELECT deals.*, contacts.name AS contact_name, contacts.email AS contact_email,
                       companies.name AS company_name, websites.site_id
                FROM deals
                LEFT JOIN contacts ON contacts.id = deals.contact_id
                LEFT JOIN companies ON companies.id = deals.company_id
                LEFT JOIN websites ON websites.id = deals.website_id
                WHERE websites.site_id = ?
                ORDER BY deals.updated_at DESC, deals.id DESC
                LIMIT ?
                """,
                (site_id, limit),
            )
        summary = {
            **summary,
            "customers": len(customers),
            "submissions": len(submissions),
            "visitors": summary.get("visitors", len(visitors)),
            "open_deals": summary.get("open_deals", len([deal for deal in deals if deal.get("stage") not in {"won", "lost"}])),
        }
        self._send_json(200, {
            "ok": True,
            "site_id": site_id,
            "summary": summary,
            "customers": customers,
            "submissions": submissions,
            "visitors": visitors,
            "deals": deals,
        })

    def _proxy_wiki(self) -> None:
        path = self.path.split("?", 1)[0]
        user = self._require_admin() if self.command == "POST" else self._require_logged_in()
        if not user:
            return
        self._proxy(self.wiki_api_base)

    def _proxy_email_agent(self) -> None:
        if not self._require_admin():
            return
        self._proxy()

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/health" or path.startswith("/api/chat/") or path.startswith("/api/rag/"):
            self._proxy()
        elif path.startswith("/api/email-agent/"):
            self._proxy_email_agent()
        elif path.startswith("/api/wiki/"):
            self._proxy_wiki()
        elif path == "/api/admin/crm":
            self._handle_admin_crm()
        elif path == "/auth/me":
            self._handle_me()
        elif path == "/downloads.html" and not self._current_user():
            self._redirect_to_login("downloads.html")
        elif path == "/api/downloads":
            self._handle_downloads()
        elif path.startswith("/download/"):
            self._serve_download()
        else:
            super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path.startswith("/api/chat/") or path.startswith("/api/rag/"):
            self._proxy()
        elif path.startswith("/api/email-agent/"):
            self._proxy_email_agent()
        elif path.startswith("/api/wiki/"):
            self._proxy_wiki()
        elif path == "/auth/login":
            self._handle_login()
        elif path == "/auth/change-password":
            self._handle_change_password()
        elif path == "/auth/logout":
            self._handle_logout()
        elif path == "/admin/upload":
            self._handle_upload()
        elif path == "/api/share/upload":
            self._handle_share_upload()
        else:
            self.send_error(405, "method not allowed")

    def do_OPTIONS(self) -> None:  # noqa: N802
        if self.path.startswith("/api/"):
            if self.path.startswith("/api/wiki/"):
                self._proxy(self.wiki_api_base)
            elif self.path.startswith("/api/email-agent/"):
                self._proxy_email_agent()
            else:
                self._proxy()
        else:
            self.send_response(204)
            self.end_headers()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8020)
    parser.add_argument("--site-dir", required=True)
    parser.add_argument("--api-base", default="http://127.0.0.1:8099")
    parser.add_argument("--wiki-api-base", default="http://127.0.0.1:8105")
    parser.add_argument("--auth-db", default="/home/jianl/.hermes/tools/website_chatbot/data/ai_solo_site.db")
    parser.add_argument("--crm-db", default=os.environ.get("SOLO_CRM_DB", "/home/jianl/.hermes/tools/solo_crm/solo_crm.db"))
    parser.add_argument("--upload-dir", default="/home/jianl/.hermes/tools/website_chatbot/data/ai_solo_downloads")
    parser.add_argument("--admin-email", default=os.environ.get("AI_SOLO_ADMIN_EMAIL", "jian.lin@easiio.com"))
    parser.add_argument("--admin-password", default=os.environ.get("AI_SOLO_ADMIN_PASSWORD", ""))
    args = parser.parse_args()
    site_dir = Path(args.site_dir).resolve()
    GatewayHandler.api_base = args.api_base
    GatewayHandler.wiki_api_base = args.wiki_api_base
    GatewayHandler.auth_db_path = Path(args.auth_db).expanduser().resolve()
    GatewayHandler.crm_db_path = Path(args.crm_db).expanduser().resolve()
    GatewayHandler.upload_dir = Path(args.upload_dir).expanduser().resolve()
    GatewayHandler.admin_email = args.admin_email
    GatewayHandler.admin_password = args.admin_password
    if not args.admin_password:
        raise SystemExit("AI_SOLO_ADMIN_PASSWORD or --admin-password is required to initialize the admin account")
    initialize_auth_backend(GatewayHandler.auth_db_path, GatewayHandler.upload_dir, args.admin_email, args.admin_password)
    handler = lambda *a, **kw: GatewayHandler(*a, directory=str(site_dir), **kw)
    with ReusableThreadingTCPServer((args.host, args.port), handler) as httpd:
        print(
            f"Serving gateway on {args.host}:{args.port}; site={site_dir}; api={args.api_base}; wiki_api={args.wiki_api_base}; auth_db={GatewayHandler.auth_db_path}",
            flush=True,
        )
        httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
