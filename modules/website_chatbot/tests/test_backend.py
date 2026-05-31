#!/usr/bin/env python3
"""Tests for the website chatbot backend CRM bridge."""
from __future__ import annotations

import base64
import io
import json
import os
import zipfile
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

import sys
sys.path.insert(0, str(ROOT / "backend"))


class ChatbotBackendTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "crm.db"
        self.rag_store_path = Path(self.tmp.name) / "rag_content.json"
        self.form_config_store_path = Path(self.tmp.name) / "form_config.json"
        self.email_config_store_path = Path(self.tmp.name) / "email_agent_config.json"
        self.email_outbox_path = Path(self.tmp.name) / "email_outbox"
        self.rag_answer_log_path = Path(self.tmp.name) / "rag_answer_log.json"
        self.rag_feedback_path = Path(self.tmp.name) / "rag_feedback.json"
        self.rag_sync_log_path = Path(self.tmp.name) / "rag_sync_log.json"
        self.external_sources_path = Path(self.tmp.name) / "rag_external_sources.json"
        self.rag_schedule_path = Path(self.tmp.name) / "rag_refresh_schedule.json"
        self.rag_notifications_path = Path(self.tmp.name) / "rag_notifications.json"
        self.voice_cache_path = Path(self.tmp.name) / "voice_cache"
        self.docs_db_path = Path(self.tmp.name) / "easiio_docs.db"
        self.wiki_db_path = Path(self.tmp.name) / "website_wiki.db"
        os.environ["SOLO_CRM_DB"] = str(self.db_path)
        os.environ["EASIIO_CHATBOT_RAG_STORE"] = str(self.rag_store_path)
        os.environ["EASIIO_CHATBOT_FORM_CONFIG_STORE"] = str(self.form_config_store_path)
        os.environ["EASIIO_CHATBOT_EMAIL_CONFIG_STORE"] = str(self.email_config_store_path)
        os.environ["EASIIO_CHATBOT_EMAIL_OUTBOX_DIR"] = str(self.email_outbox_path)
        os.environ["EASIIO_CHATBOT_RAG_ANSWER_LOG"] = str(self.rag_answer_log_path)
        os.environ["EASIIO_CHATBOT_RAG_FEEDBACK_STORE"] = str(self.rag_feedback_path)
        os.environ["EASIIO_CHATBOT_RAG_SYNC_LOG"] = str(self.rag_sync_log_path)
        os.environ["EASIIO_CHATBOT_RAG_EXTERNAL_SOURCES"] = str(self.external_sources_path)
        os.environ["EASIIO_CHATBOT_RAG_REFRESH_SCHEDULE"] = str(self.rag_schedule_path)
        os.environ["EASIIO_CHATBOT_RAG_NOTIFICATIONS"] = str(self.rag_notifications_path)
        os.environ["EASIIO_CHATBOT_VOICE_CACHE_DIR"] = str(self.voice_cache_path)
        os.environ["VOICE_RESPONSE_PROVIDER"] = "mock"
        os.environ["VOICE_RESPONSE_MOCK_AUDIO_TEXT"] = "backend mock voice audio"
        os.environ["VOICE_RESPONSE_MAX_CHARS"] = "120"
        os.environ["EASIIO_DOCS_DB"] = str(self.docs_db_path)
        os.environ["EASIIO_WIKI_DB"] = str(self.wiki_db_path)
        for key in (
            "EASIIO_BREVO_API_KEY", "BREVO_API_KEY", "SENDINBLUE_API_KEY", "EASIIO_EMAIL_PROVIDER", "EASIIO_EMAIL_FROM",
            "EASIIO_CHATBOT_LLM_API_KEY", "OPENAI_API_KEY", "EASIIO_CHATBOT_LLM_BASE_URL", "OPENAI_BASE_URL",
            "EASIIO_CHATBOT_LLM_MODEL", "OPENAI_MODEL",
        ):
            os.environ.pop(key, None)
        # Keep tests isolated from the developer's real ~/.hermes/.env values.
        # app.load_env_file uses setdefault(), so these explicit test values
        # prevent real credentials from turning outbox tests into live sends
        # or making LLM-unavailable tests depend on the machine environment.
        os.environ["EASIIO_EMAIL_PROVIDER"] = "outbox"
        os.environ["EASIIO_EMAIL_FROM"] = "test-sender@example.com"
        os.environ["EASIIO_CHATBOT_LLM_API_KEY"] = ""
        os.environ["OPENAI_API_KEY"] = ""
        # Import after SOLO_CRM_DB is set so the CRM core default sees the test DB.
        import importlib
        import app
        self.app = importlib.reload(app)
        self.crm = self.app.SoloCRM(self.db_path)

    def tearDown(self) -> None:
        self.tmp.cleanup()
        os.environ.pop("SOLO_CRM_DB", None)
        os.environ.pop("EASIIO_CHATBOT_RAG_STORE", None)
        os.environ.pop("EASIIO_CHATBOT_FORM_CONFIG_STORE", None)
        os.environ.pop("EASIIO_CHATBOT_EMAIL_CONFIG_STORE", None)
        os.environ.pop("EASIIO_CHATBOT_EMAIL_OUTBOX_DIR", None)
        os.environ.pop("EASIIO_CHATBOT_RAG_ANSWER_LOG", None)
        os.environ.pop("EASIIO_CHATBOT_RAG_FEEDBACK_STORE", None)
        os.environ.pop("EASIIO_CHATBOT_RAG_SYNC_LOG", None)
        os.environ.pop("EASIIO_CHATBOT_RAG_EXTERNAL_SOURCES", None)
        os.environ.pop("EASIIO_CHATBOT_RAG_REFRESH_SCHEDULE", None)
        os.environ.pop("EASIIO_CHATBOT_RAG_NOTIFICATIONS", None)
        os.environ.pop("EASIIO_CHATBOT_VOICE_CACHE_DIR", None)
        os.environ.pop("VOICE_RESPONSE_PROVIDER", None)
        os.environ.pop("VOICE_RESPONSE_MOCK_AUDIO_TEXT", None)
        os.environ.pop("VOICE_RESPONSE_MAX_CHARS", None)
        os.environ.pop("VOICE_RESPONSE_API_KEY", None)
        os.environ.pop("VOICE_RESPONSE_BASE_URL", None)
        os.environ.pop("VOICE_RESPONSE_MODEL", None)
        os.environ.pop("VOICE_RESPONSE_VOICE", None)
        os.environ.pop("VOICE_RESPONSE_FORMAT", None)
        os.environ.pop("EASIIO_DOCS_DB", None)
        os.environ.pop("EASIIO_WIKI_DB", None)
        os.environ.pop("EASIIO_BREVO_API_KEY", None)
        os.environ.pop("BREVO_API_KEY", None)
        os.environ.pop("EASIIO_EMAIL_PROVIDER", None)
        os.environ.pop("EASIIO_EMAIL_FROM", None)
        os.environ.pop("EASIIO_CHATBOT_LLM_API_KEY", None)
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("EASIIO_CHATBOT_LLM_BASE_URL", None)
        os.environ.pop("OPENAI_BASE_URL", None)
        os.environ.pop("EASIIO_CHATBOT_LLM_MODEL", None)
        os.environ.pop("OPENAI_MODEL", None)

    def seed_docs_db(self) -> None:
        ts = int(time.time())
        with sqlite3.connect(self.docs_db_path) as conn:
            conn.executescript("""
                CREATE TABLE docs_documents (
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
            """)
            rows = [
                ("phase3-site", "agent-manual", "Agent Manual", "Agent docs", "Agent Manual explains the autonomous agent demo and setup checklist.", "published", "public", '["rag"]', 1),
                ("phase3-site", "private-plan", "Private Plan", "", "Secret roadmap should not sync.", "published", "private", '["rag"]', 1),
                ("phase3-site", "draft-note", "Draft Note", "", "Draft docs should not sync.", "draft", "public", '["rag"]', 1),
                ("other-site", "other-doc", "Other Doc", "", "Other site docs should not sync.", "published", "public", '["rag"]', 1),
            ]
            conn.executemany(
                """
                INSERT INTO docs_documents(site_id, slug, title, summary, content, status, visibility, framework_targets_json, rag_enabled, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [row + (ts, ts) for row in rows],
            )

    def seed_wiki_db(self) -> None:
        ts = int(time.time())
        with sqlite3.connect(self.wiki_db_path) as conn:
            conn.executescript("""
                CREATE TABLE wiki_pages (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  site_id TEXT NOT NULL,
                  slug TEXT NOT NULL,
                  title TEXT NOT NULL,
                  summary TEXT DEFAULT '',
                  content TEXT NOT NULL,
                  content_format TEXT NOT NULL DEFAULT 'markdown',
                  status TEXT NOT NULL DEFAULT 'draft',
                  category TEXT DEFAULT '',
                  tags_json TEXT DEFAULT '[]',
                  rag_enabled INTEGER NOT NULL DEFAULT 1,
                  created_at INTEGER NOT NULL,
                  updated_at INTEGER NOT NULL,
                  UNIQUE(site_id, slug)
                );
            """)
            rows = [
                ("phase3-site", "sales-faq", "Sales FAQ", "", "Sales FAQ says the demo is available for AI agents and CRM workflows.", "published", 1),
                ("phase3-site", "disabled", "Disabled", "", "Disabled wiki page should not sync.", "published", 0),
                ("phase3-site", "draft", "Draft Wiki", "", "Draft wiki should not sync.", "draft", 1),
            ]
            conn.executemany(
                """
                INSERT INTO wiki_pages(site_id, slug, title, summary, content, status, rag_enabled, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [row + (ts, ts) for row in rows],
            )

    def test_health_response_reports_ok(self):
        response = self.app.route_request("GET", "/health", {}, b"", self.crm)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body["ok"], True)
        self.assertEqual(response.body["service"], "easiio-website-chatbot")

    def test_chat_voice_endpoint_generates_site_scoped_audio_and_serves_file(self):
        payload = {
            "site_id": "voice-demo-site",
            "text": "Hello from the website chatbot voice response.",
            "voice": "teacher",
            "format": "mp3",
        }
        response = self.app.route_request("POST", "/api/chat/voice", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertTrue(response.body["ok"])
        self.assertEqual(response.body["mime_type"], "audio/mpeg")
        self.assertEqual(response.body["provider"], "mock")
        self.assertTrue(response.body["audio_url"].startswith("api/chat/voice/"))
        self.assertNotIn("Hello from", response.body["audio_url"])

        audio = self.app.route_request("GET", "/" + response.body["audio_url"], {}, b"", self.crm)
        self.assertEqual(audio.status, 200)
        self.assertEqual(audio.headers["Content-Type"], "audio/mpeg")
        self.assertEqual(audio.body, b"backend mock voice audio")

    def test_chat_voice_endpoint_rejects_overlong_text_without_audio_file(self):
        payload = {"site_id": "voice-demo-site", "text": "x" * 140}
        response = self.app.route_request("POST", "/api/chat/voice", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 400)
        self.assertEqual(response.body["error_code"], "text_too_long")
        self.assertFalse(list(self.voice_cache_path.glob("*.mp3")))

    def test_session_endpoint_returns_session_and_welcome(self):
        payload = {"site_id": "easiio-main", "page_url": "https://www.easiio.com/pricing/"}
        response = self.app.route_request("POST", "/api/chat/session", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertTrue(response.body["session_id"].startswith("chat_"))
        self.assertIn("welcome_message", response.body)

    def test_form_config_defaults_remove_phone_and_add_message(self):
        response = self.app.route_request("GET", "/api/chat/form-config?site_id=easiio-main", {}, b"", self.crm)
        self.assertEqual(response.status, 200)
        config = response.body["form_config"]
        names = [field["name"] for field in config["fields"]]
        self.assertEqual(names, ["name", "email", "company", "message"])
        self.assertNotIn("phone", names)
        message_field = next(field for field in config["fields"] if field["name"] == "message")
        self.assertEqual(message_field["type"], "textarea")
        self.assertTrue(message_field["required"])

    def test_form_config_saves_safe_widget_voice_settings(self):
        custom = {
            "site_id": "voice-settings-site",
            "form_config": {
                "title": "Talk to us",
                "help_text": "Voice can be enabled by the admin.",
                "submit_label": "Send",
                "widget_config": {
                    "voice_enabled": True,
                    "voice_label": "Play answer",
                    "voice_autoplay": True,
                    "voice": "teacher",
                    "voice_format": "wav",
                    "provider_api_key": "should-never-save",
                    "raw_cache_path": "/tmp/secret-audio",
                },
                "fields": [
                    {"name": "email", "label": "Email", "type": "email", "required": True},
                    {"name": "message", "label": "Message", "type": "textarea", "required": True},
                ],
            },
        }
        save = self.app.route_request("POST", "/api/chat/form-config", {}, json.dumps(custom).encode(), self.crm)
        self.assertEqual(save.status, 200)
        widget_config = save.body["form_config"]["widget_config"]
        self.assertEqual(widget_config["voice_enabled"], True)
        self.assertEqual(widget_config["voice_label"], "Play answer")
        self.assertEqual(widget_config["voice_autoplay"], True)
        self.assertEqual(widget_config["voice"], "teacher")
        self.assertEqual(widget_config["voice_format"], "wav")
        self.assertEqual(widget_config["voice_input_enabled"], False)
        self.assertEqual(widget_config["voice_input_label"], "Speak")
        self.assertEqual(widget_config["voice_input_language"], "auto")
        self.assertNotIn("provider_api_key", json.dumps(widget_config))
        self.assertNotIn("raw_cache_path", json.dumps(widget_config))

        loaded = self.app.route_request("GET", "/api/chat/form-config?site_id=voice-settings-site", {}, b"", self.crm)
        self.assertEqual(loaded.body["form_config"]["widget_config"], widget_config)

    def test_form_config_saves_safe_widget_voice_input_settings(self):
        custom = {
            "site_id": "voice-input-site",
            "form_config": {
                "widget_config": {
                    "voice_input_enabled": True,
                    "voice_input_label": "Ask by voice",
                    "voice_input_language": "zh-CN",
                    "speech_api_key": "should-never-save",
                    "transcript_raw_audio_path": "/tmp/raw-mic.wav",
                }
            },
        }
        save = self.app.route_request("POST", "/api/chat/form-config", {}, json.dumps(custom).encode(), self.crm)
        self.assertEqual(save.status, 200)
        widget_config = save.body["form_config"]["widget_config"]
        self.assertEqual(widget_config["voice_input_enabled"], True)
        self.assertEqual(widget_config["voice_input_label"], "Ask by voice")
        self.assertEqual(widget_config["voice_input_language"], "zh-CN")
        self.assertNotIn("speech_api_key", json.dumps(widget_config))
        self.assertNotIn("transcript_raw_audio_path", json.dumps(widget_config))

        loaded = self.app.route_request("GET", "/api/chat/form-config?site_id=voice-input-site", {}, b"", self.crm)
        self.assertEqual(loaded.body["form_config"]["widget_config"], widget_config)

    def test_form_config_api_is_site_specific_and_sanitizes_fields(self):
        custom = {
            "site_id": "factory-site",
            "form_config": {
                "title": "Talk to sales",
                "help_text": "Tell us what you need.",
                "submit_label": "Send request",
                "fields": [
                    {"name": "name", "label": "Full name", "type": "text", "required": True},
                    {"name": "email", "label": "Email", "type": "email", "required": True},
                    {"name": "budget", "label": "Budget", "type": "text", "required": False},
                    {"name": "details", "label": "Project details", "type": "textarea", "required": True},
                    {"name": "bad<script>", "label": "Bad", "type": "select", "required": True},
                ],
            },
        }
        save = self.app.route_request("POST", "/api/chat/form-config", {}, json.dumps(custom).encode(), self.crm)
        self.assertEqual(save.status, 200)
        fields = save.body["form_config"]["fields"]
        self.assertEqual([field["name"] for field in fields], ["name", "email", "budget", "details"])
        self.assertEqual(fields[-1]["type"], "textarea")

        factory = self.app.route_request("GET", "/api/chat/form-config?site_id=factory-site", {}, b"", self.crm)
        other = self.app.route_request("GET", "/api/chat/form-config?site_id=other-site", {}, b"", self.crm)
        self.assertEqual(factory.body["form_config"]["title"], "Talk to sales")
        self.assertEqual([field["name"] for field in other.body["form_config"]["fields"]], ["name", "email", "company", "message"])

    def test_session_endpoint_indexes_page_context_without_crashing(self):
        payload = {
            "site_id": "ai-solo-company-class",
            "page_context": {
                "url": "https://example.com/ai-solo-company/",
                "title": "AI Solo Company Bootcamp",
                "content": "AI Solo Company Bootcamp has 14 lessons and a Website Assistant lesson.",
            },
        }
        response = self.app.route_request("POST", "/api/chat/session", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        # Repeat the same page session after chunks already exist; this used to
        # crash because update_site_rag_index referenced url/title out of scope.
        response = self.app.route_request("POST", "/api/chat/session", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        indexed = self.app.SITE_RAG_INDEX["ai-solo-company-class"]
        self.assertEqual(indexed[0]["url"], "https://example.com/ai-solo-company/")
        self.assertEqual(indexed[0]["title"], "AI Solo Company Bootcamp")

    def test_enhanced_rag_chunks_preserve_sections_neighbors_and_summaries(self):
        content = """
        AI Solo Company Bootcamp

        Curriculum
        Lesson 1: Foundation. Install tools and define the business.
        Lesson 2: Website. Build the public website.
        Lesson 3: Website Assistant. Add chatbot, RAG knowledge, CRM, and follow-up email.

        Pricing
        The bootcamp includes 14 lessons.
        """
        chunks = self.app.build_enhanced_rag_chunks(
            site_id="ai-solo-company-class",
            page_context={"url": "https://example.com", "title": "AI Solo", "content": content},
            source="page",
        )
        self.assertGreaterEqual(len(chunks), 3)
        lesson3 = next(chunk for chunk in chunks if "Lesson 3" in chunk["text"])
        self.assertEqual(lesson3["section"], "Curriculum")
        self.assertIn("summary", lesson3)
        self.assertIn("tokens", lesson3)
        self.assertIn("chunk_id", lesson3)
        self.assertTrue(lesson3.get("prev_id") or lesson3.get("next_id"))
        self.assertIn("search_text", lesson3)

    def test_enhanced_rag_query_plan_expands_course_question(self):
        plan = self.app.build_rag_query_plan("How many classes do you have and what does lesson 3 build?", language="en")
        self.assertEqual(plan["intent"], "fact_lookup")
        combined = " ".join(plan["queries"] + plan["keywords"])
        self.assertIn("lesson", combined.lower())
        self.assertIn("class", combined.lower())
        self.assertIn("course", combined.lower())
        self.assertIn("3", combined)

    def test_hybrid_retrieval_uses_summary_and_hyde_to_find_answer_chunk(self):
        payload = {
            "site_id": "ai-solo-company-class",
            "page_context": {
                "url": "https://example.com/ai-solo-company/",
                "title": "AI Solo Company Bootcamp",
                "content": " ".join([
                    "Curriculum",
                    "Lesson 1: Foundation. Install tools and define the business.",
                    "Lesson 2: Website. Build the public website.",
                    "Lesson 3: Website Assistant and Lead Capture. Configure the website AI assistant, knowledge base, lead form, CRM database, and generate the first follow-up email. Output: AI lead system.",
                    "Lesson 4: Finance Agent. Build bookkeeping automation.",
                ]),
            },
        }
        self.app.update_site_rag_index("ai-solo-company-class", payload["page_context"])
        with patch.object(self.app, "call_llm_hyde_queries", return_value=["AI assistant lead capture CRM follow-up email"]):
            plan = self.app.build_rag_query_plan("What does the chatbot lesson build?", language="en")
        candidates = self.app.retrieve_rag_candidates("ai-solo-company-class", plan, limit=10)
        self.assertTrue(candidates)
        self.assertIn("Lesson 3", candidates[0]["chunk"]["text"])
        self.assertIn("hyde_overlap", candidates[0]["reasons"])

    def test_hybrid_retrieval_without_llm_matches_chatbot_to_website_assistant(self):
        payload = {
            "site_id": "ai-solo-company-class",
            "page_context": {
                "url": "https://example.com/ai-solo-company/",
                "title": "AI Solo Company Bootcamp",
                "content": " ".join([
                    "AI Solo Company Bootcamp. Curriculum.",
                    "Lesson 1: Foundation. Install tools and define the business.",
                    "Lesson 2: Website. Build the public website.",
                    "Lesson 3: Website Assistant and Lead Capture. Configure the website AI assistant, knowledge base, lead form, CRM database, and generate the first follow-up email. Output: AI lead system.",
                    "Lesson 4: Finance Agent. Build bookkeeping automation. Pricing. The bootcamp includes 14 lessons.",
                ]),
            },
        }
        self.app.update_site_rag_index("ai-solo-company-class", payload["page_context"])
        plan = self.app.build_rag_query_plan("What does the chatbot lesson build?", language="en")
        candidates = self.app.retrieve_rag_candidates("ai-solo-company-class", plan, limit=10)
        ranked = self.app.rerank_rag_candidates("What does the chatbot lesson build?", candidates, keep=3)
        self.assertIn("Lesson 3", ranked[0]["chunk"]["text"])

    def test_course_question_prefers_specific_seo_lesson_over_generic_manual_content(self):
        site_id = "ai-solo-company-class"
        self.app.index_manual_rag_content(site_id, [
            {
                "content_id": "manual-guide",
                "title": "AI Solo Company Website Feature User Guide",
                "url": "/wiki/ai-solo-website-feature-guide",
                "content": "Public home page visitors course landing page class overview chatbot and footer inquiry form. Add new lesson notes or SOPs in Wiki Manager.",
            }
        ])
        self.app.update_site_rag_index(site_id, {
            "url": "https://example.com/ai-solo-company/",
            "title": "AI Solo Company Bootcamp",
            "content": " ".join([
                "课程大纲。第 7 课 AI 品牌与视觉系统，生成品牌定位、Logo 概念、配色和社交媒体模板。",
                "第 8 课 AI SEO 内容 Agent，研究长尾关键词和买家意图，生成文章大纲、标题、Meta、博客主题库与内链计划。产出：SEO 内容引擎。",
                "第 9 课 GEO / AI 搜索优化，面向 ChatGPT、Claude、Perplexity 等 AI 搜索创建 FAQ、比较页、最佳方案页与专家内容。产出：GEO 内容计划。",
            ]),
        })
        question = "Do we teach how to do SEO and in which class?"
        plan = self.app.build_rag_query_plan(question, language="en")
        candidates = self.app.retrieve_rag_candidates(site_id, plan, limit=10)
        ranked = self.app.rerank_rag_candidates(question, candidates, keep=3)
        self.assertIn("第 8 课", ranked[0]["chunk"]["text"])
        self.assertIn("SEO", ranked[0]["chunk"]["text"])

    def test_enhanced_rag_verification_rejects_unsupported_llm_number(self):
        payload = {
            "site_id": "ai-solo-company-class",
            "session_id": "chat_rag_verify",
            "message": "How many lessons are in the bootcamp?",
            "page_context": {
                "language": "en",
                "content": "AI Solo Company Bootcamp. Build Your AI Solo Company Operating System in 14 Lessons. Lesson 1: Foundation. Lesson 2: Website. Lesson 3: Website Assistant and Lead Capture.",
            },
        }
        with patch.object(self.app, "call_llm_answer_formatter", return_value="The bootcamp has 30 lessons."):
            response = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body["answer_source"], "website_rag")
        self.assertIn("14", response.body["reply"])
        self.assertNotIn("30", response.body["reply"])
        self.assertIn(response.body.get("confidence"), {"high", "medium"})

    def test_rag_debug_endpoint_explains_retrieval_pipeline(self):
        payload = {
            "site_id": "phase2-debug-site",
            "question": "What does the chatbot lesson build?",
            "page_context": {
                "url": "https://example.com/course",
                "title": "AI Solo Course",
                "language": "en",
                "content": "Lesson 3: Website Assistant and Lead Capture. Configure the website AI assistant, knowledge base, lead form, CRM database, and first follow-up email. Output: AI lead system.",
            },
        }
        response = self.app.route_request("POST", "/api/rag/debug", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertTrue(response.body["ok"])
        self.assertEqual(response.body["site_id"], "phase2-debug-site")
        self.assertEqual(response.body["query_plan"]["intent"], "fact_lookup")
        self.assertIn("chatbot", " ".join(response.body["query_plan"]["keywords"]))
        self.assertGreaterEqual(len(response.body["candidates"]), 1)
        self.assertIn("score", response.body["candidates"][0])
        self.assertIn("reasons", response.body["candidates"][0])
        self.assertGreaterEqual(len(response.body["selected_sources"]), 1)
        self.assertIn("AI lead system", response.body["answer"]["reply"])
        self.assertIn(response.body["answer"]["confidence"], {"high", "medium"})

    def test_rag_answer_log_is_site_specific_and_masks_contact_info(self):
        payload = {
            "site_id": "phase2-log-site",
            "session_id": "chat_phase2_log",
            "message": "How many lessons are included?",
            "page_context": {
                "language": "en",
                "content": "AI Solo Company Bootcamp includes 14 lessons total.",
            },
        }
        response = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        log = self.app.route_request("GET", "/api/rag/answer-log?site_id=phase2-log-site", {}, b"", self.crm)
        self.assertEqual(log.status, 200)
        self.assertEqual(len(log.body["items"]), 1)
        item = log.body["items"][0]
        self.assertEqual(item["site_id"], "phase2-log-site")
        self.assertIn("lessons", item["question"])
        self.assertNotIn("visitor@example.com", json.dumps(item))
        self.assertEqual(item["answer_source"], response.body["answer_source"])
        other = self.app.route_request("GET", "/api/rag/answer-log?site_id=other-phase2-site", {}, b"", self.crm)
        self.assertEqual(other.body["items"], [])

    def test_rag_feedback_endpoint_records_sanitized_helpfulness(self):
        payload = {
            "site_id": "phase2-feedback-site",
            "answer_log_id": "raglog_test",
            "question": "Can you email alice@example.com?",
            "answer": "The class has 14 lessons.",
            "rating": "not_helpful",
            "reason": "missing information",
            "comment": "wrong answer; call 555-123-4567",
        }
        response = self.app.route_request("POST", "/api/rag/feedback", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertTrue(response.body["ok"])
        self.assertEqual(response.body["item"]["rating"], "not_helpful")
        self.assertIn("[email]", response.body["item"]["question"])
        self.assertIn("[phone]", response.body["item"]["comment"])
        stored = self.app.route_request("GET", "/api/rag/feedback?site_id=phase2-feedback-site", {}, b"", self.crm)
        self.assertEqual(len(stored.body["items"]), 1)
        self.assertNotIn("alice@example.com", json.dumps(stored.body))
        self.assertNotIn("555-123-4567", json.dumps(stored.body))

    def test_rag_eval_endpoint_runs_golden_questions(self):
        payload = {
            "site_id": "phase2-eval-site",
            "page_context": {
                "language": "en",
                "content": "AI Solo Company Bootcamp includes 14 lessons. Lesson 3: Website Assistant and Lead Capture builds an AI lead system with CRM and follow-up email.",
            },
            "cases": [
                {"question": "How many lessons are in the bootcamp?", "expected_answer_contains": ["14"], "expected_source_contains": ["14 lessons"]},
                {"question": "What does lesson 3 build?", "expected_answer_contains": ["AI lead system", "CRM"], "expected_source_contains": ["Lesson 3"]},
            ],
        }
        response = self.app.route_request("POST", "/api/rag/eval", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body["summary"]["total"], 2)
        self.assertEqual(response.body["summary"]["passed"], 2)
        self.assertTrue(all(item["passed"] for item in response.body["results"]))

    def test_rag_sync_sources_imports_docs_and_wiki_without_leaking_private_content(self):
        self.seed_docs_db()
        self.seed_wiki_db()
        manual = {
            "site_id": "phase3-site",
            "content_id": "manual:pricing",
            "title": "Manual Pricing",
            "url": "manual://pricing",
            "content": "Manual pricing note stays in the knowledge base.",
        }
        manual_response = self.app.route_request("POST", "/api/rag/content", {}, json.dumps(manual).encode(), self.crm)
        self.assertEqual(manual_response.status, 200)

        payload = {"site_id": "phase3-site", "sources": ["docs", "wiki"], "confirm_sync": True, "approved_by": "tester@example.com"}
        response = self.app.route_request("POST", "/api/rag/sync-sources", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertTrue(response.body["ok"])
        self.assertEqual(response.body["summary"]["synced_items"], 2)
        self.assertEqual(response.body["summary"]["kept_manual_items"], 1)
        self.assertIn("docs", response.body["summary"]["source_counts"])
        self.assertIn("wiki", response.body["summary"]["source_counts"])
        self.assertNotIn("tester@example.com", json.dumps(response.body))

        listed = self.app.route_request("GET", "/api/rag/content?site_id=phase3-site", {}, b"", self.crm)
        titles = [item["title"] for item in listed.body["items"]]
        body_json = json.dumps(listed.body)
        self.assertIn("Manual Pricing", titles)
        self.assertIn("Agent Manual", titles)
        self.assertIn("Sales FAQ", titles)
        self.assertNotIn("Secret roadmap", body_json)
        self.assertNotIn("Draft docs", body_json)
        self.assertNotIn("Disabled wiki", body_json)

        question = {"site_id": "phase3-site", "session_id": "phase3-chat", "message": "What does the agent manual explain?"}
        answer = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(question).encode(), self.crm)
        self.assertEqual(answer.status, 200)
        self.assertEqual(answer.body["answer_source"], "website_rag")
        self.assertIn("autonomous agent demo", answer.body["reply"])

    def test_rag_sources_endpoint_reports_multisource_status_and_last_sync(self):
        self.seed_docs_db()
        self.seed_wiki_db()
        before = self.app.route_request("GET", "/api/rag/sources?site_id=phase3-site", {}, b"", self.crm)
        self.assertEqual(before.status, 200)
        self.assertEqual(before.body["sources"]["docs"]["eligible_count"], 1)
        self.assertEqual(before.body["sources"]["wiki"]["eligible_count"], 1)
        self.assertEqual(before.body["sources"]["manual"]["stored_count"], 0)

        sync_payload = {"site_id": "phase3-site", "sources": ["docs", "wiki"], "confirm_sync": True}
        self.app.route_request("POST", "/api/rag/sync-sources", {}, json.dumps(sync_payload).encode(), self.crm)
        after = self.app.route_request("GET", "/api/rag/sources?site_id=phase3-site", {}, b"", self.crm)
        self.assertEqual(after.body["sources"]["manual"]["stored_count"], 2)
        self.assertEqual(after.body["last_sync"]["site_id"], "phase3-site")
        self.assertEqual(after.body["last_sync"]["synced_items"], 2)


    def test_rag_external_source_items_store_and_sync_wordpress_uploads(self):
        wordpress_payload = {
            "site_id": "phase4-site",
            "source": "wordpress",
            "items": [
                {
                    "slug": "homepage",
                    "title": "WordPress Homepage",
                    "url": "https://example.com/",
                    "status": "publish",
                    "visibility": "public",
                    "content": "WordPress homepage says Easiio builds AI agents, websites, and CRM automation.",
                },
                {
                    "slug": "private-page",
                    "title": "Private WP",
                    "status": "private",
                    "visibility": "private",
                    "content": "Private WordPress strategy should not sync.",
                },
            ],
            "approved_by": "phase4-admin@example.com",
        }
        upload_payload = {
            "site_id": "phase4-site",
            "source": "upload",
            "items": [
                {
                    "slug": "course-brochure",
                    "title": "Course Brochure",
                    "filename": "course-brochure.md",
                    "mime_type": "text/markdown",
                    "content": "Uploaded brochure covers the AI solo company course, chatbot RAG, and lead capture workflow.",
                    "status": "published",
                    "visibility": "public",
                },
                {
                    "slug": "draft-upload",
                    "title": "Draft Upload",
                    "content": "Draft uploaded document should not sync.",
                    "status": "draft",
                    "visibility": "public",
                },
            ],
        }
        wp_save = self.app.route_request("POST", "/api/rag/source-items", {}, json.dumps(wordpress_payload).encode(), self.crm)
        upload_save = self.app.route_request("POST", "/api/rag/source-items", {}, json.dumps(upload_payload).encode(), self.crm)
        self.assertEqual(wp_save.status, 200)
        self.assertEqual(upload_save.status, 200)
        self.assertEqual(wp_save.body["eligible_count"], 1)
        self.assertNotIn("phase4-admin@example.com", json.dumps(wp_save.body))

        sources = self.app.route_request("GET", "/api/rag/sources?site_id=phase4-site", {}, b"", self.crm)
        self.assertEqual(sources.body["sources"]["wordpress"]["eligible_count"], 1)
        self.assertEqual(sources.body["sources"]["upload"]["eligible_count"], 1)
        self.assertFalse(sources.body["sources"]["wordpress"].get("requires_payload", False))

        sync_payload = {"site_id": "phase4-site", "sources": ["wordpress", "upload"], "confirm_sync": True, "approved_by": "phase4-admin@example.com"}
        sync = self.app.route_request("POST", "/api/rag/sync-sources", {}, json.dumps(sync_payload).encode(), self.crm)
        self.assertEqual(sync.status, 200)
        self.assertEqual(sync.body["summary"]["synced_items"], 2)
        self.assertEqual(sync.body["summary"]["source_counts"], {"wordpress": 1, "upload": 1})
        body_json = json.dumps(sync.body)
        self.assertNotIn("Private WordPress strategy", body_json)
        self.assertNotIn("Draft uploaded document", body_json)
        self.assertNotIn("phase4-admin@example.com", body_json)

        question = {"site_id": "phase4-site", "session_id": "phase4-chat", "message": "What does the uploaded brochure cover?"}
        answer = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(question).encode(), self.crm)
        self.assertEqual(answer.status, 200)
        self.assertEqual(answer.body["answer_source"], "website_rag")
        self.assertIn("chatbot RAG", answer.body["reply"])

    def test_rag_source_items_get_and_delete_are_site_scoped(self):
        payload = {"site_id": "phase4-site", "source": "wordpress", "items": [{"slug": "faq", "title": "FAQ", "content": "FAQ sync content", "status": "publish", "visibility": "public"}]}
        other_payload = {"site_id": "other-site", "source": "wordpress", "items": [{"slug": "other", "title": "Other", "content": "Other site content", "status": "publish", "visibility": "public"}]}
        self.app.route_request("POST", "/api/rag/source-items", {}, json.dumps(payload).encode(), self.crm)
        self.app.route_request("POST", "/api/rag/source-items", {}, json.dumps(other_payload).encode(), self.crm)

        listed = self.app.route_request("GET", "/api/rag/source-items?site_id=phase4-site&source=wordpress", {}, b"", self.crm)
        self.assertEqual(listed.status, 200)
        self.assertEqual(len(listed.body["items"]), 1)
        self.assertEqual(listed.body["items"][0]["slug"], "faq")
        self.assertNotIn("Other site content", json.dumps(listed.body))

        deleted = self.app.route_request("POST", "/api/rag/source-items/delete", {}, json.dumps({"site_id": "phase4-site", "source": "wordpress", "slug": "faq"}).encode(), self.crm)
        self.assertEqual(deleted.status, 200)
        self.assertTrue(deleted.body["deleted"])
        after = self.app.route_request("GET", "/api/rag/source-items?site_id=phase4-site&source=wordpress", {}, b"", self.crm)
        self.assertEqual(after.body["items"], [])


    def test_rag_wordpress_pull_fetches_public_rest_posts_and_stages_without_secrets(self):
        wp_posts = [
            {
                "id": 101,
                "slug": "services",
                "link": "https://wp.example.com/services/",
                "status": "publish",
                "title": {"rendered": "Services &amp; AI Agents"},
                "excerpt": {"rendered": "<p>Public services excerpt.</p>"},
                "content": {"rendered": "<h2>Services</h2><p>Easiio builds WordPress AI agent websites with CRM automation.</p>"},
                "modified_gmt": "2026-05-27T01:02:03",
            }
        ]
        captured = {}

        class FakeResponse:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return json.dumps(wp_posts).encode()
            def getcode(self):
                return 200

        def fake_urlopen(request, timeout=0):
            captured["url"] = request.full_url
            captured["headers"] = dict(request.header_items())
            return FakeResponse()

        payload = {
            "site_id": "phase5-site",
            "base_url": "https://wp.example.com",
            "post_types": ["pages"],
            "per_page": 5,
            "auth_env": "WP_APP_PASSWORD",
            "confirm_pull": True,
            "approved_by": "puller@example.com",
        }
        with patch("app.urllib.request.urlopen", fake_urlopen):
            response = self.app.route_request("POST", "/api/rag/wordpress/pull", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body["stored_count"], 1)
        self.assertEqual(response.body["eligible_count"], 1)
        self.assertIn("/wp-json/wp/v2/pages", captured["url"])
        body_json = json.dumps(response.body)
        self.assertNotIn("WP_APP_PASSWORD", body_json)
        self.assertNotIn("puller@example.com", body_json)

        sync = self.app.route_request("POST", "/api/rag/sync-sources", {}, json.dumps({"site_id": "phase5-site", "sources": ["wordpress"], "confirm_sync": True}).encode(), self.crm)
        self.assertEqual(sync.status, 200)
        self.assertEqual(sync.body["summary"]["synced_items"], 1)
        listed = self.app.route_request("GET", "/api/rag/content?site_id=phase5-site", {}, b"", self.crm)
        self.assertIn("WordPress AI agent websites", json.dumps(listed.body))

    def test_rag_extract_document_stages_docx_upload_text_for_review(self):
        docx_io = io.BytesIO()
        document_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>
          <w:p><w:r><w:t>AI Solo Company Document</w:t></w:r></w:p>
          <w:p><w:r><w:t>DOCX extraction imports chatbot RAG setup and CRM workflow details.</w:t></w:r></w:p>
        </w:body></w:document>"""
        with zipfile.ZipFile(docx_io, "w") as z:
            z.writestr("word/document.xml", document_xml)
        payload = {
            "site_id": "phase5-site",
            "filename": "ai-solo-guide.docx",
            "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "content_base64": base64.b64encode(docx_io.getvalue()).decode(),
            "title": "AI Solo Guide",
            "confirm_extract": True,
            "approved_by": "docs@example.com",
        }
        response = self.app.route_request("POST", "/api/rag/upload/extract", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertTrue(response.body["ok"])
        self.assertEqual(response.body["source"], "upload")
        self.assertEqual(response.body["eligible_count"], 1)
        self.assertIn("DOCX extraction imports", response.body["text_preview"])
        self.assertNotIn("docs@example.com", json.dumps(response.body))

        sync = self.app.route_request("POST", "/api/rag/sync-sources", {}, json.dumps({"site_id": "phase5-site", "sources": ["upload"], "confirm_sync": True}).encode(), self.crm)
        self.assertEqual(sync.status, 200)
        self.assertEqual(sync.body["summary"]["synced_items"], 1)
        question = {"site_id": "phase5-site", "session_id": "phase5-doc", "message": "What does the document import cover?"}
        answer = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(question).encode(), self.crm)
        self.assertEqual(answer.body["answer_source"], "website_rag")
        self.assertIn("chatbot RAG", answer.body["reply"])

    def test_rag_wordpress_pull_requires_confirmation_and_valid_public_url(self):
        missing = self.app.route_request("POST", "/api/rag/wordpress/pull", {}, json.dumps({"site_id": "phase5-site", "base_url": "https://wp.example.com"}).encode(), self.crm)
        self.assertEqual(missing.status, 400)
        self.assertTrue(missing.body["requires_pull_approval"])
        bad = self.app.route_request("POST", "/api/rag/wordpress/pull", {}, json.dumps({"site_id": "phase5-site", "base_url": "file:///tmp/private", "confirm_pull": True}).encode(), self.crm)
        self.assertEqual(bad.status, 400)

    def test_rag_review_preview_reports_new_changed_unchanged_and_deleted_sources(self):
        initial = {
            "site_id": "phase6-site",
            "source": "wordpress",
            "items": [
                {"slug": "home", "title": "Home", "content": "Original home content", "status": "publish", "visibility": "public"},
                {"slug": "faq", "title": "FAQ", "content": "FAQ content stays the same", "status": "publish", "visibility": "public"},
            ],
        }
        self.app.route_request("POST", "/api/rag/source-items", {}, json.dumps(initial).encode(), self.crm)
        self.app.route_request("POST", "/api/rag/sync-sources", {}, json.dumps({"site_id": "phase6-site", "sources": ["wordpress"], "confirm_sync": True}).encode(), self.crm)

        updated = {
            "site_id": "phase6-site",
            "source": "wordpress",
            "items": [
                {"slug": "home", "title": "Home", "content": "Updated home content with new pricing", "status": "publish", "visibility": "public"},
                {"slug": "faq", "title": "FAQ", "content": "FAQ content stays the same", "status": "publish", "visibility": "public"},
                {"slug": "new-guide", "title": "New Guide", "content": "New public guide content", "status": "publish", "visibility": "public"},
            ],
        }
        self.app.route_request("POST", "/api/rag/source-items", {}, json.dumps(updated).encode(), self.crm)
        deleted = self.app.route_request("POST", "/api/rag/source-items/delete", {}, json.dumps({"site_id": "phase6-site", "source": "wordpress", "slug": "faq"}).encode(), self.crm)
        self.assertTrue(deleted.body["deleted"])

        preview = self.app.route_request("POST", "/api/rag/sync-preview", {}, json.dumps({"site_id": "phase6-site", "sources": ["wordpress"]}).encode(), self.crm)
        self.assertEqual(preview.status, 200)
        statuses = {item["content_id"]: item["review_status"] for item in preview.body["items"]}
        self.assertEqual(statuses["wordpress:phase6-site:home"], "changed")
        self.assertEqual(statuses["wordpress:phase6-site:new-guide"], "new")
        self.assertEqual(statuses["wordpress:phase6-site:faq"], "deleted_upstream")
        changed = next(item for item in preview.body["items"] if item["content_id"] == "wordpress:phase6-site:home")
        self.assertIn("Original home", changed["diff_preview"])
        self.assertIn("Updated home", changed["diff_preview"])
        self.assertEqual(preview.body["summary"]["changed"], 1)
        self.assertEqual(preview.body["summary"]["deleted_upstream"], 1)

        review = self.app.route_request("GET", "/api/rag/review?site_id=phase6-site", {}, b"", self.crm)
        self.assertEqual(review.status, 200)
        self.assertEqual(review.body["summary"]["new"], 1)
        self.assertEqual(review.body["summary"]["changed"], 1)
        self.assertEqual(review.body["summary"]["deleted_upstream"], 1)
        self.assertIn("last_sync", review.body)
        self.assertIn("sources", review.body)

    def test_rag_sync_rollback_restores_previous_synced_items_without_touching_manual(self):
        manual = {"site_id": "phase6-rollback", "content_id": "manual:note", "title": "Manual Note", "content": "Manual content survives rollback."}
        self.app.route_request("POST", "/api/rag/content", {}, json.dumps(manual).encode(), self.crm)
        v1 = {"site_id": "phase6-rollback", "source": "upload", "items": [{"slug": "guide", "title": "Guide", "content": "Version one upload content", "status": "published", "visibility": "public"}]}
        self.app.route_request("POST", "/api/rag/source-items", {}, json.dumps(v1).encode(), self.crm)
        sync1 = self.app.route_request("POST", "/api/rag/sync-sources", {}, json.dumps({"site_id": "phase6-rollback", "sources": ["upload"], "confirm_sync": True}).encode(), self.crm)
        self.assertEqual(sync1.status, 200)

        v2 = {"site_id": "phase6-rollback", "source": "upload", "items": [{"slug": "guide", "title": "Guide", "content": "Version two upload content", "status": "published", "visibility": "public"}]}
        self.app.route_request("POST", "/api/rag/source-items", {}, json.dumps(v2).encode(), self.crm)
        sync2 = self.app.route_request("POST", "/api/rag/sync-sources", {}, json.dumps({"site_id": "phase6-rollback", "sources": ["upload"], "confirm_sync": True}).encode(), self.crm)
        self.assertEqual(sync2.status, 200)
        self.assertIn("rollback_id", sync2.body["summary"])

        rollback = self.app.route_request("POST", "/api/rag/rollback", {}, json.dumps({"site_id": "phase6-rollback", "rollback_id": sync2.body["summary"]["rollback_id"], "confirm_rollback": True, "approved_by": "rollback@example.com"}).encode(), self.crm)
        self.assertEqual(rollback.status, 200)
        self.assertTrue(rollback.body["ok"])
        self.assertNotIn("rollback@example.com", json.dumps(rollback.body))

        listed = self.app.route_request("GET", "/api/rag/content?site_id=phase6-rollback", {}, b"", self.crm)
        body_json = json.dumps(listed.body)
        self.assertIn("Version one upload content", body_json)
        self.assertNotIn("Version two upload content", body_json)
        self.assertIn("Manual content survives rollback", body_json)

        missing_confirm = self.app.route_request("POST", "/api/rag/rollback", {}, json.dumps({"site_id": "phase6-rollback", "rollback_id": sync2.body["summary"]["rollback_id"]}).encode(), self.crm)
        self.assertEqual(missing_confirm.status, 400)
        self.assertTrue(missing_confirm.body["requires_rollback_approval"])

    def test_rag_refresh_schedule_config_sanitizes_and_lists_due_sites(self):
        payload = {
            "site_id": "phase7-site",
            "schedule": {
                "enabled": True,
                "sources": ["wordpress", "upload", "invalid"],
                "interval_minutes": 15,
                "stale_after_minutes": 30,
                "notify_on_changes": True,
                "notify_recipients": "ops@example.com bad-value owner@example.com",
                "auto_sync": False,
            },
        }
        save = self.app.route_request("POST", "/api/rag/refresh-schedule", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(save.status, 200)
        self.assertTrue(save.body["schedule"]["enabled"])
        self.assertEqual(save.body["schedule"]["sources"], ["wordpress", "upload"])
        self.assertEqual(save.body["schedule"]["notify_recipients"], ["ops@example.com", "owner@example.com"])
        self.assertNotIn("bad-value", json.dumps(save.body))

        listed = self.app.route_request("GET", "/api/rag/refresh-schedule?site_id=phase7-site", {}, b"", self.crm)
        self.assertEqual(listed.status, 200)
        self.assertEqual(listed.body["schedule"]["interval_minutes"], 15)

        due = self.app.route_request("GET", "/api/rag/refresh-due", {}, b"", self.crm)
        self.assertEqual(due.status, 200)
        self.assertIn("phase7-site", [item["site_id"] for item in due.body["due_sites"]])

    def test_rag_scheduled_refresh_creates_notifications_and_respects_dry_run(self):
        self.app.route_request("POST", "/api/rag/refresh-schedule", {}, json.dumps({
            "site_id": "phase7-refresh",
            "schedule": {
                "enabled": True,
                "sources": ["wordpress"],
                "interval_minutes": 10,
                "stale_after_minutes": 20,
                "notify_on_changes": True,
                "notify_recipients": ["ops@example.com"],
                "auto_sync": False,
            },
        }).encode(), self.crm)
        initial = {"site_id": "phase7-refresh", "source": "wordpress", "items": [{"slug": "home", "title": "Home", "content": "Old homepage text", "status": "publish", "visibility": "public"}]}
        self.app.route_request("POST", "/api/rag/source-items", {}, json.dumps(initial).encode(), self.crm)
        self.app.route_request("POST", "/api/rag/sync-sources", {}, json.dumps({"site_id": "phase7-refresh", "sources": ["wordpress"], "confirm_sync": True}).encode(), self.crm)
        updated = {"site_id": "phase7-refresh", "source": "wordpress", "items": [{"slug": "home", "title": "Home", "content": "New homepage text with updated offer", "status": "publish", "visibility": "public"}]}
        self.app.route_request("POST", "/api/rag/source-items", {}, json.dumps(updated).encode(), self.crm)

        dry_run = self.app.route_request("POST", "/api/rag/run-scheduled-refresh", {}, json.dumps({"site_id": "phase7-refresh", "dry_run": True}).encode(), self.crm)
        self.assertEqual(dry_run.status, 200)
        self.assertEqual(dry_run.body["results"][0]["review_summary"]["changed"], 1)
        self.assertEqual(dry_run.body["results"][0]["action"], "preview_only")

        notifications = self.app.route_request("GET", "/api/rag/notifications?site_id=phase7-refresh", {}, b"", self.crm)
        self.assertEqual(notifications.status, 200)
        self.assertEqual(notifications.body["unread_count"], 1)
        body_json = json.dumps(notifications.body)
        self.assertIn("changed", body_json)
        self.assertNotIn("ops@example.com", body_json)

    def test_rag_scheduled_refresh_can_auto_sync_and_mark_notifications_read(self):
        self.app.route_request("POST", "/api/rag/refresh-schedule", {}, json.dumps({
            "site_id": "phase7-auto",
            "schedule": {
                "enabled": True,
                "sources": ["upload"],
                "interval_minutes": 10,
                "notify_on_changes": True,
                "notify_recipients": ["ops@example.com"],
                "auto_sync": True,
            },
        }).encode(), self.crm)
        source = {"site_id": "phase7-auto", "source": "upload", "items": [{"slug": "guide", "title": "Guide", "content": "Phase 7 auto sync content", "status": "published", "visibility": "public"}]}
        self.app.route_request("POST", "/api/rag/source-items", {}, json.dumps(source).encode(), self.crm)

        run = self.app.route_request("POST", "/api/rag/run-scheduled-refresh", {}, json.dumps({"site_id": "phase7-auto"}).encode(), self.crm)
        self.assertEqual(run.status, 200)
        self.assertEqual(run.body["results"][0]["action"], "synced")
        self.assertIn("rollback_id", run.body["results"][0])
        listed = self.app.route_request("GET", "/api/rag/content?site_id=phase7-auto", {}, b"", self.crm)
        self.assertIn("Phase 7 auto sync content", json.dumps(listed.body))

        notifications = self.app.route_request("GET", "/api/rag/notifications?site_id=phase7-auto", {}, b"", self.crm)
        self.assertEqual(notifications.body["unread_count"], 1)
        notification_id = notifications.body["items"][0]["notification_id"]
        ack = self.app.route_request("POST", "/api/rag/notifications/read", {}, json.dumps({"site_id": "phase7-auto", "notification_id": notification_id}).encode(), self.crm)
        self.assertEqual(ack.status, 200)
        self.assertEqual(ack.body["unread_count"], 0)

    def test_message_with_email_and_demo_intent_creates_contact_deal_activity(self):
        payload = {
            "site_id": "easiio-main",
            "session_id": "chat_test",
            "message": "I want a demo for AI agents. My email is founder@example.com",
            "visitor": {"name": "Jian", "company": "Easiio"},
            "page_context": {"url": "https://www.easiio.com/pricing/", "title": "Pricing"},
        }
        response = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertTrue(response.body["lead_captured"])
        self.assertIn("crm_contact_id", response.body)
        self.assertIn("crm_deal_id", response.body)
        self.assertIn("book_demo", response.body["suggested_actions"])

        contacts = self.crm.search_contacts("founder@example.com")
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]["email"], "founder@example.com")
        self.assertEqual(contacts[0]["company_name"], "Easiio")
        deals = self.crm.list_deals(contact_id=contacts[0]["id"])
        self.assertEqual(len(deals), 1)
        self.assertIn("Website chatbot", deals[0]["title"])
        activities = self.crm.list_activities(contact_id=contacts[0]["id"])
        self.assertEqual(len(activities), 1)
        self.assertIn("I want a demo", activities[0]["body"])

    def test_message_answers_from_website_page_content_rag_without_lead_form(self):
        payload = {
            "site_id": "ai-solo-company-class",
            "session_id": "chat_rag",
            "message": "How many lessons are in the bootcamp and what does lesson 3 build?",
            "page_context": {
                "url": "https://example.com/ai-solo-company/",
                "title": "AI Solo Company Bootcamp",
                "language": "en",
                "content": "AI Solo Company Bootcamp. Build Your AI Solo Company Operating System in 14 Lessons. Lesson 3: Website Assistant and Lead Capture. Configure the website AI assistant, knowledge base, lead form, CRM database, and generate the first follow-up email. Output: AI lead system."
            },
        }
        response = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertFalse(response.body["lead_captured"])
        self.assertFalse(response.body["show_lead_form"])
        self.assertEqual(response.body["answer_source"], "website_rag")
        self.assertIn("14 Lessons", response.body["reply"])
        self.assertIn("Website Assistant", response.body["reply"])
        self.assertIn("AI lead system", response.body["reply"])

    def test_message_formats_rag_context_with_llm_and_does_not_dump_full_page(self):
        payload = {
            "site_id": "ai-solo-company-class",
            "session_id": "chat_rag_llm",
            "message": "What does lesson 3 build?",
            "page_context": {
                "url": "https://example.com/ai-solo-company/",
                "title": "AI Solo Company Bootcamp",
                "language": "en",
                "content": " ".join([
                    "Lesson 1: Install Hermes and run the example website.",
                    "Lesson 2: Customize the website template.",
                    "Lesson 3: Website Assistant and Lead Capture. Configure the website AI assistant, knowledge base, lead form, CRM database, and generate the first follow-up email. Output: AI lead system.",
                    "Lesson 4: Hermes Skills and Codex customization.",
                    "Lesson 5: AI Finance Agent.",
                ]),
            },
        }
        with patch.object(self.app, "call_llm_answer_formatter", return_value="Lesson 3 builds an AI lead system: a website assistant, knowledge base, lead form, CRM database, and first follow-up email.") as formatter:
            response = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body["answer_source"], "website_rag_llm")
        self.assertLessEqual(len(response.body["reply"]), 240)
        self.assertIn("AI lead system", response.body["reply"])
        self.assertNotIn("Lesson 5", response.body["reply"])
        formatter.assert_called_once()
        call_args = formatter.call_args.args
        self.assertEqual(call_args[0], "What does lesson 3 build?")
        self.assertIn("Lesson 3", call_args[1])

    def test_message_uses_question_specific_fallback_when_llm_unavailable(self):
        payload = {
            "site_id": "ai-solo-company-class",
            "session_id": "chat_rag_fallback",
            "message": "Do you teach AI agents and SEO?",
            "page_context": {
                "language": "en",
                "content": "AI Solo Company teaches AI agents, websites, marketing automation, SEO, and chatbot CRM lessons.",
            },
        }
        with patch.object(self.app, "call_llm_answer_formatter", return_value=""):
            response = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body["answer_source"], "website_rag")
        self.assertLessEqual(len(response.body["reply"]), 420)
        self.assertIn("Yes", response.body["reply"])
        self.assertIn("AI agents", response.body["reply"])
        self.assertIn("SEO", response.body["reply"])
        self.assertNotIn("Based on this website:", response.body["reply"])

    def test_message_uses_concise_marketing_capability_fallback_when_llm_unavailable(self):
        payload = {
            "site_id": "ai-solo-company-class",
            "session_id": "chat_rag_marketing_fallback",
            "message": "请告诉我,就是市场的功能大概有哪一些市场,就是做市场Marketing的功能大概有哪一些你的能力",
            "page_context": {
                "language": "zh-CN",
                "content": " ".join([
                    "AI Solo Company 可以生产 SEO、GEO、短视频内容生产线。",
                    "网站 AI 助手可答疑并收集销售线索。",
                    "CRM、邮件跟进、销售客服流程打通。",
                    "财务、合规、市场研究 Agent 可协助运营。",
                    "课程还有营销自动化、预算、实验和 ROI 分析。",
                ]),
            },
        }
        with patch.object(self.app, "call_llm_answer_formatter", return_value=""):
            response = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(payload, ensure_ascii=False).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body["answer_source"], "website_rag")
        self.assertLessEqual(len(response.body["reply"]), 260)
        self.assertIn("市场/Marketing", response.body["reply"])
        self.assertIn("SEO", response.body["reply"])
        self.assertIn("线索", response.body["reply"])
        self.assertNotIn("根据当前网站内容：", response.body["reply"])
        self.assertNotIn("查看 14 课大纲", response.body["reply"])

    def test_message_uses_concise_extractive_fallback_when_llm_unavailable(self):
        payload = {
            "site_id": "ai-solo-company-class",
            "session_id": "chat_rag_fallback_lesson",
            "message": "What does lesson 3 build?",
            "page_context": {
                "language": "en",
                "content": " ".join([
                    "Lesson 1: Install Hermes and run the example website.",
                    "Lesson 2: Customize the website template.",
                    "Lesson 3: Website Assistant and Lead Capture. Configure the website AI assistant, knowledge base, lead form, CRM database, and generate the first follow-up email. Output: AI lead system.",
                    "Lesson 4: Hermes Skills and Codex customization.",
                    "Lesson 5: AI Finance Agent.",
                ]),
            },
        }
        with patch.object(self.app, "call_llm_answer_formatter", return_value=""):
            response = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body["answer_source"], "website_rag")
        self.assertLessEqual(len(response.body["reply"]), 420)
        self.assertIn("AI lead system", response.body["reply"])
        self.assertNotIn("Lesson 5", response.body["reply"])

    def test_rag_debug_reports_llm_unavailable_when_no_key_loaded(self):
        payload = {
            "site_id": "ai-solo-company-class",
            "question": "Do you teach AI agents and SEO?",
            "page_context": {
                "language": "en",
                "content": "AI Solo Company teaches AI agents, websites, marketing automation, SEO, and chatbot CRM lessons.",
            },
        }
        response = self.app.route_request("POST", "/api/rag/debug", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertFalse(response.body["llm_status"]["configured"])
        self.assertEqual(response.body["llm_status"]["reason"], "missing_api_key")
        self.assertEqual(response.body["answer"]["answer_source"], "website_rag")

    def test_message_answers_total_class_count_directly_without_lead_form(self):
        payload = {
            "site_id": "ai-solo-company-class",
            "session_id": "chat_class_count",
            "message": "how many classes total?",
            "page_context": {
                "language": "en",
                "content": "AI Solo Company Bootcamp. Build Your AI Solo Company Operating System in 14 Lessons. Lesson 1: Foundation. Lesson 2: Website. Lesson 3: Website Assistant and Lead Capture.",
            },
        }
        with patch.object(self.app, "call_llm_answer_formatter", return_value=""):
            response = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body["answer_source"], "website_rag")
        self.assertFalse(response.body["show_lead_form"])
        self.assertIn("14", response.body["reply"])
        self.assertRegex(response.body["reply"].lower(), r"lesson|class")
        self.assertNotIn("Please share your work email", response.body["reply"])

    def test_ai_solo_company_demo_site_id_uses_course_rag_alias_before_sales_handoff(self):
        # The public voice demo embeds data-site-id="ai-solo-company", while the
        # imported AI Solo Company course knowledge currently lives under
        # ai-solo-company-class. The backend should bridge that alias and answer
        # from RAG instead of immediately asking for a work email.
        self.rag_store_path.write_text(json.dumps({
            "version": 1,
            "sites": {
                "ai-solo-company-class": [
                    {
                        "content_id": "course-overview",
                        "title": "AI Solo Company Course Overview",
                        "url": "/wiki/course-overview",
                        "content": "AI Solo Company Bootcamp teaches AI agents, website building, chatbot RAG, CRM automation, marketing automation, and follow-up workflows in 14 Lessons."
                    }
                ]
            }
        }), encoding="utf-8")
        payload = {
            "site_id": "ai-solo-company",
            "session_id": "chat_ai_solo_alias",
            "message": "Do you teach AI agents and chatbot RAG?",
            "page_context": {
                "language": "en",
                "content": "Chatbot voice call demo page. Ask by chat, speech, or start a voice call."
            },
        }
        with patch.object(self.app, "call_llm_answer_formatter", return_value=""):
            response = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body["answer_source"], "website_rag")
        self.assertFalse(response.body["show_lead_form"])
        self.assertIn("AI agents", response.body["reply"])
        self.assertIn("chatbot RAG", response.body["reply"])
        self.assertNotIn("Please share your work email", response.body["reply"])

    def test_cached_visitor_contact_does_not_turn_normal_chat_into_lead_capture(self):
        lead_payload = {
            "site_id": "ai-solo-company-class",
            "session_id": "chat_after_form",
            "name": "Jian",
            "email": "jian-after-form@example.com",
            "company": "Easiio",
            "message": "I want more information about the class.",
            "page_context": {"language": "en", "content": "AI Solo Company Bootcamp has 14 Lessons."},
        }
        lead_response = self.app.route_request("POST", "/api/chat/lead", {}, json.dumps(lead_payload).encode(), self.crm)
        self.assertEqual(lead_response.status, 200)

        chat_payload = {
            "site_id": "ai-solo-company-class",
            "session_id": "chat_after_form",
            "message": "how many classes you have?",
            "visitor": {"name": "Jian", "email": "jian-after-form@example.com", "company": "Easiio"},
            "page_context": {
                "language": "en",
                "content": "AI Solo Company Bootcamp. Build Your AI Solo Company Operating System in 14 Lessons. Lesson 1: Foundation. Lesson 2: Website. Lesson 3: Website Assistant and Lead Capture.",
            },
        }
        with patch.object(self.app, "call_llm_answer_formatter", return_value=""):
            response = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(chat_payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertFalse(response.body["lead_captured"])
        self.assertEqual(response.body["answer_source"], "website_rag")
        self.assertIn("14", response.body["reply"])
        self.assertNotIn("saved your request", response.body["reply"])
        contacts = self.crm.search_contacts("jian-after-form@example.com")
        self.assertEqual(len(contacts), 1)
        activities = self.crm.list_activities(contact_id=contacts[0]["id"])
        self.assertEqual(len(activities), 1)

    def test_sales_intent_does_not_request_lead_form_when_forms_disabled(self):
        payload = {
            "site_id": "ai-solo-company-class",
            "session_id": "chat_forms_off",
            "message": "I need help and want more information",
            "page_context": {"language": "en", "content": "AI Solo Company Bootcamp. Build your AI solo company in 14 lessons."},
        }
        response = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertFalse(response.body["show_lead_form"])

    def test_message_uses_site_specific_rag_content(self):
        first = {
            "site_id": "site-a",
            "session_id": "chat_a",
            "message": "What is the refund policy?",
            "page_context": {"content": "Refund policy: Site A gives a 14 day refund window for bootcamp students."},
        }
        second = {
            "site_id": "site-b",
            "session_id": "chat_b",
            "message": "What is the refund policy?",
            "page_context": {"content": "Refund policy: Site B only offers account credit, not cash refunds."},
        }
        response_a = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(first).encode(), self.crm)
        response_b = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(second).encode(), self.crm)
        self.assertEqual(response_a.status, 200)
        self.assertEqual(response_b.status, 200)
        self.assertIn("14 day refund", response_a.body["reply"])
        self.assertNotIn("account credit", response_a.body["reply"])
        self.assertIn("account credit", response_b.body["reply"])
        self.assertNotIn("14 day refund", response_b.body["reply"])

    def test_rag_content_api_is_site_specific_and_powers_chat_answers(self):
        add_a = {
            "site_id": "factory-site",
            "title": "Factory capabilities",
            "url": "https://factory.example/capabilities",
            "content": "Factory RAG: Xinyuntong provides CNC milling, EDM, precision grinding, and tungsten carbide components.",
        }
        add_b = {
            "site_id": "ai-solo-site",
            "title": "AI Solo curriculum",
            "url": "https://ai.example/classes",
            "content": "AI Solo RAG: the bootcamp teaches agents, CRM, website chatbot, and follow-up automation.",
        }
        response_a = self.app.route_request("POST", "/api/rag/content", {}, json.dumps(add_a).encode(), self.crm)
        response_b = self.app.route_request("POST", "/api/rag/content", {}, json.dumps(add_b).encode(), self.crm)
        self.assertEqual(response_a.status, 200)
        self.assertEqual(response_b.status, 200)
        self.assertTrue(response_a.body["content_id"])
        self.assertTrue(response_b.body["content_id"])

        list_a = self.app.route_request("GET", "/api/rag/content?site_id=factory-site", {}, b"", self.crm)
        list_b = self.app.route_request("GET", "/api/rag/content?site_id=ai-solo-site", {}, b"", self.crm)
        self.assertEqual(list_a.status, 200)
        self.assertEqual(list_b.status, 200)
        self.assertEqual(len(list_a.body["items"]), 1)
        self.assertEqual(len(list_b.body["items"]), 1)
        self.assertIn("Xinyuntong", list_a.body["items"][0]["content"])
        self.assertIn("bootcamp", list_b.body["items"][0]["content"])

        factory_question = {
            "site_id": "factory-site",
            "session_id": "chat_factory_rag",
            "message": "What machining capabilities does Xinyuntong provide?",
        }
        ai_question = {
            "site_id": "ai-solo-site",
            "session_id": "chat_ai_rag",
            "message": "What does the bootcamp teach?",
        }
        response_factory = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(factory_question).encode(), self.crm)
        response_ai = self.app.route_request("POST", "/api/chat/message", {}, json.dumps(ai_question).encode(), self.crm)
        self.assertEqual(response_factory.status, 200)
        self.assertEqual(response_ai.status, 200)
        self.assertEqual(response_factory.body["answer_source"], "website_rag")
        self.assertIn("CNC milling", response_factory.body["reply"])
        self.assertNotIn("bootcamp", response_factory.body["reply"])
        self.assertIn("follow-up automation", response_ai.body["reply"])
        self.assertNotIn("tungsten carbide", response_ai.body["reply"])

    def test_rag_content_api_deletes_only_requested_site_content(self):
        add_a = {"site_id": "site-delete-a", "title": "A", "content": "Delete test A has AlphaOnly support."}
        add_b = {"site_id": "site-delete-b", "title": "B", "content": "Delete test B has BetaOnly support."}
        response_a = self.app.route_request("POST", "/api/rag/content", {}, json.dumps(add_a).encode(), self.crm)
        response_b = self.app.route_request("POST", "/api/rag/content", {}, json.dumps(add_b).encode(), self.crm)
        self.assertEqual(response_a.status, 200)
        self.assertEqual(response_b.status, 200)
        delete_payload = {"site_id": "site-delete-a", "content_id": response_a.body["content_id"]}
        delete_response = self.app.route_request("POST", "/api/rag/content/delete", {}, json.dumps(delete_payload).encode(), self.crm)
        self.assertEqual(delete_response.status, 200)
        self.assertTrue(delete_response.body["deleted"])
        list_a = self.app.route_request("GET", "/api/rag/content?site_id=site-delete-a", {}, b"", self.crm)
        list_b = self.app.route_request("GET", "/api/rag/content?site_id=site-delete-b", {}, b"", self.crm)
        self.assertEqual(list_a.body["items"], [])
        self.assertEqual(len(list_b.body["items"]), 1)

    def test_email_agent_config_is_site_specific_and_sanitized(self):
        payload = {
            "site_id": "factory-site",
            "email_config": {
                "enabled": True,
                "owner_recipients": "owner@example.com, bad-value, manager@example.com",
                "welcome_subject": "Welcome {{name}}",
                "welcome_body": "Hi {{name}}, thanks for contacting {{site_id}}. {{message}}",
                "owner_subject": "New lead: {{email}}",
                "owner_body": "Lead {{name}} at {{company}} from {{page_url}}",
                "send_owner_notification": True,
                "send_welcome_email": True,
            },
        }
        save = self.app.route_request("POST", "/api/email-agent/config", {}, json.dumps(payload).encode(), self.crm)
        self.assertEqual(save.status, 200)
        self.assertEqual(save.body["email_config"]["owner_recipients"], ["owner@example.com", "manager@example.com"])
        self.assertTrue(save.body["email_config"]["enabled"])

        factory = self.app.route_request("GET", "/api/email-agent/config?site_id=factory-site", {}, b"", self.crm)
        other = self.app.route_request("GET", "/api/email-agent/config?site_id=other-site", {}, b"", self.crm)
        self.assertEqual(factory.body["email_config"]["welcome_subject"], "Welcome {{name}}")
        self.assertEqual(other.body["email_config"]["owner_recipients"], [])

    def test_brevo_api_key_configuration_sends_via_transactional_api_without_exposing_key(self):
        os.environ["EASIIO_BREVO_API_KEY"] = "test-brevo-secret"
        os.environ["EASIIO_EMAIL_FROM"] = "robot@example.com"
        config = self.app.sanitize_email_agent_config({
            "provider": "brevo",
            "from_name": "Robot",
            "from_email": "robot@example.com",
        })
        self.assertEqual(config["provider"], "brevo")
        self.assertTrue(self.app.configured_brevo().get("enabled"))
        calls = []

        class FakeResponse:
            status = 201
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return b'{"messageId":"brevo-test-id"}'

        def fake_urlopen(request, timeout=0):
            calls.append(request)
            return FakeResponse()

        original_urlopen = self.app.urllib.request.urlopen
        self.app.urllib.request.urlopen = fake_urlopen
        try:
            result = self.app.send_email_message(["alice@example.com"], "Welcome", "Hello Alice", config)
        finally:
            self.app.urllib.request.urlopen = original_urlopen
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "sent")
        self.assertEqual(result["provider"], "brevo")
        self.assertEqual(len(calls), 1)
        request = calls[0]
        self.assertEqual(request.full_url, "https://api.brevo.com/v3/smtp/email")
        self.assertEqual(request.get_header("Api-key"), "test-brevo-secret")
        body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(body["sender"]["email"], "robot@example.com")
        self.assertEqual(body["to"][0]["email"], "alice@example.com")
        self.assertEqual(body["subject"], "Welcome")

    def test_new_lead_triggers_welcome_and_owner_email_outbox_once(self):
        config = {
            "site_id": "email-site",
            "email_config": {
                "enabled": True,
                "owner_recipients": ["owner@example.com", "manager@example.com"],
                "welcome_subject": "Welcome {{name}}",
                "welcome_body": "Hi {{name}}, we received: {{message}}",
                "owner_subject": "New {{site_id}} lead: {{email}}",
                "owner_body": "Name: {{name}}\nEmail: {{email}}\nCompany: {{company}}\nMessage: {{message}}",
                "send_owner_notification": True,
                "send_welcome_email": True,
            },
        }
        save = self.app.route_request("POST", "/api/email-agent/config", {}, json.dumps(config).encode(), self.crm)
        self.assertEqual(save.status, 200)
        lead = {
            "site_id": "email-site",
            "session_id": "chat_email",
            "message": "I want to register for the AI class",
            "name": "Alice",
            "email": "alice@example.com",
            "company": "Example Co",
            "page_context": {"url": "https://example.com/register", "title": "Register"},
        }
        response = self.app.route_request("POST", "/api/chat/lead", {}, json.dumps(lead).encode(), self.crm)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body["email_agent"]["sent"], 2)
        outbox_files = sorted(self.email_outbox_path.glob("*.json"))
        self.assertEqual(len(outbox_files), 2)
        outbox = [json.loads(path.read_text()) for path in outbox_files]
        self.assertIn("alice@example.com", [msg["to"][0] for msg in outbox])
        owner_msg = next(msg for msg in outbox if "owner@example.com" in msg["to"])
        self.assertIn("New email-site lead", owner_msg["subject"])
        self.assertIn("Alice", owner_msg["body"])

        duplicate = self.app.route_request("POST", "/api/chat/lead", {}, json.dumps(lead).encode(), self.crm)
        self.assertEqual(duplicate.status, 200)
        self.assertEqual(duplicate.body.get("email_agent", {}).get("sent", 0), 0)
        self.assertEqual(len(list(self.email_outbox_path.glob("*.json"))), 2)

    def test_lead_endpoint_updates_existing_contact_without_duplicate(self):
        first = {
            "site_id": "easiio-main",
            "session_id": "chat_test",
            "message": "Please contact me about pricing",
            "name": "Alice",
            "email": "alice@example.com",
            "company": "Example Co",
            "phone": "+1 555 100 2000",
        }
        second = dict(first, name="Alice Updated", phone="+1 555 999 0000")
        response1 = self.app.route_request("POST", "/api/chat/lead", {}, json.dumps(first).encode(), self.crm)
        response2 = self.app.route_request("POST", "/api/chat/lead", {}, json.dumps(second).encode(), self.crm)
        self.assertEqual(response1.status, 200)
        self.assertEqual(response2.status, 200)
        self.assertTrue(response2.body["lead_captured"])
        self.assertEqual(response1.body["crm_contact_id"], response2.body["crm_contact_id"])
        contacts = self.crm.search_contacts("alice@example.com")
        self.assertEqual(len(contacts), 1)
        self.assertEqual(contacts[0]["name"], "Alice Updated")
        self.assertEqual(contacts[0]["phone"], "+1 555 999 0000")



class WidgetVoiceCallConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        import importlib
        import app
        self.app = importlib.reload(app)

    def test_sanitize_widget_config_preserves_safe_voice_call_settings_only(self):
        config = self.app.sanitize_widget_config({
            'voice_call_enabled': True,
            'voice_call_label': 'Talk to AI',
            'voice_call_api_base': 'https://voice.example.com/',
            'voice_call_consent_text': 'Voice may be transcribed.',
            'voice_call_auto_start': True,
            'twilio_api_key': 'SHOULD_NOT_SURVIVE',
            'api_key': 'SHOULD_NOT_SURVIVE',
        })
        self.assertTrue(config['voice_call_enabled'])
        self.assertEqual(config['voice_call_label'], 'Talk to AI')
        self.assertEqual(config['voice_call_api_base'], 'https://voice.example.com/')
        self.assertEqual(config['voice_call_consent_text'], 'Voice may be transcribed.')
        serialized = json.dumps(config)
        self.assertNotIn('twilio_api_key', serialized)
        self.assertNotIn('SHOULD_NOT_SURVIVE', serialized)
        self.assertNotIn('api_key', serialized)

if __name__ == "__main__":
    unittest.main(verbosity=2)
