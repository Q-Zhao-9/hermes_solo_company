# AI Solo Owner Mobile App Implementation Plan

> **For Hermes:** Use the mobile-app-agency-orchestrator flow, route to Expo/React Native, and implement the MVP in thin vertical slices.

**Goal:** Build a cross-platform mobile app for AI Solo Company owners to chat with their Hermes bot, browse available skills, and monitor their website from one mobile dashboard.

**Architecture:** Use Expo + React Native + TypeScript with Expo Router. Start with a clean owner-console MVP using mocked/local data plus a service layer prepared for future live Hermes/website API integration. Prioritize one clear happy path: open app → review owner dashboard → chat with Hermes → inspect skills → view website health/metrics.

**Tech Stack:** Expo, React Native, TypeScript, Expo Router, React Context/light local state, mock service layer, tokenized theme system.

---

## Product intent

### App concept
- **Name:** AI Solo Owner
- **Users:** AI Solo Company owners/operators
- **Core promise:** Manage Hermes, inspect skills, and watch website health from mobile without opening the full desktop control stack.

### Why Expo / React Native
- Cross-platform iPhone + Android is required.
- The app is an owner MVP/internal operator tool.
- The UI is standard dashboard/chat/list/detail mobile work.
- Fast iteration matters more than deep native-only APIs.
- Expo is the fastest path to a working demo.

### MVP scope
#### Must-have
- Owner dashboard/home screen
- Hermes chat screen with conversation history UI
- Skills library screen with categories and skill detail drawer/page
- Website monitor screen with health cards, uptime snapshot, and alerts list
- Shared theme + reusable cards/buttons/section containers
- Mock service layer prepared for live Hermes/site endpoints later

#### Deferred
- Real auth
- Push notifications
- Live websocket streaming chat
- Skill execution from mobile
- Multi-website management
- Real analytics charts from production data

## Screen map
1. **Home Dashboard** — owner summary, quick actions, latest status
2. **Hermes Chat** — chat composer, recent conversation bubbles, starter prompts
3. **Skills** — categories, searchable skill cards, detail view
4. **Website Monitor** — site health, metrics, incidents/alerts, recommended actions
5. **Settings** — connection targets, owner profile, environment notes

## Data model
- `OwnerProfile`: id, name, role, companyName
- `BotStatus`: mode, lastSyncAt, pendingTasks, activeSkillsCount
- `SkillSummary`: id, name, category, shortDescription, tags
- `WebsiteMetric`: id, label, value, trend, status
- `WebsiteAlert`: id, title, severity, createdAt, detail
- `ChatMessage`: id, role, text, createdAt

## Delivery phases
### Phase 1 — Scaffold
- Create Expo Router app under `mobile-apps/ai-solo-owner-app`
- Establish theme tokens, layout shell, bottom tabs
- Add reusable UI primitives

### Phase 2 — Primary owner flow
- Implement dashboard
- Implement Hermes chat UI
- Wire mock data services

### Phase 3 — Supporting operator flows
- Implement skills browser
- Implement website monitor screen
- Add settings screen

### Phase 4 — Polish and verification
- Empty/loading/error states
- Lint/typecheck/export verification
- README handoff notes

## Exact workspace target
- Project root: `/home/jianl/github-work/hermes_solo_company/mobile-apps/ai-solo-owner-app`

## Immediate implementation order
1. Scaffold Expo app
2. Replace starter routes with owner tabs
3. Create theme tokens and reusable shell/card/button primitives
4. Add mock domain data
5. Build Dashboard screen
6. Build Chat screen
7. Build Skills screen
8. Build Website Monitor screen
9. Add Settings screen
10. Verify lint + web export
