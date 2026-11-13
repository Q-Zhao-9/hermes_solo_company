---
name: mobile-app-delivery-handoff
description: "Package a mobile app project for developer, client, demo, QA, or store-prep handoff by assembling setup instructions, environment variables, run/build/test commands, architecture summary, known issues, release readiness notes, and next-step ownership."
license: Proprietary. LICENSE.txt has complete terms
---

# Mobile App Delivery Handoff

## When to use
Use this skill when a mobile app needs to be handed off in a structured, usable way after planning, implementation, or QA.

Use it for apps built with:
- Expo / React Native
- Flutter
- SwiftUI
- Kotlin / Jetpack Compose

Typical triggers:
- "Prepare this app for handoff"
- "Package the delivery notes"
- "Create client/developer handoff docs"
- "Get this ready for another engineer"
- "Prepare demo/setup/build instructions"
- "Create release-prep notes for this mobile app"

## Goal
Turn a codebase and its current status into a clean delivery package that another person can use without guessing.

The handoff should make it easy for the next person to:
1. understand what the app is
2. understand what stack it uses
3. set it up locally
4. run it
5. build/test it
6. know what works and what does not
7. know what environment/config is required
8. know what to do next

## Inputs to gather
Collect as many of these as available:
- project path/repo path
- stack/framework
- original prompt/spec
- current implementation status
- QA findings if available
- build/test/lint results
- environment variable requirements
- backend/service dependencies
- release target: demo, internal test, client handoff, store prep

If information is missing, state the gap explicitly instead of guessing.

## Handoff workflow

### Phase 1 — Reconstruct project purpose
Summarize:
- app name
- target users
- core promise
- chosen stack
- platform target
- current maturity level

This section is for someone who has never seen the project before.

### Phase 2 — Inspect runnable requirements
Document what is needed to run the app:
- required tools/SDKs
- package manager
- platform tooling
- emulator/simulator assumptions
- backend services required
- env vars/secrets placeholders
- asset/config dependencies

If secrets are required, list variable names only — never expose secret values.

### Phase 3 — Document local setup
Produce setup instructions with:
- install prerequisites
- install dependencies
- configure env
- start dev server/app
- open emulator/simulator or device target
- run tests/lint/typecheck/build

Keep the instructions specific to the actual stack.

### Phase 4 — Document project structure
Explain the most important folders/files only, such as:
- app shell / entrypoint
- routes/navigation
- feature modules
- reusable UI components
- services/data layer
- theme/tokens
- assets/config

Avoid dumping the whole tree. Focus on the files another engineer must understand first.

### Phase 5 — Document current status
State clearly:
- what is working
- what is partially implemented
- what is mocked or placeholder-only
- what is blocked
- what is intentionally deferred

This is the honesty section. It should prevent false expectations.

### Phase 6 — Include QA/readiness summary
If QA findings exist, summarize:
- overall readiness
- known blockers
- important polish gaps
- known bugs
- recommended next actions before demo/release

If no QA was done, say so explicitly.

### Phase 7 — Build and release notes
Document how to produce the relevant output for the stack:
- Expo/React Native: dev start, export/build notes, EAS or equivalent if relevant
- Flutter: run/build commands for debug/release
- SwiftUI: Xcode build/archive assumptions
- Jetpack Compose: Gradle build, debug/release output assumptions

If store submission is in scope, include a prep checklist rather than pretending it is already complete.

### Phase 8 — Ownership and next steps
Create a clear next-step queue, such as:
- immediate blockers to fix
- next implementation phase
- QA follow-up
- release hardening tasks
- store submission preparation

If relevant, identify who the handoff is for:
- another engineer
- a client/stakeholder
- QA
- demo operator

## Required output format
When using this skill, structure the handoff as:

### 1. Project summary
- app name
- purpose
- target users
- stack
- platform target
- handoff target (engineer/client/QA/demo/release)

### 2. Current status
- working now
- partially complete
- mocked/deferred
- blockers

### 3. Setup prerequisites
- required tools/SDKs
- environment/config needs
- backend/service dependencies

### 4. Local setup steps
- install
- configure
- run
- test/lint/build

### 5. Key project structure
- important folders/files and what they do

### 6. Run/build commands
- exact commands or command categories appropriate to the stack

### 7. QA and known issues
- readiness notes
- known bugs
- design/flow gaps
- technical risks

### 8. Release/store-prep notes
- what is done
- what still needs completion

### 9. Recommended next steps
- prioritized action list

### 10. Handoff note
- concise note to the next owner explaining where to start

## Stack-specific guidance

### Expo / React Native
Usually include:
- Node/package manager version expectations
- dependency install command
- dev server start command
- emulator/device/web preview assumptions
- env file names
- build/export notes if available

### Flutter
Usually include:
- Flutter SDK requirement
- `flutter pub get`
- `flutter run`
- `flutter analyze`
- `flutter test`
- platform build notes

### Native iOS
Usually include:
- Xcode requirement
- opening `.xcodeproj` or `.xcworkspace`
- scheme/target notes
- signing/team assumptions
- simulator/device build notes

### Native Android
Usually include:
- Android Studio / JDK / SDK expectations
- Gradle sync/build assumptions
- `./gradlew assembleDebug` or related commands
- emulator/device notes

## Delivery modes
Tailor the handoff based on audience:

### Developer handoff
Focus on:
- setup
- structure
- commands
- known issues
- next implementation tasks

### Client/stakeholder handoff
Focus on:
- what is implemented
- what to click/demo
- known limitations
- what remains before production

### QA handoff
Focus on:
- testable flows
- known fragile areas
- expected behaviors
- open bugs and risk areas

### Release/store-prep handoff
Focus on:
- signing/build artifacts
- required assets/metadata
- environment readiness
- submission blockers

## Common pitfalls
- giving generic setup instructions not tied to the actual stack
- hiding incomplete features instead of documenting them
- omitting env/config requirements
- mixing demo-readiness with production-readiness
- providing commands without explaining when to use them
- failing to identify the next owner and next action

## Final rule
This skill should leave the next person with a practical, trustworthy handoff package so they can continue the project, demo it, QA it, or prepare it for release without reverse-engineering the current state.
