---
name: class14-student-handoff-assignment-builder
description: Class 14 closeout skill for turning a student's current launch state into one clear after-class assignment with concrete actions, evidence requirements, and due date.
version: 0.1.0
metadata:
  hermes:
    tags: [class14, handoff, assignment, classroom, accountability, launch]
    related_skills: [class14-teacher-workflow-orchestrator, class14-launch-blocker-fixer, class14-30-day-launch-plan, class14-weekly-operations-sop, final-integration-launch-orchestrator]
---

# Class 14 Student Handoff Assignment Builder

## Purpose
Use this Class 14 skill at the end of the final integration class when the teacher needs to convert a broad discussion into one concrete after-class assignment.

The goal is to produce a short handoff that tells the student exactly:
- what the single most important next assignment is
- why this assignment matters now
- the 3 concrete actions to complete
- what “done” looks like
- what evidence the student must submit
- when it is due

## When to use
Use this skill when the user asks any of the following:
- help me write the Class 14 homework
- turn this into one clear student assignment
- define the post-class handoff
- give the student the next step after Class 14
- create an accountable follow-up task for the student

## Core principle
A good Class 14 assignment is not a long task list.

It should:
- remove ambiguity
- focus on one business-critical outcome
- be realistic for one operator
- produce proof the teacher can review

The assignment should usually unlock one of these outcomes:
- a working lead capture path
- a believable final demo path
- a real follow-up / quote path
- a launchable first traffic / outreach step

## Input checklist
Collect or infer when available:
- student name
- business type
- current strongest working module
- current biggest blocker
- one business outcome that matters most next
- available weekly time
- next review date if known
- whether the assignment is for demo readiness, launch readiness, or both
- what proof artifacts the student can realistically submit

If details are missing, keep the assignment conservative and label assumptions clearly.

## Assignment selection rules
### 1. Choose only one primary assignment
Do not give 3 separate strategic objectives.
Pick the single assignment that most improves the student's ability to:
- demo credibly
- launch credibly
- or move from demo to real customer action

### 2. Base the assignment on the biggest bottleneck
Typical assignment categories:
- fix missing website CTA / contact path
- improve assistant answers for common buyer questions
- connect lead capture to CRM / follow-up
- prepare quote / proposal / pricing package
- publish first trust-building content asset
- practice one end-to-end demo and collect proof

### 3. Break it into exactly 3 actions when possible
Each action should be concrete, observable, and finishable.
Avoid vague actions like:
- improve the website
- optimize the business
- make the assistant better

Prefer actions like:
- add one pricing FAQ section to the service page
- test and capture one successful lead submission
- create one quote template for the core offer

### 4. Define completion evidence
The handoff must specify what the student submits back, such as:
- URL
- screenshot
- short screen recording
- CRM screenshot
- proposal PDF
- copy-paste of assistant Q&A examples
- completed checklist

### 5. Set a realistic deadline
If the user does not provide a due date:
- default to within 3-7 days for narrow tasks
- default to within 7-14 days for broader launch tasks

## Recommended assignment types
### Demo-readiness assignment
Use when the system is partly built but fragile.
Output should focus on:
- making the core demo path believable
- reducing live failure risk
- gathering proof artifacts

### Launch-readiness assignment
Use when the student can demo but cannot yet operate the business.
Output should focus on:
- lead capture
- follow-up
- quote / proposal
- trust assets
- first traffic or outreach

### Hybrid assignment
Use when one narrow task improves both demo and launch readiness.
Example:
- connect FAQ -> assistant -> form -> CRM and collect proof

## Output format
## 课后唯一重点作业
## 为什么这个作业现在最重要
## 3 个具体行动项
## 完成标准
## 需提交的证明材料
## 截止时间
## 下次复盘重点
## 风险与假设

## Chinese classroom guidance
When the request is in Chinese:
- write in direct teacher-to-student language
- keep the assignment scannable and actionable
- avoid overloaded homework lists
- explicitly define submission evidence
- make the task feel achievable within the student's current capacity

## Template files
Use these supporting files when useful:
- `templates/student-handoff-assignment-template-zh.md`
- `references/student-handoff-assignment-example-zh.md`

## Recommended downstream skills
- use `class14-launch-blocker-fixer` first if the top bottleneck is unclear
- use `class14-final-demo-proof-builder` if the assignment is mainly about demo evidence
- use `class14-30-day-launch-plan` if the assignment should feed into a broader next-month plan
- use `class14-weekly-operations-sop` if the assignment should evolve into recurring weekly habits
- use `final-integration-launch-orchestrator` if the handoff should be part of a full Class 14 output package

## Guardrails
- Do not assign too many parallel tasks.
- Do not choose a cosmetic task unless it directly affects trust or conversion.
- Do not define success only as “worked on it”; require evidence.
- Keep the workload realistic for a solo student.
- End with a reviewable handoff, not a motivational speech.
