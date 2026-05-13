---
name: change-style
description: Change a website's visual style, brand feeling, color palette, typography, spacing, layout density, or component treatment consistently across the site.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, design-system, visual-editor, command]
    related_skills: [website-design-system, website-visual-editor, website-agency-orchestrator]
---

# Change Style

Use this skill when the user invokes `/change-style` or asks to make a website
feel more luxury, modern, playful, enterprise, local-business, premium, simple,
or otherwise visually different.

## Workflow

1. Use `website-design-system` to translate the requested feeling into concrete
   colors, type, spacing, button, card, icon, and layout rules.
2. For generated static HTML and Next.js projects, apply supported palette
   changes with:

   ```bash
   scripts/website_agency.py change-style --project-dir "<project dir>" --preset luxury
   ```

   Supported presets: `professional`, `luxury`, `modern`, `warm`. You can also
   pass `--accent`, `--ink`, or `--surface` for explicit colors. This records
   revision history in `docs/hermes-website-state.json`.
3. Use `website-visual-editor` to apply any deeper custom style edits to real
   files.
4. Preserve accessibility, contrast, responsive behavior, and brand consistency.
5. Avoid one-section-only styling unless the user specifically asks for it.
6. Run build or visual checks where available.

State the design assumptions briefly and list the key files changed.
