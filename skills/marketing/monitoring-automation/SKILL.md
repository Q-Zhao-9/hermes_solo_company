---
name: monitoring-automation
description: Create local marketing monitoring queries, schedule handoff records, alert reports, and weekly digests for brand, competitor, lead, keyword, and hashtag watch workflows.
version: 1.0.0
metadata:
  hermes:
    tags: [marketing, monitoring, alerts, competitors, leads, weekly-digest]
    category: marketing
    related_skills: [marketing-agency-orchestrator, lead-detection, competitor-intelligence, marketing-analytics, platform-integration-handoff]
---

# Monitoring Automation

Use this skill when the user wants Hermes to monitor brand mentions,
competitor moves, market trends, hashtags, keywords, or buying-intent lead
signals.

This skill creates local artifacts only. It does not browse the web, start a
real scheduler, call social APIs, reply to comments, send outreach, write CRM
records, or publish anything.

## Commands

Create a saved query:

```bash
scripts/marketing_agency.py create-monitor-query \
  --project-dir "<project dir>" \
  --name "<watch name>" \
  --type lead \
  --query "<saved search query>" \
  --channels "LinkedIn,X,Reddit" \
  --priority high
```

Create local monitor job handoffs:

```bash
scripts/marketing_agency.py schedule-monitor \
  --project-dir "<project dir>" \
  --cadence weekly \
  --owner "marketing ops" \
  --destination "weekly digest"
```

Record an alert found by a human or approved integration:

```bash
scripts/marketing_agency.py record-monitor-alert \
  --project-dir "<project dir>" \
  --query-id "<query id>" \
  --title "<alert title>" \
  --summary "<alert summary>" \
  --severity high \
  --source LinkedIn \
  --url "<source url>"
```

Generate the weekly digest:

```bash
scripts/marketing_agency.py weekly-digest \
  --project-dir "<project dir>" \
  --period "2026-W20" \
  --audience "founder and marketing team"
```

## Artifacts

The workflow writes:

- `docs/monitoring/monitor-queries.md`
- `docs/monitoring/monitor-queries.json`
- `docs/monitoring/monitor-jobs.md`
- `docs/monitoring/monitor-jobs.json`
- `docs/monitoring/monitor-alerts.md`
- `docs/monitoring/monitor-alerts.json`
- `docs/monitoring/weekly-digest.md`
- `docs/monitoring/weekly-digest.json`

## Routing Rules

- For buying-intent alerts, score the lead with `score-lead` before drafting
  outreach.
- For competitor alerts, record a competitor observation with
  `track-competitor` before recommending a response campaign.
- For brand or community alerts, prepare a reviewed response note before any
  public reply.
- For weekly reporting, combine monitor alerts with lead scorecards,
  competitor observations, performance snapshots, and execution evidence.

## Safety

Monitoring artifacts are planning records. They are not permission to contact
people, reply publicly, change campaigns, update CRM records, or publish
content. Ask for explicit approval before any external action.
