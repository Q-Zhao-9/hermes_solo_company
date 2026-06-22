---
name: class7-brand-image-generation
description: Reusable workflow for turning a selected Class 7 brand direction into review-first image assets using Codex or a fal.ai-backed generator, with prompt structure, exact output paths, QA, and website handoff.
---

# Class 7 Brand Image Generation

## When to use

Use this skill when Class 7 work needs to move from a chosen visual direction into actual image assets that can be reviewed and then applied to a website, presentation, or classroom demo.

Typical use cases:

- generate hero images from a selected brand direction
- create logo concept boards, social promo images, and explainer banners
- produce website-ready images after the student chooses one winning direction
- create classroom examples that compare prompt quality and visual consistency
- prepare image assets for later upload into a website or presentation UI

This skill is specifically for **asset production after direction selection**. It should usually be used after `brand-visual-system`, not before it.

## Core constraint

Do not generate disconnected artwork from vague prompts.

The workflow should stay:

1. business brief
2. three directions
3. one selected winner
4. image prompt pack from the winner
5. generate reviewable assets
6. QA the assets
7. map the approved assets into website or presentation usage

Keep repeating the Class 7 boundary:

- this is creative-direction-driven asset generation
- this is not final approved brand identity work
- one selected direction should drive the images
- website and presentation application matter more than visual novelty alone

## Required inputs

Collect or infer these before generating:

- business name
- offer / product / service
- target audience
- selected brand direction name
- tone keywords
- palette direction
- typography vibe
- imagery guidance
- required asset list
- target usage for each asset
- output size / aspect ratio
- exact save path if using Codex inside a repo

If the user provides only partial information, proceed with explicit assumptions unless the missing information would make the output unusable.

## Output types to support

Common Class 7 asset set:

- logo concept image or board
- homepage hero image
- social promo image
- service / product explainer banner
- optional founder portrait treatment direction
- optional slide cover or presentation-room cover image

## Provider selection rule

Choose the generation path based on the task.

### Use Codex when

Use Codex when the output should be written directly into a project workspace or when the prompt needs close coupling with repo files, exact paths, or iterative code-adjacent asset creation.

Best for:

- saving directly to `public/`, `assets/`, or another known repo path
- generating or revising assets inside an implementation task
- workflows where exact filename and folder location matter
- iterative app/website integration work

### Use fal.ai-backed image generation when

Use the fal.ai-backed generator when the goal is high-quality image rendering and the output does not need Codex to reason over repo structure.

Best for:

- fast creative generation from polished prompts
- multiple visual candidates for review
- hero, promo, and social images where raw image quality matters most
- cases where the Hermes image generation backend is already configured to fal.ai or another image provider

## Recommended workflow

### 1. Confirm the selected direction

Before generating assets, summarize the chosen direction in one compact block:

- direction name
- positioning angle
- emotional feel
- palette
- typography vibe
- imagery rules
- what to avoid

Do not keep all three directions active during image generation.

### 2. Build an asset table

Create a concrete asset list such as:

| Asset | Usage | Ratio | Size | Notes |
|---|---|---:|---:|---|
| hero image | homepage hero | 16:9 | 1600x900 | leave negative space for headline |
| social promo | LinkedIn/X post | 1:1 | 1080x1080 | bold focal object |
| explainer banner | section/banner | 3:2 | 1440x960 | show workflow context |
| logo concept board | review only | 1:1 | 1536x1536 | 3 variations on one sheet |

### 3. Build prompt packs from the chosen direction

Each prompt should contain:

- business / offer context
- target audience
- visual direction summary
- composition instructions
- subject matter
- palette guidance
- lighting / texture / rendering style
- brand-safe exclusions
- output ratio or dimensions
- placement notes such as negative space for website copy

### 4. Generate assets with the chosen path

#### Codex path

Use Codex when files must land in an exact project location.

Prompting rules:

- specify exact filename and path
- specify exact dimensions and format
- ask Codex to return only the saved file path or a short generation result
- if working in a scratch repo, tell Codex where to place outputs under `output/`
- after generation, verify the file actually exists

Representative pattern:

```bash
codex exec -s workspace-write 'Create a 1600x900 PNG homepage hero image for [BUSINESS]. Follow this brand direction: [DIRECTION]. Save it exactly as public/images/class7-hero.png. Keep clean negative space on the left for headline text. Return only the final saved file path.'
```

Important:

- always use an exact save path
- specify PNG/JPG/SVG explicitly
- specify dimensions explicitly
- verify the asset after generation with file inspection
- if Codex cannot produce the desired image natively, use it to create prompt-pack files or integration scaffolding instead of pretending the image was produced

#### fal.ai-backed generation path

Use the Hermes image generation path when a high-quality rendered image is needed and the backend is already configured to fal.ai or another compatible provider.

Prompting rules:

- write one clean generation prompt per asset
- keep provider-specific details abstracted unless the environment requires them
- request the correct aspect ratio
- generate multiple candidates when comparison is useful
- save or upload the winning result into the project afterward

Representative Hermes pattern:

- hero image → landscape
- social promo → square
- portrait poster → portrait

If the environment exposes a direct fal.ai API outside Hermes, keep secrets out of the skill and store credentials in environment/config only.

### 5. QA every generated asset

Check:

- does it match the chosen direction?
- is the palette consistent?
- is there enough negative space for website or slide text?
- does it avoid generic AI clutter or distorted typography?
- is the composition usable at the intended crop?
- is any text inside the image either absent or intentionally minimal?
- does it fit the target page or presentation section?

### 6. Extract text carefully

If a workflow later needs text from an image:

- prefer using the original prompt/source copy when available
- do not rely on decorative text rendered inside AI images as authoritative copy
- if OCR/extraction is required, treat the result as draft text that still needs cleanup and review
- for presentation slides, keep the slide text source separate from the visual asset whenever possible

### 7. Handoff to website or presentation implementation

For every approved asset, produce:

- final filename
- source prompt
- intended page/section/slide usage
- crop notes
- fallback alt text
- any follow-up edits needed

## Recommended output structure

Return results in this order.

### 1. Selected direction summary

A compact reminder of the chosen brand direction.

### 2. Asset plan

A table of assets, usage, ratio, and dimensions.

### 3. Prompt pack

One prompt per asset, clearly labeled.

### 4. Generation path

State whether each asset should use:

- Codex
- fal.ai-backed image generation
- or both, where fal.ai creates the image and Codex places/integrates it

### 5. Review checklist

List acceptance checks for brand consistency and usability.

### 6. Handoff notes

Explain where each asset should go in the website or presentation.

## Common pitfalls

### 1. Generating before selecting a winner

Do not generate production assets while all three directions are still active.

### 2. Forgetting exact save paths in Codex

If Codex is being used inside a repo, always specify the full destination path.

### 3. Asking the model to render lots of text inside the image

Avoid heavy text-in-image requirements. Use website HTML or presentation text layers for final copy whenever possible.

### 4. Ignoring negative space

Hero and banner images often fail because there is nowhere to place the headline or CTA.

### 5. No asset QA step

Do not hand off raw generations without checking crop, style consistency, and usability.

## File and naming guidance

Recommended naming pattern:

```text
class7-{direction}-{asset}-{ratio-or-size}.{ext}
```

Examples:

```text
class7-modern-trust-hero-1600x900.png
class7-modern-trust-social-1080x1080.png
class7-modern-trust-banner-1440x960.png
```

## Response style

- be concise but implementation-ready
- keep prompts clean and copyable
- tie image instructions back to the selected direction
- prefer website-ready practical guidance over abstract art critique
