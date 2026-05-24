#!/usr/bin/env python3
"""Dependency-free backend API for the Easiio website chatbot.

The browser widget calls this HTTP API. The API performs deterministic lead
extraction and writes useful contact/deal/activity records into the local Solo
CRM SQLite database. It intentionally does not expose MCP, database paths, or
secrets to browser JavaScript.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import smtplib
import sys
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
SOLO_CRM_ROOT = ROOT.parent / "solo_crm"
if str(SOLO_CRM_ROOT) not in sys.path:
    sys.path.insert(0, str(SOLO_CRM_ROOT))

from crm_core import SoloCRM  # noqa: E402
try:  # noqa: E402
    from connectors.sync import retry_sync_event, sync_contact_to_enabled_crms  # type: ignore
    from connectors.config import load_connectors_config, sanitize_connectors_config, connectors_config_path  # type: ignore
    from connectors.sync_log import list_sync_events  # type: ignore
except Exception:  # pragma: no cover - optional connector package may be absent in older installs
    def sync_contact_to_enabled_crms(crm: SoloCRM, site_id: str, contact_id: int, *, deal_id: int | None = None,
                                     activity_id: int | None = None) -> dict[str, Any]:
        return {"enabled": False, "ok": True, "providers": []}

    def retry_sync_event(crm: SoloCRM, event_id: str) -> dict[str, Any]:
        return {"enabled": False, "ok": False, "providers": [], "error": "sync_log_unavailable"}

    def load_connectors_config(path: str | Path | None = None) -> dict[str, Any]:
        return {"sites": {}}

    def sanitize_connectors_config(config: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"sites": {}}

    def connectors_config_path() -> Path:
        return Path(os.environ.get("SOLO_CRM_CONNECTORS_CONFIG", str(ROOT / "data" / "crm_connectors.json"))).expanduser()

    def list_sync_events(*, site_id: str | None = None, status: str | None = None, provider: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        return []


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
MAX_RAG_CONTENT_CHARS = int(os.environ.get("EASIIO_CHATBOT_MAX_RAG_CONTENT", "50000"))
MAX_RAG_CHUNKS_PER_SITE = int(os.environ.get("EASIIO_CHATBOT_MAX_RAG_CHUNKS", "80"))
MAX_RAG_LLM_CONTEXT_CHARS = int(os.environ.get("EASIIO_CHATBOT_MAX_RAG_LLM_CONTEXT", "2400"))
MAX_RAG_REPLY_CHARS = int(os.environ.get("EASIIO_CHATBOT_MAX_RAG_REPLY", "700"))
LLM_TIMEOUT_SECONDS = float(os.environ.get("EASIIO_CHATBOT_LLM_TIMEOUT", "12"))
LEAD_FORMS_ENABLED = os.environ.get("EASIIO_CHATBOT_LEAD_FORMS_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
RAG_CONTENT_STORE_PATH = Path(os.environ.get("EASIIO_CHATBOT_RAG_STORE", str(ROOT / "data" / "rag_content.json")))
FORM_CONFIG_STORE_PATH = Path(os.environ.get("EASIIO_CHATBOT_FORM_CONFIG_STORE", str(ROOT / "data" / "form_config.json")))
EMAIL_CONFIG_STORE_PATH = Path(os.environ.get("EASIIO_CHATBOT_EMAIL_CONFIG_STORE", str(ROOT / "data" / "email_agent_config.json")))
EMAIL_OUTBOX_DIR = Path(os.environ.get("EASIIO_CHATBOT_EMAIL_OUTBOX_DIR", str(ROOT / "data" / "email_outbox")))
SMTP_TIMEOUT_SECONDS = float(os.environ.get("EASIIO_CHATBOT_SMTP_TIMEOUT", "15"))
SITE_RAG_INDEX: dict[str, list[dict[str, Any]]] = {}
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
    body: dict[str, Any]
    headers: dict[str, str] | None = None


def json_response(status: int, body: dict[str, Any], headers: dict[str, str] | None = None) -> Response:
    return Response(status=status, body=body, headers=headers or {})


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
    candidates = phrase_counts + ([max(lesson_numbers)] if lesson_numbers else [])
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


def _rag_chunks_from_page_context(site_id: str, page_context: dict[str, Any], *, source: str = "page", content_id: str = "") -> list[dict[str, Any]]:
    content = sanitize_text(page_context.get("content") or page_context.get("text") or "", MAX_RAG_CONTENT_CHARS)
    if not content:
        return []
    url = sanitize_text(page_context.get("url") or "", 500)
    title = sanitize_text(page_context.get("title") or "", 300)
    new_chunks = []
    for chunk in chunk_website_content(content):
        tokens = tokenize(f"{title} {chunk}")
        if tokens:
            new_chunks.append({"text": chunk, "url": url, "title": title, "tokens": tokens, "source": source, "content_id": content_id, "site_id": site_id})
    return new_chunks


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
    return json.loads(json.dumps(DEFAULT_LEAD_FORM_CONFIG))


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


def sanitize_form_config(config: dict[str, Any]) -> dict[str, Any]:
    base = default_lead_form_config()
    result = {
        "title": sanitize_text(config.get("title") or base["title"], 120),
        "help_text": sanitize_text(config.get("help_text") or config.get("helpText") or base["help_text"], 240),
        "submit_label": sanitize_text(config.get("submit_label") or config.get("submitLabel") or base["submit_label"], 80),
        "fields": [],
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


ALLOWED_CRM_CONNECTOR_PROVIDERS = {"hubspot", "google_sheets"}
ALLOWED_CRM_CONNECTOR_FIELDS = {
    "hubspot": {"enabled", "mode", "token_env", "pipeline_id", "dealstage"},
    "google_sheets": {"enabled", "mode", "webhook_url_env", "sheet_name", "spreadsheet_id"},
}


def sanitize_crm_connector_site_config(config: dict[str, Any]) -> dict[str, Any]:
    providers: dict[str, Any] = {}
    raw_providers = config.get("providers") if isinstance(config.get("providers"), dict) else {}
    for provider, raw_provider_cfg in raw_providers.items():
        provider_name = sanitize_text(provider, 40).lower()
        if provider_name not in ALLOWED_CRM_CONNECTOR_PROVIDERS or not isinstance(raw_provider_cfg, dict):
            continue
        allowed = ALLOWED_CRM_CONNECTOR_FIELDS[provider_name]
        provider_cfg: dict[str, Any] = {"enabled": bool(raw_provider_cfg.get("enabled"))}
        for key in allowed:
            if key == "enabled" or key not in raw_provider_cfg:
                continue
            if key.endswith("_env"):
                value = sanitize_text(raw_provider_cfg.get(key), 120)
                if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,119}", value or ""):
                    provider_cfg[key] = value
                continue
            limit = 120 if key in {"pipeline_id", "dealstage", "sheet_name", "mode"} else 240
            provider_cfg[key] = sanitize_text(raw_provider_cfg.get(key), limit)
        provider_cfg.setdefault("mode", "sync_on_lead")
        providers[provider_name] = provider_cfg
    return {"enabled": bool(config.get("enabled")), "providers": providers}


def save_connectors_config(config: dict[str, Any]) -> None:
    path = connectors_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def crm_connectors_config_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    raw_config = load_connectors_config()
    sanitized = sanitize_connectors_config(raw_config)
    site_config = (sanitized.get("sites") or {}).get(site_id) or {"enabled": False, "providers": {}}
    return json_response(200, {"ok": True, "site_id": site_id, "site_config": site_config, "config": sanitized})


def crm_connectors_config_upsert_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "default", 100)
    raw_site_config = payload.get("site_config") or payload.get("siteConfig") or payload
    if not isinstance(raw_site_config, dict):
        return json_response(400, {"ok": False, "error": "site_config must be an object"})
    site_config = sanitize_crm_connector_site_config(raw_site_config)
    config = load_connectors_config()
    sites = config.get("sites") if isinstance(config.get("sites"), dict) else {}
    config["sites"] = sites
    sites[site_id] = site_config
    save_connectors_config(config)
    public_site_config = (sanitize_connectors_config(config).get("sites") or {}).get(site_id) or {"enabled": False, "providers": {}}
    return json_response(200, {"ok": True, "site_id": site_id, "site_config": public_site_config})




def crm_connectors_sync_log_handler(payload: dict[str, Any]) -> Response:
    site_id = sanitize_text(payload.get("site_id") or "", 100)
    status = sanitize_text(payload.get("status") or "", 40)
    provider = sanitize_text(payload.get("provider") or "", 40)
    try:
        limit = int(payload.get("limit") or 50)
    except Exception:
        limit = 50
    events = list_sync_events(
        site_id=site_id or None,
        status=status or None,
        provider=provider or None,
        limit=max(1, min(limit, 200)),
    )
    return json_response(200, {"ok": True, "site_id": site_id or None, "events": events})


def crm_connectors_retry_handler(payload: dict[str, Any], crm: SoloCRM) -> Response:
    event_id = sanitize_text(payload.get("event_id") or payload.get("eventId") or "", 80)
    if not event_id:
        return json_response(400, {"ok": False, "error": "event_id_required"})
    result = retry_sync_event(crm, event_id)
    status = 200 if result.get("ok") else 409
    return json_response(status, {"ok": bool(result.get("ok")), "event_id": event_id, "retry": result})


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


def find_lesson_number(text: str) -> str:
    match = re.search(r"(?:Lesson\s*|第\s*)(\d+)(?:\s*课)?", text, re.I)
    return match.group(1) if match else ""


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
        "You are a concise website assistant. Answer the user's question using only the provided website context. "
        "Do not paste the full context. If the context does not contain the answer, say you do not see it on this page. "
        "Keep the answer under 120 words, use bullets only when helpful, and match the user's language."
    )
    user_prompt = (
        f"Preferred language: {lang_hint}\n"
        f"Question: {question}\n\n"
        f"Website context:\n{context[:MAX_RAG_LLM_CONTEXT_CHARS]}"
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


def concise_extractive_answer(question: str, context: str, language: str = "") -> str:
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
    refresh_manual_rag_index(site_id)
    query_tokens = tokenize(message)
    query_lesson = find_lesson_number(message)
    if not query_tokens:
        return None
    scored: list[tuple[float, dict[str, Any]]] = []
    all_chunks = SITE_RAG_INDEX.get(site_id, [])
    all_context = "\n".join(normalize_whitespace(chunk.get("text", "")) for chunk in all_chunks)
    direct_answer = direct_count_answer(message, all_context[:MAX_RAG_LLM_CONTEXT_CHARS], language)
    if direct_answer:
        return {
            "reply": direct_answer,
            "answer_source": "website_rag",
            "sources": [{"title": chunk.get("title", ""), "url": chunk.get("url", "")} for chunk in all_chunks[:2]],
        }
    for chunk in all_chunks:
        overlap = query_tokens & set(chunk.get("tokens") or set())
        if not overlap:
            continue
        score = len(overlap) / max(1, len(query_tokens))
        # Give a small boost to exact phrase overlap for short policy/lesson questions.
        lower_text = str(chunk.get("text", "")).lower()
        if query_lesson:
            chunk_lesson = find_lesson_number(lower_text)
            if chunk_lesson == query_lesson:
                score += 1.0
            elif chunk_lesson:
                score -= 0.35
        for token in overlap:
            if token in lower_text:
                score += 0.08
        scored.append((score, chunk))
    if not scored:
        return None
    scored.sort(key=lambda item: item[0], reverse=True)
    if scored[0][0] < 0.18:
        return None
    selected = [chunk for _, chunk in scored[:3]]
    context = "\n".join(normalize_whitespace(chunk["text"]) for chunk in selected)
    context = context[:MAX_RAG_LLM_CONTEXT_CHARS].rstrip()
    direct_answer = direct_count_answer(message, context, language)
    if direct_answer:
        return {
            "reply": direct_answer,
            "answer_source": "website_rag",
            "sources": [{"title": chunk.get("title", ""), "url": chunk.get("url", "")} for chunk in selected[:2]],
        }
    llm_answer = call_llm_answer_formatter(message, context, language)
    answer_source = "website_rag_llm" if llm_answer else "website_rag"
    answer = llm_answer or concise_extractive_answer(message, context, language)
    if not answer:
        return None
    return {
        "reply": answer,
        "answer_source": answer_source,
        "sources": [{"title": chunk.get("title", ""), "url": chunk.get("url", "")} for chunk in selected[:2]],
    }


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
    crm_sync_result: dict[str, Any] | None = None

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
        if contact:
            crm_sync_result = sync_contact_to_enabled_crms(
                crm,
                site_id,
                int(contact["id"]),
                deal_id=int(deal["id"]) if deal else None,
                activity_id=int(activity["id"]) if activity else None,
            )

    rag_answer = answer_from_site_rag(site_id, message, sanitize_text(page_context.get("language") or "", 20))
    if contact:
        reply = "Thanks — I saved your request. Easiio can follow up with you soon."
        answer_source = "lead_capture"
    elif rag_answer:
        reply = rag_answer["reply"]
        answer_source = rag_answer["answer_source"]
    elif intent.get("sales"):
        reply = "I can help with that. Please share your work email or use the form so Easiio can follow up."
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
    if contact:
        body["crm_contact_id"] = contact["id"]
    if deal:
        body["crm_deal_id"] = deal["id"]
    if activity:
        body["crm_activity_id"] = activity["id"]
    if email_agent_result:
        body["email_agent"] = email_agent_result
    if crm_sync_result and crm_sync_result.get("enabled"):
        body["crm_sync"] = crm_sync_result
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
    crm_sync_result = None
    if contact:
        crm_sync_result = sync_contact_to_enabled_crms(
            crm,
            site_id,
            int(contact["id"]),
            deal_id=int(deal["id"]) if deal else None,
            activity_id=int(activity["id"]) if activity else None,
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
    if crm_sync_result and crm_sync_result.get("enabled"):
        body["crm_sync"] = crm_sync_result
    return json_response(200, body)


def route_request(method: str, path: str, headers: dict[str, str], body: bytes, crm: SoloCRM | None = None) -> Response:
    crm = crm or SoloCRM()
    parsed = urlparse(path)
    route = parsed.path
    method = method.upper()
    if method == "OPTIONS":
        return json_response(204, {})
    if method == "GET" and route == "/health":
        return json_response(200, {"ok": True, "service": SERVICE_NAME})
    if method == "GET" and route == "/api/rag/content":
        return rag_content_list_handler({key: values[-1] if values else "" for key, values in parse_qs(parsed.query).items()})
    if method == "GET" and route == "/api/chat/form-config":
        return form_config_handler({key: values[-1] if values else "" for key, values in parse_qs(parsed.query).items()})
    if method == "GET" and route == "/api/email-agent/config":
        return email_agent_config_handler({key: values[-1] if values else "" for key, values in parse_qs(parsed.query).items()})
    if method == "GET" and route == "/api/crm-connectors/config":
        return crm_connectors_config_handler({key: values[-1] if values else "" for key, values in parse_qs(parsed.query).items()})
    if method == "GET" and route == "/api/crm-connectors/sync-log":
        return crm_connectors_sync_log_handler({key: values[-1] if values else "" for key, values in parse_qs(parsed.query).items()})
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
    if route == "/api/chat/form-config":
        return form_config_upsert_handler(payload)
    if route == "/api/email-agent/config":
        return email_agent_config_upsert_handler(payload)
    if route == "/api/crm-connectors/config":
        return crm_connectors_config_upsert_handler(payload)
    if route == "/api/crm-connectors/retry":
        return crm_connectors_retry_handler(payload, crm)
    if route == "/api/rag/content":
        return rag_content_upsert_handler(payload)
    if route == "/api/rag/content/delete":
        return rag_content_delete_handler(payload)
    return json_response(404, {"ok": False, "error": "not found"})


class ChatbotHandler(BaseHTTPRequestHandler):
    server_version = "EasiioChatbotHTTP/0.1"

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length") or "0")
        if length > MAX_BODY_BYTES:
            return b""
        return self.rfile.read(length) if length else b""

    def _send(self, response: Response) -> None:
        body = b"" if response.status == 204 else json.dumps(response.body).encode("utf-8")
        self.send_response(response.status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        origin = self.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        for key, value in (response.headers or {}).items():
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
