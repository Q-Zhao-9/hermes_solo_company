---
name: native-ios-from-prompt
description: Turn a natural-language product prompt and optional UI reference images into a reviewable native iPhone/iOS app MVP using SwiftUI-first workflows, with escalation guidance for deeper UIKit or Apple framework integrations.
license: Proprietary. LICENSE.txt has complete terms
---

# Native iOS From Prompt

## When to use
Use this skill when the user wants to create, scaffold, plan, redesign, or iteratively build a **native iPhone/iOS app** from:
- a plain-English prompt
- a rough feature list or product spec
- screenshots, mockups, wireframes, or UI images
- a combined product + design brief

Typical triggers:
- "Build an iPhone app from this prompt"
- "Make this app natively for iOS"
- "Use these screenshots and create a SwiftUI app"
- "I need Apple-native UX and integrations"
- "Create an App Store-ready iPhone MVP"

## Default strategy
Unless the prompt clearly requires UIKit-specific legacy work, default to:
- **Swift**
- **SwiftUI**
- **Xcode project scaffold**
- **Apple-native patterns** for navigation, settings, permissions, and system integrations

Why:
- Fastest modern path for native iPhone apps
- Best alignment with Apple platform conventions
- Strong fit for image-driven recreation of polished iOS UI
- Good foundation for deeper Apple frameworks later

## Choose the implementation path

### Path A — SwiftUI-first MVP
Use **SwiftUI** when:
- the app is iPhone/iOS only
- the user wants modern native Apple UX
- the feature set is standard app UI, auth, content, forms, settings, lists, media, maps, chat-lite, dashboards
- the goal is an MVP, prototype, or production foundation

### Path B — SwiftUI + Apple frameworks
Use **SwiftUI** plus targeted native frameworks when the prompt needs:
- camera/photo/video workflows
- maps/location/geofencing
- notifications/background tasks
- HealthKit, CoreBluetooth, NFC, CallKit, SiriKit, Widgets, Live Activities, etc.

### Path C — UIKit escalation
Escalate only when clearly needed for:
- legacy codebase integration
- highly custom imperative flows that SwiftUI cannot reasonably cover in scope
- third-party SDK constraints that assume UIKit lifecycle patterns

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
- Apple-specific integrations
- auth/account needs
- must-have vs deferred features

If the prompt is vague, make practical MVP assumptions and label them clearly.

If screenshots or mockups are provided, inspect them and capture:
- navigation structure
- screen hierarchy
- spacing rhythm
- typography scale
- card/list/form patterns
- color palette
- iconography style
- iOS-specific affordances
- repeated components

Do not promise pixel-perfect cloning unless explicitly asked. By default, learn the design system and rebuild it using reusable SwiftUI components.

### Step 1A — Extract an iOS design system from images
Derive:
- colors, spacing scale, corner radius, shadows/material usage
- font sizing and weight hierarchy
- component inventory: rows, cards, segmented controls, CTA buttons, sheets, tab bars, nav bars
- interaction patterns: tab navigation, push detail, bottom sheet, modal form, inline validation

Write a concise design-extraction note before implementation.

### Step 2 — Define the MVP scope
Reduce v1 to:
- 1 main persona
- 1 core workflow
- 3-7 screens
- minimal data model
- minimal settings complexity
- minimal backend integration needed to demonstrate the value

### Step 3 — Choose the app architecture
Recommended default structure:
- `App/` for app entry and root coordination
- `Features/` for domain features and screens
- `Components/` for reusable SwiftUI UI pieces
- `Services/` for API/storage/auth/integration logic
- `Models/` for typed models
- `Resources/` for assets/config
- `Theme/` for design tokens, colors, spacing, text styles

Recommended defaults:
- SwiftUI
- MVVM-ish organization without over-abstracting
- start with local/mock data unless the user explicitly needs a real backend
- use Apple-native components whenever they fit the UI

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
2. theme/tokens and reusable UI primitives
3. first end-to-end user flow
4. second supporting flow
5. remaining screens
6. persistence/API wiring
7. permissions, error handling, polish

Prefer a working native flow over wide incomplete scaffolding.

## Prompt-to-app delivery pattern
When the user gives only a prompt, produce these artifacts before or alongside coding:
1. app summary
2. MVP feature list
3. screen list
4. data model
5. iOS architecture decision
6. build plan
7. implementation

If the user also gives design images, add:
8. design extraction summary
9. component inventory derived from the UI reference
10. starter theme token set

If the user asks directly to build, start implementing immediately after deriving the MVP.

## Full SwiftUI scaffold workflow
Use this when the chosen path is native iOS.

### Scaffold steps
1. Choose app name, bundle identifier pattern, and minimum iOS target.
2. Create an Xcode SwiftUI app project.
3. Establish base folders:
   - `App/`
   - `Features/`
   - `Components/`
   - `Services/`
   - `Models/`
   - `Theme/`
   - `Resources/`
4. Create the app shell:
   - root app entry
   - navigation container
   - tab structure if needed
   - theme/tokens file
   - shared button/input/card primitives
5. Implement the primary user journey first.
6. Add mock data or preview data where needed.
7. Wire real backend/services only when justified by scope.
8. Verify build, previews, and main flow.

### Recommended initial files
- `App/<AppName>App.swift`
- `App/RootView.swift`
- `Theme/AppTheme.swift`
- `Theme/Color+App.swift`
- `Components/`
- `Features/Home/HomeView.swift`
- `Models/`
- `Services/`

### Verification commands / checks
Use environment-appropriate verification. Prefer:
- project opens cleanly in Xcode
- app builds successfully
- previews render for key views when practical
- main navigation flow works
- key permissions/integrations are documented

If command-line build is available, use something like:
```bash
xcodebuild -scheme <AppName> -destination 'generic/platform=iOS' build
```

### Native iOS delivery expectations
A complete scaffold should include:
- launchable SwiftUI app
- route/navigation structure
- reusable theme/tokens
- at least one polished end-to-end flow
- documented setup notes for signing, permissions, or external SDKs

## UI-from-image workflow
When the user provides screenshots or design images:
1. Inspect the image with vision tools.
2. Describe the layout objectively before coding.
3. Extract design tokens and repeated components.
4. Rebuild the style using reusable SwiftUI views and modifiers.
5. Match the design language first, then refine individual screens.
6. If multiple screenshots conflict, identify the dominant pattern and keep consistency.

## Image-analysis checklist
Capture these details if visible:
- top navigation style
- tab bar or root navigation pattern
- title/subtitle hierarchy
- spacing and density
- CTA placement and prominence
- input/list/card radius and shadows
- system material usage, blur, sheets, segmented controls
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
- Apple-native local persistence when offline/local-only is enough

## iOS-specific escalation rules
Plan carefully when the prompt requires:
- HealthKit
- CoreBluetooth
- NFC
- background processing
- push notifications
- widgets/live activities
- camera/media capture
- App Store review-sensitive permissions

These are still valid native-iOS fits, but they require more explicit entitlement, permission, and testing planning.

## UI / UX defaults
Unless the user specifies otherwise:
- use a clean Apple-native UI language
- use large touch targets
- keep forms concise
- favor standard navigation and controls when possible
- include loading, empty, and error states
- keep the extracted design language consistent across all screens

## Implementation standards
- keep code modular and reusable
- use typed models
- prefer simple SwiftUI composition over premature abstractions
- keep view logic readable
- document assumptions for Apple-specific permissions/integrations
- do not leave disconnected placeholder screens without marking them clearly

## Verification checklist
Before declaring the app ready:
- app builds
- navigation works end-to-end
- primary CTA works on each implemented screen
- loading/empty/error states exist where needed
- permissions/integration assumptions are documented
- the main user journey can be demoed quickly
- design language matches prompt/image references

## Common pitfalls
- overbuilding architecture before proving one real flow
- recreating screenshots with one-off styling instead of reusable components
- underestimating Apple permission/integration setup
- choosing UIKit too early when SwiftUI is sufficient
- mixing conflicting reference styles

## Good default outcome
A successful first pass should give the user:
- a structured native iOS project
- a clear theme system
- reusable SwiftUI components
- at least one working end-to-end iPhone app flow
- a strong basis for App Store-oriented iteration
