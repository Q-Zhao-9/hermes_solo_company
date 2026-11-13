---
name: mobile-app-from-prompt
description: Turn a natural-language product prompt into a reviewable iPhone app, Android app, or cross-platform mobile MVP using a default Expo/React Native workflow, with native-only fallback paths when the requirements demand them.
license: Proprietary. LICENSE.txt has complete terms
---

# Mobile App From Prompt

## When to use
Use this skill when the user wants to create, scaffold, plan, redesign, or iteratively build a mobile app from:
- a plain-English prompt
- a feature list or rough product spec
- a screenshot, mockup, wireframe, or design image
- a combination of prompt + image references

Typical triggers:
- "Build me an iPhone app from this prompt"
- "Create an Android app MVP"
- "Turn this idea into a mobile app"
- "Make a cross-platform app from this product description"
- "Generate the starter app and screens"
- "Recreate this mobile UI from the screenshot"
- "Use this image as the design direction for the app"

## Default strategy
Unless the user explicitly requires native-only iOS or native-only Android, default to:
- **Expo + React Native + TypeScript**
- **Expo Router** for navigation
- **Cross-platform delivery** for both iPhone and Android from one codebase

Why:
- Fastest path from prompt to working prototype
- Lowest setup friction
- Easier preview and iteration
- Best default for prompt-driven MVP creation

## Choose the implementation path

### Path A — Default cross-platform MVP
Use **Expo/React Native** when:
- The user wants speed
- The app is an MVP, demo, prototype, or internal tool
- The feature set is standard CRUD, auth, forms, chat, dashboards, media, maps, or lightweight AI features
- iPhone and Android should both be supported

### Path B — Native iPhone app
Use **Swift / SwiftUI** only when the user explicitly asks for:
- iOS-only delivery
- Apple-specific UX or integrations
- Advanced native SDKs not suitable for Expo
- App Store / production hardening where native-only is preferred

### Path C — Native Android app
Use **Kotlin / Jetpack Compose** only when the user explicitly asks for:
- Android-only delivery
- Android-specific hardware / background behavior
- Play Store / production hardening where native-only is preferred

If the prompt does not force B or C, choose A.

## First-pass workflow

### Step 1 — Convert the prompt and/or image into a product spec
Extract and write down:
- App name
- One-sentence value proposition
- Target users
- Core user journey
- Required screens
- Required entities / data models
- Required actions
- External integrations
- Authentication needs
- Nice-to-have vs must-have features

If the prompt is vague, do **not** block immediately. Make reasonable MVP assumptions and label them clearly.

If the user provides one or more screenshots, mockups, or UI images, inspect them and capture:
- navigation pattern
- visual hierarchy
- spacing rhythm
- card/list/form patterns
- color palette
- typography feel
- icon/button treatment
- recurring components
- likely responsive/mobile behaviors

Do **not** promise pixel-perfect cloning unless asked. By default, learn the UI language from the image and adapt it into a clean reusable component system.

### Step 1A — Turn design images into a reusable UI system
When an image is provided, derive:
- design tokens: colors, radius, spacing scale, shadows, typography sizes
- reusable building blocks: header, tab bar, cards, input rows, CTA buttons, chips, modals
- interaction patterns: bottom tabs, stacked cards, floating CTA, segmented control, etc.
- app-wide design rules: light/dark bias, density, corner roundness, content spacing, illustration style

Output a short “design extraction” note before implementation so the style direction is explicit.

### Step 2 — Define the MVP scope
Reduce the first version to:
- 1 primary user persona
- 1 core workflow
- 3-7 screens
- Minimal data model
- Minimal settings
- Minimal branding

Cut anything that is not needed for a clickable or functional MVP.

### Step 3 — Choose the app architecture
Default Expo architecture:
- `app/` for route-based screens
- `components/` for reusable UI
- `features/` for domain logic where helpful
- `lib/` for API clients, config, helpers
- `hooks/` for reusable hooks
- `types/` for shared TypeScript types
- `assets/` for icons/images/fonts
- `constants/` for design tokens and app config

Recommended defaults:
- TypeScript
- ESLint / Prettier if already available
- Async state: React Query or lightweight local state depending on complexity
- Backend: start with mocked/local data unless the user explicitly wants a real backend
- Small reusable design system extracted from the prompt/image references

### Step 4 — Generate the screen map
For each screen, define:
- Screen name
- User goal
- Main UI elements
- Primary CTA
- Empty state
- Error state
- Navigation destination

### Step 5 — Implement in thin vertical slices
Build in this order:
1. App shell / routing
2. Design tokens and reusable UI primitives
3. Screen 1 end-to-end
4. Screen 2 end-to-end
5. Remaining screens
6. Local persistence / API wiring
7. Polish, validation, loading, error states

Prefer a working vertical slice over broad incomplete scaffolding.

## Prompt-to-app delivery pattern
When the user gives only a prompt, produce these artifacts before or alongside coding:

1. **App summary**
2. **MVP feature list**
3. **Screen list**
4. **Data model**
5. **Tech-stack decision**
6. **Build plan**
7. **Implementation**

If the user also gives design images, add:
8. **Design extraction summary**
9. **Component inventory derived from the UI reference**
10. **Design-token starter set**

If the user asks directly to build, start implementing immediately after deriving the MVP.

## Full Expo scaffold workflow
Use this when the chosen path is Expo/React Native.

### Scaffold steps
1. Choose a project folder name and app slug.
2. Create the app with TypeScript:
   ```bash
   npx create-expo-app@latest my-app --template
   ```
   Prefer the tabs/router template when the product clearly needs multi-screen navigation.
3. Enter the project and inspect generated structure.
4. Add key dependencies only after confirming need, commonly:
   - `expo-router`
   - `@tanstack/react-query`
   - `zustand` or another light state tool if needed
   - `react-native-safe-area-context`
   - `react-native-svg`
   - `expo-image`
5. Create the app shell:
   - route layout
   - theme/tokens file
   - reusable screen container
   - shared button/input/card primitives
6. Implement the primary user journey first.
7. Add placeholder/mock data only where needed to keep the flow functional.
8. Run verification commands.

### Recommended initial file layout
- `app/_layout.tsx`
- `app/index.tsx`
- `app/(tabs)/_layout.tsx` when tabs are needed
- `components/ui/`
- `constants/theme.ts`
- `lib/mock/`
- `types/`

### Verification commands
Run as appropriate:
```bash
npm install
npm run lint
npx expo export --platform web
```
If available, also run the dev server and verify route compilation:
```bash
npx expo start --web
```

### Expo delivery expectations
A complete scaffold should include:
- launchable project
- route structure
- reusable theme/tokens
- at least one polished end-to-end flow
- clear README or handoff notes if special setup is needed

## UI-from-image workflow
When the user provides screenshots or design images:
1. Inspect the image with a vision-capable tool.
2. Describe the layout objectively before coding.
3. Extract reusable tokens and components.
4. Rebuild the look with native mobile primitives rather than one-off hardcoded layouts.
5. Match the **style system** first, then the exact screens.
6. If multiple screenshots conflict, identify the dominant pattern and keep consistency.

## Image-analysis checklist
Capture these details from each image if visible:
- top/bottom navigation style
- number of columns/cards
- title/subtitle hierarchy
- margin/padding rhythm
- accent colors and background contrast
- CTA placement and prominence
- input style, chip style, and card radius
- icon style and illustration usage
- dark/light mode assumptions

## Implementation note for image-driven builds
Prefer creating:
- `constants/theme.ts` for tokens
- shared primitives in `components/ui/`
- screen sections that compose those primitives

Do not directly hardcode every style separately per screen if the image reveals reusable patterns.

## UI / UX defaults
Unless the user specifies otherwise:
- Use a clean modern mobile UI
- Use large tap targets
- Keep forms short
- Make the main CTA visually obvious
- Prefer bottom tabs for 2-5 top-level destinations
- Prefer stack navigation for drill-down flows
- Use card-based layouts and clear section spacing
- Add loading, empty, and error states to every non-trivial screen
- If an image reference exists, keep the extracted visual language consistent across all new screens

## Backend decision rules

### Use mock/local data first when:
- The user wants speed
- The app is an MVP/demo
- Backend requirements are unclear

### Add a real backend when:
- The user explicitly asks for auth, storage, sync, or multi-user workflows
- The app needs durable user data
- The app needs admin/reporting or cloud functions

Common default backend for MVPs:
- **Supabase** for auth, Postgres, storage, realtime

## Implementation standards
- Keep code modular and reusable
- Use typed interfaces for app data
- Avoid premature abstraction
- Add comments only where logic is non-obvious
- Keep styling consistent across screens
- Do not leave dead placeholder components without marking them clearly
- Prefer real navigation flows over disconnected mock screens

## Verification checklist
Before declaring the app ready:
- App boots successfully
- Navigation works end-to-end
- Primary CTA works on every implemented screen
- Empty/error/loading states exist where needed
- Typecheck/lint passes if configured
- The main user journey can be demonstrated in under 60 seconds
- Platform-specific instructions are documented if relevant

## Testing / preview workflow
For Expo apps, prefer:
- Project scaffold
- Install dependencies
- Run the development server
- Verify routes/screens compile
- If possible, test key flows in browser preview and/or device emulator workflow available in the environment

If emulator/device testing is unavailable, still verify via:
- TypeScript checks
- Lint
- Route structure inspection
- Unit/component tests where practical

## Common pitfalls
- Trying to support too many user personas in v1
- Building too many screens before wiring one real flow
- Over-designing the backend before validating the core UX
- Using native-only tooling when Expo is sufficient
- Shipping screens without empty/error/loading states
- Mixing app planning and implementation with no explicit MVP boundary

## Recommended Hermes workflow
1. Read the user prompt carefully
2. Turn it into a concise MVP spec
3. Create a task plan if the app is non-trivial
4. Scaffold the mobile project in the chosen stack
5. Build the primary flow first
6. Verify the flow
7. Expand iteratively

For larger builds, combine with:
- `software-development/writing-plans`
- `software-development/test-driven-development`
- `software-development/subagent-driven-development`

## Output format for a prompt-only request
When starting from just a prompt, structure the response/work as:

### App concept
- Name
- Users
- Core promise

### MVP scope
- Must-have features
- Deferred features

### Screens
- Screen list with purpose

### Data model
- Entities and fields

### Build choice
- Expo cross-platform / SwiftUI / Kotlin Compose
- Why this choice fits

### Delivery plan
- Phase 1 scaffold
- Phase 2 primary flow
- Phase 3 polish/integrations

## Good default stack
For most prompt-driven mobile apps:
- Expo
- React Native
- TypeScript
- Expo Router
- Supabase when persistence/auth is needed
- Simple reusable component system

## Escalate from default only when necessary
Move away from Expo only if the prompt clearly requires:
- deep native SDK integration
- heavy background services
- advanced low-level device APIs
- strict platform-exclusive behavior

Otherwise, stay on the default fast path.
