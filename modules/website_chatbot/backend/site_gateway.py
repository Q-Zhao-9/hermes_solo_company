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
import difflib
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
    skills_root = Path("/home/jianl/.hermes/skills")
    site_skill_docs_root = Path("/mnt/c/Users/jianl/solo-company-class-site/docs")
    student_skills_root = Path("/home/jianl/.hermes/tools/website_chatbot/data/student_skills")
    student_skill_allowlist = {
        "class4/student-lead-followup": {
            "name": "student-lead-followup",
            "template": Path("class4/student-lead-followup/SKILL.md"),
            "description": "Student local copy of the Class 4 lead follow-up skill",
        }
    }
    admin_email = "jian.lin@easiio.com"
    admin_password = ""

    def _cors_origin(self) -> str | None:
        origin = self.headers.get("Origin", "").strip()
        if not origin:
            return None
        try:
            parsed = urllib.parse.urlparse(origin)
        except Exception:
            return None
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in {"http", "https"}:
            return None
        if host in {"sitelet.easiiodev.ai", "hermesproxy.easiiodev.ai", "localhost", "127.0.0.1"}:
            return origin
        if host.endswith(".easiiodev.ai"):
            return origin
        return None

    def _send_cors_headers(self) -> None:
        origin = self._cors_origin()
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")

    def _send_json(self, status: int, payload: dict, headers: dict[str, str] | None = None) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self._send_cors_headers()
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
                    if key.lower() not in {"connection", "transfer-encoding", "access-control-allow-origin", "access-control-allow-methods", "access-control-allow-headers", "vary"}:
                        self.send_header(key, value)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as exc:
            data = exc.read()
            self.send_response(exc.code)
            self.send_header("Content-Type", exc.headers.get("Content-Type", "application/json"))
            self.send_header("Content-Length", str(len(data)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(data)
        except Exception as exc:
            data = f"gateway proxy error: {exc}\n".encode()
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self._send_cors_headers()
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
            visits = self._crm_rows(
                conn,
                """
                SELECT website_visits.*, website_visitors.visitor_key, website_visitors.email AS visitor_email,
                       website_visitors.name AS visitor_name, websites.site_id, websites.name AS website_name
                FROM website_visits
                LEFT JOIN website_visitors ON website_visitors.id = website_visits.visitor_id
                LEFT JOIN websites ON websites.id = website_visits.website_id
                WHERE websites.site_id = ?
                ORDER BY website_visits.occurred_at DESC, website_visits.id DESC
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
            "visits": visits,
            "deals": deals,
        })

    def _proxy_wiki(self) -> None:
        path = self.path.split("?", 1)[0]
        user = self._require_admin() if self.command == "POST" else self._require_logged_in()
        if not user:
            return
        self._proxy(self.wiki_api_base)


    def _safe_skill_path(self, raw_path: str) -> Path | None:
        if not raw_path:
            return None
        try:
            path = Path(urllib.parse.unquote(str(raw_path))).expanduser().resolve()
        except Exception:
            return None
        allowed_roots = [self.skills_root.expanduser().resolve(), self.site_skill_docs_root.expanduser().resolve()]
        if path.name != "SKILL.md":
            return None
        for root in allowed_roots:
            try:
                path.relative_to(root)
                return path
            except ValueError:
                continue
        return None

    @staticmethod
    def _skill_frontmatter(text: str) -> dict:
        meta = {}
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                for line in parts[1].splitlines():
                    if ":" in line:
                        key, value = line.split(":", 1)
                        meta[key.strip()] = value.strip().strip('"').strip("'")
        return meta

    def _skill_summary(self, path: Path) -> dict:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            text = ""
        meta = self._skill_frontmatter(text)
        try:
            rel = str(path.relative_to(self.skills_root.expanduser().resolve()))
            category = rel.split("/", 1)[0] if "/" in rel else "general"
        except ValueError:
            try:
                rel = str(path.relative_to(self.site_skill_docs_root.expanduser().resolve()))
            except ValueError:
                rel = path.name
            category = "site-docs"
        name = meta.get("name") or (path.parent.name if path.parent.name else "skill")
        return {
            "name": name,
            "description": meta.get("description", ""),
            "category": category,
            "path": str(path),
            "relative_path": rel,
            "updated_at": int(path.stat().st_mtime) if path.exists() else 0,
        }

    def _handle_skills_list(self) -> None:
        if not self._require_admin():
            return
        roots = [self.skills_root.expanduser().resolve(), self.site_skill_docs_root.expanduser().resolve()]
        skills = []
        for root in roots:
            if not root.exists():
                continue
            for path in root.rglob("SKILL.md"):
                safe = self._safe_skill_path(str(path))
                if safe:
                    skills.append(self._skill_summary(safe))
        skills.sort(key=lambda item: (item.get("category", ""), item.get("name", "")))
        self._send_json(200, {"ok": True, "skills": skills})

    def _handle_skill_file_get(self) -> None:
        if not self._require_admin():
            return
        query = parse_qs(urllib.parse.urlparse(self.path).query)
        path = self._safe_skill_path((query.get("path") or [""])[0])
        if not path or not path.exists():
            self._send_json(404, {"ok": False, "error": "skill_not_found"})
            return
        self._send_json(200, {"ok": True, "skill": self._skill_summary(path), "content": path.read_text(encoding="utf-8")})

    def _handle_skill_file_save(self) -> None:
        if not self._require_admin():
            return
        try:
            payload = self._read_json()
        except Exception:
            self._send_json(400, {"ok": False, "error": "invalid_json"})
            return
        path = self._safe_skill_path(str(payload.get("path") or ""))
        content = str(payload.get("content") or "")
        if not path:
            self._send_json(400, {"ok": False, "error": "invalid_skill_path"})
            return
        if not content.startswith("---") or "name:" not in content[:500]:
            self._send_json(400, {"ok": False, "error": "skill_frontmatter_required"})
            return
        if any(secret in content.lower() for secret in ["api_key=", "password=", "authorization: bearer", "private key"]):
            self._send_json(400, {"ok": False, "error": "possible_secret_detected"})
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        backup = path.with_suffix(path.suffix + f".bak-{int(time.time())}")
        if path.exists():
            shutil.copy2(path, backup)
        path.write_text(content, encoding="utf-8")
        self._send_json(200, {"ok": True, "skill": self._skill_summary(path), "backup_path": str(backup) if backup.exists() else ""})

    def _student_skill_root(self, user: dict) -> Path:
        return (self.student_skills_root.expanduser().resolve() / str(user["id"])).resolve()

    def _student_skill_path(self, user: dict, skill_id: str) -> Path | None:
        if skill_id not in self.student_skill_allowlist:
            return None
        relative = self.student_skill_allowlist[skill_id]["template"]
        root = self._student_skill_root(user)
        path = (root / relative).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            return None
        return path

    def _student_skill_template_path(self, skill_id: str) -> Path | None:
        spec = self.student_skill_allowlist.get(skill_id)
        if not spec:
            return None
        relative = spec["template"]
        candidates = [
            (self.site_skill_docs_root.expanduser().resolve() / relative).resolve(),
            (self.skills_root.expanduser().resolve() / relative).resolve(),
        ]
        for candidate in candidates:
            if candidate.exists() and candidate.name == "SKILL.md":
                return candidate
        return None

    def _ensure_student_skill_copy(self, user: dict, skill_id: str) -> Path | None:
        path = self._student_skill_path(user, skill_id)
        if not path:
            return None
        if path.exists():
            return path
        template = self._student_skill_template_path(skill_id)
        if not template:
            return None
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(template, path)
        return path

    def _student_skill_summary(self, user: dict, skill_id: str, path: Path | None = None) -> dict:
        spec = self.student_skill_allowlist[skill_id]
        path = path or self._student_skill_path(user, skill_id)
        text = path.read_text(encoding="utf-8") if path and path.exists() else ""
        meta = self._skill_frontmatter(text)
        return {
            "skill_id": skill_id,
            "name": meta.get("name") or spec["name"],
            "description": meta.get("description") or spec["description"],
            "relative_path": str(spec["template"]),
            "is_student_copy": True,
            "updated_at": int(path.stat().st_mtime) if path and path.exists() else 0,
        }

    @staticmethod
    def _validate_skill_content(content: str) -> str | None:
        if not content.startswith("---") or "name:" not in content[:500]:
            return "skill_frontmatter_required"
        lowered = content.lower()
        if any(secret in lowered for secret in ["api_key=", "password=", "authorization: bearer", "private key", "-----begin"]):
            return "possible_secret_detected"
        return None

    def _handle_student_skills_list(self) -> None:
        user = self._require_logged_in()
        if not user:
            return
        skills = []
        for skill_id in self.student_skill_allowlist:
            path = self._ensure_student_skill_copy(user, skill_id)
            if path:
                skills.append(self._student_skill_summary(user, skill_id, path))
        self._send_json(200, {"ok": True, "skills": skills})

    def _handle_student_skill_file_get(self) -> None:
        user = self._require_logged_in()
        if not user:
            return
        query = parse_qs(urllib.parse.urlparse(self.path).query)
        skill_id = (query.get("skill_id") or [""])[0]
        path = self._ensure_student_skill_copy(user, skill_id)
        if not path or not path.exists():
            self._send_json(404, {"ok": False, "error": "student_skill_not_found"})
            return
        self._send_json(200, {"ok": True, "skill": self._student_skill_summary(user, skill_id, path), "content": path.read_text(encoding="utf-8")})

    def _handle_student_skill_file_save(self) -> None:
        user = self._require_logged_in()
        if not user:
            return
        try:
            payload = self._read_json()
        except Exception:
            self._send_json(400, {"ok": False, "error": "invalid_json"})
            return
        skill_id = str(payload.get("skill_id") or "")
        path = self._student_skill_path(user, skill_id)
        if not path:
            self._send_json(400, {"ok": False, "error": "invalid_student_skill"})
            return
        content = str(payload.get("content") or "")
        validation_error = self._validate_skill_content(content)
        if validation_error:
            self._send_json(400, {"ok": False, "error": validation_error})
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        backup = path.with_suffix(path.suffix + f".bak-{int(time.time())}")
        if path.exists():
            shutil.copy2(path, backup)
        path.write_text(content, encoding="utf-8")
        self._send_json(200, {"ok": True, "skill": self._student_skill_summary(user, skill_id, path), "backup_created": backup.exists()})

    def _handle_student_skill_reset(self) -> None:
        user = self._require_logged_in()
        if not user:
            return
        try:
            payload = self._read_json()
        except Exception:
            self._send_json(400, {"ok": False, "error": "invalid_json"})
            return
        skill_id = str(payload.get("skill_id") or "")
        path = self._student_skill_path(user, skill_id)
        template = self._student_skill_template_path(skill_id)
        if not path or not template:
            self._send_json(400, {"ok": False, "error": "invalid_student_skill"})
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        backup = path.with_suffix(path.suffix + f".bak-{int(time.time())}")
        if path.exists():
            shutil.copy2(path, backup)
        shutil.copy2(template, path)
        self._send_json(200, {"ok": True, "skill": self._student_skill_summary(user, skill_id, path), "backup_created": backup.exists()})

    @staticmethod
    def _parse_student_lead_input(raw_text: str) -> dict:
        lead = {}
        aliases = {
            "business": "business",
            "company": "business",
            "business / company": "business",
            "service": "service_interest",
            "service interest": "service_interest",
        }
        for line in str(raw_text or "").splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            normalized = key.strip().lower().replace("_", " ")
            field = aliases.get(normalized, normalized.replace(" ", "_"))
            lead[field] = value.strip() or "Unknown"
        return lead

    @staticmethod
    def _infer_student_skill_style(skill_text: str) -> dict:
        lowered = skill_text.lower()
        tone = "warm and consultative"
        if "more direct" in lowered or "direct" in lowered:
            tone = "direct and practical"
        elif "premium" in lowered:
            tone = "polished and premium"
        elif "casual" in lowered:
            tone = "casual and friendly"
        elif "concise" in lowered or "shorter" in lowered:
            tone = "concise and helpful"
        wants_json = "json" in lowered and "output format" in lowered
        return {"tone": tone, "wants_json": wants_json}

    @staticmethod
    def _score_student_lead(lead: dict) -> tuple[int, str]:
        budget = str(lead.get("budget") or "").lower()
        timeline = str(lead.get("timeline") or "").lower()
        need = str(lead.get("need") or lead.get("service_interest") or "").lower()
        score = 2
        reasons = []
        if any(marker in budget for marker in ["$", "month", "budget", "1500", "2000", "5000"]):
            score += 1
            reasons.append("budget signal is present")
        if any(marker in timeline for marker in ["now", "this month", "urgent", "week"]):
            score += 1
            reasons.append("timeline shows urgency")
        if any(marker in need for marker in ["chatbot", "ai", "automation", "website", "appointment", "lead"]):
            score += 1
            reasons.append("need is a clear AI solo company fit")
        score = max(1, min(score, 5))
        return score, "; ".join(reasons) if reasons else "Need, budget, and timeline need more clarification."

    def _render_student_skill_test_output(self, skill_text: str, sample_input: str) -> dict:
        lead = self._parse_student_lead_input(sample_input)
        style = self._infer_student_skill_style(skill_text)
        score, score_reason = self._score_student_lead(lead)
        name = lead.get("name") or "Unknown"
        email = lead.get("email") or "Unknown"
        business = lead.get("business") or lead.get("company") or lead.get("business_type") or "Unknown"
        need = lead.get("need") or lead.get("service_interest") or "Unknown"
        budget = lead.get("budget") or "Unknown"
        timeline = lead.get("timeline") or "Unknown"
        source = lead.get("source") or "student_skill_test"
        subject = f"Next step for {business}" if business != "Unknown" else "Next step for your AI workflow"
        output = f"""## Lead summary
- Name: {name}
- Email: {email}
- Business / company: {business}
- Need: {need}
- Budget: {budget}
- Timeline: {timeline}
- Source: {source}

## Qualification score
- lead_score: {score}
- score_reason: {score_reason}

## Follow-up email
Subject: {subject}

Hi {name if name != 'Unknown' else 'there'},

Thanks for sharing what you are building. Based on your note about {need}, the best next step is a short discovery call so we can confirm the workflow, expected ROI, and launch timeline. I will keep the follow-up {style['tone']}.

Would you be open to a 20-minute call this week?

## CRM note
- Lead source: {source}
- Problem / need: {need}
- Fit: Score {score}/5 based on {score_reason}
- Budget / timeline: {budget} / {timeline}
- Recommended next action: Send follow-up email and propose a short discovery call.

## Next action
Send the follow-up email, then update the CRM after the student receives a reply.
"""
        checklist = [
            {"label": "Lead summary section present", "passed": "## Lead summary" in output},
            {"label": "Qualification score section present", "passed": "## Qualification score" in output},
            {"label": "lead_score is between 1 and 5", "passed": 1 <= score <= 5},
            {"label": "score_reason is present", "passed": bool(score_reason)},
            {"label": "Follow-up email section present", "passed": "## Follow-up email" in output},
            {"label": "CRM note section present", "passed": "## CRM note" in output},
            {"label": "Next action section present", "passed": "## Next action" in output},
        ]
        if style["wants_json"]:
            output += "\n## JSON practice note\nYour skill mentions JSON output. For class testing, keep the Markdown sections above unless your assignment specifically asks for JSON.\n"
        return {"output": output, "checklist": checklist, "style": style, "parsed_lead": lead}

    def _handle_student_skill_test(self) -> None:
        user = self._require_logged_in()
        if not user:
            return
        try:
            payload = self._read_json()
        except Exception:
            self._send_json(400, {"ok": False, "error": "invalid_json"})
            return
        skill_id = str(payload.get("skill_id") or "")
        path = self._ensure_student_skill_copy(user, skill_id)
        if not path or not path.exists():
            self._send_json(400, {"ok": False, "error": "invalid_student_skill"})
            return
        sample_input = str(payload.get("sample_input") or "").strip()
        if not sample_input:
            self._send_json(400, {"ok": False, "error": "sample_input_required"})
            return
        skill_text = path.read_text(encoding="utf-8")
        result = self._render_student_skill_test_output(skill_text, sample_input)
        self._send_json(200, {"ok": True, "skill": self._student_skill_summary(user, skill_id, path), "result": result})

    def _handle_student_skill_diff(self) -> None:
        user = self._require_logged_in()
        if not user:
            return
        query = parse_qs(urllib.parse.urlparse(self.path).query)
        skill_id = (query.get("skill_id") or [""])[0]
        path = self._ensure_student_skill_copy(user, skill_id)
        template = self._student_skill_template_path(skill_id)
        if not path or not path.exists() or not template:
            self._send_json(400, {"ok": False, "error": "invalid_student_skill"})
            return
        template_text = template.read_text(encoding="utf-8")
        student_text = path.read_text(encoding="utf-8")
        diff_lines = list(difflib.unified_diff(
            template_text.splitlines(),
            student_text.splitlines(),
            fromfile="teacher-template/SKILL.md",
            tofile="my-student-copy/SKILL.md",
            lineterm="",
        ))
        self._send_json(200, {
            "ok": True,
            "skill": self._student_skill_summary(user, skill_id, path),
            "has_changes": template_text != student_text,
            "diff": "\n".join(diff_lines) if diff_lines else "No changes from the teacher template yet.",
        })

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
        elif path == "/api/skills":
            self._handle_skills_list()
        elif path == "/api/skills/file":
            self._handle_skill_file_get()
        elif path == "/api/student/skills":
            self._handle_student_skills_list()
        elif path == "/api/student/skills/file":
            self._handle_student_skill_file_get()
        elif path == "/api/student/skills/diff":
            self._handle_student_skill_diff()
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
        elif path == "/api/skills/file":
            self._handle_skill_file_save()
        elif path == "/api/student/skills/file":
            self._handle_student_skill_file_save()
        elif path == "/api/student/skills/reset":
            self._handle_student_skill_reset()
        elif path == "/api/student/skills/test":
            self._handle_student_skill_test()
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
            self._send_cors_headers()
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
    parser.add_argument("--student-skills-dir", default="/home/jianl/.hermes/tools/website_chatbot/data/student_skills")
    parser.add_argument("--admin-email", default=os.environ.get("AI_SOLO_ADMIN_EMAIL", "jian.lin@easiio.com"))
    parser.add_argument("--admin-password", default=os.environ.get("AI_SOLO_ADMIN_PASSWORD", ""))
    args = parser.parse_args()
    site_dir = Path(args.site_dir).resolve()
    GatewayHandler.api_base = args.api_base
    GatewayHandler.wiki_api_base = args.wiki_api_base
    GatewayHandler.auth_db_path = Path(args.auth_db).expanduser().resolve()
    GatewayHandler.crm_db_path = Path(args.crm_db).expanduser().resolve()
    GatewayHandler.upload_dir = Path(args.upload_dir).expanduser().resolve()
    GatewayHandler.student_skills_root = Path(args.student_skills_dir).expanduser().resolve()
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
