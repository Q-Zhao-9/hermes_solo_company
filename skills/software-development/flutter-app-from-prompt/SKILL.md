---
name: flutter-app-from-prompt
description: Turn a natural-language product prompt and optional UI reference images into a reviewable Flutter mobile app MVP for iPhone and Android, with a practical scaffold-first workflow.
license: Proprietary. LICENSE.txt has complete terms
---

# Flutter App From Prompt

## When to use
Use this skill when the user wants a mobile app created with Flutter from:
- a plain-English prompt
- a rough feature list
- screenshots, design mockups, or reference images
- a combined product + design brief

Typical triggers:
- "Build this app in Flutter"
- "Make me a Flutter MVP from this prompt"
- "Use these UI screenshots and create the app in Flutter"
- "Create an iPhone and Android app from this design"

## Default strategy
Default to:
- **Flutter**
- **Dart**
- **Single cross-platform codebase** for iPhone and Android

Choose Flutter when:
- the user explicitly prefers Flutter
- the team wants one polished UI codebase
- the app depends heavily on custom UI consistency
- the user may later expand to web/desktop with the same stack

## Prompt and image intake workflow

### Step 1 — Convert prompt/images into an MVP spec
Extract:
- app name
- target users
- main user journey
- must-have features
- required screens
- data/entities
- backend/auth needs
- integrations
- deferred features

If screenshots or mockups are provided, extract:
- layout patterns
- spacing rhythm
- color system
- typography feel
- navigation structure
- component styles
- interaction patterns

Output a short design-extraction summary before building.

### Step 2 — Reduce to MVP scope
Constrain v1 to:
- 1 main persona
- 1 core user flow
- 3-7 screens
- minimal data model
- minimal settings/admin complexity

### Step 3 — Choose architecture
Recommended default structure:
- `lib/main.dart`
- `lib/app/` for app shell, routes, theme
- `lib/features/` for domain features
- `lib/widgets/` for reusable UI pieces
- `lib/services/` for API/storage/auth
- `lib/models/` for typed data models
- `assets/` for images/fonts/icons

State management default:
- keep it simple first
- Provider / Riverpod / Bloc only when complexity justifies it

## Full Flutter scaffold workflow

### Scaffold steps
1. Create project:
   ```bash
   flutter create my_app
   ```
2. Verify Flutter project structure.
3. Add only needed dependencies after confirming scope.
4. Create:
   - app shell
   - route/navigation structure
   - theme tokens
   - reusable UI primitives
5. Implement the primary flow first.
6. Add mock/local data as needed.
7. Wire backend only when requirements justify it.
8. Run formatting/analyzer/tests.

### Recommended initial files
- `lib/main.dart`
- `lib/app/app.dart`
- `lib/app/router.dart`
- `lib/app/theme.dart`
- `lib/widgets/`
- `lib/features/<feature>/`

### Verification commands
Run as available:
```bash
flutter pub get
flutter analyze
flutter test
```

A good scaffold should include:
- launchable Flutter app
- working navigation shell
- reusable theme/tokens
- at least one polished vertical slice
- notes for next implementation steps

## UI-from-image workflow
When screenshots or UI images are provided:
1. Inspect the image with vision tools.
2. Describe the visible structure objectively.
3. Extract design tokens and repeated components.
4. Rebuild the style using reusable Flutter widgets.
5. Match the overall design language first, then fine-tune individual screens.

### Image-analysis checklist
Capture:
- app bar / tab bar / bottom nav style
- card/list/form composition
- spacing and density
- corner radius and shadows
- color palette and contrast
- CTA prominence
- typography scale
- icon style
- dark/light assumptions

## UI / UX defaults
Unless the user says otherwise:
- use a clean modern mobile UI
- keep primary flows obvious
- favor large tap targets
- make layouts reusable
- include loading, empty, and error states
- maintain consistency with any provided design references

## Backend decision rules
Use mock/local data first when:
- speed matters
- backend is unclear
- the app is a demo/MVP

Add a real backend when:
- auth is required
- user data must persist across devices
- multi-user sync is necessary

Reasonable default backend:
- Supabase when auth/storage/database are needed

## Delivery pattern
For prompt-only requests, produce:
1. app concept
2. MVP scope
3. screen list
4. data model
5. Flutter architecture choice
6. scaffold/build plan
7. implementation

If images are provided, also include:
8. design extraction summary
9. reusable component inventory
10. theme token starter set

## Common pitfalls
- overbuilding state management too early
- building many screens before wiring one real flow
- hardcoding styles screen-by-screen instead of making reusable widgets
- mixing design inspiration from conflicting screenshots
- adding backend complexity before validating the UX

## Verification checklist
Before declaring success:
- app starts
- main flow works
- navigation works
- analyzer passes if configured
- tests pass if present
- design language is consistent with prompt/image references

## Good default outcome
A successful first pass should give the user:
- a structured Flutter project
- a clear theme system
- reusable widgets
- at least one working end-to-end app flow
- a clean basis for future iteration
