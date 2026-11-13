---
name: class14-launch-blocker-fixer
description: Class 14 repair-planning skill for converting a student's audit gaps into a prioritized pre-launch fix list.
version: 0.1.0
metadata:
  hermes:
    tags: [class14, blockers, launch, prioritization, repair]
    related_skills: [class14-system-audit-checker, final-integration-launch-orchestrator, website-agency-orchestrator]
---

# Class 14 Launch Blocker Fixer

## Purpose
Use this Class 14 skill when a student already knows what is missing, but needs help deciding what to fix first before launch.

The goal is to convert an audit or gap list into:
- critical pre-launch blockers
- important but non-blocking improvements
- post-launch optimizations
- a short action order

## Core principle
Not every missing feature matters equally.

This skill should reduce overwhelm by forcing the system into three levels:
- must fix before launch
- should improve before launch
- can wait until after launch

## Inputs
Collect or infer when available:
- audit results
- known missing modules
- current business model
- target customer
- launch date or urgency
- available weekly capacity
- which modules already work in demo form
- which modules fail in real use

## Prioritization framework
### P0 — Must fix before launch
Use for items that break the business path, such as:
- unclear offer
- broken CTA or contact path
- broken lead form
- assistant giving wrong core answers
- no place to store leads
- no follow-up path
- no quote / proposal / next step for qualified leads

### P1 — Should improve before launch
Use for items that weaken conversion but do not totally block launch, such as:
- FAQ is too thin
- website proof is weak
- follow-up wording is rough
- pricing explanation is unclear
- traffic engine is still small

### P2 — Can improve after launch
Use for items that are useful but not necessary for first launch, such as:
- extra automation polish
- extra page variants
- more advanced CRM stages
- more content depth
- broader channel expansion

## Decision rules
For each issue, explain:
- why it matters
- why it belongs in P0, P1, or P2
- the consequence if left unfixed
- the smallest acceptable fix

## Repair rules
- Prefer smallest practical repair over full redesign.
- Prefer repairs that restore the full revenue path.
- Do not recommend large feature expansion if a narrow launch path already exists.
- Keep the plan realistic for a solo operator.

## Output format
## 阻塞项总体判断
## P0 启动前必须修
## P1 启动前建议补强
## P2 启动后持续优化
## 最小可启动修复路径
## 本周修复顺序建议
## 风险与假设

## Template files
Use these supporting files when useful:
- `templates/blocker-priority-matrix-zh.md`

## Guardrails
- Do not turn this into a giant roadmap.
- Limit P0 to the smallest set that unlocks launch.
- Be explicit when a problem is only a polish issue, not a blocker.
