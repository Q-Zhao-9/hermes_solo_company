---
name: website-visual-editor
description: Translate natural-language website edit requests into safe project file changes, including section edits, style changes, mobile improvements, content revisions, and preview refreshes.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, visual-editor, revisions, ux, codex]
    related_skills: [nextjs-site-builder, static-html-site-builder, website-design-system, hermes-proxy-server]
---

# Website Visual Editor

Use this skill when the user asks for visual or content changes such as:

- "make the hero more luxury"
- "change the CTA"
- "add a pricing table"
- "make mobile better"
- "make it look more modern"
- "add testimonials"

## Edit Workflow

1. Identify the active site/project and page.
2. Locate the component, section, or HTML block.
3. Translate the request into specific file edits.
4. Preserve unrelated code.
5. Run formatting/build checks when available.
6. Refresh preview and return the updated public URL.

## Mapping Examples

- "More luxury": calmer palette, larger whitespace, premium typography,
  restrained imagery, less clutter.
- "More trustworthy": proof, certifications, testimonials, clearer contact
  details, privacy/security copy.
- "Better mobile": simplify columns, reduce hero height, check button wrapping,
  increase tap target spacing.
- "Stronger CTA": clearer verb, repeated CTA, nearby proof, reduced competing
  actions.

If the request is ambiguous but low risk, make the most reasonable improvement
and summarize what changed.
