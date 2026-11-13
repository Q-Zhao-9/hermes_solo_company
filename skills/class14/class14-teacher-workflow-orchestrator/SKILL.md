---
name: class14-teacher-workflow-orchestrator
description: Class 14 teacher-facing orchestration skill for running the final AI solo company integration class from opening audit through flow validation, demo design, proof-pack preparation, 30-day launch plan, weekly SOP, closeout assignment, course recap framing, and packaged handoff.
version: 0.3.0
metadata:
  hermes:
    tags: [class14, teacher, classroom, orchestrator, demo, launch]
    related_skills: [class14-system-audit-checker, class14-end-to-end-flow-validator, class14-final-demo-builder, class14-final-demo-proof-builder, class14-launch-blocker-fixer, class14-30-day-launch-plan, class14-weekly-operations-sop, class14-student-handoff-assignment-builder, class14-output-package-builder, class14-launch-readiness-scorecard, class14-classroom-master-prompt-builder, final-integration-launch-orchestrator]
---

# Class 14 Teacher Workflow Orchestrator

## Purpose
Use this skill as the **teacher's main Class 14 operating prompt** when guiding a student through the final AI solo company integration session.

The goal is not just to evaluate the student. The goal is to help the student leave the class with:
- a short Class 14 key-points recap
- a short AI solo company summary bridge
- a clear current-system audit
- a validated end-to-end business flow
- a believable final demo path
- a prepared demo proof / backup pack
- a ranked blocker list
- a 30-day launch plan
- a weekly operating SOP
- one concrete after-class assignment
- one clean packaged classroom handoff

## When to use
Use this skill when the user asks any of the following:
- help me run Class 14
- create the Class 14 teacher prompt
- give me the teacher workflow for the final class
- orchestrate the final integration class
- turn these Class 14 skills into one classroom flow

## Core teacher principle
The teacher should behave like an operator-coach, not only an evaluator.

Follow this order:
1. open the class and define the target
2. audit what is really built
3. validate the end-to-end business flow
4. identify blockers and rank them
5. simplify the final demo
6. prepare the demo proof / backup pack
7. define the next 30 days
8. define the weekly SOP
9. close with one clear assignment
10. package the final teacher/student handoff

## Inputs
Collect or infer when available:
- student name
- business type
- target customer
- website status
- assistant or chatbot status
- lead capture status
- CRM / follow-up status
- customer service status
- sales / proposal status
- traffic / SEO / GEO / short-video status
- launch goal or target date
- available weekly operating time
- known blockers

If information is missing, do not invent it. Mark it as `Unknown`, `Missing`, or `Needs verification`.

## Main classroom workflow
### Phase 1 — Class opening
Teacher objectives:
- confirm the student's business and current build scope
- explain that Class 14 is about integration, launch readiness, and operating reality
- define what “good enough to demo” means

### Phase 2 — System audit
Use `class14-system-audit-checker` logic.
Check:
- website
- AI assistant
- lead capture
- CRM
- customer service
- sales follow-up
- pricing / proposal
- traffic / content

For each module, state:
- what exists now
- what is missing
- what can be demoed now
- what blocks launch

### Phase 3 — End-to-end flow mapping
Use `class14-end-to-end-flow-validator` logic.
Check the student against this target chain:
content / SEO / GEO / short video -> website -> AI assistant -> lead capture -> CRM -> customer service -> sales follow-up -> quote / proposal -> customer

Teacher output here:
- strongest working link
- weakest broken link
- one missing transition that most hurts launch readiness
- 2-4 bullets that recap the real Class 14 integration lesson from this student's case
- 2-4 bullets that translate the student's current modules into an AI solo company operating summary

### Phase 4 — Blocker prioritization
Use `class14-launch-blocker-fixer` logic.
Rank issues as:
- P0 critical blocker
- P1 important but non-fatal
- P2 optimization / polish

Prioritize business blockers over cosmetic website issues unless the cosmetic issue blocks trust or conversion.

### Phase 5 — Final demo simplification
Use `class14-final-demo-builder` logic.
The final demo should be short, clear, and believable.
It should usually include:
- website / landing page
- AI assistant answering real questions
- lead capture or inquiry handoff
- CRM / follow-up step
- quote / proposal or next-step handoff

Teacher must reduce complexity if the student's system is incomplete.
Prefer a narrow believable demo over an ambitious broken one.

### Phase 6 — Demo proof / fallback preparation
Use `class14-final-demo-proof-builder` logic.
Teacher output here:
- which steps must be shown live
- which screenshots, CRM records, recordings, or quote assets must be prepared as backup
- what fallback to use if assistant, form, CRM, or proposal steps fail live

### Phase 7 — 30-day launch plan
Use `class14-30-day-launch-plan` logic.
Return a 4-week launch path:
- Week 1: fix critical blockers
- Week 2: improve trust assets and content
- Week 3: practice follow-up and proposal flow
- Week 4: launch, outreach, and review

### Phase 8 — Weekly operating SOP
Use `class14-weekly-operations-sop` logic.
Include:
- content publishing
- website / FAQ updates
- lead review
- CRM follow-up
- sales actions
- metrics review
- next optimization priority

### Phase 9 — Class close / assignment handoff
Use `class14-student-handoff-assignment-builder` logic.
Teacher closes with:
- one-sentence readiness verdict
- top 3 priorities
- one after-class assignment due before next review
- required submission evidence and due date

### Phase 10 — Final packaged output
Use `class14-output-package-builder` logic.
Return one final teacher-ready or student-ready package that compresses the full class into a clean handoff document.

The final package should explicitly open with:
- `## 第 14 课重点回顾`
- `## 如何把这些信息用于 AI 一人公司总结`

These two sections should be short, practical, and tied to the student's actual modules, not generic theory.

## Output package
Prefer this full output structure in Chinese classroom use, with the final package assembled using `class14-output-package-builder`:

```markdown
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
```

If the teacher also wants a separate opening note about classroom intent, keep it outside the final packaged output so the package headings stay aligned with `class14-output-package-builder`.

## Teacher tone rules
- Be direct, practical, and encouraging.
- Do not praise vague ideas without evidence.
- Do not overload the student with too many fixes.
- Keep the class moving toward one believable launch path.
- Prefer business-operating language over technical jargon.
- Keep the opening recap and AI solo company summary sections concise and grounded in the student's actual system.

## Template files
Use these supporting files when useful:
- `templates/class14-teacher-orchestrator-prompt-zh.md`
- `references/class14-teacher-runbook-zh.md`
- `references/sample-student-case-zh.md`
- `references/sample-class14-output-package-zh.md`
- packaging support from `class14-output-package-builder`:
  - `templates/class14-output-package-template-zh.md`
  - `references/class14-output-package-example-zh.md`
  - `references/class14-unified-output-standard-zh.md`
- assignment support from `class14-student-handoff-assignment-builder`:
  - `templates/student-handoff-assignment-template-zh.md`
  - `references/student-handoff-assignment-example-zh.md`
- proof-pack support from `class14-final-demo-proof-builder`:
  - `templates/final-demo-proof-template-zh.md`
  - `references/final-demo-proof-example-zh.md`

## Recommended downstream skills
- audit focus -> `class14-system-audit-checker`
- flow-validation focus -> `class14-end-to-end-flow-validator`
- demo focus -> `class14-final-demo-builder`
- proof-pack focus -> `class14-final-demo-proof-builder`
- blocker focus -> `class14-launch-blocker-fixer`
- launch planning focus -> `class14-30-day-launch-plan`
- SOP focus -> `class14-weekly-operations-sop`
- assignment focus -> `class14-student-handoff-assignment-builder`
- packaging focus -> `class14-output-package-builder`
- scoring focus -> `class14-launch-readiness-scorecard`
- teacher master prompt construction -> `class14-classroom-master-prompt-builder`
- full end-to-end integration summary -> `final-integration-launch-orchestrator`

## Guardrails
- Draft only by default.
- Do not claim anything is production-ready unless the student can actually operate it.
- Separate demo readiness from launch readiness.
- Keep the teacher workflow modular so one section can be reused alone.
- Always end with one concrete next step.
