# Enhanced RAG Phase 6 — Review Queue, Stale Detection, Diff Preview, and Rollback

Date: 2026-05-27

## Purpose

Phase 6 adds a review-first operations layer on top of the Phase 3–5 multi-source RAG pipeline.

Before this phase, admins could stage WordPress/upload sources and sync selected sources into chatbot RAG. Phase 6 adds:

- preview before sync
- review queue counts
- changed/new/unchanged/deleted-upstream detection
- diff previews for changed items
- source freshness summary in `/api/rag/sources`
- rollback snapshots for source sync operations
- admin customizer controls for preview, review, and rollback

The design remains site-scoped and secret-safe. It does not expose credentials, env values, WordPress auth values, or raw approver emails.

## Backend endpoints

### `POST /api/rag/sync-preview`

Preview selected source changes without writing to the RAG store.

Example:

```json
{
  "site_id": "ai-solo-company-class",
  "sources": ["docs", "wiki", "wordpress", "upload"]
}
```

Returns:

```json
{
  "ok": true,
  "site_id": "ai-solo-company-class",
  "sources": ["docs", "wiki", "wordpress", "upload"],
  "summary": {
    "new": 1,
    "changed": 2,
    "unchanged": 5,
    "deleted_upstream": 1,
    "total": 9
  },
  "items": [
    {
      "content_id": "wordpress:ai-solo-company-class:homepage",
      "title": "Homepage",
      "source": "wordpress",
      "review_status": "changed",
      "diff_preview": "--- current\n+++ upstream\n...",
      "text_preview": "..."
    }
  ],
  "last_sync": {}
}
```

### `GET /api/rag/review?site_id=...`

Loads the current review queue for all sources:

```text
docs,wiki,wordpress,upload
```

Returns the same review statuses plus source counts and latest sync metadata.

### `POST /api/rag/rollback`

Restores the RAG content store to the snapshot that existed before a sync run.

Example:

```json
{
  "site_id": "ai-solo-company-class",
  "rollback_id": "rag-sync-...",
  "confirm_rollback": true,
  "approved_by": "admin_customizer"
}
```

Safety rules:

- Requires `confirm_rollback: true`.
- Rollback is scoped to one `site_id`.
- Uses the previous sync snapshot stored in the sync log.
- Does not expose raw approver contact details.

### Updated `POST /api/rag/sync-sources`

Sync now records a rollback snapshot and returns a public `rollback_id` in the summary:

```json
{
  "summary": {
    "rollback_id": "rag-sync-...",
    "sources": ["wordpress"],
    "source_counts": {"wordpress": 3},
    "review_summary": {"new": 1, "changed": 2, "unchanged": 0, "deleted_upstream": 0, "total": 3},
    "synced_items": 3,
    "kept_manual_items": 4
  }
}
```

Snapshots are stored in:

```text
EASIIO_CHATBOT_RAG_SYNC_LOG
```

Default:

```text
/home/jianl/.hermes/tools/website_chatbot/data/rag_sync_log.json
```

### Updated `GET /api/rag/sources`

Now includes `review_summary` so an admin console can show freshness/staleness counts without doing a destructive sync.

## Review statuses

- `new` — upstream source item does not exist in current synced RAG content.
- `changed` — same `content_id`, but title/url/content fingerprint changed.
- `unchanged` — current synced item matches upstream source item.
- `deleted_upstream` — item exists in synced RAG content but no longer exists in upstream selected source.

## Admin customizer UI

Updated:

```text
/home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.js
/home/jianl/.hermes/tools/website_chatbot/admin/chatbot-customizer.css
```

Added controls in the **RAG source sync** card:

- `Preview changes`
- `Load review queue`
- `Rollback last sync`
- `RAG review queue` panel
- diff preview rendering for changed items
- status badges for `new`, `changed`, `unchanged`, and `deleted_upstream`

The deployed AI Solo admin customizer copy was also updated:

```text
/mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.js
/mnt/c/Users/jianl/solo-company-class-site/chatbot-admin/chatbot-customizer.css
```

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

Runtime smoke:

```text
easiio_rag_phase6_smoke_ok
```

## Notes

- Rollback restores the whole `site_id` RAG content snapshot from before the sync operation, including manual items that existed at that time.
- Manual items are preserved during normal sync.
- The admin UI still requires a protected/admin-only console because it manages RAG operations.
- WordPress credentials and env values remain server-side only.
