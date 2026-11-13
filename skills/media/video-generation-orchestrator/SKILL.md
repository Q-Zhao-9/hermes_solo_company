---
name: video-generation-orchestrator
description: Route a video request into the right review-first workflow by deciding when to use source-grounded NotebookLM-style prep, Google Veo cinematic generation, broader script-to-video production, or short-video campaign skills.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [video, orchestration, routing, notebooklm, veo, ai-video, workflow, production, class10]
    related_skills: [notebooklm-to-video, google-veo-cinematic-video, ai-video-from-script, website-to-video-funnel, short-video-campaign-orchestrator, short-video-content-factory]
---

# Video Generation Orchestrator

Use this skill when the user does **not** just need one narrow deliverable, but instead needs Hermes to decide the best video workflow and sequence of skills.

This is the routing and operating-system layer above:
- `notebooklm-to-video`
- `google-veo-cinematic-video`
- `ai-video-from-script`
- `website-to-video-funnel`
- `short-video-content-factory`
- `short-video-campaign-orchestrator`

Its job is to answer:
- what kind of video job is this?
- what source material exists?
- what level of factual grounding is required?
- is the user asking for cinematic generation, evidence-backed scripting, campaign operations, or full production?
- what should happen first, second, and third?

This skill should prevent Hermes from jumping into Veo too early, or from keeping the user stuck in research mode when a direct generation workflow is better.

## Core outcomes

Produce a review-ready orchestration packet that includes:
- job classification
- route recommendation
- why that route fits
- sequence of downstream skills
- concrete deliverables per stage
- assumptions and risks
- the smallest useful next step

## Default assumptions

If the user does not specify otherwise, assume:
- the workflow is review-first
- Hermes should avoid paid generation or external publishing until explicitly approved
- the user benefits from a staged pipeline rather than one giant prompt
- the user wants the best practical route, not a theoretical comparison
- Hermes should recommend the smallest useful next move while preserving upgrade paths

## Core routing principle

Classify the request before generating anything.

The orchestrator should first decide which of these job types best matches the request:

1. **Source-grounded explainer / lesson / research video**
2. **Cinematic promo / ad / trailer / visual story**
3. **General script-to-video production package**
4. **Website/page-to-video repurposing**
5. **Short-video campaign / repeatable content operation**
6. **Mixed workflow** requiring more than one route

## Fast routing matrix

### Route A — NotebookLM first
Use `notebooklm-to-video` first when:
- the user starts from PDFs, docs, articles, notes, FAQs, research, transcripts, or multiple sources
- factual grounding matters
- the user wants educational, evidence-backed, or source-sensitive content
- there is not yet a clean spoken script

Typical sequence:
`notebooklm-to-video -> google-veo-cinematic-video`
or
`notebooklm-to-video -> ai-video-from-script`

### Route B — Veo first
Use `google-veo-cinematic-video` first when:
- the user already has a clear message or script
- the main value is strong visuals, mood, realism, camera language, or cinematic motion
- the result is promo/trailer/ad/brand-film oriented
- source citations are not the primary constraint

Typical sequence:
`google-veo-cinematic-video -> ai-video-from-script`

### Route C — Script-to-video production first
Use `ai-video-from-script` first when:
- the user already has a script and wants a broader production package
- the route may use multiple generation or editing tools, not only Veo
- the user needs voiceover, pacing, edit assembly, captions, and output planning more than source compression

Typical sequence:
`ai-video-from-script`
or
`ai-video-from-script -> google-veo-cinematic-video`

### Route D — Website-to-video first
Use `website-to-video-funnel` first when:
- the source is a website page, offer page, FAQ, service page, landing page, or blog post
- the user wants marketing repurposing from existing web assets
- Hermes needs to extract angles, claims, CTAs, and content hooks from site copy

Typical sequence:
`website-to-video-funnel -> short-video-content-factory`
or
`website-to-video-funnel -> notebooklm-to-video`
or
`website-to-video-funnel -> google-veo-cinematic-video`

### Route E — Campaign orchestrator first
Use `short-video-campaign-orchestrator` first when:
- the user wants an ongoing content system rather than one video
- the goal is a batch, series, weekly cadence, or campaign operation
- Hermes needs to coordinate multiple downstream deliverables across planning, production, publishing, and reporting

Typical sequence:
`short-video-campaign-orchestrator -> short-video-content-factory -> short-video-production-queue`

### Route F — Mixed route
Use a mixed route when:
- the user has source documents and also wants cinematic scenes
- the job needs both factual grounding and high-end visual generation
- the user has one source asset that must be split into long-form explainer + short-form promos

Typical sequence:
`notebooklm-to-video -> google-veo-cinematic-video -> ai-video-from-script`

## Inputs to collect or infer

Gather or infer before asking follow-up questions:
- source material type: none, script, website, docs, notes, research, video transcript
- desired outcome: explainer, lesson, promo, trailer, ad, demo, campaign, recap, social batch
- audience
- primary goal: educate, convert, attract attention, summarize, launch, build trust
- platform and aspect ratio
- required duration
- grounding sensitivity: low / medium / high
- style sensitivity: cinematic / clean / social / documentary / presentation
- available assets: brand guide, voiceover, screenshots, B-roll, reference images, source docs
- production constraints: budget, paid credits, editing capacity, privacy, compliance

Safe defaults if unspecified:
- one-video request: recommend a single primary route and optional upgrade path
- unclear source quality: start with source normalization before generation
- unclear platform: 9:16 for short social, 16:9 for explainers and presentations

## Recommended workflow

### Step 1 — Classify the job
Start with:

```markdown
## Video Request Classification
Primary job type:
Source material state:
Grounding sensitivity:
Visual ambition:
Likely best route:
```

### Step 2 — Decide the entry skill
Pick the first skill based on what is missing.

Rule of thumb:
- missing grounded structure -> start NotebookLM
- missing cinematic visual package -> start Veo
- missing production assembly -> start ai-video-from-script
- missing content extraction from a page -> start website-to-video-funnel
- missing campaign architecture -> start short-video-campaign-orchestrator

### Step 3 — Define the stage sequence
Use a stage plan like:

| Stage | Goal | Deliverable | Best skill |
|---|---|---|---|
| 1 | Normalize source / concept | source map or creative brief | <skill> |
| 2 | Script / scene design | script or shot pack | <skill> |
| 3 | Generation / assembly | prompts / edit package | <skill> |
| 4 | Review / iteration | revised package | <skill> |

Keep the sequence short and practical. Usually 2–4 stages is enough.

### Step 4 — Explain why this route wins
Always justify the route.

Examples:
- "Start with NotebookLM because the main risk is factual drift, not visual quality."
- "Start with Veo because the message is already clear and the main value now is cinematic execution."
- "Start with website-to-video because the content already exists on the page and should be mined before scripting from scratch."
- "Start with the campaign orchestrator because this is really a repeatable operating system request, not a one-off video."

### Step 5 — Define deliverables per stage
For each stage, specify the concrete output Hermes should produce.

Examples:
- source map
- grounded claim table
- refined script
- shot list
- Veo prompt pack
- edit handoff
- 5-video batch plan
- platform publishing pack

### Step 6 — Add decision gates
Decision gates keep the workflow review-first.

Recommended gates:
- approve source framing before heavy scripting
- approve script before paid generation
- approve shot pack before batch generation
- approve batch direction before campaign scaling

### Step 7 — Recommend the smallest next move
Do not end with only a big architecture diagram.

Always provide:
- the route
- the first skill to use
- the first artifact Hermes should generate next

## Output modes

### Mode A — Single video route recommendation
Use when the user wants the right workflow for one video.

Return:
- classification
- recommended route
- stage sequence
- next step

### Mode B — Production orchestration packet
Use when the user wants a reusable one-project workflow.

Return everything in Mode A, plus:
- rationale
- decision gates
- deliverables per stage
- risk notes

### Mode C — Reusable video operations system
Use when the user wants a reusable internal system or class capability.

Return everything in Mode B, plus:
- trigger conditions for each route
- routing matrix
- handoff rules between skills
- archive / naming suggestions
- scale-up notes for future workflows

## Recommended output structure

```markdown
## Video Request Classification
## Recommended Route
## Why This Route Fits
## Stage Plan
## Deliverables by Stage
## Decision Gates
## Risks and Constraints
## Best Next Step
```

## Routing guardrails

- Do not send document-heavy projects directly to Veo before extracting grounded claims.
- Do not force NotebookLM-style prep when the user already has a clean, approved script and only needs cinematic execution.
- Do not confuse a one-video request with a campaign operating-system request.
- Do not treat website copy as if it were already a spoken script.
- Do not imply platform availability, paid credits, or direct account access without verification.
- Keep the user moving toward the next artifact, not trapped in abstract planning.

## Quality checks

Before delivering, verify:
- the route matches the actual bottleneck
- the first skill chosen addresses the missing layer
- the stage sequence is short and actionable
- the output names specific downstream skills rather than vague categories
- the recommended next step is concrete enough to execute immediately

## Final response template

```markdown
Done — I created the video generation orchestration plan.

Included:
- request classification
- workflow route recommendation
- stage-by-stage skill sequence
- decision gates
- risks and constraints
- best next step

Recommended next step: I can now run Stage 1 and generate the first artifact for this route.
```
