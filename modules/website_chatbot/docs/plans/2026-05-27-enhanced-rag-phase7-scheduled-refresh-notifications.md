# Enhanced RAG Phase 7 — Scheduled Refresh + Notifications

## Goal

Phase 7 adds an operations layer on top of the Phase 6 review-first RAG workflow.

The intended workflow is:

```text
Configure schedule per site_id
→ periodically check Docs/Wiki/WordPress/upload sources
→ preview source changes
→ create admin notifications when changes are found
→ optionally auto-sync approved sources
→ keep rollback metadata from Phase 6
```

This remains local-first and review-safe. It does not require a long-running scheduler inside the backend; an external cron/Hermes scheduled job/systemd timer can call the run endpoint.

## Files changed

```text
/home/jianl/.hermes/tools/website_chatbot/backend/app.py
/home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.js
/home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.css
/home/jianl/.hermes/tools/website_chatbot/tests/test_backend.py
/home/jianl/.hermes/tools/website_chatbot/tests/admin_customizer_static.test.js
```

The reusable admin customizer was also copied to the AI Solo local site:

```text
/mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.js
/mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.css
```

## New data stores

```text
EASIIO_CHATBOT_RAG_REFRESH_SCHEDULE
```

Default:

```text
/home/jianl/.hermes/tools/website_chatbot/data/rag_refresh_schedule.json
```

```text
EASIIO_CHATBOT_RAG_NOTIFICATIONS
```

Default:

```text
/home/jianl/.hermes/tools/website_chatbot/data/rag_notifications.json
```

Notification API responses never expose raw notification recipient email lists or email-provider secrets.

## New backend endpoints

### GET /api/rag/refresh-schedule

Fetch one site's schedule.

```text
GET /api/rag/refresh-schedule?site_id=ai-solo-company-class
```

### POST /api/rag/refresh-schedule

Create/update one site's refresh schedule.

Example:

```json
{
  "site_id": "ai-solo-company-class",
  "schedule": {
    "enabled": true,
    "sources": ["docs", "wiki", "wordpress", "upload"],
    "interval_minutes": 1440,
    "stale_after_minutes": 2880,
    "notify_on_changes": true,
    "notify_recipients": ["owner@example.com"],
    "auto_sync": false
  }
}
```

### GET /api/rag/refresh-due

List schedules due to run based on `interval_minutes` and `last_checked_at`.

### POST /api/rag/run-scheduled-refresh

Run scheduled refresh checks. This endpoint can be called by Hermes cron/system cron.

Dry-run example:

```json
{
  "site_id": "ai-solo-company-class",
  "dry_run": true
}
```

Behavior:

- builds a Phase 6 review summary
- action is `preview_only` when changes are found but `auto_sync` is false or dry-run is true
- action is `synced` when `auto_sync` is true and dry-run is false
- creates a notification if `notify_on_changes` is true and the review summary has new/changed/deleted items
- preserves rollback ID when auto-sync runs

### GET /api/rag/notifications

List safe notifications for one site.

```text
GET /api/rag/notifications?site_id=ai-solo-company-class
```

### POST /api/rag/notifications/read

Mark one or all notifications read.

```json
{
  "site_id": "ai-solo-company-class",
  "mark_all": true
}
```

or:

```json
{
  "site_id": "ai-solo-company-class",
  "notification_id": "rag-note-..."
}
```

## Admin UI updates

The reusable admin customizer now includes a new section inside the RAG card:

```text
RAG schedule + notifications
```

Controls:

- enable scheduled refresh
- interval minutes
- stale alert minutes
- notification recipients
- notify when changes are found
- optional auto-sync
- save schedule
- run scheduled refresh now
- check due sites
- load notifications
- mark notifications read

## Verification

Commands run:

```bash
cd /home/jianl/.hermes/tools/website_chatbot
python3 -m py_compile backend/app.py backend/site_gateway.py
python3 tests/test_backend.py -v
node --check admin/chatbot-customizer.js
node tests/admin_customizer_static.test.js
node --check widget/widget.js
node tests/widget_static.test.js
node tests/wp_plugin_static.test.js
python3 /mnt/c/Users/jianl/solo-company-class-site/auth_download_static_test.py
node --check /mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.js
```

Runtime smoke result:

```text
easiio_rag_phase7_smoke_ok
```

Backend test total after Phase 7:

```text
Ran 40 tests
OK
```

## Suggested scheduler call

A Hermes cron/system cron job can call:

```bash
curl -sS -X POST http://127.0.0.1:8099/api/rag/run-scheduled-refresh \
  -H 'Content-Type: application/json' \
  -d '{"force": false}'
```

For a single site:

```bash
curl -sS -X POST http://127.0.0.1:8099/api/rag/run-scheduled-refresh \
  -H 'Content-Type: application/json' \
  -d '{"site_id":"ai-solo-company-class"}'
```

## Future Phase 8 ideas

- real cron helper script with lock file and retry policy
- owner digest email grouping notifications across sites
- source-specific WordPress pull schedules
- admin notification severity levels
- stale-source banners inside chatbot admin dashboard
- approval workflow before auto-sync for sensitive sources
