# AI Solo Owner App

Mobile owner console for AI Solo Company.

## Current phase
This build now includes the first **real integration slice**:
- live public gateway health check
- live public RAG source coverage check
- live Hermes chat session + message calls
- curated owner skill catalog aligned to the Hermes skill system
- automatic fallback to local mock data when the live gateway is unavailable

## Current app behavior
### Home
- owner snapshot
- quick actions
- live/fallback status summary
- latest monitor metrics and alerts

### Hermes chat
- creates a real chat session through the production AI Solo gateway
- sends real `/api/chat/message` requests
- falls back to local owner-summary replies if the live path fails

### Skills
- uses a curated owner skill pack based on the Hermes skill catalog
- ready for a future authenticated live skill-feed slice

### Website monitor
- reads live `/health`
- reads live `/api/rag/sources?site_id=...`
- converts that data into owner-facing metrics and alerts

### Settings
- edit gateway base URL
- edit site ID / site name
- reset to the production AI Solo target
- trigger a live monitor refresh

## Stack
- Expo
- React Native
- TypeScript
- Expo Router

## Run
```bash
npm install
npx tsc --noEmit
npx expo export --platform web
npm run web
```

## Default live target
- Base URL: `https://hermesproxy.easiiodev.ai/p/VaYZmN7v5naw-ai-solo`
- Site ID: `ai-solo-company-class`

## Known limitation in this phase
The existing gateway endpoints for admin skill files and CRM owner data are currently cookie-auth web flows, so this mobile slice does **not** yet pull the admin-only live skill list or CRM dashboard directly.

## Best next phase
1. add a mobile-safe auth/API path for owner/admin data
2. replace curated skill cards with a real authenticated skill feed
3. expose owner CRM / lead / deal summary endpoints for the dashboard
4. optionally persist app settings locally between launches
