#!/usr/bin/env python3
"""Dependency-free backend API for the Easiio website chatbot.

The browser widget calls this HTTP API. The API performs deterministic lead
extraction and writes useful contact/deal/activity records into the local Solo
CRM SQLite database. It intentionally does not expose MCP, database paths, or
secrets to browser JavaScript.
"""
from __future__ import annotations

import argparse
import base64
import difflib
import hashlib
import html
import io
import json
import mimetypes
import os
import re
import smtplib
import sqlite3
import sys
import time
import urllib.error
import urllib.request
import uuid
import zipfile
from dataclasses import dataclass
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest
from urllib.parse import parse_qs, urlencode, urlparse

ROOT = Path(__file__).resolve().parents[1]
SOLO_CRM_ROOT = ROOT.parent / "solo_crm"
if str(SOLO_CRM_ROOT) not in sys.path:
    sys.path.insert(0, str(SOLO_CRM_ROOT))
VOICE_RESPONSE_ROOT = ROOT.parent / "voice_response"
if str(VOICE_RESPONSE_ROOT) not in sys.path:
    sys.path.insert(0, str(VOICE_RESPONSE_ROOT))

from crm_core import SoloCRM  # noqa: E402


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


load_env_file(Path.home() / ".hermes" / ".env")

SERVICE_NAME = "easiio-website-chatbot"
DEFAULT_HOST = os.environ.get("EASIIO_CHATBOT_HOST", "0.0.0.0")
DEFAULT_PORT = int(os.environ.get("EASIIO_CHATBOT_PORT", "8099"))
MAX_BODY_BYTES = int(os.environ.get("EASIIO_CHATBOT_MAX_BODY", "65536"))
MAX_MESSAGE_CHARS = int(os.environ.get("EASIIO_CHATBOT_MAX_MESSAGE", "2000"))
ALLOWED_ORIGINS = [origin.strip() for origin in os.environ.get(
    "EASIIO_CHATBOT_ALLOWED_ORIGINS",
    "http://localhost:8088,http://127.0.0.1:8088,http://localhost:8010,http://127.0.0.1:8010,https://www.easiio.com,https://easiio.com",
).split(",") if origin.strip()]

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?:(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})")
SALES_INTENT_RE = re.compile(
    r"\b(demo|pricing|price|quote|proposal|consultation|sales|automation|agent|agents|workflow|chatbot|crm|book|meeting)\b",
    re.I,
)
PRICING_RE = re.compile(r"\b(pricing|price|quote|proposal|cost|budget)\b", re.I)
DEMO_RE = re.compile(r"\b(demo|book|meeting|consultation|sales)\b", re.I)
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "can", "does", "for", "from", "how", "i", "in", "is", "it", "me", "of", "on", "or", "our", "the", "this", "to", "what", "when", "where", "who", "with", "you", "your",
    "多少", "什么", "如何", "这个", "那个", "课程", "网站",
}
RAG_QUERY_SYNONYMS = {
    "class": ["lesson", "course", "module", "curriculum"],
    "classes": ["lessons", "course", "modules", "curriculum"],
    "lesson": ["class", "course", "module", "curriculum"],
    "lessons": ["classes", "course", "modules", "curriculum"],
    "course": ["class", "lesson", "bootcamp", "curriculum"],
    "price": ["pricing", "cost", "fee", "tuition"],
    "pricing": ["price", "cost", "fee", "tuition"],
    "enroll": ["register", "signup", "join", "报名"],
    "chatbot": ["website assistant", "AI assistant", "RAG", "knowledge base"],
    "assistant": ["chatbot", "AI assistant", "website assistant", "knowledge base"],
    "rag": ["knowledge base", "retrieval", "website content", "docs"],
}

# Public demos sometimes use a shorter site_id than the production/course
# knowledge store. Keep these aliases server-side so the widget can answer from
# the AI Solo Company knowledge base before falling back to sales handoff text.
RAG_SITE_ALIASES = {
    "ai-solo-company": ["ai-solo-company-class"],
    "ai-solo-company-demo": ["ai-solo-company", "ai-solo-company-class"],
}

MAX_RAG_CONTENT_CHARS = int(os.environ.get("EASIIO_CHATBOT_MAX_RAG_CONTENT", "50000"))
MAX_RAG_CHUNKS_PER_SITE = int(os.environ.get("EASIIO_CHATBOT_MAX_RAG_CHUNKS", "80"))
MAX_RAG_LLM_CONTEXT_CHARS = int(os.environ.get("EASIIO_CHATBOT_MAX_RAG_LLM_CONTEXT", "2400"))
MAX_RAG_REPLY_CHARS = int(os.environ.get("EASIIO_CHATBOT_MAX_RAG_REPLY", "700"))
LLM_TIMEOUT_SECONDS = float(os.environ.get("EASIIO_CHATBOT_LLM_TIMEOUT", "12"))
RAG_MODE = os.environ.get("EASIIO_CHATBOT_RAG_MODE", "enhanced").lower()
RAG_DEBUG = os.environ.get("EASIIO_CHATBOT_RAG_DEBUG", "false").lower() in {"1", "true", "yes", "on"}
RAG_HYDE_ENABLED = os.environ.get("EASIIO_CHATBOT_RAG_HYDE_ENABLED", "true").lower() in {"1", "true", "yes", "on"}
RAG_VERIFY_ENABLED = os.environ.get("EASIIO_CHATBOT_RAG_VERIFY_ENABLED", "true").lower() in {"1", "true", "yes", "on"}
RAG_MAX_CANDIDATES = int(os.environ.get("EASIIO_CHATBOT_RAG_MAX_CANDIDATES", "50"))
RAG_MAX_SELECTED = int(os.environ.get("EASIIO_CHATBOT_RAG_MAX_SELECTED", "8"))
LEAD_FORMS_ENABLED = os.environ.get("EASIIO_CHATBOT_LEAD_FORMS_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
RAG_CONTENT_STORE_PATH = Path(os.environ.get("EASIIO_CHATBOT_RAG_STORE", str(ROOT / "data" / "rag_content.json")))
FORM_CONFIG_STORE_PATH = Path(os.environ.get("EASIIO_CHATBOT_FORM_CONFIG_STORE", str(ROOT / "data" / "form_config.json")))
EMAIL_CONFIG_STORE_PATH = Path(os.environ.get("EASIIO_CHATBOT_EMAIL_CONFIG_STORE", str(ROOT / "data" / "email_agent_config.json")))
EMAIL_OUTBOX_DIR = Path(os.environ.get("EASIIO_CHATBOT_EMAIL_OUTBOX_DIR", str(ROOT / "data" / "email_outbox")))
RAG_ANSWER_LOG_PATH = Path(os.environ.get("EASIIO_CHATBOT_RAG_ANSWER_LOG", str(ROOT / "data" / "rag_answer_log.json")))
RAG_FEEDBACK_STORE_PATH = Path(os.environ.get("EASIIO_CHATBOT_RAG_FEEDBACK_STORE", str(ROOT / "data" / "rag_feedback.json")))
RAG_SYNC_LOG_PATH = Path(os.environ.get("EASIIO_CHATBOT_RAG_SYNC_LOG", str(ROOT / "data" / "rag_sync_log.json")))
RAG_EXTERNAL_SOURCES_PATH = Path(os.environ.get("EASIIO_CHATBOT_RAG_EXTERNAL_SOURCES", str(ROOT / "data" / "rag_external_sources.json")))
RAG_REFRESH_SCHEDULE_PATH = Path(os.environ.get("EASIIO_CHATBOT_RAG_REFRESH_SCHEDULE", str(ROOT / "data" / "rag_refresh_schedule.json")))
RAG_NOTIFICATIONS_PATH = Path(os.environ.get("EASIIO_CHATBOT_RAG_NOTIFICATIONS", str(ROOT / "data" / "rag_notifications.json")))
VOICE_CACHE_DIR = Path(os.environ.get("EASIIO_CHATBOT_VOICE_CACHE_DIR", str(ROOT / "data" / "voice_cache")))
MAX_VOICE_TEXT_CHARS = int(os.environ.get("EASIIO_CHATBOT_VOICE_MAX_CHARS", os.environ.get("VOICE_RESPONSE_MAX_CHARS", "2000")))
MAX_RAG_UPLOAD_BYTES = int(os.environ.get("EASIIO_CHATBOT_RAG_UPLOAD_MAX_BYTES", "5242880"))
DOCS_DB_PATH = Path(os.environ.get("EASIIO_DOCS_DB", str(ROOT.parent / "easiio_docs_module" / "data" / "easiio_docs.db")))
WIKI_DB_PATH = Path(os.environ.get("EASIIO_WIKI_DB", str(ROOT.parent / "website_wiki_module" / "data" / "website_wiki.db")))
MAX_RAG_ANSWER_LOG_ITEMS = int(os.environ.get("EASIIO_CHATBOT_RAG_ANSWER_LOG_MAX", "500"))
MAX_RAG_FEEDBACK_ITEMS = int(os.environ.get("EASIIO_CHATBOT_RAG_FEEDBACK_MAX", "500"))
SMTP_TIMEOUT_SECONDS = float(os.environ.get("EASIIO_CHATBOT_SMTP_TIMEOUT", "15"))
SITE_RAG_INDEX: dict[str, list[dict[str, Any]]] = {}
DEFAULT_WIDGET_CONFIG: dict[str, Any] = {
    "voice_enabled": False,
    "voice_label": "Listen",
    "voice_autoplay": False,
    "voice": "",
    "voice_format": "mp3",
    "voice_input_enabled": False,
    "voice_input_label": "Speak",
    "voice_input_language": "auto",
    "voice_call_enabled": False,
    "voice_call_label": "Call AI Assistant",
    "voice_call_api_base": "",
    "voice_call_consent_text": "This AI assistant may transcribe your voice to answer your question and follow up if you share contact details.",
}

DEFAULT_LEAD_FORM_CONFIG: dict[str, Any] = {
    "title": "Where should we follow up?",
    "help_text": "Optional — close this and keep chatting if you are not ready.",
    "submit_label": "Send to Easiio",
    "fields": [
        {"name": "name", "label": "Name", "type": "text", "required": False, "autocomplete": "name"},
        {"name": "email", "label": "Work email", "type": "email", "required": True, "autocomplete": "email"},
        {"name": "company", "label": "Company", "type": "text", "required": False, "autocomplete": "organization"},
        {"name": "message", "label": "Message", "type": "textarea", "required": True, "autocomplete": ""},
    ],
}
DEFAULT_EMAIL_AGENT_CONFIG: dict[str, Any] = {
    "enabled": False,
    "provider": "brevo",
    "send_welcome_email": True,
    "send_owner_notification": True,
    "owner_recipients": [],
    "from_email": "",
    "from_name": "Easiio Website Assistant",
    "welcome_subject": "Welcome to {{site_name}}",
    "welcome_body": "Hi {{name}},\n\nThanks for contacting {{site_name}}. We received your information and will follow up soon.\n\nYour message:\n{{message}}\n\nBest,\n{{site_name}} Team",
    "owner_subject": "New website lead from {{site_name}}: {{name}}",
    "owner_body": "A new website lead was captured.\n\nName: {{name}}\nEmail: {{email}}\nPhone: {{phone}}\nCompany: {{company}}\nSite ID: {{site_id}}\nPage: {{page_url}}\nSession: {{session_id}}\nLead score: {{lead_score}}\n\nMessage:\n{{message}}",
}


@dataclass
class Response:
    status: int
    body: Any
    headers: dict[str, str] | None = None


def json_response(status: int, body: dict[str, Any], headers: dict[str, str] | None = None) -> Response:
    return Response(status=status, body=body, headers=headers or {})


def mask_pii(value: Any, limit: int = 1000) -> str:
    text = sanitize_text(value, limit) if "sanitize_text" in globals() else str(value or "")[:limit]
    text = EMAIL_RE.sub("[email]", text)
    text = PHONE_RE.sub("[phone]", text)
    return text


def load_json_items(path: Path) -> list[dict[str, Any]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    items = raw.get("items", raw) if isinstance(raw, dict) else raw
    return [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []


def save_json_items(path: Path, items: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"version": 1, "items": items}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def json_safe(value: Any) -> Any:
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    return value


def chunk_debug_summary(chunk: dict[str, Any]) -> dict[str, Any]:
    return {
        "chunk_id": chunk.get("chunk_id", ""),
        "source": chunk.get("source", ""),
        "content_id": chunk.get("content_id", ""),
        "title": chunk.get("title", ""),
        "section": chunk.get("section", ""),
        "url": chunk.get("url", ""),
        "summary": chunk.get("summary", ""),
        "text_preview": normalize_whitespace(chunk.get("text", ""))[:280],
    }


def parse_json(body: bytes) -> dict[str, Any]:
    if not body:
        return {}
    try:
        value = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError("JSON body must be an object")
    return value


def sanitize_text(value: Any, limit: int = MAX_MESSAGE_CHARS) -> str:
    text = str(value or "").replace("\x00", "").strip()
    if len(text) > limit:
        return text[:limit]
    return text


def extract_email(*values: Any) -> str:
    for value in values:
        match = EMAIL_RE.search(str(value or ""))
        if match:
            return match.group(0).lower()
    return ""


def extract_phone(*values: Any) -> str:
    for value in values:
        match = PHONE_RE.search(str(value or ""))
        if match:
            return match.group(0).strip()
    return ""


def page_text(page_context: dict[str, Any]) -> str:
    return " ".join(str(page_context.get(key, "")) for key in ("url", "title", "referrer"))


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def tokenize(text: str) -> set[str]:
    # English words, numbers, and CJK tokens. Include Chinese characters and
    # bigrams so short questions like "第 3 课是什么" can match "第 3 课".
    lowered = text.lower()
    raw_tokens = re.findall(r"[a-z][a-z0-9_+-]*|\d+|[\u4e00-\u9fff]{2,}", lowered)
    cjk_chars = re.findall(r"[\u4e00-\u9fff]", lowered)
    cjk_bigrams = ["".join(pair) for pair in zip(cjk_chars, cjk_chars[1:])]
    tokens = set(raw_tokens + cjk_chars + cjk_bigrams)
    if "class" in tokens or "classes" in tokens:
        tokens.update({"lesson", "lessons", "课"})
    if "lesson" in tokens or "lessons" in tokens:
        tokens.update({"class", "classes", "课"})
    if "课" in tokens:
        tokens.update({"lesson", "lessons", "class", "classes"})
    return {token for token in tokens if token and token not in STOP_WORDS}


def direct_count_answer(question: str, context: str, language: str = "") -> str:
    question_lower = question.lower()
    asks_total_classes = bool(re.search(r"\b(how many|total|number of)\b", question_lower)) and bool(re.search(r"\b(class|classes|lesson|lessons)\b", question_lower))
    if not asks_total_classes:
        return ""
    query_lesson = find_lesson_number(question)
    phrase_counts = [int(value) for value in re.findall(r"\b(\d{1,3})\s*(?:lessons|classes|课|節|节)\b", context, re.I)]
    lesson_numbers = [int(value) for value in re.findall(r"(?:Lesson\s*|第\s*)(\d{1,3})(?:\s*课)?", context, re.I)]
    candidates = phrase_counts if phrase_counts else ([max(lesson_numbers)] if lesson_numbers else [])
    if not candidates:
        return ""
    count = max(candidates)
    if str(language).lower().startswith("zh"):
        answer = f"一共有 {count} 节课。"
    else:
        answer = f"There are {count} classes total ({count} Lessons)."
    if query_lesson:
        lesson_matches = list(re.finditer(r"(?:Lesson\s*|第\s*)(\d+)(?:\s*课)?", context, re.I))
        for idx, lesson_match in enumerate(lesson_matches):
            if lesson_match.group(1) == query_lesson:
                next_start = lesson_matches[idx + 1].start() if idx + 1 < len(lesson_matches) else len(context)
                lesson_text = normalize_whitespace(context[lesson_match.start():next_start])
                if lesson_text:
                    answer = f"{answer} {lesson_text[:260].rstrip()}"
                break
    return answer


def split_rag_units(text: str) -> list[str]:
    text = normalize_whitespace(text)
    # Add boundaries before lesson headings so one answer does not include the
    # neighboring lessons from a long single-page curriculum section.
    text = re.sub(r"\s+(?=(?:Lesson\s+\d+\b|第\s*\d+\s*课))", "\n", text, flags=re.I)
    return [part.strip() for part in re.split(r"(?<=[。！？.!?])\s+|\n+", text) if part.strip()]


def chunk_website_content(content: str) -> list[str]:
    content = normalize_whitespace(content[:MAX_RAG_CONTENT_CHARS])
    if not content:
        return []
    sentences = split_rag_units(content)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        starts_new_lesson = bool(re.match(r"(?:Lesson\s+\d+\b|第\s*\d+\s*课)", sentence, re.I))
        if starts_new_lesson and current:
            chunks.append(current)
            current = sentence
        elif not current:
            current = sentence
        elif len(current) + len(sentence) < 520:
            current = f"{current} {sentence}"
        else:
            chunks.append(current)
            current = sentence
    if current:
        chunks.append(current)
    if not chunks and content:
        chunks = [content]
    return chunks[:MAX_RAG_CHUNKS_PER_SITE]


def detect_section_heading(line: str) -> str:
    text = normalize_whitespace(line)
    if not text:
        return ""
    # Lesson headings are answer units, not parent sections. Keep the previous
    # parent section (for example Curriculum) so nearby lessons can be expanded
    # without treating each lesson as an unrelated section.
    if re.match(r"^(lesson\s+\d+|第\s*\d+\s*课)\b", text, re.I):
        return ""
    if len(text) <= 90 and not re.search(r"[.!?。！？:：].{8,}$", text):
        return text[:120]
    return ""


def summarize_chunk(title: str, section: str, text: str) -> str:
    sentences = split_rag_units(text)
    first = sentences[0] if sentences else normalize_whitespace(text)[:180]
    prefix = " / ".join(part for part in [title, section] if part)
    return normalize_whitespace(f"{prefix}: {first}" if prefix else first)[:300]


def _enhanced_paragraph_units(content: str) -> list[str]:
    raw = str(content or "")[:MAX_RAG_CONTENT_CHARS].replace("\x00", "")
    # Preserve explicit author/document line breaks; also add virtual boundaries
    # before lesson headings in single-line website text.
    raw = re.sub(r"\s+(?=(?:Lesson\s+\d+\b|第\s*\d+\s*课))", "\n", raw, flags=re.I)
    units = [normalize_whitespace(part) for part in re.split(r"\n\s*\n|\n+", raw) if normalize_whitespace(part)]
    if len(units) <= 1:
        units = split_rag_units(raw)
    return units


def build_enhanced_rag_chunks(site_id: str, page_context: dict[str, Any], *, source: str = "page", content_id: str = "") -> list[dict[str, Any]]:
    content = sanitize_text(page_context.get("content") or page_context.get("text") or "", MAX_RAG_CONTENT_CHARS)
    if not content:
        return []
    url = sanitize_text(page_context.get("url") or "", 500)
    title = sanitize_text(page_context.get("title") or "", 300)
    current_section = ""
    chunks: list[dict[str, Any]] = []
    buffer = ""
    buffer_section = ""

    def flush() -> None:
        nonlocal buffer, buffer_section
        text = normalize_whitespace(buffer)
        if not text:
            buffer = ""
            return
        index = len(chunks)
        chunk_id = f"{source}:{content_id or url or title or site_id}:{index}"
        summary = summarize_chunk(title, buffer_section, text)
        search_text = normalize_whitespace(f"{title} {buffer_section} {summary} {text}")
        chunks.append({
            "chunk_id": chunk_id,
            "text": text,
            "summary": summary,
            "search_text": search_text,
            "url": url,
            "title": title,
            "section": buffer_section,
            "chunk_index": index,
            "tokens": tokenize(search_text),
            "summary_tokens": tokenize(f"{title} {buffer_section} {summary}"),
            "source": source,
            "content_id": content_id,
            "site_id": site_id,
            "prev_id": "",
            "next_id": "",
        })
        buffer = ""

    for unit in _enhanced_paragraph_units(content):
        heading = detect_section_heading(unit)
        if heading:
            flush()
            current_section = heading
            continue
        starts_new_answer_unit = bool(re.match(r"(?:Lesson\s+\d+\b|第\s*\d+\s*课)", unit, re.I))
        if starts_new_answer_unit and buffer:
            flush()
        proposed = normalize_whitespace(f"{buffer} {unit}" if buffer else unit)
        if buffer and len(proposed) > 1800:
            flush()
            proposed = unit
        buffer = proposed
        buffer_section = current_section
    flush()
    if not chunks:
        for index, chunk in enumerate(chunk_website_content(content)):
            summary = summarize_chunk(title, current_section, chunk)
            search_text = normalize_whitespace(f"{title} {current_section} {summary} {chunk}")
            chunks.append({
                "chunk_id": f"{source}:{content_id or url or title or site_id}:{index}",
                "text": chunk,
                "summary": summary,
                "search_text": search_text,
                "url": url,
                "title": title,
                "section": current_section,
                "chunk_index": index,
                "tokens": tokenize(search_text),
                "summary_tokens": tokenize(f"{title} {current_section} {summary}"),
                "source": source,
                "content_id": content_id,
                "site_id": site_id,
                "prev_id": "",
                "next_id": "",
            })
    for index, chunk in enumerate(chunks):
        if index > 0:
            chunk["prev_id"] = chunks[index - 1]["chunk_id"]
        if index + 1 < len(chunks):
            chunk["next_id"] = chunks[index + 1]["chunk_id"]
    return chunks[:MAX_RAG_CHUNKS_PER_SITE]


def _rag_chunks_from_page_context(site_id: str, page_context: dict[str, Any], *, source: str = "page", content_id: str = "") -> list[dict[str, Any]]:
    return build_enhanced_rag_chunks(site_id, page_context, source=source, content_id=content_id)


def update_site_rag_index(site_id: str, page_context: dict[str, Any]) -> None:
    new_chunks = _rag_chunks_from_page_context(site_id, page_context, source="page")
    if not new_chunks:
        return
    existing = SITE_RAG_INDEX.setdefault(site_id, [])
    url = new_chunks[0].get("url", "")
    title = new_chunks[0].get("title", "")
    # Replace previous chunks for this URL/title so each page refresh updates the
    # knowledge base instead of accumulating stale duplicate content.
    existing[:] = [chunk for chunk in existing if chunk.get("source") == "manual" or chunk.get("url") != url or chunk.get("title") != title]
    existing.extend(new_chunks)
    del existing[:-MAX_RAG_CHUNKS_PER_SITE]

def load_rag_content_store() -> dict[str, list[dict[str, Any]]]:
    try:
        raw = json.loads(RAG_CONTENT_STORE_PATH.read_text(encoding="utf-8"))
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


def save_rag_content_store(store: dict[str, list[dict[str, Any]]]) -> None:
    RAG_CONTENT_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    RAG_CONTENT_STORE_PATH.write_text(json.dumps({"version": 1, "sites": store}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def default_lead_form_config() -> dict[str, Any]:
    config = json.loads(json.dumps(DEFAULT_LEAD_FORM_CONFIG))
    config["widget_config"] = json.loads(json.dumps(DEFAULT_WIDGET_CONFIG))
    return config


def load_form_config_store() -> dict[str, dict[str, Any]]:
    try:
        raw = json.loads(FORM_CONFIG_STORE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    sites = raw.get("sites", raw)
    if not isinstance(sites, dict):
        return {}
    cleaned: dict[str, dict[str, Any]] = {}
    for site_id, config in sites.items():
        if isinstance(site_id, str) and isinstance(config, dict):
            cleaned[site_id] = sanitize_form_config(config)
    return cleaned


def save_form_config_store(store: dict[str, dict[str, Any]]) -> None:
    FORM_CONFIG_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FORM_CONFIG_STORE_PATH.write_text(json.dumps({"version": 1, "sites": store}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sanitize_widget_config(config: dict[str, Any] | None) -> dict[str, Any]:
    source = config if isinstance(config, dict) else {}
    def pick_bool(*keys: str) -> bool:
        for key in keys:
            if key in source:
                return bool(source.get(key))
        return False
    voice_format = sanitize_text(source.get("voice_format") or source.get("voiceFormat") or DEFAULT_WIDGET_CONFIG["voice_format"], 20).lower()
    if voice_format not in {"mp3", "wav", "opus"}:
        voice_format = DEFAULT_WIDGET_CONFIG["voice_format"]
    voice_call_api_base = sanitize_text(source.get("voice_call_api_base") or source.get("voiceCallApiBase") or DEFAULT_WIDGET_CONFIG["voice_call_api_base"], 500)
    if voice_call_api_base and not re.match(r"^https?://", voice_call_api_base):
        voice_call_api_base = ""
    return {
        "voice_enabled": pick_bool("voice_enabled", "voiceEnabled"),
        "voice_label": sanitize_text(source.get("voice_label") or source.get("voiceLabel") or DEFAULT_WIDGET_CONFIG["voice_label"], 80),
        "voice_autoplay": pick_bool("voice_autoplay", "voiceAutoplay"),
        "voice": sanitize_text(source.get("voice") or DEFAULT_WIDGET_CONFIG["voice"], 80),
        "voice_format": voice_format,
        "voice_input_enabled": pick_bool("voice_input_enabled", "voiceInputEnabled"),
        "voice_input_label": sanitize_text(source.get("voice_input_label") or source.get("voiceInputLabel") or DEFAULT_WIDGET_CONFIG["voice_input_label"], 80),
        "voice_input_language": sanitize_text(source.get("voice_input_language") or source.get("voiceInputLanguage") or DEFAULT_WIDGET_CONFIG["voice_input_language"], 32),
        "voice_call_enabled": pick_bool("voice_call_enabled", "voiceCallEnabled"),
        "voice_call_label": sanitize_text(source.get("voice_call_label") or source.get("voiceCallLabel") or DEFAULT_WIDGET_CONFIG["voice_call_label"], 80),
        "voice_call_api_base": voice_call_api_base,
        "voice_call_consent_text": sanitize_text(source.get("voice_call_consent_text") or source.get("voiceCallConsentText") or DEFAULT_WIDGET_CONFIG["voice_call_consent_text"], 240),
    }


def sanitize_form_config(config: dict[str, Any]) -> dict[str, Any]:
    base = default_lead_form_config()
    result = {
        "title": sanitize_text(config.get("title") or base["title"], 120),
        "help_text": sanitize_text(config.get("help_text") or config.get("helpText") or base["help_text"], 240),
        "submit_label": sanitize_text(config.get("submit_label") or config.get("submitLabel") or base["submit_label"], 80),
        "fields": [],
        "widget_config": sanitize_widget_config(config.get("widget_config") or config.get("widgetConfig")),
    }
    raw_fields = config.get("fields") or config.get("formItems") or base["fields"]
    if not isinstance(raw_fields, list):
        raw_fields = base["fields"]
    seen: set[str] = set()
    for raw_field in raw_fields[:12]:
        if not isinstance(raw_field, dict):
            continue
        name = sanitize_text(raw_field.get("name") or raw_field.get("key") or "", 40)
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,39}", name or ""):
            continue
        if name in seen:
            continue
        field_type = sanitize_text(raw_field.get("type") or "text", 20).lower()
        if field_type not in {"text", "email", "textarea"}:
            continue
        label = sanitize_text(raw_field.get("label") or raw_field.get("fieldName") or name.replace("_", " ").title(), 80)
        placeholder = sanitize_text(raw_field.get("placeholder") or label, 120)
        autocomplete = sanitize_text(raw_field.get("autocomplete") or "", 60)
        result["fields"].append({
            "name": name,
            "label": label,
            "type": field_type,
            "required": bool(raw_field.get("required")),
            "placeholder": placeholder,
            "autocomplete": autocomplete,
        })
        seen.add(name)
    if not result["fields"]:
        result["fields"] = base["fields"]
    return result


def form_config_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    config = load_form_config_store().get(site_id) or default_lead_form_config()
    return json_response(200, {"ok": True, "site_id": site_id, "form_config": config})


def form_config_upsert_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    raw_config = payload.get("form_config") or payload.get("formConfig") or payload
    if not isinstance(raw_config, dict):
        return json_response(400, {"ok": False, "error": "form_config must be an object"})
    config = sanitize_form_config(raw_config)
    store = load_form_config_store()
    store[site_id] = config
    save_form_config_store(store)
    return json_response(200, {"ok": True, "site_id": site_id, "form_config": config})


def default_email_agent_config() -> dict[str, Any]:
    config = json.loads(json.dumps(DEFAULT_EMAIL_AGENT_CONFIG))
    recipients = os.environ.get("EASIIO_EMAIL_OWNER_RECIPIENTS", "")
    if recipients:
        config["owner_recipients"] = sanitize_email_list(recipients)
    config["from_email"] = sanitize_email_address(os.environ.get("EASIIO_EMAIL_FROM", "") or os.environ.get("EASIIO_EMAIL_FROM_EMAIL", ""))
    config["from_name"] = sanitize_text(os.environ.get("EASIIO_EMAIL_FROM_NAME", config["from_name"]), 120)
    config["provider"] = sanitize_text(os.environ.get("EASIIO_EMAIL_PROVIDER", config["provider"]), 30).lower() or "brevo"
    return config


def sanitize_email_address(value: Any) -> str:
    email = extract_email(value)
    return email.lower() if email else ""


def sanitize_email_list(value: Any) -> list[str]:
    if isinstance(value, str):
        raw_items = re.split(r"[,;\s]+", value)
    elif isinstance(value, list):
        raw_items = value
    else:
        raw_items = []
    result: list[str] = []
    seen: set[str] = set()
    for raw in raw_items[:20]:
        email = sanitize_email_address(raw)
        if email and email not in seen:
            result.append(email)
            seen.add(email)
    return result


def sanitize_template(value: Any, fallback: str, limit: int = 5000) -> str:
    text = str(value if value is not None else fallback).replace("\x00", "").strip()
    if not text:
        text = fallback
    return text[:limit]


def sanitize_email_agent_config(config: dict[str, Any]) -> dict[str, Any]:
    base = default_email_agent_config()
    provider = sanitize_text(config.get("provider") or base.get("provider") or "brevo", 30).lower()
    if provider not in {"brevo", "smtp", "outbox"}:
        provider = "brevo"
    return {
        "enabled": bool(config.get("enabled", base["enabled"])),
        "provider": provider,
        "send_welcome_email": bool(config.get("send_welcome_email", config.get("sendWelcomeEmail", base["send_welcome_email"]))),
        "send_owner_notification": bool(config.get("send_owner_notification", config.get("sendOwnerNotification", base["send_owner_notification"]))),
        "owner_recipients": sanitize_email_list(config.get("owner_recipients", config.get("ownerRecipients", base["owner_recipients"]))),
        "from_email": sanitize_email_address(config.get("from_email", config.get("fromEmail", base["from_email"]))),
        "from_name": sanitize_text(config.get("from_name") or config.get("fromName") or base["from_name"], 120),
        "welcome_subject": sanitize_template(config.get("welcome_subject") or config.get("welcomeSubject"), base["welcome_subject"], 200),
        "welcome_body": sanitize_template(config.get("welcome_body") or config.get("welcomeBody"), base["welcome_body"], 5000),
        "owner_subject": sanitize_template(config.get("owner_subject") or config.get("ownerSubject"), base["owner_subject"], 200),
        "owner_body": sanitize_template(config.get("owner_body") or config.get("ownerBody"), base["owner_body"], 5000),
    }


def load_email_config_store() -> dict[str, dict[str, Any]]:
    try:
        raw = json.loads(EMAIL_CONFIG_STORE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    sites = raw.get("sites", raw) if isinstance(raw, dict) else {}
    if not isinstance(sites, dict):
        return {}
    return {site_id: sanitize_email_agent_config(config) for site_id, config in sites.items() if isinstance(site_id, str) and isinstance(config, dict)}


def save_email_config_store(store: dict[str, dict[str, Any]]) -> None:
    EMAIL_CONFIG_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EMAIL_CONFIG_STORE_PATH.write_text(json.dumps({"version": 1, "sites": store}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def email_agent_config_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    config = load_email_config_store().get(site_id) or default_email_agent_config()
    return json_response(200, {"ok": True, "site_id": site_id, "email_config": config})


def email_agent_config_upsert_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    raw_config = payload.get("email_config") or payload.get("emailConfig") or payload
    if not isinstance(raw_config, dict):
        return json_response(400, {"ok": False, "error": "email_config must be an object"})
    config = sanitize_email_agent_config(raw_config)
    store = load_email_config_store()
    store[site_id] = config
    save_email_config_store(store)
    return json_response(200, {"ok": True, "site_id": site_id, "email_config": config})


def render_email_template(template: str, values: dict[str, Any]) -> str:
    def repl(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        return str(values.get(key, ""))
    return re.sub(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}", repl, template)


def configured_brevo() -> dict[str, Any]:
    api_key = os.environ.get("EASIIO_BREVO_API_KEY") or os.environ.get("BREVO_API_KEY") or os.environ.get("SENDINBLUE_API_KEY") or ""
    if not api_key:
        return {"enabled": False}
    return {
        "enabled": True,
        "api_key": api_key,
        "url": os.environ.get("EASIIO_BREVO_API_URL") or "https://api.brevo.com/v3/smtp/email",
    }


def configured_smtp() -> dict[str, Any]:
    host = os.environ.get("EASIIO_SMTP_HOST") or os.environ.get("SMTP_HOST") or ""
    if not host:
        return {}
    return {
        "host": host,
        "port": int(os.environ.get("EASIIO_SMTP_PORT") or os.environ.get("SMTP_PORT") or "587"),
        "username": os.environ.get("EASIIO_SMTP_USERNAME") or os.environ.get("SMTP_USERNAME") or "",
        "password": os.environ.get("EASIIO_SMTP_PASSWORD") or os.environ.get("SMTP_PASSWORD") or "",
        "starttls": os.environ.get("EASIIO_SMTP_STARTTLS", "true").lower() not in {"0", "false", "no", "off"},
    }


def write_email_outbox(message: dict[str, Any]) -> dict[str, Any]:
    EMAIL_OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    outbox_id = f"email_{int(time.time() * 1000)}_{uuid.uuid4().hex[:10]}"
    path = EMAIL_OUTBOX_DIR / f"{outbox_id}.json"
    payload = {**message, "id": outbox_id, "status": "queued_dry_run", "created_at": int(time.time())}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"ok": True, "status": "queued_dry_run", "id": outbox_id, "path": str(path)}


def send_brevo_email_message(message_record: dict[str, Any]) -> dict[str, Any]:
    brevo = configured_brevo()
    if not brevo.get("enabled"):
        return {"ok": False, "status": "skipped", "error": "missing_brevo_api_key"}
    sender = {"email": message_record["from"]}
    if message_record.get("from_name"):
        sender["name"] = message_record["from_name"]
    payload = {
        "sender": sender,
        "to": [{"email": email} for email in message_record["to"]],
        "subject": message_record["subject"],
        "textContent": message_record["body"],
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        brevo["url"],
        data=data,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "api-key": brevo["api_key"],
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=SMTP_TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {"ok": True, "status": "sent", "provider": "brevo", "to": message_record["to"], "response_status": getattr(response, "status", 200), "response": body[:500]}
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")[:500]
        return {"ok": False, "status": "failed", "provider": "brevo", "error": f"brevo_http_{exc.code}", "response": error_body}
    except OSError as exc:
        return {"ok": False, "status": "failed", "provider": "brevo", "error": str(exc)[:200]}


def send_email_message(to: list[str], subject: str, body: str, config: dict[str, Any]) -> dict[str, Any]:
    to = sanitize_email_list(to)
    if not to:
        return {"ok": False, "status": "skipped", "error": "missing_recipient"}
    from_email = sanitize_email_address(config.get("from_email")) or sanitize_email_address(os.environ.get("EASIIO_EMAIL_FROM", "") or os.environ.get("EASIIO_EMAIL_FROM_EMAIL", "")) or "no-reply@example.local"
    from_name = sanitize_text(config.get("from_name") or os.environ.get("EASIIO_EMAIL_FROM_NAME") or "Easiio Website Assistant", 120)
    message_record = {"to": to, "from": from_email, "from_name": from_name, "subject": subject, "body": body}
    provider = sanitize_text(config.get("provider") or os.environ.get("EASIIO_EMAIL_PROVIDER") or "brevo", 30).lower()
    if provider == "brevo":
        brevo_result = send_brevo_email_message(message_record)
        if brevo_result.get("ok") or configured_brevo().get("enabled"):
            return brevo_result
    if provider == "outbox":
        return write_email_outbox(message_record)
    smtp = configured_smtp()
    if not smtp:
        return write_email_outbox(message_record)
    msg = EmailMessage()
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = ", ".join(to)
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(smtp["host"], smtp["port"], timeout=SMTP_TIMEOUT_SECONDS) as server:
        if smtp["starttls"]:
            server.starttls()
        if smtp["username"]:
            server.login(smtp["username"], smtp["password"])
        server.send_message(msg)
    return {"ok": True, "status": "sent", "to": to}


def run_email_agent_for_lead(*, site_id: str, contact: dict[str, Any] | None, is_new_contact: bool, lead: dict[str, Any]) -> dict[str, Any]:
    config = load_email_config_store().get(site_id) or default_email_agent_config()
    if not config.get("enabled") or not is_new_contact:
        return {"enabled": bool(config.get("enabled")), "sent": 0, "skipped": "disabled_or_existing_contact"}
    values = {
        "site_id": site_id,
        "site_name": lead.get("website_name") or lead.get("site_name") or site_id,
        "name": lead.get("name") or (contact or {}).get("name") or "there",
        "email": lead.get("email") or (contact or {}).get("email") or "",
        "phone": lead.get("phone") or (contact or {}).get("phone") or "",
        "company": lead.get("company") or "",
        "message": lead.get("message") or "",
        "page_url": lead.get("page_url") or "",
        "page_title": lead.get("page_title") or "",
        "session_id": lead.get("session_id") or "",
        "lead_score": lead.get("lead_score") or "",
    }
    results: list[dict[str, Any]] = []
    if config.get("send_welcome_email") and values["email"]:
        results.append(send_email_message(
            [values["email"]],
            render_email_template(config["welcome_subject"], values),
            render_email_template(config["welcome_body"], values),
            config,
        ))
    if config.get("send_owner_notification") and config.get("owner_recipients"):
        results.append(send_email_message(
            config["owner_recipients"],
            render_email_template(config["owner_subject"], values),
            render_email_template(config["owner_body"], values),
            config,
        ))
    return {"enabled": True, "sent": sum(1 for item in results if item.get("ok")), "results": results}


def index_manual_rag_content(site_id: str, items: list[dict[str, Any]]) -> None:
    existing = SITE_RAG_INDEX.setdefault(site_id, [])
    existing[:] = [chunk for chunk in existing if chunk.get("source") != "manual"]
    for item in items:
        content_id = sanitize_text(item.get("content_id") or item.get("id") or "", 120)
        page_context = {
            "url": item.get("url") or "",
            "title": item.get("title") or "",
            "content": item.get("content") or "",
        }
        existing.extend(_rag_chunks_from_page_context(site_id, page_context, source="manual", content_id=content_id))
    del existing[:-MAX_RAG_CHUNKS_PER_SITE]


def refresh_manual_rag_index(site_id: str) -> list[dict[str, Any]]:
    store = load_rag_content_store()
    items = store.get(site_id, [])
    index_manual_rag_content(site_id, items)
    return items


def rag_content_list_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    items = refresh_manual_rag_index(site_id)
    return json_response(200, {"ok": True, "site_id": site_id, "items": items})


def rag_content_upsert_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    content = sanitize_text(payload.get("content") or payload.get("text") or "", MAX_RAG_CONTENT_CHARS)
    if not content:
        return json_response(400, {"ok": False, "error": "content is required"})
    now = int(time.time())
    content_id = sanitize_text(payload.get("content_id") or payload.get("id") or "", 120) or "rag_" + uuid.uuid4().hex[:16]
    item = {
        "content_id": content_id,
        "title": sanitize_text(payload.get("title") or "Manual knowledge", 300),
        "url": sanitize_text(payload.get("url") or "", 500),
        "content": content,
        "updated_at": now,
    }
    store = load_rag_content_store()
    items = store.setdefault(site_id, [])
    for idx, existing in enumerate(items):
        if existing.get("content_id") == content_id:
            item["created_at"] = existing.get("created_at") or now
            items[idx] = item
            break
    else:
        item["created_at"] = now
        items.append(item)
    store[site_id] = items[-MAX_RAG_CHUNKS_PER_SITE:]
    save_rag_content_store(store)
    index_manual_rag_content(site_id, store[site_id])
    return json_response(200, {"ok": True, "site_id": site_id, "content_id": content_id, "item": item})


def rag_content_delete_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    content_id = sanitize_text(payload.get("content_id") or payload.get("id") or "", 120)
    if not content_id:
        return json_response(400, {"ok": False, "error": "content_id is required"})
    store = load_rag_content_store()
    items = store.get(site_id, [])
    kept = [item for item in items if item.get("content_id") != content_id]
    deleted = len(kept) != len(items)
    if kept:
        store[site_id] = kept
    else:
        store.pop(site_id, None)
    save_rag_content_store(store)
    index_manual_rag_content(site_id, kept)
    return json_response(200, {"ok": True, "site_id": site_id, "content_id": content_id, "deleted": deleted})


SYNC_SOURCE_PREFIXES = {
    "docs": "easiio-docs:",
    "wiki": "easiio-wiki:",
    "wordpress": "wordpress:",
    "upload": "upload:",
}
SYNCABLE_SOURCES = set(SYNC_SOURCE_PREFIXES)


def json_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []
    return []


def sqlite_table_exists(db_path: Path, table: str) -> bool:
    if not db_path.exists():
        return False
    try:
        with sqlite3.connect(db_path) as conn:
            row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
            return row is not None
    except sqlite3.Error:
        return False


def synced_content_id(source: str, site_id: str, slug: str) -> str:
    safe_slug = re.sub(r"[^A-Za-z0-9_.:-]+", "-", sanitize_text(slug, 160)).strip("-") or uuid.uuid4().hex[:12]
    return f"{SYNC_SOURCE_PREFIXES[source]}{site_id}:{safe_slug}"


def make_synced_rag_item(*, source: str, site_id: str, slug: str, title: str, summary: str = "", content: str = "", url: str = "", updated_at: Any = None, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    text_parts = [title, summary, content]
    combined = normalize_whitespace("\n".join(str(part or "") for part in text_parts))[:MAX_RAG_CONTENT_CHARS]
    now = int(time.time())
    try:
        updated = int(updated_at or now)
    except (TypeError, ValueError):
        updated = now
    item = {
        "content_id": synced_content_id(source, site_id, slug),
        "title": sanitize_text(title or slug or source, 300),
        "url": sanitize_text(url or f"{source}://{site_id}/{slug}", 500),
        "content": combined,
        "source": source,
        "synced_from": source,
        "updated_at": updated,
        "synced_at": now,
    }
    if metadata:
        item["metadata"] = {sanitize_text(key, 40): sanitize_text(value, 300) for key, value in metadata.items() if sanitize_text(key, 40)}
    return item


def fetch_docs_rag_items(site_id: str) -> list[dict[str, Any]]:
    if not sqlite_table_exists(DOCS_DB_PATH, "docs_documents"):
        return []
    items: list[dict[str, Any]] = []
    try:
        with sqlite3.connect(DOCS_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT * FROM docs_documents
                WHERE site_id=? AND status='published' AND visibility='public' AND rag_enabled=1
                ORDER BY updated_at DESC, title ASC
                """,
                (site_id,),
            ).fetchall()
    except sqlite3.Error:
        return []
    for row in rows:
        targets = [str(item) for item in json_list(row["framework_targets_json"])]
        if targets and "rag" not in targets:
            continue
        items.append(make_synced_rag_item(
            source="docs",
            site_id=site_id,
            slug=row["slug"],
            title=row["title"],
            summary=row["summary"],
            content=row["content"],
            url=f"easiio-docs://{site_id}/{row['slug']}",
            updated_at=row["updated_at"],
            metadata={"category": row["category"], "locale": row["locale"], "source_table": "docs_documents"},
        ))
    return [item for item in items if item.get("content")]


def fetch_wiki_rag_items(site_id: str) -> list[dict[str, Any]]:
    if not sqlite_table_exists(WIKI_DB_PATH, "wiki_pages"):
        return []
    try:
        with sqlite3.connect(WIKI_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT * FROM wiki_pages
                WHERE site_id=? AND status='published' AND rag_enabled=1
                ORDER BY updated_at DESC, title ASC
                """,
                (site_id,),
            ).fetchall()
    except sqlite3.Error:
        return []
    return [make_synced_rag_item(
        source="wiki",
        site_id=site_id,
        slug=row["slug"],
        title=row["title"],
        summary=row["summary"],
        content=row["content"],
        url=f"easiio-wiki://{site_id}/{row['slug']}",
        updated_at=row["updated_at"],
        metadata={"category": row["category"], "source_table": "wiki_pages"},
    ) for row in rows if row["content"]]


def normalize_sync_source(value: Any) -> str:
    source = sanitize_text(value, 40).lower().replace("-", "_")
    return source if source in SYNCABLE_SOURCES else ""


def strip_html_text(value: Any) -> str:
    text = str(value or "")
    text = re.sub(r"(?is)<(script|style).*?>.*?</\\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return normalize_whitespace(text)


def external_item_is_eligible(source: str, item: dict[str, Any]) -> bool:
    if item.get("rag_enabled") is False or item.get("sync_to_rag") is False:
        return False
    status = sanitize_text(item.get("status") or ("publish" if source == "wordpress" else "published"), 40).lower()
    visibility = sanitize_text(item.get("visibility") or "public", 40).lower()
    if source == "wordpress" and status not in {"publish", "published"}:
        return False
    if source == "upload" and status not in {"published", "publish", "ready", "active"}:
        return False
    return visibility in {"", "public"}


def sanitize_external_source_item(site_id: str, source: str, raw: dict[str, Any], index: int = 1) -> dict[str, Any] | None:
    content = sanitize_text(raw.get("content") or raw.get("text") or raw.get("body") or raw.get("extracted_text") or strip_html_text(raw.get("content_html") or raw.get("html") or ""), MAX_RAG_CONTENT_CHARS)
    if not content:
        return None
    slug = sanitize_text(raw.get("slug") or raw.get("id") or raw.get("content_id") or raw.get("filename") or f"item-{index}", 160)
    slug = re.sub(r"[^A-Za-z0-9_.:-]+", "-", slug).strip("-") or f"item-{index}"
    title = sanitize_text(raw.get("title") or raw.get("name") or raw.get("filename") or slug, 300)
    item = {
        "slug": slug,
        "title": title,
        "summary": sanitize_text(raw.get("summary") or raw.get("excerpt") or raw.get("description") or "", 1000),
        "content": content,
        "url": sanitize_text(raw.get("url") or raw.get("link") or f"{source}://{site_id}/{slug}", 500),
        "status": sanitize_text(raw.get("status") or ("publish" if source == "wordpress" else "published"), 40),
        "visibility": sanitize_text(raw.get("visibility") or "public", 40),
        "updated_at": raw.get("updated_at") or int(time.time()),
        "metadata": {
            "source_type": source,
            "filename": sanitize_text(raw.get("filename") or "", 160),
            "mime_type": sanitize_text(raw.get("mime_type") or raw.get("content_type") or "", 120),
        },
    }
    if raw.get("rag_enabled") is not None:
        item["rag_enabled"] = bool(raw.get("rag_enabled"))
    if raw.get("sync_to_rag") is not None:
        item["sync_to_rag"] = bool(raw.get("sync_to_rag"))
    return item


def load_external_source_store() -> dict[str, dict[str, list[dict[str, Any]]]]:
    items = load_json_items(RAG_EXTERNAL_SOURCES_PATH)
    store: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for item in items:
        site_id = sanitize_text(item.get("site_id") or "default", 100)
        source = normalize_sync_source(item.get("source"))
        if source not in {"wordpress", "upload"}:
            continue
        clean = {key: value for key, value in item.items() if key not in {"site_id", "source"}}
        store.setdefault(site_id, {}).setdefault(source, []).append(clean)
    return store


def save_external_source_store(store: dict[str, dict[str, list[dict[str, Any]]]]) -> None:
    items: list[dict[str, Any]] = []
    for site_id, by_source in sorted(store.items()):
        for source, source_items in sorted(by_source.items()):
            for item in source_items:
                copy = dict(item)
                copy["site_id"] = site_id
                copy["source"] = source
                items.append(copy)
    save_json_items(RAG_EXTERNAL_SOURCES_PATH, items)


def external_source_items(site_id: str, source: str, eligible_only: bool = False) -> list[dict[str, Any]]:
    source = normalize_sync_source(source)
    if source not in {"wordpress", "upload"}:
        return []
    items = load_external_source_store().get(site_id, {}).get(source, [])
    if eligible_only:
        return [item for item in items if external_item_is_eligible(source, item)]
    return items


def payload_external_rag_items(site_id: str, source: str, raw_items: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_items, list):
        return []
    sanitized = [sanitize_external_source_item(site_id, source, raw, index) for index, raw in enumerate(raw_items[:100], 1) if isinstance(raw, dict)]
    source_items = [item for item in sanitized if item and external_item_is_eligible(source, item)]
    return external_source_rag_items(site_id, source, source_items)


def external_source_rag_items(site_id: str, source: str, source_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for item in source_items[:100]:
        if not external_item_is_eligible(source, item):
            continue
        metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
        items.append(make_synced_rag_item(
            source=source,
            site_id=site_id,
            slug=item.get("slug") or item.get("title") or source,
            title=item.get("title") or item.get("slug") or source,
            summary=item.get("summary") or "",
            content=item.get("content") or "",
            url=item.get("url") or f"{source}://{site_id}/{item.get('slug') or ''}",
            updated_at=item.get("updated_at"),
            metadata={**metadata, "external": "true"},
        ))
    return [item for item in items if item.get("content")]


def source_rag_items(site_id: str, source: str, payload: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    if source == "docs":
        return fetch_docs_rag_items(site_id)
    if source == "wiki":
        return fetch_wiki_rag_items(site_id)
    if source == "wordpress":
        payload_items = payload_external_rag_items(site_id, "wordpress", (payload or {}).get("wordpress_items") or (payload or {}).get("items"))
        return payload_items or external_source_rag_items(site_id, "wordpress", external_source_items(site_id, "wordpress", eligible_only=True))
    if source == "upload":
        payload_items = payload_external_rag_items(site_id, "upload", (payload or {}).get("upload_items") or (payload or {}).get("documents"))
        return payload_items or external_source_rag_items(site_id, "upload", external_source_items(site_id, "upload", eligible_only=True))
    return []


def rag_source_items_list_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    source = normalize_sync_source(payload.get("source"))
    if source not in {"wordpress", "upload"}:
        return json_response(400, {"ok": False, "error": "source must be wordpress or upload"})
    items = external_source_items(site_id, source, eligible_only=False)
    return json_response(200, {"ok": True, "site_id": site_id, "source": source, "items": items, "eligible_count": len([item for item in items if external_item_is_eligible(source, item)])})


def rag_source_items_upsert_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    source = normalize_sync_source(payload.get("source"))
    if source not in {"wordpress", "upload"}:
        return json_response(400, {"ok": False, "error": "source must be wordpress or upload"})
    raw_items = payload.get("items") or payload.get("documents") or payload.get(f"{source}_items")
    if not isinstance(raw_items, list):
        return json_response(400, {"ok": False, "error": "items must be a list"})
    sanitized = [sanitize_external_source_item(site_id, source, raw, index) for index, raw in enumerate(raw_items[:100], 1) if isinstance(raw, dict)]
    new_items = [item for item in sanitized if item]
    store = load_external_source_store()
    existing = store.setdefault(site_id, {}).setdefault(source, [])
    by_slug = {str(item.get("slug") or ""): item for item in existing if item.get("slug")}
    for item in new_items:
        by_slug[str(item.get("slug"))] = item
    store[site_id][source] = list(by_slug.values())
    save_external_source_store(store)
    eligible_count = len([item for item in store[site_id][source] if external_item_is_eligible(source, item)])
    return json_response(200, {"ok": True, "site_id": site_id, "source": source, "stored_count": len(store[site_id][source]), "eligible_count": eligible_count})


def rag_source_items_delete_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    source = normalize_sync_source(payload.get("source"))
    slug = sanitize_text(payload.get("slug") or payload.get("content_id") or "", 160)
    if source not in {"wordpress", "upload"} or not slug:
        return json_response(400, {"ok": False, "error": "source and slug are required"})
    store = load_external_source_store()
    existing = store.get(site_id, {}).get(source, [])
    kept = [item for item in existing if str(item.get("slug") or "") != slug]
    deleted = len(kept) != len(existing)
    store.setdefault(site_id, {})[source] = kept
    save_external_source_store(store)
    return json_response(200, {"ok": True, "site_id": site_id, "source": source, "slug": slug, "deleted": deleted})


def public_http_base_url(value: Any) -> str:
    raw = sanitize_text(value, 500).rstrip("/")
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    host = parsed.hostname or ""
    if host in {"localhost", "127.0.0.1", "::1"} or host.endswith(".localhost"):
        return ""
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")


def rendered_text(value: Any) -> str:
    if isinstance(value, dict):
        value = value.get("rendered") or value.get("raw") or ""
    return html.unescape(strip_html_text(value))


def wordpress_post_to_source_item(post: dict[str, Any], post_type: str, index: int = 1) -> dict[str, Any] | None:
    slug = sanitize_text(post.get("slug") or post.get("id") or f"wp-{index}", 160)
    title = rendered_text(post.get("title")) or slug
    excerpt = rendered_text(post.get("excerpt"))
    content = rendered_text(post.get("content"))
    if not content and not excerpt:
        return None
    return sanitize_external_source_item("", "wordpress", {
        "slug": slug,
        "title": title,
        "summary": excerpt,
        "content": content or excerpt,
        "url": post.get("link") or post.get("guid", {}).get("rendered") or "",
        "status": post.get("status") or "publish",
        "visibility": "public" if post.get("status") in {None, "publish", "published"} else "private",
        "updated_at": post.get("modified_gmt") or post.get("modified") or int(time.time()),
        "content_type": f"wordpress/{post_type}",
    }, index)


def save_source_items(site_id: str, source: str, new_items: list[dict[str, Any]]) -> tuple[int, int]:
    store = load_external_source_store()
    existing = store.setdefault(site_id, {}).setdefault(source, [])
    by_slug = {str(item.get("slug") or ""): item for item in existing if item.get("slug")}
    for item in new_items:
        by_slug[str(item.get("slug"))] = item
    store[site_id][source] = list(by_slug.values())
    save_external_source_store(store)
    eligible_count = len([item for item in store[site_id][source] if external_item_is_eligible(source, item)])
    return len(store[site_id][source]), eligible_count


def rag_wordpress_pull_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    if payload.get("confirm_pull") is not True and payload.get("confirmPull") is not True:
        return json_response(400, {"ok": False, "error": "confirm_pull is required before pulling WordPress content", "requires_pull_approval": True})
    base_url = public_http_base_url(payload.get("base_url") or payload.get("wordpress_url"))
    if not base_url:
        return json_response(400, {"ok": False, "error": "base_url must be a public http(s) WordPress URL"})
    raw_types = payload.get("post_types") if isinstance(payload.get("post_types"), list) else [payload.get("post_type") or "pages", "posts"]
    post_types = []
    for raw in raw_types:
        post_type = sanitize_text(raw, 40).lower().strip("/")
        if post_type in {"page", "pages"}:
            post_type = "pages"
        elif post_type in {"post", "posts"}:
            post_type = "posts"
        if post_type in {"pages", "posts"} and post_type not in post_types:
            post_types.append(post_type)
    per_page = max(1, min(int(payload.get("per_page") or 20), 100))
    headers = {"Accept": "application/json", "User-Agent": "EasiioChatbotRAG/1.0"}
    auth_env = sanitize_text(payload.get("auth_env") or "", 120)
    auth_value = os.environ.get(auth_env, "") if auth_env else ""
    if auth_value:
        token = base64.b64encode(auth_value.encode()).decode()
        headers["Authorization"] = f"Basic {token}"
    pulled_items: list[dict[str, Any]] = []
    errors: list[str] = []
    for post_type in post_types:
        query = urlencode({"per_page": per_page, "status": "publish", "_fields": "id,slug,link,status,title,excerpt,content,modified,modified_gmt"})
        url = f"{base_url}/wp-json/wp/v2/{post_type}?{query}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                raw_body = response.read().decode("utf-8", errors="replace")
            data = json.loads(raw_body)
        except Exception as exc:  # noqa: BLE001 - sanitized API response
            errors.append(f"{post_type}: {type(exc).__name__}")
            continue
        if isinstance(data, dict):
            data = data.get("items") or data.get("data") or []
        if not isinstance(data, list):
            continue
        for index, post in enumerate(data[:per_page], 1):
            if isinstance(post, dict):
                item = wordpress_post_to_source_item(post, post_type, index)
                if item:
                    pulled_items.append(item)
    stored_count, eligible_count = save_source_items(site_id, "wordpress", pulled_items) if pulled_items else (len(external_source_items(site_id, "wordpress")), len(external_source_items(site_id, "wordpress", eligible_only=True)))
    return json_response(200, {"ok": True, "site_id": site_id, "source": "wordpress", "pulled_count": len(pulled_items), "stored_count": stored_count, "eligible_count": eligible_count, "errors": errors[:5]})


def extract_docx_text(data: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="replace")
    except (KeyError, zipfile.BadZipFile, OSError):
        return ""
    parts = re.findall(r"<w:t[^>]*>(.*?)</w:t>", xml, flags=re.S)
    return normalize_whitespace(" ".join(html.unescape(re.sub(r"<[^>]+>", " ", part)) for part in parts))


def extract_pdf_text_best_effort(data: bytes) -> str:
    try:
        import fitz  # type: ignore
    except Exception:
        return ""
    try:
        doc = fitz.open(stream=data, filetype="pdf")
        return normalize_whitespace("\n".join(page.get_text("text") for page in doc))
    except Exception:
        return ""


def extract_upload_text(filename: str, mime_type: str, data: bytes) -> tuple[str, str]:
    lower = filename.lower()
    mime = mime_type.lower()
    if lower.endswith(".docx") or "wordprocessingml" in mime:
        return extract_docx_text(data), "docx"
    if lower.endswith(".pdf") or mime == "application/pdf":
        return extract_pdf_text_best_effort(data), "pdf"
    decoded = data.decode("utf-8", errors="replace")
    if lower.endswith(('.html', '.htm')) or "html" in mime:
        return strip_html_text(decoded), "html"
    return normalize_whitespace(decoded), "text"


def rag_upload_extract_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    if payload.get("confirm_extract") is not True and payload.get("confirmExtract") is not True:
        return json_response(400, {"ok": False, "error": "confirm_extract is required before staging uploaded document text", "requires_extract_approval": True})
    filename = sanitize_text(payload.get("filename") or "uploaded-document.txt", 180)
    mime_type = sanitize_text(payload.get("mime_type") or payload.get("content_type") or "text/plain", 120)
    if payload.get("content_base64"):
        try:
            data = base64.b64decode(str(payload.get("content_base64")), validate=True)
        except Exception:
            return json_response(400, {"ok": False, "error": "content_base64 is invalid"})
    else:
        data = str(payload.get("content") or payload.get("text") or "").encode("utf-8")
    if not data or len(data) > MAX_RAG_UPLOAD_BYTES:
        return json_response(400, {"ok": False, "error": "document content is empty or too large"})
    text, extraction_method = extract_upload_text(filename, mime_type, data)
    text = sanitize_text(text, MAX_RAG_CONTENT_CHARS)
    if not text:
        return json_response(400, {"ok": False, "error": "no text could be extracted from document"})
    slug = sanitize_text(payload.get("slug") or Path(filename).stem or uuid.uuid4().hex[:10], 160)
    item = sanitize_external_source_item(site_id, "upload", {
        "slug": slug,
        "title": payload.get("title") or Path(filename).stem or filename,
        "filename": filename,
        "mime_type": mime_type,
        "status": payload.get("status") or "published",
        "visibility": payload.get("visibility") or "public",
        "content": text,
        "summary": payload.get("summary") or f"Extracted from {filename}",
        "url": payload.get("url") or f"upload://{site_id}/{slug}",
    })
    if not item:
        return json_response(400, {"ok": False, "error": "document could not be staged"})
    item.setdefault("metadata", {})["extraction_method"] = extraction_method
    stored_count, eligible_count = save_source_items(site_id, "upload", [item])
    return json_response(200, {"ok": True, "site_id": site_id, "source": "upload", "slug": item["slug"], "stored_count": stored_count, "eligible_count": eligible_count, "extraction_method": extraction_method, "text_preview": mask_pii(text, 500)})


def load_last_rag_sync(site_id: str) -> dict[str, Any] | None:
    items = [item for item in load_json_items(RAG_SYNC_LOG_PATH) if item.get("site_id") == site_id]
    return items[-1] if items else None


def append_rag_sync_log(item: dict[str, Any]) -> None:
    items = load_json_items(RAG_SYNC_LOG_PATH)
    items.append(item)
    save_json_items(RAG_SYNC_LOG_PATH, items[-200:])


def content_fingerprint(item: dict[str, Any]) -> str:
    material = "\n".join(str(item.get(key) or "") for key in ("title", "url", "content"))
    return hashlib.sha256(material.encode("utf-8", errors="replace")).hexdigest()[:16]


def sync_prefixes_for_sources(sources: list[str]) -> tuple[str, ...]:
    return tuple(SYNC_SOURCE_PREFIXES[source] for source in sources if source in SYNC_SOURCE_PREFIXES)


def review_diff_preview(old_item: dict[str, Any] | None, new_item: dict[str, Any] | None) -> str:
    old_text = normalize_whitespace((old_item or {}).get("content") or "")[:1200]
    new_text = normalize_whitespace((new_item or {}).get("content") or "")[:1200]
    if old_text == new_text:
        return ""
    old_lines = old_text.splitlines() or ([old_text] if old_text else [])
    new_lines = new_text.splitlines() or ([new_text] if new_text else [])
    diff = list(difflib.unified_diff(old_lines, new_lines, fromfile="current", tofile="upstream", lineterm=""))
    return "\n".join(diff[:24])[:2000]


def build_rag_sync_review(site_id: str, sources: list[str], payload: dict[str, Any] | None = None) -> dict[str, Any]:
    requested = []
    for raw in sources:
        source = normalize_sync_source(raw)
        if source and source not in requested:
            requested.append(source)
    if not requested:
        requested = ["docs", "wiki", "wordpress", "upload"]
    new_items = [item for source in requested for item in source_rag_items(site_id, source, payload or {})]
    store_items = load_rag_content_store().get(site_id, [])
    prefixes = sync_prefixes_for_sources(requested)
    existing_synced = [item for item in store_items if str(item.get("content_id") or "").startswith(prefixes)] if prefixes else []
    new_by_id = {str(item.get("content_id") or ""): item for item in new_items if item.get("content_id")}
    old_by_id = {str(item.get("content_id") or ""): item for item in existing_synced if item.get("content_id")}
    review_items: list[dict[str, Any]] = []
    summary = {"new": 0, "changed": 0, "unchanged": 0, "deleted_upstream": 0, "total": 0}
    for content_id, item in sorted(new_by_id.items()):
        old = old_by_id.get(content_id)
        if old is None:
            status = "new"
        elif content_fingerprint(old) == content_fingerprint(item):
            status = "unchanged"
        else:
            status = "changed"
        summary[status] += 1
        review_items.append({
            "content_id": content_id,
            "title": item.get("title") or "",
            "url": item.get("url") or "",
            "source": item.get("synced_from") or item.get("source") or "",
            "review_status": status,
            "current_updated_at": old.get("updated_at") if old else None,
            "upstream_updated_at": item.get("updated_at"),
            "diff_preview": review_diff_preview(old, item) if status == "changed" else "",
            "text_preview": mask_pii(item.get("content") or "", 320),
        })
    for content_id, old in sorted(old_by_id.items()):
        if content_id in new_by_id:
            continue
        summary["deleted_upstream"] += 1
        review_items.append({
            "content_id": content_id,
            "title": old.get("title") or "",
            "url": old.get("url") or "",
            "source": old.get("synced_from") or old.get("source") or "",
            "review_status": "deleted_upstream",
            "current_updated_at": old.get("updated_at"),
            "upstream_updated_at": None,
            "diff_preview": review_diff_preview(old, None),
            "text_preview": mask_pii(old.get("content") or "", 320),
        })
    summary["total"] = len(review_items)
    return {"summary": summary, "items": review_items, "requested_sources": requested}


def rag_sync_preview_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    raw_sources = payload.get("sources") if isinstance(payload.get("sources"), list) else ["docs", "wiki", "wordpress", "upload"]
    review = build_rag_sync_review(site_id, raw_sources, payload)
    return json_response(200, {"ok": True, "site_id": site_id, "sources": review["requested_sources"], "summary": review["summary"], "items": review["items"][:100], "last_sync": load_last_rag_sync(site_id) or {}})


def rag_review_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    raw_sources = payload.get("sources") or "docs,wiki,wordpress,upload"
    sources = [item.strip() for item in str(raw_sources).split(",") if item.strip()]
    review = build_rag_sync_review(site_id, sources, {})
    source_status = rag_sources_status_body(site_id)
    return json_response(200, {"ok": True, "site_id": site_id, "sources": source_status["sources"], "stored_source_counts": source_status["stored_source_counts"], "last_sync": source_status["last_sync"], "summary": review["summary"], "items": review["items"][:100]})


def rag_sources_status_body(site_id: str) -> dict[str, Any]:
    store_items = load_rag_content_store().get(site_id, [])
    source_counts: dict[str, int] = {}
    for item in store_items:
        source = sanitize_text(item.get("synced_from") or item.get("source") or "manual", 40) or "manual"
        source_counts[source] = source_counts.get(source, 0) + 1
    wordpress_items = external_source_items(site_id, "wordpress", eligible_only=False)
    upload_items = external_source_items(site_id, "upload", eligible_only=False)
    sources = {
        "manual": {"stored_count": len(store_items), "editable": True},
        "docs": {"eligible_count": len(fetch_docs_rag_items(site_id)), "db_configured": DOCS_DB_PATH.exists(), "db_path_configured": bool(str(DOCS_DB_PATH))},
        "wiki": {"eligible_count": len(fetch_wiki_rag_items(site_id)), "db_configured": WIKI_DB_PATH.exists(), "db_path_configured": bool(str(WIKI_DB_PATH))},
        "wordpress": {"eligible_count": len([item for item in wordpress_items if external_item_is_eligible("wordpress", item)]), "stored_count": len(wordpress_items), "requires_payload": False, "editable": True},
        "upload": {"eligible_count": len([item for item in upload_items if external_item_is_eligible("upload", item)]), "stored_count": len(upload_items), "requires_payload": False, "editable": True},
    }
    last_sync = load_last_rag_sync(site_id) or {}
    review = build_rag_sync_review(site_id, ["docs", "wiki", "wordpress", "upload"], {})
    return {"sources": sources, "stored_source_counts": source_counts, "last_sync": last_sync, "review_summary": review["summary"]}


def rag_sources_status_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    body = rag_sources_status_body(site_id)
    return json_response(200, {"ok": True, "site_id": site_id, **body})


def rag_sync_sources_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    if payload.get("confirm_sync") is not True and payload.get("confirmSync") is not True:
        return json_response(400, {"ok": False, "error": "confirm_sync is required before writing multi-source RAG content", "requires_sync_approval": True})
    raw_sources = payload.get("sources") if isinstance(payload.get("sources"), list) else ["docs", "wiki"]
    requested = []
    for raw in raw_sources:
        source = normalize_sync_source(raw)
        if source and source not in requested:
            requested.append(source)
    if not requested:
        return json_response(400, {"ok": False, "error": "at least one valid source is required"})
    source_items: dict[str, list[dict[str, Any]]] = {source: source_rag_items(site_id, source, payload) for source in requested}
    synced_items = [item for source in requested for item in source_items[source]]
    synced_prefixes = tuple(SYNC_SOURCE_PREFIXES[source] for source in requested)
    store = load_rag_content_store()
    existing = store.get(site_id, [])
    snapshot_before = json.loads(json.dumps(existing))
    kept = [item for item in existing if not str(item.get("content_id") or "").startswith(synced_prefixes)]
    store[site_id] = kept + synced_items
    snapshot_after = json.loads(json.dumps(store[site_id]))
    save_rag_content_store(store)
    index_manual_rag_content(site_id, store[site_id])
    source_counts = {source: len(source_items[source]) for source in requested}
    rollback_id = f"rag-sync-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    review = build_rag_sync_review(site_id, requested, payload)
    log_item = {
        "site_id": site_id,
        "rollback_id": rollback_id,
        "sources": requested,
        "source_counts": source_counts,
        "review_summary": review.get("summary", {}),
        "synced_items": len(synced_items),
        "kept_manual_items": len(kept),
        "snapshot_before": snapshot_before,
        "snapshot_after": snapshot_after,
        "approved_by": mask_pii(payload.get("approved_by") or payload.get("approvedBy") or "", 160),
        "created_at": int(time.time()),
    }
    append_rag_sync_log(log_item)
    public_summary = {key: value for key, value in log_item.items() if key not in {"snapshot_before", "snapshot_after"}}
    return json_response(200, {"ok": True, "site_id": site_id, "summary": public_summary, "items": synced_items[:50]})


def rag_rollback_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    rollback_id = sanitize_text(payload.get("rollback_id") or payload.get("rollbackId") or "", 120)
    if payload.get("confirm_rollback") is not True and payload.get("confirmRollback") is not True:
        return json_response(400, {"ok": False, "error": "confirm_rollback is required before restoring previous RAG sync content", "requires_rollback_approval": True})
    if not rollback_id:
        return json_response(400, {"ok": False, "error": "rollback_id is required"})
    candidates = [item for item in load_json_items(RAG_SYNC_LOG_PATH) if item.get("site_id") == site_id and item.get("rollback_id") == rollback_id]
    if not candidates:
        return json_response(404, {"ok": False, "error": "rollback snapshot not found"})
    log_item = candidates[-1]
    snapshot_before = log_item.get("snapshot_before")
    if not isinstance(snapshot_before, list):
        return json_response(400, {"ok": False, "error": "rollback snapshot is unavailable"})
    clean_snapshot = [item for item in snapshot_before if isinstance(item, dict)]
    store = load_rag_content_store()
    store[site_id] = clean_snapshot
    save_rag_content_store(store)
    index_manual_rag_content(site_id, store[site_id])
    rollback_log = {
        "site_id": site_id,
        "rollback_of": rollback_id,
        "sources": log_item.get("sources") or [],
        "restored_items": len(clean_snapshot),
        "approved_by": mask_pii(payload.get("approved_by") or payload.get("approvedBy") or "", 160),
        "created_at": int(time.time()),
        "event": "rollback",
    }
    append_rag_sync_log(rollback_log)
    public_log = {key: value for key, value in rollback_log.items() if key != "approved_by" or value}
    return json_response(200, {"ok": True, "site_id": site_id, "summary": public_log})


DEFAULT_RAG_REFRESH_SCHEDULE: dict[str, Any] = {
    "enabled": False,
    "sources": ["docs", "wiki", "wordpress", "upload"],
    "interval_minutes": 1440,
    "stale_after_minutes": 2880,
    "notify_on_changes": True,
    "notify_recipients": [],
    "auto_sync": False,
    "last_checked_at": 0,
    "last_run_at": 0,
}


def load_rag_schedule_store() -> dict[str, dict[str, Any]]:
    try:
        raw = json.loads(RAG_REFRESH_SCHEDULE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    sites = raw.get("sites", raw) if isinstance(raw, dict) else {}
    if not isinstance(sites, dict):
        return {}
    return {sanitize_text(site_id, 100): sanitize_rag_refresh_schedule(config) for site_id, config in sites.items() if isinstance(site_id, str) and isinstance(config, dict)}


def save_rag_schedule_store(store: dict[str, dict[str, Any]]) -> None:
    RAG_REFRESH_SCHEDULE_PATH.parent.mkdir(parents=True, exist_ok=True)
    RAG_REFRESH_SCHEDULE_PATH.write_text(json.dumps({"version": 1, "sites": store}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sanitize_rag_refresh_schedule(config: dict[str, Any]) -> dict[str, Any]:
    base = dict(DEFAULT_RAG_REFRESH_SCHEDULE)
    sources: list[str] = []
    raw_sources = config.get("sources", config.get("sync_sources", base["sources"]))
    if not isinstance(raw_sources, list):
        raw_sources = str(raw_sources or "").split(",")
    for raw in raw_sources:
        source = normalize_sync_source(raw)
        if source and source not in sources:
            sources.append(source)
    if not sources:
        sources = list(base["sources"])
    def int_between(value: Any, fallback: int, low: int, high: int) -> int:
        try:
            number = int(value)
        except (TypeError, ValueError):
            number = fallback
        return max(low, min(high, number))
    return {
        "enabled": bool(config.get("enabled", base["enabled"])),
        "sources": sources,
        "interval_minutes": int_between(config.get("interval_minutes", config.get("intervalMinutes", base["interval_minutes"])), base["interval_minutes"], 5, 43200),
        "stale_after_minutes": int_between(config.get("stale_after_minutes", config.get("staleAfterMinutes", base["stale_after_minutes"])), base["stale_after_minutes"], 5, 129600),
        "notify_on_changes": bool(config.get("notify_on_changes", config.get("notifyOnChanges", base["notify_on_changes"]))),
        "notify_recipients": sanitize_email_list(config.get("notify_recipients", config.get("notifyRecipients", base["notify_recipients"]))),
        "auto_sync": bool(config.get("auto_sync", config.get("autoSync", base["auto_sync"]))),
        "last_checked_at": int_between(config.get("last_checked_at", config.get("lastCheckedAt", base["last_checked_at"])), base["last_checked_at"], 0, 4102444800),
        "last_run_at": int_between(config.get("last_run_at", config.get("lastRunAt", base["last_run_at"])), base["last_run_at"], 0, 4102444800),
    }


def public_rag_schedule(schedule: dict[str, Any]) -> dict[str, Any]:
    public = dict(schedule)
    public["notification_recipient_count"] = len(schedule.get("notify_recipients") or [])
    return public


def rag_refresh_schedule_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    store = load_rag_schedule_store()
    schedule = store.get(site_id) or sanitize_rag_refresh_schedule({})
    return json_response(200, {"ok": True, "site_id": site_id, "schedule": public_rag_schedule(schedule)})


def rag_refresh_schedule_upsert_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    raw = payload.get("schedule") or payload.get("refresh_schedule") or payload
    if not isinstance(raw, dict):
        return json_response(400, {"ok": False, "error": "schedule must be an object"})
    schedule = sanitize_rag_refresh_schedule(raw)
    store = load_rag_schedule_store()
    store[site_id] = schedule
    save_rag_schedule_store(store)
    return json_response(200, {"ok": True, "site_id": site_id, "schedule": public_rag_schedule(schedule)})


def rag_schedule_is_due(schedule: dict[str, Any], now: int | None = None) -> bool:
    if not schedule.get("enabled"):
        return False
    now = int(now or time.time())
    interval_seconds = int(schedule.get("interval_minutes") or 1440) * 60
    last_checked = int(schedule.get("last_checked_at") or schedule.get("last_run_at") or 0)
    return last_checked <= 0 or now - last_checked >= interval_seconds


def rag_refresh_due_handler(payload: dict[str, Any]) -> Response:
    now = int(time.time())
    store = load_rag_schedule_store()
    due_sites = []
    for site_id, schedule in sorted(store.items()):
        if rag_schedule_is_due(schedule, now):
            due_sites.append({"site_id": site_id, "sources": schedule.get("sources") or [], "interval_minutes": schedule.get("interval_minutes"), "last_checked_at": schedule.get("last_checked_at") or 0})
    return json_response(200, {"ok": True, "due_sites": due_sites, "count": len(due_sites), "checked_at": now})


def load_rag_notifications() -> list[dict[str, Any]]:
    return load_json_items(RAG_NOTIFICATIONS_PATH)


def save_rag_notifications(items: list[dict[str, Any]]) -> None:
    save_json_items(RAG_NOTIFICATIONS_PATH, items[-300:])


def public_rag_notification(item: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in item.items() if key not in {"notify_recipients", "email_results"}}


def append_rag_notification(site_id: str, schedule: dict[str, Any], review: dict[str, Any], *, action: str, rollback_id: str = "") -> dict[str, Any]:
    summary = review.get("summary") or {}
    notification = {
        "notification_id": f"rag-note-{int(time.time())}-{uuid.uuid4().hex[:8]}",
        "site_id": site_id,
        "type": "rag_refresh",
        "action": action,
        "sources": schedule.get("sources") or [],
        "review_summary": summary,
        "rollback_id": rollback_id,
        "message": f"RAG refresh found new={summary.get('new', 0)}, changed={summary.get('changed', 0)}, deleted_upstream={summary.get('deleted_upstream', 0)}.",
        "unread": True,
        "created_at": int(time.time()),
        "notify_recipient_count": len(schedule.get("notify_recipients") or []),
        "notify_recipients": sanitize_email_list(schedule.get("notify_recipients") or []),
    }
    recipients = notification["notify_recipients"]
    if recipients:
        email_config = load_email_config_store().get(site_id) or default_email_agent_config()
        email_config = {**email_config, "enabled": True}
        subject = f"RAG refresh review for {site_id}"
        body = f"{notification['message']}\n\nAction: {action}\nSources: {', '.join(notification['sources'])}\nReview this in the protected chatbot admin console."
        result = send_email_message(recipients, subject, body, email_config)
        notification["email_results"] = [{key: value for key, value in result.items() if key not in {"to", "path", "response"}}]
    items = load_rag_notifications()
    items.append(notification)
    save_rag_notifications(items)
    return public_rag_notification(notification)


def rag_notifications_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "", 100)
    items = [public_rag_notification(item) for item in load_rag_notifications() if not site_id or item.get("site_id") == site_id]
    items = list(reversed(items[-100:]))
    return json_response(200, {"ok": True, "site_id": site_id or None, "items": items, "unread_count": sum(1 for item in items if item.get("unread"))})


def rag_notification_read_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "", 100)
    notification_id = sanitize_text(payload.get("notification_id") or payload.get("notificationId") or "", 120)
    mark_all = bool(payload.get("mark_all") or payload.get("markAll"))
    items = load_rag_notifications()
    changed = 0
    for item in items:
        if site_id and item.get("site_id") != site_id:
            continue
        if mark_all or (notification_id and item.get("notification_id") == notification_id):
            if item.get("unread"):
                item["unread"] = False
                item["read_at"] = int(time.time())
                changed += 1
    save_rag_notifications(items)
    remaining = [item for item in items if (not site_id or item.get("site_id") == site_id) and item.get("unread")]
    return json_response(200, {"ok": True, "site_id": site_id or None, "updated": changed, "unread_count": len(remaining)})


def review_has_changes(review: dict[str, Any]) -> bool:
    summary = review.get("summary") or {}
    return any(int(summary.get(key) or 0) > 0 for key in ("new", "changed", "deleted_upstream"))


def run_one_rag_scheduled_refresh(site_id: str, schedule: dict[str, Any], *, dry_run: bool) -> dict[str, Any]:
    review = build_rag_sync_review(site_id, schedule.get("sources") or [], {})
    changed = review_has_changes(review)
    action = "no_changes"
    rollback_id = ""
    if changed and schedule.get("auto_sync") and not dry_run:
        sync_payload = {"site_id": site_id, "sources": schedule.get("sources") or [], "confirm_sync": True, "approved_by": "scheduled_refresh"}
        sync = rag_sync_sources_handler(sync_payload)
        if sync.status == 200 and sync.body.get("ok"):
            action = "synced"
            rollback_id = ((sync.body.get("summary") or {}).get("rollback_id") or "")
        else:
            action = "sync_failed"
    elif changed:
        action = "preview_only"
    if changed and schedule.get("notify_on_changes"):
        append_rag_notification(site_id, schedule, review, action=action, rollback_id=rollback_id)
    return {"site_id": site_id, "sources": schedule.get("sources") or [], "action": action, "changed": changed, "review_summary": review.get("summary") or {}, "rollback_id": rollback_id}


def rag_run_scheduled_refresh_handler(payload: dict[str, Any]) -> Response:
    site_filter = sanitize_text(payload.get("site_id") or "", 100)
    dry_run = bool(payload.get("dry_run") or payload.get("dryRun"))
    force = bool(payload.get("force")) or bool(site_filter)
    now = int(time.time())
    store = load_rag_schedule_store()
    results = []
    for site_id, schedule in sorted(store.items()):
        if site_filter and site_id != site_filter:
            continue
        if not force and not rag_schedule_is_due(schedule, now):
            continue
        if not schedule.get("enabled"):
            continue
        result = run_one_rag_scheduled_refresh(site_id, schedule, dry_run=dry_run)
        results.append(result)
        schedule["last_checked_at"] = now
        if result["action"] in {"synced", "preview_only", "no_changes"}:
            schedule["last_run_at"] = now
        store[site_id] = schedule
    save_rag_schedule_store(store)
    return json_response(200, {"ok": True, "dry_run": dry_run, "results": results, "checked_at": now})


def find_lesson_number(text: str) -> str:
    match = re.search(r"(?:Lesson\s*|第\s*)(\d+)(?:\s*课)?", text, re.I)
    return match.group(1) if match else ""



def classify_rag_intent(question: str) -> str:
    text = str(question or "").lower()
    if re.search(r"\b(compare|difference|versus|vs)\b|区别|比较", text):
        return "comparison"
    if re.search(r"\b(how to|steps|setup|configure|install|use)\b|如何|怎么|步骤", text):
        return "procedure"
    if re.search(r"\b(summary|summarize|overview)\b|总结|概括", text):
        return "summary"
    if re.search(r"\b(error|issue|troubleshoot|fix|problem)\b|错误|问题|排查", text):
        return "troubleshooting"
    if re.search(r"\b(extract|list|show me|table)\b|列出|提取", text):
        return "extraction"
    return "fact_lookup"


def build_rag_query_plan(question: str, language: str = "") -> dict[str, Any]:
    original = normalize_whitespace(question)
    base_tokens = tokenize(original)
    expanded_tokens = set(base_tokens)
    for token in list(base_tokens):
        for synonym in RAG_QUERY_SYNONYMS.get(token, []):
            expanded_tokens.update(tokenize(synonym))
            expanded_tokens.add(synonym.lower())
    numbers = re.findall(r"\d+", original)
    keywords = sorted(token for token in expanded_tokens if token)
    expanded_query = normalize_whitespace(" ".join([original] + keywords))
    metadata_query = normalize_whitespace(" ".join([original, "title section summary source", *numbers]))
    hyde_queries = call_llm_hyde_queries(original, language) if RAG_HYDE_ENABLED else []
    queries = [original]
    if expanded_query and expanded_query != original:
        queries.append(expanded_query)
    if metadata_query and metadata_query not in queries:
        queries.append(metadata_query)
    queries.extend(hyde_queries)
    return {
        "intent": classify_rag_intent(original),
        "question": original,
        "language": language,
        "queries": queries,
        "keywords": keywords,
        "original_tokens": base_tokens,
        "expanded_tokens": expanded_tokens,
        "hyde_queries": hyde_queries,
        "hyde_tokens": set().union(*(tokenize(item) for item in hyde_queries)) if hyde_queries else set(),
        "numbers": set(numbers),
    }


def call_llm_hyde_queries(question: str, language: str = "") -> list[str]:
    api_key = os.environ.get("EASIIO_CHATBOT_LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return []
    base_url = (os.environ.get("EASIIO_CHATBOT_LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("EASIIO_CHATBOT_LLM_MODEL") or os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"
    lang_hint = "Chinese" if str(language).lower().startswith("zh") else "English"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Generate up to 3 short hypothetical answer-style retrieval queries. Do not invent exact numbers, prices, dates, or guarantees. These are retrieval aids only, not evidence."},
            {"role": "user", "content": f"Language: {lang_hint}\nQuestion: {question}"},
        ],
        "temperature": 0.2,
        "max_tokens": 180,
    }
    req = urlrequest.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urlrequest.urlopen(req, timeout=min(LLM_TIMEOUT_SECONDS, 8)) as response:
            body = json.loads(response.read().decode("utf-8"))
        text = normalize_whitespace(body["choices"][0]["message"]["content"])
    except (OSError, urlerror.URLError, urlerror.HTTPError, TimeoutError, json.JSONDecodeError, KeyError, IndexError, TypeError):
        return []
    parts = [re.sub(r"^[-*\d.)\s]+", "", part).strip() for part in re.split(r"\n|;", text) if part.strip()]
    return [part[:240] for part in parts[:3] if part]


def _score_overlap(query_tokens: set[str], target_tokens: set[str]) -> float:
    if not query_tokens or not target_tokens:
        return 0.0
    return len(query_tokens & target_tokens) / max(1, len(query_tokens))


def rag_site_ids(site_id: str) -> list[str]:
    """Return the primary site_id plus safe knowledge aliases in priority order."""
    primary = sanitize_text(site_id or "default", 100)
    ids: list[str] = []
    for candidate in [primary] + list(RAG_SITE_ALIASES.get(primary, [])):
        candidate = sanitize_text(candidate, 100)
        if candidate and candidate not in ids:
            ids.append(candidate)
    return ids or ["default"]


def rag_chunks_for_site(site_id: str) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for candidate in rag_site_ids(site_id):
        for chunk in SITE_RAG_INDEX.get(candidate, []):
            key = str(chunk.get("chunk_id") or "") or f"{candidate}:{len(seen)}"
            if key in seen:
                continue
            seen.add(key)
            chunks.append(chunk)
    return chunks


def retrieve_rag_candidates(site_id: str, query_plan: dict[str, Any], *, limit: int = RAG_MAX_CANDIDATES) -> list[dict[str, Any]]:
    chunks = rag_chunks_for_site(site_id)
    original_tokens = set(query_plan.get("original_tokens") or set())
    expanded_tokens = set(query_plan.get("expanded_tokens") or set())
    hyde_tokens = set(query_plan.get("hyde_tokens") or set())
    numbers = set(query_plan.get("numbers") or set())
    phrase = str(query_plan.get("question") or "").lower()
    results: list[dict[str, Any]] = []
    for chunk in chunks:
        chunk_tokens = set(chunk.get("tokens") or set())
        summary_tokens = set(chunk.get("summary_tokens") or set())
        text = str(chunk.get("text") or "")
        lower = text.lower()
        score = 0.0
        reasons: list[str] = []
        original_score = _score_overlap(original_tokens, chunk_tokens)
        if original_score:
            score += 0.35 * original_score
            reasons.append("original_overlap")
        expanded_score = _score_overlap(expanded_tokens, chunk_tokens)
        if expanded_score:
            score += 0.20 * expanded_score
            reasons.append("expanded_overlap")
        hyde_score = _score_overlap(hyde_tokens, chunk_tokens)
        if hyde_score:
            score += 0.15 * hyde_score
            reasons.append("hyde_overlap")
        summary_score = _score_overlap(original_tokens | expanded_tokens, summary_tokens)
        if summary_score:
            score += 0.15 * summary_score
            reasons.append("summary_overlap")
        exact_score = 0.0
        for number in numbers:
            if re.search(rf"\b{re.escape(number)}\b", lower):
                exact_score += 0.08
        query_lesson = find_lesson_number(phrase)
        if query_lesson:
            chunk_lesson = find_lesson_number(lower)
            if chunk_lesson == query_lesson:
                exact_score += 0.35
                reasons.append("exact_lesson")
            elif chunk_lesson:
                exact_score -= 0.18
        for token in original_tokens:
            if len(token) >= 4 and token in lower:
                exact_score += 0.015
        if exact_score:
            score += min(0.45, exact_score)
            if "exact_lesson" not in reasons:
                reasons.append("exact_match")
        if chunk.get("source") == "manual":
            score += 0.03
            reasons.append("manual_source")
        if score > 0:
            results.append({"chunk": chunk, "score": score, "reasons": reasons})
    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:limit]


def rerank_rag_candidates(question: str, candidates: list[dict[str, Any]], *, keep: int = RAG_MAX_SELECTED) -> list[dict[str, Any]]:
    query_tokens = tokenize(question)
    query_lesson = find_lesson_number(question)
    reranked: list[dict[str, Any]] = []
    for item in candidates:
        chunk = item["chunk"]
        text = str(chunk.get("text") or "")
        score = float(item.get("score") or 0)
        if query_lesson and find_lesson_number(text) == query_lesson:
            score += 0.8
        if re.search(r"\b(how to|steps|setup|configure)\b", question, re.I) and re.search(r"\b(step|configure|setup|install|use)\b", text, re.I):
            score += 0.15
        if query_tokens & tokenize(str(chunk.get("title") or "") + " " + str(chunk.get("section") or "")):
            score += 0.1
        lower_question = str(question or "").lower()
        lower_text = text.lower()
        if "chatbot" in lower_question and re.search(r"\b(assistant|knowledge base|rag|crm|lead capture|lead form)\b", lower_text):
            score += 0.45
        if "knowledge" in lower_question and re.search(r"\b(knowledge base|rag|docs|wiki)\b", lower_text):
            score += 0.25
        asks_for_course_location = bool(re.search(r"\b(which|what)\s+(class|lesson|module)\b|\bin\s+which\s+(class|lesson|module)\b|哪.*(课|节)", lower_question))
        if asks_for_course_location and find_lesson_number(lower_text):
            core_tokens = {token for token in query_tokens if len(token) >= 3 and token not in {"which", "what", "class", "classes", "lesson", "lessons", "module", "modules", "teach", "course"}}
            if any(token in lower_text for token in core_tokens):
                score += 0.65
        updated = dict(item)
        updated["score"] = score
        reranked.append(updated)
    reranked.sort(key=lambda item: item["score"], reverse=True)
    return reranked[:keep]


def expand_rag_context(site_id: str, ranked: list[dict[str, Any]], *, max_chars: int = MAX_RAG_LLM_CONTEXT_CHARS) -> list[dict[str, Any]]:
    chunks = rag_chunks_for_site(site_id)
    by_id = {chunk.get("chunk_id"): chunk for chunk in chunks}
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    total = 0

    def add(chunk: dict[str, Any]) -> None:
        nonlocal total
        cid = str(chunk.get("chunk_id") or "")
        text = normalize_whitespace(chunk.get("text") or "")
        if not cid or cid in seen or not text:
            return
        if total + len(text) > max_chars and selected:
            return
        selected.append(chunk)
        seen.add(cid)
        total += len(text)

    for item in ranked:
        chunk = item["chunk"]
        add(chunk)
        for neighbor_key in ("prev_id", "next_id"):
            neighbor = by_id.get(chunk.get(neighbor_key))
            if not neighbor:
                continue
            same_source = neighbor.get("url") == chunk.get("url") and neighbor.get("source") == chunk.get("source")
            compatible_section = not neighbor.get("section") or not chunk.get("section") or neighbor.get("section") == chunk.get("section")
            chunk_lesson = find_lesson_number(str(chunk.get("text") or ""))
            neighbor_lesson = find_lesson_number(str(neighbor.get("text") or ""))
            different_lesson = bool(chunk_lesson and neighbor_lesson and chunk_lesson != neighbor_lesson)
            if same_source and compatible_section and not different_lesson:
                add(neighbor)
    return selected


def format_rag_context(chunks: list[dict[str, Any]], *, max_chars: int = MAX_RAG_LLM_CONTEXT_CHARS) -> str:
    parts: list[str] = []
    total = 0
    for index, chunk in enumerate(chunks, start=1):
        text = normalize_whitespace(chunk.get("text") or "")
        block = "\n".join([
            f"[Source {index}]",
            f"Title: {chunk.get('title', '')}",
            f"Section: {chunk.get('section', '')}",
            f"URL: {chunk.get('url', '')}",
            f"Text: {text}",
        ])
        if total + len(block) > max_chars and parts:
            break
        parts.append(block)
        total += len(block)
    return "\n\n".join(parts)[:max_chars]


def source_list(chunks: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    sources = []
    seen: set[tuple[str, str, str]] = set()
    for index, chunk in enumerate(chunks, start=1):
        key = (str(chunk.get("title", "")), str(chunk.get("url", "")), str(chunk.get("section", "")))
        if key in seen:
            continue
        seen.add(key)
        sources.append({"source_id": f"Source {index}", "title": chunk.get("title", ""), "url": chunk.get("url", ""), "section": chunk.get("section", "")})
        if len(sources) >= limit:
            break
    return sources


def verify_grounded_answer(answer: str, selected_chunks: list[dict[str, Any]], question: str) -> dict[str, Any]:
    evidence = "\n".join(str(chunk.get("text") or "") for chunk in selected_chunks)
    evidence_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", evidence))
    answer_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", answer))
    unsupported_numbers = answer_numbers - evidence_numbers
    answer_tokens = tokenize(answer)
    evidence_tokens = tokenize(evidence)
    overlap = len(answer_tokens & evidence_tokens) / max(1, len(answer_tokens)) if answer_tokens else 0.0
    supported = not unsupported_numbers and (overlap >= 0.18 or not answer_tokens)
    confidence = "high" if supported and overlap >= 0.45 else "medium" if supported else "low"
    return {"supported": supported, "confidence": confidence, "unsupported_numbers": sorted(unsupported_numbers), "overlap": overlap}

def llm_runtime_status() -> dict[str, Any]:
    api_key = os.environ.get("EASIIO_CHATBOT_LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base_url = (os.environ.get("EASIIO_CHATBOT_LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("EASIIO_CHATBOT_LLM_MODEL") or os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"
    if not api_key:
        return {"configured": False, "reason": "missing_api_key", "model": model, "base_url_configured": bool(base_url)}
    return {"configured": True, "reason": "configured", "model": model, "base_url_configured": bool(base_url)}


def call_llm_answer_formatter(question: str, context: str, language: str = "") -> str:
    """Use an OpenAI-compatible chat API to turn retrieved context into a concise answer.

    This is intentionally optional: if no API key/config is present, or the call
    fails, the backend falls back to a deterministic extractive answer rather
    than dumping the whole RAG chunk or blocking lead capture.
    """
    api_key = os.environ.get("EASIIO_CHATBOT_LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return ""
    base_url = (os.environ.get("EASIIO_CHATBOT_LLM_BASE_URL") or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("EASIIO_CHATBOT_LLM_MODEL") or os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"
    lang_hint = "Chinese" if str(language).lower().startswith("zh") else "English"
    system_prompt = (
        "You are a concise website assistant. Answer the user's question using only the provided website sources. "
        "Do not paste the full context. If the sources do not contain the answer, say you do not see it in the current website knowledge. "
        "Cite sources inline like [Source 1] when a source label is provided. Keep the answer under 120 words, use bullets only when helpful, and match the user's language."
    )
    user_prompt = (
        f"Preferred language: {lang_hint}\n"
        f"Question: {question}\n\n"
        f"Website sources:\n{context[:MAX_RAG_LLM_CONTEXT_CHARS]}"
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 220,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(
        f"{base_url}/chat/completions",
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlrequest.urlopen(req, timeout=LLM_TIMEOUT_SECONDS) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (OSError, urlerror.URLError, urlerror.HTTPError, TimeoutError, json.JSONDecodeError):
        return ""
    try:
        answer = normalize_whitespace(body["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError):
        return ""
    return answer[:MAX_RAG_REPLY_CHARS].rstrip()


def is_marketing_capability_question(question: str) -> bool:
    text = normalize_whitespace(question).lower()
    asks_marketing = bool(re.search(r"\bmarketing\b|市场|营销", text))
    asks_capability = bool(re.search(r"功能|能力|可以做|能做|包括|有哪些|哪一些|what.*capabil|what.*function|can.*do|include", text, re.I))
    return asks_marketing and asks_capability


def marketing_capabilities_fallback_answer(question: str, context: str, language: str = "") -> str:
    """Answer marketing-capability questions concisely when LLM formatting is unavailable.

    The generic extractive fallback can otherwise select a broad hero/course
    chunk and sound like a raw page dump. For marketing questions, synthesize a
    short capability list from grounded keywords in the retrieved context.
    """
    question_clean = normalize_whitespace(question)
    context_clean = normalize_whitespace(context)
    if not question_clean or not context_clean:
        return ""
    lower_q = question_clean.lower()
    lower_context = context_clean.lower()
    if not is_marketing_capability_question(question_clean):
        return ""
    is_chinese = str(language).lower().startswith("zh") or bool(re.search(r"[\u4e00-\u9fff]", question_clean))
    capability_patterns = [
        ("市场研究 / 竞争情报", "market research / competitor intelligence", r"市场研究|竞争情报|market research|competitor"),
        ("SEO / GEO 内容优化", "SEO / GEO content optimization", r"\bseo\b|\bgeo\b|搜索|answer[- ]?engine|优化"),
        ("短视频和内容生产线", "short-video and content production", r"短视频|视频内容|内容生产|content production|short[- ]?video"),
        ("线索收集与 CRM 跟进", "lead capture and CRM follow-up", r"线索|潜在客户|lead|crm"),
        ("邮件跟进和营销自动化", "email follow-up and marketing automation", r"邮件|跟进|email|follow[- ]?up|marketing automation|营销自动化"),
        ("销售客服流程支持", "sales and customer-service workflow support", r"销售客服|销售|客服|sales|customer service"),
        ("预算、实验和 ROI 分析", "budget, experiment, and ROI analysis", r"预算|实验|roi|投放|budget|experiment"),
    ]
    capabilities: list[tuple[str, str]] = []
    seen: set[str] = set()
    for zh_label, en_label, pattern in capability_patterns:
        if re.search(pattern, lower_context, re.I):
            key = zh_label.lower()
            if key not in seen:
                seen.add(key)
                capabilities.append((zh_label, en_label))
    if not capabilities:
        return ""
    if is_chinese:
        items = "；".join(zh for zh, _ in capabilities[:6])
        return f"我在市场/Marketing 方面可以帮你做：{items}。这些能力可以组合成从获客、内容、跟进到分析优化的营销工作流。"
    items = "; ".join(en for _, en in capabilities[:6])
    return f"For marketing, I can help with: {items}. These can be combined into an acquisition, content, follow-up, and optimization workflow."


def question_specific_fallback_answer(question: str, context: str, language: str = "") -> str:
    question_clean = normalize_whitespace(question)
    context_clean = normalize_whitespace(context)
    if not question_clean or not context_clean:
        return ""
    marketing_answer = marketing_capabilities_fallback_answer(question_clean, context_clean, language)
    if marketing_answer:
        return marketing_answer
    is_chinese = str(language).lower().startswith("zh") or bool(re.search(r"[\u4e00-\u9fff]", question_clean))
    lower_q = question_clean.lower()
    lower_context = context_clean.lower()
    yes_no = bool(re.match(r"^(do|does|did|is|are|can|could|will|would|have|has|am)\b", lower_q))
    if yes_no:
        topic_text = re.sub(r"^(do|does|did|is|are|can|could|will|would|have|has|am)\s+(you|we|this|the|your|our|it|they)?\s*", "", question_clean, flags=re.I)
        topic_text = re.sub(r"\?+$", "", topic_text).strip()
        topic_text = re.sub(r"^(teach|offer|include|cover|provide|support|have|has|build|explain|show)\s+", "", topic_text, flags=re.I).strip()
        separators = r"\s*(?:,|/|\band\b|\bor\b|\+|&|以及|和)\s*"
        raw_topics = [part.strip(" .?!") for part in re.split(separators, topic_text, flags=re.I) if part.strip(" .?!")]
        matched_topics: list[str] = []
        for topic in raw_topics:
            if len(topic) < 2:
                continue
            pattern = re.compile(re.escape(topic), re.I)
            match = pattern.search(context_clean)
            if match:
                matched_topics.append(context_clean[match.start():match.end()])
        if matched_topics:
            unique_topics = []
            seen = set()
            for topic in matched_topics:
                key = topic.lower()
                if key not in seen:
                    seen.add(key)
                    unique_topics.append(topic)
            if is_chinese:
                return f"是的。根据当前知识库，网站内容提到：{'、'.join(unique_topics)}。"
            if len(unique_topics) == 1:
                topic_phrase = unique_topics[0]
            else:
                topic_phrase = ", ".join(unique_topics[:-1]) + f" and {unique_topics[-1]}"
            return f"Yes. Based on the current website knowledge, it covers {topic_phrase}."
    return ""


def concise_extractive_answer(question: str, context: str, language: str = "") -> str:
    question_specific = question_specific_fallback_answer(question, context, language)
    if question_specific:
        return question_specific
    query_tokens = tokenize(question)
    query_lesson = find_lesson_number(question)
    if query_lesson:
        lesson_matches = list(re.finditer(r"(?:Lesson\s*|第\s*)(\d+)(?:\s*课)?", context, re.I))
        for idx, match in enumerate(lesson_matches):
            if match.group(1) == query_lesson:
                next_start = lesson_matches[idx + 1].start() if idx + 1 < len(lesson_matches) else len(context)
                context = context[match.start():next_start]
                break
    sentences = split_rag_units(context)
    if not sentences:
        sentences = [normalize_whitespace(context)] if context else []
    scored: list[tuple[float, int, str]] = []
    for index, sentence in enumerate(sentences):
        tokens = tokenize(sentence)
        overlap = query_tokens & tokens
        if not overlap:
            continue
        score = len(overlap) / max(1, len(query_tokens))
        for token in overlap:
            if token in sentence.lower():
                score += 0.05
        scored.append((score, index, sentence))
    if scored:
        scored.sort(key=lambda item: (-item[0], item[1]))
        best_index = scored[0][1]
        chosen = [sentences[best_index]]
        # Include following sentences until the answer is still compact because
        # website copy often has a heading followed by details and output.
        neighbor = best_index + 1
        while neighbor < len(sentences):
            next_sentence = sentences[neighbor]
            lesson_match = re.match(r"(?:Lesson|第)\s*(\d+)", next_sentence, re.I)
            if lesson_match and lesson_match.group(1) not in query_tokens:
                break
            if len(" ".join(chosen + [next_sentence])) > 340:
                break
            chosen.append(next_sentence)
            neighbor += 1
    else:
        chosen = sentences[:1]
    answer = " ".join(chosen)
    if len(answer) > 360:
        answer = answer[:357].rstrip() + "..."
    prefix = "根据当前网站内容：" if str(language).lower().startswith("zh") else "Based on this website:"
    return f"{prefix} {answer}" if answer else ""


def answer_from_site_rag(site_id: str, message: str, language: str = "") -> dict[str, Any] | None:
    for candidate_site_id in rag_site_ids(site_id):
        refresh_manual_rag_index(candidate_site_id)
    query_tokens = tokenize(message)
    if not query_tokens:
        return None
    all_chunks = rag_chunks_for_site(site_id)
    all_context = "\n".join(normalize_whitespace(" ".join(str(chunk.get(key, "")) for key in ("title", "section", "text"))) for chunk in all_chunks)
    direct_answer = direct_count_answer(message, all_context[:MAX_RAG_LLM_CONTEXT_CHARS], language)
    if direct_answer:
        return {
            "reply": direct_answer,
            "answer_source": "website_rag",
            "sources": source_list(all_chunks[:2]),
            "confidence": "high",
        }

    query_plan = build_rag_query_plan(message, language)
    candidates = retrieve_rag_candidates(site_id, query_plan, limit=RAG_MAX_CANDIDATES)
    if not candidates:
        return None
    ranked = rerank_rag_candidates(message, candidates, keep=RAG_MAX_SELECTED)
    if not ranked:
        return None
    min_score = 0.05 if is_marketing_capability_question(message) else 0.12
    if ranked[0]["score"] < min_score:
        return None
    selected = expand_rag_context(site_id, ranked, max_chars=MAX_RAG_LLM_CONTEXT_CHARS)
    if not selected:
        selected = [item["chunk"] for item in ranked[:3]]
    plain_context = "\n".join(normalize_whitespace(chunk.get("text", "")) for chunk in selected)[:MAX_RAG_LLM_CONTEXT_CHARS].rstrip()
    top_context = normalize_whitespace(selected[0].get("text", "")) if selected else plain_context
    direct_answer = direct_count_answer(message, plain_context, language)
    if direct_answer:
        return {
            "reply": direct_answer,
            "answer_source": "website_rag",
            "sources": source_list(selected),
            "confidence": "high",
        }

    formatted_context = format_rag_context(selected, max_chars=MAX_RAG_LLM_CONTEXT_CHARS)
    llm_answer = call_llm_answer_formatter(message, formatted_context or plain_context, language)
    answer_source = "website_rag_llm" if llm_answer else "website_rag"
    fallback_context = plain_context if is_marketing_capability_question(message) else (top_context or plain_context)
    answer = llm_answer or concise_extractive_answer(message, fallback_context, language)
    if not answer:
        return None
    verification = verify_grounded_answer(answer, selected, message) if RAG_VERIFY_ENABLED else {"supported": True, "confidence": "medium"}
    if llm_answer and not verification.get("supported"):
        fallback = concise_extractive_answer(message, top_context or plain_context, language)
        if fallback:
            answer = fallback
            answer_source = "website_rag"
            verification = verify_grounded_answer(answer, selected, message) if RAG_VERIFY_ENABLED else {"supported": True, "confidence": "medium"}
    result = {
        "reply": answer,
        "answer_source": answer_source,
        "sources": source_list(selected),
        "confidence": verification.get("confidence", "medium"),
    }
    if RAG_DEBUG:
        result["retrieval_debug"] = [{"score": round(float(item.get("score", 0)), 4), "reasons": item.get("reasons", []), "title": item["chunk"].get("title", ""), "section": item["chunk"].get("section", "")} for item in ranked[:5]]
    return result


def run_rag_debug(site_id: str, question: str, page_context: dict[str, Any] | None = None, language: str = "") -> dict[str, Any]:
    page_context = page_context or {}
    if page_context:
        update_site_rag_index(site_id, page_context)
    refresh_manual_rag_index(site_id)
    language = language or sanitize_text(page_context.get("language") if isinstance(page_context, dict) else "", 20)
    query_plan = build_rag_query_plan(question, language)
    candidates = retrieve_rag_candidates(site_id, query_plan, limit=RAG_MAX_CANDIDATES)
    ranked = rerank_rag_candidates(question, candidates, keep=RAG_MAX_SELECTED) if candidates else []
    selected = expand_rag_context(site_id, ranked, max_chars=MAX_RAG_LLM_CONTEXT_CHARS) if ranked else []
    if not selected and ranked:
        selected = [item["chunk"] for item in ranked[:3]]
    answer = answer_from_site_rag(site_id, question, language) or {
        "reply": "",
        "answer_source": "none",
        "sources": [],
        "confidence": "low",
    }
    return {
        "ok": True,
        "site_id": site_id,
        "query_plan": json_safe(query_plan),
        "candidates": [
            {
                "score": round(float(item.get("score", 0)), 4),
                "reasons": item.get("reasons", []),
                "chunk": chunk_debug_summary(item.get("chunk", {})),
            }
            for item in candidates[:10]
        ],
        "ranked": [
            {
                "score": round(float(item.get("score", 0)), 4),
                "reasons": item.get("reasons", []),
                "chunk": chunk_debug_summary(item.get("chunk", {})),
            }
            for item in ranked[:10]
        ],
        "selected_sources": source_list(selected, limit=8),
        "selected_chunks": [chunk_debug_summary(chunk) for chunk in selected[:8]],
        "llm_status": llm_runtime_status(),
        "answer": answer,
    }


def rag_debug_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    question = sanitize_text(payload.get("question") or payload.get("message") or "", MAX_MESSAGE_CHARS)
    if not question:
        return json_response(400, {"ok": False, "error": "question is required"})
    page_context = payload.get("page_context") if isinstance(payload.get("page_context"), dict) else {}
    return json_response(200, run_rag_debug(site_id, question, page_context, sanitize_text(payload.get("language") or "", 20)))


def record_rag_answer_log(site_id: str, session_id: str, question: str, response_body: dict[str, Any]) -> str:
    if not str(response_body.get("answer_source", "")).startswith("website_rag"):
        return ""
    now = int(time.time())
    item = {
        "log_id": "raglog_" + uuid.uuid4().hex[:16],
        "site_id": sanitize_text(site_id, 100),
        "session_id": mask_pii(session_id, 120),
        "question": mask_pii(question, MAX_MESSAGE_CHARS),
        "answer": mask_pii(response_body.get("reply", ""), MAX_RAG_REPLY_CHARS),
        "answer_source": sanitize_text(response_body.get("answer_source", ""), 80),
        "confidence": sanitize_text(response_body.get("confidence", ""), 40),
        "sources": response_body.get("sources", [])[:5] if isinstance(response_body.get("sources"), list) else [],
        "lead_captured": bool(response_body.get("lead_captured")),
        "fallback_used": response_body.get("answer_source") == "website_rag",
        "created_at": now,
    }
    items = load_json_items(RAG_ANSWER_LOG_PATH)
    items.append(item)
    save_json_items(RAG_ANSWER_LOG_PATH, items[-MAX_RAG_ANSWER_LOG_ITEMS:])
    return item["log_id"]


def rag_answer_log_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    limit = min(200, max(1, int(str(payload.get("limit") or "50") if str(payload.get("limit") or "50").isdigit() else "50")))
    items = [item for item in load_json_items(RAG_ANSWER_LOG_PATH) if item.get("site_id") == site_id]
    return json_response(200, {"ok": True, "site_id": site_id, "items": list(reversed(items[-limit:]))})


def normalize_feedback_rating(value: Any) -> str:
    rating = sanitize_text(value, 40).lower().replace("-", "_")
    if rating in {"helpful", "up", "yes", "thumbs_up", "positive"}:
        return "helpful"
    if rating in {"not_helpful", "down", "no", "thumbs_down", "negative"}:
        return "not_helpful"
    return "neutral"


def rag_feedback_upsert_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    item = {
        "feedback_id": "ragfb_" + uuid.uuid4().hex[:16],
        "site_id": site_id,
        "answer_log_id": sanitize_text(payload.get("answer_log_id") or payload.get("log_id") or "", 120),
        "rating": normalize_feedback_rating(payload.get("rating")),
        "reason": sanitize_text(payload.get("reason") or "", 160),
        "question": mask_pii(payload.get("question") or "", MAX_MESSAGE_CHARS),
        "answer": mask_pii(payload.get("answer") or "", MAX_RAG_REPLY_CHARS),
        "comment": mask_pii(payload.get("comment") or "", 1000),
        "created_at": int(time.time()),
    }
    items = load_json_items(RAG_FEEDBACK_STORE_PATH)
    items.append(item)
    save_json_items(RAG_FEEDBACK_STORE_PATH, items[-MAX_RAG_FEEDBACK_ITEMS:])
    return json_response(200, {"ok": True, "site_id": site_id, "item": item})


def rag_feedback_list_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    limit = min(200, max(1, int(str(payload.get("limit") or "50") if str(payload.get("limit") or "50").isdigit() else "50")))
    items = [item for item in load_json_items(RAG_FEEDBACK_STORE_PATH) if item.get("site_id") == site_id]
    return json_response(200, {"ok": True, "site_id": site_id, "items": list(reversed(items[-limit:]))})


def rag_eval_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    page_context = payload.get("page_context") if isinstance(payload.get("page_context"), dict) else {}
    if page_context:
        update_site_rag_index(site_id, page_context)
    raw_cases = payload.get("cases") if isinstance(payload.get("cases"), list) else []
    results: list[dict[str, Any]] = []
    for index, raw_case in enumerate(raw_cases[:50], start=1):
        if not isinstance(raw_case, dict):
            continue
        question = sanitize_text(raw_case.get("question") or "", MAX_MESSAGE_CHARS)
        if not question:
            continue
        answer = answer_from_site_rag(site_id, question, sanitize_text(page_context.get("language") or payload.get("language") or "", 20)) or {}
        reply = str(answer.get("reply") or "")
        sources_text = " ".join(str(value) for source in answer.get("sources", []) if isinstance(source, dict) for value in source.values())
        evidence_text = " ".join(normalize_whitespace(chunk.get("text", "")) for chunk in SITE_RAG_INDEX.get(site_id, []))
        expected_answer = [str(item) for item in raw_case.get("expected_answer_contains", []) if str(item)]
        expected_source = [str(item) for item in raw_case.get("expected_source_contains", []) if str(item)]
        answer_ok = all(item.lower() in reply.lower() for item in expected_answer)
        source_ok = all(item.lower() in (sources_text + " " + reply + " " + evidence_text).lower() for item in expected_source)
        confidence_ok = answer.get("confidence", "low") in {"high", "medium"}
        results.append({
            "case_index": index,
            "question": mask_pii(question, MAX_MESSAGE_CHARS),
            "passed": bool(answer_ok and source_ok and confidence_ok),
            "answer_ok": answer_ok,
            "source_ok": source_ok,
            "confidence_ok": confidence_ok,
            "reply": mask_pii(reply, MAX_RAG_REPLY_CHARS),
            "confidence": answer.get("confidence", "low"),
            "sources": answer.get("sources", []),
        })
    passed = sum(1 for item in results if item["passed"])
    return json_response(200, {"ok": True, "site_id": site_id, "summary": {"total": len(results), "passed": passed, "failed": len(results) - passed}, "results": results})


def detect_intent(message: str, page_context: dict[str, Any] | None = None) -> dict[str, Any]:
    page_context = page_context or {}
    combined = f"{message} {page_text(page_context)}"
    sales = bool(SALES_INTENT_RE.search(combined))
    demo = bool(DEMO_RE.search(combined))
    pricing = bool(PRICING_RE.search(combined))
    actions: list[str] = []
    if demo:
        actions.append("book_demo")
    if pricing:
        actions.append("send_pricing_followup")
    if sales and "contact_sales" not in actions:
        actions.append("contact_sales")
    return {"sales": sales, "demo": demo, "pricing": pricing, "suggested_actions": actions}


def lead_score(email: str, company: str, intent: dict[str, Any], page_context: dict[str, Any] | None = None) -> int:
    score = 0
    if email:
        score += 20
    if company:
        score += 10
    if intent.get("demo"):
        score += 30
    if intent.get("pricing"):
        score += 20
    if page_context and re.search(r"pricing|demo|contact", page_text(page_context), re.I):
        score += 10
    return score


def website_metadata(payload: dict[str, Any], page_context: dict[str, Any] | None = None) -> dict[str, Any]:
    page_context = page_context or {}
    site_id = sanitize_text(payload.get("site_id") or page_context.get("site_id") or "default", 100)
    url = sanitize_text(payload.get("page_url") or page_context.get("url") or "", 500)
    title = sanitize_text(payload.get("page_title") or page_context.get("title") or "", 300)
    domain = ""
    if url:
        try:
            domain = urlparse(url).netloc
        except Exception:
            domain = ""
    return {
        "site_id": site_id,
        "organization_name": sanitize_text(payload.get("organization_name") or "AI Solo Company", 160),
        "website_name": sanitize_text(payload.get("website_name") or title or site_id, 160),
        "domain": sanitize_text(payload.get("domain") or domain, 160),
        "url": url,
        "title": title,
    }


def get_or_create_website(crm: SoloCRM, payload: dict[str, Any], page_context: dict[str, Any] | None = None) -> dict[str, Any]:
    meta = website_metadata(payload, page_context)
    return crm.ensure_website(
        site_id=meta["site_id"],
        organization_name=meta["organization_name"],
        website_name=meta["website_name"],
        domain=meta["domain"],
        url=meta["url"],
    )


def record_visit_from_payload(crm: SoloCRM, payload: dict[str, Any], headers: dict[str, str] | None = None) -> dict[str, Any] | None:
    headers = headers or {}
    page_context = payload.get("page_context") if isinstance(payload.get("page_context"), dict) else {}
    meta = website_metadata(payload, page_context)
    visitor = payload.get("visitor") if isinstance(payload.get("visitor"), dict) else {}
    visitor_key = sanitize_text(payload.get("visitor_key") or visitor.get("visitor_key") or payload.get("session_id") or "", 160)
    if not visitor_key and not payload.get("session_id"):
        return None
    return crm.record_website_visit(
        site_id=meta["site_id"],
        visitor_key=visitor_key,
        session_id=sanitize_text(payload.get("session_id") or "", 160),
        page_url=meta["url"],
        page_title=meta["title"],
        referrer=sanitize_text(payload.get("referrer") or page_context.get("referrer") or "", 500),
        user_agent=sanitize_text(headers.get("User-Agent") or payload.get("user_agent") or "", 500),
        ip_address=sanitize_text(headers.get("X-Forwarded-For") or "", 160),
        utm=page_context.get("utm") if isinstance(page_context.get("utm"), dict) else {},
        organization_name=meta["organization_name"],
        website_name=meta["website_name"],
        domain=meta["domain"],
    )


def find_existing_contact(crm: SoloCRM, email: str) -> dict[str, Any] | None:
    if not email:
        return None
    matches = crm.search_contacts(email, limit=5)
    for contact in matches:
        if str(contact.get("email", "")).lower() == email.lower():
            return contact
    return None


def upsert_contact(crm: SoloCRM, *, name: str, email: str, phone: str, company: str, source: str, notes: str,
                   organization_id: int | None = None, website_id: int | None = None, visitor_id: int | None = None) -> dict[str, Any] | None:
    if not email and not phone:
        return None
    company_id = None
    if company:
        company_row = crm.create_company(name=company, notes=f"Created/updated from {source}", organization_id=organization_id, website_id=website_id)
        company_id = int(company_row["id"])
    existing = find_existing_contact(crm, email)
    if existing:
        fields: dict[str, Any] = {
            "name": name or existing.get("name") or email or phone,
            "phone": phone or existing.get("phone") or "",
            "company_id": company_id if company_id is not None else existing.get("company_id"),
            "organization_id": organization_id if organization_id is not None else existing.get("organization_id"),
            "website_id": website_id if website_id is not None else existing.get("website_id"),
            "visitor_id": visitor_id if visitor_id is not None else existing.get("visitor_id"),
            "status": "lead",
            "source": source,
            "tags": ["website-chatbot", "lead"],
            "notes": notes or existing.get("notes") or "",
        }
        if email:
            fields["email"] = email
        return crm.update_contact(int(existing["id"]), **fields)
    return crm.create_contact(
        name=name or email or phone or "Website visitor",
        email=email,
        phone=phone,
        company_id=company_id,
        organization_id=organization_id,
        website_id=website_id,
        visitor_id=visitor_id,
        status="lead",
        source=source,
        tags=["website-chatbot", "lead"],
        notes=notes,
    )


def create_deal_if_needed(crm: SoloCRM, contact: dict[str, Any] | None, company_id: int | None, intent: dict[str, Any], message: str, score: int,
                          organization_id: int | None = None, website_id: int | None = None) -> dict[str, Any] | None:
    if not contact or not intent.get("sales"):
        return None
    title_suffix = "Demo request" if intent.get("demo") else "Pricing inquiry" if intent.get("pricing") else "Sales inquiry"
    return crm.create_deal(
        title=f"Website chatbot - {title_suffix}",
        contact_id=int(contact["id"]),
        company_id=company_id,
        stage="new",
        probability=min(80, max(20, score)),
        notes=f"Lead score: {score}\nInitial message: {message}",
        organization_id=organization_id,
        website_id=website_id,
    )


def write_activity(crm: SoloCRM, contact: dict[str, Any] | None, deal: dict[str, Any] | None, *, kind: str, body: str,
                   organization_id: int | None = None, website_id: int | None = None, visitor_id: int | None = None) -> dict[str, Any] | None:
    if not contact and not deal:
        return None
    return crm.add_activity(
        contact_id=int(contact["id"]) if contact else None,
        deal_id=int(deal["id"]) if deal else None,
        kind=kind,
        body=body,
        organization_id=organization_id,
        website_id=website_id,
        visitor_id=visitor_id,
    )


def session_handler(payload: dict[str, Any], crm: SoloCRM, headers: dict[str, str] | None = None) -> Response:
    session_id = sanitize_text(payload.get("session_id") or "", 100) or "chat_" + uuid.uuid4().hex[:16]
    payload = dict(payload, session_id=session_id)
    visitor = record_visit_from_payload(crm, payload, headers)
    page_context = payload.get("page_context") if isinstance(payload.get("page_context"), dict) else {}
    update_site_rag_index(website_metadata(payload, page_context)["site_id"], page_context)
    website = get_or_create_website(crm, payload, page_context)
    return json_response(200, {
        "session_id": session_id,
        "visitor_id": visitor.get("id") if visitor else None,
        "website_id": website.get("id") if website else None,
        "organization_id": website.get("organization_id") if website else None,
        "welcome_message": "Hi, I can help with AI automation, pricing, or booking a demo.",
    })


def message_handler(payload: dict[str, Any], crm: SoloCRM) -> Response:
    message = sanitize_text(payload.get("message"))
    if not message:
        return json_response(400, {"ok": False, "error": "message is required"})
    visitor = payload.get("visitor") if isinstance(payload.get("visitor"), dict) else {}
    page_context = payload.get("page_context") if isinstance(payload.get("page_context"), dict) else {}
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    update_site_rag_index(site_id, page_context)
    session_id = sanitize_text(payload.get("session_id") or "", 100)
    visit = record_visit_from_payload(crm, payload, {})
    website = get_or_create_website(crm, payload, page_context)
    organization_id = int(website["organization_id"]) if website and website.get("organization_id") is not None else None
    website_id = int(website["id"]) if website and website.get("id") is not None else None
    visitor_id = int(visit["id"]) if visit and visit.get("id") is not None else None

    # Only a contact method typed in the current message should turn a normal
    # chat message into a CRM lead. The widget sends cached visitor contact data
    # after a lead-form submission so the assistant can remember the visitor,
    # but factual follow-up questions must still route through RAG/LLM instead
    # of repeatedly writing CRM activities and returning a lead-capture reply.
    email = extract_email(message)
    phone = sanitize_text(extract_phone(message), 80)
    company = sanitize_text(visitor.get("company"), 160)
    name = sanitize_text(visitor.get("name"), 160)
    intent = detect_intent(message, page_context)
    score = lead_score(email, company, intent, page_context)
    contact = None
    deal = None
    activity = None
    email_agent_result: dict[str, Any] | None = None

    if email or phone:
        notes = f"Website chatbot lead\nSite: {site_id}\nSession: {session_id}\nPage: {page_context.get('url', '')}\nLead score: {score}"
        existing_contact = find_existing_contact(crm, email) if email else None
        contact = upsert_contact(crm, name=name, email=email, phone=phone, company=company, source="website_chatbot", notes=notes, organization_id=organization_id, website_id=website_id, visitor_id=visitor_id)
        company_id = int(contact["company_id"]) if contact and contact.get("company_id") is not None else None
        deal = create_deal_if_needed(crm, contact, company_id, intent, message, score, organization_id=organization_id, website_id=website_id)
        activity_body = f"Website chatbot message\nSite: {site_id}\nSession: {session_id}\nMessage: {message}\nPage: {page_context.get('url', '')}"
        activity = write_activity(crm, contact, deal, kind="chat", body=activity_body, organization_id=organization_id, website_id=website_id, visitor_id=visitor_id)
        email_agent_result = run_email_agent_for_lead(
            site_id=site_id,
            contact=contact,
            is_new_contact=existing_contact is None,
            lead={
                "name": name,
                "email": email,
                "phone": phone,
                "company": company,
                "message": message,
                "site_id": site_id,
                "session_id": session_id,
                "page_url": page_context.get("url", ""),
                "page_title": page_context.get("title", ""),
                "website_name": payload.get("website_name") or page_context.get("title") or site_id,
                "lead_score": score,
            },
        )

    rag_answer = answer_from_site_rag(site_id, message, sanitize_text(page_context.get("language") or "", 20))
    if contact:
        reply = "Thanks — I saved your request. Easiio can follow up with you soon."
        answer_source = "lead_capture"
    elif rag_answer:
        reply = rag_answer["reply"]
        answer_source = rag_answer["answer_source"]
    elif intent.get("sales"):
        reply = "I do not see a specific answer in the current website knowledge yet. You can ask another question about AI Solo Company, AI agents, automation, pricing, or demos; if you want a human follow-up, share your email or use the form."
        answer_source = "sales_handoff"
    else:
        reply = "Thanks — I can help with AI agents, automation, pricing, or booking a demo."
        answer_source = "fallback"

    body: dict[str, Any] = {
        "reply": reply,
        "answer_source": answer_source,
        "lead_captured": bool(contact),
        "show_lead_form": bool(LEAD_FORMS_ENABLED and intent.get("sales") and not contact and not rag_answer),
        "suggested_actions": intent["suggested_actions"],
        "lead_score": score,
    }
    if rag_answer and rag_answer.get("sources"):
        body["sources"] = rag_answer["sources"]
    if rag_answer and rag_answer.get("confidence"):
        body["confidence"] = rag_answer["confidence"]
    if rag_answer and rag_answer.get("retrieval_debug"):
        body["retrieval_debug"] = rag_answer["retrieval_debug"]
    if contact:
        body["crm_contact_id"] = contact["id"]
    if deal:
        body["crm_deal_id"] = deal["id"]
    if activity:
        body["crm_activity_id"] = activity["id"]
    if email_agent_result:
        body["email_agent"] = email_agent_result
    rag_log_id = record_rag_answer_log(site_id, session_id, message, body)
    if rag_log_id:
        body["answer_log_id"] = rag_log_id
    return json_response(200, body)


def lead_handler(payload: dict[str, Any], crm: SoloCRM) -> Response:
    email = extract_email(payload.get("email"), payload.get("message"))
    phone = sanitize_text(payload.get("phone") or extract_phone(payload.get("message")), 80)
    if not email and not phone:
        return json_response(400, {"ok": False, "error": "email or phone is required"})
    name = sanitize_text(payload.get("name"), 160)
    company = sanitize_text(payload.get("company"), 160)
    message = sanitize_text(payload.get("message") or "Lead form submitted", MAX_MESSAGE_CHARS)
    metadata_keys = {"site_id", "organization_name", "website_name", "visitor_key", "session_id", "page_context", "page_url", "page_title", "referrer", "user_agent", "ip_address", "utm"}
    form_fields = []
    for key, value in payload.items():
        if key in metadata_keys or isinstance(value, (dict, list)):
            continue
        cleaned_value = sanitize_text(value, 500)
        if cleaned_value:
            form_fields.append({"name": key, "value": cleaned_value})
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    session_id = sanitize_text(payload.get("session_id") or "", 100)
    page_context = payload.get("page_context") if isinstance(payload.get("page_context"), dict) else {}
    update_site_rag_index(site_id, page_context)
    visit = record_visit_from_payload(crm, payload, {})
    website = get_or_create_website(crm, payload, page_context)
    organization_id = int(website["organization_id"]) if website and website.get("organization_id") is not None else None
    website_id = int(website["id"]) if website and website.get("id") is not None else None
    visitor_id = int(visit["id"]) if visit and visit.get("id") is not None else None
    intent = detect_intent(message, page_context)
    # A direct lead form submission is a sales handoff even if message is generic.
    if not intent["sales"]:
        intent["sales"] = True
        intent["suggested_actions"].append("contact_sales")
    score = lead_score(email, company, intent, page_context)
    notes = f"Website chatbot lead form\nSite: {site_id}\nSession: {session_id}\nLead score: {score}"
    existing_contact = find_existing_contact(crm, email) if email else None
    contact = upsert_contact(crm, name=name, email=email, phone=phone, company=company, source="website_chatbot", notes=notes, organization_id=organization_id, website_id=website_id, visitor_id=visitor_id)
    company_id = int(contact["company_id"]) if contact and contact.get("company_id") is not None else None
    deal = create_deal_if_needed(crm, contact, company_id, intent, message, score, organization_id=organization_id, website_id=website_id)
    form_field_lines = "\n".join(f"{item['name']}: {item['value']}" for item in form_fields)
    activity_message = f"Website chatbot lead form\nSite: {site_id}\nSession: {session_id}\nMessage: {message}"
    if form_field_lines:
        activity_message += f"\nForm fields:\n{form_field_lines}"
    activity = write_activity(
        crm,
        contact,
        deal,
        kind="lead",
        body=activity_message,
        organization_id=organization_id,
        website_id=website_id,
        visitor_id=visitor_id,
    )
    email_agent_result = run_email_agent_for_lead(
        site_id=site_id,
        contact=contact,
        is_new_contact=existing_contact is None,
        lead={
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "message": message,
            "site_id": site_id,
            "session_id": session_id,
            "page_url": page_context.get("url") or payload.get("page_url") or "",
            "page_title": page_context.get("title") or payload.get("page_title") or "",
            "website_name": payload.get("website_name") or page_context.get("title") or site_id,
            "lead_score": score,
        },
    )
    body: dict[str, Any] = {
        "reply": "Thanks — I saved your contact details. Easiio can follow up soon.",
        "lead_captured": True,
        "crm_contact_id": contact["id"] if contact else None,
        "crm_deal_id": deal["id"] if deal else None,
        "crm_activity_id": activity["id"] if activity else None,
        "suggested_actions": intent["suggested_actions"],
        "lead_score": score,
        "email_agent": email_agent_result,
    }
    return json_response(200, body)


def chat_voice_handler(payload: dict[str, Any]) -> Response:
    text = sanitize_text(payload.get("text") or payload.get("reply") or "", MAX_VOICE_TEXT_CHARS + 1000)
    site_id = sanitize_text(payload.get("site_id") or "default-site", 80) or "default-site"
    voice = sanitize_text(payload.get("voice") or os.environ.get("VOICE_RESPONSE_VOICE") or "", 80)
    audio_format = sanitize_text(payload.get("format") or payload.get("audio_format") or os.environ.get("VOICE_RESPONSE_FORMAT") or "mp3", 16)
    language = sanitize_text(payload.get("language") or os.environ.get("VOICE_RESPONSE_LANGUAGE") or "auto", 32)
    try:
        speed = float(payload.get("speed") or os.environ.get("VOICE_RESPONSE_SPEED") or "1.0")
    except (TypeError, ValueError):
        speed = 1.0
    if not text:
        return json_response(400, {"ok": False, "error_code": "empty_text", "error": "Text is required for voice generation."})
    if len(text) > MAX_VOICE_TEXT_CHARS:
        return json_response(400, {"ok": False, "error_code": "text_too_long", "error": f"Text is too long for voice generation: {len(text)} > {MAX_VOICE_TEXT_CHARS}."})
    try:
        from core import VoiceResponseConfig, synthesize_speech  # type: ignore
        cfg = VoiceResponseConfig.from_env(cache_dir=VOICE_CACHE_DIR, max_chars=MAX_VOICE_TEXT_CHARS)
        result = synthesize_speech(text, cfg=cfg, site_id=site_id, voice=voice or None, audio_format=audio_format or None, language=language, speed=speed)
    except Exception as exc:
        return json_response(500, {"ok": False, "error_code": "voice_generation_failed", "error": mask_pii(f"{type(exc).__name__}: {exc}", 500)})
    if not result.get("ok"):
        status = 400 if result.get("error_code") in {"empty_text", "text_too_long", "unsupported_provider"} else 502
        return json_response(status, {key: value for key, value in result.items() if key not in {"audio_path"}})
    audio_path = Path(str(result.get("audio_path", ""))).expanduser().resolve()
    try:
        cache_root = VOICE_CACHE_DIR.expanduser().resolve()
        audio_path.relative_to(cache_root)
    except Exception:
        return json_response(500, {"ok": False, "error_code": "invalid_audio_path", "error": "Generated audio path is outside the voice cache."})
    audio_id = audio_path.name
    body = {key: value for key, value in result.items() if key != "audio_path"}
    body.update({"ok": True, "audio_id": audio_id, "audio_url": f"api/chat/voice/{audio_id}"})
    return json_response(200, body)


def chat_voice_file_handler(audio_id: str) -> Response:
    audio_id = sanitize_text(audio_id, 200)
    if not re.match(r"^voice_[A-Za-z0-9_-]+_[a-f0-9]{24}\.(mp3|wav|opus|aac|flac|pcm)$", audio_id):
        return json_response(404, {"ok": False, "error": "voice audio not found"})
    root = VOICE_CACHE_DIR.expanduser().resolve()
    path = (root / audio_id).resolve()
    try:
        path.relative_to(root)
    except Exception:
        return json_response(404, {"ok": False, "error": "voice audio not found"})
    if not path.exists() or not path.is_file():
        return json_response(404, {"ok": False, "error": "voice audio not found"})
    mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    return Response(
        status=200,
        body=path.read_bytes(),
        headers={
            "Content-Type": mime,
            "Cache-Control": "public, max-age=604800, immutable",
            "Content-Disposition": f'inline; filename="{audio_id}"',
        },
    )


def route_request(method: str, path: str, headers: dict[str, str], body: bytes, crm: SoloCRM | None = None) -> Response:
    crm = crm or SoloCRM()
    parsed = urlparse(path)
    route = parsed.path
    method = method.upper()
    if method == "OPTIONS":
        return json_response(204, {})
    if method == "GET" and route == "/health":
        return json_response(200, {"ok": True, "service": SERVICE_NAME})
    if method == "GET" and route.startswith("/api/chat/voice/"):
        return chat_voice_file_handler(route.rsplit("/", 1)[-1])
    if method == "GET" and route == "/api/rag/content":
        return rag_content_list_handler({key: values[-1] if values else "" for key, values in parse_qs(parsed.query).items()})
    if method == "GET" and route == "/api/rag/answer-log":
        return rag_answer_log_handler({key: values[-1] if values else "" for key, values in parse_qs(parsed.query).items()})
    if method == "GET" and route == "/api/rag/feedback":
        return rag_feedback_list_handler({key: values[-1] if values else "" for key, values in parse_qs(parsed.query).items()})
    if method == "GET" and route == "/api/rag/sources":
        return rag_sources_status_handler({key: values[-1] if values else "" for key, values in parse_qs(parsed.query).items()})
    if method == "GET" and route == "/api/rag/source-items":
        return rag_source_items_list_handler({key: values[-1] if values else "" for key, values in parse_qs(parsed.query).items()})
    if method == "GET" and route == "/api/rag/review":
        return rag_review_handler({key: values[-1] if values else "" for key, values in parse_qs(parsed.query).items()})
    if method == "GET" and route == "/api/rag/refresh-schedule":
        return rag_refresh_schedule_handler({key: values[-1] if values else "" for key, values in parse_qs(parsed.query).items()})
    if method == "GET" and route == "/api/rag/refresh-due":
        return rag_refresh_due_handler({key: values[-1] if values else "" for key, values in parse_qs(parsed.query).items()})
    if method == "GET" and route == "/api/rag/notifications":
        return rag_notifications_handler({key: values[-1] if values else "" for key, values in parse_qs(parsed.query).items()})
    if method == "GET" and route == "/api/chat/form-config":
        return form_config_handler({key: values[-1] if values else "" for key, values in parse_qs(parsed.query).items()})
    if method == "GET" and route == "/api/email-agent/config":
        return email_agent_config_handler({key: values[-1] if values else "" for key, values in parse_qs(parsed.query).items()})
    if method != "POST":
        return json_response(405, {"ok": False, "error": "method not allowed"})
    try:
        payload = parse_json(body)
    except ValueError as exc:
        return json_response(400, {"ok": False, "error": str(exc)})
    if route == "/api/chat/session":
        return session_handler(payload, crm, headers)
    if route == "/api/chat/message":
        return message_handler(payload, crm)
    if route == "/api/chat/lead":
        return lead_handler(payload, crm)
    if route == "/api/chat/voice":
        return chat_voice_handler(payload)
    if route == "/api/chat/form-config":
        return form_config_upsert_handler(payload)
    if route == "/api/email-agent/config":
        return email_agent_config_upsert_handler(payload)
    if route == "/api/rag/content":
        return rag_content_upsert_handler(payload)
    if route == "/api/rag/content/delete":
        return rag_content_delete_handler(payload)
    if route == "/api/rag/debug":
        return rag_debug_handler(payload)
    if route == "/api/rag/feedback":
        return rag_feedback_upsert_handler(payload)
    if route == "/api/rag/eval":
        return rag_eval_handler(payload)
    if route == "/api/rag/sync-sources":
        return rag_sync_sources_handler(payload)
    if route == "/api/rag/sync-preview":
        return rag_sync_preview_handler(payload)
    if route == "/api/rag/rollback":
        return rag_rollback_handler(payload)
    if route == "/api/rag/refresh-schedule":
        return rag_refresh_schedule_upsert_handler(payload)
    if route == "/api/rag/run-scheduled-refresh":
        return rag_run_scheduled_refresh_handler(payload)
    if route == "/api/rag/notifications/read":
        return rag_notification_read_handler(payload)
    if route == "/api/rag/source-items":
        return rag_source_items_upsert_handler(payload)
    if route == "/api/rag/source-items/delete":
        return rag_source_items_delete_handler(payload)
    if route == "/api/rag/wordpress/pull":
        return rag_wordpress_pull_handler(payload)
    if route == "/api/rag/upload/extract":
        return rag_upload_extract_handler(payload)
    return json_response(404, {"ok": False, "error": "not found"})


class ChatbotHandler(BaseHTTPRequestHandler):
    server_version = "EasiioChatbotHTTP/0.1"

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length") or "0")
        if length > MAX_BODY_BYTES:
            return b""
        return self.rfile.read(length) if length else b""

    def _send(self, response: Response) -> None:
        is_binary = isinstance(response.body, (bytes, bytearray))
        body = b"" if response.status == 204 else (bytes(response.body) if is_binary else json.dumps(response.body).encode("utf-8"))
        self.send_response(response.status)
        self.send_header("Content-Type", (response.headers or {}).get("Content-Type", "application/json; charset=utf-8"))
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        origin = self.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        for key, value in (response.headers or {}).items():
            if key.lower() == "content-type":
                continue
            self.send_header(key, value)
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send(route_request("OPTIONS", self.path, dict(self.headers), b"", self.server.crm))  # type: ignore[attr-defined]

    def do_GET(self) -> None:  # noqa: N802
        self._send(route_request("GET", self.path, dict(self.headers), b"", self.server.crm))  # type: ignore[attr-defined]

    def do_POST(self) -> None:  # noqa: N802
        self._send(route_request("POST", self.path, dict(self.headers), self._read_body(), self.server.crm))  # type: ignore[attr-defined]

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), fmt % args))


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, db_path: str | None = None) -> None:
    crm = SoloCRM(db_path) if db_path else SoloCRM()
    httpd = ThreadingHTTPServer((host, port), ChatbotHandler)
    httpd.crm = crm  # type: ignore[attr-defined]
    print(f"Serving Easiio chatbot backend on {host}:{port}", flush=True)
    httpd.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Easiio website chatbot backend")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--db", default=os.environ.get("SOLO_CRM_DB", ""))
    args = parser.parse_args()
    serve(args.host, args.port, args.db or None)


if __name__ == "__main__":
    main()
