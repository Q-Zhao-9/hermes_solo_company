---
name: final-integration-launch-orchestrator
description: Class 14 orchestration skill for turning the student's websites, assistant, lead capture, CRM, content, and sales workflow into one demo-ready AI solo company operating system with explicit flow validation, proof-pack preparation, closeout assignment, and packaged handoff.
version: 0.2.0
metadata:
  hermes:
    tags: [class14, integration, launch, sop, demo, solo-company]
    related_skills: [business-model-commercialization-orchestrator, website-agency-orchestrator, marketing-agency-orchestrator, student-lead-followup, legal-compliance-agent, class14-teacher-workflow-orchestrator, class14-end-to-end-flow-validator, class14-final-demo-proof-builder, class14-student-handoff-assignment-builder, class14-output-package-builder, class14-classroom-master-prompt-builder]
---

# Final Integration Launch Orchestrator

## Purpose
Use this Class 14 skill when a student has already built the main parts of an AI solo company and now needs to connect them into one clear, demo-ready operating system.

For teacher-led classroom delivery, start with `class14-teacher-workflow-orchestrator` as the main class prompt, then use this skill for the end-to-end integration summary itself.

The goal is to check the business flow, validate the strongest and weakest transitions, identify gaps, produce a final demo plan, prepare a demo proof / fallback pack, generate a 30-day launch plan, define a weekly operating SOP, assign one concrete after-class next step, and package the final output cleanly.

## Class 14 outcomes
This skill must produce:
- a short Class 14 key-points recap
- a short AI solo company summary bridge
- end-to-end business flow summary
- strongest working link / weakest broken link / missing transition summary
- blocker priority summary
- final demo plan summary
- demo proof / backup summary
- 30-day launch plan summary
- weekly operating SOP summary
- one concrete after-class assignment
- one clean packaged output

## Input checklist
Collect or infer these inputs:
- current website status
- assistant/chatbot status
- lead capture status
- CRM or follow-up status
- SEO / GEO content status
- short-video or content channel status
- customer service / sales workflow status
- pricing / proposal / offer status
- target launch date
- available weekly capacity

If information is missing, do not invent facts. Mark it as a gap or assumption.

## Workflow
system audit -> end-to-end flow validation -> gap list -> blocker priorities -> demo plan -> demo proof / backup pack -> 30-day launch plan -> weekly SOP -> after-class assignment -> final packaged output

## Required system flow
Use `class14-end-to-end-flow-validator` logic when checking the student against this target flow:
content / SEO / GEO / short video -> website -> AI assistant -> lead form -> CRM -> customer service -> sales follow-up -> quote / proposal -> closed customer

For the flow summary, always identify:
- strongest working link
- weakest broken link
- most harmful missing transition

## Audit rules
For each stage, state:
- what already exists
- what is missing
- what can be demoed now
- what must be fixed before launch

## Demo rules
Use `class14-final-demo-builder` logic for the live sequence and `class14-final-demo-proof-builder` logic for backup preparation.

The final demo should be simple and believable.
It should show:
- website or landing page
- assistant answering real questions
- lead capture / form submission
- CRM or follow-up step
- pricing / proposal handoff

Also specify:
- which items must be live
- which items should have screenshot / recording / CRM / quote backups

## 30-day launch plan rules
Break the plan into 4 weeks:
- Week 1: fix blockers
- Week 2: content / traffic setup
- Week 3: lead follow-up and proposal practice
- Week 4: live outreach / launch / iteration

## Weekly SOP rules
Return a repeatable weekly operating routine covering:
- content publishing
- website / FAQ updates
- lead review
- CRM follow-up
- sales activity
- metrics review
- optimization priorities

## Assignment and packaging rules
Use `class14-student-handoff-assignment-builder` logic to end with one concrete after-class assignment, including:
- 3 concrete actions
- completion criteria
- required submission evidence
- due date

Use `class14-output-package-builder` logic to compress the final answer into one clean teacher-ready or student-ready package instead of leaving the output as scattered analysis sections.

## Chinese classroom optimization
For AI Solo Company classroom use, prefer simplified Chinese by default when the student prompt is in Chinese.

When writing Chinese outputs:
- use practical classroom business language
- keep terms consistent with the course: 网站, 助手, 线索, CRM, 报价, 提案, 启动计划, SOP
- focus on operating reality, not abstract strategy
- include a short Class 14 key-points recap before the integration summary
- explicitly explain how the student's current modules map into the AI solo company summary for Class 14

## Chinese output format
When the request is in Chinese, prefer this section structure, with the final package assembled using `class14-output-package-builder`:

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

The first two sections should stay short. They are not a generic theory lecture; they should remind the student what Class 14 is really about and connect that to the student's current solo-company operating system.

Keep these Chinese section headings aligned with `class14-output-package-builder` so downstream classroom outputs stay consistent across the Class 14 skill set.

## Template files
Use these reusable classroom files when building outputs:
- `templates/final-integration-output-template-zh.md`
- `templates/30-day-launch-plan-template-zh.md`
- `templates/weekly-sop-template-zh.md`
- `references/demo-case-zh.md`
- `references/demo-sample-output-zh.md`
- flow validation support from `class14-end-to-end-flow-validator`
- proof-pack support from `class14-final-demo-proof-builder`:
  - `templates/final-demo-proof-template-zh.md`
  - `references/final-demo-proof-example-zh.md`
- assignment support from `class14-student-handoff-assignment-builder`:
  - `templates/student-handoff-assignment-template-zh.md`
  - `references/student-handoff-assignment-example-zh.md`
- packaging support from `class14-output-package-builder`:
  - `templates/class14-output-package-template-zh.md`
  - `references/class14-output-package-example-zh.md`
  - `references/class14-unified-output-standard-zh.md`
- teacher sample case/output lives in `class14-teacher-workflow-orchestrator`:
  - `references/sample-student-case-zh.md`
  - `references/sample-class14-output-package-zh.md`

## Recommended downstream skills
- teacher-led class sequencing -> `class14-teacher-workflow-orchestrator`
- master prompt construction -> `class14-classroom-master-prompt-builder`
- flow validation deepening -> `class14-end-to-end-flow-validator`
- demo proof / fallback deepening -> `class14-final-demo-proof-builder`
- after-class assignment generation -> `class14-student-handoff-assignment-builder`
- final packaging -> `class14-output-package-builder`

## Guardrails
- Draft only by default.
- Do not claim a module is working unless the student actually has it.
- Prefer a launchable narrow system over an impressive but incomplete system.
- Keep the final demo believable and easy to explain.
- Do not stop at analysis; end with one packaged handoff and one concrete next assignment.
