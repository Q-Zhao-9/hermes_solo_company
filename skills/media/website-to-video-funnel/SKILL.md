---
name: website-to-video-funnel
description: Convert a website page, service description, FAQ, blog post, case study, or offer into a review-ready short-video funnel package with audience framing, pain-point extraction, topics, hooks, scripts, CTA bank, platform variants, and optional publishing calendar.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [video, website, funnel, shorts, reels, tiktok, youtube-shorts, linkedin, repurposing, marketing, faq, offer]
    related_skills: [short-video-content-factory, ai-video-from-script, content-studio, social-calendar, website-seo-content]
---

# Website to Video Funnel

Use this skill when the user wants Hermes to turn existing business content into short-form video content that can attract attention, educate the audience, and drive a next-step action.

Typical source inputs:
- homepage copy
- service page
- FAQ page
- blog post
- case study
- landing page
- sales notes
- course lesson
- offer summary

This skill sits between website/business messaging and video production. It is best for turning content that already exists into a repeatable short-video funnel.

## Core outcomes

Produce a review-ready package that can include:
- source offer summary
- audience and pain-point map
- messaging angles / content themes
- 10 short-video topics
- 10 hooks
- 3 scripts (15s / 30s / 60s)
- CTA bank
- platform-specific captions/copy
- optional 2-week publishing calendar
- optional handoff into storyboard/video production

## Default assumptions

If the user does not specify otherwise, assume:
- primary formats: YouTube Shorts, TikTok, Instagram Reels
- secondary format: LinkedIn short professional video
- durations: 15s, 30s, 60s
- style: clear, practical, mobile-first, direct-response friendly
- objective: attract leads, DMs, clicks, booked calls, or registrations
- voice: explain the customer problem clearly before naming the offer

## What this skill must extract first

Before generating content, identify or infer these from the source material:
- business / offer
- audience / ICP
- primary pain point
- desired transformation or result
- proof or credibility elements
- CTA / next step
- reusable themes for a content series

If some fields are missing but inferable from the material, infer them and continue. Only ask the user for clarification when the missing information would materially change the output.

## Theme buckets to look for

When analyzing the source material, organize content into reusable buckets such as:
- FAQ answers
- myths vs truth
- mistakes to avoid
- before / after
- checklist or framework
- founder insight
- case-study proof
- tool demo or workflow
- decision guide
- urgency / risk of inaction

These buckets usually produce better short-video topics than generic “about us” messaging.

## Output modes

### Mode A — Content pack only
Use when the user wants ideas and scripts fast.

Return:
- offer summary
- audience + pain-point map
- 10 topics
- 10 hooks
- 3 scripts
- CTA bank
- platform caption suggestions

### Mode B — Publishing pack
Use when the user wants a more operational output.

Return everything in Mode A, plus:
- 2-week publishing calendar
- content-series grouping
- recommended priority order

### Mode C — Production handoff pack
Use when the user wants to produce an actual sample video.

Return everything in Mode B, plus:
- recommended “best script to produce first”
- storyboard brief for that script
- tool route recommendation
- handoff note to `ai-video-from-script`

## Recommended workflow

### Step 1 — Understand the source material
Extract:
- top customer pain point
- promise / transformation
- supporting proof
- CTA
- likely objections
- repeatable content themes

Good working summary format:

```markdown
## Offer summary
What the business helps with:
Who it is for:
Main pain point:
Desired result:
Proof / credibility:
Primary CTA:
```

### Step 2 — Build a pain-point map
Summarize the audience’s:
- problem
- frustration
- confusion
- consequence of delay
- desired outcome

This improves topic quality and makes hooks stronger.

### Step 3 — Generate 10 video topics
Each topic should be:
- concrete
- easy to visualize
- easy to say in one breath
- relevant to buyer intent
- useful for one of the theme buckets above

Good examples:
- Why your website gets traffic but no leads
- 3 signs your service page is confusing customers
- Before you pay for ads, fix this on your homepage
- The FAQ mistake that costs you inquiries

Avoid vague topics like:
- About our company
- Why we are different
- Our mission

### Step 4 — Generate 10 hooks
Hooks should be optimized for the first 1–3 seconds.

Preferred styles:
- contrarian
- warning
- curiosity
- problem-first
- quick win
- mistake pattern
- comparison

Examples:
- Most business websites are losing leads for one simple reason.
- Before you run more ads, fix this first.
- If people visit your site but don’t message you, watch this.
- Your FAQ might be doing the opposite of what you think.

### Step 5 — Generate 3 scripts
Always produce three versions:
1. 15-second punchy version
2. 30-second balanced version
3. 60-second explainer version

Each script should include:
- Hook
- Problem
- Solution / insight
- CTA

Use this format:

```markdown
## Script 1 — 15 seconds
Hook:
Voiceover:
On-screen text:
CTA:
```

Keep sentences short, spoken-language friendly, and easy to caption.

### Step 6 — Build a CTA bank
Generate several CTA types so the user can match the funnel stage:
- comment keyword
- DM keyword
- book a call
- request a quote
- visit page
- download checklist
- register / sign up

Important: the CTA must match a real next step that exists.

### Step 7 — Create platform variants
For the selected best topic or script, produce:
- YouTube Shorts title
- YouTube Shorts description
- TikTok caption
- Instagram Reels caption
- LinkedIn short-video caption
- optional hashtag suggestions

Adjust by platform:
- TikTok/Reels: sharper, lighter, more immediate
- YouTube Shorts: clear and searchable
- LinkedIn: more professional and insight-led

### Step 8 — Optional publishing calendar
When the user wants a plan, create a 2-week calendar with:
- day / date label
- topic
- hook angle
- platform
- CTA
- status

### Step 9 — Optional production handoff
If the user wants actual video creation, recommend:
- the best script to produce first
- the production route
- whether to use `short-video-content-factory` next for a storyboard
- whether to use `ai-video-from-script` next for asset package / final video

## Routing rules

- If the user wants only topic/hook/script generation, stay in this skill or pair with `short-video-content-factory`.
- If the user wants storyboard, shot list, or final video assembly, route to `ai-video-from-script`.
- If the user wants broader campaign adaptation, pair with `content-studio` and `social-calendar`.
- If the user wants to derive content from existing website messaging strategy, combine with website/SEO skills as needed.

## Output structure

When possible, organize the result in this order:

```markdown
## Offer Summary
## Audience + Pain-Point Map
## Content Theme Buckets
## 10 Video Topics
## 10 Hooks
## 3 Scripts
## CTA Bank
## Platform Copy Pack
## 2-Week Publishing Calendar (optional)
## Recommended Next Production Step
```

## Quality checks

Before delivering, verify:
- each topic is concrete, not generic
- hooks are usable in the first 1–3 seconds
- scripts sound spoken, not like blog text
- CTA maps to a real next step
- LinkedIn copy is more professional than TikTok copy
- content explains the customer problem before over-explaining the product
- output avoids generic brand fluff

## Teaching / classroom use

For classroom mode, keep the response highly actionable:
1. offer summary
2. topic ideas
3. hooks
4. scripts
5. CTA bank
6. platform reuse
7. publishing plan
8. production recommendation

## Final response template

```markdown
Done — I created the website-to-video funnel package.

Included:
- offer summary
- audience/pain-point map
- 10 topics
- 10 hooks
- 3 scripts
- CTA bank
- platform copy pack
- optional publishing calendar

Best first video to produce: ...
Recommended next step: use `short-video-content-factory` for storyboard or `ai-video-from-script` for production.
```
