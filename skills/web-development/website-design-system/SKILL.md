---
name: website-design-system
description: Create a professional website design system covering brand feel, colors, typography, spacing, components, responsive behavior, accessibility, and visual implementation rules.
version: 1.0.0
metadata:
  hermes:
    tags: [web-development, design-system, ui, ux, accessibility, responsive]
    related_skills: [website-agency-orchestrator, popular-web-designs]
---

# Website Design System

Use this skill before building UI or when the user asks to change style, brand
feel, layout, typography, or visual polish.

## Output Artifact

Create or update:

```text
docs/design-system.md
```

## Required Sections

```markdown
# Design System

## Brand Direction
## Color Palette
## Typography
## Spacing And Layout
## Components
## Imagery And Icons
## Responsive Rules
## Accessibility Rules
## Implementation Notes
```

## Design Rules

- Design for the business domain, not generic SaaS defaults.
- Prefer restrained, scannable layouts for B2B or operational tools.
- For landing pages, make the product/service obvious in the first viewport.
- Use real assets, generated images, or relevant placeholders with clear alt
  text when visuals matter.
- For generated agency projects, plan and track media with:

  ```bash
  scripts/website_agency.py media-plan --project-dir "<project dir>" --style "<image style>"
  scripts/website_agency.py media-apply --project-dir "<project dir>"
  ```

- Keep text readable on mobile; never let labels or buttons overflow.
- Use consistent buttons, cards, forms, nav, footer, FAQ, pricing, testimonial,
  and contact components.
- Avoid one-note palettes and decorative blobs/orbs.

## Using Popular Design References

If the user says "like Stripe", "like Linear", "luxury", "Airbnb style", or
similar, use `popular-web-designs` as a reference and copy the relevant tokens
into `docs/design-system.md`. Do not blindly clone a brand; adapt the design
language to the user's business.
