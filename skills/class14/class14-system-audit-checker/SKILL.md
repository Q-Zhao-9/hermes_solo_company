---
name: class14-system-audit-checker
description: Class 14 audit skill for checking whether a student's AI solo company system is complete enough to demo and launch.
version: 0.1.0
metadata:
  hermes:
    tags: [class14, audit, readiness, systems, launch]
    related_skills: [final-integration-launch-orchestrator, website-agency-orchestrator, class12-customer-service-sales-orchestrator, business-model-commercialization-orchestrator]
---

# Class 14 System Audit Checker

## Purpose
Use this Class 14 skill when a student already has multiple AI solo company modules built and now needs a clear audit of what is actually ready.

The goal is to evaluate the student's current system and produce:
- current system status
- end-to-end flow audit
- demo readiness status
- launch readiness status
- missing modules and blockers

## When to use
Use this skill when the user asks any of the following:
- what is still missing before Class 14 final demo
- can this business system launch now
- what parts of my AI solo company are incomplete
- audit my current website / assistant / CRM / sales flow

## Input checklist
Collect or infer when available:
- business type or commercial path
- target customer
- current website status
- AI assistant or chatbot status
- lead capture or form status
- CRM or lead tracking status
- customer-service workflow status
- sales follow-up workflow status
- offer / pricing / proposal status
- SEO / GEO / content status
- short-video or traffic-channel status
- trust assets such as FAQ, case studies, testimonials, or policies

If information is missing, do not invent facts. Mark the item as unknown or missing.

## Required audit flow
Check the system against this target chain:
content / SEO / GEO / short video -> website -> AI assistant -> lead capture -> CRM -> customer service -> sales follow-up -> quote / proposal -> customer

## Audit rules
For each stage, report:
- what already exists
- what is missing
- what can be demoed now
- what blocks real launch
- whether the issue is critical or non-critical

## Evaluation categories
### 1. Website readiness
Check:
- homepage clarity
- service / product explanation
- CTA clarity
- FAQ presence
- contact path

### 2. Assistant readiness
Check:
- answers core questions
- uses correct business facts
- guides user to next step
- avoids obvious hallucinations

### 3. Lead capture readiness
Check:
- form exists
- fields are sufficient
- submissions are stored
- next action after submit is defined

### 4. CRM readiness
Check:
- leads are recorded
- status or stage exists
- operator can review and follow up

### 5. Customer-service readiness
Check:
- FAQ or response logic exists
- common inquiries can be answered
- escalation boundaries are clear

### 6. Sales readiness
Check:
- lead qualification exists
- follow-up messaging exists
- quote or proposal path exists
- closing next step is clear

### 7. Traffic readiness
Check:
- SEO or GEO content exists
- short-video or publishing path exists
- at least one realistic traffic source exists

### 8. Offer readiness
Check:
- target customer is clear
- offer is clear
- pricing or pricing logic exists
- proposal / package can be shown

## Readiness labels
Use these labels when summarizing each category:
- Ready
- Partially ready
- Demo only
- Not ready

## Output format
## 当前系统整合结论
## 端到端业务流程检查
## 模块审计明细
## 演示就绪度判断
## 启动就绪度判断
## 缺口与阻塞项
## 风险与假设

## Template files
Use these supporting files when useful:
- `templates/system-audit-template-zh.md`
- `references/audit-example-zh.md`

## Guardrails
- Prefer practical business readiness over technical completeness.
- Do not say a module is ready unless the student can actually show or operate it.
- Separate demo readiness from launch readiness.
- Prefer a narrow launchable system over a large incomplete one.
