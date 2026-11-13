---
name: class14-final-demo-proof-builder
description: Class 14 demo-preparation skill for building a reliable evidence pack, backup materials, and preflight checklist for a student's final AI solo company demo.
version: 0.1.0
metadata:
  hermes:
    tags: [class14, demo, proof-pack, fallback, classroom, launch]
    related_skills: [class14-final-demo-builder, class14-end-to-end-flow-validator, class14-launch-blocker-fixer, final-integration-launch-orchestrator, class14-teacher-workflow-orchestrator]
---

# Class 14 Final Demo Proof Builder

## Purpose
Use this Class 14 skill when a teacher or student already knows the intended final demo flow, but needs to prepare the supporting proof materials that make the live presentation believable, smooth, and resilient to failures.

This skill is not for designing the demo narrative itself. It is for preparing the **evidence pack** behind the demo.

The goal is to produce:
- required live demo steps
- required backup screenshots, records, or documents
- sample lead and CRM proof items
- proposal / pricing / consultation proof items
- fallback plan for likely live failures
- a final pre-demo checklist

## When to use
Use this skill when the user asks any of the following:
- help me prepare the Class 14 final demo materials
- what proof should the student prepare before presenting
- build a backup pack in case the live demo fails
- create a final demo evidence checklist
- help me reduce live presentation risk for Class 14

## Core principle
A believable Class 14 demo does not need every module to work perfectly live.

It does need:
- one clear live path when possible
- honest labeling of demo-only parts
- prepared evidence for unstable modules
- a fallback story that still proves business value

## What counts as demo proof
Possible proof materials include:
- preloaded website pages
- assistant question list
- screenshots of successful assistant replies
- sample lead submissions
- CRM screenshots or exported lead records
- follow-up email drafts
- proposal / quote screenshot or PDF
- consultation booking flow screenshots
- short screen recordings if an unstable flow must be shown safely

## Input checklist
Collect or infer when available:
- business type
- target customer
- final demo goal
- intended demo order
- available website pages
- assistant status and sample questions
- lead capture path
- CRM or tracking destination
- follow-up asset availability
- quote / proposal / pricing asset availability
- known unstable modules
- known live-working modules
- available screenshots, recordings, or mock records

If information is missing, do not invent a proof asset. Mark it as missing and recommend the smallest acceptable substitute.

## Required preparation flow
### 1. Confirm the intended live revenue path
Identify the narrowest believable path the demo needs to prove, such as:
website -> assistant -> lead capture -> CRM -> next-step proposal

### 2. Split the demo into live items and backup items
For each step, decide whether it should be:
- Live required
- Live preferred with backup
- Backup only
- Optional proof

### 3. Prepare proof by module
Check whether each demo stage has at least one backup artifact.

#### Website proof
Prepare:
- homepage
- service / offer page
- FAQ or trust section
- CTA target page

#### Assistant proof
Prepare:
- 2-3 realistic questions
- expected strong answers
- one screenshot backup for a successful answer

#### Lead capture proof
Prepare:
- one sample lead form submission path
- one prefilled safe demo lead
- one screenshot proving submit success if possible

#### CRM / follow-up proof
Prepare:
- one sample new lead record
- one visible status / note / next action
- one follow-up example

#### Quote / proposal / next-step proof
Prepare one of:
- pricing summary
- proposal template
- quote example
- consultation booking next-step artifact

### 4. Build fallback scenarios
Always prepare fallback logic for:
- assistant answering badly
- form not submitting
- CRM page not loading
- proposal / quote asset missing
- login or network instability

### 5. Create preflight checklist
Produce a short checklist the presenter can use 15 minutes before class/demo.

## Recommended fallback patterns
### Assistant failure
Fallback:
- ask a simpler prepared question
- show a saved successful answer screenshot
- explain that the knowledge base version shown is the validated one

### Form failure
Fallback:
- show a saved screenshot of a successful submission
- switch to a prepared example lead already in CRM
- narrate the submit step instead of retrying live multiple times

### CRM failure
Fallback:
- show a saved CRM screenshot or exported record
- explain the fields and next action
- continue the demo using the prepared follow-up step

### Proposal failure
Fallback:
- show a saved proposal draft or pricing summary
- switch to the next-step consultation path
- clearly say this step is template-backed if not fully automated

## Output format
## Demo 证明目标
## 建议的 live 演示项
## 建议的 backup 证明项
## 网站证明材料
## 助手证明材料
## 线索收集证明材料
## CRM / 跟进证明材料
## 报价 / 提案 / 下一步证明材料
## 常见失败场景与备用方案
## Demo 前 15 分钟检查清单
## 风险与假设

## Chinese classroom guidance
When the request is in Chinese:
- keep the wording practical and presenter-friendly
- do not pretend backup material is live automation
- explicitly label what is live and what is evidence-only
- optimize for a believable classroom presentation, not technical perfection

## Template files
Use these supporting files when useful:
- `templates/final-demo-proof-template-zh.md`
- `references/final-demo-proof-example-zh.md`

## Recommended downstream skills
- use `class14-end-to-end-flow-validator` first to find the best working loop
- use `class14-final-demo-builder` to define the presentation sequence
- use `class14-launch-blocker-fixer` to separate demo risks from launch blockers
- use `final-integration-launch-orchestrator` to include the proof pack in the full output package

## Guardrails
- Do not require every step to be live if that increases failure risk without adding business credibility.
- Do not hide unstable modules; label them clearly and provide backup proof.
- Do not over-prepare too many artifacts; focus on the few items that protect the core revenue narrative.
- Prefer one believable success path with proof over an ambitious but fragile walkthrough.
- End with a short, usable checklist the presenter can follow immediately.
