#!/usr/bin/env python3
"""SQLite-backed CRM core for the AI solo company project."""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_DB = Path(os.environ.get("SOLO_CRM_DB", Path.home() / ".hermes" / "tools" / "solo_crm" / "solo_crm.db"))


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _json_list(value: Any) -> str:
    if value is None:
        return "[]"
    if isinstance(value, str):
        # Accept comma-separated input from humans, but preserve JSON strings if supplied.
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return json.dumps(parsed)
        except Exception:
            pass
        return json.dumps([part.strip() for part in value.split(",") if part.strip()])
    if isinstance(value, (list, tuple, set)):
        return json.dumps(list(value))
    return json.dumps([str(value)])


def _decode_row(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    for key in ("tags",):
        if key in data and isinstance(data[key], str):
            try:
                data[key] = json.loads(data[key])
            except Exception:
                data[key] = []
    return data


class SoloCRM:
    """Small CRM with contacts, companies, deals, activities, and follow-ups."""

    def __init__(self, db_path: str | Path = DEFAULT_DB):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS organizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    slug TEXT NOT NULL UNIQUE,
                    website TEXT DEFAULT '',
                    notes TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS websites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER,
                    site_id TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    domain TEXT DEFAULT '',
                    url TEXT DEFAULT '',
                    notes TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(organization_id) REFERENCES organizations(id) ON DELETE SET NULL
                );
                CREATE TABLE IF NOT EXISTS website_visitors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER,
                    website_id INTEGER,
                    visitor_key TEXT NOT NULL,
                    first_seen_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    email TEXT DEFAULT '',
                    phone TEXT DEFAULT '',
                    name TEXT DEFAULT '',
                    company TEXT DEFAULT '',
                    user_agent TEXT DEFAULT '',
                    notes TEXT DEFAULT '',
                    FOREIGN KEY(organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
                    FOREIGN KEY(website_id) REFERENCES websites(id) ON DELETE SET NULL,
                    UNIQUE(website_id, visitor_key)
                );
                CREATE TABLE IF NOT EXISTS website_visits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER,
                    website_id INTEGER,
                    visitor_id INTEGER,
                    session_id TEXT DEFAULT '',
                    page_url TEXT DEFAULT '',
                    page_title TEXT DEFAULT '',
                    referrer TEXT DEFAULT '',
                    user_agent TEXT DEFAULT '',
                    ip_address TEXT DEFAULT '',
                    utm TEXT DEFAULT '{}',
                    occurred_at TEXT NOT NULL,
                    FOREIGN KEY(organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
                    FOREIGN KEY(website_id) REFERENCES websites(id) ON DELETE SET NULL,
                    FOREIGN KEY(visitor_id) REFERENCES website_visitors(id) ON DELETE SET NULL
                );
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER,
                    website_id INTEGER,
                    name TEXT NOT NULL UNIQUE,
                    website TEXT DEFAULT '',
                    industry TEXT DEFAULT '',
                    notes TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
                    FOREIGN KEY(website_id) REFERENCES websites(id) ON DELETE SET NULL
                );
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT DEFAULT '',
                    phone TEXT DEFAULT '',
                    company_id INTEGER,
                    organization_id INTEGER,
                    website_id INTEGER,
                    visitor_id INTEGER,
                    role TEXT DEFAULT '',
                    status TEXT DEFAULT 'lead',
                    source TEXT DEFAULT '',
                    tags TEXT DEFAULT '[]',
                    notes TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE SET NULL,
                    FOREIGN KEY(organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
                    FOREIGN KEY(website_id) REFERENCES websites(id) ON DELETE SET NULL,
                    FOREIGN KEY(visitor_id) REFERENCES website_visitors(id) ON DELETE SET NULL
                );
                CREATE TABLE IF NOT EXISTS deals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    contact_id INTEGER,
                    company_id INTEGER,
                    organization_id INTEGER,
                    website_id INTEGER,
                    value REAL DEFAULT 0,
                    currency TEXT DEFAULT 'USD',
                    stage TEXT DEFAULT 'new',
                    probability INTEGER DEFAULT 0,
                    close_date TEXT DEFAULT '',
                    notes TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE SET NULL,
                    FOREIGN KEY(organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
                    FOREIGN KEY(website_id) REFERENCES websites(id) ON DELETE SET NULL
                );
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER,
                    deal_id INTEGER,
                    organization_id INTEGER,
                    website_id INTEGER,
                    visitor_id INTEGER,
                    kind TEXT NOT NULL DEFAULT 'note',
                    body TEXT NOT NULL,
                    happened_at TEXT NOT NULL,
                    follow_up_at TEXT DEFAULT '',
                    completed INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
                    FOREIGN KEY(deal_id) REFERENCES deals(id) ON DELETE SET NULL,
                    FOREIGN KEY(organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
                    FOREIGN KEY(website_id) REFERENCES websites(id) ON DELETE SET NULL,
                    FOREIGN KEY(visitor_id) REFERENCES website_visitors(id) ON DELETE SET NULL
                );
                CREATE INDEX IF NOT EXISTS idx_contacts_search ON contacts(name, email, notes);
                CREATE INDEX IF NOT EXISTS idx_deals_stage ON deals(stage);
                CREATE INDEX IF NOT EXISTS idx_activities_followup ON activities(follow_up_at, completed);
                """
            )
            self._migrate_existing_schema(conn)

    def _migrate_existing_schema(self, conn: sqlite3.Connection) -> None:
        def add_column(table: str, column: str, definition: str) -> None:
            cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
            if column not in cols:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        for table in ("companies",):
            add_column(table, "organization_id", "INTEGER")
            add_column(table, "website_id", "INTEGER")
        for table in ("contacts",):
            add_column(table, "organization_id", "INTEGER")
            add_column(table, "website_id", "INTEGER")
            add_column(table, "visitor_id", "INTEGER")
        for table in ("deals",):
            add_column(table, "organization_id", "INTEGER")
            add_column(table, "website_id", "INTEGER")
        for table in ("activities",):
            add_column(table, "organization_id", "INTEGER")
            add_column(table, "website_id", "INTEGER")
            add_column(table, "visitor_id", "INTEGER")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_contacts_site ON contacts(organization_id, website_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_deals_site ON deals(organization_id, website_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_activities_site ON activities(organization_id, website_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_websites_org ON websites(organization_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_visits_site_time ON website_visits(website_id, occurred_at)")

    def _fetch_one(self, query: str, params: tuple[Any, ...]) -> dict[str, Any] | None:
        with self.connect() as conn:
            return _decode_row(conn.execute(query, params).fetchone())

    def _fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self.connect() as conn:
            return [_decode_row(row) for row in conn.execute(query, params).fetchall()]  # type: ignore[list-item]


    def create_organization(self, name: str, slug: str = "", website: str = "", notes: str = "") -> dict[str, Any]:
        stamp = now_iso()
        slug = (slug or name).lower().strip().replace(" ", "-")
        slug = "".join(ch for ch in slug if ch.isalnum() or ch in "-_") or "default"
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO organizations(name, slug, website, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(slug) DO UPDATE SET
                    name=excluded.name,
                    website=excluded.website,
                    notes=excluded.notes,
                    updated_at=excluded.updated_at
                RETURNING *
                """,
                (name, slug, website, notes, stamp, stamp),
            )
            return _decode_row(cur.fetchone())  # type: ignore[return-value]

    def get_organization(self, organization_id: int) -> dict[str, Any] | None:
        return self._fetch_one("SELECT * FROM organizations WHERE id=?", (organization_id,))

    def list_organizations(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._fetch_all("SELECT * FROM organizations ORDER BY updated_at DESC, id DESC LIMIT ?", (max(1, min(int(limit), 100)),))

    def create_website(self, site_id: str, name: str = "", organization_id: int | None = None,
                       domain: str = "", url: str = "", notes: str = "") -> dict[str, Any]:
        stamp = now_iso()
        site_id = (site_id or "default").strip()
        name = name or site_id
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO websites(organization_id, site_id, name, domain, url, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(site_id) DO UPDATE SET
                    organization_id=COALESCE(excluded.organization_id, websites.organization_id),
                    name=excluded.name,
                    domain=excluded.domain,
                    url=excluded.url,
                    notes=excluded.notes,
                    updated_at=excluded.updated_at
                RETURNING *
                """,
                (organization_id, site_id, name, domain, url, notes, stamp, stamp),
            )
            return _decode_row(cur.fetchone())  # type: ignore[return-value]

    def get_website_by_site_id(self, site_id: str) -> dict[str, Any] | None:
        return self._fetch_one(
            """
            SELECT websites.*, organizations.name AS organization_name
            FROM websites LEFT JOIN organizations ON organizations.id = websites.organization_id
            WHERE websites.site_id=?
            """,
            (site_id,),
        )

    def list_websites(self, organization_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
        params: list[Any] = []
        where = ""
        if organization_id is not None:
            where = "WHERE websites.organization_id=?"
            params.append(organization_id)
        params.append(max(1, min(int(limit), 100)))
        return self._fetch_all(
            f"""
            SELECT websites.*, organizations.name AS organization_name
            FROM websites LEFT JOIN organizations ON organizations.id = websites.organization_id
            {where}
            ORDER BY websites.updated_at DESC, websites.id DESC
            LIMIT ?
            """,
            tuple(params),
        )

    def ensure_website(self, site_id: str = "default", organization_name: str = "", website_name: str = "",
                       domain: str = "", url: str = "") -> dict[str, Any]:
        org_id = None
        if organization_name:
            org = self.create_organization(organization_name, website=url or domain)
            org_id = int(org["id"])
        existing = self.get_website_by_site_id(site_id)
        if existing and not organization_name and not website_name and not domain and not url:
            return existing
        return self.create_website(site_id=site_id, name=website_name or (existing or {}).get("name") or site_id,
                                   organization_id=org_id if org_id is not None else (existing or {}).get("organization_id"),
                                   domain=domain or (existing or {}).get("domain", ""),
                                   url=url or (existing or {}).get("url", ""))

    def record_website_visit(self, site_id: str = "default", visitor_key: str = "", session_id: str = "",
                             page_url: str = "", page_title: str = "", referrer: str = "",
                             user_agent: str = "", ip_address: str = "", utm: Any = None,
                             organization_name: str = "", website_name: str = "", domain: str = "") -> dict[str, Any]:
        stamp = now_iso()
        website = self.ensure_website(site_id=site_id, organization_name=organization_name,
                                      website_name=website_name, domain=domain, url=page_url)
        website_id = int(website["id"])
        organization_id = website.get("organization_id")
        visitor_key = visitor_key or session_id or f"anon-{stamp}"
        utm_json = json.dumps(utm if isinstance(utm, dict) else {}, ensure_ascii=False)
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO website_visitors(organization_id, website_id, visitor_key, first_seen_at, last_seen_at, user_agent)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(website_id, visitor_key) DO UPDATE SET
                    last_seen_at=excluded.last_seen_at,
                    user_agent=COALESCE(NULLIF(excluded.user_agent, ''), website_visitors.user_agent)
                RETURNING *
                """,
                (organization_id, website_id, visitor_key, stamp, stamp, user_agent),
            )
            visitor = _decode_row(cur.fetchone())
            conn.execute(
                """
                INSERT INTO website_visits(organization_id, website_id, visitor_id, session_id, page_url, page_title, referrer, user_agent, ip_address, utm, occurred_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (organization_id, website_id, visitor["id"], session_id, page_url, page_title, referrer, user_agent, ip_address, utm_json, stamp),
            )
            visitor["website"] = website
            return visitor

    def list_website_visitors(self, site_id: str = "", organization_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if site_id:
            clauses.append("websites.site_id=?")
            params.append(site_id)
        if organization_id is not None:
            clauses.append("website_visitors.organization_id=?")
            params.append(organization_id)
        where = "WHERE " + " AND ".join(clauses) if clauses else ""
        params.append(max(1, min(int(limit), 100)))
        return self._fetch_all(
            f"""
            SELECT website_visitors.*, websites.site_id, websites.name AS website_name, organizations.name AS organization_name,
                   (SELECT COUNT(*) FROM website_visits WHERE website_visits.visitor_id = website_visitors.id) AS visit_count
            FROM website_visitors
            LEFT JOIN websites ON websites.id = website_visitors.website_id
            LEFT JOIN organizations ON organizations.id = website_visitors.organization_id
            {where}
            ORDER BY website_visitors.last_seen_at DESC, website_visitors.id DESC
            LIMIT ?
            """,
            tuple(params),
        )

    def list_website_customers(self, site_id: str = "", organization_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if site_id:
            clauses.append("websites.site_id=?")
            params.append(site_id)
        if organization_id is not None:
            clauses.append("contacts.organization_id=?")
            params.append(organization_id)
        where = "WHERE " + " AND ".join(clauses) if clauses else ""
        params.append(max(1, min(int(limit), 100)))
        return self._fetch_all(
            f"""
            SELECT contacts.*, companies.name AS company_name, websites.site_id, websites.name AS website_name,
                   organizations.name AS organization_name
            FROM contacts
            LEFT JOIN companies ON companies.id = contacts.company_id
            LEFT JOIN websites ON websites.id = contacts.website_id
            LEFT JOIN organizations ON organizations.id = contacts.organization_id
            {where}
            ORDER BY contacts.updated_at DESC, contacts.id DESC
            LIMIT ?
            """,
            tuple(params),
        )

    def website_summary(self, site_id: str = "", organization_id: int | None = None) -> dict[str, Any]:
        clauses: list[str] = []
        params: list[Any] = []
        if site_id:
            clauses.append("websites.site_id=?")
            params.append(site_id)
        if organization_id is not None:
            clauses.append("websites.organization_id=?")
            params.append(organization_id)
        where = "WHERE " + " AND ".join(clauses) if clauses else ""
        with self.connect() as conn:
            websites = conn.execute(f"SELECT COUNT(*) FROM websites {where}", tuple(params)).fetchone()[0]
            visitors = conn.execute(f"SELECT COUNT(*) FROM website_visitors LEFT JOIN websites ON websites.id=website_visitors.website_id {where}", tuple(params)).fetchone()[0]
            visits = conn.execute(f"SELECT COUNT(*) FROM website_visits LEFT JOIN websites ON websites.id=website_visits.website_id {where}", tuple(params)).fetchone()[0]
            contacts = conn.execute(f"SELECT COUNT(*) FROM contacts LEFT JOIN websites ON websites.id=contacts.website_id {where}", tuple(params)).fetchone()[0]
            deals = conn.execute(f"SELECT COUNT(*) FROM deals LEFT JOIN websites ON websites.id=deals.website_id {where} AND deals.stage NOT IN ('won','lost')" if where else "SELECT COUNT(*) FROM deals WHERE stage NOT IN ('won','lost')", tuple(params)).fetchone()[0]
        return {"websites": websites, "visitors": visitors, "visits": visits, "contacts": contacts, "open_deals": deals, "site_id": site_id, "organization_id": organization_id}

    def create_company(self, name: str, website: str = "", industry: str = "", notes: str = "",
                       organization_id: int | None = None, website_id: int | None = None) -> dict[str, Any]:
        stamp = now_iso()
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO companies(name, website, industry, notes, organization_id, website_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    website=excluded.website,
                    industry=excluded.industry,
                    notes=excluded.notes,
                    organization_id=COALESCE(excluded.organization_id, companies.organization_id),
                    website_id=COALESCE(excluded.website_id, companies.website_id),
                    updated_at=excluded.updated_at
                RETURNING *
                """,
                (name, website, industry, notes, organization_id, website_id, stamp, stamp),
            )
            return _decode_row(cur.fetchone())  # type: ignore[return-value]

    def get_company(self, company_id: int) -> dict[str, Any] | None:
        return self._fetch_one("SELECT * FROM companies WHERE id=?", (company_id,))

    def create_contact(self, name: str, email: str = "", phone: str = "", company_id: int | None = None,
                       role: str = "", status: str = "lead", source: str = "", tags: Any = None,
                       notes: str = "", organization_id: int | None = None, website_id: int | None = None,
                       visitor_id: int | None = None) -> dict[str, Any]:
        stamp = now_iso()
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO contacts(name, email, phone, company_id, organization_id, website_id, visitor_id, role, status, source, tags, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (name, email, phone, company_id, organization_id, website_id, visitor_id, role, status, source, _json_list(tags), notes, stamp, stamp),
            )
            row = conn.execute(
                """
                SELECT contacts.*, companies.name AS company_name
                FROM contacts LEFT JOIN companies ON companies.id = contacts.company_id
                WHERE contacts.id=?
                """,
                (cur.lastrowid,),
            ).fetchone()
            return _decode_row(row)  # type: ignore[return-value]

    def get_contact(self, contact_id: int) -> dict[str, Any] | None:
        return self._fetch_one(
            """
            SELECT contacts.*, companies.name AS company_name
            FROM contacts LEFT JOIN companies ON companies.id = contacts.company_id
            WHERE contacts.id=?
            """,
            (contact_id,),
        )

    def update_contact(self, contact_id: int, **fields: Any) -> dict[str, Any] | None:
        allowed = {"name", "email", "phone", "company_id", "organization_id", "website_id", "visitor_id", "role", "status", "source", "tags", "notes"}
        updates: list[str] = []
        values: list[Any] = []
        for key, value in fields.items():
            if key in allowed and value is not None:
                updates.append(f"{key}=?")
                values.append(_json_list(value) if key == "tags" else value)
        if not updates:
            return self.get_contact(contact_id)
        updates.append("updated_at=?")
        values.extend([now_iso(), contact_id])
        with self.connect() as conn:
            conn.execute(f"UPDATE contacts SET {', '.join(updates)} WHERE id=?", tuple(values))
        return self.get_contact(contact_id)

    def search_contacts(self, query: str = "", status: str = "", tag: str = "", limit: int = 20) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if query:
            like = f"%{query}%"
            clauses.append("(contacts.name LIKE ? OR contacts.email LIKE ? OR contacts.phone LIKE ? OR contacts.notes LIKE ? OR companies.name LIKE ?)")
            params.extend([like, like, like, like, like])
        if status:
            clauses.append("contacts.status=?")
            params.append(status)
        if tag:
            clauses.append("contacts.tags LIKE ?")
            params.append(f"%{tag}%")
        where = "WHERE " + " AND ".join(clauses) if clauses else ""
        params.append(max(1, min(int(limit), 100)))
        return self._fetch_all(
            f"""
            SELECT contacts.*, companies.name AS company_name
            FROM contacts LEFT JOIN companies ON companies.id = contacts.company_id
            {where}
            ORDER BY contacts.updated_at DESC, contacts.id DESC
            LIMIT ?
            """,
            tuple(params),
        )

    def create_deal(self, title: str, contact_id: int | None = None, company_id: int | None = None,
                    value: float = 0, currency: str = "USD", stage: str = "new", probability: int = 0,
                    close_date: str = "", notes: str = "", organization_id: int | None = None,
                    website_id: int | None = None) -> dict[str, Any]:
        stamp = now_iso()
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO deals(title, contact_id, company_id, organization_id, website_id, value, currency, stage, probability, close_date, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (title, contact_id, company_id, organization_id, website_id, value, currency, stage, probability, close_date, notes, stamp, stamp),
            )
            row = conn.execute(
                """
                SELECT deals.*, contacts.name AS contact_name, companies.name AS company_name
                FROM deals
                LEFT JOIN contacts ON contacts.id = deals.contact_id
                LEFT JOIN companies ON companies.id = deals.company_id
                WHERE deals.id=?
                """,
                (cur.lastrowid,),
            ).fetchone()
            return _decode_row(row)  # type: ignore[return-value]

    def get_deal(self, deal_id: int) -> dict[str, Any] | None:
        return self._fetch_one(
            """
            SELECT deals.*, contacts.name AS contact_name, companies.name AS company_name
            FROM deals
            LEFT JOIN contacts ON contacts.id = deals.contact_id
            LEFT JOIN companies ON companies.id = deals.company_id
            WHERE deals.id=?
            """,
            (deal_id,),
        )

    def update_deal(self, deal_id: int, **fields: Any) -> dict[str, Any] | None:
        allowed = {"title", "contact_id", "company_id", "organization_id", "website_id", "value", "currency", "stage", "probability", "close_date", "notes"}
        updates: list[str] = []
        values: list[Any] = []
        for key, value in fields.items():
            if key in allowed and value is not None:
                updates.append(f"{key}=?")
                values.append(value)
        if not updates:
            return self.get_deal(deal_id)
        updates.append("updated_at=?")
        values.extend([now_iso(), deal_id])
        with self.connect() as conn:
            conn.execute(f"UPDATE deals SET {', '.join(updates)} WHERE id=?", tuple(values))
        return self.get_deal(deal_id)

    def list_deals(self, stage: str = "", contact_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if stage:
            clauses.append("deals.stage=?")
            params.append(stage)
        if contact_id is not None:
            clauses.append("deals.contact_id=?")
            params.append(contact_id)
        where = "WHERE " + " AND ".join(clauses) if clauses else ""
        params.append(max(1, min(int(limit), 100)))
        return self._fetch_all(
            f"""
            SELECT deals.*, contacts.name AS contact_name, companies.name AS company_name
            FROM deals
            LEFT JOIN contacts ON contacts.id = deals.contact_id
            LEFT JOIN companies ON companies.id = deals.company_id
            {where}
            ORDER BY deals.updated_at DESC, deals.id DESC
            LIMIT ?
            """,
            tuple(params),
        )

    def add_activity(self, contact_id: int | None = None, deal_id: int | None = None, kind: str = "note",
                     body: str = "", happened_at: str = "", follow_up_at: str = "",
                     completed: bool = False, organization_id: int | None = None, website_id: int | None = None,
                     visitor_id: int | None = None) -> dict[str, Any]:
        stamp = now_iso()
        happened = happened_at or stamp
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO activities(contact_id, deal_id, organization_id, website_id, visitor_id, kind, body, happened_at, follow_up_at, completed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (contact_id, deal_id, organization_id, website_id, visitor_id, kind, body, happened, follow_up_at, int(bool(completed)), stamp),
            )
            row = conn.execute(
                """
                SELECT activities.*, contacts.name AS contact_name, deals.title AS deal_title
                FROM activities
                LEFT JOIN contacts ON contacts.id = activities.contact_id
                LEFT JOIN deals ON deals.id = activities.deal_id
                WHERE activities.id=?
                """,
                (cur.lastrowid,),
            ).fetchone()
            return _decode_row(row)  # type: ignore[return-value]

    def get_activity(self, activity_id: int) -> dict[str, Any] | None:
        return self._fetch_one(
            """
            SELECT activities.*, contacts.name AS contact_name, deals.title AS deal_title
            FROM activities
            LEFT JOIN contacts ON contacts.id = activities.contact_id
            LEFT JOIN deals ON deals.id = activities.deal_id
            WHERE activities.id=?
            """,
            (activity_id,),
        )

    def list_activities(self, contact_id: int | None = None, deal_id: int | None = None, limit: int = 50) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if contact_id is not None:
            clauses.append("activities.contact_id=?")
            params.append(contact_id)
        if deal_id is not None:
            clauses.append("activities.deal_id=?")
            params.append(deal_id)
        where = "WHERE " + " AND ".join(clauses) if clauses else ""
        params.append(max(1, min(int(limit), 100)))
        return self._fetch_all(
            f"""
            SELECT activities.*, contacts.name AS contact_name, deals.title AS deal_title
            FROM activities
            LEFT JOIN contacts ON contacts.id = activities.contact_id
            LEFT JOIN deals ON deals.id = activities.deal_id
            {where}
            ORDER BY activities.happened_at DESC, activities.id DESC
            LIMIT ?
            """,
            tuple(params),
        )

    def complete_activity(self, activity_id: int) -> dict[str, Any] | None:
        with self.connect() as conn:
            conn.execute("UPDATE activities SET completed=1 WHERE id=?", (activity_id,))
        return self.get_activity(activity_id)

    def next_followups(self, limit: int = 10) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT activities.*, contacts.name AS contact_name, contacts.email AS contact_email, deals.title AS deal_title
            FROM activities
            LEFT JOIN contacts ON contacts.id = activities.contact_id
            LEFT JOIN deals ON deals.id = activities.deal_id
            WHERE activities.follow_up_at != '' AND activities.completed = 0
            ORDER BY activities.follow_up_at ASC, activities.id ASC
            LIMIT ?
            """,
            (max(1, min(int(limit), 100)),),
        )

    def summary(self) -> dict[str, Any]:
        with self.connect() as conn:
            contacts = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
            companies = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
            open_deals = conn.execute("SELECT COUNT(*) FROM deals WHERE stage NOT IN ('won', 'lost')").fetchone()[0]
            pipeline_value = conn.execute("SELECT COALESCE(SUM(value), 0) FROM deals WHERE stage NOT IN ('won', 'lost')").fetchone()[0]
            due_followups = conn.execute("SELECT COUNT(*) FROM activities WHERE follow_up_at != '' AND completed = 0").fetchone()[0]
            organizations = conn.execute("SELECT COUNT(*) FROM organizations").fetchone()[0]
            websites = conn.execute("SELECT COUNT(*) FROM websites").fetchone()[0]
            visitors = conn.execute("SELECT COUNT(*) FROM website_visitors").fetchone()[0]
            visits = conn.execute("SELECT COUNT(*) FROM website_visits").fetchone()[0]
        return {
            "organizations": organizations,
            "websites": websites,
            "visitors": visitors,
            "visits": visits,
            "contacts": contacts,
            "companies": companies,
            "open_deals": open_deals,
            "pipeline_value": pipeline_value,
            "due_followups": due_followups,
            "db_path": str(self.db_path),
        }
