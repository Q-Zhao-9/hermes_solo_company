---
name: edit-section
description: Modify one website section from natural language feedback, preserving project conventions, responsive behavior, copy quality, and preview readiness.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, visual-editor, website-editing, command]
    related_skills: [website-visual-editor, website-agency-orchestrator, website-qa-deploy]
---

# Edit Section

Use this skill when the user invokes `/edit-section` or asks for a natural
language change to a specific website section.

## Workflow

1. Use `website-visual-editor` as the primary skill.
2. For generated static HTML and Next.js projects, list editable sections first:

   ```bash
   scripts/website_agency.py list-sections --project-dir "<project dir>"
   ```

3. Apply structured section edits with:

   ```bash
   scripts/website_agency.py edit-section --project-dir "<project dir>" --section "<section id>" --heading "<new heading>" --body "<new body>" --cta "<new CTA>" --request "<user request>"
   ```

   This updates the page and records revision history in
   `docs/hermes-website-state.json`.
4. Locate the target page, component, section, or WordPress/Shopify template.
5. Convert vague requests into concrete edits to layout, copy, hierarchy, CTA,
   imagery, color, spacing, or responsive behavior.
6. Keep the existing design system unless the user asks to change it.
7. Run focused validation and report the changed files or page/template.

If the requested section is ambiguous, ask one short clarifying question or make
the safest visible edit and state the assumption.
