---
name: ai-video-from-script
description: "Build AI videos from scripts using a review-first production pipeline. Covers script breakdown, storyboard, shot list, image/video generation prompts, voiceover, captions, music, editing with ffmpeg, and optional external AI video tools such as Runway, Pika, Kling, Luma, HeyGen, Synthesia, CapCut, Canva, and ElevenLabs. Use when a user asks to create, plan, storyboard, generate, or assemble videos from scripts, ads, social posts, courses, explainer scripts, product demos, or short-form marketing videos."
version: 1.0.0
---

# AI Video From Script Production Skill

## When to use

Use this skill whenever the user asks to create or plan AI video from:

- a written script
- an ad script
- a course lesson
- a social media post
- a product demo outline
- a landing page or blog post
- a brand story
- a short video idea
- a storyboard request

The goal is to turn text into a production-ready or assembled video package.

## Core principle

Operate as a review-first video production assistant.

The assistant may create scripts, storyboards, prompts, assets, voiceover, captions, edit plans, ffmpeg commands, and assembled local videos when tools are available. External publishing or paid-generation actions require explicit user approval.

Do not claim an external platform was used unless it was actually used. If API keys or accounts are unavailable, produce review-ready prompts and an execution package for the user to paste into the selected tool.

## Supported output levels

### Level 1 — Production brief only

Use when the user wants a plan or when video-generation tools are unavailable.

Deliverables:

- refined script
- target platform and aspect ratio
- audience and objective
- scene-by-scene storyboard
- shot list
- generation prompts
- voiceover script
- caption text
- music / SFX notes
- editing instructions

### Level 2 — Asset package

Use when image generation, TTS, or local editing tools are available.

Deliverables:

- storyboard
- per-scene image prompts
- per-scene video prompts
- generated images if available
- TTS narration if available
- subtitle file `.srt`
- edit decision list
- asset manifest

### Level 3 — Assembled local video

Use when enough local tools are available.

Deliverables:

- final `.mp4`
- captions `.srt`
- thumbnail image
- source assets folder
- edit manifest

Possible local stack:

- image generation tool via Hermes `image_generate`
- TTS via Hermes `text_to_speech`
- Python for file processing
- ffmpeg for assembly, subtitles, audio mixing, format conversion
- Manim for technical/explainer animations
- ASCII video pipeline for stylized/retro videos

### Level 4 — External AI video execution package

Use when the user wants cinematic/generative video and external tools are needed.

Deliverables:

- platform-specific prompts for Runway/Pika/Kling/Luma/etc.
- reference image prompts
- per-shot camera motion instructions
- negative prompts
- consistency notes
- recommended model/tool settings
- upload checklist
- final assembly plan

## External tool options

Choose based on the job type. Verify availability before using any account/API.

| Need | Good options | Notes |
|---|---|---|
| Cinematic text/image-to-video | Runway, Pika, Kling, Luma Dream Machine | Good for shots, B-roll, cinematic scenes |
| Talking avatar / presenter | HeyGen, Synthesia, D-ID | Good for business explainers and training videos |
| Fast social editing | CapCut, Canva, Descript | Good for captions, templates, short videos |
| Voiceover | ElevenLabs, OpenAI TTS, MiniMax, local TTS | Keep voice consistent; generate per scene or full track |
| Technical animation | Manim | Best for diagrams, math, software explainers |
| Stock media | Pexels, Pixabay, Storyblocks, Artgrid | Use only licensed assets |
| Local assembly | ffmpeg, Python MoviePy | Use ffmpeg for reliable final encoding |

## Workflow

### Step 1 — Collect production requirements

If missing, infer safe defaults. Ask only if the decision meaningfully changes output.

Key inputs:

- script or topic
- target platform: TikTok, YouTube Shorts, Reels, LinkedIn, YouTube, website, course
- aspect ratio: 9:16, 16:9, 1:1
- duration: 15s, 30s, 60s, 2–5min, etc.
- audience
- brand/product
- tone: cinematic, documentary, UGC, professional, animated, technical, luxury, playful
- desired language and voice
- whether to generate final video locally or prepare external-tool prompts

Default assumptions if unspecified:

- short-form social: 9:16, 30–60 seconds
- business explainer: 16:9, 60–120 seconds
- platform: LinkedIn/YouTube if B2B, TikTok/Reels/Shorts if consumer/social
- style: clean professional cinematic

### Step 2 — Rewrite script for video

Convert the input into video-friendly structure:

- hook in first 1–3 seconds
- one idea per scene
- short spoken lines
- visualizable concrete actions
- clear CTA
- remove overly dense text
- preserve factual claims and brand constraints

Output:

```markdown
## Refined Video Script
Scene 1 — Hook — 0:00–0:03
Voiceover: ...
On-screen text: ...
Visual: ...

Scene 2 — Problem — 0:03–0:10
...
```

### Step 3 — Create shot list and storyboard

For each scene specify:

- timestamp
- duration
- narration
- on-screen text
- visual description
- camera movement
- asset type: generated video, generated image, stock clip, screen recording, animation, talking avatar
- prompt
- negative prompt
- transition
- audio/SFX

Use this table:

| Scene | Time | VO | On-screen text | Visual | Asset type | Prompt | Transition |
|---|---:|---|---|---|---|---|---|

### Step 4 — Choose production route

Pick one route and state it.

#### Route A: Social ad / cinematic AI video

- Create reference images if needed
- Generate short clips in external AI video tool
- Keep each shot 3–6 seconds
- Use consistent character/style references
- Assemble in CapCut/Descript/ffmpeg

#### Route B: Talking avatar explainer

- Generate voice or use avatar platform voice
- Create slide/visual background prompts
- Use HeyGen/Synthesia/D-ID
- Add captions and brand CTA

#### Route C: Technical explainer

- Use Manim for diagrams and motion graphics
- Use TTS or user-provided narration
- Export 16:9 or 9:16 version

#### Route D: Local slideshow/video package

- Generate still images
- Generate TTS
- Use ffmpeg zoompan/pan effects
- Add captions and background music if available

#### Route E: Local / Codex-coded motion graphics without image-generation API

Use this route when the user wants "Mode 1", "Codex-generated visuals", or a no-API/no-Runway approach, or when external video tools are unavailable and the built-in image generation tool fails, for example because its provider key is not configured. Do not stop after the image-generation failure. Generate polished vector-style slide images locally with Python/Pillow, SVG, or HTML/CSS screenshots, then animate them with ffmpeg.

Reusable pattern:

1. Write `script.md`, `storyboard.md`, `prompts.md`, and `captions.srt` first.
2. Generate TTS narration with `text_to_speech` if available.
3. Use code to create one 16:9 or 9:16 branded slide per scene: gradient background, clean SaaS-style cards/icons, dashboards, AI hub diagrams, workflow arrows, large readable headline, no secrets, no fake logos.
4. Prefer generating one high-quality PNG per scene and animating it with ffmpeg `zoompan`, `drawbox`, and `drawtext`. This is much faster and more reliable than rendering every frame in Python.
5. Concatenate clips, mux narration, burn captions, then validate with `ffprobe`.

This route produces a complete downloadable `.mp4` even without Runway/Pika/Kling/Luma or image-generation API access. It is best for business explainers, SaaS workflows, AI-agent demos, website/CRM/chatbot diagrams, social ads, product concept videos, and educational summaries where clean motion graphics are acceptable.

Important performance lesson: avoid generating thousands of full-resolution PNG frames with Python/Pillow unless true per-frame animation is required. For a 77-second 1080p video at 30fps, full-frame generation can be slow and disk-heavy. A better default is coded scene slides plus ffmpeg motion effects.

### Step 5 — Prompt engineering for AI video tools

Prompt format:

```text
[Subject] doing [action] in [environment], [style], [camera movement], [lighting], [mood], [composition], [duration], [aspect ratio].
Keep [character/product/style] consistent. No text, no logos, no distorted hands, no extra limbs, no flicker.
```

Examples:

```text
A small business owner sitting at a desk late at night, overwhelmed by spreadsheets and customer messages, cinematic documentary style, slow push-in camera, warm desk lamp lighting, shallow depth of field, realistic, 5 seconds, vertical 9:16. No text, no logos, no distorted hands.
```

```text
Clean SaaS dashboard interface with automated AI agent cards moving tasks from inbox to done, modern product demo style, smooth screen-recording-like camera movement, crisp UI, blue and white brand palette, 4 seconds, 16:9. No unreadable text, no fake logos.
```

For consistency:

- reuse exact character description across scenes
- reuse exact brand/color/style phrase
- keep camera language consistent
- generate images first if the video platform supports image-to-video
- avoid asking text-to-video tools to render readable text; add text in editing instead

### Step 6 — Voiceover

If using Hermes TTS, call `text_to_speech` with the final narration. For long videos, split by scene.

Voice direction template:

```text
Voice: warm, confident, natural founder tone.
Pace: conversational, not rushed.
Emotion: helpful and practical.
```

### Step 7 — Captions

Create `.srt` captions from scene timings. Keep captions short and readable.

Rules:

- max 1–2 lines
- max ~42 characters per line
- align with spoken phrases
- burn captions for short-form video
- provide separate `.srt` for YouTube/LinkedIn

### Step 8 — Local assembly with ffmpeg

If assets are local and ffmpeg is installed, assemble a draft video.

If image generation is unavailable, first create local slide images with Python/Pillow. A reusable approach is:

- create a project folder with `assets/images`, `assets/clips`, `assets/audio`, `edit`, and `final`
- create one PNG per scene at the target resolution, e.g. `1920x1080` for 16:9
- use a coherent brand palette, gradient background, cards/icons, and large readable text
- avoid relying on AI-generated readable text; place real text overlays during editing
- animate each PNG with `zoompan` and overlay scene headlines with `drawtext`
- keep clip durations aligned to narration duration, not just the initial storyboard estimate

Common commands:

Create a video from images with simple zoom:

```bash
ffmpeg -y -loop 1 -t 4 -i scene1.png \
  -vf "scale=1080:1920,zoompan=z='min(zoom+0.0015,1.08)':d=120:s=1080x1920:fps=30" \
  -c:v libx264 -pix_fmt yuv420p scene1.mp4
```

Concatenate clips:

```bash
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy rough_cut.mp4
```

Mux narration:

```bash
ffmpeg -y -i rough_cut.mp4 -i narration.mp3 \
  -c:v copy -c:a aac -shortest final.mp4
```

Burn subtitles:

```bash
ffmpeg -y -i final.mp4 -vf "subtitles=captions.srt" \
  -c:v libx264 -c:a copy final_captioned.mp4
```

Normalize final encoding:

```bash
ffmpeg -y -i input.mp4 -c:v libx264 -pix_fmt yuv420p -crf 20 -preset medium -c:a aac -b:a 192k output.mp4
```

### Step 9 — Quality review

Verify before delivering:

- duration matches request
- aspect ratio is correct
- first 3 seconds have a strong hook
- captions are readable
- CTA is clear
- no secrets/private data in visuals
- no generated text artifacts if AI video was used
- no unlicensed assets
- audio does not clip
- final file opens with ffprobe/ffmpeg

Run:

```bash
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height -of json final.mp4
```

## Deliverable folder structure

Use this layout:

```text
video-project-name/
  brief.md
  script.md
  storyboard.md
  prompts.md
  captions.srt
  assets/
    images/
    clips/
    audio/
    music/
  edit/
    concat.txt
    manifest.json
  final/
    final.mp4
    final_captioned.mp4
    thumbnail.png
```

## Safety and approval rules

Require explicit approval before:

- spending money or using paid credits
- logging into external accounts
- publishing to social channels
- sending a video to clients/leads
- using a real person's likeness or voice clone
- making claims about a product, income, health, finance, or legal outcomes
- using copyrighted music or restricted stock media

For likeness/voice:

- only use user-provided or clearly licensed consented likeness/voice
- do not create deceptive impersonations
- label synthetic avatar/voice where appropriate

For business marketing claims:

- avoid unsupported guarantees
- phrase uncertain results as possibilities or examples
- preserve user-provided factual constraints

## Common pitfalls

- Script is too dense for video: shorten scenes and captions.
- AI video tools produce bad text: add text in editing instead.
- Character changes between shots: use image-to-video references and repeated character descriptors.
- Shots are too long: AI video often works best as 3–6 second clips.
- Voiceover and visuals do not match: create scene timings before generation.
- Video has no CTA: end with one simple action.
- Captions too small: design for phone viewing.

## Final response template

When delivering a video production package, summarize:

```markdown
Done — I created the AI video production package.

Files:
- brief: ...
- storyboard: ...
- prompts: ...
- captions: ...
- final video: MEDIA:/path/to/final.mp4

Production route used: ...
Validation: ...
Next step: review the storyboard/final video and tell me what to change.
```

If only creating prompts for external tools:

```markdown
I prepared the external AI video package. Use the prompts in Runway/Pika/Kling/Luma/etc. Generate one clip per scene, then assemble using the included edit plan.
```
