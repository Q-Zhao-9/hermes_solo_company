# mybnb Video Generation Orchestrator Demo

Use this as a real Class 10 example for a business topic tied to the user's Airbnb-like rental marketplace MVP.

## Assumptions
- Brand: mybnb
- Product: an Airbnb-like rental marketplace MVP
- Primary audience: hosts, property managers, and renters evaluating a new booking platform
- Goal: explain the product clearly and generate early interest
- Source state: likely website copy, feature notes, and founder messaging exist or can be drafted
- Constraint: keep the workflow practical and review-first

## Video Request Classification
- Primary job type: mixed workflow
- Source material state: website/product messaging plus likely founder notes
- Grounding sensitivity: medium
- Visual ambition: medium to high
- Likely best route: `website-to-video-funnel -> short-video-content-factory -> google-veo-cinematic-video` for promos, with `ai-video-from-script` as an assembly path

## Recommended Route

### Route A — Best default for launch content
1. `website-to-video-funnel`
2. `short-video-content-factory`
3. `google-veo-cinematic-video`
4. `ai-video-from-script`

### Why this route fits
- The most likely starting asset for mybnb is website or offer copy, not a fully approved script.
- The first bottleneck is message extraction: what the marketplace offers, for whom, and why it is different.
- After that, short-video content generation creates practical topics, hooks, and scripts.
- Then Veo-style cinematic prompting is useful for the best promo concept, not for the whole campaign upfront.
- Finally, broader script-to-video assembly can package voiceover, captions, pacing, and editing notes.

## Stage Plan
| Stage | Goal | Deliverable | Best skill |
|---|---|---|---|
| 1 | Extract launch messaging from the offer/site | offer summary, pain points, CTA angles | `website-to-video-funnel` |
| 2 | Turn messaging into testable short-form concepts | 10 topics, 10 hooks, 3 scripts, caption ideas | `short-video-content-factory` |
| 3 | Upgrade the strongest concept into a cinematic promo | continuity lock, shot list, Veo prompt pack | `google-veo-cinematic-video` |
| 4 | Prepare production-ready handoff | voiceover/edit plan, scene order, final assembly notes | `ai-video-from-script` |

## Deliverables by Stage

### Stage 1
- homepage/offer extraction
- ICP framing
- benefits vs alternatives
- CTA framing for hosts vs renters

### Stage 2
- 10 short-video topics
- 10 hooks
- 15s / 30s / 60s scripts
- platform caption pack
- first 5-video batch recommendation

### Stage 3
- one cinematic brief for the winning promo idea
- shot-by-shot visual plan
- Veo-ready prompts
- regeneration notes

### Stage 4
- narration or subtitle draft
- clip naming plan
- edit handoff for CapCut/Canva/other editor
- publishing-ready structure

## Decision Gates
- Gate 1: approve extracted messaging before script generation
- Gate 2: approve the strongest topic before cinematic shot planning
- Gate 3: approve the Veo prompt pack before any paid generation
- Gate 4: approve the final assembly direction before publishing

## Risks and Constraints
- Source risk: if the mybnb differentiation is not clear yet, topic quality will drift into generic rental-marketplace language
- Claim risk: avoid unsupported trust, revenue, occupancy, or host-growth claims
- Production risk: do not start with cinematic generation before the offer and audience message are sharp
- Cost risk: Veo-style generation should only be used on the strongest approved concept, not the entire first batch

## Best Next Step
Run Stage 1 first.

Recommended Stage 1 prompt:

```text
Use website-to-video-funnel for mybnb.
Business: mybnb
Offer: Airbnb-like rental marketplace MVP
Audience: early hosts, property managers, and renters
Goal: extract the clearest launch messaging and convert it into short-video source angles.
Output: offer summary, audience pain points, proof gaps, CTA angles, and the 5 strongest short-video directions to test first.
Keep it review-first.
```

## Optional upgrade path
If mybnb later has:
- a strong founder memo or product explainer doc -> start with `notebooklm-to-video`
- a polished launch script already approved -> start directly with `google-veo-cinematic-video` or `ai-video-from-script`
- a broader weekly content plan -> branch into `short-video-campaign-orchestrator`
