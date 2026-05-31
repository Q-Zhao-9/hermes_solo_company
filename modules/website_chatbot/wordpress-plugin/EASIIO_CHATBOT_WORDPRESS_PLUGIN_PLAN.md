# Easiio Chatbot WordPress Plugin Enhancement Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Turn the existing basic Easiio Chatbot WordPress footer plugin into a class-ready and production-review-ready plugin for embedding the website chatbot, connecting to RAG, and sending leads to Solo CRM through the backend API.

**Architecture:** WordPress only renders safe public widget configuration and optional admin settings UI. The browser widget calls the Easiio chatbot backend; CRM, RAG storage, LLM keys, email provider keys, and external CRM connector credentials remain server-side only.

**Tech Stack:** WordPress PHP plugin, WordPress Settings API, frontend widget script, existing Python chatbot backend, existing Solo CRM backend, Node/PHP/static tests.

---

## Current State

We already have a basic plugin:

```text
/home/jianl/.hermes/tools/website_chatbot/wordpress-plugin/easiio-chatbot/easiio-chatbot.php
/home/jianl/.hermes/tools/website_chatbot/dist/easiio-chatbot-wordpress-plugin.zip
```

Current capabilities:

- Injects chatbot script in `wp_footer`.
- Uses escaped attributes with `esc_url()` and `esc_attr()`.
- Has conservative defaults:
  - `data-auto-open="false"`
  - `data-rag-admin="false"`
  - excludes `/wp-admin,/wp-login.php,/cart,/checkout,/my-account`
- Does not expose CRM database paths, MCP internals, API keys, tokens, or webhook URLs.

Current limitation:

- Configuration is hard-coded in PHP.
- No WordPress admin settings page yet.
- No admin-side validation UI for backend health, site ID, or RAG/CRM connection.
- No shortcode/block option yet.

---

## Target User Experience

A WordPress admin should be able to:

1. Upload and activate the plugin.
2. Open **Settings → Easiio Chatbot**.
3. Enter:
   - API base URL
   - widget script URL
   - `site_id`
   - organization name
   - website name
   - title/greeting/color/position
   - safe excluded paths
   - page-view tracking on/off
   - lead form behavior on/off
4. Save settings.
5. Preview the chatbot on the public site.
6. Confirm backend health and CRM/RAG status from the plugin settings page.

Important: WordPress should not store raw LLM keys, CRM tokens, HubSpot tokens, Google Sheets webhook URLs, SMTP/Brevo keys, or MCP connection data.

---

## Phase 1 — Settings Page

### Task 1: Add plugin option defaults

**Objective:** Replace hard-coded values with sanitized WordPress options while preserving safe defaults.

**Files:**

- Modify: `/home/jianl/.hermes/tools/website_chatbot/wordpress-plugin/easiio-chatbot/easiio-chatbot.php`
- Test: `/home/jianl/.hermes/tools/website_chatbot/tests/wp_plugin_static.test.js`

**Implementation notes:**

Add a function like:

```php
function easiio_chatbot_default_options() {
    return array(
        'api_base' => 'https://chat.easiio.com',
        'widget_url' => 'https://chat.easiio.com/widget.js',
        'site_id' => 'easiio-main',
        'organization_name' => 'Easiio',
        'website_name' => get_bloginfo('name') ?: 'Easiio Website',
        'track_page_views' => 'true',
        'position' => 'bottom-right',
        'title' => 'Easiio Assistant',
        'primary_color' => '#2563eb',
        'launcher_style' => 'bubble',
        'launcher_size' => 'small',
        'auto_open' => 'false',
        'rag_admin' => 'false',
        'lead_forms_enabled' => 'false',
        'greeting' => 'Hi, I can help answer questions or book a demo.',
        'email' => '',
        'exclude_paths' => '/wp-admin,/wp-login.php,/cart,/checkout,/my-account',
        'consent_text' => 'By chatting, you agree that this website may use your message to follow up.'
    );
}
```

### Task 2: Add WordPress Settings API page

**Objective:** Add an admin settings page under **Settings → Easiio Chatbot**.

**Files:**

- Modify: `wordpress-plugin/easiio-chatbot/easiio-chatbot.php`
- Test: `tests/wp_plugin_static.test.js`

**Expected markers:**

```text
add_options_page
register_setting
sanitize_callback
easiiio/easiio settings nonce handled by WordPress Settings API
```

Use capability:

```php
manage_options
```

### Task 3: Add sanitization function

**Objective:** Ensure all plugin settings are safe before saving.

**Validation rules:**

- URLs: `esc_url_raw()`
- Text: `sanitize_text_field()`
- Multiline consent text: `sanitize_textarea_field()`
- Booleans: convert to `'true'` or `'false'`
- Color: validate hex color, fallback to default
- Excluded paths: sanitize comma-separated path strings
- Reject raw secret-looking fields; do not add settings for API keys/tokens/webhooks.

### Task 4: Render footer script from options

**Objective:** Use saved options to render public widget attributes.

**Security requirements:**

- Use `esc_url()` for URLs.
- Use `esc_attr()` for data attributes.
- Do not render settings on excluded paths.
- Keep `data-rag-admin="false"` by default.
- Keep `data-lead-forms-enabled="false"` by default.

---

## Phase 2 — Admin Health Check and Setup Guidance

### Task 5: Add backend health check button

**Objective:** Let a WordPress admin verify that the chatbot backend is reachable.

**Approach:**

- Add a settings-page button: **Check backend health**.
- Use WordPress admin AJAX or REST endpoint.
- Server-side PHP calls `${api_base}/health` with `wp_remote_get()`.
- Return sanitized status only.

**Do not:**

- Print backend secrets.
- Save response bodies that may contain sensitive data.

### Task 6: Add safe setup instructions inside plugin admin

**Objective:** Include quick steps for setting up RAG and CRM without exposing secrets.

Admin text should explain:

- `site_id` must match backend/RAG/CRM.
- RAG knowledge is managed in backend/admin tools, not public frontend.
- CRM lead capture happens through backend API.
- LLM keys and email provider keys are server-side only.

---

## Phase 3 — Shortcode and Page-Level Controls

### Task 7: Add optional shortcode

**Objective:** Allow page-specific overrides when needed.

Shortcode example:

```text
[easiio_chatbot site_id="ai-solo-demo" title="AI Solo Assistant" position="bottom-right"]
```

Rules:

- Only allow safe public options.
- No secrets.
- If shortcode is present, avoid duplicate footer injection on the same page.

### Task 8: Add page/post meta override later if needed

**Objective:** Let admins disable chatbot on specific pages without editing code.

YAGNI note: Do this only after settings page and shortcode are stable.

---

## Phase 4 — RAG and CRM Admin Integration Planning

### Task 9: Plan protected admin knowledge editor

**Objective:** Decide whether to embed the existing RAG admin customizer in WordPress admin.

Options:

1. Keep RAG admin outside WordPress in Easiio backend console.
2. Add WordPress admin page that embeds the admin customizer.
3. Add WordPress REST proxy routes for admin-only RAG editing.

Recommended first choice:

- Keep RAG editing in protected Easiio backend console for now.
- WordPress plugin should remain simple public widget + settings.

### Task 10: Plan CRM status display

**Objective:** Show admin-safe CRM status without exposing database paths or MCP internals.

Possible fields:

- backend reachable yes/no
- site_id configured yes/no
- last successful lead test timestamp if backend exposes it safely
- external CRM sync status if backend exposes admin-safe endpoint

---

## Phase 5 — Packaging and Tests

### Task 11: Expand static tests

**Objective:** Protect security and WordPress markers.

Test file:

```text
/home/jianl/.hermes/tools/website_chatbot/tests/wp_plugin_static.test.js
```

Assertions should include:

- `Plugin Name: Easiio Chatbot`
- `add_action('wp_footer'`
- `add_options_page`
- `register_setting`
- `manage_options`
- `esc_url`
- `esc_attr`
- `sanitize_text_field`
- `esc_url_raw`
- `data-rag-admin`
- `data-lead-forms-enabled`
- no raw `api_key`, `access_token`, `webhook_url`, `password` settings

### Task 12: Package plugin ZIP

**Objective:** Rebuild the uploadable WordPress ZIP.

Expected output:

```text
/home/jianl/.hermes/tools/website_chatbot/dist/easiio-chatbot-wordpress-plugin.zip
```

Suggested command:

```bash
cd /home/jianl/.hermes/tools/website_chatbot/wordpress-plugin
zip -r ../dist/easiio-chatbot-wordpress-plugin.zip easiio-chatbot -x '*.DS_Store' '__MACOSX/*'
```

### Task 13: Final verification

Run:

```bash
node /home/jianl/.hermes/tools/website_chatbot/tests/wp_plugin_static.test.js
php -l /home/jianl/.hermes/tools/website_chatbot/wordpress-plugin/easiio-chatbot/easiio-chatbot.php || true
python3 -m py_compile /home/jianl/.hermes/tools/website_chatbot/backend/app.py
```

If PHP is not installed in WSL, document that PHP lint was skipped.

---

## Acceptance Criteria

The improved plugin is ready when:

- WordPress admin can configure public widget options.
- Public pages render the chatbot script with escaped safe attributes.
- Excluded paths do not render chatbot.
- Default `rag_admin` is false.
- Default auto-open is false.
- No secrets are stored or rendered by the plugin.
- Backend health check returns sanitized status.
- Plugin ZIP can be uploaded through WordPress admin.
- Static tests pass.

---

## Production Safety Rules

1. The plugin must not contain LLM API keys.
2. The plugin must not contain CRM tokens, webhook URLs, SMTP passwords, or Brevo keys.
3. The plugin must not expose local CRM SQLite paths or MCP details.
4. RAG admin controls must remain admin-only.
5. CRM connector configuration must remain server-side.
6. External CRM sync must remain optional and non-blocking.
7. Review on staging before activating on production.
