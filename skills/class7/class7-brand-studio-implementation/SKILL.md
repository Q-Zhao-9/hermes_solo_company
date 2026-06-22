---
name: class7-brand-studio-implementation
description: Reusable workflow for implementing or extending Class 7 AI Brand & Visual System / Brand Studio on Jian's AI Solo Company class site, including plan-first docs, static-test-first validation, student/admin UI, and website-integration outputs.
---

# Class 7 Brand Studio Implementation

## When to use

Use this skill when preparing or extending **Class 7 — AI Brand & Visual System** for the AI Solo Company class site, especially when the work includes:

- student-facing Brand Studio workspace UI
- admin/teacher Brand Studio console UI
- class docs, demo inputs, and design-system examples
- static regression tests for Class 7 markers
- prompt-pack builders for logo / hero / social / website assets
- lightweight design-system generation tied back to website implementation

Primary site root observed:

```text
/mnt/c/Users/jianl/solo-company-class-site
```

## Core class constraints

Do not let Class 7 drift into generic design exploration. The lesson should stay focused on:

- converting a business brief into a brand brief
- generating **three clear directions**
- forcing a **single chosen direction**
- turning that direction into a prompt pack
- turning that direction into a **website-ready design system**
- mapping outputs back to homepage hero, CTA, sections, and social assets

Important classroom boundary language should stay explicit:

- this is **creative direction**
- this is **not final approved branding**
- students should not keep endless options alive
- website application matters more than aesthetic brainstorming alone

## Recommended workflow

1. **Inspect existing class patterns before editing**
   - Read:
     - `student-workspace.html`
     - `admin.html`
     - `site-auth.js`
     - `styles.css`
   - Inspect nearby class slices, especially Class 6, because it already models:
     - paired student/admin panels
     - docs lists
     - helper-card / hero-card layout
     - static-test-first conventions
   - Reuse existing menu and panel markers rather than inventing a new navigation pattern.

2. **Write the implementation plan first**
   - Create a plan file such as:
     ```text
     docs/plans/2026-06-15-class7-brand-studio-implementation-plan.md
     ```
   - Include:
     - product scope
     - files to modify
     - files to create
     - guardrails
     - MVP UI markers
     - definition of done
   - This is useful because the user often wants class materials, tools, and UI built together, not in isolation.

3. **Use static-test-first before implementation**
   - Create a dedicated test such as:
     ```text
     class7_brand_studio_static_test.py
     ```
   - Make it fail first by asserting markers in:
     - `student-workspace.html`
     - `admin.html`
     - `site-auth.js`
     - `styles.css`
     - `docs/class7/*`
   - Recommended student markers:
     - `data-student-panel-target="brand-studio"`
     - `data-student-panel="brand-studio"`
     - `data-student-brand-studio-panel`
     - `data-class7-brand-form`
     - `data-class7-demo-load`
     - `data-class7-generate-directions`
     - `data-class7-generate-prompt-pack`
     - `data-class7-generate-design-system`
     - `data-class7-direction-output`
     - `data-class7-prompt-pack-output`
     - `data-class7-design-system-output`
   - Recommended admin markers:
     - `data-admin-panel-target="brand-studio"`
     - `data-admin-panel="brand-studio"`
     - `data-admin-brand-studio-panel`
     - `data-admin-brand-doc-list`
     - `data-admin-brand-phase-plan`
   - Recommended CSS markers:
     - `.brand-studio-hero`
     - `.brand-studio-grid`
     - `.brand-direction-card`
     - `.brand-prompt-pack`
     - `.brand-design-system-card`
     - `.brand-chip-list`

4. **Create docs before or alongside UI**
   - Recommended files:
     - `docs/class7/brand-brief-template.md`
     - `docs/class7/brand-brief-template-zh.md`
     - `docs/class7/demo-inputs.md`
     - `docs/class7/demo-inputs-zh.md`
     - `docs/class7/demo-output-example.md`
     - `docs/class7/demo-output-example-zh.md`
     - `docs/class7/design-system-example.md`
     - `docs/class7/design-system-example-zh.md`
     - `docs/class7/website-brand-integration-checklist.md`
     - `docs/class7/website-brand-integration-checklist-zh.md`
     - `docs/class7/test-checklist.md`
     - `docs/class7/test-checklist-zh.md`
     - `docs/class7/brand-visual-system/SKILL.md`
   - The docs should support both classroom teaching and UI-linked references.

5. **Add the student Brand Studio slice**
   - Add a left-nav item in `student-workspace.html`:
     ```html
     data-student-panel-target="brand-studio"
     ```
   - Add a dashboard/feature card pointing to the same target.
   - Add a full student panel section such as:
     ```html
     <section id="student-panel-brand-studio" ... data-student-brand-studio-panel>
     ```
   - Include:
     - class overview
     - brand brief form
     - demo-load buttons for EN / ZH
     - generate-directions button
     - generate-prompt-pack button
     - generate-design-system button
     - copy actions for outputs
     - links to the Class 7 docs
   - Keep the student copy explicit that they must choose one direction before moving to prompts/design system.

6. **Add the admin/teacher Brand Studio slice**
   - Add a matching nav item in `admin.html`:
     ```html
     data-admin-panel-target="brand-studio"
     ```
   - Add a dashboard card.
   - Add a full admin panel such as:
     ```html
     <section id="admin-panel-brand-studio" ... data-admin-brand-studio-panel>
     ```
   - Include:
     - lesson framing
     - same brief and generator flow for live demo use
     - docs list
     - teacher talk track
     - prompt-pack and design-system output panels
   - The admin panel should emphasize the teaching sequence: brief → directions → one winner → website integration.

7. **Wire panel behavior in `site-auth.js` with a frontend MVP**
   - For the first version, keep it frontend-only and deterministic.
   - Recommended functions/patterns:
     - `initClass7BrandStudio()`
     - demo library object for EN / ZH
     - per-panel state via `WeakMap`
     - form-state reader/writer helpers
     - `buildClass7BrandDirections(...)`
     - `buildClass7PromptPack(...)`
     - a markdown builder for the design system
     - render helper for direction cards and outputs
     - clipboard-copy helper
   - Initialize the panel from both:
     - `initStudentWorkspace()`
     - `initAdmin()`
   - Keep state panel-local so student and admin panels do not leak state into each other.

8. **Use a single selected direction model**
   - The generator should produce three direction cards.
   - The UI should let the user pick one direction, then use that selected direction to build:
     - prompt pack
     - design system
   - Avoid “generate everything at once with no winner” because it weakens the class outcome.

9. **Add CSS using the existing class-site visual language**
   - Use existing hero/card/grid patterns instead of introducing a new site-wide design system.
   - Good selectors:
     - `.brand-studio-hero`
     - `.brand-studio-boundary-card`
     - `.brand-studio-grid`
     - `.brand-studio-form`
     - `.brand-direction-output`
     - `.brand-direction-card`
     - `.brand-prompt-pack`
     - `.brand-design-system-card`
     - `.brand-chip-list`
   - Add a mobile breakpoint that collapses the grids to one column.

10. **Verify with both static test and JS syntax check**
   - Recommended commands:
     ```bash
     cd /mnt/c/Users/jianl/solo-company-class-site
     python3 class7_brand_studio_static_test.py
     node --check site-auth.js
     ```
   - If the static test fails after implementation, inspect whether the mismatch is in the test string rather than the UI.

## Important implementation findings

### 1. HTML entity mismatch can break exact-marker tests

A real failure happened because the UI contained:

```html
Class 7 / AI Brand &amp; Visual System
```

while the static test expected:

```text
Class 7 / AI Brand & Visual System
```

If the test reads raw HTML, assert the escaped form actually present in the file.

### 2. Avoid duplicate function names in `site-auth.js`

A real implementation bug occurred when one function name was used for both:
- a markdown builder
- and a click-handler / panel action

For example, avoid reusing a name like:

```text
buildClass7DesignSystem
```

for two different purposes. Use a clear split such as:
- `buildClass7DesignSystemMarkdown(...)`
- `generateClass7DesignSystem(panel)` or equivalent

This prevents accidental recursion / collisions and makes the code easier to reason about.

### 3. If a static test expects a doc path literal in JS, include a stable constant

A real test failure happened because the test expected:

```text
docs/class7/demo-inputs.md
```

to appear in `site-auth.js`, but the JS used only hardcoded demo objects and never referenced the path. A simple durable fix is to keep a small constant map such as:

```js
const class7BrandDemoDocs = {
  en: 'docs/class7/demo-inputs.md',
  zh: 'docs/class7/demo-inputs-zh.md',
};
```

This both documents the source files and satisfies marker-based test expectations.

### 4. Static-test-first works well for class-site slices

For these classroom features, the proven sequence is:
1. write plan
2. write failing static test
3. create docs/skill files
4. add student/admin UI
5. add JS/CSS wiring
6. rerun static test + syntax check

This keeps class docs, UI, and JS in sync.

### 5. Do one browser check against the real running site, not only `file://`

A real implementation finding was that the Brand Studio panel could look present in HTML while still not be functionally initialized in the running app.

Use the running local site (for this project, typically the gateway-served workspace such as `http://127.0.0.1:8020/student-workspace.html`) for a lightweight browser pass.

Check at minimum:
- the Brand Studio nav target opens the panel
- the panel root exists: `data-student-brand-studio-panel`
- the init-ready flag is set after JS boot: `data-class7-brand-ready` / `dataset.class7BrandReady`
- demo-load buttons actually populate the brief form
- generate-directions creates 3 cards
- selecting a direction unlocks prompt-pack / design-system / website-workflow generation

If the panel exists but the ready flag remains unset and buttons do nothing, inspect the init path rather than the markup first.

### 6. Brand Studio may need an explicit top-level init call

A real browser-test finding was that Class 7 markup could be present while `initClass7BrandStudio()` was not reliably taking effect from the existing workspace boot path.

A durable fix is to ensure Class 7 is initialized in the main page init sequence, not only indirectly through a narrower branch. In practice, adding an explicit top-level call near the other student-page init calls is a good safeguard, for example alongside:
- `initStudentSkillStudio()`
- `initStudentWorkspace()`
- other student feature initializers

After adding this, re-check the running site and confirm the panel reports ready state before relying on static-test success.

### 6b. The running student workspace may execute `student-workspace-page.js`, not `site-auth.js`

A real root-cause investigation found that the live student workspace page loaded:

```html
<script src="student-workspace-page.js" defer></script>
```

rather than using `site-auth.js` directly for the student-side runtime.

That means a Class 7 change can appear correct in:
- `student-workspace.html`
- `site-auth.js`
- static regression tests

while still being broken in the actual running student workspace if the same logic was not copied or ported into:

```text
student-workspace-page.js
```

When browser testing shows:
- the Brand Studio panel exists,
- `dataset.class7BrandReady` stays unset,
- and button clicks do nothing,

check which script the live page really loads before changing more logic. For the student workspace, patch `student-workspace-page.js` and add `initClass7BrandStudio()` inside that page’s `initStudentWorkspace()` path if needed.

### 7. Website workflow output should use the direction object's `angle` field

A real bug appeared in the generated website workflow output as:

```text
Positioning angle: undefined
```

Root cause: the direction objects created by `buildClass7BrandDirections(...)` store the positioning summary in `direction.angle`, but the workflow template referenced `direction.positioning`.

When building website-application output, use:
- `direction.angle`

and re-check every copy section that references the selected positioning, not just the header block.

### 8. If you add website-workflow output, update both state shape and copy routing

A real implementation pass added a new output type for website workflow. Two easy-to-miss breakpoints showed up:

1. panel state must actually store the workflow text, for example a field like:
   - `class7BrandStudioState.websiteWorkflow`
2. the copy helper must know how to return the correct text for each output type, not just directions / prompt pack / design system

A durable pattern is to keep copy routing in a single mapping object, e.g. `textByType`, so adding `workflow` does not require brittle condition chains in multiple places.

Symptoms when this is missed:
- workflow visibly renders but copy button returns empty text
- one output type works while another silently copies the wrong section
- state looks complete except the new field was never initialized

### 9. Exact-marker doc tests may depend on raw markdown heading case

A real static-test compatibility issue came from the checklist doc heading needing to be exactly:

```md
## homepage hero
```

rather than a title-cased variant.

If a regression test reads raw markdown and expects an exact heading literal, preserve the exact casing and spacing present in the test contract. For this Class 7 slice, treat heading text in `docs/class7/website-brand-integration-checklist.md` as part of the interface.

## Final response checklist

Summarize:

- plan file created
- static test file created
- docs created
- student/admin panel additions
- JS/CSS additions
- exact verification commands and pass/fail result
- whether the implementation is frontend-only MVP or has backend integrations
