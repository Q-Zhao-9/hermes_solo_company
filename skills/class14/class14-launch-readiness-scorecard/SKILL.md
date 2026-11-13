---
name: class14-launch-readiness-scorecard
description: Class 14 scoring skill for evaluating how ready a student's AI solo company is for final demo and real launch.
version: 0.1.0
metadata:
  hermes:
    tags: [class14, scorecard, readiness, launch, evaluation]
    related_skills: [class14-system-audit-checker, class14-launch-blocker-fixer, final-integration-launch-orchestrator]
---

# Class 14 Launch Readiness Scorecard

## Purpose
Use this Class 14 skill when a student needs a clear readiness score instead of only a descriptive audit.

The goal is to score the student's current system and return:
- total readiness score
- category-by-category scores
- strongest areas
- weakest areas
- demo readiness judgment
- launch readiness judgment

## Core principle
A scorecard should simplify decision-making, not pretend to be mathematically perfect.

Use the score to help prioritize action.

## Suggested categories and weights
### 1. Offer clarity — 15
Check:
- target customer is clear
- offer is clear
- outcome or promise is understandable
- pricing or pricing logic exists

### 2. Website readiness — 15
Check:
- homepage clarity
- service or product explanation
- CTA clarity
- FAQ / contact path

### 3. Assistant readiness — 15
Check:
- answers core questions
- uses correct facts
- supports next-step conversion

### 4. Lead capture readiness — 10
Check:
- form or contact path exists
- fields are usable
- submissions can be tracked

### 5. CRM and follow-up readiness — 10
Check:
- lead storage exists
- follow-up status exists
- next actions can be managed

### 6. Sales asset readiness — 10
Check:
- proposal / quote path exists
- consultation or sales script exists
- conversion next step is clear

### 7. Traffic readiness — 15
Check:
- SEO / GEO / content path exists
- short-video or publishing path exists
- at least one practical channel exists

### 8. Trust and compliance basics — 10
Check:
- trust assets exist
- policies or basic compliance pages exist when needed
- the system does not create obvious business-risk confusion

## Scoring bands
Use these overall judgments:
- 85-100: launch ready
- 70-84: near launch, fix a few blockers
- 50-69: demo-ready but not launch-ready
- below 50: still foundational

## Scoring rules
For each category, include:
- score
- short explanation
- top missing item
- one improvement suggestion

## Output format
## 总分与总体判断
## 分项评分明细
## 最强模块
## 最弱模块
## 演示就绪度
## 启动就绪度
## 优先改进建议
## 风险与假设

## Template files
Use these supporting files when useful:
- `templates/launch-readiness-scorecard-template-zh.md`

## Guardrails
- Do not pretend the score is exact science.
- Use the score to guide action, not to shame the student.
- If key information is missing, lower confidence and state the assumption clearly.
