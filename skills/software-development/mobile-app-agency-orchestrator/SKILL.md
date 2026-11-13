---
name: mobile-app-agency-orchestrator
description: "End-to-end orchestration skill for turning a mobile app prompt and optional UI reference images into a routed implementation workflow: inspect prompt/images, choose the right stack, derive MVP scope, prepare build plan, and hand off to the correct mobile build skill."
license: Proprietary. LICENSE.txt has complete terms
---

# Mobile App Agency Orchestrator

## When to use
Use this skill when the user wants Hermes to handle a mobile app request end-to-end, especially when the user provides:
- a rough app idea
- a natural-language prompt
- screenshots, mockups, wireframes, or design images
- uncertainty about whether to use Expo, Flutter, iOS native, or Android native

Typical triggers:
- "Build me a mobile app from this prompt"
- "Use these screenshots and make the app"
- "Figure out the right mobile stack and start"
- "Create an iPhone or Android app from this idea"
- "Turn this concept into a real mobile MVP"

## Goal
Standardize the full prompt-to-mobile-app intake flow:
1. inspect the prompt
2. inspect UI/design references if provided
3. determine product scope and MVP boundary
4. choose the right stack
5. generate a concise implementation plan
6. route into the correct downstream build skill
7. keep outputs consistent and reviewable

## Primary downstream skills
- `software-development/mobile-stack-selector`
- `software-development/mobile-app-from-prompt`
- `software-development/flutter-app-from-prompt`
- `software-development/native-ios-from-prompt`
- `software-development/native-android-from-prompt`
- `software-development/writing-plans` for non-trivial builds

## Orchestration workflow

### Phase 1 — Intake
Collect or infer:
- app name
- target users
- target platform: iPhone, Android, or both
- main user problem solved
- main user journey
- must-have features
- deferred features
- backend/auth needs
- external integrations
- time pressure: MVP vs polished production app

If missing details do not block the build, make practical MVP assumptions and label them clearly.

### Phase 2 — Design inspection
If screenshots/mockups/images are provided:
1. inspect them with vision tools
2. summarize the visible UI system
3. extract:
   - navigation pattern
   - layout rhythm
   - color palette
   - typography feel
   - repeated components
   - CTA style
   - density / spacing
   - likely interaction patterns
4. note whether the design looks:
   - standard app UI
   - moderately custom branded UI
   - highly custom / highly polished / platform-native UI

If no images are provided, define a default clean mobile design direction.

### Phase 3 — MVP definition
Reduce the app to a realistic first version:
- 1 primary persona
- 1 core workflow
- 3-7 initial screens
- minimal data model
- minimal settings/config complexity
- only essential integrations

The orchestrator should actively cut scope instead of preserving every idea from the original prompt.

### Phase 4 — Stack routing
Use `software-development/mobile-stack-selector` logic.

Default routing rules:
- **Expo / React Native** → fastest cross-platform MVP
- **Flutter** → cross-platform with stronger custom visual fidelity
- **SwiftUI** → iPhone-only or Apple-native requirements
- **Kotlin / Jetpack Compose** → Android-only or Android-specific platform requirements

If no strong constraint pushes elsewhere, default to Expo.

### Phase 5 — Build plan generation
For any non-trivial app, prepare a concise implementation plan before coding.
The plan should include:
- chosen stack
- screen list
- data model
- primary user flow
- reusable component inventory
- backend decision
- delivery phases

Use `software-development/writing-plans` style when the app is complex enough to benefit from bite-sized implementation tasks.

### Phase 6 — Downstream handoff
After stack selection:
- Expo / React Native → use `software-development/mobile-app-from-prompt`
- Flutter → use `software-development/flutter-app-from-prompt`
- iOS native → use `software-development/native-ios-from-prompt`
- Android native → use `software-development/native-android-from-prompt`

The orchestrator should not stop at naming the stack. It should carry forward:
- MVP assumptions
- design extraction summary
- screen map
- key constraints
- implementation priority order

## Standard output format
When using this skill, produce work in this structure:

### 1. App concept
- app name
- target users
- core promise

### 2. Recommended stack
- chosen stack/framework
- why it fits this request

### 3. MVP scope
- must-have features
- deferred features
- core user flow

### 4. Design direction
- image/design extraction summary if references exist
- or default UI direction if not

### 5. Screen map
- screen names with purpose

### 6. Data model
- entities and key fields

### 7. Delivery plan
- phase 1 scaffold
- phase 2 primary flow
- phase 3 supporting flows
- phase 4 polish/integrations

### 8. Downstream build path
- exact next skill/path to use

## Design-to-stack heuristics
- standard or moderately custom business UI + speed priority → Expo
- highly branded, design-heavy, visually strict cross-platform UI → Flutter
- Apple-native UX, iOS-only, or Apple frameworks → SwiftUI
- Android-specific device/background behavior → Jetpack Compose

## Backend heuristics
Use mock/local data first when:
- the goal is fast validation
- backend requirements are unclear
- the app is a prototype or demo

Add a real backend when:
- auth is required
- durable multi-user data is required
- sync/cloud behavior is part of the main value

Reasonable default backend:
- Supabase for auth/storage/database

## Review-first principle
The orchestrator should keep the process reviewable:
- separate must-have from nice-to-have
- state assumptions explicitly
- make stack choice explainable
- keep screen/data decisions visible before deep implementation
- avoid black-box prompt dumping into code generation

## Common pitfalls
- trying to preserve too much scope from the original idea
- routing to native too early for a simple MVP
- routing to Expo when the design or native requirements clearly demand more
- failing to inspect screenshots before choosing the stack
- generating a build plan that is too abstract to execute
- stopping at stack recommendation without producing the implementation handoff

## Final rule
This orchestrator is the default front door for mobile app requests when the user wants Hermes to own the whole process from prompt/design intake to implementation routing.
