---
name: mobile-app-qa-review
description: "Review a generated or in-progress mobile app against the original prompt, design references, navigation flow, UI consistency, platform expectations, and MVP completeness, then produce a concrete fix list and ship-readiness verdict."
license: Proprietary. LICENSE.txt has complete terms
---

# Mobile App QA Review

## When to use
Use this skill after a mobile app has been scaffolded, partially implemented, or completed, and the goal is to evaluate quality before handoff, demo, iteration, or release.

Use it for apps built with:
- Expo / React Native
- Flutter
- SwiftUI
- Kotlin / Jetpack Compose

Typical triggers:
- "Review this mobile app build"
- "Compare the app to the mockups"
- "QA this MVP"
- "Does this app match the prompt?"
- "Check navigation, consistency, and completeness"
- "Is this ready to demo or ship?"

## Goal
Turn vague app review into a structured QA process that checks:
1. prompt/spec alignment
2. design/image alignment
3. navigation correctness
4. UI consistency
5. MVP completeness
6. platform-fit issues
7. technical verification evidence
8. prioritized fix recommendations

## Inputs to review
Gather as many of these as available:
- original product prompt
- screenshots/mockups/reference images
- chosen stack/framework
- current source code/project path
- preview/build output
- app screenshots or screen recordings
- known limitations or incomplete areas

If some are missing, review what is available and clearly label review gaps.

## Review workflow

### Phase 1 — Reconstruct the intended target
Before judging the app, summarize:
- target users
- core promise
- core user flow
- must-have features
- deferred features
- expected screens
- expected design direction

Do not review against an unstated standard. Review against the intended product.

### Phase 2 — Determine evidence available
Identify what evidence exists:
- source code inspection
- preview URL or simulator screenshots
- image/mockup references
- build/test/lint output
- user-provided notes

Mark confidence level accordingly:
- high confidence if source + visuals + build verification exist
- medium if source + partial visuals exist
- low if only screenshots or only source are available

### Phase 3 — Prompt/spec alignment review
Check whether the implemented app matches the requested product.

Look for:
- missing must-have features
- extra features that distract from MVP
- wrong screen structure
- broken core user flow
- incorrect terminology or domain modeling
- mismatch between target users and implemented UX

### Phase 4 — Design alignment review
If design images/mockups exist, compare the implementation against them.

Review:
- layout structure
- spacing rhythm
- hierarchy
- color usage
- typography feel
- component shapes/radius/shadows
- CTA prominence
- nav pattern consistency
- dark/light assumptions

Do not require pixel-perfect matching unless explicitly requested. By default, judge whether the implementation captures the same reusable design language.

### Phase 5 — Navigation and flow review
Check the implemented flow end-to-end:
- app launch experience
- primary entry point
- main navigation structure
- tab/stack/sheet transitions
- back navigation behavior
- dead ends
- orphan screens
- broken CTA destinations
- confusing flow order

The main user journey should be demonstrable quickly and cleanly.

### Phase 6 — UI consistency review
Inspect consistency across screens:
- spacing
- typography scale
- color semantics
- button styles
- input styles
- card/list styles
- icon usage
- headers/section structure
- empty/loading/error states

Flag places where the app looks assembled screen-by-screen instead of driven by a shared design system.

### Phase 7 — Platform expectation review
Check whether the app feels appropriate for its chosen stack/platform.

Examples:
- Expo/React Native: route structure, reusable components, practical cross-platform patterns
- Flutter: strong theme consistency, reusable widgets, clean state/layout composition
- SwiftUI: native iOS navigation and control usage, Apple-like interaction patterns
- Jetpack Compose: coherent Material/native Android structure, predictable state/navigation flow

Flag mismatches such as:
- iOS app that feels Android-like in the wrong way
- Android app that ignores platform expectations
- cross-platform app with inconsistent behavior between screens

### Phase 8 — MVP completeness review
Judge whether the app is complete enough for its current goal:
- demo-ready
- review-ready
- internal testing ready
- production-hardened

Check for:
- missing screens in the main flow
- missing empty/loading/error states
- placeholder data or dead mock buttons
- obvious incomplete sections
- no clear happy path

### Phase 9 — Technical verification review
When code/project access exists, verify with appropriate evidence:
- project structure sanity
- typecheck/lint/build status if available
- routing structure
- presence of reusable primitives/tokens/theme
- obvious hardcoded content or duplication
- assets/config issues

Do not rely only on visual inspection when code/build evidence is available.

### Phase 10 — Prioritized fix synthesis
Convert observations into a practical fix queue.

Group issues into:
- blocking issues
- important polish issues
- optional future improvements

Each issue should include:
- what is wrong
- why it matters
- affected screen/flow
- recommended fix direction

## Required output format
When using this skill, structure the review as:

### 1. Review target summary
- app purpose
- target users
- chosen stack
- evidence reviewed
- confidence level

### 2. Overall verdict
- on track / needs revision / not ready
- one-paragraph summary

### 3. Prompt alignment
- matched well
- missing/wrong items

### 4. Design alignment
- where the implementation matches
- where it diverges

### 5. Navigation and user flow
- good paths
- broken/confusing paths

### 6. UI consistency
- reusable-system strengths
- inconsistencies found

### 7. MVP completeness
- what is complete
- what is still missing

### 8. Technical quality signals
- build/test/lint/project-structure notes

### 9. Prioritized issues
- P0 blockers
- P1 important fixes
- P2 polish/future improvements

### 10. Recommended next step
- fix and re-review
- proceed to demo
- proceed to internal test
- proceed to release hardening

## Severity guidance
Use these severity bands:
- **P0 blocker**: core flow broken, must-have feature missing, navigation dead end, build failure, obviously wrong stack/platform behavior
- **P1 important**: major inconsistency, weak design match, missing states, confusing interaction, incomplete but demoable flow
- **P2 polish**: copy tweaks, spacing refinement, visual polish, minor consistency cleanup

## Evidence-based review principles
- Do not invent screens or requirements the prompt never asked for
- Do not declare ship-readiness without build/flow evidence
- Distinguish between missing evidence and actual failure
- Label assumptions clearly
- Prefer concrete examples over vague judgments

## Good QA findings examples
- "P0: The primary CTA on Home opens no destination, so the core booking flow is non-functional."
- "P1: The settings screen uses a different spacing and button style system than the rest of the app, suggesting shared tokens were not applied."
- "P1: The implementation captures the card-based visual language from the mockup, but the typography scale is flatter, reducing hierarchy."
- "P2: Add empty states for list screens so the app feels complete in demo conditions."

## Common pitfalls
- reviewing aesthetics only and missing broken flows
- reviewing code only and missing UI/UX drift
- demanding pixel perfection when the request only called for stylistic matching
- ignoring platform conventions
- failing to separate blockers from polish
- saying "looks good" without evidence-based checks

## Final rule
This skill should produce a concrete, build-oriented QA verdict that tells the user whether the mobile app is actually ready for its intended purpose and exactly what to fix next if it is not.
