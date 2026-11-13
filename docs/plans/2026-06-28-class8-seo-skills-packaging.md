# Class 8 SEO Skills Packaging Plan

> **For Hermes:** implement this in `hermes_solo_company` with source-only skills, installer updates, gateway allowlist wiring, and regression tests.

**Goal:** Package the remaining core Class 8 SEO teaching skills into the Hermes bot repository so they install cleanly alongside the existing Class 8 keyword research skill.

**Architecture:** Keep the reusable source of truth under `skills/class8/`, expose the skills through `modules/website_chatbot/backend/site_gateway.py` so Student Skill Studio can open/test them, and teach the installer/docs to copy them into `~/.hermes/skills/class8/...`.

**Selected skills to add:**
1. `class8/seo-audit-skill` — review-safe single-page SEO audit workflow
2. `class8/seo-brief-skill` — turn keyword research into a selected brief + handoff
3. `class8/seo-article-writer-skill` — generate one review-safe full article from the selected brief

**Why these three:** They match the main missing Class 8 workflow slices already implemented in the classroom site after keyword research: audit, brief generation, and full article writing.

## Implementation steps

### Task 1: Add the new Class 8 skill source files
- Create `skills/class8/seo-audit-skill/SKILL.md`
- Create `skills/class8/seo-brief-skill/SKILL.md`
- Create `skills/class8/seo-article-writer-skill/SKILL.md`
- Keep them student-editable, classroom-safe, and deterministic in output structure.

### Task 2: Wire the new skill ids into the reusable website chatbot gateway
- Update `modules/website_chatbot/backend/site_gateway.py`
- Extend `student_skill_allowlist`
- Add deterministic test-output helpers for the new skill ids so Student Skill Studio can validate them locally without live SEO APIs.

### Task 3: Extend repo tests and packaging metadata
- Update `modules/website_chatbot/tests/test_site_gateway_auth.py`
- Verify `/api/student/skills` lists the new skill ids
- Verify skill test runs for at least the audit, brief, and article workflows
- Update `scripts/install_easiio_modules.sh`, `modules/README.md`, and `docs/easiio-modules-install.md`

### Task 4: Validate and publish
- Run shell syntax, Python compile, and gateway tests
- Run installer dry-run and a real temp-directory install
- Run a secret scan on the touched files
- Commit and push only the Class 8 SEO packaging changes
