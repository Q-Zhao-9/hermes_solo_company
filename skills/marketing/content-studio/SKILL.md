---
name: content-studio
description: Generate review-ready marketing content drafts from approved strategy and campaign context: LinkedIn posts, X threads, SEO blog briefs, YouTube scripts, email drafts, Discord announcements, and platform adaptations.
version: 1.0.0
metadata:
  hermes:
    tags: [marketing, content, social-media, linkedin, x, blog, email, youtube]
    category: marketing
    related_skills: [marketing-agency-orchestrator, create-campaign, social-calendar, website-seo-content, youtube-content, xurl, himalaya]
---

# Content Studio

Use this skill when the user asks Hermes to create marketing content, social
posts, threads, blog briefs, video scripts, email copy, community announcements,
or platform-specific adaptations.

Do not generate random posts. Generate from campaign context:

```text
campaign objective -> theme -> funnel stage -> channel format -> draft -> review
```

## Helper

```bash
scripts/marketing_agency.py generate-posts \
  --project-dir "<project dir>" \
  --channels "LinkedIn,X,SEO blog,Email,YouTube demos" \
  --count 1 \
  --stage consideration
```

Use `--theme` when the user asks for a specific angle:

```bash
scripts/marketing_agency.py generate-posts --project-dir "<project dir>" --theme "Operational ROI" --channels "LinkedIn,X"
```

## Supported Draft Types

- LinkedIn thought leadership post
- X/Twitter short thread
- SEO blog/article brief
- YouTube demo script outline
- Email nurture message
- Discord/community announcement
- generic platform-native social post

## Approval Rule

All content is draft-only. Do not post, email, reply, schedule, or run ads
without explicit approval.
