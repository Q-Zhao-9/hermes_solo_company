---
name: class14-end-to-end-flow-validator
description: Class 14 integration skill for checking whether a student's website, assistant, lead capture, CRM, customer service, sales, and quote flow are truly connected into one working launch path.
version: 0.1.0
metadata:
  hermes:
    tags: [class14, integration, flow-validation, launch, demo, classroom]
    related_skills: [class14-system-audit-checker, class14-launch-blocker-fixer, class14-final-demo-builder, final-integration-launch-orchestrator, class14-teacher-workflow-orchestrator]
---

# Class 14 End-to-End Flow Validator

## Purpose
Use this Class 14 skill when a student appears to have multiple business modules built, but the teacher needs to verify whether those modules actually connect into a usable end-to-end flow.

This skill is not a generic audit. It is specifically for validating **transitions** between stages.

The goal is to determine:
- which links in the business chain are truly working
- which links are broken or unverified
- what the smallest believable demo-ready loop is
- what the smallest launchable loop is
- which broken transition most hurts launch readiness

## When to use
Use this skill when the user asks any of the following:
- help me check whether this student's whole Class 14 flow is actually connected
- which part of the website -> lead -> CRM -> sales chain is broken
- what is the weakest link before final demo
- validate the student's end-to-end business flow
- find the most important handoff gap before launch

## Core principle
A module existing is not the same as a transition working.

For example:
- a website page existing does not prove the CTA leads somewhere useful
- a form existing does not prove submissions reach CRM
- a CRM existing does not prove follow-up happens
- a proposal template existing does not prove qualified leads receive a next step

This skill must focus on the **handoffs between modules**.

## Target business chain
Validate the student's system against this Class 14 target chain:

content / SEO / GEO / short video -> website -> AI assistant -> lead capture -> CRM -> customer service -> sales follow-up -> quote / proposal -> customer

## Input checklist
Collect or infer when available:
- business type
- target customer
- main offer
- current website pages and CTA path
- assistant status and example questions it can answer
- lead capture status
- CRM or tracking status
- customer service response path
- sales follow-up path
- quote / proposal / consultation next-step path
- current traffic or content path
- known demo-only modules
- known live-working modules

If information is missing, do not invent it. Mark the transition as:
- Unknown
- Needs verification
- Demo only
- Not connected

## Required validation flow
Check the chain one transition at a time.

### 1. Content / traffic -> website
Check:
- whether the student has at least one realistic traffic or discovery source
- whether that source points to a usable landing page or website entry page

### 2. Website -> AI assistant or CTA
Check:
- whether the website clearly explains the offer
- whether the user can reach the assistant or CTA naturally
- whether the assistant or CTA supports next-step conversion

### 3. AI assistant / CTA -> lead capture
Check:
- whether the assistant or page leads to a form, contact action, booking, or inquiry handoff
- whether the next step is obvious enough for a prospect

### 4. Lead capture -> CRM
Check:
- whether submitted leads are stored somewhere usable
- whether the operator can see and act on new leads

### 5. CRM -> customer service or follow-up
Check:
- whether new leads trigger or support a response path
- whether the student has a status, note, or next-action mechanism

### 6. Follow-up -> quote / proposal / consultation next step
Check:
- whether qualified leads can be moved to a real next step
- whether quote, proposal, pricing summary, or consultation booking exists

### 7. Quote / proposal -> customer advancement
Check:
- whether the system defines what happens after proposal delivery
- whether there is a believable path toward closing or continued follow-up

## Transition labels
Use one of these labels for each transition:
- Connected
- Partially connected
- Demo only
- Not connected
- Unknown

## Required synthesis
After checking all transitions, explicitly identify:
- strongest working link
- weakest broken link
- the single broken transition that most hurts launch readiness
- the smallest believable demo loop
- the smallest believable launch loop

## Output format
## 端到端链路总体判断
## 分段链路验证
## 已打通的关键连接
## 未打通或未验证的关键连接
## 最强工作链路
## 最弱断裂链路
## 最影响启动的断点
## 最小可演示闭环
## 最小可启动闭环
## Demo 前必须补的连接
## Launch 前必须补的连接
## 风险与假设

## Chinese classroom guidance
When the request is in Chinese:
- prefer practical business wording
- name exact handoff problems clearly
- distinguish “有模块” from “能衔接”
- keep focus on launch reality, not abstract architecture

## Template files
Use these supporting files when useful:
- `templates/flow-validator-template-zh.md`
- `references/flow-validator-example-zh.md`

## Recommended downstream skills
- use `class14-system-audit-checker` first when the module status is still unclear
- use `class14-launch-blocker-fixer` after this skill to prioritize repairs
- use `class14-final-demo-builder` after this skill to design a believable demo around the best working loop
- use `final-integration-launch-orchestrator` to summarize the full result package

## Guardrails
- Do not confuse existence of assets with working transitions.
- Do not assume automation is live unless the student can actually show it.
- Do not mark a transition Connected if the output only implies a future intention.
- Prefer identifying one minimum working path over demanding a fully mature system.
- Keep the conclusion actionable: point to the next transition to fix.
