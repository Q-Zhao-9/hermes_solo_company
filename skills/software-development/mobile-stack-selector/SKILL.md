---
name: mobile-stack-selector
description: Choose the right mobile app implementation path from a prompt and optional UI/design references, routing work to Expo/React Native, Flutter, SwiftUI, or Kotlin/Jetpack Compose based on platform needs, native requirements, UI demands, and speed-to-MVP constraints.
license: Proprietary. LICENSE.txt has complete terms
---

# Mobile Stack Selector

## When to use
Use this skill when the user wants a mobile app built but has **not clearly chosen the stack**, or when they want help deciding between:
- Expo / React Native
- Flutter
- SwiftUI
- Kotlin / Jetpack Compose

Typical triggers:
- "Build a mobile app from this prompt"
- "Should this be Flutter or React Native?"
- "What's the best stack for this iPhone + Android app?"
- "I have screenshots and a product idea — what should we use?"
- "Make this app, choose the right mobile framework"

## Goal
Route the request to the best implementation path with a clear justification, then continue using the corresponding build skill.

Primary downstream skills:
- `software-development/mobile-app-from-prompt`
- `software-development/flutter-app-from-prompt`

If the request is explicitly native-only, use the same routing logic but build with:
- **SwiftUI** for iPhone/iOS
- **Kotlin + Jetpack Compose** for Android

## Inputs to inspect
From the user prompt and any attached screenshots/mockups/images, determine:
- target platform: iPhone, Android, or both
- MVP speed vs long-term customization
- UI fidelity and custom design demands
- native SDK / hardware requirements
- offline/background behavior requirements
- store-readiness / production hardening needs
- team preference if explicitly stated
- future platform expansion (web/desktop)
- backend/auth/data sync needs

## Decision framework

### Route to Expo / React Native when
Choose **Expo / React Native** if most of these are true:
- the user wants the fastest MVP
- both iPhone and Android are needed
- requirements are mostly standard app patterns: auth, forms, CRUD, dashboards, chat, content, maps, camera-lite
- there is no strong native-only constraint
- iteration speed matters more than deep rendering control
- the UI can be reproduced well with a practical component system

Why:
- fastest path from prompt to demo
- large ecosystem
- efficient prompt-to-scaffold workflow
- best default unless requirements force otherwise

### Route to Flutter when
Choose **Flutter** if most of these are true:
- both iPhone and Android are needed
- UI consistency and custom visuals matter a lot
- screenshots/mockups suggest highly branded, design-heavy screens
- the user explicitly prefers Flutter
- future expansion to web/desktop is plausible
- the team is comfortable with Dart or wants one consistent rendering layer

Why:
- strong control over visual consistency
- excellent for custom UI systems
- very good fit for image-driven app recreation

### Route to SwiftUI when
Choose **SwiftUI** if most of these are true:
- the app is iPhone/iOS only
- Apple-native feel is important
- deep iOS integrations are required
- App Store production quality and native behavior are top priority
- the user explicitly asks for native iOS

Why:
- best fit for platform-native iPhone experiences
- easiest route for deep Apple integrations
- strongest iOS-native UX alignment

### Route to Kotlin / Jetpack Compose when
Choose **Kotlin / Jetpack Compose** if most of these are true:
- the app is Android only
- Android-specific behavior, hardware, or background services matter
- Play Store/native Android quality is a priority
- the user explicitly asks for native Android

Why:
- best fit for Android-specific capabilities
- strongest native Android integration path

## Native escalation rules
Do **not** choose Expo or Flutter by default if the prompt clearly requires:
- advanced Bluetooth / NFC / low-level hardware workflows
- heavy background services or persistent background execution
- advanced health/device integrations
- strict platform-exclusive behavior
- deep OS-specific APIs where cross-platform wrappers are risky

In such cases, route to native.

## UI-from-image routing rules
If the user provides screenshots, mockups, or design images:
1. Inspect the images first.
2. Estimate whether the UI is:
   - standard app UI
   - design-heavy but still component-friendly
   - highly custom/animated/platform-native
3. Use that to guide the stack choice.

General rule:
- **standard or moderately custom UI** → Expo is often enough
- **highly polished, heavily branded, visually custom UI** → Flutter often wins
- **platform-native visual language or deep OS integration** → SwiftUI / Jetpack Compose

## Simple routing heuristic
Use this order:
1. **Explicit user stack preference wins** unless it clearly conflicts with requirements.
2. If **native-only platform requirement** exists, choose native.
3. If **deep native APIs** are central, choose native.
4. If **cross-platform + fastest MVP** is primary, choose Expo.
5. If **cross-platform + custom visual fidelity** is primary, choose Flutter.
6. If ambiguous, default to Expo and explain why.

## Required output format
When using this skill, respond with:

### Recommended stack
- Expo / React Native
- Flutter
- SwiftUI
- Kotlin / Jetpack Compose

### Why this choice fits
- 3-6 bullets tied to the actual prompt

### What we optimize for
- speed
- UI fidelity
- native access
- maintainability
- platform reach

### What we trade off
- e.g. faster delivery vs deepest native access

### Next build skill/path
- `software-development/mobile-app-from-prompt`
- `software-development/flutter-app-from-prompt`
- native iOS implementation path
- native Android implementation path

## Recommended defaults after routing
- If Expo chosen → load `software-development/mobile-app-from-prompt`
- If Flutter chosen → load `software-development/flutter-app-from-prompt`
- If native chosen → create a concise implementation plan before building

## Common pitfalls
- over-choosing native for a simple MVP
- choosing Expo when the app is fundamentally hardware/native-driven
- choosing Flutter only because the UI looks pretty when speed is the true priority
- ignoring explicit team/user preference
- failing to inspect screenshots before deciding

## Short decision table
- **Fastest cross-platform MVP** → Expo / React Native
- **Cross-platform + strongest custom UI consistency** → Flutter
- **iPhone-only + deep Apple/native needs** → SwiftUI
- **Android-only + deep Android/native needs** → Kotlin / Jetpack Compose

## Final rule
If no strong constraint pushes elsewhere, choose **Expo / React Native** as the default prompt-to-mobile-app path.
