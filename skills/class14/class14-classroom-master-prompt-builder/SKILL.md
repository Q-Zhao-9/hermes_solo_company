---
name: class14-classroom-master-prompt-builder
description: Class 14 meta-orchestration skill for building one complete teacher-ready master prompt that explicitly sequences audit, flow validation, demo proof, launch planning, handoff assignment, course recap framing, and final output packaging.
version: 0.2.0
metadata:
  hermes:
    tags: [class14, master-prompt, teacher, classroom, orchestrator, packaging]
    related_skills: [class14-teacher-workflow-orchestrator, final-integration-launch-orchestrator, class14-end-to-end-flow-validator, class14-final-demo-proof-builder, class14-student-handoff-assignment-builder, class14-output-package-builder]
---

# Class 14 Classroom Master Prompt Builder

## Purpose
Use this Class 14 skill when the teacher does not just need a report or one section, but needs a **single reusable master prompt** that can drive the whole Class 14 session and final deliverable.

This skill is for prompt construction and orchestration design.
It turns the modular Class 14 skill set into one teacher-ready operating prompt.

The goal is to produce:
- one complete teacher-ready master prompt
- explicit phase order
- clear handoff between sub-skills
- required output structure
- teacher instructions for handling missing information
- final packaging instructions for the classroom deliverable
- default inclusion of a short Class 14 recap section
- default inclusion of a short AI solo company summary bridge section

## When to use
Use this skill when the user asks any of the following:
- build the master prompt for Class 14
- combine all Class 14 skills into one runnable prompt
- create the teacher super prompt for the final class
- make one reusable Class 14 operating prompt
- sequence the new Class 14 skills into one workflow

## Core principle
The master prompt should not try to do everything at once without structure.

It should:
- move in a strict classroom order
- explicitly call the right sub-skill logic at the right phase
- keep teacher outputs practical and compressed
- end with one clean student-ready / teacher-ready package

## When this is better than the base orchestrators
Use this skill instead of only using `class14-teacher-workflow-orchestrator` when:
- you want explicit references to the newer modular Class 14 skills
- you want a prompt that can be copied into another agent or teaching workflow
- you want a stricter final package requirement
- you want the class closeout and proof-pack logic to be guaranteed, not implicit

## Input checklist
Collect or infer when available:
- student name
- business type
- target customer
- current website status
- assistant status
- lead capture status
- CRM / follow-up status
- pricing / proposal status
- content / traffic status
- top known blockers
- launch goal or review goal
- whether the class is teacher-facing, student-facing, or hybrid
- whether the user wants a short prompt or full prompt

If inputs are incomplete, the master prompt must instruct the agent to mark unknowns instead of inventing facts.

## Required orchestration order
The master prompt should explicitly sequence these logic blocks:

### Phase 1 — System audit
Use `class14-system-audit-checker` logic.
Goal:
- establish what is actually built
- mark missing items
- separate demoable modules from launch-critical gaps

### Phase 2 — End-to-end flow validation
Use `class14-end-to-end-flow-validator` logic.
Goal:
- identify strongest working link
- identify weakest broken link
- identify the single most harmful missing transition
- derive 2-4 bullets for `第 14 课重点回顾` grounded in the student's actual case
- derive 2-4 bullets for `如何把这些信息用于 AI 一人公司总结` grounded in the student's actual operating chain

### Phase 3 — Blocker prioritization
Use `class14-launch-blocker-fixer` logic.
Goal:
- rank issues into P0 / P1 / P2
- keep business-critical blockers above cosmetic polish

### Phase 4 — Final demo design
Use `class14-final-demo-builder` logic.
Goal:
- define the shortest believable live demo path
- keep the demo connected to revenue logic

### Phase 5 — Demo proof and fallback pack
Use `class14-final-demo-proof-builder` logic.
Goal:
- define which parts must be live
- define which proof assets should be prepared as backup
- reduce live demo fragility

### Phase 6 — 30-day launch plan
Use `class14-30-day-launch-plan` logic.
Goal:
- create a realistic four-week path after class

### Phase 7 — Weekly operating SOP
Use `class14-weekly-operations-sop` logic.
Goal:
- create a repeatable operator rhythm

### Phase 8 — Student handoff assignment
Use `class14-student-handoff-assignment-builder` logic.
Goal:
- end with one concrete post-class assignment
- define required submission evidence and due date

### Phase 9 — Final package assembly
Use `class14-output-package-builder` logic.
Goal:
- compress all prior sections into one teacher-ready or student-ready package
- explicitly open the final package with `## 第 14 课重点回顾`
- explicitly follow with `## 如何把这些信息用于 AI 一人公司总结`
- keep both opening sections short, practical, and tied to the student's real modules and operating path

## Master prompt writing rules
When building the prompt:
- tell the agent to behave like an operator-teacher, not a generic strategist
- instruct the agent to mark unknowns clearly
- instruct the agent to prefer narrow believable systems over ambitious incomplete ones
- require concise sections and reviewable outputs
- require a final package near the end, not scattered mini-summaries
- make the opening Class 14 recap and AI solo company summary sections mandatory in the generated prompt

## Output options
### Short master prompt
Use when the teacher wants a compact reusable prompt.
The output should contain:
- role framing
- ordered phases
- required final output structure
- core guardrails

### Full master prompt
Use when the teacher wants a fully copy-pasteable classroom prompt.
The output should contain:
- role framing
- input checklist
- phase-by-phase instructions
- quality rules
- Chinese output format
- guardrails
- final packaging instructions

## Preferred output format
When the request is in Chinese, prefer this structure:

## Prompt目标
## 建议使用场景
## Master Prompt（可直接复制）
## Prompt里应显式串联的子技能
## 输出结构要求
## 使用注意事项

## Chinese classroom guidance
When the request is in Chinese:
- write the prompt in direct teacher-operating language
- avoid abstract pedagogy wording
- keep phase transitions explicit
- make the final package requirement impossible to miss
- ensure the prompt ends with a reviewable class deliverable
- require `第 14 课重点回顾` and `如何把这些信息用于 AI 一人公司总结` near the top of the final output structure

## Template files
Use these supporting files when useful:
- `templates/class14-master-prompt-template-zh.md`
- `references/class14-master-prompt-example-zh.md`
- canonical packaging standard from `class14-output-package-builder`:
  - `references/class14-unified-output-standard-zh.md`

## Recommended upstream skills
Load or reference these when the master prompt should align tightly with current Class 14 modules:
- `class14-teacher-workflow-orchestrator`
- `final-integration-launch-orchestrator`
- `class14-output-package-builder`
- `class14-final-demo-proof-builder`
- `class14-student-handoff-assignment-builder`

## Guardrails
- Do not produce a master prompt that skips the closeout assignment.
- Do not omit proof-pack / fallback preparation if the class includes a live demo.
- Do not let the prompt wander into generic startup advice.
- Do not hide missing information; instruct the downstream agent to mark gaps explicitly.
- Do not end the prompt before specifying the final packaged output.
