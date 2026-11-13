---
name: short-video-content-factory
description: Generate short-form video ideas, hooks, scripts, storyboards, captions, repurposing copy, and publishing calendars from a business offer, webpage, FAQ, blog post, case study, or course lesson. Designed for Class 10 AI short-video production teaching and fast multi-platform reuse across YouTube Shorts, TikTok, Instagram Reels, and LinkedIn.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [video, shorts, reels, tiktok, youtube-shorts, linkedin, content-repurposing, class10, education]
    related_skills: [ai-video-from-script]
---

# Short Video Content Factory

Use this skill when the user wants to turn a website page, service description, FAQ, course lesson, blog post, case study, or business idea into short-form video content that can be reused across multiple platforms.

This skill is optimized for Class 10 of the AI Solo Company bootcamp: AI short-video production and multi-platform reuse.

## Core outcomes

Produce a review-ready package that can include:

- 10 short video topics
- 10 hooks
- 3 ready-to-produce scripts in different lengths
- 1 storyboard / shot list
- captions or subtitle draft
- platform-specific titles and captions
- a 2-week publishing calendar
- optional prompts for AI video or avatar tools

## Default assumptions

If the user does not specify otherwise, assume:

- audience: business decision-makers or prospective customers
- primary formats: YouTube Shorts, TikTok, Instagram Reels
- secondary format: LinkedIn short professional video
- durations: 15s, 30s, 60s
- style: clear, practical, mobile-first, high-retention
- goal: attract attention, explain value quickly, and drive inquiry or click-through

## Inputs to collect or infer

Gather as many as possible from the user’s material before asking questions.

- business name
- product or service
- audience
- source material: homepage, service page, FAQ, article, notes, transcript, lesson plan
- desired platform(s)
- language
- tone: professional, educational, founder-led, energetic, premium, friendly
- CTA: book a call, message us, visit website, register, download, learn more
- whether the user wants:
  - content only
  - storyboard package
  - AI-video prompts
  - avatar video script
  - editing handoff

If key context is missing but inferable from supplied text, infer it and continue.

## Output modes

### Mode A — Content pack only
Use when the user wants ideas and scripts fast.

Return:
- 10 topics
- 10 hooks
- 3 scripts
- platform caption suggestions
- 2-week calendar

### Mode B — Production pack
Use when the user wants to actually make a sample video.

Return:
- 10 topics
- 10 hooks
- 3 scripts
- 1 storyboard / shot list
- captions draft
- visual instructions
- editing notes
- platform copy
- 2-week calendar

### Mode C — Tool handoff pack
Use when the user wants prompts for external video tools.

Return everything in Mode B, plus:
- image-to-video or text-to-video prompts
- avatar video script variant
- voiceover script
- scene-by-scene tool handoff notes

## Recommended workflow

### Step 1 — Understand the source material
Extract:
- top customer pain point
- core promise or transformation
- proof or credibility
- CTA
- repeatable themes for series content

Useful theme buckets:
- FAQ answers
- mistakes to avoid
- myths vs truth
- before/after
- mini case study
- founder insight
- tool walkthrough
- checklist / framework

### Step 2 — Generate 10 video topics
Each topic should be short, concrete, and platform-friendly.

Good format examples:
- 3 mistakes businesses make when ...
- Before you buy ..., know this
- The fastest way to improve ...
- Why most people fail at ...
- What clients really ask about ...

Avoid vague topics.

### Step 3 — Generate 10 hooks
Hooks should be optimized for the first 1–3 seconds.

Preferred hook styles:
- contrarian
- curiosity
- problem statement
- warning
- quick win
- proof/result
- mistake pattern

Examples:
- Most businesses are doing this completely wrong.
- Before you pay for this, watch this first.
- If you want more leads, fix this one thing.
- Nobody tells you this about AI websites.

### Step 4 — Generate 3 production-ready scripts
Always produce three versions:

1. 15-second punchy version
2. 30-second balanced version
3. 60-second explainer version

Each script should include:
- Hook
- Problem
- Solution or insight
- CTA

Format:

```markdown
## Script 1 — 15 seconds
Hook:
Voiceover:
On-screen text:
CTA:
```

Keep sentences short and spoken-language friendly.

### Step 5 — Create a storyboard or shot list
For at least one script, produce a scene table:

| Scene | Time | Voiceover | On-screen text | Visual | Asset type | Notes |
|---|---:|---|---|---|---|---|

Asset types can include:
- talking head
- avatar
- screen recording
- B-roll
- stock clip
- AI-generated scene
- slide graphic

### Step 6 — Prepare multi-platform reuse pack
For the chosen script, create:

- YouTube Shorts title
- YouTube Shorts description
- TikTok caption
- Instagram Reels caption
- LinkedIn short-video caption
- optional hashtag suggestions

Adjust tone by platform:
- TikTok/Reels: sharper, lighter, more casual
- YouTube Shorts: searchable and clear
- LinkedIn: more professional and insight-led

### Step 7 — Build a publishing calendar
Create a 2-week calendar with:
- date or day label
- topic
- platform
- format
- CTA
- status

Suggested rhythm:
- 3 to 5 short videos per week
- mix educational, proof, and CTA content

## External tool mapping

When the user asks what tools to use, recommend based on video type.

### Fastest beginner workflow
- Hermes for ideas, scripts, captions, calendar
- CapCut for editing and captions
- Canva for simple visuals

### No-camera presenter workflow
- Hermes for script
- HeyGen or Synthesia for avatar video
- CapCut for finishing

### Cinematic AI promo workflow
- Hermes for shot list and prompts
- Google Flow, Runway, Kling, or Luma for video generation
- ElevenLabs or Hermes TTS for voice
- CapCut for final edit

## Tool-specific prompt handoff

When asked, provide prompts for:
- Google Flow / Veo-style generation
- Runway
- Kling
- Luma
- HeyGen / Synthesia

Prompt rule:
- do not rely on AI video tools to render readable text in-scene
- add readable text during editing instead
- keep prompts visually concrete
- keep each shot short, usually 3–6 seconds

## Editing guidance

Always remind the user of these editing rules:
- strong hook in first 3 seconds
- large captions for mobile viewing
- one idea per clip
- clear CTA at end
- export vertical 9:16 by default
- keep a square or LinkedIn variant when requested

## Teaching mode for Class 10

When used for classroom teaching, organize the response into:

1. Topic ideas
2. Hooks
3. Scripts
4. Storyboard
5. Recommended tool route
6. Repurposing pack
7. Publishing calendar

Keep explanations practical and brief so students can act immediately.

## Final response template

```markdown
Done — I created the short-video content package.

Included:
- 10 topics
- 10 hooks
- 3 scripts
- 1 storyboard
- platform captions
- 2-week calendar

Recommended production route: ...
Best tools for this case: ...
Next step: choose one script and I can turn it into a full video production package.
```
