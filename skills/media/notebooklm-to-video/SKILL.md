---
name: notebooklm-to-video
description: "Turn source-grounded material from Gemini Notebook / NotebookLM style workflows into review-ready video packages: summaries, narrative angles, scripts, storyboard, citations-aware claims, and handoff to Veo, editors, or local assembly."
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [video, notebooklm, gemini-notebook, research, scriptwriting, storyboarding, citations, education, class10]
    related_skills: [website-to-video-funnel, short-video-content-factory, ai-video-from-script, google-veo-cinematic-video]
---

# NotebookLM to Video

Use this skill when the user wants to turn source material into a video package using a NotebookLM / Gemini Notebook style workflow.

This skill is optimized for:
- lecture notes to video
- article / blog to video
- website / FAQ / docs to video
- research packet to explainer video
- case study to social video
- course materials to lesson video
- founder notes / research / competitor notes to content plan

## Important scope note

NotebookLM / Gemini Notebook is best treated here as a **source-grounded research and script-prep system**, not as a primary cinematic video generator.

Use this skill to:
- organize source material
- extract themes and evidence
- produce grounded scripts
- preserve claim discipline
- create storyboard / production handoff

Then route the result into:
- `google-veo-cinematic-video` for cinematic generation
- `ai-video-from-script` for broader production
- local editing / captions / TTS workflows

## Grounding assumptions

Public positioning currently emphasizes that Gemini Notebook can:
- take in PDFs, websites, YouTube videos, audio files, Docs, Slides, and similar sources
- summarize and connect ideas across sources
- provide citations tied to source material
- create source-grounded insights
- generate audio-overview style discussions

Do not claim NotebookLM directly generated a finished cinematic video unless that actually happened.

## Core operating principle

Preserve a strict boundary between:
1. **source-grounded claims** from the material
2. **creative framing** added for the video format

When adapting source material into video:
- keep factual claims grounded in supplied material
- mark interpretations clearly
- avoid inventing metrics, quotes, or proof
- keep the strongest source lines available for narration or overlays

## Best use cases

Use this skill when the user has:
- PDFs
- internal notes
- article drafts
- wiki pages
- lesson notes
- website copy
- source transcripts
- research packets
- multiple documents that need compression into a video script

This is especially strong when the user wants:
- credible educational content
- source-based explainers
- lesson videos
- expert-summary videos
- article-to-video repurposing
- founder/research-based social content

## Inputs to collect or infer

Gather or infer:
- source type(s)
- topic
- audience
- desired video format
- goal: educate, summarize, persuade, recap, promote, teach
- target platform
- desired duration
- whether the result should be:
  - short-form social
  - lesson/explainer
  - presentation video
  - promo video backed by evidence
- whether strong citations / evidence mapping are required

Safe defaults if unspecified:
- short-form educational: 30–60 seconds, 9:16
- explainer/presentation: 60–180 seconds, 16:9
- style: clean, factual, engaging, non-hype

## Output modes

### Mode A — Source-to-script pack
Use when the user wants a grounded script only.

Return:
- source summary
- key claims
- evidence anchors
- angle options
- 1–3 scripts

### Mode B — Source-to-storyboard pack
Use when the user wants a production-ready outline.

Return everything in Mode A, plus:
- storyboard
- scene-by-scene visuals
- on-screen text suggestions
- narration notes
- caption draft

### Mode C — Source-to-production handoff
Use when the user wants the result turned into a generation/execution package.

Return everything in Mode B, plus:
- route recommendation: Veo / avatar / local / slides / editing workflow
- per-scene generation prompts
- asset suggestions
- editor handoff notes

## Recommended workflow

### Step 1 — Normalize the source set
First classify the source material:
- factual / instructional
- persuasive / marketing
- research / analysis
- narrative / story-driven
- mixed

Then produce:

```markdown
## Source map
Primary sources:
Secondary sources:
Trust level / claim sensitivity:
Main themes:
```

If the material is messy, organize it before scripting.

### Step 2 — Extract grounded claims
Build a claims table before writing the script.

Use:

| Claim | Evidence from source | Confidence | Safe to narrate directly? |
|---|---|---|---|

This prevents hallucinated marketing language.

Recommended categories:
- direct facts
- examples
- opinions / interpretations
- unsupported gaps that need user confirmation

### Step 3 — Choose the video angle
Common angles:
- summary / briefing
- lesson / explainer
- myth vs truth
- framework / checklist
- case study breakdown
- product or service explanation
- research digest
- decision guide

Pick the angle that best matches the source and audience.

### Step 4 — Rewrite for spoken video
Convert the material into video language.

Rules:
- shorter sentences
- one idea per beat
- viewer-first framing
- concrete visuals
- clear transitions
- keep the strongest source-backed claims
- do not overload with citations in the spoken line; reserve citations for notes or overlays

Suggested output structure:

```markdown
## Refined video script
Scene 1 — Hook
Scene 2 — Context
Scene 3 — Main insight
Scene 4 — Supporting point
Scene 5 — CTA / takeaway
```

### Step 5 — Prepare source-aware visual plan
For each scene specify:
- what the viewer hears
- what the viewer sees
- whether the scene should show:
  - abstract graphics
  - direct source screenshots
  - slides
  - diagrams
  - cinematic reenactment / B-roll
  - UI / workflow demonstration

When the source is educational or documentary-like, prefer grounded visuals:
- document excerpts
- diagrams
- charts
- timeline cards
- source snapshots
- interface demos

When the source is marketing or founder content, blend grounded claims with cinematic or social visuals.

### Step 6 — Decide the production route
Recommended routing:

#### Route A — Source-grounded short social video
Use when the user wants 30–60 second repurposing.
- produce 10 topics / 10 hooks if needed
- generate 1–3 short scripts
- add captions and CTA
- optionally hand off to short-video or Veo skill

#### Route B — Lesson / explainer video
Use when the user wants clear teaching.
- summarize source set
- script lesson
- use slides / diagrams / screen visuals
- optionally add TTS and captions

#### Route C — Evidence-backed cinematic promo
Use when the user wants strong visuals without losing grounding.
- extract supported claims first
- create a concise voiceover
- hand off scenes to `google-veo-cinematic-video`
- keep factual statements conservative

### Step 7 — Citation discipline
NotebookLM-style workflows are valuable because they stay tied to source material.

Hermes should preserve that benefit by keeping a lightweight evidence section.

Recommended format:

```markdown
## Evidence notes
Claim 1:
Supported by:
Use in video as:

Claim 2:
Supported by:
Use in video as:
```

Do not bury the user in references unless requested. The goal is credibility, not academic formatting overload.

### Step 8 — Prepare handoff package
If the user wants production next, provide:
- final script
- storyboard
- on-screen text
- citation-sensitive claims list
- visual route recommendation
- tool-specific next step

For cinematic generation, hand off to:
- `google-veo-cinematic-video`

For general video assembly, hand off to:
- `ai-video-from-script`

## Source hygiene rules

Always prefer:
- exact wording for sensitive claims
- conservative paraphrase for uncertain material
- user confirmation for missing numbers, dates, or claims

Do not invent:
- metrics
- testimonials
- customer results
- quotes
- source conclusions that were never stated

If the source is weak, say so and downgrade the confidence of the output.

## Output structure

Prefer this order:

```markdown
## Source Map
## Grounded Claim Table
## Video Angle Recommendation
## Refined Script
## Storyboard / Scene Plan
## Evidence Notes
## Recommended Production Route
## Next Step Handoff
```

## Quality checks

Before delivering, verify:
- the script still reflects the source material
- risky claims are either removed or clearly framed
- visuals match the type of source
- the chosen route fits the user’s goal
- the output is actually video-friendly, not just a summary pasted into scenes

## Safety / approval rules

Require explicit approval before:
- uploading private material to external tools
- using paid services or account logins
- publishing generated videos externally
- turning uncertain claims into promotional claims

If the material appears confidential, recommend a local/offline draft workflow first.

## Final response template

```markdown
Done — I created the NotebookLM-to-video package.

Included:
- source map
- grounded claim table
- refined script
- storyboard
- evidence notes
- production route recommendation

Best next step: if you want cinematic scenes, I can now convert this into a Google Veo generation package. If you want a full assembled video package, I can route it into the broader AI video production workflow.
```
