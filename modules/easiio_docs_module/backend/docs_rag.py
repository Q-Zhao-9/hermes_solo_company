from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any

from docs_db import DocsStore, clean_text
from docs_sitelet import render_doc_content

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHATBOT_RAG_STORE = ROOT.parent / "website_chatbot" / "data" / "rag_content.json"
DOCS_RAG_PREFIX = "easiio-docs:"
MAX_RAG_CONTENT_CHARS = int(os.environ.get("EASIIO_DOCS_RAG_MAX_CONTENT", "50000"))
MAX_RAG_CHUNK_CHARS = int(os.environ.get("EASIIO_DOCS_RAG_CHUNK_CHARS", "1200"))
MAX_RAG_CHUNKS_PER_DOC = int(os.environ.get("EASIIO_DOCS_RAG_CHUNKS_PER_DOC", "8"))


def chatbot_rag_store_path() -> Path:
    return Path(os.environ.get("EASIIO_CHATBOT_RAG_STORE", str(DEFAULT_CHATBOT_RAG_STORE)))


def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def strip_html(text: str) -> str:
    text = re.sub(r"<\s*br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</\s*(p|div|section|h[1-6]|li|ul|ol)\s*>", "\n", text, flags=re.I)
    return re.sub(r"<[^>]+>", " ", text)


def content_to_plain_text(doc: dict[str, Any]) -> str:
    rendered = render_doc_content(doc)
    text = strip_html(rendered)
    parts = [doc.get("title") or "", doc.get("summary") or "", text]
    return normalize_ws("\n".join(str(part or "") for part in parts))[:MAX_RAG_CONTENT_CHARS]


def chunk_text(text: str) -> list[str]:
    text = normalize_ws(text)
    if not text:
        return []
    sentences = [part.strip() for part in re.split(r"(?<=[。！？.!?])\s+|\n+", text) if part.strip()]
    if not sentences:
        sentences = [text]
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if not current:
            current = sentence
        elif len(current) + len(sentence) + 1 <= MAX_RAG_CHUNK_CHARS:
            current = f"{current} {sentence}"
        else:
            chunks.append(current)
            current = sentence
    if current:
        chunks.append(current)
    return chunks[:MAX_RAG_CHUNKS_PER_DOC]


def eligible_rag_docs(store: DocsStore, site_id: str, *, target: str = "rag", status: str = "published", visibility: str = "public", include_private: bool = False) -> list[dict[str, Any]]:
    site_id = clean_text(site_id, 100)
    if not site_id:
        raise ValueError("site_id is required")
    docs = store.list_docs(site_id, status=status, visibility="" if include_private else visibility)
    result: list[dict[str, Any]] = []
    for doc in docs:
        if status and doc.get("status") != status:
            continue
        if not include_private and doc.get("visibility") != visibility:
            continue
        if not doc.get("rag_enabled"):
            continue
        targets = doc.get("framework_targets") or []
        if target and target not in targets:
            continue
        result.append(doc)
    result.sort(key=lambda d: (str(d.get("category") or ""), str(d.get("title") or ""), str(d.get("slug") or "")))
    return result


def doc_to_rag_items(doc: dict[str, Any]) -> list[dict[str, Any]]:
    site_id = clean_text(doc.get("site_id"), 100)
    slug = clean_text(doc.get("slug"), 160)
    title = clean_text(doc.get("title") or slug, 300)
    summary = clean_text(doc.get("summary"), 500)
    tags = doc.get("tags") if isinstance(doc.get("tags"), list) else []
    category = clean_text(doc.get("category"), 120)
    updated_at = int(time.time())
    try:
        updated_at = int(doc.get("updated_at") or updated_at)
    except (TypeError, ValueError):
        pass
    text = content_to_plain_text(doc)
    chunks = chunk_text(text)
    items = []
    for index, chunk in enumerate(chunks, 1):
        suffix = f":chunk-{index}" if len(chunks) > 1 else ""
        items.append({
            "content_id": f"{DOCS_RAG_PREFIX}{site_id}:{slug}{suffix}",
            "site_id": site_id,
            "title": title if len(chunks) == 1 else f"{title} — part {index}",
            "url": f"easiio-docs://{site_id}/{slug}{suffix}",
            "content": chunk,
            "source": "easiio-docs-module",
            "doc_slug": slug,
            "category": category,
            "tags": [clean_text(tag, 80) for tag in tags if clean_text(tag, 80)],
            "summary": summary,
            "created_at": updated_at,
            "updated_at": int(time.time()),
        })
    return items


def build_rag_preview(store: DocsStore, site_id: str, *, target: str = "rag", status: str = "published", visibility: str = "public", include_private: bool = False) -> dict[str, Any]:
    docs = eligible_rag_docs(store, site_id, target=target, status=status, visibility=visibility, include_private=include_private)
    chunks: list[dict[str, Any]] = []
    for doc in docs:
        chunks.extend(doc_to_rag_items(doc))
    return {
        "ok": True,
        "exportType": "easiio-docs-rag-preview",
        "site_id": clean_text(site_id, 100),
        "target": target,
        "status": status,
        "visibility": "all" if include_private else visibility,
        "documentCount": len(docs),
        "chunkCount": len(chunks),
        "chunks": chunks,
        "requiresSyncApproval": True,
        "syncBlocked": True,
        "storePath": str(chatbot_rag_store_path()),
        "syncInstructions": {
            "endpoint": "POST /api/docs/rag/sync",
            "requiredFlag": "confirmRagSync:true",
            "note": "Review chunks before writing to the chatbot manual RAG store.",
        },
    }


def load_rag_store(path: Path | None = None) -> dict[str, list[dict[str, Any]]]:
    path = path or chatbot_rag_store_path()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    sites = raw.get("sites", raw)
    if not isinstance(sites, dict):
        return {}
    cleaned: dict[str, list[dict[str, Any]]] = {}
    for site_id, items in sites.items():
        if isinstance(site_id, str) and isinstance(items, list):
            cleaned[site_id] = [item for item in items if isinstance(item, dict)]
    return cleaned


def save_rag_store(store: dict[str, list[dict[str, Any]]], path: Path | None = None) -> None:
    path = path or chatbot_rag_store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"version": 1, "sites": store}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sync_docs_to_chatbot_rag(store: DocsStore, payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("confirmRagSync") is not True:
        return {
            "ok": False,
            "error": "confirmRagSync is required before writing docs to chatbot RAG",
            "requiresSyncApproval": True,
            "syncBlocked": True,
        }
    site_id = clean_text(payload.get("site_id"), 100)
    preview = build_rag_preview(
        store,
        site_id,
        target=payload.get("target") or "rag",
        status=payload.get("status") or "published",
        visibility=payload.get("visibility") or "public",
        include_private=bool(payload.get("includePrivate")),
    )
    chunks = preview["chunks"]
    path = chatbot_rag_store_path()
    rag_store = load_rag_store(path)
    existing = rag_store.get(site_id, [])
    kept = [item for item in existing if not str(item.get("content_id") or "").startswith(f"{DOCS_RAG_PREFIX}{site_id}:")]
    rag_store[site_id] = kept + chunks
    save_rag_store(rag_store, path)
    return {
        "ok": True,
        "exportType": "easiio-docs-rag-sync-result",
        "site_id": site_id,
        "storePath": str(path),
        "documentCount": preview["documentCount"],
        "chunkCount": preview["chunkCount"],
        "syncedCount": len(chunks),
        "keptExistingCount": len(kept),
        "requiresSyncApproval": True,
        "syncBlocked": False,
        "approvedBy": clean_text(payload.get("approvedBy"), 120),
        "items": chunks,
    }
