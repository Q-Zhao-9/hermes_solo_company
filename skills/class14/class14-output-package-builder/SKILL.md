---
name: class14-output-package-builder
description: Class 14 packaging skill for turning audit, demo, blocker, launch-plan, SOP, assignment, and course recap outputs into one clean teacher-ready or student-ready deliverable.
version: 0.2.0
metadata:
  hermes:
    tags: [class14, output-package, classroom, handoff, teacher, launch]
    related_skills: [class14-teacher-workflow-orchestrator, final-integration-launch-orchestrator, class14-end-to-end-flow-validator, class14-final-demo-builder, class14-final-demo-proof-builder, class14-student-handoff-assignment-builder, class14-classroom-master-prompt-builder]
---

# Class 14 Output Package Builder

## Purpose
Use this Class 14 skill when the individual analysis pieces already exist, but the teacher needs to merge them into one clean classroom deliverable.

This skill is for packaging, not for deep diagnosis.

The goal is to turn scattered Class 14 outputs into one reviewable package containing:
- a short Class 14 key-points recap
- a short AI solo company summary bridge
- readiness verdict
- end-to-end flow summary
- blocker priorities
- final demo plan
- demo proof / backup pack summary
- 30-day launch plan
- weekly operating SOP
- one after-class assignment

## When to use
Use this skill when the user asks any of the following:
- package the Class 14 output
- combine these Class 14 sections into one document
- make a teacher-ready Class 14 report
- create the final student handoff package
- organize the final integration output for class delivery

## Core principle
A good Class 14 package should feel like a decision-ready operating memo.

It should:
- be easy for a teacher to present or send
- be easy for a student to review after class
- preserve priorities without turning into a giant report
- clearly separate what is ready now from what still needs work

## Input checklist
Collect or infer when available:
- student name
- business type
- target customer
- current overall readiness verdict
- end-to-end flow findings
- top blockers and priority labels
- final demo plan
- demo proof / fallback assets
- 30-day launch plan
- weekly SOP
- after-class assignment
- review date or next checkpoint if known

If some sections are missing, do not invent them. Mark them as `Pending`, `Missing`, or `Needs confirmation`.

## Packaging workflow
### 1. Start with a short course recap and solo-company bridge
Open with two short sections:
- what Class 14 is really about
- how the student's current modules translate into an AI solo company operating summary

Keep these sections short and practical. They should frame the package, not become a theory essay.

### 2. Start with the one-line verdict
Open the system conclusion with a short teacher-style verdict such as:
- demo-ready but not launch-ready
- narrow launch-ready with follow-up risk
- strong website + assistant, weak lead handling

### 3. Compress the business flow
Summarize the real operating path in one short chain, for example:
traffic -> website -> assistant -> lead capture -> CRM -> follow-up -> proposal

Then note:
- strongest link
- weakest link
- most urgent missing transition

### 4. Keep blockers ranked
Limit the blocker section to:
- P0 critical blockers
- P1 important gaps
- P2 polish items

Do not let cosmetic notes dominate the package.

### 5. Convert the demo into a presenter-ready summary
Keep demo guidance concise:
- objective
- live sequence
- backup sequence
- end close / CTA

If a detailed script exists elsewhere, reference it instead of duplicating everything.

### 6. Include only the proof assets that reduce risk
Summarize the demo proof pack as:
- required live items
- required backup items
- missing proof items to prepare before presenting

### 7. End with actionability
The last sections must help the student act after class:
- 30-day launch plan
- weekly SOP
- one after-class assignment
- next review checkpoint

## Audience modes
### Teacher-ready package
Use when the package is for classroom delivery or instructor review.
Tone:
- direct
- practical
- evaluative but supportive

### Student-ready package
Use when the package will be sent to the student after class.
Tone:
- clear
- encouraging
- highly actionable

### Hybrid package
Use when one version should work for both teacher presentation and student follow-up.
Default to this if the user does not specify.

## Output format
## 第 14 课重点回顾
## 如何把这些信息用于 AI 一人公司总结
## 第 14 课整体结论
## 学员当前系统状态摘要
## 端到端业务流程结论
## 阻塞项优先级
## 最终演示方案摘要
## Demo 证明材料与备用方案摘要
## 未来 30 天启动计划摘要
## 每周运营 SOP 摘要
## 课后唯一重点作业
## 下次复盘检查点
## 风险与假设

## Chinese classroom guidance
When the request is in Chinese:
- use short section summaries, not long essays
- keep labels consistent with the course vocabulary
- separate “能演示” from “能启动” clearly
- highlight the single most important next action near the end
- make the package readable on one pass by a teacher or student
- keep the “第 14 课重点回顾” and “如何把这些信息用于 AI 一人公司总结” sections short, practical, and tightly tied to the student's current system

## Template files
Use these supporting files when useful:
- `templates/class14-output-package-template-zh.md`
- `references/class14-output-package-example-zh.md`
- `references/class14-unified-output-standard-zh.md`

## Recommended upstream skills
Use these skills first when the corresponding material is not yet prepared:
- `class14-system-audit-checker`
- `class14-end-to-end-flow-validator`
- `class14-launch-blocker-fixer`
- `class14-final-demo-builder`
- `class14-final-demo-proof-builder`
- `class14-30-day-launch-plan`
- `class14-weekly-operations-sop`
- `class14-student-handoff-assignment-builder`

## Recommended downstream skills
- use `class14-teacher-workflow-orchestrator` when the whole class still needs to be run live
- use `final-integration-launch-orchestrator` when the package should be regenerated from a fresh system analysis

## Guardrails
- Do not repeat full long-form content from every section; compress it.
- Do not blur demo readiness and launch readiness.
- Do not bury the top blocker under secondary notes.
- Do not end without a concrete next checkpoint.
- Prefer one clean handoff document over multiple disconnected summaries.
