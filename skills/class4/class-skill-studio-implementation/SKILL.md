---
name: class-skill-studio-implementation
description: "Reusable workflow for adding a classroom Skill Studio lesson: create/update a Hermes teaching skill, add student-facing docs/examples, wire a bilingual admin-console panel, and verify local/public deployment markers."
---

# Class Skill Studio Implementation

## When to use

Use this skill when preparing a class session that teaches students how Hermes skills work, especially when the class needs:

- a concrete demo skill under `~/.hermes/skills/<class>/...`
- student-facing Markdown examples/checklists
- an admin-console or website panel that points students to the workflow
- bilingual English/Chinese UI labels or teaching hooks
- verification that the lesson assets are available locally and publicly

This workflow was extracted from the Class 4 Skill Studio implementation for the AI Solo Company class site.

## Recommended workflow

1. **Inspect the target site and existing lesson assets**
   - Identify the website root, e.g. `/mnt/c/Users/jianl/solo-company-class-site`.
   - Search/read the existing admin console files, usually:
     - `admin.html`
     - `site-auth.js`
     - `styles.css`
     - static tests such as `auth_download_static_test.py`
   - Inspect current class docs folders such as `docs/class3/` or `docs/class4/` to match naming and teaching style.

2. **Create or update the Hermes teaching skill**
   - Put the live class-specific Hermes skill under:
     ```text
     /home/jianl/.hermes/skills/<class-name>/<skill-name>/SKILL.md
     ```
   - If the classroom website is a Git repo and the user asks to check the lesson into GitHub, also commit a tracked copy under the site repo, for example:
     ```text
     <site-root>/docs/<class-name>/<skill-name>/SKILL.md
     ```
     This avoids relying on `~/.hermes/skills`, which is usually not inside the website repository.
   - Include:
     - when to use
     - required inputs
     - business/teaching rules
     - fixed output format
     - example input
     - example output style
     - student customization exercises
     - testing checklist
   - Avoid secrets, backend tokens, passwords, API keys, private URLs, and raw credentials.
   - Verify the live skill loads with `skill_view(<skill-name>)` and verify the tracked copy exists before committing.

3. **Create classroom docs/examples**
   - Use a folder like:
     ```text
     <site-root>/docs/<class-name>/
     ```
   - Good reusable files:
     - `lead-input-example.md` or task input example
     - `skill-output-before.md`
     - `skill-output-after-tone-change.md`
     - `skill-output-after-json-change.md`
     - `codex-demo-prompts.md`
     - `test-checklist.md`
   - Include a rollback reminder when students edit skills or code.

4. **Add the admin-console panel**
   - Add a visible menu item such as:
     ```text
     Skill Studio / 技能工作台
     ```
   - Add a dashboard card that opens the panel.
   - In the panel, include:
     - class overview
     - demo skill path
     - skill anatomy: user input, rules, tool calls, structured output, logs/verification
     - Codex/Hermes safe workflow
     - classroom file list
     - test/logs/rollback checklist
   - For live Skill Studio editing, add an admin-only manager area with markers such as `data-skill-studio-manager`, `data-skill-list`, `data-skill-content`, `data-skill-save`, and `data-skill-copy-prompt`.
   - Add browser JS that loads `GET api/skills`, opens `GET api/skills/file?path=...`, saves via `POST api/skills/file`, and generates a safe copy-paste prompt for prompt-based skill modification.
   - Add protected gateway endpoints in `website_chatbot/backend/site_gateway.py`, not the public chatbot API, so the static admin page can edit `SKILL.md` files only after admin login. Restrict paths to `~/.hermes/skills/**/SKILL.md` and the site docs skill-copy root; reject other filenames and path traversal.
   - Add bilingual strings in the existing i18n/translation object if the site uses one.
   - Add CSS classes for the new panel/card instead of relying on unstyled markup.

5. **Add static regression tests**
   - Extend existing static tests to check for:
     - panel/menu markers
     - translation keys
     - CSS selectors
     - docs file existence
     - skill path marker or lesson copy
   - Prefer simple marker tests for static classroom sites so future edits do not silently remove the lesson.
   - Do not make tests depend only on an absolute `~/.hermes/skills/...` path if the website repo is meant to be portable. Prefer a repo-tracked skill copy first and use the live Hermes path only as a local fallback.

6. **Verify locally**
   - Run static tests and syntax checks, for example:
     ```bash
     cd <site-root>
     python3 auth_download_static_test.py
     node --check site-auth.js
     node --check chatbot-admin/chatbot-customizer.js
     ```
   - Add a targeted marker check for the class panel, i18n keys, CSS selectors, and tracked `SKILL.md` copy before committing.
   - Remove generated Python cache files such as `__pycache__/` before staging.
   - If the site is static, use marker checks before browser checks.

7. **Verify public deployment when applicable**
   - Check the public/proxied URL for updated files, such as:
     ```text
     https://hermesproxy.easiiodev.ai/p/<site-id>/
     ```
   - Confirm the public HTML/JS/CSS contain the new markers.
   - Do not expose any secret values in final summaries.

## Student-owned Skill Studio pattern

Use this pattern when the class site needs students to edit skills safely.

- Keep the existing `admin.html#skill-studio` editor as the **teacher/master editor** only. It may edit Jian/admin master files such as `/home/jianl/.hermes/skills/**/SKILL.md` and repo-tracked template copies under the class site docs folder.
- Create a separate student page, e.g. `<site-root>/student-skill-studio.html`, instead of exposing the admin console to normal users.
- Student editing endpoints should be separate from admin endpoints. Prefer:
  ```text
  GET  /api/student/skills
  GET  /api/student/skills/file?skill_id=class4/student-lead-followup
  POST /api/student/skills/file
  POST /api/student/skills/reset
  ```
- Student APIs require login but not admin role. They must never accept arbitrary absolute paths from the browser. Accept an allowlisted `skill_id` and map it server-side to the logged-in user's sandbox.
- Store each student's editable copy under a per-user sandbox such as:
  ```text
  /home/jianl/.hermes/tools/website_chatbot/data/student_skills/<user_id>/class4/student-lead-followup/SKILL.md
  ```
- On first open, copy from the teacher template, preferably the repo-tracked class template:
  ```text
  <site-root>/docs/class4/student-lead-followup/SKILL.md
  ```
  with the live Hermes master skill as fallback only if appropriate.
- Student saves should validate YAML frontmatter, reject likely secret markers, create backups, and write only inside that student's sandbox.
- Add `POST /api/student/skills/reset` to restore that student's copy from the teacher template without affecting other students.
- The student UI should clearly say: "This edits your personal student copy only. It does not change the teacher's master skill."
- Prompt-copy text for students should refer to the safe `skill_id` and explicitly say not to modify the teacher/admin master skill. Do not show Jian's master absolute path in student prompts.
- Add a temporary-gateway API smoke test before public verification. Use a temporary auth DB and temporary `student_skills` root when possible, then verify: normal student login works, student cannot access admin `/api/skills`, student can list/open/save/reset via `/api/student/skills*`, a second student gets a separate copy, path traversal/invalid `skill_id` is rejected, and temp files are cleaned up.
- After static files change, restart the local gateway/proxy process that serves the class site and then verify public proxy markers for the new student page, updated `site-auth.js`, and updated admin copy. Do not assume public `hermesproxy.easiiodev.ai/p/<site-id>/...` reflects changes until markers are checked through the proxied URL.
- Recommended Phase 2 after the class-backend sandbox: add a student test runner and diff view before adding any local laptop agent. Use `POST /api/student/skills/test` to run the logged-in student's sandbox copy against a sample lead and return a class-safe output/checklist. Use `GET /api/student/skills/diff?skill_id=...` to compare the teacher template with that student's copy via `difflib.unified_diff`. The UI markers should include `data-student-skill-test-input`, `data-student-skill-run-test`, `data-student-skill-test-output`, `data-student-skill-load-diff`, and `data-student-skill-diff`.
- Optional later phase: add a local student Skill Agent on `127.0.0.1` for editing `~/.hermes/skills` on a student's own laptop. Do this after the class-backend sandbox and test/diff workflow work; require a pairing token, bind to loopback only, allowlist skills, and avoid arbitrary path writes.

## Implementation notes

- Use targeted `read_file`, `search_files`, `write_file`, and `patch` edits instead of shell heredocs or `sed`.
- Keep the teaching skill itself separate from the website UI. The skill is reusable; the admin panel is the class navigation layer.
- For classroom demos, make the before/after examples explicit so students can see what changed after editing the skill.
- Prefer safe workflows: inspect, test, change one layer, test again, then verify public markers.
- When implementing student Skill Studio, add static tests that ensure the student page exists, student markers are present, admin markers remain, `api/student/skills` is referenced, and the student page does not expose `/home/jianl/.hermes/skills`.

## Final response checklist

Summarize:

- skill path created/updated
- class docs folder and files
- admin/menu/dashboard changes
- exact verification commands and pass/fail result
- public URL checked, if applicable
- suggested live demo flow
