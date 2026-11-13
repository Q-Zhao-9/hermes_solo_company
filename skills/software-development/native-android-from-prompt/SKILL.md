---
name: native-android-from-prompt
description: Turn a natural-language product prompt and optional UI reference images into a reviewable native Android app MVP using Kotlin and Jetpack Compose-first workflows, with escalation guidance for deeper Android platform integrations.
license: Proprietary. LICENSE.txt has complete terms
---

# Native Android From Prompt

## When to use
Use this skill when the user wants to create, scaffold, plan, redesign, or iteratively build a **native Android app** from:
- a plain-English prompt
- a rough feature list or product spec
- screenshots, mockups, wireframes, or UI images
- a combined product + design brief

Typical triggers:
- "Build an Android app from this prompt"
- "Make this app natively for Android"
- "Use these screenshots and create a Jetpack Compose app"
- "I need Android-specific hardware/background behavior"
- "Create a Play Store-ready Android MVP"

## Default strategy
Unless the prompt clearly requires legacy View-based work, default to:
- **Kotlin**
- **Jetpack Compose**
- **Android Studio / Gradle project scaffold**
- **Android-native patterns** for navigation, permissions, services, and integrations

Why:
- Fastest modern path for native Android apps
- Best alignment with current Android UI architecture
- Strong fit for image-driven recreation of polished mobile UI
- Good foundation for Android-specific background or hardware features

## Choose the implementation path

### Path A — Compose-first MVP
Use **Jetpack Compose** when:
- the app is Android only
- the user wants modern native Android UX
- the feature set is standard app UI, auth, content, forms, settings, lists, media, maps, chat-lite, dashboards
- the goal is an MVP, prototype, or production foundation

### Path B — Compose + Android platform features
Use **Compose** plus Android platform services when the prompt needs:
- foreground/background services
- notifications
- advanced file/media flows
- Bluetooth/NFC/location/device integrations
- widgets or Android-specific OS behavior

### Path C — View-system escalation
Escalate only when clearly needed for:
- legacy Android codebase integration
- third-party SDK limitations tied to older patterns
- specific UI components that are impractical in current scope with Compose alone

If the prompt does not force Path C, choose A or B.

## First-pass workflow

### Step 1 — Convert the prompt and/or image into a product spec
Extract:
- app name
- one-sentence value proposition
- target users
- core user journey
- required screens
- required entities / data models
- required actions
- Android-specific integrations
- auth/account needs
- must-have vs deferred features

If the prompt is vague, make practical MVP assumptions and label them clearly.

If screenshots or mockups are provided, inspect them and capture:
- navigation structure
- visual hierarchy
- spacing rhythm
- typography scale
- card/list/form patterns
- color palette
- icon treatment
- Android-specific affordances
- repeated components

Do not promise pixel-perfect cloning unless explicitly asked. By default, learn the design system and rebuild it using reusable Compose components.

### Step 1A — Extract an Android design system from images
Derive:
- colors, spacing scale, corner radius, elevation, typography roles
- component inventory: app bars, bottom nav, cards, chips, list rows, FABs, forms, dialogs, sheets
- interaction patterns: tabs, bottom nav, modal sheet, inline forms, filter chips, pull-to-refresh

Write a concise design-extraction note before implementation.

### Step 2 — Define the MVP scope
Reduce v1 to:
- 1 main persona
- 1 core workflow
- 3-7 screens
- minimal data model
- minimal settings complexity
- minimal backend integration needed to demonstrate value

### Step 3 — Choose the app architecture
Recommended default structure:
- `app/src/main/java/.../app/` for app setup/navigation/theme
- `app/src/main/java/.../features/` for domain features
- `app/src/main/java/.../components/` for reusable Compose UI
- `app/src/main/java/.../data/` for repositories/API/storage
- `app/src/main/java/.../model/` for typed models
- `app/src/main/res/` for resources

Recommended defaults:
- Kotlin
- Jetpack Compose
- simple feature-oriented structure
- local/mock data first unless the user explicitly needs a real backend
- Material-based patterns adapted to the provided design language

### Step 4 — Generate the screen map
For each screen define:
- screen name
- user goal
- primary UI sections
- primary CTA
- empty state
- loading state
- error state
- navigation destination

### Step 5 — Implement in thin vertical slices
Build in this order:
1. app shell and navigation
2. theme/tokens and reusable Compose primitives
3. first end-to-end user flow
4. second supporting flow
5. remaining screens
6. persistence/API wiring
7. permissions, background behavior, polish

Prefer a working native flow over broad incomplete scaffolding.

## Prompt-to-app delivery pattern
When the user gives only a prompt, produce these artifacts before or alongside coding:
1. app summary
2. MVP feature list
3. screen list
4. data model
5. Android architecture decision
6. build plan
7. implementation

If the user also gives design images, add:
8. design extraction summary
9. component inventory derived from the UI reference
10. starter theme token set

If the user asks directly to build, start implementing immediately after deriving the MVP.

## Full Android scaffold workflow
Use this when the chosen path is native Android.

### Scaffold steps
1. Choose app name, package name, and minimum SDK target.
2. Create an Android Studio project with Kotlin + Compose.
3. Establish base folders/modules as needed:
   - `app/`
   - feature packages
   - component package
   - data/model layers
   - theme package
4. Create the app shell:
   - activity entry
   - navigation graph/container
   - theme/tokens
   - shared button/input/card primitives
5. Implement the primary user journey first.
6. Add mock data or local persistence where needed.
7. Wire real backend/services only when justified by scope.
8. Verify build, previews, and main flow.

### Recommended initial files
- `MainActivity.kt`
- `app/AppNav.kt`
- `app/AppTheme.kt`
- `components/`
- `features/home/HomeScreen.kt`
- `model/`
- `data/`

### Verification commands / checks
Use environment-appropriate verification. Prefer:
- Gradle sync succeeds
- app builds successfully
- Compose previews render when practical
- main navigation flow works
- permissions/services assumptions are documented

If CLI build is available, use something like:
```bash
./gradlew assembleDebug
```

### Native Android delivery expectations
A complete scaffold should include:
- launchable Android app
- route/navigation structure
- reusable theme/tokens
- at least one polished end-to-end flow
- documented setup notes for permissions, services, or external SDKs

## UI-from-image workflow
When the user provides screenshots or design images:
1. Inspect the image with vision tools.
2. Describe the layout objectively before coding.
3. Extract design tokens and repeated components.
4. Rebuild the style using reusable Compose composables and theme tokens.
5. Match the design language first, then refine individual screens.
6. If multiple screenshots conflict, identify the dominant pattern and keep consistency.

## Image-analysis checklist
Capture these details if visible:
- top app bar/bottom nav/navigation pattern
- title/subtitle hierarchy
- card/list/form structure
- spacing and density
- CTA placement and prominence
- FAB presence and action style
- chips/filters/dialogs/sheets style
- elevation/shadow usage
- icon style and imagery
- dark/light assumptions

## Backend decision rules
Use mock/local data first when:
- speed matters
- backend requirements are unclear
- the app is an MVP/demo

Add a real backend when:
- auth is explicitly required
- user data must persist or sync
- the app needs cloud functions/admin workflows

Reasonable default backend:
- Supabase when auth/storage/database are needed
- Room/local storage when offline/local-first is enough

## Android-specific escalation rules
Plan carefully when the prompt requires:
- background services
- Bluetooth/NFC
- advanced location/geofencing
- notifications/work manager flows
- file/media providers
- Android widgets
- battery/performance-sensitive persistent behaviors

These are still valid native-Android fits, but they require more explicit permission, lifecycle, and testing planning.

## UI / UX defaults
Unless the user specifies otherwise:
- use a clean Android-native UI language
- use large touch targets
- keep flows obvious
- favor standard navigation and controls when possible
- include loading, empty, and error states
- keep the extracted design language consistent across all screens

## Implementation standards
- keep code modular and reusable
- use typed models
- prefer simple Compose composition over premature abstractions
- keep state/data flow understandable
- document assumptions for permissions/services/integrations
- do not leave disconnected placeholder screens without marking them clearly

## Verification checklist
Before declaring the app ready:
- app builds
- navigation works end-to-end
- primary CTA works on each implemented screen
- loading/empty/error states exist where needed
- permissions/service assumptions are documented
- the main user journey can be demoed quickly
- design language matches prompt/image references

## Common pitfalls
- overbuilding architecture before proving one real flow
- recreating screenshots with one-off styling instead of reusable composables
- underestimating Android permission/background complexity
- escalating away from Compose too early
- mixing conflicting reference styles

## Good default outcome
A successful first pass should give the user:
- a structured native Android project
- a clear theme system
- reusable Compose components
- at least one working end-to-end Android app flow
- a strong basis for Play Store-oriented iteration
