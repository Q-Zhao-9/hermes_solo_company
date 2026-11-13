---
name: mobile-ui-image-analyzer
description: "Analyze mobile app screenshots, mockups, wireframes, and design images to extract reusable UI patterns, design tokens, navigation structure, component inventory, and implementation guidance for Expo/React Native, Flutter, SwiftUI, or Jetpack Compose."
license: Proprietary. LICENSE.txt has complete terms
---

# Mobile UI Image Analyzer

## When to use
Use this skill when the user provides one or more mobile UI images and wants Hermes to:
- understand the design system
- learn the UI style from screenshots/mockups
- recreate the UI in code
- extract reusable tokens and components
- compare design options across multiple app screens
- decide which mobile stack best fits the visual/system demands

Typical triggers:
- "Analyze this app screenshot"
- "Learn the UI from this image and build the app"
- "Extract the design system from these screens"
- "What components and tokens are in this mobile design?"
- "Use this mockup as the app design direction"

## Goal
Turn raw mobile design images into a structured implementation brief that downstream build skills can use directly.

The analyzer should transform screenshots/mockups into:
1. design summary
2. navigation pattern
3. visual hierarchy notes
4. design tokens
5. component inventory
6. interaction pattern notes
7. responsive/adaptive assumptions
8. stack-specific implementation notes

## Inputs supported
- single screenshot
- multiple screenshots from one app flow
- wireframes
- polished product mockups
- reference images from existing apps
- light mode and dark mode screens

## Required analysis workflow

### Phase 1 — Identify image role
For each image, determine whether it is primarily:
- onboarding / landing
- home/dashboard
- feed/list
- detail page
- form/input flow
- checkout/payment
- profile/settings
- modal/sheet/dialog state
- tabbed navigation shell
- empty/loading/error state

If uncertain, state the best guess.

### Phase 2 — Structural UI analysis
Describe the visible structure objectively:
- top app bar / nav bar behavior
- bottom tab bar / bottom nav behavior
- floating action button presence
- screen sections and content grouping
- column/card/list structure
- content density
- spacing rhythm
- dominant focal point / CTA placement

Do not jump straight to implementation. First describe what is visibly present.

### Phase 3 — Design token extraction
Extract the likely design system, including:
- primary colors
- secondary/accent colors
- neutrals/backgrounds
- typography scale
- corner radius patterns
- shadow/elevation patterns
- spacing scale
- border/divider usage
- icon style
- imagery/illustration style

If exact values are uncertain, estimate ranges and label them as approximations.

### Phase 4 — Component inventory
List reusable UI elements visible in the design, such as:
- buttons
- cards
- chips/tags
- list rows
- nav bars
- tab bars
- segmented controls
- search bars
- forms/inputs
- toggles
- progress indicators
- sheets/modals
- banners/alerts
- avatars
- metric/stat blocks

For each component, note:
- its role
- its visual style
- whether it appears reusable across screens

### Phase 5 — Interaction pattern analysis
Infer likely interaction behaviors from the UI:
- tab navigation
- push/drill-down navigation
- modal presentation
- bottom sheets
- inline filtering
- card tap actions
- CTA hierarchy
- gesture assumptions where visually implied

Make it clear when behavior is inferred rather than directly visible.

### Phase 6 — Multi-screen consistency analysis
When multiple images are provided, compare them for:
- consistency of spacing
- consistency of typography
- consistency of color system
- repeated components
- navigation continuity
- state variations (default/empty/loading/detail/form)

Identify:
- stable app-wide patterns
- one-off exceptions
- likely reusable primitives

### Phase 7 — Implementation guidance
Translate the design into build guidance for:
- Expo / React Native
- Flutter
- SwiftUI
- Jetpack Compose

Focus on:
- what should become tokens
- what should become shared primitives
- what should become composed sections
- what should stay screen-specific

## Required output format
When using this skill, structure the output as follows:

### 1. Design summary
- short visual description of the app/style

### 2. Screen role
- what this screen or set of screens appears to represent

### 3. Navigation pattern
- top-level navigation and likely movement model

### 4. Visual hierarchy
- what the eye is drawn to first, second, third

### 5. Design tokens
- color palette
- typography
- spacing
- radius
- elevation/shadows

### 6. Reusable component inventory
- list of components with notes

### 7. Interaction assumptions
- likely behaviors implied by the UI

### 8. Cross-screen system notes
- repeated patterns and consistency notes

### 9. Build translation notes
- Expo / React Native guidance
- Flutter guidance
- SwiftUI guidance
- Jetpack Compose guidance

### 10. Suggested next step
- whether to route to stack selector, orchestrator, or a specific build skill

## Stack-fit heuristics from images
Use image evidence to help downstream routing:
- **standard business app UI** → Expo often sufficient
- **highly branded/custom visual system** → Flutter often strong fit
- **very Apple-native visual language** → SwiftUI may fit best
- **very Android-native/material/system-heavy UI** → Jetpack Compose may fit best

This skill does not have to choose the final stack, but it should surface clues that help the router/orchestrator decide.

## Image-analysis checklist
Always try to capture:
- light/dark mode assumption
- main navigation type
- card/list/form dominance
- CTA color and prominence
- spacing tightness vs airiness
- typography contrast
- one-hand mobile ergonomics hints
- iconography style
- whether the design feels system-native or brand-native
- whether the UI depends on custom illustrations/graphics

## Good implementation advice examples
- "Create a shared `AppCard` primitive with 20-24px radius and soft shadow"
- "Use one primary CTA button style and one secondary ghost style"
- "Extract a 4/8/12/16/24 spacing scale"
- "Model the header + subtitle + search block as a reusable screen hero section"
- "Use a tokenized semantic color set instead of hardcoding each screen"

## Common pitfalls
- describing only aesthetics without extracting reusable structure
- hardcoding every visual detail instead of identifying system patterns
- assuming interaction behaviors too confidently from a static image
- failing to separate reusable components from one-off hero sections
- ignoring cross-screen inconsistencies in multi-image sets
- stopping at analysis without giving build-oriented output

## Final rule
This skill should produce outputs that a downstream mobile build skill can immediately use to recreate the design language with reusable code, not just a vague visual description.
