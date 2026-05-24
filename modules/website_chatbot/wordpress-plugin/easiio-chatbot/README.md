# Easiio Chatbot WordPress Plugin

This small WordPress plugin injects the Easiio chatbot widget into the site footer using `wp_footer`.

## Current status

Local package implementation only. Do **not** activate on the production site until the chatbot backend is deployed at the configured public URL and reviewed.

Default backend/widget URL:

```text
https://chat.easiio.com/widget.js
```

Default script configuration:

```text
data-site-id="easiio-main"
data-api-base="https://chat.easiio.com"
data-position="bottom-right"
data-title="Easiio Assistant"
data-primary-color="#2563eb"
data-launcher-style="bubble"
data-launcher-size="small"
data-auto-open="false"
data-rag-admin="false"
```

## Install by WordPress admin upload

1. Build or locate the ZIP:

   ```text
   /home/jianl/.hermes/tools/website_chatbot/dist/easiio-chatbot-wordpress-plugin.zip
   ```

2. In WordPress admin, go to:

   ```text
   Plugins → Add New → Upload Plugin
   ```

3. Upload `easiio-chatbot-wordpress-plugin.zip`.
4. Activate only after confirming `https://chat.easiio.com/widget.js` and backend API are live.
5. View page source and confirm the script appears near the footer.
6. Check homepage and important pages still return `200 OK`.

## Safety notes

- The plugin uses fixed reviewed values first; no admin settings page yet.
- `data-auto-open` is `false` by default.
- `data-rag-admin` is `false` by default; only enable it on protected/admin-only pages because it exposes the chatbot knowledge editor for that `site_id`.
- Sensitive paths are excluded:
  - `/wp-admin`
  - `/wp-login.php`
  - `/cart`
  - `/checkout`
  - `/my-account`
- The browser widget only talks to the HTTPS backend API. It does not expose CRM paths, MCP details, database files, or secrets.

## Editing configuration

For now, edit constants inside `easiio-chatbot.php` before zipping. Later, add a WordPress settings page after the live backend and widget flow are stable.
