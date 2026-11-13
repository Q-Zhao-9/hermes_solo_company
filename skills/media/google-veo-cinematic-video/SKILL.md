---
name: google-veo-cinematic-video
description: Create review-first cinematic video generation packages for Google Veo / Flow workflows, including Veo-ready prompts, shot design, continuity rules, native-audio guidance, regeneration loops, and final edit handoff.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [video, veo, google-flow, cinematic, generative-video, prompts, filmmaking, class10]
    related_skills: [ai-video-from-script, short-video-content-factory, website-to-video-funnel]
---

# Google Veo Cinematic Video

Use this skill when the user wants Hermes to prepare or run a cinematic video-generation workflow specifically aimed at Google Veo / Google Flow style generation.

This skill is optimized for:
- cinematic promo videos
- product trailers
- brand films
- social ads with strong visuals
- short film / scene experiments
- Class 10 AI video teaching workflows

It is **not** just a generic script skill. It is a Veo-oriented production skill focused on:
- strong prompt design
- scene structure
- consistency across shots
- camera and lighting language
- native-audio planning
- regeneration and iteration
- final assembly handoff

## Grounding assumptions

Public product positioning currently emphasizes that Veo is a leading video-generation model with:
- strong prompt adherence
- high realism / fidelity
- creative control
- support for audio generation
- support for reference-driven control in Google Flow style workflows

Do not claim any account feature is available unless it is actually available in the user’s environment.

## Core operating principle

Treat Veo as a **shot generator**, not a full editing suite.

Hermes should usually:
1. clarify the concept and outcome
2. rewrite the script into shot-based language
3. generate Veo-ready prompts scene by scene
4. define continuity locks
5. define native audio expectations
6. propose a regeneration loop
7. prepare edit/assembly notes

If direct Veo access is unavailable, still produce a **paste-ready Veo package**.

## Best use cases

Use Veo when the user wants:
- rich cinematic motion
- stylized but realistic scenes
- camera language like push-in, dolly, aerial, handheld, macro, tracking
- ambient sound or dialogue integrated into generation
- ad-style or trailer-style visual storytelling

Do **not** default to Veo when the user mainly needs:
- source-grounded summarization from documents → use NotebookLM-style prep first
- a talking avatar explainer → consider HeyGen/Synthesia route
- heavy motion graphics / diagrams → consider local coded or Manim route
- polished editing, captions, transitions, publishing → use external editor or local ffmpeg assembly after generation

## Inputs to collect or infer

Gather or infer:
- business / story / product / lesson topic
- audience
- objective: awareness, conversion, education, teaser, demo
- target platform
- aspect ratio: 9:16, 16:9, 1:1
- duration target
- tone: cinematic, luxury, documentary, gritty, futuristic, warm, premium, energetic
- realism level
- whether dialogue or ambient audio is desired
- whether the user has:
  - Veo in Gemini
  - Veo in Flow
  - reference images
  - existing script
  - existing brand style

Safe defaults if unspecified:
- short-form promo: 9:16, 30–45 seconds
- B2B explainer/promo: 16:9, 45–90 seconds
- style: clean cinematic realism
- shot length: 3–6 seconds per generated clip

## Output modes

### Mode A — Veo prompt pack only
Use when the user wants a ready-to-paste generation package.

Return:
- creative brief
- shot list
- per-shot Veo prompts
- continuity lock
- negative prompts / avoidances
- audio notes
- regeneration notes

### Mode B — Veo production package
Use when the user wants a stronger filmmaking workflow.

Return everything in Mode A, plus:
- refined script
- storyboard table
- scene timing
- title / caption suggestions
- editor handoff notes
- thumbnail ideas

### Mode C — Veo + assembly handoff
Use when the user wants the whole production path.

Return everything in Mode B, plus:
- clip naming plan
- selection criteria for the best generations
- rough-cut sequence
- music / SFX notes
- subtitle draft
- handoff to local ffmpeg / CapCut / Canva / other editor

## Recommended workflow

### Step 1 — Define the cinematic goal
Summarize in 4 lines:

```markdown
## Cinematic brief
What the video is about:
Who it is for:
What the viewer should feel / do:
What style world it belongs to:
```

Good phrasing matters more than long prompts.

### Step 2 — Convert script into shots
Veo performs best when the concept is split into shots rather than one giant paragraph.

For each shot define:
- shot objective
- subject
- environment
- action
- camera movement
- lighting
- mood
- audio
- duration

Use a table like:

| Shot | Time | Purpose | Visual | Camera | Audio | Prompt |
|---|---:|---|---|---|---|---|

### Step 3 — Create continuity locks
This is critical.

Always define reusable locked elements:
- character description
- wardrobe
- product appearance
- color palette
- lens / camera feel
- environment style
- audio mood
- pacing style

Recommended continuity block format:

```markdown
## Continuity lock
Character:
Wardrobe:
Environment:
Color palette:
Camera feel:
Lighting:
Audio mood:
Things that must stay consistent:
```

When there is a recurring character or product, repeat the same exact description across prompts.

### Step 4 — Write Veo-native prompts
Preferred prompt structure:

```text
[Shot type]. [Subject] in [environment], [action], [style], [camera movement], [lighting], [mood], [composition], [duration].
Audio: [ambient / dialogue / sound effects / music feel].
Keep [consistency rules]. Avoid [artifacts].
```

Prompt-writing rules:
- keep one visual idea per shot
- specify the camera
- specify the emotional tone
- specify ambient audio if relevant
- do not rely on generated readable text inside the scene
- add text overlays later in editing

### Step 5 — Plan native audio deliberately
Because Veo-style generation may include audio, decide scene by scene whether to use:
- ambient-only
- ambient + SFX
- music feel only
- short spoken line
- silence for later voiceover replacement

If the user needs crisp marketing copy, prefer:
- visuals + ambience in Veo
- final narration added later in editing

If the user wants dramatic realism or scene acting, use:
- short natural dialogue lines
- specific sound cues
- restrained ambience

### Step 6 — Regeneration strategy
Never assume the first generation is final.

For each shot, define what to vary between attempts:
- camera distance
- speed / movement
- subject emphasis
- realism vs stylization
- lighting warmth / contrast
- dialogue vs no dialogue
- duration

Good regeneration loop:
1. generate 2–4 variants per important shot
2. choose best motion / composition
3. tighten prompt for weak areas
4. re-run only the weak shots
5. assemble finalists

### Step 7 — Negative prompt / avoidance notes
Even if the platform does not expose explicit negative prompts in the same way as image models, Hermes should still list avoidances.

Common avoidances:
- unreadable / fake text
- warped hands
- extra limbs
- unstable faces
- flicker
- chaotic background extras
- sudden style drift
- inconsistent product details
- overdramatic camera shake

## Shot archetypes that work well

Veo is especially well suited for:
- establishing shots
- slow push-ins
- dramatic close-ups
- product beauty shots
- urban or environmental atmosphere
- lifestyle moments
- cinematic transitions between story beats
- mood / tension / reveal sequences

For marketing videos, combine:
- 1 hook shot
- 2–4 proof / product / pain-point shots
- 1 CTA or resolution shot

## Tool routing guidance

Use this skill together with:
- `ai-video-from-script` when the user wants a full production package
- `short-video-content-factory` when the user needs topics/hooks/scripts first
- `website-to-video-funnel` when source material comes from a website or offer

If the user only has source documents and no script yet, start with NotebookLM-style prep before Veo prompting.

## Output structure

Prefer this response order:

```markdown
## Cinematic Brief
## Refined Video Structure
## Continuity Lock
## Shot List
## Veo Prompts
## Audio Strategy
## Regeneration Plan
## Edit / Assembly Handoff
```

## Quality checks

Before delivering, verify:
- each shot has a clear purpose
- prompts are concrete, not vague
- camera and lighting language are present
- continuity rules are explicit
- audio is intentionally planned
- the user is not depending on generated readable in-scene text
- CTA or final resolution is clear when this is marketing content

## Safety / approval rules

Require explicit approval before:
- using paid generation credits
- logging into Google accounts
- publishing externally
- generating a real person’s likeness or cloned voice without consent
- making unsupported product or outcome claims

## Final response template

```markdown
Done — I created the Google Veo cinematic video package.

Included:
- cinematic brief
- continuity lock
- shot list
- Veo-ready prompts
- audio strategy
- regeneration plan
- edit handoff

Recommended next step: generate 2–4 variants of the top 3 shots first, then I can help choose finalists and assemble the sequence.
```
