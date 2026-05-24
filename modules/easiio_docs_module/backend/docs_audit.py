from __future__ import annotations

import csv
import hashlib
import io
import json
import sqlite3
import re
import time
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

from docs_db import clean_text

APPROVAL_STATUSES = {"draft", "reviewed", "approved", "released", "rejected"}
LOCKING_APPROVAL_STATUSES = {"approved", "released"}


DEFAULT_CHECKLIST = {
    "manual_review": {"label": "Manual review completed", "completed": False, "note": ""},
    "static_files_verified": {"label": "Static files verified", "completed": False, "note": ""},
    "sitelet_upload": {"label": "Sitelet upload completed", "completed": False, "note": ""},
    "wordpress_upload": {"label": "WordPress upload completed", "completed": False, "note": ""},
    "production_publish": {"label": "Production publish approved", "completed": False, "note": ""},
}


class DocsAuditStore:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS docs_deployment_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    deployment_target TEXT NOT NULL,
                    export_target TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    locale TEXT NOT NULL,
                    status TEXT NOT NULL,
                    visibility TEXT NOT NULL,
                    package_path TEXT NOT NULL,
                    package_size INTEGER NOT NULL DEFAULT 0,
                    approved_by TEXT NOT NULL DEFAULT '',
                    document_count INTEGER NOT NULL DEFAULT 0,
                    file_count INTEGER NOT NULL DEFAULT 0,
                    file_paths_json TEXT NOT NULL DEFAULT '[]',
                    manifest_json TEXT NOT NULL DEFAULT '{}',
                    created_at INTEGER NOT NULL
                )
                """
            )
            existing = {row["name"] for row in conn.execute("PRAGMA table_info(docs_deployment_audit)").fetchall()}
            if "checklist_json" not in existing:
                conn.execute("ALTER TABLE docs_deployment_audit ADD COLUMN checklist_json TEXT NOT NULL DEFAULT '{}'")
            if "checklist_updated_by" not in existing:
                conn.execute("ALTER TABLE docs_deployment_audit ADD COLUMN checklist_updated_by TEXT NOT NULL DEFAULT ''")
            if "checklist_updated_at" not in existing:
                conn.execute("ALTER TABLE docs_deployment_audit ADD COLUMN checklist_updated_at INTEGER NOT NULL DEFAULT 0")
            if "approval_status" not in existing:
                conn.execute("ALTER TABLE docs_deployment_audit ADD COLUMN approval_status TEXT NOT NULL DEFAULT 'draft'")
            if "approval_history_json" not in existing:
                conn.execute("ALTER TABLE docs_deployment_audit ADD COLUMN approval_history_json TEXT NOT NULL DEFAULT '[]'")
            if "release_notes_json" not in existing:
                conn.execute("ALTER TABLE docs_deployment_audit ADD COLUMN release_notes_json TEXT NOT NULL DEFAULT '{}'")
            if "package_locked" not in existing:
                conn.execute("ALTER TABLE docs_deployment_audit ADD COLUMN package_locked INTEGER NOT NULL DEFAULT 0")
            if "approval_updated_by" not in existing:
                conn.execute("ALTER TABLE docs_deployment_audit ADD COLUMN approval_updated_by TEXT NOT NULL DEFAULT ''")
            if "approval_updated_at" not in existing:
                conn.execute("ALTER TABLE docs_deployment_audit ADD COLUMN approval_updated_at INTEGER NOT NULL DEFAULT 0")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_docs_deployment_audit_site_created ON docs_deployment_audit(site_id, created_at DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_docs_deployment_audit_target_env ON docs_deployment_audit(deployment_target, environment)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_docs_deployment_audit_locale ON docs_deployment_audit(locale)")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS docs_release_archive (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    audit_record_id INTEGER NOT NULL UNIQUE,
                    site_id TEXT NOT NULL,
                    deployment_target TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    locale TEXT NOT NULL,
                    approval_status TEXT NOT NULL,
                    archive_status TEXT NOT NULL DEFAULT 'archived',
                    attestation_path TEXT NOT NULL,
                    report_path TEXT NOT NULL,
                    package_sha256 TEXT NOT NULL,
                    manifest_sha256 TEXT NOT NULL,
                    handoff_report_sha256 TEXT NOT NULL,
                    attestation_json TEXT NOT NULL DEFAULT '{}',
                    created_by TEXT NOT NULL DEFAULT '',
                    created_at INTEGER NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_docs_release_archive_site_created ON docs_release_archive(site_id, created_at DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_docs_release_archive_env ON docs_release_archive(environment, deployment_target)")

    def record_deployment_package(self, package_result: dict[str, Any]) -> dict[str, Any]:
        manifest = package_result.get("manifest") if isinstance(package_result.get("manifest"), dict) else {}
        site_id = clean_text(package_result.get("site_id") or manifest.get("site_id"), 100)
        if not site_id:
            raise ValueError("site_id is required for deployment audit")
        file_paths = package_result.get("filePaths") if isinstance(package_result.get("filePaths"), list) else []
        created_at = int(time.time())
        values = {
            "site_id": site_id,
            "event_type": "deployment_package_created",
            "deployment_target": clean_text(package_result.get("deploymentTarget") or manifest.get("deploymentTarget"), 80),
            "export_target": clean_text(package_result.get("exportTarget") or "", 80),
            "environment": clean_text(package_result.get("environment") or manifest.get("environment"), 40),
            "locale": clean_text(package_result.get("locale") or manifest.get("locale") or "all", 40),
            "status": clean_text(manifest.get("status") or "published", 40),
            "visibility": clean_text(manifest.get("visibility") or "public", 40),
            "package_path": clean_text(package_result.get("packagePath"), 500),
            "package_size": int(package_result.get("packageSize") or 0),
            "approved_by": clean_text(package_result.get("approvedBy"), 120),
            "document_count": int(package_result.get("documentCount") or 0),
            "file_count": int(package_result.get("fileCount") or 0),
            "file_paths_json": json.dumps(file_paths, ensure_ascii=False),
            "manifest_json": json.dumps(manifest, ensure_ascii=False, sort_keys=True),
            "checklist_json": json.dumps(DEFAULT_CHECKLIST, ensure_ascii=False, sort_keys=True),
            "checklist_updated_by": "",
            "checklist_updated_at": 0,
            "approval_status": "draft",
            "approval_history_json": "[]",
            "release_notes_json": "{}",
            "package_locked": 0,
            "approval_updated_by": "",
            "approval_updated_at": 0,
            "created_at": created_at,
        }
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO docs_deployment_audit (
                    site_id, event_type, deployment_target, export_target, environment, locale,
                    status, visibility, package_path, package_size, approved_by, document_count,
                    file_count, file_paths_json, manifest_json, checklist_json, checklist_updated_by,
                    checklist_updated_at, approval_status, approval_history_json, release_notes_json,
                    package_locked, approval_updated_by, approval_updated_at, created_at
                ) VALUES (
                    :site_id, :event_type, :deployment_target, :export_target, :environment, :locale,
                    :status, :visibility, :package_path, :package_size, :approved_by, :document_count,
                    :file_count, :file_paths_json, :manifest_json, :checklist_json, :checklist_updated_by,
                    :checklist_updated_at, :approval_status, :approval_history_json, :release_notes_json,
                    :package_locked, :approval_updated_by, :approval_updated_at, :created_at
                )
                """,
                values,
            )
            record_id = int(cur.lastrowid)
        return self._record_from_values({**values, "id": record_id})

    def get_deployment_package_detail(self, record_id: int | str) -> dict[str, Any] | None:
        try:
            rid = int(record_id)
        except (TypeError, ValueError):
            return None
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM docs_deployment_audit WHERE id = ?", (rid,)).fetchone()
        return self._record_from_row(row) if row else None

    def update_deployment_checklist(self, record_id: int | str, checklist_updates: dict[str, Any], *, updated_by: str = "") -> dict[str, Any] | None:
        record = self.get_deployment_package_detail(record_id)
        if not record:
            return None
        if record.get("packageLocked"):
            raise RuntimeError("deployment package is locked after approval/release")
        checklist = _normalise_checklist(record.get("checklist") or DEFAULT_CHECKLIST)
        if isinstance(checklist_updates, dict):
            for key, value in checklist_updates.items():
                safe_key = clean_text(key, 80)
                if safe_key not in checklist:
                    checklist[safe_key] = {"label": safe_key.replace("_", " ").title(), "completed": False, "note": ""}
                if isinstance(value, dict):
                    if "completed" in value:
                        checklist[safe_key]["completed"] = bool(value.get("completed"))
                    if "note" in value:
                        checklist[safe_key]["note"] = clean_text(value.get("note"), 300)
                    if "label" in value:
                        checklist[safe_key]["label"] = clean_text(value.get("label"), 160) or checklist[safe_key].get("label", safe_key)
                else:
                    checklist[safe_key]["completed"] = bool(value)
        updated_at = int(time.time())
        clean_by = clean_text(updated_by, 120)
        with self.connect() as conn:
            conn.execute(
                "UPDATE docs_deployment_audit SET checklist_json = ?, checklist_updated_by = ?, checklist_updated_at = ? WHERE id = ?",
                (json.dumps(checklist, ensure_ascii=False, sort_keys=True), clean_by, updated_at, int(record["id"])),
            )
        return self.get_deployment_package_detail(record["id"])


    def update_deployment_approval(self, record_id: int | str, status: str, *, actor: str = "", note: str = "") -> dict[str, Any] | None:
        record = self.get_deployment_package_detail(record_id)
        if not record:
            return None
        clean_status = clean_text(status, 40).lower() or "reviewed"
        if clean_status not in APPROVAL_STATUSES:
            raise ValueError(f"unsupported approval status: {clean_status}")
        now = int(time.time())
        clean_actor = clean_text(actor, 120) or "operator"
        clean_note = clean_text(note, 500)
        history = record.get("approvalHistory") if isinstance(record.get("approvalHistory"), list) else []
        event = {"status": clean_status, "actor": clean_actor, "note": clean_note, "created_at": now}
        history.append(event)
        locked = clean_status in LOCKING_APPROVAL_STATUSES or bool(record.get("packageLocked"))
        release_notes = _build_release_notes(record, clean_status, history)
        with self.connect() as conn:
            conn.execute(
                "UPDATE docs_deployment_audit SET approval_status = ?, approval_history_json = ?, release_notes_json = ?, package_locked = ?, approval_updated_by = ?, approval_updated_at = ? WHERE id = ?",
                (clean_status, json.dumps(history, ensure_ascii=False, sort_keys=True), json.dumps(release_notes, ensure_ascii=False, sort_keys=True), 1 if locked else 0, clean_actor, now, int(record["id"])),
            )
        return self.get_deployment_package_detail(record["id"])

    def record_release_archive(self, record: dict[str, Any], attestation: dict[str, Any], *, archive_dir: Path, report_markdown: str, created_by: str = "") -> dict[str, Any]:
        archive_dir.mkdir(parents=True, exist_ok=True)
        attestation_path = archive_dir / "release-attestation.json"
        report_path = archive_dir / "operator-handoff-report.md"
        attestation_path.write_text(json.dumps(attestation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        report_path.write_text(report_markdown, encoding="utf-8")
        now = int(time.time())
        values = {
            "audit_record_id": int(record.get("id") or 0),
            "site_id": clean_text(record.get("site_id"), 100),
            "deployment_target": clean_text(record.get("deploymentTarget"), 80),
            "environment": clean_text(record.get("environment"), 40),
            "locale": clean_text(record.get("locale") or "all", 40),
            "approval_status": clean_text(record.get("approvalStatus") or "draft", 40),
            "archive_status": "archived",
            "attestation_path": str(attestation_path),
            "report_path": str(report_path),
            "package_sha256": attestation.get("packageSha256", ""),
            "manifest_sha256": attestation.get("manifestSha256", ""),
            "handoff_report_sha256": attestation.get("handoffReportSha256", ""),
            "attestation_json": json.dumps(attestation, ensure_ascii=False, sort_keys=True),
            "created_by": clean_text(created_by, 120),
            "created_at": now,
        }
        with self.connect() as conn:
            existing = conn.execute("SELECT id FROM docs_release_archive WHERE audit_record_id = ?", (values["audit_record_id"],)).fetchone()
            if existing:
                conn.execute(
                    """
                    UPDATE docs_release_archive SET site_id=:site_id, deployment_target=:deployment_target,
                    environment=:environment, locale=:locale, approval_status=:approval_status,
                    archive_status=:archive_status, attestation_path=:attestation_path, report_path=:report_path,
                    package_sha256=:package_sha256, manifest_sha256=:manifest_sha256,
                    handoff_report_sha256=:handoff_report_sha256, attestation_json=:attestation_json,
                    created_by=:created_by, created_at=:created_at WHERE audit_record_id=:audit_record_id
                    """,
                    values,
                )
                archive_id = int(existing["id"])
            else:
                cur = conn.execute(
                    """
                    INSERT INTO docs_release_archive (
                      audit_record_id, site_id, deployment_target, environment, locale, approval_status,
                      archive_status, attestation_path, report_path, package_sha256, manifest_sha256,
                      handoff_report_sha256, attestation_json, created_by, created_at
                    ) VALUES (
                      :audit_record_id, :site_id, :deployment_target, :environment, :locale, :approval_status,
                      :archive_status, :attestation_path, :report_path, :package_sha256, :manifest_sha256,
                      :handoff_report_sha256, :attestation_json, :created_by, :created_at
                    )
                    """,
                    values,
                )
                archive_id = int(cur.lastrowid)
        return self.get_release_archive_by_audit_id(values["audit_record_id"]) or {"id": archive_id, **values}

    def _archive_from_row(self, row: sqlite3.Row | None) -> dict[str, Any] | None:
        if not row:
            return None
        values = dict(row)
        try:
            attestation = json.loads(values.get("attestation_json") or "{}")
        except Exception:
            attestation = {}
        return {
            "id": int(values.get("id") or 0),
            "auditRecordId": int(values.get("audit_record_id") or 0),
            "site_id": values.get("site_id") or "",
            "deploymentTarget": values.get("deployment_target") or "",
            "environment": values.get("environment") or "",
            "locale": values.get("locale") or "all",
            "approvalStatus": values.get("approval_status") or "draft",
            "archiveStatus": values.get("archive_status") or "archived",
            "attestationPath": values.get("attestation_path") or "",
            "reportPath": values.get("report_path") or "",
            "packageSha256": values.get("package_sha256") or "",
            "manifestSha256": values.get("manifest_sha256") or "",
            "handoffReportSha256": values.get("handoff_report_sha256") or "",
            "attestation": attestation,
            "createdBy": values.get("created_by") or "",
            "created_at": int(values.get("created_at") or 0),
        }

    def get_release_archive_by_audit_id(self, audit_record_id: int | str) -> dict[str, Any] | None:
        try:
            rid = int(audit_record_id)
        except (TypeError, ValueError):
            return None
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM docs_release_archive WHERE audit_record_id = ?", (rid,)).fetchone()
        return self._archive_from_row(row)

    def list_release_archive(self, site_id: str = "", *, limit: int = 25, target: str = "", environment: str = "", locale: str = "") -> list[dict[str, Any]]:
        clauses: list[str] = []
        args: list[Any] = []
        if clean_text(site_id, 100):
            clauses.append("site_id = ?")
            args.append(clean_text(site_id, 100))
        if clean_text(target, 80):
            clauses.append("deployment_target = ?")
            args.append(clean_text(target, 80))
        if clean_text(environment, 40):
            clauses.append("environment = ?")
            args.append(clean_text(environment, 40))
        if clean_text(locale, 40):
            clauses.append("locale = ?")
            args.append(clean_text(locale, 40))
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        args.append(_limit(limit, 25, 500))
        with self.connect() as conn:
            rows = conn.execute(f"SELECT * FROM docs_release_archive{where} ORDER BY created_at DESC, id DESC LIMIT ?", args).fetchall()
        return [item for item in (self._archive_from_row(row) for row in rows) if item]


    def _history_query(self, site_id: str = "", *, target: str = "", environment: str = "", locale: str = "") -> tuple[str, list[Any]]:
        clean_site = clean_text(site_id, 100)
        clean_target = clean_text(target, 80)
        clean_env = clean_text(environment, 40)
        clean_locale = clean_text(locale, 40)
        clauses: list[str] = []
        args: list[Any] = []
        if clean_site:
            clauses.append("site_id = ?")
            args.append(clean_site)
        if clean_target:
            clauses.append("deployment_target = ?")
            args.append(clean_target)
        if clean_env:
            clauses.append("environment = ?")
            args.append(clean_env)
        if clean_locale:
            clauses.append("locale = ?")
            args.append(clean_locale)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        return where, args

    def filter_deployment_history(self, site_id: str = "", *, limit: int = 25, target: str = "", environment: str = "", locale: str = "") -> list[dict[str, Any]]:
        limit = max(1, min(int(limit or 25), 500))
        where, args = self._history_query(site_id, target=target, environment=environment, locale=locale)
        sql = f"SELECT * FROM docs_deployment_audit{where} ORDER BY created_at DESC, id DESC LIMIT ?"
        args.append(limit)
        with self.connect() as conn:
            rows = conn.execute(sql, args).fetchall()
        return [self._record_from_row(row) for row in rows]

    def list_deployment_history(self, site_id: str = "", *, limit: int = 25, target: str = "", environment: str = "", locale: str = "") -> list[dict[str, Any]]:
        return self.filter_deployment_history(site_id, limit=limit, target=target, environment=environment, locale=locale)

    def summarize_deployment_history(self, site_id: str = "", *, limit: int = 10, target: str = "", environment: str = "", locale: str = "") -> dict[str, Any]:
        where, args = self._history_query(site_id, target=target, environment=environment, locale=locale)
        with self.connect() as conn:
            rows = conn.execute(f"SELECT * FROM docs_deployment_audit{where} ORDER BY created_at DESC, id DESC", args).fetchall()
        records = [self._record_from_row(row) for row in rows]
        targets = Counter(r["deploymentTarget"] for r in records if r.get("deploymentTarget"))
        envs = Counter(r["environment"] for r in records if r.get("environment"))
        locales = Counter(r["locale"] for r in records if r.get("locale"))
        total_size = sum(int(r.get("packageSize") or 0) for r in records)
        return {
            "totals": {
                "count": len(records),
                "packageSize": total_size,
                "totalPackageSize": total_size,
                "documentCount": sum(int(r.get("documentCount") or 0) for r in records),
                "fileCount": sum(int(r.get("fileCount") or 0) for r in records),
            },
            "counts": {"targets": dict(targets), "environments": dict(envs), "locales": dict(locales)},
            "latest": records[:max(1, min(int(limit or 10), 50))],
        }

    def _record_from_row(self, row: sqlite3.Row) -> dict[str, Any]:
        return self._record_from_values(dict(row))

    def _record_from_values(self, values: dict[str, Any]) -> dict[str, Any]:
        def loads(value: Any, fallback: Any) -> Any:
            try:
                return json.loads(value or "")
            except Exception:
                return fallback
        checklist = _normalise_checklist(loads(values.get("checklist_json"), DEFAULT_CHECKLIST))
        return {
            "id": int(values.get("id") or 0),
            "site_id": values.get("site_id") or "",
            "event_type": values.get("event_type") or "deployment_package_created",
            "deploymentTarget": values.get("deployment_target") or "",
            "exportTarget": values.get("export_target") or "",
            "environment": values.get("environment") or "",
            "locale": values.get("locale") or "all",
            "status": values.get("status") or "published",
            "visibility": values.get("visibility") or "public",
            "packagePath": values.get("package_path") or "",
            "packageSize": int(values.get("package_size") or 0),
            "approvedBy": values.get("approved_by") or "",
            "documentCount": int(values.get("document_count") or 0),
            "fileCount": int(values.get("file_count") or 0),
            "filePaths": loads(values.get("file_paths_json"), []),
            "manifest": loads(values.get("manifest_json"), {}),
            "checklist": checklist,
            "checklistUpdatedBy": values.get("checklist_updated_by") or "",
            "checklistUpdatedAt": int(values.get("checklist_updated_at") or 0),
            "approvalStatus": values.get("approval_status") or "draft",
            "approvalHistory": loads(values.get("approval_history_json"), []),
            "releaseNotes": loads(values.get("release_notes_json"), {}),
            "packageLocked": bool(values.get("package_locked") or 0),
            "approvalUpdatedBy": values.get("approval_updated_by") or "",
            "approvalUpdatedAt": int(values.get("approval_updated_at") or 0),
            "created_at": int(values.get("created_at") or 0),
        }


def _normalise_checklist(value: Any) -> dict[str, dict[str, Any]]:
    merged = json.loads(json.dumps(DEFAULT_CHECKLIST))
    if not isinstance(value, dict):
        return merged
    for key, item in value.items():
        safe_key = clean_text(key, 80)
        if not safe_key:
            continue
        current = merged.get(safe_key, {"label": safe_key.replace("_", " ").title(), "completed": False, "note": ""})
        if isinstance(item, dict):
            current["label"] = clean_text(item.get("label") or current.get("label") or safe_key, 160)
            current["completed"] = bool(item.get("completed"))
            current["note"] = clean_text(item.get("note") or "", 300)
        else:
            current["completed"] = bool(item)
        merged[safe_key] = current
    return merged


def _limit(value: int | str | None, default: int = 25, maximum: int = 500) -> int:
    try:
        parsed = int(value or default)
    except (TypeError, ValueError):
        parsed = default
    return max(1, min(parsed, maximum))


def _filters(site_id: str = "", *, target: str = "", environment: str = "", locale: str = "", limit: int | str | None = 25) -> dict[str, Any]:
    return {"target": clean_text(target, 80), "environment": clean_text(environment, 40), "locale": clean_text(locale, 40), "limit": _limit(limit)}


def build_deployment_history_response(audit_store: DocsAuditStore, *, site_id: str = "", limit: int = 25, target: str = "", environment: str = "", locale: str = "") -> dict[str, Any]:
    history = audit_store.list_deployment_history(site_id, limit=limit, target=target, environment=environment, locale=locale)
    return {"ok": True, "exportType": "easiio-docs-deployment-history", "site_id": clean_text(site_id, 100), "count": len(history), "history": history, "filters": _filters(site_id, target=target, environment=environment, locale=locale, limit=limit)}


def build_deployment_summary_response(audit_store: DocsAuditStore, *, site_id: str = "", limit: int = 10, target: str = "", environment: str = "", locale: str = "") -> dict[str, Any]:
    summary = audit_store.summarize_deployment_history(site_id, limit=limit, target=target, environment=environment, locale=locale)
    return {"ok": True, "exportType": "easiio-docs-deployment-summary", "site_id": clean_text(site_id, 100), "filters": _filters(site_id, target=target, environment=environment, locale=locale, limit=limit), **summary}


def deployment_history_to_csv(history: list[dict[str, Any]]) -> str:
    output = io.StringIO()
    fieldnames = ["id", "site_id", "event_type", "deploymentTarget", "environment", "locale", "packagePath", "packageSize", "approvedBy", "created_at", "exportTarget", "status", "visibility", "documentCount", "fileCount"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in history:
        safe_row = {key: row.get(key, "") for key in fieldnames}
        writer.writerow(safe_row)
    return output.getvalue()


def build_deployment_history_csv_response(audit_store: DocsAuditStore, *, site_id: str = "", limit: int = 500, target: str = "", environment: str = "", locale: str = "") -> str:
    history = audit_store.list_deployment_history(site_id, limit=_limit(limit, 500, 1000), target=target, environment=environment, locale=locale)
    return deployment_history_to_csv(history)


def _manifest_files(record: dict[str, Any]) -> list[str]:
    files = record.get("filePaths") if isinstance(record.get("filePaths"), list) else []
    return [str(item) for item in files]


def build_deployment_package_detail_response(audit_store: DocsAuditStore, *, record_id: int | str) -> dict[str, Any]:
    record = audit_store.get_deployment_package_detail(record_id)
    if not record:
        return {"ok": False, "error": "deployment package audit record not found", "notFound": True}
    package_path = Path(record.get("packagePath") or "")
    exists = package_path.exists() and package_path.is_file()
    return {
        "ok": True,
        "exportType": "easiio-docs-deployment-package-detail",
        "package": record,
        "packageExists": exists,
        "packageFileName": package_path.name,
        "manifest": record.get("manifest") or {},
        "manifestFiles": _manifest_files(record),
        "checklist": record.get("checklist") or _normalise_checklist({}),
        "checklistUpdatedBy": record.get("checklistUpdatedBy") or "",
        "checklistUpdatedAt": record.get("checklistUpdatedAt") or 0,
        "approvalStatus": record.get("approvalStatus") or "draft",
        "approvalHistory": record.get("approvalHistory") or [],
        "releaseNotes": record.get("releaseNotes") or {},
        "packageLocked": bool(record.get("packageLocked")),
    }


def build_deployment_package_download_response(audit_store: DocsAuditStore, *, record_id: int | str) -> dict[str, Any]:
    detail = build_deployment_package_detail_response(audit_store, record_id=record_id)
    if not detail.get("ok"):
        return detail
    record = detail["package"]
    package_path = Path(record.get("packagePath") or "")
    if not package_path.exists() or not package_path.is_file() or package_path.suffix.lower() != ".zip":
        return {"ok": False, "error": "deployment package ZIP is not available locally", "missingPackage": True}
    return {"ok": True, "path": package_path, "fileName": package_path.name, "body": package_path.read_bytes(), "package": record}


def build_deployment_package_comparison_response(audit_store: DocsAuditStore, *, left_id: int | str, right_id: int | str) -> dict[str, Any]:
    left = audit_store.get_deployment_package_detail(left_id)
    right = audit_store.get_deployment_package_detail(right_id)
    if not left or not right:
        return {"ok": False, "error": "both deployment package audit records are required", "notFound": True}
    left_files = set(_manifest_files(left))
    right_files = set(_manifest_files(right))
    differences = {
        "targetChanged": left.get("deploymentTarget") != right.get("deploymentTarget"),
        "environmentChanged": left.get("environment") != right.get("environment"),
        "localeChanged": left.get("locale") != right.get("locale"),
        "documentCountChanged": left.get("documentCount") != right.get("documentCount"),
        "fileCountChanged": left.get("fileCount") != right.get("fileCount"),
        "packageSizeChanged": left.get("packageSize") != right.get("packageSize"),
    }
    return {
        "ok": True,
        "exportType": "easiio-docs-deployment-package-comparison",
        "left": {"id": left.get("id"), "deploymentTarget": left.get("deploymentTarget"), "environment": left.get("environment"), "locale": left.get("locale"), "packagePath": left.get("packagePath"), "packageSize": left.get("packageSize"), "documentCount": left.get("documentCount"), "fileCount": left.get("fileCount")},
        "right": {"id": right.get("id"), "deploymentTarget": right.get("deploymentTarget"), "environment": right.get("environment"), "locale": right.get("locale"), "packagePath": right.get("packagePath"), "packageSize": right.get("packageSize"), "documentCount": right.get("documentCount"), "fileCount": right.get("fileCount")},
        "differences": differences,
        "fileDiff": {"onlyInLeft": sorted(left_files - right_files), "onlyInRight": sorted(right_files - left_files), "shared": sorted(left_files & right_files)},
        "manifestDiff": {"leftManifest": left.get("manifest") or {}, "rightManifest": right.get("manifest") or {}},
    }


def build_deployment_checklist_response(audit_store: DocsAuditStore, payload: dict[str, Any]) -> dict[str, Any]:
    record_id = payload.get("id") or payload.get("record_id") or payload.get("auditRecordId")
    try:
        updated = audit_store.update_deployment_checklist(record_id, payload.get("checklist") if isinstance(payload.get("checklist"), dict) else {}, updated_by=payload.get("updatedBy") or payload.get("approvedBy") or "")
    except RuntimeError as exc:
        return {"ok": False, "error": str(exc), "packageLocked": True}
    if not updated:
        return {"ok": False, "error": "deployment package audit record not found", "notFound": True}
    return {"ok": True, "exportType": "easiio-docs-deployment-checklist", "id": updated.get("id"), "checklist": updated.get("checklist") or {}, "checklistUpdatedBy": updated.get("checklistUpdatedBy") or "", "checklistUpdatedAt": updated.get("checklistUpdatedAt") or 0, "package": updated}


def _zip_doc_titles(record: dict[str, Any]) -> list[str]:
    path = Path(record.get("packagePath") or "")
    titles: list[str] = []
    if not path.exists() or not path.is_file() or path.suffix.lower() != ".zip":
        return titles
    try:
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if not name.lower().endswith((".html", ".md", ".mdx")):
                    continue
                try:
                    text = archive.read(name).decode("utf-8", errors="ignore")[:20000]
                except Exception:
                    continue
                match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.I | re.S) or re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S) or re.search(r"^#\s+(.+)$", text, re.M)
                if match:
                    title = re.sub(r"<[^>]+>", "", match.group(1)).strip()
                    if title and title not in titles:
                        titles.append(clean_text(title, 180))
    except Exception:
        return titles
    return titles


def _build_release_notes(record: dict[str, Any], status: str, history: list[dict[str, Any]]) -> dict[str, Any]:
    titles = _zip_doc_titles(record)
    manifest = record.get("manifest") if isinstance(record.get("manifest"), dict) else {}
    heading = f"Release notes for {record.get('site_id', '')} deployment package #{record.get('id', '')}"
    lines = [f"# {heading}", "", f"- Approval status: {status}", f"- Deployment target: {record.get('deploymentTarget', '')}", f"- Environment: {record.get('environment', '')}", f"- Locale: {record.get('locale', 'all')}", f"- Documents: {record.get('documentCount', 0)}", f"- Files: {record.get('fileCount', 0)}"]
    if titles:
        lines += ["", "## Included docs"] + [f"- {title}" for title in titles]
    if history:
        lines += ["", "## Approval history"] + [f"- {item.get('status')} by {item.get('actor')} — {item.get('note', '')}" for item in history]
    return {"title": heading, "markdown": "\n".join(lines).strip() + "\n", "docTitles": titles, "manifest": manifest}


def build_deployment_approval_response(audit_store: DocsAuditStore, payload: dict[str, Any]) -> dict[str, Any]:
    record_id = payload.get("id") or payload.get("record_id") or payload.get("auditRecordId")
    updated = audit_store.update_deployment_approval(record_id, payload.get("status") or payload.get("approvalStatus") or "reviewed", actor=payload.get("actor") or payload.get("approvedBy") or payload.get("updatedBy") or "", note=payload.get("note") or "")
    if not updated:
        return {"ok": False, "error": "deployment package audit record not found", "notFound": True}
    return {"ok": True, "exportType": "easiio-docs-deployment-approval", "id": updated.get("id"), "approvalStatus": updated.get("approvalStatus"), "packageLocked": bool(updated.get("packageLocked")), "approvalHistory": updated.get("approvalHistory") or [], "releaseNotes": updated.get("releaseNotes") or {}, "package": updated}


def build_deployment_approval_history_response(audit_store: DocsAuditStore, *, record_id: int | str) -> dict[str, Any]:
    record = audit_store.get_deployment_package_detail(record_id)
    if not record:
        return {"ok": False, "error": "deployment package audit record not found", "notFound": True}
    return {"ok": True, "exportType": "easiio-docs-deployment-approval-history", "id": record.get("id"), "approvalStatus": record.get("approvalStatus") or "draft", "packageLocked": bool(record.get("packageLocked")), "approvalHistory": record.get("approvalHistory") or [], "package": record}


def build_deployment_release_notes_response(audit_store: DocsAuditStore, *, record_id: int | str) -> dict[str, Any]:
    record = audit_store.get_deployment_package_detail(record_id)
    if not record:
        return {"ok": False, "error": "deployment package audit record not found", "notFound": True}
    notes = record.get("releaseNotes") if isinstance(record.get("releaseNotes"), dict) and record.get("releaseNotes") else _build_release_notes(record, record.get("approvalStatus") or "draft", record.get("approvalHistory") or [])
    return {"ok": True, "exportType": "easiio-docs-deployment-release-notes", "id": record.get("id"), "approvalStatus": record.get("approvalStatus") or "draft", "packageLocked": bool(record.get("packageLocked")), "releaseNotes": notes, "package": record}



def calculate_deployment_readiness(record: dict[str, Any]) -> dict[str, Any]:
    """Return a local-only readiness score for operator handoff."""
    checklist = _normalise_checklist(record.get("checklist") or {})
    total = max(1, len(checklist))
    completed = sum(1 for item in checklist.values() if item.get("completed"))
    checklist_score = int(round((completed / total) * 60))
    approval_status = clean_text(record.get("approvalStatus") or "draft", 40).lower() or "draft"
    approval_score = 30 if approval_status in {"approved", "released"} else (15 if approval_status == "reviewed" else 0)
    package_path = Path(record.get("packagePath") or "")
    package_exists = package_path.exists() and package_path.is_file()
    package_score = 10 if package_exists else 0
    score = min(100, checklist_score + approval_score + package_score)
    missing = [key for key, item in checklist.items() if not item.get("completed")]
    ready = score >= 80 and approval_status in {"approved", "released"} and package_exists and not missing
    if approval_status not in {"approved", "released"}:
        missing.append("approval_status")
    if not package_exists:
        missing.append("local_package_zip")
    return {
        "score": score,
        "checklistCompleted": completed,
        "checklistTotal": total,
        "approvalStatus": approval_status,
        "packageExists": package_exists,
        "missing": sorted(set(missing)),
        "readyForOperatorHandoff": bool(ready),
        "label": "ready" if ready else ("review" if score >= 50 else "blocked"),
    }


def _release_record(record: dict[str, Any]) -> dict[str, Any]:
    readiness = calculate_deployment_readiness(record)
    return {
        "id": record.get("id"),
        "site_id": record.get("site_id"),
        "deploymentTarget": record.get("deploymentTarget"),
        "environment": record.get("environment"),
        "locale": record.get("locale"),
        "approvalStatus": record.get("approvalStatus") or "draft",
        "packageLocked": bool(record.get("packageLocked")),
        "packagePath": record.get("packagePath"),
        "packageSize": record.get("packageSize"),
        "documentCount": record.get("documentCount"),
        "fileCount": record.get("fileCount"),
        "created_at": record.get("created_at"),
        "approvalUpdatedBy": record.get("approvalUpdatedBy"),
        "approvalUpdatedAt": record.get("approvalUpdatedAt"),
        "readiness": readiness,
        "releaseNotes": record.get("releaseNotes") or {},
    }


def build_deployment_release_dashboard_response(audit_store: DocsAuditStore, *, site_id: str = "", limit: int = 25, target: str = "", environment: str = "", locale: str = "", approval_status: str = "") -> dict[str, Any]:
    limit_value = _limit(limit, 25, 500)
    history = audit_store.list_deployment_history(site_id, limit=500, target=target, environment=environment, locale=locale)
    clean_status = clean_text(approval_status, 40).lower()
    if clean_status:
        history = [record for record in history if (record.get("approvalStatus") or "draft") == clean_status]
    releases = [_release_record(record) for record in history[:limit_value]]
    status_counts = Counter((record.get("approvalStatus") or "draft") for record in history)
    readiness_counts = Counter(item["readiness"]["label"] for item in [_release_record(record) for record in history])
    release_queue = [item for item in releases if item["approvalStatus"] in {"draft", "reviewed", "approved"} and item["approvalStatus"] != "released"]
    ready_count = sum(1 for item in releases if item["readiness"].get("readyForOperatorHandoff"))
    return {
        "ok": True,
        "exportType": "easiio-docs-release-dashboard",
        "site_id": clean_text(site_id, 100),
        "filters": {**_filters(site_id, target=target, environment=environment, locale=locale, limit=limit_value), "approvalStatus": clean_status},
        "totals": {
            "count": len(history),
            "draft": int(status_counts.get("draft", 0)),
            "reviewed": int(status_counts.get("reviewed", 0)),
            "approved": int(status_counts.get("approved", 0)),
            "released": int(status_counts.get("released", 0)),
            "rejected": int(status_counts.get("rejected", 0)),
            "readyForOperatorHandoff": ready_count,
        },
        "counts": {"approvalStatus": dict(status_counts), "readiness": dict(readiness_counts)},
        "releases": releases,
        "releaseQueue": release_queue,
    }


def _handoff_markdown(record: dict[str, Any], readiness: dict[str, Any], notes: dict[str, Any]) -> str:
    checklist = _normalise_checklist(record.get("checklist") or {})
    lines = [
        f"# Operator Handoff Report — Package #{record.get('id')}",
        "",
        f"- Site ID: {record.get('site_id', '')}",
        f"- Target: {record.get('deploymentTarget', '')}",
        f"- Environment: {record.get('environment', '')}",
        f"- Locale: {record.get('locale', 'all')}",
        f"- Approval status: {record.get('approvalStatus', 'draft')}",
        f"- Readiness score: {readiness.get('score', 0)}/100",
        f"- Ready for operator handoff: {'yes' if readiness.get('readyForOperatorHandoff') else 'no'}",
        "",
        "## Checklist",
    ]
    for key, item in checklist.items():
        lines.append(f"- [{'x' if item.get('completed') else ' '}] {item.get('label') or key}: {item.get('note') or ''}")
    missing = readiness.get("missing") or []
    if missing:
        lines += ["", "## Missing readiness items"] + [f"- {item}" for item in missing]
    if notes.get("markdown"):
        lines += ["", "## Release notes", "", notes.get("markdown", "").strip()]
    return "\n".join(lines).strip() + "\n"


def build_deployment_operator_handoff_report_response(audit_store: DocsAuditStore, *, record_id: int | str) -> dict[str, Any]:
    record = audit_store.get_deployment_package_detail(record_id)
    if not record:
        return {"ok": False, "error": "deployment package audit record not found", "notFound": True}
    readiness = calculate_deployment_readiness(record)
    notes = record.get("releaseNotes") if isinstance(record.get("releaseNotes"), dict) and record.get("releaseNotes") else _build_release_notes(record, record.get("approvalStatus") or "draft", record.get("approvalHistory") or [])
    markdown = _handoff_markdown(record, readiness, notes)
    return {
        "ok": True,
        "exportType": "easiio-docs-operator-handoff-report",
        "id": record.get("id"),
        "package": record,
        "readiness": readiness,
        "releaseNotes": notes,
        "markdown": markdown,
    }



def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_json(value: Any) -> str:
    return _sha256_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8"))


def _safe_archive_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "-", clean_text(value, 120)).strip("-._")
    return slug or "site"


def _release_archive_root() -> Path:
    return Path(__file__).resolve().parents[1] / "dist" / "easiio-docs-release-archive"


def _build_release_attestation(record: dict[str, Any], report_markdown: str, readiness: dict[str, Any]) -> dict[str, Any]:
    package_path = Path(record.get("packagePath") or "")
    package_bytes = package_path.read_bytes() if package_path.exists() and package_path.is_file() else b""
    manifest = record.get("manifest") if isinstance(record.get("manifest"), dict) else {}
    file_hashes = []
    if package_path.exists() and package_path.is_file() and package_path.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(package_path) as archive:
                for name in sorted(archive.namelist()):
                    if name.endswith("/"):
                        continue
                    file_hashes.append({"path": name, "sha256": _sha256_bytes(archive.read(name)), "size": len(archive.read(name))})
        except Exception:
            file_hashes = []
    return {
        "attestationType": "easiio-docs-release-attestation",
        "version": "1.0",
        "auditRecordId": int(record.get("id") or 0),
        "site_id": record.get("site_id") or "",
        "deploymentTarget": record.get("deploymentTarget") or "",
        "environment": record.get("environment") or "",
        "locale": record.get("locale") or "all",
        "approvalStatus": record.get("approvalStatus") or "draft",
        "packageLocked": bool(record.get("packageLocked")),
        "packagePath": package_path.name,
        "packageSize": int(record.get("packageSize") or 0),
        "packageSha256": _sha256_bytes(package_bytes),
        "manifestSha256": _sha256_json(manifest),
        "handoffReportSha256": _sha256_bytes(report_markdown.encode("utf-8")),
        "releaseNotesSha256": _sha256_json(record.get("releaseNotes") or {}),
        "readiness": readiness,
        "fileHashes": file_hashes,
        "createdAt": int(time.time()),
    }


def build_release_archive_response(audit_store: DocsAuditStore, payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("confirmArchiveRelease") is not True:
        return {"ok": False, "error": "confirmArchiveRelease is required before archiving release attestation", "requiresArchiveConfirmation": True, "archiveBlocked": True}
    record_id = payload.get("id") or payload.get("record_id") or payload.get("auditRecordId")
    record = audit_store.get_deployment_package_detail(record_id)
    if not record:
        return {"ok": False, "error": "deployment package audit record not found", "notFound": True}
    readiness = calculate_deployment_readiness(record)
    if not readiness.get("readyForOperatorHandoff"):
        return {"ok": False, "error": "release package is not ready for archive", "readiness": readiness, "archiveBlocked": True}
    report = build_deployment_operator_handoff_report_response(audit_store, record_id=record_id)
    markdown = report.get("markdown") or ""
    attestation = _build_release_attestation(record, markdown, readiness)
    root = _release_archive_root() / _safe_archive_slug(record.get("site_id") or "site") / f"package-{int(record.get('id') or 0)}"
    archive = audit_store.record_release_archive(record, attestation, archive_dir=root, report_markdown=markdown, created_by=payload.get("createdBy") or payload.get("approvedBy") or payload.get("actor") or "")
    return {"ok": True, "exportType": "easiio-docs-release-archive", "archive": archive, "attestation": attestation, "reportMarkdown": markdown, "readiness": readiness}


def build_release_archive_index_response(audit_store: DocsAuditStore, *, site_id: str = "", limit: int = 25, target: str = "", environment: str = "", locale: str = "") -> dict[str, Any]:
    archive = audit_store.list_release_archive(site_id, limit=limit, target=target, environment=environment, locale=locale)
    return {"ok": True, "exportType": "easiio-docs-release-archive-index", "site_id": clean_text(site_id, 100), "count": len(archive), "archive": archive, "filters": _filters(site_id, target=target, environment=environment, locale=locale, limit=limit)}


def build_release_attestation_response(audit_store: DocsAuditStore, *, record_id: int | str) -> dict[str, Any]:
    archive = audit_store.get_release_archive_by_audit_id(record_id)
    if not archive:
        return {"ok": False, "error": "release archive attestation not found", "notFound": True}
    return {"ok": True, "exportType": "easiio-docs-release-attestation", "archive": archive, "attestation": archive.get("attestation") or {}}


def build_release_report_download_response(audit_store: DocsAuditStore, *, record_id: int | str) -> dict[str, Any]:
    archive = audit_store.get_release_archive_by_audit_id(record_id)
    if not archive:
        return {"ok": False, "error": "release archive report not found", "notFound": True}
    path = Path(archive.get("reportPath") or "")
    if not path.exists() or not path.is_file():
        return {"ok": False, "error": "release archive report file is not available locally", "missingReport": True}
    return {"ok": True, "body": path.read_text(encoding="utf-8"), "fileName": path.name, "archive": archive}



def _restore_package_root() -> Path:
    return Path(__file__).resolve().parents[1] / "dist" / "easiio-docs-restore-packages"


def verifyReleaseIntegrity(audit_store: DocsAuditStore, *, record_id: int | str) -> dict[str, Any]:
    archive = audit_store.get_release_archive_by_audit_id(record_id)
    if not archive:
        return {"ok": False, "error": "release archive not found", "notFound": True}
    record = audit_store.get_deployment_package_detail(archive.get("auditRecordId"))
    if not record:
        return {"ok": False, "error": "deployment package audit record not found", "notFound": True}
    attestation = archive.get("attestation") if isinstance(archive.get("attestation"), dict) else {}
    checks: list[dict[str, Any]] = []

    def add_check(name: str, expected: str, actual: str, exists: bool = True) -> None:
        checks.append({"name": name, "expected": expected or "", "actual": actual or "", "exists": bool(exists), "verified": bool(exists and expected and actual and expected == actual)})

    package_path = Path(record.get("packagePath") or "")
    package_exists = package_path.exists() and package_path.is_file()
    package_bytes = package_path.read_bytes() if package_exists else b""
    add_check("packageSha256", attestation.get("packageSha256", ""), _sha256_bytes(package_bytes) if package_exists else "", package_exists)

    manifest = record.get("manifest") if isinstance(record.get("manifest"), dict) else {}
    add_check("manifestSha256", attestation.get("manifestSha256", ""), _sha256_json(manifest), True)

    report_path = Path(archive.get("reportPath") or "")
    report_exists = report_path.exists() and report_path.is_file()
    report_text = report_path.read_text(encoding="utf-8") if report_exists else ""
    add_check("handoffReportSha256", attestation.get("handoffReportSha256", ""), _sha256_bytes(report_text.encode("utf-8")) if report_exists else "", report_exists)

    add_check("releaseNotesSha256", attestation.get("releaseNotesSha256", ""), _sha256_json(record.get("releaseNotes") or {}), True)

    expected_files = attestation.get("fileHashes") if isinstance(attestation.get("fileHashes"), list) else []
    file_checks = []
    actual_file_hashes: dict[str, dict[str, Any]] = {}
    if package_exists and package_path.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(package_path) as zf:
                for name in sorted(zf.namelist()):
                    if name.endswith("/"):
                        continue
                    data = zf.read(name)
                    actual_file_hashes[name] = {"path": name, "sha256": _sha256_bytes(data), "size": len(data)}
        except Exception:
            actual_file_hashes = {}
    for item in expected_files:
        if not isinstance(item, dict):
            continue
        path = item.get("path") or ""
        actual = actual_file_hashes.get(path) or {}
        file_checks.append({"path": path, "expectedSha256": item.get("sha256", ""), "actualSha256": actual.get("sha256", ""), "expectedSize": int(item.get("size") or 0), "actualSize": int(actual.get("size") or 0), "verified": bool(actual and actual.get("sha256") == item.get("sha256") and int(actual.get("size") or 0) == int(item.get("size") or 0))})
    verified = all(check.get("verified") for check in checks) and all(item.get("verified") for item in file_checks)
    return {
        "ok": True,
        "auditRecordId": archive.get("auditRecordId"),
        "archive": archive,
        "packageSha256": attestation.get("packageSha256", ""),
        "verified": bool(verified),
        "checks": checks,
        "fileChecks": file_checks,
        "localOnly": True,
    }


def _find_previous_release_archive(audit_store: DocsAuditStore, current_archive: dict[str, Any]) -> dict[str, Any] | None:
    site_id = current_archive.get("site_id") or ""
    records = audit_store.list_release_archive(site_id, limit=100, target=current_archive.get("deploymentTarget", ""), environment=current_archive.get("environment", ""), locale=current_archive.get("locale", ""))
    current_id = int(current_archive.get("auditRecordId") or 0)
    older = [item for item in records if int(item.get("auditRecordId") or 0) != current_id and int(item.get("created_at") or 0) <= int(current_archive.get("created_at") or 0)]
    return older[0] if older else (records[0] if records and int(records[0].get("auditRecordId") or 0) != current_id else None)


def _rollback_markdown(current: dict[str, Any], target: dict[str, Any], current_integrity: dict[str, Any], target_integrity: dict[str, Any]) -> str:
    lines = [
        f"# Rollback Plan — Package #{current.get('auditRecordId')} to #{target.get('auditRecordId')}",
        "",
        "This is a local-only restore planning document. It does not deploy, publish, upload, or call external services.",
        "",
        "## Current release",
        f"- Audit record ID: {current.get('auditRecordId')}",
        f"- Site ID: {current.get('site_id', '')}",
        f"- Target: {current.get('deploymentTarget', '')}",
        f"- Environment: {current.get('environment', '')}",
        f"- Package SHA-256: {current.get('packageSha256', '')}",
        f"- Integrity verified: {'yes' if current_integrity.get('verified') else 'no'}",
        "",
        "## Rollback target",
        f"- Audit record ID: {target.get('auditRecordId')}",
        f"- Site ID: {target.get('site_id', '')}",
        f"- Target: {target.get('deploymentTarget', '')}",
        f"- Environment: {target.get('environment', '')}",
        f"- Package SHA-256: {target.get('packageSha256', '')}",
        f"- Integrity verified: {'yes' if target_integrity.get('verified') else 'no'}",
        "",
        "## Operator checklist",
        "- [ ] Review current release attestation and rollback target attestation.",
        "- [ ] Verify package hashes before copying any files.",
        "- [ ] Restore only from the rollback target package after human approval.",
        "- [ ] Run website smoke checks after manual restore.",
        "- [ ] Record the final operator action in the deployment system.",
    ]
    return "\n".join(lines).strip() + "\n"


def build_release_archive_integrity_response(audit_store: DocsAuditStore, *, record_id: int | str) -> dict[str, Any]:
    integrity = verifyReleaseIntegrity(audit_store, record_id=record_id)
    if not integrity.get("ok"):
        return integrity
    return {"ok": True, "exportType": "easiio-docs-release-integrity", "integrity": integrity, "archive": integrity.get("archive")}


def build_release_rollback_plan_response(audit_store: DocsAuditStore, *, record_id: int | str, previous_id: int | str = "") -> dict[str, Any]:
    current = audit_store.get_release_archive_by_audit_id(record_id)
    if not current:
        return {"ok": False, "error": "current release archive not found", "notFound": True}
    target = audit_store.get_release_archive_by_audit_id(previous_id) if previous_id else _find_previous_release_archive(audit_store, current)
    if not target:
        return {"ok": False, "error": "rollback target release archive not found", "notFound": True}
    current_integrity = verifyReleaseIntegrity(audit_store, record_id=current.get("auditRecordId"))
    target_integrity = verifyReleaseIntegrity(audit_store, record_id=target.get("auditRecordId"))
    markdown = _rollback_markdown(current, target, current_integrity, target_integrity)
    return {
        "ok": True,
        "exportType": "easiio-docs-rollback-plan",
        "currentRelease": current,
        "rollbackTarget": target,
        "integrity": {"verified": bool(current_integrity.get("verified") and target_integrity.get("verified")), "current": current_integrity, "rollbackTarget": target_integrity},
        "rollbackPlanMarkdown": markdown,
        "localOnly": True,
    }


def build_release_restore_package_response(audit_store: DocsAuditStore, payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("confirmPrepareRestore") is not True:
        return {"ok": False, "error": "confirmPrepareRestore is required before preparing a restore package", "requiresRestoreConfirmation": True, "restoreBlocked": True}
    record_id = payload.get("id") or payload.get("record_id") or payload.get("auditRecordId")
    previous_id = payload.get("previous_id") or payload.get("previousId") or payload.get("rollbackTargetId") or ""
    plan = build_release_rollback_plan_response(audit_store, record_id=record_id, previous_id=previous_id)
    if not plan.get("ok"):
        return {**plan, "restoreBlocked": True}
    if not plan.get("integrity", {}).get("verified"):
        return {"ok": False, "error": "restore package blocked because archive integrity verification failed", "integrity": plan.get("integrity"), "restoreBlocked": True}
    current = plan["currentRelease"]
    target = plan["rollbackTarget"]
    site_slug = _safe_archive_slug(target.get("site_id") or current.get("site_id") or "site")
    out_dir = _restore_package_root() / site_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"restore-current-{int(current.get('auditRecordId') or 0)}-to-{int(target.get('auditRecordId') or 0)}.zip"
    files = []
    readme = "Easiio Docs restore package. Local-only rollback planning artifact; manual operator review required before any external action.\n"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README.txt", readme); files.append("README.txt")
        zf.writestr("rollback-plan.md", plan.get("rollbackPlanMarkdown", "")); files.append("rollback-plan.md")
        zf.writestr("current-attestation.json", json.dumps(current.get("attestation") or {}, ensure_ascii=False, indent=2, sort_keys=True)); files.append("current-attestation.json")
        zf.writestr("rollback-target-attestation.json", json.dumps(target.get("attestation") or {}, ensure_ascii=False, indent=2, sort_keys=True)); files.append("rollback-target-attestation.json")
        zf.writestr("integrity.json", json.dumps(plan.get("integrity") or {}, ensure_ascii=False, indent=2, sort_keys=True)); files.append("integrity.json")
        target_record = audit_store.get_deployment_package_detail(target.get("auditRecordId"))
        target_package = Path((target_record or {}).get("packagePath") or "")
        if target_package.exists() and target_package.is_file():
            zf.write(target_package, "rollback-target-package.zip"); files.append("rollback-target-package.zip")
    restore = {
        "currentAuditRecordId": int(current.get("auditRecordId") or 0),
        "rollbackTargetAuditRecordId": int(target.get("auditRecordId") or 0),
        "packagePath": str(zip_path),
        "packageSize": zip_path.stat().st_size if zip_path.exists() else 0,
        "packageSha256": _sha256_bytes(zip_path.read_bytes()) if zip_path.exists() else "",
        "files": files,
        "createdBy": clean_text(payload.get("createdBy") or payload.get("actor") or "", 120),
        "createdAt": int(time.time()),
        "localOnly": True,
    }
    return {"ok": True, "exportType": "easiio-docs-restore-package", "restorePackage": restore, "rollbackPlanMarkdown": plan.get("rollbackPlanMarkdown", ""), "rollbackPlan": plan, "localOnly": True}
