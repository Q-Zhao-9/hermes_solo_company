# Class 7 Brand Studio Implementation Plan

> **For Hermes:** implement this plan in small verified slices. Prefer marker-based static tests first, then docs/skill files, then UI wiring in `student-workspace.html`, `admin.html`, `site-auth.js`, and `styles.css`.

**Goal:** Add a Class 7 **AI Brand & Visual System** teaching slice to the AI Solo Company class site so instructors and students can turn a business idea into a usable brand brief, visual direction, prompt pack, and website-ready design system.

**Architecture:** Start with a classroom-safe static/client-side MVP. The first version should run entirely in the current site frontend with copyable prompts, demo loaders, rendered checklists, and export-ready markdown/json outputs. Treat image generation as a human-triggered Hermes workflow rather than an automatic backend dependency.

**Tech stack:** static HTML, `site-auth.js`, `styles.css`, existing auth/session flow, local markdown docs, static Python regression tests.

---

## Product scope

### MVP scope for Class 7

Build these user-visible capabilities:

1. **Brand Studio panel** in `admin.html`
2. **Student-facing Class 7 section** in `student-workspace.html`
3. **Business brief inputs**: company, audience, offer, personality, constraints
4. **Visual direction generator**: 3 directions with brand adjectives and cues
5. **Brand prompt builder**: logo / hero / social / website prompt templates
6. **Design-system draft output**: colors, typography, imagery, CTA tone, do/don't list
7. **Demo loaders** for one classroom sample business in EN + ZH
8. **Docs and teaching skill draft** for the class materials
9. **Static regression test** covering markers, docs, CSS, and JS wiring

### Phase 2 ideas

- Add real image generation workflow hooks
- Save/export the chosen direction into a website template workflow
- Add asset pack download, prompt history, and student submission review
- Connect generated design tokens into a page builder or template system

---

## Guardrails

These rules must appear in the UI, docs, or skill text:

- Brand outputs are **directional creative drafts**, not final design approval.
- Students must choose **one clear direction** instead of keeping too many options alive.
- Generated prompts should reflect business goals, not random aesthetics.
- Website application matters: every result should map back to homepage hero, sections, and social assets.
- Any mention of credentials, private client files, or model secrets must stay redacted as `[REDACTED]`.

---

## Files to modify

### Existing files to modify

- `/mnt/c/Users/jianl/solo-company-class-site/admin.html`
- `/mnt/c/Users/jianl/solo-company-class-site/student-workspace.html`
- `/mnt/c/Users/jianl/solo-company-class-site/site-auth.js`
- `/mnt/c/Users/jianl/solo-company-class-site/styles.css`

### New files to create

- `/mnt/c/Users/jianl/solo-company-class-site/class7_brand_studio_static_test.py`
- `/mnt/c/Users/jianl/solo-company-class-site/docs/class7/brand-brief-template.md`
- `/mnt/c/Users/jianl/solo-company-class-site/docs/class7/brand-brief-template-zh.md`
- `/mnt/c/Users/jianl/solo-company-class-site/docs/class7/demo-inputs.md`
- `/mnt/c/Users/jianl/solo-company-class-site/docs/class7/demo-inputs-zh.md`
- `/mnt/c/Users/jianl/solo-company-class-site/docs/class7/demo-output-example.md`
- `/mnt/c/Users/jianl/solo-company-class-site/docs/class7/demo-output-example-zh.md`
- `/mnt/c/Users/jianl/solo-company-class-site/docs/class7/design-system-example.md`
- `/mnt/c/Users/jianl/solo-company-class-site/docs/class7/design-system-example-zh.md`
- `/mnt/c/Users/jianl/solo-company-class-site/docs/class7/website-brand-integration-checklist.md`
- `/mnt/c/Users/jianl/solo-company-class-site/docs/class7/website-brand-integration-checklist-zh.md`
- `/mnt/c/Users/jianl/solo-company-class-site/docs/class7/test-checklist.md`
- `/mnt/c/Users/jianl/solo-company-class-site/docs/class7/test-checklist-zh.md`
- `/mnt/c/Users/jianl/solo-company-class-site/docs/class7/brand-visual-system/SKILL.md`

---

## Implementation phases

### Phase 1 — inspect and mirror existing class patterns

Reuse the existing class-site menu/panel pattern:

- `data-admin-panel-target="..."` and `data-admin-panel="..."`
- `data-student-panel-target="..."` and `data-student-panel="..."`
- hero card + card grid + docs list structure already used by Class 6
- marker-based static Python tests modeled after `class6_legal_compliance_static_test.py`

### Phase 2 — write the failing static test

Create a Class 7 test that checks for:

- admin/student menu markers
- brand studio panel markers
- docs file existence and expected keywords
- CSS selectors
- JS function names and data attributes
- disclaimer text about “creative direction, not final approved branding”

Run the test first and confirm failure before building the slice.

### Phase 3 — create docs and the teaching skill draft

Add the reusable classroom assets:

- brand brief template
- demo business inputs
- example output pack
- website integration checklist
- teacher/student test checklist
- `docs/class7/brand-visual-system/SKILL.md`

### Phase 4 — build the Brand Studio UI

Student panel should support:

- filling the brief
- loading classroom demo input
- generating direction cards
- generating prompt pack
- generating design-system markdown
- copying outputs for Hermes / image tools / website work

Admin panel should support:

- teacher overview / lesson flow
- docs links
n- same prompt builder for live demos
- brand workflow checklist tied back to website implementation

### Phase 5 — wire frontend JS behavior

Implement a self-contained client-side workflow in `site-auth.js`:

- `initClass7BrandStudio()`
- state normalization for inputs
- demo loaders (EN + ZH)
- deterministic direction generation from selected tone + audience
- prompt-pack markdown builder
- design-system markdown/json builder
- copy/export helpers
- language toggle (optional but preferred to match Class 6)

### Phase 6 — verify

Run:

```bash
cd /mnt/c/Users/jianl/solo-company-class-site
python3 class7_brand_studio_static_test.py
python3 -m py_compile site-auth.js  # replace with JS-safe verification approach if needed
```

Since `py_compile` is not valid for JS, use an actual JS parse check or project test command instead. At minimum run the Python static test and a Node syntax parse check on `site-auth.js` if Node is available.

---

## MVP UI markers to include

Student panel markers:

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

Admin panel markers:

- `data-admin-panel-target="brand-studio"`
- `data-admin-panel="brand-studio"`
- `data-admin-brand-studio-panel`
- `data-admin-brand-doc-list`
- `data-admin-brand-phase-plan`

---

## Definition of done

Class 7 is ready for the next iteration when:

- implementation plan file exists
- static test passes
- all Class 7 docs exist
- `docs/class7/brand-visual-system/SKILL.md` exists with reusable workflow instructions
- student workspace contains a visible Brand Studio section
- admin console contains a teaching/demo Brand Studio section
- `site-auth.js` can initialize the panel without console errors
- outputs can be copied and reused in the website workflow
