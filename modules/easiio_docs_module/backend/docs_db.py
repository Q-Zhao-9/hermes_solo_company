from __future__ import annotations

import json
import re
import sqlite3
import time
from pathlib import Path
from typing import Any

SLUG_RE = re.compile(r"[^a-z0-9-]+")
SUPPORTED_STATUSES = {"draft", "published", "archived"}
SUPPORTED_VISIBILITIES = {"public", "private", "login_required", "internal"}
SUPPORTED_FORMATS = {"markdown", "mdx", "html", "text"}
SUPPORTED_TARGETS = {
    "nextjs-mdx",
    "wordpress-shortcode",
    "sitelet",
    "docusaurus",
    "mkdocs",
    "hugo",
    "vitepress",
    "static-html",
    "rag",
}


def now_ts() -> int:
    return int(time.time())


def clean_text(value: Any, limit: int = 20000) -> str:
    return str(value or "").strip()[:limit]


def clean_slug(value: Any) -> str:
    raw = clean_text(value, 160).lower().replace("_", "-")
    slug = SLUG_RE.sub("-", raw).strip("-")
    return slug[:120]


def clean_list(value: Any, *, limit: int = 30, item_limit: int = 80) -> list[str]:
    if not isinstance(value, list):
        return []
    items: list[str] = []
    for item in value:
        cleaned = clean_text(item, item_limit)
        if cleaned and cleaned not in items:
            items.append(cleaned)
    return items[:limit]


def clean_framework_targets(value: Any) -> list[str]:
    return [item for item in clean_list(value, limit=20, item_limit=80) if item in SUPPORTED_TARGETS]


class DocsStore:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS docs_spaces (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  site_id TEXT NOT NULL UNIQUE,
                  name TEXT NOT NULL,
                  description TEXT DEFAULT '',
                  created_at INTEGER NOT NULL,
                  updated_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS docs_documents (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  site_id TEXT NOT NULL,
                  slug TEXT NOT NULL,
                  title TEXT NOT NULL,
                  summary TEXT DEFAULT '',
                  content TEXT NOT NULL,
                  content_format TEXT NOT NULL DEFAULT 'markdown',
                  status TEXT NOT NULL DEFAULT 'draft',
                  visibility TEXT NOT NULL DEFAULT 'public',
                  category TEXT DEFAULT '',
                  tags_json TEXT DEFAULT '[]',
                  version_label TEXT DEFAULT '',
                  locale TEXT DEFAULT 'en',
                  framework_targets_json TEXT DEFAULT '[]',
                  rag_enabled INTEGER NOT NULL DEFAULT 0,
                  created_at INTEGER NOT NULL,
                  updated_at INTEGER NOT NULL,
                  UNIQUE(site_id, slug)
                );

                CREATE TABLE IF NOT EXISTS docs_document_revisions (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  document_id INTEGER NOT NULL,
                  site_id TEXT NOT NULL,
                  slug TEXT NOT NULL,
                  title TEXT NOT NULL,
                  summary TEXT DEFAULT '',
                  content TEXT NOT NULL,
                  content_format TEXT NOT NULL,
                  status TEXT NOT NULL,
                  visibility TEXT NOT NULL,
                  category TEXT DEFAULT '',
                  tags_json TEXT DEFAULT '[]',
                  version_label TEXT DEFAULT '',
                  locale TEXT DEFAULT 'en',
                  framework_targets_json TEXT DEFAULT '[]',
                  rag_enabled INTEGER NOT NULL DEFAULT 0,
                  changed_by TEXT DEFAULT '',
                  created_at INTEGER NOT NULL,
                  FOREIGN KEY(document_id) REFERENCES docs_documents(id)
                );
                """
            )

    def ensure_space(self, site_id: str, name: str = "", description: str = "") -> None:
        ts = now_ts()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO docs_spaces(site_id, name, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(site_id) DO UPDATE SET
                  name=COALESCE(NULLIF(excluded.name, ''), docs_spaces.name),
                  description=COALESCE(NULLIF(excluded.description, ''), docs_spaces.description),
                  updated_at=excluded.updated_at
                """,
                (site_id, name or site_id, description, ts, ts),
            )

    def normalize_doc_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        site_id = clean_text(payload.get("site_id"), 100)
        slug = clean_slug(payload.get("slug"))
        title = clean_text(payload.get("title"), 300)
        content = clean_text(payload.get("content"), 500000)
        if not site_id:
            raise ValueError("site_id is required")
        if not slug:
            raise ValueError("slug is required")
        if not title:
            raise ValueError("title is required")
        if not content:
            raise ValueError("content is required")
        status = clean_text(payload.get("status") or "draft", 40)
        if status not in SUPPORTED_STATUSES:
            status = "draft"
        visibility = clean_text(payload.get("visibility") or "public", 40)
        if visibility not in SUPPORTED_VISIBILITIES:
            visibility = "public"
        content_format = clean_text(payload.get("content_format") or "markdown", 40)
        if content_format not in SUPPORTED_FORMATS:
            content_format = "markdown"
        return {
            "site_id": site_id,
            "slug": slug,
            "title": title,
            "summary": clean_text(payload.get("summary"), 1200),
            "content": content,
            "content_format": content_format,
            "status": status,
            "visibility": visibility,
            "category": clean_text(payload.get("category"), 120),
            "tags": clean_list(payload.get("tags"), limit=30, item_limit=80),
            "version_label": clean_text(payload.get("version_label") or payload.get("version"), 80),
            "locale": self.clean_locale(payload.get("locale"), "en"),
            "framework_targets": clean_framework_targets(payload.get("framework_targets")),
            "rag_enabled": bool(payload.get("rag_enabled", False)),
            "changed_by": clean_text(payload.get("changed_by"), 200),
        }

    def row_to_doc(self, row: sqlite3.Row | None, include_content: bool = True) -> dict[str, Any] | None:
        if row is None:
            return None
        doc = {
            "id": row["id"],
            "site_id": row["site_id"],
            "slug": row["slug"],
            "title": row["title"],
            "summary": row["summary"],
            "content_format": row["content_format"],
            "status": row["status"],
            "visibility": row["visibility"],
            "category": row["category"],
            "tags": json.loads(row["tags_json"] or "[]"),
            "version_label": row["version_label"],
            "locale": row["locale"],
            "framework_targets": json.loads(row["framework_targets_json"] or "[]"),
            "rag_enabled": bool(row["rag_enabled"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        if include_content:
            doc["content"] = row["content"]
        return doc

    def upsert_doc(self, payload: dict[str, Any]) -> dict[str, Any]:
        doc = self.normalize_doc_payload(payload)
        self.ensure_space(doc["site_id"])
        ts = now_ts()
        tags_json = json.dumps(doc["tags"], ensure_ascii=False)
        targets_json = json.dumps(doc["framework_targets"], ensure_ascii=False)
        with self.connect() as conn:
            existing = conn.execute(
                "SELECT * FROM docs_documents WHERE site_id=? AND slug=?",
                (doc["site_id"], doc["slug"]),
            ).fetchone()
            if existing:
                doc_id = existing["id"]
                conn.execute(
                    """
                    UPDATE docs_documents
                    SET title=?, summary=?, content=?, content_format=?, status=?, visibility=?, category=?,
                        tags_json=?, version_label=?, locale=?, framework_targets_json=?, rag_enabled=?, updated_at=?
                    WHERE id=?
                    """,
                    (
                        doc["title"], doc["summary"], doc["content"], doc["content_format"], doc["status"],
                        doc["visibility"], doc["category"], tags_json, doc["version_label"], doc["locale"],
                        targets_json, 1 if doc["rag_enabled"] else 0, ts, doc_id,
                    ),
                )
            else:
                cur = conn.execute(
                    """
                    INSERT INTO docs_documents(site_id, slug, title, summary, content, content_format, status, visibility,
                      category, tags_json, version_label, locale, framework_targets_json, rag_enabled, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        doc["site_id"], doc["slug"], doc["title"], doc["summary"], doc["content"], doc["content_format"],
                        doc["status"], doc["visibility"], doc["category"], tags_json, doc["version_label"], doc["locale"],
                        targets_json, 1 if doc["rag_enabled"] else 0, ts, ts,
                    ),
                )
                doc_id = int(cur.lastrowid)
            conn.execute(
                """
                INSERT INTO docs_document_revisions(document_id, site_id, slug, title, summary, content, content_format,
                  status, visibility, category, tags_json, version_label, locale, framework_targets_json, rag_enabled, changed_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc_id, doc["site_id"], doc["slug"], doc["title"], doc["summary"], doc["content"], doc["content_format"],
                    doc["status"], doc["visibility"], doc["category"], tags_json, doc["version_label"], doc["locale"],
                    targets_json, 1 if doc["rag_enabled"] else 0, doc["changed_by"], ts,
                ),
            )
        return self.get_doc(doc["site_id"], doc["slug"]) or {**doc, "id": doc_id, "created_at": ts, "updated_at": ts}

    def get_doc(self, site_id: str, slug: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM docs_documents WHERE site_id=? AND slug=?",
                (clean_text(site_id, 100), clean_slug(slug)),
            ).fetchone()
        return self.row_to_doc(row, include_content=True)

    def clean_locale(self, value: Any, default: str = "") -> str:
        locale = clean_text(value, 20).lower().replace("_", "-")
        locale = re.sub(r"[^a-z0-9-]+", "", locale)
        return locale or default

    def list_docs(self, site_id: str, q: str = "", status: str = "published", visibility: str = "", locale: str = "") -> list[dict[str, Any]]:
        site_id = clean_text(site_id, 100)
        q = clean_text(q, 200).lower()
        locale = self.clean_locale(locale)
        params: list[Any] = [site_id]
        sql = "SELECT * FROM docs_documents WHERE site_id=?"
        if status:
            sql += " AND status=?"
            params.append(status)
        if visibility:
            sql += " AND visibility=?"
            params.append(visibility)
        if locale:
            sql += " AND locale=?"
            params.append(locale)
        sql += " ORDER BY updated_at DESC, title ASC"
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        docs = [self.row_to_doc(row, include_content=False) for row in rows]
        docs = [doc for doc in docs if doc is not None]
        if q:
            filtered = []
            for doc in docs:
                full = self.get_doc(site_id, doc["slug"]) or doc
                haystack = " ".join([
                    full.get("title", ""), full.get("summary", ""), full.get("content", ""),
                    full.get("category", ""), " ".join(full.get("tags", [])), " ".join(full.get("framework_targets", [])),
                ]).lower()
                if q in haystack:
                    filtered.append(doc)
            docs = filtered
        return docs

    def delete_doc(self, site_id: str, slug: str) -> bool:
        doc = self.get_doc(site_id, slug)
        if not doc:
            return False
        with self.connect() as conn:
            conn.execute("DELETE FROM docs_documents WHERE id=?", (doc["id"],))
        return True

    def list_revisions(self, site_id: str, slug: str) -> list[dict[str, Any]]:
        doc = self.get_doc(site_id, slug)
        if not doc:
            return []
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM docs_document_revisions WHERE document_id=? AND site_id=? ORDER BY created_at DESC, id DESC",
                (doc["id"], clean_text(site_id, 100)),
            ).fetchall()
        revisions = []
        for row in rows:
            revisions.append({
                "id": row["id"],
                "document_id": row["document_id"],
                "site_id": row["site_id"],
                "slug": row["slug"],
                "title": row["title"],
                "summary": row["summary"],
                "content": row["content"],
                "content_format": row["content_format"],
                "status": row["status"],
                "visibility": row["visibility"],
                "category": row["category"],
                "tags": json.loads(row["tags_json"] or "[]"),
                "version_label": row["version_label"],
                "locale": row["locale"],
                "framework_targets": json.loads(row["framework_targets_json"] or "[]"),
                "rag_enabled": bool(row["rag_enabled"]),
                "changed_by": row["changed_by"],
                "created_at": row["created_at"],
            })
        return revisions

    def get_doc_localized(self, site_id: str, slug: str, locale: str = "", fallback_locale: str = "en") -> tuple[dict[str, Any] | None, bool]:
        doc = self.get_doc(site_id, slug)
        requested_locale = self.clean_locale(locale)
        fallback_locale = self.clean_locale(fallback_locale, "en")
        if not doc or not requested_locale:
            return doc, False
        if self.clean_locale(doc.get("locale")) == requested_locale:
            return doc, False
        if fallback_locale and self.clean_locale(doc.get("locale")) == fallback_locale:
            return doc, True
        return None, False

    def list_locales(self, site_id: str) -> list[str]:
        site_id = clean_text(site_id, 100)
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT locale FROM docs_documents WHERE site_id=? AND COALESCE(locale, '') != '' ORDER BY locale ASC",
                (site_id,),
            ).fetchall()
        return [row["locale"] for row in rows]

    def get_space_summary(self, site_id: str) -> dict[str, Any]:
        site_id = clean_text(site_id, 100)
        self.ensure_space(site_id)
        with self.connect() as conn:
            space = conn.execute("SELECT * FROM docs_spaces WHERE site_id=?", (site_id,)).fetchone()
            docs = conn.execute("SELECT status, visibility, category, locale FROM docs_documents WHERE site_id=?", (site_id,)).fetchall()
        status_counts: dict[str, int] = {}
        visibility_counts: dict[str, int] = {}
        locale_counts: dict[str, int] = {}
        categories: list[str] = []
        for row in docs:
            status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
            visibility_counts[row["visibility"]] = visibility_counts.get(row["visibility"], 0) + 1
            locale = row["locale"] or "en"
            locale_counts[locale] = locale_counts.get(locale, 0) + 1
            category = row["category"]
            if category and category not in categories:
                categories.append(category)
        return {
            "site_id": site_id,
            "name": space["name"] if space else site_id,
            "description": space["description"] if space else "",
            "total_docs": len(docs),
            "status_counts": dict(sorted(status_counts.items())),
            "visibility_counts": dict(sorted(visibility_counts.items())),
            "locale_counts": dict(sorted(locale_counts.items())),
            "available_locales": sorted(locale_counts.keys()),
            "categories": sorted(categories),
        }
