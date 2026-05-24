#!/usr/bin/env python3
"""Tests for the website chatbot backend CRM bridge."""
from __future__ import annotations

import json
import os
import tempfile
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
        os.environ["SOLO_CRM_DB"] = str(self.db_path)
        os.environ["EASIIO_CHATBOT_RAG_STORE"] = str(self.rag_store_path)
        os.environ["EASIIO_CHATBOT_FORM_CONFIG_STORE"] = str(self.form_config_store_path)
        os.environ["EASIIO_CHATBOT_EMAIL_CONFIG_STORE"] = str(self.email_config_store_path)
        os.environ["EASIIO_CHATBOT_EMAIL_OUTBOX_DIR"] = str(self.email_outbox_path)
        for key in ("EASIIO_BREVO_API_KEY", "BREVO_API_KEY", "SENDINBLUE_API_KEY", "EASIIO_EMAIL_PROVIDER", "EASIIO_EMAIL_FROM"):
            os.environ.pop(key, None)
        # Keep tests isolated from the developer's real ~/.hermes/.env values.
        # app.load_env_file uses setdefault(), so these explicit test values
        # prevent real Brevo credentials from turning outbox tests into live sends.
        os.environ["EASIIO_EMAIL_PROVIDER"] = "outbox"
        os.environ["EASIIO_EMAIL_FROM"] = "test-sender@example.com"
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
        os.environ.pop("EASIIO_BREVO_API_KEY", None)
        os.environ.pop("BREVO_API_KEY", None)
        os.environ.pop("EASIIO_EMAIL_PROVIDER", None)
        os.environ.pop("EASIIO_EMAIL_FROM", None)

    def test_health_response_reports_ok(self):
        response = self.app.route_request("GET", "/health", {}, b"", self.crm)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body["ok"], True)
        self.assertEqual(response.body["service"], "easiio-website-chatbot")

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

    def test_message_uses_concise_extractive_fallback_when_llm_unavailable(self):
        payload = {
            "site_id": "ai-solo-company-class",
            "session_id": "chat_rag_fallback",
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
