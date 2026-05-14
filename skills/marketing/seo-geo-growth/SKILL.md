---
name: seo-geo-growth
description: Generate SEO and AI answer-engine optimization plans for marketing campaigns: keyword clusters, search-intent pages, blog briefs, schema recommendations, internal links, and GEO tasks.
version: 1.0.0
metadata:
  hermes:
    tags: [marketing, seo, geo, ai-seo, blog, schema, search-intent]
    category: marketing
    related_skills: [marketing-agency-orchestrator, marketing-strategy, content-studio, website-seo-content, seo-optimize]
---

# SEO GEO Growth

Use this skill when the user asks for SEO, AI SEO, GEO, blog strategy,
keyword clusters, content briefs, search intent, schema, internal links, or
AI answer-engine discoverability.

Focus on buyer search intent and answer-engine clarity, not keyword stuffing.

## Helpers

Create an SEO/GEO plan:

```bash
scripts/marketing_agency.py generate-seo-plan \
  --project-dir "<project dir>" \
  --focus "<product category or offer>" \
  --pages 6 \
  --region "<market>"
```

Generate blog briefs:

```bash
scripts/marketing_agency.py generate-blog-briefs \
  --project-dir "<project dir>" \
  --count 4 \
  --intent commercial
```

## Output Quality Bar

SEO/GEO plans must include:

- keyword clusters
- search intent
- buyer questions
- page plan
- schema recommendations
- AI answer-engine recommendations
- internal linking plan
- technical SEO tasks

Blog briefs must include:

- title
- slug
- intent
- primary and secondary keywords
- meta description
- outline
- AI answer summary
- schema
- internal links

All outputs are review-ready drafts. Publishing website or blog content requires
explicit approval.
