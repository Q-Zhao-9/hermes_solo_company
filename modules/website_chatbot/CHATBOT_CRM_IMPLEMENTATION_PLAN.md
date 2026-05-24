# Website Chatbot + Solo CRM Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Add an embeddable website chatbot that appears as a popup chat dialog on web pages, captures leads, answers basic questions, and writes contacts/deals/activities into the existing Solo CRM MCP server.

**Architecture:** Build one reusable JavaScript widget that can be loaded by any website with a single `<script>` tag. The widget talks to a small backend API; the backend handles LLM/chat policy and calls the existing Solo CRM MCP server tools. WordPress gets a lightweight plugin that injects the widget script into `wp_footer`; Next.js gets a component/script snippet that loads the same widget.

**Tech Stack:** Vanilla JS widget, CSS, Python FastAPI or Node/Next API backend, existing SQLite Solo CRM MCP server at `/home/jianl/.hermes/tools/solo_crm`, optional WordPress plugin PHP, optional Next.js `<Script />` integration.

---

## 1. Current CRM Capability

Existing CRM MCP server:

```text
/home/jianl/.hermes/tools/solo_crm/server.py
/home/jianl/.hermes/tools/solo_crm/crm_core.py
/home/jianl/.hermes/tools/solo_crm/solo_crm.db
```

Available CRM tools:

```text
crm_create_company
crm_create_contact
crm_search_contacts
crm_get_contact
crm_update_contact
crm_create_deal
crm_update_deal
crm_list_deals
crm_add_activity
crm_list_activities
crm_complete_activity
crm_next_followups
crm_summary
```

The chatbot should use CRM features like this:

| Website event | CRM action |
|---|---|
| Visitor opens chat | create anonymous session activity, no CRM contact yet |
| Visitor shares email | `crm_search_contacts`, then `crm_create_contact` or `crm_update_contact` |
| Visitor asks pricing/demo/contact-sales | `crm_create_deal` |
| Visitor leaves message | `crm_add_activity` on the contact |
| Visitor asks for follow-up | `crm_add_activity` with due date |
| Sales/admin asks summary | `crm_summary`, `crm_next_followups` |

---

## 2. Recommended Architecture

```text
Website / WordPress / Next.js page
        |
        | loads one script
        v
/chatbot/widget.js  + /chatbot/widget.css
        |
        | HTTPS JSON request
        v
Chatbot API backend
        |
        | local MCP stdio or direct Python import
        v
Solo CRM MCP server / CRM core
        |
        v
SQLite CRM DB
```

Important rule: **do not call the MCP server directly from browser JavaScript.** Browser code cannot safely access local files, stdio MCP, API keys, or trusted CRM write operations. Use a backend API as the bridge.

---

## 3. Public Embed API

The final website owner should only need one script tag:

```html
<script
  async
  src="https://chat.easiio.com/widget.js"
  data-easiio-chatbot
  data-site-id="easiio-main"
  data-api-base="https://chat.easiio.com"
  data-position="bottom-right"
  data-title="Easiio Assistant"
  data-primary-color="#2563eb"
  data-launcher-style="avatar"
  data-launcher-size="small"
  data-auto-open="false"
  data-greeting="Hi, I can help with AI automation or book a demo.">
</script>
```

The older AI Chat Agent implementation used this two-script pattern:

```html
<script src="https://chatbot.easiiodev.ai/chat.js"></script>
<script>
  window.chatlayer.set({ uuid: "BOT_UUID", language: "en" })
  window.chatlayer.show()
</script>
```

For the new CRM chatbot, keep the useful global-controller idea, but prefer auto-initialization from data attributes so WordPress/Next.js only need one script. Still expose a controller for advanced usage:

```js
window.EasiioChatbot.set({ siteId: 'easiio-main' })
window.EasiioChatbot.open()
window.EasiioChatbot.close()
window.EasiioChatbot.minimize()
window.EasiioChatbot.show()
```

The widget should render:

- Floating button/capsule in bottom-right corner.
- Optional avatar launcher inspired by the old `useAvatarAsFloatingTool` mode.
- Red unread dot for initial greeting or unread bot reply.
- Popup chat dialog when clicked.
- Header with avatar, bot title, minimize, and close controls.
- Welcome message and optional proactive greeting bubble.
- Message list and input box.
- Quick action buttons: `Book demo`, `Pricing`, `Contact sales`, `Email`, `Phone`.
- Optional lead form fields: name, email, company, phone, message.
- Consent/notice text.
- Hidden page context: URL, title, referrer, UTM parameters.
- Mobile behavior: no auto-open by default; panel becomes a bottom-sheet style dialog.

---

## 3A. UI Lessons from Existing AI Chat Agent

I inspected the closest existing earlier implementation found under:

```text
/mnt/f/ai_chat_agent3/ai_chat_agent3/chat-frontend/chatgpt-webapp-devai/dist/chat.js
/mnt/f/ai_chat_agent3/ai_chat_agent3/backend/easiio-chatgpt-devai/src/models/Sfbot.ts
```

The exact `ai_chat_agent2` folder was not found, but this codebase contains the browser chatbot widget behavior the user described.

Reusable UI/features from that implementation:

| Existing feature | New CRM chatbot plan |
|---|---|
| `window.chatlayer` global object | `window.EasiioChatbot` controller |
| `set/show/open/min/max/close` methods | `set/show/open/minimize/close`; defer maximize |
| Fixed floating `.sfchat-capsule` | Floating launcher/capsule |
| Red unread badge | Keep unread dot for proactive greeting |
| Pulse animation around chat button | Keep subtle pulse animation, configurable |
| Optional email/phone/QR buttons | Keep email/phone quick actions; QR later |
| Avatar-as-launcher mode | Support `launcherStyle: avatar` |
| `iconSize` small/medium/large | Support `launcherSize` small/medium/large |
| Greeting bubble animation | Add simple proactive greeting bubble in v1; rotating messages in v2 |
| Popup shell with header + iframe | Build direct DOM panel first; iframe mode optional later |
| Auto popup with delay, disabled on mobile | Add `autoOpen` and `autoOpenDelaySeconds`; disabled on mobile by default |
| Page ignore list | Add `includePaths` / `excludePaths` |
| Backend settings by UUID | Add public widget config by `site_id` or `bot_id` |

Do **not** copy these parts directly:

- Hard-coded URLs like `https://chatbot.easiiodev.ai` or `http://localhost:7010/api`.
- Global helper functions such as `navToChatFloatPage`; keep globals under `window.EasiioChatbot` only.
- API tokens or request secrets in browser config.
- Always-auto-open behavior on mobile.
- A mandatory iframe architecture unless isolation becomes necessary.

Detailed notes saved separately:

```text
/home/jianl/.hermes/tools/website_chatbot/AI_CHAT_AGENT_UI_NOTES.md
```

---

## 4. Backend API Contract

Create a small API service with these endpoints:

### `POST /api/chat/session`

Creates or returns a visitor session.

Request:

```json
{
  "site_id": "easiio-main",
  "page_url": "https://www.easiio.com/pricing",
  "page_title": "Pricing",
  "referrer": "https://google.com",
  "utm": {
    "source": "google",
    "campaign": "ai-agents"
  }
}
```

Response:

```json
{
  "session_id": "chat_01HX...",
  "welcome_message": "Hi, I’m the Easiio assistant. I can answer questions or help you book a demo."
}
```

### `POST /api/chat/message`

Handles a visitor message and optionally writes CRM records.

Request:

```json
{
  "session_id": "chat_01HX...",
  "site_id": "easiio-main",
  "message": "Can I book a demo? My email is jian@example.com",
  "visitor": {
    "name": "Jian",
    "email": "jian@example.com",
    "company": "Easiio"
  },
  "page_context": {
    "url": "https://www.easiio.com/ai-agent-service",
    "title": "AI Agent Service"
  }
}
```

Response:

```json
{
  "reply": "Absolutely — I can help with that. I saved your request and someone from Easiio can follow up.",
  "lead_captured": true,
  "crm_contact_id": 123,
  "crm_deal_id": 456,
  "suggested_actions": ["book_demo", "send_followup"]
}
```

### `POST /api/chat/lead`

Explicit lead capture endpoint for form submit.

Request:

```json
{
  "session_id": "chat_01HX...",
  "name": "Jian",
  "email": "jian@example.com",
  "company": "Easiio",
  "phone": "+1...",
  "message": "Interested in AI automation for my company",
  "page_url": "https://www.easiio.com/"
}
```

Response:

```json
{
  "ok": true,
  "contact_id": 123,
  "deal_id": 456
}
```

---

## 5. Chatbot Behavior Policy

The chatbot should be simple and business-focused first:

1. Greet the visitor.
2. Answer common questions from a configured FAQ/knowledge base.
3. Ask one clarifying question when needed.
4. Capture email when the user asks for pricing, demo, consultation, proposal, support, or human follow-up.
5. Create/update CRM contact when email is known.
6. Create a deal when intent is sales-related.
7. Add an activity for every useful conversation summary.
8. Never expose internal CRM IDs, database paths, logs, prompts, or API keys to the visitor.
9. If unsure, offer to have a human follow up.

Lead scoring suggestion:

| Signal | Score |
|---|---:|
| Provided email | +20 |
| Provided company | +10 |
| Asked for demo | +30 |
| Asked pricing | +20 |
| Visited pricing/contact page | +10 |
| Enterprise keywords | +20 |
| Spam/toxic message | -50 |

Deal stages:

```text
new_lead -> qualified -> demo_requested -> proposal -> won/lost
```

---

## 6. File Layout

Recommended new tool folder:

```text
/home/jianl/.hermes/tools/website_chatbot/
  README.md
  CHATBOT_CRM_IMPLEMENTATION_PLAN.md
  AI_CHAT_AGENT_UI_NOTES.md
  widget/
    widget.js
    widget.css
    demo.html
  server/
    app.py
    crm_bridge.py
    config.py
    requirements.txt
    tests/
      test_lead_capture.py
      test_chat_api.py
  wordpress-plugin/
    easiio-chatbot/
      easiio-chatbot.php
      readme.txt
  nextjs/
    EasiioChatbotScript.tsx
    route-example.ts
```

---

## 7. Implementation Tasks

### Task 1: Create tool skeleton

**Objective:** Create the website chatbot folder and basic files.

**Files:**

- Create: `/home/jianl/.hermes/tools/website_chatbot/README.md`
- Create: `/home/jianl/.hermes/tools/website_chatbot/widget/widget.js`
- Create: `/home/jianl/.hermes/tools/website_chatbot/widget/widget.css`
- Create: `/home/jianl/.hermes/tools/website_chatbot/widget/demo.html`

**Step 1:** Create README with architecture and local run instructions.

**Step 2:** Create empty widget JS/CSS files.

**Step 3:** Create `demo.html` that loads local `widget.js`.

**Verification:** Open `demo.html` in browser or serve with:

```bash
python3 -m http.server 8088 -d /home/jianl/.hermes/tools/website_chatbot/widget
```

Expected: a page loads without JavaScript errors.

---

### Task 2: Build vanilla JS popup widget

**Objective:** Add the floating chat button and popup panel.

**File:**

- Modify: `/home/jianl/.hermes/tools/website_chatbot/widget/widget.js`
- Modify: `/home/jianl/.hermes/tools/website_chatbot/widget/widget.css`

**Widget features inspired by existing AI Chat Agent:**

- Inject CSS if not already loaded.
- Create launcher: `#easiio-chatbot-launcher`.
- Create optional capsule wrapper: `#easiio-chatbot-capsule`.
- Create panel: `#easiio-chatbot-panel`.
- Add red unread dot: `#easiio-chatbot-unread`.
- Add subtle pulse animation on first page load.
- Support launcher styles: `bubble`, `avatar`.
- Support launcher sizes: `small`, `medium`, `large`.
- Support quick actions: chat, email, phone; defer QR until v2.
- Support proactive greeting bubble beside launcher.
- Toggle panel on launcher click.
- Hide launcher/capsule when panel is open; restore on minimize/close.
- Render messages in a scrollable area.
- Handle Enter key submit.
- Read config from script data attributes.
- Expose `window.EasiioChatbot` with `set`, `open`, `close`, `minimize`, `show`.
- Prevent duplicate widgets if script loads twice.

**Minimal config parser:**

```js
function getConfig() {
  const script = document.querySelector('script[data-easiio-chatbot]');
  return {
    apiBase: script?.dataset.apiBase || 'http://localhost:8099',
    siteId: script?.dataset.siteId || 'default',
    title: script?.dataset.title || 'Easiio Assistant',
    primaryColor: script?.dataset.primaryColor || '#2563eb',
    position: script?.dataset.position || 'bottom-right',
    launcherStyle: script?.dataset.launcherStyle || 'bubble',
    launcherSize: script?.dataset.launcherSize || 'small',
    avatarUrl: script?.dataset.avatarUrl || '',
    greeting: script?.dataset.greeting || 'Hi, I can help with AI automation or book a demo.',
    autoOpen: script?.dataset.autoOpen === 'true',
    autoOpenDelaySeconds: Number(script?.dataset.autoOpenDelaySeconds || 0),
    email: script?.dataset.email || '',
    phone: script?.dataset.phone || '',
    excludePaths: (script?.dataset.excludePaths || '').split(',').map(s => s.trim()).filter(Boolean)
  };
}
```

**Verification:**

- Launcher appears bottom-right.
- Red unread dot appears for initial greeting.
- Greeting bubble can appear without opening the panel.
- Clicking launcher opens popup and hides launcher.
- Minimize/close restores launcher.
- User can type a message.
- Email/phone quick actions render only when configured.
- On mobile, panel uses bottom-sheet sizing and does not auto-open.
- No duplicate widgets if script loads twice.

---

### Task 3: Add local mock backend mode

**Objective:** Let widget work before backend exists.

**File:**

- Modify: `/home/jianl/.hermes/tools/website_chatbot/widget/widget.js`

**Behavior:**

If `apiBase` is `mock`, return a local fake reply:

```js
if (config.apiBase === 'mock') {
  return {
    reply: 'Thanks — this is mock mode. The CRM API is not connected yet.',
    lead_captured: false
  };
}
```

**Verification:**

Use this script tag in `demo.html`:

```html
<script async src="./widget.js" data-easiio-chatbot data-api-base="mock"></script>
```

Expected: messages receive mock replies.

---

### Task 4: Create backend API skeleton

**Objective:** Create local chatbot backend service.

**Files:**

- Create: `/home/jianl/.hermes/tools/website_chatbot/server/app.py`
- Create: `/home/jianl/.hermes/tools/website_chatbot/server/config.py`
- Create: `/home/jianl/.hermes/tools/website_chatbot/server/requirements.txt`

**Recommended Python dependencies:**

```text
fastapi
uvicorn
pydantic
```

If system lacks pip, create a venv manually only after confirming package installation is possible. If dependency installation is not allowed, use Python stdlib `http.server` as a fallback.

**Endpoints:**

- `GET /health`
- `POST /api/chat/session`
- `POST /api/chat/message`
- `POST /api/chat/lead`
- `GET /widget.js` serve static widget
- `GET /widget.css` serve static CSS

**Verification:**

```bash
curl -s http://localhost:8099/health
```

Expected:

```json
{"ok":true}
```

---

### Task 5: Add CRM bridge

**Objective:** Connect backend to the existing Solo CRM implementation.

**Files:**

- Create: `/home/jianl/.hermes/tools/website_chatbot/server/crm_bridge.py`
- Test: `/home/jianl/.hermes/tools/website_chatbot/server/tests/test_lead_capture.py`

**Preferred implementation:** import `crm_core.py` directly because backend runs on same machine.

```python
import sys
from pathlib import Path

SOLO_CRM_DIR = Path('/home/jianl/.hermes/tools/solo_crm')
sys.path.insert(0, str(SOLO_CRM_DIR))

from crm_core import SoloCRM

crm = SoloCRM('/home/jianl/.hermes/tools/solo_crm/solo_crm.db')
```

**Bridge functions:**

```python
def upsert_contact_from_lead(name, email, company=None, phone=None, source='website_chatbot'):
    # search by email
    # create or update contact
    # create company if company exists
    # add activity noting source/page/session
    pass


def create_sales_deal(contact_id, company_id=None, title='Website chatbot lead', value=None):
    pass


def add_conversation_activity(contact_id, summary, due_date=None):
    pass
```

**Verification:**

- Submit test lead.
- Confirm CRM summary contact count increases.
- Confirm activity created.

---

### Task 6: Implement lead extraction logic

**Objective:** Extract email/name/company/intent from messages before using a full LLM.

**File:**

- Create: `/home/jianl/.hermes/tools/website_chatbot/server/lead_extract.py`
- Test: `/home/jianl/.hermes/tools/website_chatbot/server/tests/test_lead_extract.py`

**Minimum extraction:**

- Email regex.
- Phone regex.
- Sales intent keywords: `demo`, `pricing`, `quote`, `proposal`, `consultation`, `talk to sales`, `agent`, `automation`.
- Support intent keywords: `support`, `help`, `bug`, `issue`.

**Verification examples:**

```python
def test_extract_email_and_demo_intent():
    result = extract_lead('Can I book a demo? My email is jian@example.com')
    assert result['email'] == 'jian@example.com'
    assert result['intent'] == 'demo'
```

---

### Task 7: Implement chat message endpoint

**Objective:** Accept messages, return replies, and write to CRM when appropriate.

**File:**

- Modify: `/home/jianl/.hermes/tools/website_chatbot/server/app.py`

**Rules:**

- Always validate `site_id`, `session_id`, `message`.
- If email found, upsert CRM contact.
- If sales intent found, create deal if one does not already exist for this session/contact.
- Add activity summary.
- Return a concise human reply.

**Example reply templates:**

```python
if lead.email and lead.intent == 'demo':
    reply = 'Thanks — I saved your demo request. Someone from Easiio can follow up with you soon.'
elif lead.intent == 'pricing':
    reply = 'I can help with pricing. Could you share your work email so our team can follow up with the right package?'
else:
    reply = 'Thanks. I can help with Easiio services, AI agents, automation, and demo requests. What would you like to do?'
```

---

### Task 8: Add CORS, rate limits, and spam protection

**Objective:** Protect the chatbot endpoint before public deployment.

**Files:**

- Modify: `/home/jianl/.hermes/tools/website_chatbot/server/app.py`
- Create: `/home/jianl/.hermes/tools/website_chatbot/server/security.py`

**Security requirements:**

- CORS allowlist for `https://www.easiio.com`, `https://easiio.com`, and local dev.
- Max message length, e.g. 2000 characters.
- Rate limit by IP/session.
- Honeypot field for bot form submissions.
- Never include internal stack traces in API response.
- Store only useful lead info; avoid sensitive data.

---

### Task 9: Build WordPress footer plugin

**Objective:** Add a plugin that injects the chatbot script in WordPress footer.

**Files:**

- Create: `/home/jianl/.hermes/tools/website_chatbot/wordpress-plugin/easiio-chatbot/easiio-chatbot.php`
- Create: `/home/jianl/.hermes/tools/website_chatbot/wordpress-plugin/easiio-chatbot/readme.txt`

**Plugin PHP:**

```php
<?php
/**
 * Plugin Name: Easiio Chatbot
 * Description: Adds the Easiio chatbot popup widget to the footer.
 * Version: 0.1.0
 * Author: Easiio
 */

if (!defined('ABSPATH')) {
    exit;
}

function easiio_chatbot_footer_script() {
    $api_base = esc_url('https://chat.easiio.com');
    $widget_url = esc_url($api_base . '/widget.js');
    ?>
    <script
        async
        src="<?php echo $widget_url; ?>"
        data-easiio-chatbot
        data-site-id="easiio-main"
        data-api-base="<?php echo $api_base; ?>"
        data-position="bottom-right"
        data-title="Easiio Assistant"
        data-primary-color="#2563eb">
    </script>
    <?php
}
add_action('wp_footer', 'easiio_chatbot_footer_script', 100);
```

**Verification:**

- Install plugin ZIP in WordPress admin.
- Activate plugin.
- View page source and confirm script appears near footer.
- Open live page and confirm popup appears.

---

### Task 10: Add WordPress admin settings later

**Objective:** Make plugin configurable without editing PHP.

**Defer unless needed.** Start simple with fixed values. Add settings only after widget works.

Future settings:

- Enable/disable chatbot.
- API base URL.
- Site ID.
- Title.
- Brand color.
- Page include/exclude rules.

---

### Task 11: Add Next.js integration component

**Objective:** Let Next.js websites load the same widget.

**File:**

- Create: `/home/jianl/.hermes/tools/website_chatbot/nextjs/EasiioChatbotScript.tsx`

**Component:**

```tsx
import Script from 'next/script';

export function EasiioChatbotScript() {
  return (
    <Script
      id="easiio-chatbot"
      src="https://chat.easiio.com/widget.js"
      strategy="afterInteractive"
      data-easiio-chatbot
      data-site-id="easiio-main"
      data-api-base="https://chat.easiio.com"
      data-position="bottom-right"
      data-title="Easiio Assistant"
      data-primary-color="#2563eb"
    />
  );
}
```

**Usage in App Router:**

```tsx
// app/layout.tsx
import { EasiioChatbotScript } from '@/components/EasiioChatbotScript';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
        <EasiioChatbotScript />
      </body>
    </html>
  );
}
```

---

### Task 12: Add deployment plan

**Objective:** Decide where the backend and static widget will run.

**Options:**

1. **Same VPS as WordPress**
   - Pros: simple, close to site.
   - Cons: must secure Python/Node process.

2. **Separate subdomain `chat.easiio.com`**
   - Pros: clean public embed URL, works for WP and Next.js.
   - Cons: DNS/reverse proxy setup required.

3. **Next.js API routes**
   - Pros: good if the website is Next.js.
   - Cons: cannot easily run local SQLite CRM unless deployed on same server or replaced with hosted DB/API.

Recommended first deployment:

```text
chat.easiio.com -> reverse proxy -> local chatbot API on port 8099
```

---

### Task 13: Add logs and admin review

**Objective:** Let the business owner review leads and conversation summaries.

**Minimum implementation:** Store conversation summary as CRM activity only.

Future improvement:

- Store full chat transcript in separate SQLite table.
- Add `crm_list_chat_sessions` tool.
- Add daily summary automation.

---

### Task 14: Production verification checklist

Before enabling on the live site:

- [ ] Widget loads on staging page.
- [ ] Widget does not block page rendering.
- [ ] Widget opens/closes on desktop and mobile.
- [ ] Form/message submission works.
- [ ] Bad API/network failure shows friendly error.
- [ ] Email lead creates/updates CRM contact.
- [ ] Demo/pricing intent creates CRM deal.
- [ ] Conversation summary creates CRM activity.
- [ ] CORS only allows expected domains.
- [ ] Rate limiting enabled.
- [ ] No secrets in browser JS.
- [ ] WordPress homepage still returns 200.
- [ ] Blog/list/contact pages still return 200.

---

## 8. Recommended Build Order

Build in this order:

1. Widget UI in mock mode.
2. Local backend `/health` and `/api/chat/message`.
3. CRM bridge using direct `crm_core.py` import.
4. Lead extraction + contact/deal/activity writes.
5. WordPress plugin footer injector.
6. Next.js component.
7. Public deployment on `chat.easiio.com`.
8. LLM-powered answers/FAQ retrieval.
9. Admin settings and analytics.

Do **not** start with a complex LLM chatbot. Start with reliable lead capture + CRM writing first, then add smarter answers.

---

## 9. Open Decisions

These need product/deployment choices before production:

1. Where will `chat.easiio.com` run?
2. Which LLM provider will power answers, if any?
3. Should full transcripts be stored, or only summaries?
4. Should the bot show on every page or only selected pages?
5. What privacy/consent text should appear in the widget?
6. Should the bot offer calendar booking directly?

---

## 10. Success Criteria

The first production-ready version is successful when:

1. Adding one script tag shows chatbot popup on WordPress and Next.js pages.
2. Visitor can send a message and receive a reply.
3. Visitor email creates or updates a Solo CRM contact.
4. Demo/pricing request creates a CRM deal.
5. Conversation summary becomes a CRM activity.
6. The website still loads normally if the chatbot API is down.
7. No API key, CRM path, or internal implementation detail is exposed to the browser.
