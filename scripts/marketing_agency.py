#!/usr/bin/env python3
"""Deterministic helpers for Hermes marketing and SEO agency workflows.

Phase 1 focuses on strategy and campaign memory. Phase 2 adds content planning
and draft generation. Phase 3 adds SEO/GEO planning and blog briefs. Phase 4
adds lead signal definitions, lead scoring, outreach drafts, and CRM export.
Phase 5 adds performance snapshots, optimization recommendations, and manager
dashboards. Phase 6 adds competitor intelligence and trend watch reports.
Phase 7 adds approval packages, execution queues, change logs, and operator
handoffs. It avoids network access and does not publish, message, email, update
CRM records, or modify external systems.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from io import StringIO
import json
import re
from pathlib import Path
from typing import Any


STATE_PATH = Path("docs") / "hermes-marketing-state.json"
CONTENT_DIR = Path("docs") / "content"
SEO_DIR = Path("docs") / "seo"
LEADS_DIR = Path("docs") / "leads"
ANALYTICS_DIR = Path("docs") / "analytics"
COMPETITOR_DIR = Path("docs") / "competitors"
EXECUTION_DIR = Path("docs") / "execution"


@dataclass(frozen=True)
class StrategySpec:
    brand: str
    business: str
    audience: str
    goal: str
    offer: str
    tone: str
    region: str
    project_slug: str


@dataclass(frozen=True)
class CampaignSpec:
    name: str
    objective: str
    audience: str
    offer: str
    channels: list[str]
    duration: str
    cta: str
    campaign_slug: str


def slugify(value: str, fallback: str = "marketing") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    return slug[:64].strip("-") or fallback


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def read_state(state_file: Path) -> dict[str, Any]:
    if not state_file.exists():
        return default_state()
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default_state()
    if not isinstance(data, dict):
        return default_state()
    data.setdefault("version", 1)
    data.setdefault("strategies", [])
    data.setdefault("campaigns", [])
    data.setdefault("contentPlans", [])
    data.setdefault("contentDrafts", [])
    data.setdefault("seoPlans", [])
    data.setdefault("blogBriefs", [])
    data.setdefault("leadSignals", [])
    data.setdefault("leadScorecards", [])
    data.setdefault("outreachDrafts", [])
    data.setdefault("crmExports", [])
    data.setdefault("performanceSnapshots", [])
    data.setdefault("reviewDashboards", [])
    data.setdefault("competitors", [])
    data.setdefault("competitorObservations", [])
    data.setdefault("competitorReports", [])
    data.setdefault("approvalPackages", [])
    data.setdefault("approvalDecisions", [])
    data.setdefault("operatorHandoffs", [])
    return data


def default_state() -> dict[str, Any]:
    return {
        "version": 1,
        "strategies": [],
        "campaigns": [],
        "contentPlans": [],
        "contentDrafts": [],
        "seoPlans": [],
        "blogBriefs": [],
        "leadSignals": [],
        "leadScorecards": [],
        "outreachDrafts": [],
        "crmExports": [],
        "performanceSnapshots": [],
        "reviewDashboards": [],
        "competitors": [],
        "competitorObservations": [],
        "competitorReports": [],
        "approvalPackages": [],
        "approvalDecisions": [],
        "operatorHandoffs": [],
    }


def write_state(project_dir: Path, state: dict[str, Any]) -> None:
    write_text(project_dir / STATE_PATH, json.dumps(state, indent=2))


def create_strategy(args: argparse.Namespace) -> dict[str, Any]:
    spec = StrategySpec(
        brand=args.brand.strip(),
        business=args.business.strip(),
        audience=args.audience.strip(),
        goal=args.goal.strip(),
        offer=args.offer.strip(),
        tone=args.tone.strip(),
        region=args.region.strip(),
        project_slug=slugify(args.brand),
    )
    root = Path(args.output_dir).expanduser().resolve() / spec.project_slug
    if root.exists() and not args.force:
        return {"ok": False, "error": f"project already exists: {root}", "projectDir": str(root)}
    root.mkdir(parents=True, exist_ok=True)

    strategy = build_strategy(spec)
    strategy_path = root / "docs" / "marketing-strategy.md"
    state_file = root / STATE_PATH
    write_text(strategy_path, render_strategy_markdown(strategy))
    record_strategy(root, strategy)
    return {
        "ok": True,
        "projectDir": str(root),
        "strategy": strategy,
        "strategyPath": str(strategy_path),
        "statePath": str(state_file),
        "next": "Create a campaign with create-campaign, then generate content in Phase 2.",
    }


def build_strategy(spec: StrategySpec) -> dict[str, Any]:
    channels = recommend_channels(spec.business, spec.audience, spec.goal)
    themes = recommend_themes(spec.business, spec.offer, spec.goal)
    funnel = [
        {"stage": "Awareness", "goal": "Teach the market the problem and why it matters.", "channels": channels[:3]},
        {"stage": "Consideration", "goal": "Show proof, use cases, ROI, and objections.", "channels": channels[:4]},
        {"stage": "Conversion", "goal": f"Drive the audience toward: {spec.goal}.", "channels": channels[-3:]},
    ]
    icp = {
        "primary": spec.audience,
        "industries": infer_industries(spec.business, spec.audience),
        "painPoints": infer_pain_points(spec.business, spec.offer),
        "buyingTriggers": infer_buying_triggers(spec.goal, spec.offer),
    }
    return {
        "type": "marketing-strategy",
        "brand": spec.brand,
        "business": spec.business,
        "audience": spec.audience,
        "goal": spec.goal,
        "offer": spec.offer,
        "tone": spec.tone,
        "region": spec.region,
        "icp": icp,
        "positioning": f"{spec.brand} helps {spec.audience} achieve {spec.goal} with {spec.offer}.",
        "channels": channels,
        "themes": themes,
        "funnel": funnel,
        "brandVoice": build_brand_voice(spec.tone),
        "seoFocus": build_seo_focus(spec.business, spec.offer, spec.audience),
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def create_campaign(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    strategy = state.get("lastStrategy", {}) if isinstance(state.get("lastStrategy"), dict) else {}
    channels = parse_list(args.channels) or strategy.get("channels", [])[:3] or ["LinkedIn", "X", "Blog"]
    spec = CampaignSpec(
        name=args.name.strip(),
        objective=args.objective.strip(),
        audience=args.audience.strip() or str(strategy.get("audience") or "target customers"),
        offer=args.offer.strip() or str(strategy.get("offer") or "core offer"),
        channels=[str(channel) for channel in channels],
        duration=args.duration.strip(),
        cta=args.cta.strip(),
        campaign_slug=slugify(args.name, fallback="campaign"),
    )
    campaign = build_campaign(spec, strategy)
    campaign_dir = project_dir / "docs" / "campaigns"
    campaign_path = campaign_dir / f"{spec.campaign_slug}.md"
    write_text(campaign_path, render_campaign_markdown(campaign))
    record_campaign(project_dir, campaign)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "campaign": campaign,
        "campaignPath": str(campaign_path),
        "statePath": str(project_dir / STATE_PATH),
        "next": "Use Phase 2 content commands to create platform-specific posts from this campaign.",
    }


def generate_content_plan(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    campaign = select_campaign(state, args.campaign)
    if not campaign:
        return {"ok": False, "error": "No campaign found. Run create-campaign first."}
    strategy = state.get("lastStrategy", {}) if isinstance(state.get("lastStrategy"), dict) else {}
    weeks = max(1, args.weeks)
    cadence = max(1, args.cadence)
    channels = parse_list(args.channels) or [str(channel) for channel in campaign.get("channels", [])] or ["LinkedIn", "X", "Blog"]
    plan = build_content_plan(campaign, strategy, weeks=weeks, cadence=cadence, channels=channels)
    plan_path = project_dir / CONTENT_DIR / f"{campaign['slug']}-content-calendar.md"
    plan_json_path = project_dir / CONTENT_DIR / f"{campaign['slug']}-content-calendar.json"
    write_text(plan_path, render_content_plan_markdown(plan))
    write_text(plan_json_path, json.dumps(plan, indent=2))
    record_content_plan(project_dir, plan)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "plan": plan,
        "planPath": str(plan_path),
        "planJsonPath": str(plan_json_path),
        "statePath": str(project_dir / STATE_PATH),
        "next": "Generate draft assets with generate-posts, then review before publishing.",
    }


def generate_posts(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    campaign = select_campaign(state, args.campaign)
    if not campaign:
        return {"ok": False, "error": "No campaign found. Run create-campaign first."}
    strategy = state.get("lastStrategy", {}) if isinstance(state.get("lastStrategy"), dict) else {}
    channels = parse_list(args.channels) or [str(channel) for channel in campaign.get("channels", [])] or ["LinkedIn"]
    count = max(1, args.count)
    drafts = build_content_drafts(campaign, strategy, channels=channels, count=count, theme=args.theme, stage=args.stage)
    draft_dir = project_dir / CONTENT_DIR / "drafts"
    draft_path = draft_dir / f"{campaign['slug']}-drafts.md"
    draft_json_path = draft_dir / f"{campaign['slug']}-drafts.json"
    write_text(draft_path, render_drafts_markdown(drafts))
    write_text(draft_json_path, json.dumps(drafts, indent=2))
    record_content_drafts(project_dir, drafts)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "drafts": drafts,
        "draftPath": str(draft_path),
        "draftJsonPath": str(draft_json_path),
        "statePath": str(project_dir / STATE_PATH),
        "message": "Content drafts created for review. Publishing requires explicit approval.",
    }


def generate_seo_plan(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    strategy = state.get("lastStrategy", {}) if isinstance(state.get("lastStrategy"), dict) else {}
    campaign = select_campaign(state, args.campaign)
    if not strategy:
        return {"ok": False, "error": "No strategy found. Run create-strategy first."}
    plan = build_seo_plan(
        strategy,
        campaign,
        focus=args.focus,
        pages=max(1, args.pages),
        region=args.region,
    )
    seo_path = project_dir / SEO_DIR / "seo-geo-plan.md"
    seo_json_path = project_dir / SEO_DIR / "seo-geo-plan.json"
    write_text(seo_path, render_seo_plan_markdown(plan))
    write_text(seo_json_path, json.dumps(plan, indent=2))
    record_seo_plan(project_dir, plan)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "seoPlan": plan,
        "seoPlanPath": str(seo_path),
        "seoPlanJsonPath": str(seo_json_path),
        "statePath": str(project_dir / STATE_PATH),
        "next": "Generate search-intent blog briefs with generate-blog-briefs.",
    }


def generate_blog_briefs(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    strategy = state.get("lastStrategy", {}) if isinstance(state.get("lastStrategy"), dict) else {}
    seo_plan = state.get("lastSeoPlan", {}) if isinstance(state.get("lastSeoPlan"), dict) else {}
    if not strategy:
        return {"ok": False, "error": "No strategy found. Run create-strategy first."}
    briefs = build_blog_briefs(strategy, seo_plan, count=max(1, args.count), intent=args.intent)
    briefs_path = project_dir / SEO_DIR / "blog-briefs.md"
    briefs_json_path = project_dir / SEO_DIR / "blog-briefs.json"
    write_text(briefs_path, render_blog_briefs_markdown(briefs))
    write_text(briefs_json_path, json.dumps(briefs, indent=2))
    record_blog_briefs(project_dir, briefs)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "blogBriefs": briefs,
        "blogBriefsPath": str(briefs_path),
        "blogBriefsJsonPath": str(briefs_json_path),
        "statePath": str(project_dir / STATE_PATH),
        "message": "SEO/GEO blog briefs created for review. Publishing requires explicit approval.",
    }


def define_lead_signals(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    strategy = state.get("lastStrategy", {}) if isinstance(state.get("lastStrategy"), dict) else {}
    if not strategy:
        return {"ok": False, "error": "No strategy found. Run create-strategy first."}
    lead_signals = build_lead_signals(
        strategy,
        channels=parse_list(args.channels),
        signals=parse_list(args.signals),
        negative_signals=parse_list(args.negative_signals),
    )
    signals_path = project_dir / LEADS_DIR / "lead-signals.md"
    signals_json_path = project_dir / LEADS_DIR / "lead-signals.json"
    write_text(signals_path, render_lead_signals_markdown(lead_signals))
    write_text(signals_json_path, json.dumps(lead_signals, indent=2))
    record_lead_signals(project_dir, lead_signals)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "leadSignals": lead_signals,
        "leadSignalsPath": str(signals_path),
        "leadSignalsJsonPath": str(signals_json_path),
        "statePath": str(project_dir / STATE_PATH),
        "next": "Score inbound or monitored lead text with score-lead.",
    }


def score_lead(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    strategy = state.get("lastStrategy", {}) if isinstance(state.get("lastStrategy"), dict) else {}
    if not strategy:
        return {"ok": False, "error": "No strategy found. Run create-strategy first."}
    lead_signals = state.get("lastLeadSignals", {}) if isinstance(state.get("lastLeadSignals"), dict) else {}
    if not lead_signals:
        lead_signals = build_lead_signals(strategy, channels=[], signals=[], negative_signals=[])
    scorecard = build_lead_scorecard(
        name=args.name,
        company=args.company,
        source=args.source,
        text=args.text,
        url=args.url,
        role=args.role,
        channel=args.channel,
        strategy=strategy,
        lead_signals=lead_signals,
    )
    scorecards = [item for item in state.get("leadScorecards", []) if isinstance(item, dict)]
    scorecards.append(scorecard)
    scorecards_path = project_dir / LEADS_DIR / "lead-scorecards.md"
    scorecards_json_path = project_dir / LEADS_DIR / "lead-scorecards.json"
    write_text(scorecards_path, render_scorecards_markdown(scorecards))
    write_text(scorecards_json_path, json.dumps(scorecards, indent=2))
    record_lead_scorecard(project_dir, scorecard)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "scorecard": scorecard,
        "scorecardsPath": str(scorecards_path),
        "scorecardsJsonPath": str(scorecards_json_path),
        "statePath": str(project_dir / STATE_PATH),
        "next": "Create review-only outreach with draft-outreach, or export CRM rows with crm-export.",
    }


def draft_outreach(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    strategy = state.get("lastStrategy", {}) if isinstance(state.get("lastStrategy"), dict) else {}
    campaign = state.get("lastCampaign", {}) if isinstance(state.get("lastCampaign"), dict) else {}
    scorecard = select_lead_scorecard(state, args.lead_id)
    if not scorecard:
        return {"ok": False, "error": "No lead scorecard found. Run score-lead first."}
    draft = build_outreach_draft(
        scorecard=scorecard,
        strategy=strategy,
        campaign=campaign,
        channel=args.channel,
        tone=args.tone,
        cta=args.cta,
    )
    drafts = [item for item in state.get("outreachDrafts", []) if isinstance(item, dict)]
    drafts.append(draft)
    drafts_path = project_dir / LEADS_DIR / "outreach-drafts.md"
    drafts_json_path = project_dir / LEADS_DIR / "outreach-drafts.json"
    write_text(drafts_path, render_outreach_markdown(drafts))
    write_text(drafts_json_path, json.dumps(drafts, indent=2))
    record_outreach_draft(project_dir, draft)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "outreachDraft": draft,
        "outreachDraftsPath": str(drafts_path),
        "outreachDraftsJsonPath": str(drafts_json_path),
        "statePath": str(project_dir / STATE_PATH),
        "message": "Outreach draft created for review. Sending requires explicit approval.",
    }


def crm_export(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    rows = crm_rows_from_state(state, owner=args.owner)
    if not rows:
        return {"ok": False, "error": "No lead scorecards found. Run score-lead first."}
    export = {
        "type": "crm-export",
        "format": args.format,
        "owner": args.owner,
        "leadCount": len(rows),
        "rows": rows,
        "approvalRequired": True,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    export_path = project_dir / LEADS_DIR / f"crm-export.{args.format}"
    if args.format == "csv":
        write_text(export_path, crm_rows_to_csv(rows))
    else:
        write_text(export_path, json.dumps(export, indent=2))
    record_crm_export(project_dir, {**export, "path": str(export_path)})
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "crmExport": export,
        "crmExportPath": str(export_path),
        "statePath": str(project_dir / STATE_PATH),
        "message": "CRM export prepared as a review artifact. Importing or writing CRM records requires approval.",
    }


def record_performance(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    campaign = select_campaign(state, args.campaign)
    if not campaign:
        return {"ok": False, "error": "No campaign found. Run create-campaign first."}
    strategy = state.get("lastStrategy", {}) if isinstance(state.get("lastStrategy"), dict) else {}
    snapshot = build_performance_snapshot(
        campaign=campaign,
        strategy=strategy,
        channel=args.channel,
        period=args.period,
        metrics=parse_metrics(args.metrics),
        notes=args.notes,
    )
    snapshots = [item for item in state.get("performanceSnapshots", []) if isinstance(item, dict)]
    snapshots.append(snapshot)
    snapshot_path = project_dir / ANALYTICS_DIR / "performance-snapshots.md"
    snapshot_json_path = project_dir / ANALYTICS_DIR / "performance-snapshots.json"
    write_text(snapshot_path, render_performance_snapshots_markdown(snapshots))
    write_text(snapshot_json_path, json.dumps(snapshots, indent=2))
    record_performance_snapshot(project_dir, snapshot)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "performanceSnapshot": snapshot,
        "performanceSnapshotsPath": str(snapshot_path),
        "performanceSnapshotsJsonPath": str(snapshot_json_path),
        "statePath": str(project_dir / STATE_PATH),
        "next": "Generate the manager dashboard with generate-review-dashboard.",
    }


def generate_review_dashboard(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    strategy = state.get("lastStrategy", {}) if isinstance(state.get("lastStrategy"), dict) else {}
    if not strategy:
        return {"ok": False, "error": "No strategy found. Run create-strategy first."}
    dashboard = build_review_dashboard(state, focus=args.focus, period=args.period)
    dashboard_path = project_dir / ANALYTICS_DIR / "manager-review-dashboard.md"
    dashboard_json_path = project_dir / ANALYTICS_DIR / "manager-review-dashboard.json"
    write_text(dashboard_path, render_review_dashboard_markdown(dashboard))
    write_text(dashboard_json_path, json.dumps(dashboard, indent=2))
    record_review_dashboard(project_dir, dashboard)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "reviewDashboard": dashboard,
        "reviewDashboardPath": str(dashboard_path),
        "reviewDashboardJsonPath": str(dashboard_json_path),
        "statePath": str(project_dir / STATE_PATH),
        "message": "Manager review dashboard generated from local project state.",
    }


def add_competitor(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    strategy = state.get("lastStrategy", {}) if isinstance(state.get("lastStrategy"), dict) else {}
    if not strategy:
        return {"ok": False, "error": "No strategy found. Run create-strategy first."}
    competitor = build_competitor_profile(
        strategy=strategy,
        name=args.name,
        url=args.url,
        category=args.category,
        positioning=args.positioning,
        strengths=parse_list(args.strengths),
        weaknesses=parse_list(args.weaknesses),
        channels=parse_list(args.channels),
    )
    competitors = upsert_by_id([item for item in state.get("competitors", []) if isinstance(item, dict)], competitor)
    profile_path = project_dir / COMPETITOR_DIR / "competitor-profiles.md"
    profile_json_path = project_dir / COMPETITOR_DIR / "competitor-profiles.json"
    write_text(profile_path, render_competitor_profiles_markdown(competitors))
    write_text(profile_json_path, json.dumps(competitors, indent=2))
    record_competitor(project_dir, competitor)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "competitor": competitor,
        "competitorProfilesPath": str(profile_path),
        "competitorProfilesJsonPath": str(profile_json_path),
        "statePath": str(project_dir / STATE_PATH),
        "next": "Track competitor moves with track-competitor, then generate a competitor-report.",
    }


def track_competitor(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    competitor = select_competitor(state, args.competitor)
    if not competitor:
        return {"ok": False, "error": "No competitor found. Run add-competitor first."}
    observation = build_competitor_observation(
        competitor=competitor,
        event_type=args.event_type,
        channel=args.channel,
        summary=args.summary,
        url=args.url,
        impact=args.impact,
        tags=parse_list(args.tags),
    )
    observations = [item for item in state.get("competitorObservations", []) if isinstance(item, dict)]
    observations.append(observation)
    observations_path = project_dir / COMPETITOR_DIR / "competitor-observations.md"
    observations_json_path = project_dir / COMPETITOR_DIR / "competitor-observations.json"
    write_text(observations_path, render_competitor_observations_markdown(observations))
    write_text(observations_json_path, json.dumps(observations, indent=2))
    record_competitor_observation(project_dir, observation)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "competitorObservation": observation,
        "competitorObservationsPath": str(observations_path),
        "competitorObservationsJsonPath": str(observations_json_path),
        "statePath": str(project_dir / STATE_PATH),
        "next": "Generate competitive positioning and response recommendations with competitor-report.",
    }


def competitor_report(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    strategy = state.get("lastStrategy", {}) if isinstance(state.get("lastStrategy"), dict) else {}
    competitors = [item for item in state.get("competitors", []) if isinstance(item, dict)]
    if not strategy:
        return {"ok": False, "error": "No strategy found. Run create-strategy first."}
    if not competitors:
        return {"ok": False, "error": "No competitors found. Run add-competitor first."}
    report = build_competitor_report(state, focus=args.focus, period=args.period)
    report_path = project_dir / COMPETITOR_DIR / "competitor-intelligence-report.md"
    report_json_path = project_dir / COMPETITOR_DIR / "competitor-intelligence-report.json"
    write_text(report_path, render_competitor_report_markdown(report))
    write_text(report_json_path, json.dumps(report, indent=2))
    record_competitor_report(project_dir, report)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "competitorReport": report,
        "competitorReportPath": str(report_path),
        "competitorReportJsonPath": str(report_json_path),
        "statePath": str(project_dir / STATE_PATH),
        "message": "Competitor intelligence report generated from local observations.",
    }


def create_approval_package(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    strategy = state.get("lastStrategy", {}) if isinstance(state.get("lastStrategy"), dict) else {}
    if not strategy:
        return {"ok": False, "error": "No strategy found. Run create-strategy first."}
    package = build_approval_package(
        state,
        channels=parse_list(args.channels),
        owner=args.owner,
        due=args.due,
        scope=args.scope,
    )
    package_path = project_dir / EXECUTION_DIR / "approval-package.md"
    package_json_path = project_dir / EXECUTION_DIR / "approval-package.json"
    queue_path = project_dir / EXECUTION_DIR / "publishing-queue.json"
    write_text(package_path, render_approval_package_markdown(package))
    write_text(package_json_path, json.dumps(package, indent=2))
    write_text(queue_path, json.dumps(package["publishingQueue"], indent=2))
    record_approval_package(project_dir, {**package, "path": str(package_path), "queuePath": str(queue_path)})
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "approvalPackage": package,
        "approvalPackagePath": str(package_path),
        "approvalPackageJsonPath": str(package_json_path),
        "publishingQueuePath": str(queue_path),
        "statePath": str(project_dir / STATE_PATH),
        "message": "Approval package created. Execution still requires explicit approval and external publishing tools.",
    }


def record_approval(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    package = select_approval_package(state, args.package_id)
    if not package:
        return {"ok": False, "error": "No approval package found. Run create-approval-package first."}
    decision = build_approval_decision(
        package=package,
        decision=args.decision,
        approver=args.approver,
        notes=args.notes,
    )
    decisions = [item for item in state.get("approvalDecisions", []) if isinstance(item, dict)]
    decisions.append(decision)
    change_log_path = project_dir / EXECUTION_DIR / "approval-change-log.md"
    change_log_json_path = project_dir / EXECUTION_DIR / "approval-change-log.json"
    write_text(change_log_path, render_change_log_markdown(decisions))
    write_text(change_log_json_path, json.dumps(decisions, indent=2))
    record_approval_decision(project_dir, decision)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "approvalDecision": decision,
        "approvalChangeLogPath": str(change_log_path),
        "approvalChangeLogJsonPath": str(change_log_json_path),
        "statePath": str(project_dir / STATE_PATH),
        "message": "Approval decision recorded in local change log.",
    }


def operator_handoff(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    package = select_approval_package(state, args.package_id)
    if not package:
        return {"ok": False, "error": "No approval package found. Run create-approval-package first."}
    handoff = build_operator_handoff(state, package=package, operator=args.operator)
    handoff_path = project_dir / EXECUTION_DIR / "operator-handoff.md"
    handoff_json_path = project_dir / EXECUTION_DIR / "operator-handoff.json"
    write_text(handoff_path, render_operator_handoff_markdown(handoff))
    write_text(handoff_json_path, json.dumps(handoff, indent=2))
    record_operator_handoff(project_dir, {**handoff, "path": str(handoff_path)})
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "operatorHandoff": handoff,
        "operatorHandoffPath": str(handoff_path),
        "operatorHandoffJsonPath": str(handoff_json_path),
        "statePath": str(project_dir / STATE_PATH),
        "message": "Operator handoff generated for human execution.",
    }


def select_campaign(state: dict[str, Any], campaign_slug: str) -> dict[str, Any]:
    if campaign_slug:
        for campaign in state.get("campaigns", []):
            if isinstance(campaign, dict) and campaign.get("slug") == campaign_slug:
                return campaign
        return {}
    campaign = state.get("lastCampaign", {})
    return campaign if isinstance(campaign, dict) else {}


def select_lead_scorecard(state: dict[str, Any], lead_id: str) -> dict[str, Any]:
    if lead_id:
        for scorecard in state.get("leadScorecards", []):
            if isinstance(scorecard, dict) and scorecard.get("id") == lead_id:
                return scorecard
        return {}
    scorecard = state.get("lastLeadScorecard", {})
    return scorecard if isinstance(scorecard, dict) else {}


def select_competitor(state: dict[str, Any], competitor_id_or_name: str) -> dict[str, Any]:
    needle = competitor_id_or_name.strip().lower()
    competitors = [item for item in state.get("competitors", []) if isinstance(item, dict)]
    if not needle and competitors:
        return competitors[-1]
    for competitor in competitors:
        if str(competitor.get("id", "")).lower() == needle or str(competitor.get("name", "")).lower() == needle:
            return competitor
    return {}


def select_approval_package(state: dict[str, Any], package_id: str) -> dict[str, Any]:
    packages = [item for item in state.get("approvalPackages", []) if isinstance(item, dict)]
    if not package_id and packages:
        return packages[-1]
    for package in packages:
        if str(package.get("id", "")) == package_id:
            return package
    return {}


def build_content_plan(
    campaign: dict[str, Any],
    strategy: dict[str, Any],
    *,
    weeks: int,
    cadence: int,
    channels: list[str],
) -> dict[str, Any]:
    themes = campaign.get("themes", []) if isinstance(campaign.get("themes"), list) else []
    if not themes:
        themes = strategy.get("themes", []) if isinstance(strategy.get("themes"), list) else []
    if not themes:
        themes = ["Problem education", "Customer proof", "ROI and outcomes"]
    items = []
    for week in range(1, weeks + 1):
        for slot in range(1, cadence + 1):
            channel = channels[(week + slot - 2) % len(channels)]
            theme = str(themes[(week + slot - 2) % len(themes)])
            stage = content_stage(week, weeks)
            items.append(
                {
                    "week": week,
                    "slot": slot,
                    "channel": channel,
                    "stage": stage,
                    "theme": theme,
                    "angle": content_angle(channel, stage, theme, campaign),
                    "format": platform_format(channel),
                    "cta": campaign.get("cta", ""),
                    "approvalStatus": "draft",
                }
            )
    return {
        "type": "content-plan",
        "campaign": campaign.get("name", ""),
        "campaignSlug": campaign.get("slug", ""),
        "weeks": weeks,
        "cadencePerWeek": cadence,
        "channels": channels,
        "items": items,
        "approvalRequired": True,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def build_content_drafts(
    campaign: dict[str, Any],
    strategy: dict[str, Any],
    *,
    channels: list[str],
    count: int,
    theme: str,
    stage: str,
) -> dict[str, Any]:
    themes = [theme] if theme else campaign.get("themes", [])
    if not isinstance(themes, list) or not themes:
        themes = strategy.get("themes", []) if isinstance(strategy.get("themes"), list) else ["Problem education"]
    brand = str(strategy.get("brand") or "The company")
    brand_voice = strategy.get("brandVoice", {}) if isinstance(strategy.get("brandVoice"), dict) else {}
    tone = str(strategy.get("tone") or brand_voice.get("tone") or "professional")
    drafts = []
    for channel in channels:
        for index in range(1, count + 1):
            active_theme = str(themes[(index - 1) % len(themes)])
            draft = draft_for_channel(
                channel=channel,
                brand=brand,
                campaign=campaign,
                theme=active_theme,
                stage=stage or content_stage(index, count),
                tone=tone,
                index=index,
            )
            drafts.append(draft)
    return {
        "type": "content-drafts",
        "campaign": campaign.get("name", ""),
        "campaignSlug": campaign.get("slug", ""),
        "channels": channels,
        "countPerChannel": count,
        "drafts": drafts,
        "approvalRequired": True,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def build_seo_plan(
    strategy: dict[str, Any],
    campaign: dict[str, Any],
    *,
    focus: str,
    pages: int,
    region: str,
) -> dict[str, Any]:
    brand = str(strategy.get("brand") or "Brand")
    business = str(strategy.get("business") or "")
    audience = str(strategy.get("audience") or "target customers")
    offer = str(campaign.get("offer") or strategy.get("offer") or focus or "solution")
    seo_focus = strategy.get("seoFocus", {}) if isinstance(strategy.get("seoFocus"), dict) else {}
    base_clusters = seo_focus.get("keywordClusters", []) if isinstance(seo_focus.get("keywordClusters"), list) else []
    clusters = build_keyword_clusters(offer, audience, business, base_clusters)
    page_plan = []
    page_types = ["pillar", "comparison", "use-case", "faq", "case-study", "integration"]
    for index in range(pages):
        cluster = clusters[index % len(clusters)]
        page_type = page_types[index % len(page_types)]
        page_plan.append(
            {
                "type": page_type,
                "title": seo_page_title(page_type, cluster, brand),
                "primaryKeyword": cluster["primary"],
                "intent": cluster["intent"],
                "cta": campaign.get("cta") or strategy.get("goal") or "Book a consultation",
                "internalLinks": suggested_internal_links(page_type),
            }
        )
    return {
        "type": "seo-geo-plan",
        "brand": brand,
        "offer": offer,
        "audience": audience,
        "region": region or strategy.get("region") or "global",
        "focus": focus or offer,
        "keywordClusters": clusters,
        "pagePlan": page_plan,
        "geoRecommendations": build_geo_recommendations(brand, offer, audience),
        "schemaRecommendations": ["Organization", "Product", "FAQPage", "HowTo", "Article", "BreadcrumbList"],
        "technicalTasks": [
            "Write unique title and meta description for every campaign landing page.",
            "Add FAQ blocks that answer buyer objections in plain language.",
            "Use descriptive H1/H2 headings that include the offer and audience.",
            "Add internal links from blog briefs to the pillar page and conversion page.",
            "Keep terminology consistent across website, blog, social, and outreach.",
        ],
        "approvalRequired": True,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def build_blog_briefs(strategy: dict[str, Any], seo_plan: dict[str, Any], *, count: int, intent: str) -> dict[str, Any]:
    brand = str(strategy.get("brand") or "Brand")
    audience = str(strategy.get("audience") or "target customers")
    offer = str(seo_plan.get("offer") or strategy.get("offer") or "solution")
    clusters = seo_plan.get("keywordClusters", []) if isinstance(seo_plan.get("keywordClusters"), list) else []
    if not clusters:
        clusters = build_keyword_clusters(offer, audience, str(strategy.get("business") or ""), [])
    intents = [intent] if intent else ["informational", "commercial", "comparison", "problem-aware"]
    briefs = []
    for index in range(count):
        cluster = clusters[index % len(clusters)]
        active_intent = intents[index % len(intents)]
        title = blog_title(active_intent, cluster["primary"], offer)
        briefs.append(
            {
                "title": title,
                "slug": slugify(title, fallback=f"blog-{index + 1}"),
                "intent": active_intent,
                "primaryKeyword": cluster["primary"],
                "secondaryKeywords": cluster["secondary"],
                "audience": audience,
                "metaDescription": f"Learn how {audience} can evaluate {offer}, compare options, and make a confident next decision.",
                "outline": [
                    f"Define the problem behind {cluster['primary']}",
                    f"Explain what {audience} should measure or compare",
                    f"Show how {offer} changes the workflow",
                    "Answer common objections",
                    f"CTA: {brand} consultation or demo",
                ],
                "aiAnswerSummary": f"{brand} helps {audience} understand and evaluate {offer} with clear proof, use cases, and next steps.",
                "schema": ["Article", "FAQPage", "BreadcrumbList"],
                "internalLinks": ["pillar page", "campaign landing page", "case study", "contact/demo page"],
                "approvalStatus": "draft",
            }
        )
    return {
        "type": "blog-briefs",
        "brand": brand,
        "offer": offer,
        "briefs": briefs,
        "approvalRequired": True,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def build_lead_signals(
    strategy: dict[str, Any],
    *,
    channels: list[str],
    signals: list[str],
    negative_signals: list[str],
) -> dict[str, Any]:
    inferred = infer_lead_signals(strategy)
    positive = unique_list([*signals, *inferred["positiveSignals"]])
    negatives = unique_list([*negative_signals, *inferred["negativeSignals"]])
    active_channels = channels or [str(channel) for channel in strategy.get("channels", []) if str(channel).strip()]
    if not active_channels:
        active_channels = ["LinkedIn", "X", "Reddit", "Industry forums", "Website form", "Email"]
    return {
        "type": "lead-signals",
        "brand": strategy.get("brand", ""),
        "audience": strategy.get("audience", ""),
        "offer": strategy.get("offer", ""),
        "channels": active_channels,
        "positiveSignals": positive,
        "buyingTriggerPhrases": inferred["buyingTriggerPhrases"],
        "painPointPhrases": inferred["painPointPhrases"],
        "negativeSignals": negatives,
        "scoringRules": [
            "+16 for each explicit positive signal",
            "+12 for each buying trigger phrase",
            "+10 for each pain point phrase",
            "+8 for ICP, industry, role, or channel fit",
            "-18 for each negative signal",
            "Hot >= 75, warm >= 45, nurture below 45",
        ],
        "approvalRequired": True,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def infer_lead_signals(strategy: dict[str, Any]) -> dict[str, list[str]]:
    icp = strategy.get("icp", {}) if isinstance(strategy.get("icp"), dict) else {}
    pain_points = [str(item) for item in icp.get("painPoints", []) if str(item).strip()]
    buying_triggers = [str(item) for item in icp.get("buyingTriggers", []) if str(item).strip()]
    offer = str(strategy.get("offer") or "solution")
    goal = str(strategy.get("goal") or "improve results")
    audience = str(strategy.get("audience") or "target customer")
    positive = [
        f"looking for {offer}",
        f"need {offer}",
        f"evaluating {offer}",
        f"requesting demo for {offer}",
        f"want to {goal}",
        f"{audience} asking for vendor recommendations",
    ]
    trigger_phrases = [
        "looking for",
        "need a solution",
        "need help",
        "evaluating vendors",
        "request for proposal",
        "budget approved",
        "book a demo",
        "reduce losses",
        "improve accuracy",
        "replace manual",
    ]
    pain_phrases = []
    for pain in pain_points:
        pain_phrases.extend([pain, pain.replace("manual ", ""), pain.replace("limited ", "")])
    for trigger in buying_triggers:
        trigger_phrases.append(trigger)
    return {
        "positiveSignals": positive,
        "buyingTriggerPhrases": unique_list(trigger_phrases),
        "painPointPhrases": unique_list(pain_phrases),
        "negativeSignals": [
            "student research",
            "job application",
            "free only",
            "not buying",
            "already solved",
            "competitor hiring",
        ],
    }


def build_lead_scorecard(
    *,
    name: str,
    company: str,
    source: str,
    text: str,
    url: str,
    role: str,
    channel: str,
    strategy: dict[str, Any],
    lead_signals: dict[str, Any],
) -> dict[str, Any]:
    scored = score_lead_text(text, lead_signals, strategy, role=role, channel=channel, company=company)
    lead_id = slugify(f"{company or name}-{source or channel}-{datetime.now(timezone.utc).isoformat()}", fallback="lead")
    grade = lead_grade(scored["score"])
    return {
        "type": "lead-scorecard",
        "id": lead_id,
        "name": name.strip(),
        "company": company.strip(),
        "role": role.strip(),
        "source": source.strip(),
        "channel": channel.strip(),
        "url": url.strip(),
        "text": text.strip(),
        "score": scored["score"],
        "grade": grade,
        "matchedSignals": scored["matchedSignals"],
        "negativeMatches": scored["negativeMatches"],
        "rationale": scored["rationale"],
        "suggestedAction": lead_action(grade),
        "approvalStatus": "review",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def score_lead_text(
    text: str,
    lead_signals: dict[str, Any],
    strategy: dict[str, Any],
    *,
    role: str,
    channel: str,
    company: str,
) -> dict[str, Any]:
    haystack = f"{text} {role} {channel} {company}".lower()
    matched: list[str] = []
    negative_matches: list[str] = []
    score = 10
    for signal in lead_signals.get("positiveSignals", []):
        if phrase_matches(haystack, str(signal)):
            matched.append(str(signal))
            score += 16
    for signal in lead_signals.get("buyingTriggerPhrases", []):
        if phrase_matches(haystack, str(signal)):
            matched.append(str(signal))
            score += 12
    for signal in lead_signals.get("painPointPhrases", []):
        if phrase_matches(haystack, str(signal)):
            matched.append(str(signal))
            score += 10
    for signal in lead_signals.get("negativeSignals", []):
        if phrase_matches(haystack, str(signal)):
            negative_matches.append(str(signal))
            score -= 18
    score += fit_score(haystack, strategy, lead_signals)
    score = max(0, min(100, score))
    rationale = "Matched " + ", ".join(unique_list(matched)[:5]) if matched else "No strong explicit buying signals found."
    if negative_matches:
        rationale += " Negative signals: " + ", ".join(unique_list(negative_matches)[:3]) + "."
    return {"score": score, "matchedSignals": unique_list(matched), "negativeMatches": unique_list(negative_matches), "rationale": rationale}


def phrase_matches(haystack: str, phrase: str) -> bool:
    needle = phrase.lower().strip()
    if not needle:
        return False
    if needle in haystack:
        return True
    words = [word for word in re.split(r"[^a-z0-9]+", needle) if len(word) > 3]
    return bool(words) and sum(1 for word in words if word in haystack) >= min(2, len(words))


def fit_score(haystack: str, strategy: dict[str, Any], lead_signals: dict[str, Any]) -> int:
    score = 0
    icp = strategy.get("icp", {}) if isinstance(strategy.get("icp"), dict) else {}
    industries = [str(item) for item in icp.get("industries", []) if str(item).strip()]
    channels = [str(item) for item in lead_signals.get("channels", []) if str(item).strip()]
    for item in industries[:8]:
        if phrase_matches(haystack, item):
            score += 8
            break
    if any(role in haystack for role in ("owner", "founder", "director", "manager", "vp", "head", "operations", "procurement")):
        score += 8
    for item in channels:
        if item.lower() in haystack:
            score += 6
            break
    return score


def lead_grade(score: int) -> str:
    if score >= 75:
        return "hot"
    if score >= 45:
        return "warm"
    return "nurture"


def lead_action(grade: str) -> str:
    if grade == "hot":
        return "Review quickly, personalize outreach, and ask for a demo or discovery call."
    if grade == "warm":
        return "Add to nurture, share a relevant proof asset, and follow up within three business days."
    return "Keep for content retargeting or low-touch nurture until a stronger buying signal appears."


def build_outreach_draft(
    *,
    scorecard: dict[str, Any],
    strategy: dict[str, Any],
    campaign: dict[str, Any],
    channel: str,
    tone: str,
    cta: str,
) -> dict[str, Any]:
    brand = str(strategy.get("brand") or "our team")
    offer = str(campaign.get("offer") or strategy.get("offer") or "the solution")
    final_cta = cta or str(campaign.get("cta") or "Book a short consultation")
    final_tone = tone or str(strategy.get("tone") or "professional")
    matched = scorecard.get("matchedSignals", []) if isinstance(scorecard.get("matchedSignals"), list) else []
    reason = str(matched[0]) if matched else str(scorecard.get("rationale") or "your current priority")
    lead_name = str(scorecard.get("name") or "there")
    company = str(scorecard.get("company") or "your team")
    subject = f"Quick idea for {company}" if channel == "email" else f"{brand} follow-up"
    body = outreach_body(channel, lead_name, company, brand, offer, reason, final_cta)
    draft_id = slugify(f"outreach-{scorecard.get('id', '')}-{channel}", fallback="outreach")
    return {
        "type": "outreach-draft",
        "id": draft_id,
        "leadId": scorecard.get("id", ""),
        "channel": channel,
        "tone": final_tone,
        "subject": subject,
        "body": body,
        "followUpSchedule": build_follow_up_schedule(str(scorecard.get("grade") or "nurture")),
        "approvalStatus": "draft",
        "approvalRequired": True,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def outreach_body(channel: str, lead_name: str, company: str, brand: str, offer: str, reason: str, cta: str) -> str:
    greeting = f"Hi {lead_name}," if lead_name else "Hi,"
    if channel == "linkedin":
        return (
            f"{greeting}\n\nI noticed your team may be focused on {reason}. "
            f"{brand} helps teams evaluate {offer} with a practical before/after workflow.\n\n"
            f"If useful, I can share a short example for {company}.\n\n{cta}"
        )
    if channel == "x":
        return f"{greeting} saw the note about {reason}. {brand} works on {offer}; happy to share a quick example if useful. {cta}"
    if channel == "phone":
        return (
            f"Call note: Ask {lead_name} whether {reason} is an active project at {company}. "
            f"Position {brand} around {offer}. Close with: {cta}."
        )
    if channel == "crm-note":
        return f"Lead mentioned {reason}. Recommended next step: send {brand} proof asset for {offer}, then ask: {cta}."
    return (
        f"{greeting}\n\nI saw a signal that {company} may be working on {reason}.\n\n"
        f"{brand} helps teams evaluate {offer} by connecting the problem to a measurable workflow change.\n\n"
        "A useful next step could be a short review of the current process and where the gaps show up.\n\n"
        f"{cta}"
    )


def build_follow_up_schedule(grade: str) -> list[dict[str, Any]]:
    if grade == "hot":
        offsets = [0, 2, 5]
    elif grade == "warm":
        offsets = [1, 4, 10]
    else:
        offsets = [3, 14, 30]
    return [
        {"dayOffset": offsets[0], "action": "Send reviewed first-touch outreach."},
        {"dayOffset": offsets[1], "action": "Follow up with proof asset or relevant content."},
        {"dayOffset": offsets[2], "action": "Ask whether timing, owner, or priority changed."},
    ]


def crm_rows_from_state(state: dict[str, Any], *, owner: str) -> list[dict[str, Any]]:
    latest_drafts: dict[str, dict[str, Any]] = {}
    for draft in state.get("outreachDrafts", []):
        if isinstance(draft, dict):
            latest_drafts[str(draft.get("leadId") or "")] = draft
    rows = []
    for scorecard in state.get("leadScorecards", []):
        if not isinstance(scorecard, dict):
            continue
        draft = latest_drafts.get(str(scorecard.get("id") or ""), {})
        rows.append(
            {
                "lead_id": scorecard.get("id", ""),
                "name": scorecard.get("name", ""),
                "company": scorecard.get("company", ""),
                "role": scorecard.get("role", ""),
                "source": scorecard.get("source", ""),
                "channel": scorecard.get("channel", ""),
                "url": scorecard.get("url", ""),
                "score": scorecard.get("score", 0),
                "grade": scorecard.get("grade", ""),
                "suggested_action": scorecard.get("suggestedAction", ""),
                "outreach_channel": draft.get("channel", ""),
                "outreach_subject": draft.get("subject", ""),
                "owner": owner,
                "approval_status": "review",
            }
        )
    return rows


def crm_rows_to_csv(rows: list[dict[str, Any]]) -> str:
    output = StringIO()
    fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().rstrip()


def unique_list(items: list[str]) -> list[str]:
    seen = set()
    unique = []
    for item in items:
        value = str(item).strip()
        key = value.lower()
        if value and key not in seen:
            seen.add(key)
            unique.append(value)
    return unique


def parse_metrics(value: str) -> dict[str, float]:
    metrics: dict[str, float] = {}
    for item in parse_list(value):
        if "=" not in item:
            continue
        key, raw_value = item.split("=", 1)
        key = slugify(key.strip(), fallback="metric").replace("-", "_")
        try:
            metrics[key] = float(raw_value.strip())
        except ValueError:
            continue
    return metrics


def build_performance_snapshot(
    *,
    campaign: dict[str, Any],
    strategy: dict[str, Any],
    channel: str,
    period: str,
    metrics: dict[str, float],
    notes: str,
) -> dict[str, Any]:
    normalized = normalize_metrics(metrics)
    derived = derive_performance_metrics(normalized)
    recommendations = performance_recommendations(campaign, strategy, channel, normalized, derived)
    return {
        "type": "performance-snapshot",
        "campaign": campaign.get("name", ""),
        "campaignSlug": campaign.get("slug", ""),
        "channel": channel or "all channels",
        "period": period or "latest period",
        "metrics": normalized,
        "derivedMetrics": derived,
        "notes": notes.strip(),
        "recommendations": recommendations,
        "approvalRequired": False,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def normalize_metrics(metrics: dict[str, float]) -> dict[str, float]:
    defaults = {
        "impressions": 0.0,
        "engagements": 0.0,
        "clicks": 0.0,
        "leads": 0.0,
        "conversions": 0.0,
        "spend": 0.0,
        "revenue": 0.0,
    }
    defaults.update(metrics)
    return defaults


def derive_performance_metrics(metrics: dict[str, float]) -> dict[str, float]:
    impressions = metrics.get("impressions", 0.0)
    clicks = metrics.get("clicks", 0.0)
    engagements = metrics.get("engagements", 0.0)
    leads = metrics.get("leads", 0.0)
    conversions = metrics.get("conversions", 0.0)
    spend = metrics.get("spend", 0.0)
    revenue = metrics.get("revenue", 0.0)
    return {
        "engagementRate": safe_ratio(engagements, impressions),
        "ctr": safe_ratio(clicks, impressions),
        "leadRate": safe_ratio(leads, clicks),
        "conversionRate": safe_ratio(conversions, leads),
        "costPerLead": safe_ratio(spend, leads),
        "roas": safe_ratio(revenue, spend),
    }


def safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def performance_recommendations(
    campaign: dict[str, Any],
    strategy: dict[str, Any],
    channel: str,
    metrics: dict[str, float],
    derived: dict[str, float],
) -> list[str]:
    recommendations = []
    if derived["ctr"] < 0.01 and metrics["impressions"] > 0:
        recommendations.append("Improve the hook and CTA because click-through rate is below 1%.")
    if derived["engagementRate"] < 0.03 and metrics["impressions"] > 0:
        recommendations.append("Test a stronger problem-led angle or proof asset to increase engagement.")
    if metrics["leads"] == 0 and metrics["clicks"] > 0:
        recommendations.append("Review landing page/message match because clicks are not converting into leads.")
    if metrics["leads"] > 0 and derived["conversionRate"] < 0.2:
        recommendations.append("Add follow-up proof and clearer qualification steps for generated leads.")
    if metrics["spend"] > 0 and derived["roas"] < 1:
        recommendations.append("Pause scaling until offer, audience, or conversion path improves.")
    if not recommendations:
        recommendations.append("Keep the campaign running, preserve the current winning angle, and test one controlled variation.")
    offer = campaign.get("offer") or strategy.get("offer") or "the offer"
    recommendations.append(f"Next test: compare ROI-focused messaging against technical proof for {offer} on {channel or 'the active channel'}.")
    return recommendations


def build_review_dashboard(state: dict[str, Any], *, focus: str, period: str) -> dict[str, Any]:
    strategy = state.get("lastStrategy", {}) if isinstance(state.get("lastStrategy"), dict) else {}
    snapshots = [item for item in state.get("performanceSnapshots", []) if isinstance(item, dict)]
    lead_scorecards = [item for item in state.get("leadScorecards", []) if isinstance(item, dict)]
    content_drafts = state.get("lastContentDrafts", {}) if isinstance(state.get("lastContentDrafts"), dict) else {}
    blog_briefs = state.get("lastBlogBriefs", {}) if isinstance(state.get("lastBlogBriefs"), dict) else {}
    totals = aggregate_performance(snapshots)
    lead_funnel = aggregate_lead_funnel(lead_scorecards)
    review_queue = build_review_queue(state)
    recommendations = dashboard_recommendations(totals, lead_funnel, review_queue)
    return {
        "type": "manager-review-dashboard",
        "brand": strategy.get("brand", ""),
        "focus": focus or "marketing review",
        "period": period or "latest period",
        "artifactCounts": {
            "strategies": len(state.get("strategies", [])),
            "campaigns": len(state.get("campaigns", [])),
            "contentDrafts": len(content_drafts.get("drafts", [])) if isinstance(content_drafts.get("drafts"), list) else 0,
            "blogBriefs": len(blog_briefs.get("briefs", [])) if isinstance(blog_briefs.get("briefs"), list) else 0,
            "leadScorecards": len(lead_scorecards),
            "outreachDrafts": len(state.get("outreachDrafts", [])),
            "performanceSnapshots": len(snapshots),
        },
        "performanceTotals": totals,
        "leadFunnel": lead_funnel,
        "reviewQueue": review_queue,
        "optimizationRecommendations": recommendations,
        "approvalRequired": False,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def aggregate_performance(snapshots: list[dict[str, Any]]) -> dict[str, Any]:
    totals = normalize_metrics({})
    by_channel: dict[str, dict[str, float]] = {}
    for snapshot in snapshots:
        metrics = snapshot.get("metrics", {}) if isinstance(snapshot.get("metrics"), dict) else {}
        channel = str(snapshot.get("channel") or "all channels")
        channel_totals = by_channel.setdefault(channel, normalize_metrics({}))
        for key in totals:
            value = float(metrics.get(key, 0.0) or 0.0)
            totals[key] += value
            channel_totals[key] += value
    return {
        "totals": totals,
        "derivedMetrics": derive_performance_metrics(totals),
        "byChannel": {channel: {**metrics, "derivedMetrics": derive_performance_metrics(metrics)} for channel, metrics in by_channel.items()},
    }


def aggregate_lead_funnel(scorecards: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {"hot": 0, "warm": 0, "nurture": 0}
    for scorecard in scorecards:
        grade = str(scorecard.get("grade") or "nurture")
        counts[grade if grade in counts else "nurture"] += 1
    total = sum(counts.values())
    return {
        "total": total,
        "hot": counts["hot"],
        "warm": counts["warm"],
        "nurture": counts["nurture"],
        "salesReady": counts["hot"] + counts["warm"],
        "salesReadyRate": safe_ratio(counts["hot"] + counts["warm"], total),
    }


def build_review_queue(state: dict[str, Any]) -> list[dict[str, Any]]:
    queue = []
    drafts = state.get("lastContentDrafts", {}) if isinstance(state.get("lastContentDrafts"), dict) else {}
    if isinstance(drafts.get("drafts"), list) and drafts["drafts"]:
        queue.append({"artifact": "content drafts", "count": len(drafts["drafts"]), "action": "Review and approve posts before publishing."})
    briefs = state.get("lastBlogBriefs", {}) if isinstance(state.get("lastBlogBriefs"), dict) else {}
    if isinstance(briefs.get("briefs"), list) and briefs["briefs"]:
        queue.append({"artifact": "blog briefs", "count": len(briefs["briefs"]), "action": "Review outlines before assigning writing or publishing."})
    scorecards = [item for item in state.get("leadScorecards", []) if isinstance(item, dict)]
    if scorecards:
        queue.append({"artifact": "lead scorecards", "count": len(scorecards), "action": "Review hot and warm leads before outreach."})
    outreach = [item for item in state.get("outreachDrafts", []) if isinstance(item, dict)]
    if outreach:
        queue.append({"artifact": "outreach drafts", "count": len(outreach), "action": "Approve or edit drafts before sending."})
    return queue


def dashboard_recommendations(totals: dict[str, Any], lead_funnel: dict[str, Any], review_queue: list[dict[str, Any]]) -> list[str]:
    derived = totals.get("derivedMetrics", {}) if isinstance(totals.get("derivedMetrics"), dict) else {}
    recommendations = []
    if derived.get("ctr", 0) < 0.01 and totals.get("totals", {}).get("impressions", 0) > 0:
        recommendations.append("Prioritize hook and CTA testing across low-CTR channels.")
    if lead_funnel.get("hot", 0) > 0:
        recommendations.append("Review hot leads first and create a short follow-up block for this week.")
    if lead_funnel.get("total", 0) > 0 and lead_funnel.get("salesReadyRate", 0) < 0.35:
        recommendations.append("Tighten lead signal definitions because too many leads remain nurture-only.")
    if len(review_queue) > 2:
        recommendations.append("Clear the approval queue before creating more campaign assets.")
    if not recommendations:
        recommendations.append("Continue weekly reporting and run one controlled content or audience test.")
    return recommendations


def build_competitor_profile(
    *,
    strategy: dict[str, Any],
    name: str,
    url: str,
    category: str,
    positioning: str,
    strengths: list[str],
    weaknesses: list[str],
    channels: list[str],
) -> dict[str, Any]:
    competitor_id = slugify(name, fallback="competitor")
    return {
        "type": "competitor-profile",
        "id": competitor_id,
        "name": name.strip(),
        "url": url.strip(),
        "category": category.strip() or "direct competitor",
        "positioning": positioning.strip(),
        "strengths": strengths or ["brand awareness", "existing market presence"],
        "weaknesses": weaknesses or ["unclear differentiation", "limited proof visible from supplied notes"],
        "channels": channels or [str(channel) for channel in strategy.get("channels", [])[:3]],
        "watchTopics": build_competitor_watch_topics(strategy, positioning, strengths),
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def build_competitor_watch_topics(strategy: dict[str, Any], positioning: str, strengths: list[str]) -> list[str]:
    offer = str(strategy.get("offer") or "the category")
    topics = [
        f"{offer} pricing or packaging changes",
        "new case studies or customer proof",
        "new feature or integration claims",
        "SEO pages targeting buyer comparison intent",
        "paid campaign or landing page changes",
    ]
    if positioning:
        topics.append(f"messaging around: {positioning}")
    topics.extend(str(item) for item in strengths[:3])
    return unique_list(topics)


def build_competitor_observation(
    *,
    competitor: dict[str, Any],
    event_type: str,
    channel: str,
    summary: str,
    url: str,
    impact: str,
    tags: list[str],
) -> dict[str, Any]:
    observation_id = slugify(f"{competitor.get('id', 'competitor')}-{event_type}-{summary}", fallback="competitor-observation")
    return {
        "type": "competitor-observation",
        "id": observation_id,
        "competitorId": competitor.get("id", ""),
        "competitorName": competitor.get("name", ""),
        "eventType": event_type,
        "channel": channel,
        "summary": summary.strip(),
        "url": url.strip(),
        "impact": impact,
        "tags": tags,
        "responseIdeas": competitor_response_ideas(event_type, summary, impact),
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def competitor_response_ideas(event_type: str, summary: str, impact: str) -> list[str]:
    lowered = f"{event_type} {summary} {impact}".lower()
    ideas = []
    if any(word in lowered for word in ("case", "customer", "proof", "testimonial")):
        ideas.append("Prepare a proof-led response asset with a stronger before/after story.")
    if any(word in lowered for word in ("pricing", "discount", "free", "package")):
        ideas.append("Clarify value and ROI instead of matching price directly.")
    if any(word in lowered for word in ("feature", "launch", "integration", "product")):
        ideas.append("Publish a comparison checklist focused on buyer outcomes, not feature volume.")
    if any(word in lowered for word in ("seo", "blog", "keyword", "guide")):
        ideas.append("Add a comparison or FAQ page targeting the same buyer intent.")
    if not ideas:
        ideas.append("Monitor for repeated patterns before changing campaign direction.")
    return ideas


def build_competitor_report(state: dict[str, Any], *, focus: str, period: str) -> dict[str, Any]:
    strategy = state.get("lastStrategy", {}) if isinstance(state.get("lastStrategy"), dict) else {}
    competitors = [item for item in state.get("competitors", []) if isinstance(item, dict)]
    observations = [item for item in state.get("competitorObservations", []) if isinstance(item, dict)]
    gaps = build_positioning_gaps(strategy, competitors)
    trends = build_market_trends(observations)
    response_campaigns = build_response_campaigns(strategy, observations, gaps)
    return {
        "type": "competitor-intelligence-report",
        "brand": strategy.get("brand", ""),
        "focus": focus or "competitive intelligence",
        "period": period or "latest period",
        "competitorCount": len(competitors),
        "observationCount": len(observations),
        "competitors": competitors,
        "recentObservations": observations[-10:],
        "positioningGaps": gaps,
        "marketTrends": trends,
        "responseCampaigns": response_campaigns,
        "approvalRequired": False,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def build_positioning_gaps(strategy: dict[str, Any], competitors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    brand_offer = str(strategy.get("offer") or "offer")
    brand_themes = [str(item).lower() for item in strategy.get("themes", []) if str(item).strip()]
    gaps = []
    for competitor in competitors:
        strengths = [str(item) for item in competitor.get("strengths", []) if str(item).strip()]
        weaknesses = [str(item) for item in competitor.get("weaknesses", []) if str(item).strip()]
        competitor_text = " ".join([str(competitor.get("positioning", "")), *strengths]).lower()
        missing_theme = next((theme for theme in brand_themes if theme and theme not in competitor_text), "")
        gaps.append(
            {
                "competitor": competitor.get("name", ""),
                "risk": strengths[0] if strengths else "competitor has visible market presence",
                "opening": weaknesses[0] if weaknesses else f"Differentiate {brand_offer} with clearer buyer proof.",
                "recommendedMessage": f"Emphasize {missing_theme or 'measurable proof'} and show why {brand_offer} is easier to evaluate.",
            }
        )
    return gaps


def build_market_trends(observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tag_counts: dict[str, int] = {}
    impact_counts: dict[str, int] = {}
    for observation in observations:
        impact = str(observation.get("impact") or "medium")
        impact_counts[impact] = impact_counts.get(impact, 0) + 1
        for tag in observation.get("tags", []):
            key = str(tag).lower()
            tag_counts[key] = tag_counts.get(key, 0) + 1
    trends = []
    for tag, count in sorted(tag_counts.items(), key=lambda item: (-item[1], item[0]))[:5]:
        trends.append({"topic": tag, "count": count, "recommendation": f"Watch {tag} messaging and prepare a differentiated proof point."})
    if not trends:
        trends.append({"topic": "insufficient observations", "count": 0, "recommendation": "Track at least three competitor moves before changing strategy."})
    if impact_counts.get("high", 0):
        trends.append({"topic": "high-impact competitor activity", "count": impact_counts["high"], "recommendation": "Review response campaigns in the next planning cycle."})
    return trends


def build_response_campaigns(strategy: dict[str, Any], observations: list[dict[str, Any]], gaps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    brand = str(strategy.get("brand") or "The brand")
    offer = str(strategy.get("offer") or "the offer")
    campaigns = []
    high_impact = [item for item in observations if item.get("impact") == "high"]
    if high_impact:
        campaigns.append(
            {
                "name": "Competitive Proof Response",
                "objective": "Reinforce buyer confidence after high-impact competitor activity.",
                "message": f"{brand} should publish proof that {offer} creates measurable workflow improvement.",
                "channels": ["LinkedIn", "SEO blog", "Email"],
            }
        )
    if gaps:
        campaigns.append(
            {
                "name": "Comparison Education Campaign",
                "objective": "Own comparison intent without attacking competitors.",
                "message": gaps[0]["recommendedMessage"],
                "channels": ["SEO blog", "LinkedIn", "Sales enablement"],
            }
        )
    if not campaigns:
        campaigns.append(
            {
                "name": "Market Watch Nurture",
                "objective": "Keep a light competitor watch while continuing the current campaign.",
                "message": f"{brand} should keep publishing practical buyer education for {offer}.",
                "channels": ["LinkedIn", "Email"],
            }
        )
    return campaigns


def upsert_by_id(items: list[dict[str, Any]], item: dict[str, Any]) -> list[dict[str, Any]]:
    output = []
    replaced = False
    for existing in items:
        if existing.get("id") == item.get("id"):
            output.append(item)
            replaced = True
        else:
            output.append(existing)
    if not replaced:
        output.append(item)
    return output


def build_approval_package(
    state: dict[str, Any],
    *,
    channels: list[str],
    owner: str,
    due: str,
    scope: str,
) -> dict[str, Any]:
    strategy = state.get("lastStrategy", {}) if isinstance(state.get("lastStrategy"), dict) else {}
    campaign = state.get("lastCampaign", {}) if isinstance(state.get("lastCampaign"), dict) else {}
    active_channels = channels or [str(channel) for channel in campaign.get("channels", []) if str(channel).strip()] or [str(channel) for channel in strategy.get("channels", [])[:3]]
    queue = build_publishing_queue(state, active_channels, scope=scope)
    package_id = slugify(f"approval-{campaign.get('slug') or strategy.get('brand') or 'marketing'}-{datetime.now(timezone.utc).isoformat()}", fallback="approval-package")
    return {
        "type": "approval-package",
        "id": package_id,
        "brand": strategy.get("brand", ""),
        "campaign": campaign.get("name", ""),
        "campaignSlug": campaign.get("slug", ""),
        "scope": scope or "campaign execution",
        "owner": owner,
        "due": due,
        "channels": active_channels,
        "publishingQueue": queue,
        "executionChecklists": build_execution_checklists(active_channels),
        "riskReview": build_execution_risk_review(queue),
        "approvalStatus": "pending",
        "approvalRequired": True,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def build_publishing_queue(state: dict[str, Any], channels: list[str], *, scope: str) -> list[dict[str, Any]]:
    queue: list[dict[str, Any]] = []
    drafts = state.get("lastContentDrafts", {}) if isinstance(state.get("lastContentDrafts"), dict) else {}
    for draft in drafts.get("drafts", []) if isinstance(drafts.get("drafts"), list) else []:
        if not channels or str(draft.get("channel", "")) in channels:
            queue.append(
                {
                    "id": draft.get("id", ""),
                    "source": "content-draft",
                    "channel": draft.get("channel", ""),
                    "title": f"{draft.get('theme', '')} - {draft.get('stage', '')}",
                    "action": "publish after approval",
                    "status": "pending_approval",
                }
            )
    blog_briefs = state.get("lastBlogBriefs", {}) if isinstance(state.get("lastBlogBriefs"), dict) else {}
    for brief in blog_briefs.get("briefs", []) if isinstance(blog_briefs.get("briefs"), list) else []:
        if scope in {"", "campaign execution", "all", "seo", "blog"}:
            queue.append(
                {
                    "id": brief.get("slug", ""),
                    "source": "blog-brief",
                    "channel": "SEO blog",
                    "title": brief.get("title", ""),
                    "action": "write and publish after approval",
                    "status": "pending_approval",
                }
            )
    for draft in state.get("outreachDrafts", []):
        if isinstance(draft, dict) and (not channels or str(draft.get("channel", "")) in channels or "Email" in channels):
            queue.append(
                {
                    "id": draft.get("id", ""),
                    "source": "outreach-draft",
                    "channel": draft.get("channel", ""),
                    "title": draft.get("subject", ""),
                    "action": "send after approval",
                    "status": "pending_approval",
                }
            )
    competitor_report_data = state.get("lastCompetitorReport", {}) if isinstance(state.get("lastCompetitorReport"), dict) else {}
    for campaign in competitor_report_data.get("responseCampaigns", []) if isinstance(competitor_report_data.get("responseCampaigns"), list) else []:
        queue.append(
            {
                "id": slugify(str(campaign.get("name", "response-campaign")), fallback="response-campaign"),
                "source": "competitor-response",
                "channel": ", ".join(campaign.get("channels", [])),
                "title": campaign.get("name", ""),
                "action": "plan response assets after approval",
                "status": "pending_approval",
            }
        )
    return queue


def build_execution_checklists(channels: list[str]) -> list[dict[str, Any]]:
    return [{"channel": channel, "items": checklist_for_channel(channel)} for channel in channels]


def checklist_for_channel(channel: str) -> list[str]:
    lowered = channel.lower()
    common = ["Confirm final copy and CTA.", "Confirm owner and publishing time.", "Capture final URL or screenshot after execution."]
    if "linkedin" in lowered:
        return ["Verify post formatting and link preview.", "Confirm company or personal profile target.", *common]
    if lowered in {"x", "twitter"} or "x/" in lowered:
        return ["Check thread numbering and character length.", "Confirm hashtags and mention policy.", *common]
    if "email" in lowered:
        return ["Confirm recipient list and suppression rules.", "Send test email before production send.", *common]
    if "blog" in lowered or "seo" in lowered:
        return ["Confirm title, meta description, schema, and internal links.", "Run final grammar and SEO review.", *common]
    if "youtube" in lowered:
        return ["Confirm video file, title, description, thumbnail, and chapters.", "Check links in description.", *common]
    return common


def build_execution_risk_review(queue: list[dict[str, Any]]) -> list[str]:
    risks = ["No item should be executed without explicit approval."]
    if any(item.get("source") == "outreach-draft" for item in queue):
        risks.append("Outreach items may contact real people; confirm recipient and consent policy before sending.")
    if any("SEO" in str(item.get("channel", "")) or item.get("source") == "blog-brief" for item in queue):
        risks.append("Publishing SEO/blog content may affect live site quality; confirm final editorial review.")
    if any(item.get("source") == "competitor-response" for item in queue):
        risks.append("Competitor response should stay factual and avoid unsupported claims.")
    return risks


def build_approval_decision(*, package: dict[str, Any], decision: str, approver: str, notes: str) -> dict[str, Any]:
    return {
        "type": "approval-decision",
        "id": slugify(f"decision-{package.get('id', 'package')}-{datetime.now(timezone.utc).isoformat()}", fallback="approval-decision"),
        "packageId": package.get("id", ""),
        "decision": decision,
        "approver": approver,
        "notes": notes.strip(),
        "queueItemCount": len(package.get("publishingQueue", [])),
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def build_operator_handoff(state: dict[str, Any], *, package: dict[str, Any], operator: str) -> dict[str, Any]:
    decisions = [item for item in state.get("approvalDecisions", []) if isinstance(item, dict) and item.get("packageId") == package.get("id")]
    latest_decision = decisions[-1] if decisions else {}
    return {
        "type": "operator-handoff",
        "id": slugify(f"handoff-{package.get('id', 'package')}", fallback="operator-handoff"),
        "packageId": package.get("id", ""),
        "operator": operator,
        "approvalDecision": latest_decision,
        "publishingQueue": package.get("publishingQueue", []),
        "executionChecklists": package.get("executionChecklists", []),
        "requiredEvidence": [
            "Final published URL or platform permalink.",
            "Screenshot or export showing the published/sent asset.",
            "Execution timestamp and operator name.",
            "Any deviation from the approved copy or queue.",
        ],
        "handoffStatus": "ready" if latest_decision.get("decision") == "approved" else "waiting_for_approval",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def build_campaign(spec: CampaignSpec, strategy: dict[str, Any]) -> dict[str, Any]:
    themes = strategy.get("themes", []) if isinstance(strategy.get("themes"), list) else []
    if not themes:
        themes = recommend_themes(str(strategy.get("business") or ""), spec.offer, spec.objective)
    weekly_plan = []
    for index, channel in enumerate(spec.channels, start=1):
        theme = themes[(index - 1) % len(themes)] if themes else "Proof and education"
        weekly_plan.append(
            {
                "week": index,
                "channel": channel,
                "theme": theme,
                "angle": campaign_angle(channel, spec.objective, spec.offer),
                "cta": spec.cta,
            }
        )
    return {
        "type": "campaign",
        "name": spec.name,
        "slug": spec.campaign_slug,
        "objective": spec.objective,
        "audience": spec.audience,
        "offer": spec.offer,
        "channels": spec.channels,
        "duration": spec.duration,
        "cta": spec.cta,
        "message": f"{spec.offer} helps {spec.audience} accomplish {spec.objective}.",
        "themes": themes[:5],
        "weeklyPlan": weekly_plan,
        "successMetrics": ["qualified leads", "demo requests", "website visits", "engagement rate", "content-assisted opportunities"],
        "approvalRequired": True,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }


def status_summary(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    state = read_state(project_dir / STATE_PATH)
    summary = format_summary(project_dir, state)
    return {"ok": True, "projectDir": str(project_dir), "summary": summary, "statePath": str(project_dir / STATE_PATH)}


def format_summary(project_dir: Path, state: dict[str, Any]) -> str:
    strategy = state.get("lastStrategy", {}) if isinstance(state.get("lastStrategy"), dict) else {}
    campaign = state.get("lastCampaign", {}) if isinstance(state.get("lastCampaign"), dict) else {}
    brand = strategy.get("brand") or project_dir.name.replace("-", " ").title()
    lines = [f"**Marketing Status: {brand}**"]
    if strategy.get("positioning"):
        lines.append(f"Positioning: {strategy['positioning']}")
    channels = strategy.get("channels", [])
    if isinstance(channels, list) and channels:
        lines.append("Channels: " + ", ".join(f"`{channel}`" for channel in channels[:5]))
    if campaign.get("name"):
        lines.append(f"Latest campaign: `{campaign['name']}` ({campaign.get('duration', 'duration TBD')})")
    plan = state.get("lastContentPlan", {}) if isinstance(state.get("lastContentPlan"), dict) else {}
    if plan.get("items"):
        lines.append(f"Content plan: `{len(plan['items'])} draft slots` across `{len(plan.get('channels', []))} channels`")
    drafts = state.get("lastContentDrafts", {}) if isinstance(state.get("lastContentDrafts"), dict) else {}
    if drafts.get("drafts"):
        lines.append(f"Content drafts: `{len(drafts['drafts'])}` ready for review")
    seo_plan = state.get("lastSeoPlan", {}) if isinstance(state.get("lastSeoPlan"), dict) else {}
    if seo_plan.get("keywordClusters"):
        lines.append(f"SEO/GEO plan: `{len(seo_plan['keywordClusters'])}` keyword clusters")
    blog_briefs = state.get("lastBlogBriefs", {}) if isinstance(state.get("lastBlogBriefs"), dict) else {}
    if blog_briefs.get("briefs"):
        lines.append(f"Blog briefs: `{len(blog_briefs['briefs'])}` ready for review")
    lead_signals = state.get("lastLeadSignals", {}) if isinstance(state.get("lastLeadSignals"), dict) else {}
    if lead_signals.get("positiveSignals"):
        lines.append(f"Lead signals: `{len(lead_signals['positiveSignals'])}` positive signals")
    scorecard = state.get("lastLeadScorecard", {}) if isinstance(state.get("lastLeadScorecard"), dict) else {}
    if scorecard.get("id"):
        lines.append(f"Latest lead: `{scorecard.get('grade')}` score `{scorecard.get('score')}` for `{scorecard.get('company') or scorecard.get('name')}`")
    outreach = state.get("lastOutreachDraft", {}) if isinstance(state.get("lastOutreachDraft"), dict) else {}
    if outreach.get("id"):
        lines.append(f"Outreach drafts: `{len(state.get('outreachDrafts', []))}` ready for review")
    crm = state.get("lastCrmExport", {}) if isinstance(state.get("lastCrmExport"), dict) else {}
    if crm.get("path"):
        lines.append(f"CRM export: `{crm['path']}`")
    performance = state.get("lastPerformanceSnapshot", {}) if isinstance(state.get("lastPerformanceSnapshot"), dict) else {}
    if performance.get("derivedMetrics"):
        derived = performance["derivedMetrics"]
        lines.append(f"Latest performance: CTR `{percent(derived.get('ctr', 0))}`, lead rate `{percent(derived.get('leadRate', 0))}`")
    dashboard = state.get("lastReviewDashboard", {}) if isinstance(state.get("lastReviewDashboard"), dict) else {}
    if dashboard.get("artifactCounts"):
        lines.append(f"Review dashboard: `{dashboard.get('period', 'latest period')}` with `{len(dashboard.get('reviewQueue', []))}` review queues")
    competitor_report_data = state.get("lastCompetitorReport", {}) if isinstance(state.get("lastCompetitorReport"), dict) else {}
    if competitor_report_data.get("competitorCount"):
        lines.append(
            f"Competitor report: `{competitor_report_data.get('competitorCount')}` competitors, `{competitor_report_data.get('observationCount', 0)}` observations"
        )
    approval = state.get("lastApprovalPackage", {}) if isinstance(state.get("lastApprovalPackage"), dict) else {}
    if approval.get("id"):
        lines.append(f"Approval package: `{len(approval.get('publishingQueue', []))}` queued items, status `{approval.get('approvalStatus', 'pending')}`")
    handoff = state.get("lastOperatorHandoff", {}) if isinstance(state.get("lastOperatorHandoff"), dict) else {}
    if handoff.get("id"):
        lines.append(f"Operator handoff: `{handoff.get('handoffStatus', 'waiting_for_approval')}`")
    lines.append("")
    lines.append("Next: create a campaign, generate content, prepare SEO/GEO tasks, score leads, review analytics, track competitors, or package execution.")
    return "\n".join(lines)


def record_strategy(project_dir: Path, strategy: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state["brand"] = strategy["brand"]
    state.setdefault("strategies", []).append(strategy)
    state["lastStrategy"] = strategy
    state["workflowState"] = "strategy_ready"
    write_state(project_dir, state)


def record_campaign(project_dir: Path, campaign: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state.setdefault("campaigns", []).append(campaign)
    state["lastCampaign"] = campaign
    state["workflowState"] = "campaign_ready"
    write_state(project_dir, state)


def record_content_plan(project_dir: Path, plan: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state.setdefault("contentPlans", []).append(plan)
    state["lastContentPlan"] = plan
    state["workflowState"] = "content_plan_ready"
    write_state(project_dir, state)


def record_content_drafts(project_dir: Path, drafts: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state.setdefault("contentDrafts", []).append(drafts)
    state["lastContentDrafts"] = drafts
    state["workflowState"] = "content_drafts_ready"
    write_state(project_dir, state)


def record_seo_plan(project_dir: Path, plan: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state.setdefault("seoPlans", []).append(plan)
    state["lastSeoPlan"] = plan
    state["workflowState"] = "seo_plan_ready"
    write_state(project_dir, state)


def record_blog_briefs(project_dir: Path, briefs: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state.setdefault("blogBriefs", []).append(briefs)
    state["lastBlogBriefs"] = briefs
    state["workflowState"] = "blog_briefs_ready"
    write_state(project_dir, state)


def record_lead_signals(project_dir: Path, lead_signals: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state.setdefault("leadSignals", []).append(lead_signals)
    state["lastLeadSignals"] = lead_signals
    state["workflowState"] = "lead_signals_ready"
    write_state(project_dir, state)


def record_lead_scorecard(project_dir: Path, scorecard: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state.setdefault("leadScorecards", []).append(scorecard)
    state["lastLeadScorecard"] = scorecard
    state["workflowState"] = "lead_scored"
    write_state(project_dir, state)


def record_outreach_draft(project_dir: Path, draft: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state.setdefault("outreachDrafts", []).append(draft)
    state["lastOutreachDraft"] = draft
    state["workflowState"] = "outreach_draft_ready"
    write_state(project_dir, state)


def record_crm_export(project_dir: Path, export: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state.setdefault("crmExports", []).append(export)
    state["lastCrmExport"] = export
    state["workflowState"] = "crm_export_ready"
    write_state(project_dir, state)


def record_performance_snapshot(project_dir: Path, snapshot: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state.setdefault("performanceSnapshots", []).append(snapshot)
    state["lastPerformanceSnapshot"] = snapshot
    state["workflowState"] = "performance_snapshot_ready"
    write_state(project_dir, state)


def record_review_dashboard(project_dir: Path, dashboard: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state.setdefault("reviewDashboards", []).append(dashboard)
    state["lastReviewDashboard"] = dashboard
    state["workflowState"] = "review_dashboard_ready"
    write_state(project_dir, state)


def record_competitor(project_dir: Path, competitor: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state["competitors"] = upsert_by_id([item for item in state.get("competitors", []) if isinstance(item, dict)], competitor)
    state["lastCompetitor"] = competitor
    state["workflowState"] = "competitor_profile_ready"
    write_state(project_dir, state)


def record_competitor_observation(project_dir: Path, observation: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state.setdefault("competitorObservations", []).append(observation)
    state["lastCompetitorObservation"] = observation
    state["workflowState"] = "competitor_observation_ready"
    write_state(project_dir, state)


def record_competitor_report(project_dir: Path, report: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state.setdefault("competitorReports", []).append(report)
    state["lastCompetitorReport"] = report
    state["workflowState"] = "competitor_report_ready"
    write_state(project_dir, state)


def record_approval_package(project_dir: Path, package: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state.setdefault("approvalPackages", []).append(package)
    state["lastApprovalPackage"] = package
    state["workflowState"] = "approval_package_ready"
    write_state(project_dir, state)


def record_approval_decision(project_dir: Path, decision: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state.setdefault("approvalDecisions", []).append(decision)
    if decision.get("packageId"):
        for package in state.get("approvalPackages", []):
            if isinstance(package, dict) and package.get("id") == decision["packageId"]:
                package["approvalStatus"] = decision["decision"]
                state["lastApprovalPackage"] = package
    state["lastApprovalDecision"] = decision
    state["workflowState"] = "approval_decision_recorded"
    write_state(project_dir, state)


def record_operator_handoff(project_dir: Path, handoff: dict[str, Any]) -> None:
    state = read_state(project_dir / STATE_PATH)
    state.setdefault("operatorHandoffs", []).append(handoff)
    state["lastOperatorHandoff"] = handoff
    state["workflowState"] = "operator_handoff_ready"
    write_state(project_dir, state)


def recommend_channels(business: str, audience: str, goal: str) -> list[str]:
    text = f"{business} {audience} {goal}".lower()
    channels = ["LinkedIn", "SEO blog", "Email", "YouTube", "X"]
    if any(word in text for word in ("industrial", "manufacturing", "lidar", "logistics", "enterprise", "b2b")):
        return ["LinkedIn", "SEO blog", "YouTube demos", "Industry forums", "Email", "Distributor outreach"]
    if any(word in text for word in ("shop", "ecommerce", "retail", "consumer", "fashion", "beauty")):
        return ["Instagram", "TikTok", "Shopify blog", "Email", "Facebook", "Influencer outreach"]
    if any(word in text for word in ("local", "clinic", "restaurant", "salon", "law", "dental")):
        return ["Google Business Profile", "Local SEO", "Instagram", "Facebook", "Email", "Reviews"]
    if any(word in text for word in ("saas", "software", "ai", "startup", "dashboard")):
        return ["LinkedIn", "SEO blog", "X", "Product Hunt", "YouTube demos", "Email"]
    return channels


def recommend_themes(business: str, offer: str, goal: str) -> list[str]:
    text = f"{business} {offer} {goal}".lower()
    base = ["Problem education", "Customer proof", "ROI and outcomes", "Behind the product", "FAQ and objection handling"]
    if any(word in text for word in ("lidar", "industrial", "manufacturing", "logistics")):
        return ["Operational ROI", "Accuracy and measurement proof", "Safety and compliance", "Before and after workflow", "Technical demo"]
    if any(word in text for word in ("ai", "software", "saas", "automation")):
        return ["Workflow automation", "Time saved", "Integration proof", "Founder POV", "Product demo"]
    if any(word in text for word in ("shop", "ecommerce", "product")):
        return ["Product benefits", "Lifestyle use cases", "Social proof", "Bundles and offers", "Buying guide"]
    return base


def infer_industries(business: str, audience: str) -> list[str]:
    text = f"{business} {audience}".lower()
    if any(word in text for word in ("lidar", "volume", "truck", "rail", "port", "mining")):
        return ["mining", "aggregates", "logistics", "ports", "rail", "construction materials"]
    if any(word in text for word in ("saas", "software", "ai")):
        return ["software", "operations", "technology", "professional services"]
    if any(word in text for word in ("shop", "retail", "ecommerce")):
        return ["retail", "direct-to-consumer", "online commerce"]
    return ["small business", "professional services", "local market"]


def infer_pain_points(business: str, offer: str) -> list[str]:
    text = f"{business} {offer}".lower()
    if any(word in text for word in ("measurement", "lidar", "volume")):
        return ["manual measurement errors", "loading loss", "slow inspections", "limited operational visibility"]
    if any(word in text for word in ("automation", "ai", "software")):
        return ["manual workflows", "slow reporting", "fragmented data", "inconsistent follow-up"]
    return ["low visibility", "unclear differentiation", "inconsistent lead flow", "weak conversion path"]


def infer_buying_triggers(goal: str, offer: str) -> list[str]:
    return [
        f"Actively trying to {goal.lower()}",
        f"Researching {offer.lower()}",
        "Comparing vendors or asking peers for recommendations",
        "Budget or operational pressure creates urgency",
    ]


def build_brand_voice(tone: str) -> dict[str, Any]:
    normalized = tone or "professional"
    return {
        "tone": normalized,
        "rules": [
            "Lead with business value before features.",
            "Use concrete examples and measurable outcomes.",
            "Avoid unsupported claims and fake urgency.",
            "Keep CTAs direct and easy to act on.",
        ],
    }


def build_seo_focus(business: str, offer: str, audience: str) -> dict[str, Any]:
    root = slugify(offer or business, fallback="solution").replace("-", " ")
    audience_term = slugify(audience, fallback="customers").replace("-", " ")
    return {
        "keywordClusters": [
            f"{root} for {audience_term}",
            f"{root} ROI",
            f"{root} case study",
            f"best {root} solution",
        ],
        "geoFocus": [
            "Define the category in plain language for AI answer engines.",
            "Publish comparison, FAQ, and use-case pages.",
            "Use consistent terminology across site, blog, social, and outreach.",
        ],
    }


def build_keyword_clusters(offer: str, audience: str, business: str, base_clusters: list[Any]) -> list[dict[str, Any]]:
    roots = [str(item) for item in base_clusters if str(item).strip()]
    root = slugify(offer or business, fallback="solution").replace("-", " ")
    audience_term = slugify(audience, fallback="customers").replace("-", " ")
    roots.extend(
        [
            f"{root} for {audience_term}",
            f"{root} ROI",
            f"{root} comparison",
            f"{root} implementation",
            f"{root} case study",
            f"{root} FAQ",
        ]
    )
    unique_roots = []
    for item in roots:
        if item not in unique_roots:
            unique_roots.append(item)
    clusters = []
    for index, primary in enumerate(unique_roots[:8]):
        clusters.append(
            {
                "primary": primary,
                "intent": ["commercial", "informational", "comparison", "problem-aware"][index % 4],
                "secondary": [
                    f"{primary} benefits",
                    f"{primary} cost",
                    f"{primary} examples",
                ],
                "questions": [
                    f"What is {primary}?",
                    f"How do buyers evaluate {primary}?",
                    f"What results should teams expect from {primary}?",
                ],
            }
        )
    return clusters


def seo_page_title(page_type: str, cluster: dict[str, Any], brand: str) -> str:
    primary = cluster["primary"]
    if page_type == "pillar":
        return f"{primary.title()}: Complete Buyer Guide"
    if page_type == "comparison":
        return f"How to Compare {primary.title()} Options"
    if page_type == "use-case":
        return f"{primary.title()} Use Cases for Operations Teams"
    if page_type == "faq":
        return f"{primary.title()} FAQ"
    if page_type == "case-study":
        return f"{brand} Case Study: {primary.title()}"
    return f"{primary.title()} Integration Guide"


def suggested_internal_links(page_type: str) -> list[str]:
    common = ["campaign landing page", "contact/demo page"]
    if page_type == "pillar":
        return ["comparison page", "FAQ page", "case study", *common]
    if page_type == "comparison":
        return ["pillar page", "pricing or ROI section", *common]
    if page_type == "faq":
        return ["pillar page", "supporting blog posts", *common]
    return ["pillar page", "related use case", *common]


def build_geo_recommendations(brand: str, offer: str, audience: str) -> list[str]:
    return [
        f"Write a concise category definition for {offer} that AI answer engines can quote.",
        f"Publish a {brand} FAQ that directly answers buyer questions from {audience}.",
        "Create comparison pages that explain selection criteria without attacking competitors.",
        "Use consistent entities: brand name, product category, audience, industry, and use cases.",
        "Add short answer blocks under H2 headings so AI snippets can extract complete answers.",
    ]


def blog_title(intent: str, primary_keyword: str, offer: str) -> str:
    if intent == "comparison":
        return f"How to Compare {primary_keyword.title()} Vendors"
    if intent == "commercial":
        return f"Best Practices for Buying {offer.title()}"
    if intent == "problem-aware":
        return f"Why Teams Struggle With {primary_keyword.title()}"
    return f"What Is {primary_keyword.title()}?"


def campaign_angle(channel: str, objective: str, offer: str) -> str:
    lowered = channel.lower()
    if "linkedin" in lowered:
        return f"Business outcome: how {offer} supports {objective}."
    if "youtube" in lowered or "demo" in lowered:
        return f"Show the workflow before and after using {offer}."
    if "seo" in lowered or "blog" in lowered:
        return f"Search-intent article that answers buyer questions around {offer}."
    if "email" in lowered:
        return f"Case-study style sequence driving toward {objective}."
    return f"Short platform-native story about {offer} and {objective}."


def content_stage(week: int, total_weeks: int) -> str:
    if total_weeks <= 1 or week == 1:
        return "awareness"
    if week >= total_weeks:
        return "conversion"
    return "consideration"


def platform_format(channel: str) -> str:
    lowered = channel.lower()
    if "linkedin" in lowered:
        return "thought leadership post"
    if lowered in {"x", "twitter"} or "x/" in lowered:
        return "short thread"
    if "youtube" in lowered:
        return "video script outline"
    if "tiktok" in lowered or "instagram" in lowered:
        return "short-form video script"
    if "blog" in lowered or "seo" in lowered:
        return "SEO article brief"
    if "email" in lowered:
        return "email sequence message"
    if "discord" in lowered:
        return "community announcement"
    if "reddit" in lowered:
        return "discussion starter"
    return "platform-native post"


def content_angle(channel: str, stage: str, theme: str, campaign: dict[str, Any]) -> str:
    offer = str(campaign.get("offer") or "the offer")
    objective = str(campaign.get("objective") or "the campaign goal")
    lowered = channel.lower()
    if "linkedin" in lowered:
        return f"{theme}: executive lesson about {offer} and {objective}."
    if lowered in {"x", "twitter"} or "x/" in lowered:
        return f"{theme}: concise thread with one proof point and one CTA."
    if "youtube" in lowered:
        return f"{theme}: demo narrative showing the problem, workflow, and result."
    if "blog" in lowered or "seo" in lowered:
        return f"{theme}: search-intent brief for buyers in {stage} stage."
    if "email" in lowered:
        return f"{theme}: nurture message that moves the reader toward {campaign.get('cta', 'the CTA')}."
    return f"{theme}: {stage} content adapted for {channel}."


def draft_for_channel(
    *,
    channel: str,
    brand: str,
    campaign: dict[str, Any],
    theme: str,
    stage: str,
    tone: str,
    index: int,
) -> dict[str, Any]:
    lowered = channel.lower()
    if "linkedin" in lowered:
        content = linkedin_draft(brand, campaign, theme, stage)
    elif lowered in {"x", "twitter"} or "x/" in lowered:
        content = x_thread_draft(brand, campaign, theme, stage)
    elif "youtube" in lowered:
        content = youtube_script_draft(brand, campaign, theme, stage)
    elif "blog" in lowered or "seo" in lowered:
        content = blog_brief_draft(brand, campaign, theme, stage)
    elif "email" in lowered:
        content = email_draft(brand, campaign, theme, stage)
    elif "discord" in lowered:
        content = discord_draft(brand, campaign, theme, stage)
    else:
        content = generic_social_draft(brand, campaign, theme, stage, channel)
    return {
        "id": slugify(f"{campaign.get('slug', 'campaign')}-{channel}-{index}", fallback=f"draft-{index}"),
        "channel": channel,
        "format": platform_format(channel),
        "theme": theme,
        "stage": stage,
        "tone": tone,
        "content": content,
        "approvalStatus": "draft",
    }


def linkedin_draft(brand: str, campaign: dict[str, Any], theme: str, stage: str) -> str:
    offer = campaign.get("offer", "the solution")
    objective = campaign.get("objective", "improve outcomes")
    cta = campaign.get("cta", "Book a consultation")
    return (
        f"{theme} is not just a marketing message. It is often the difference between a team that can measure progress and a team that is guessing.\n\n"
        f"For {campaign.get('audience', 'buyers')}, {offer} should connect directly to {objective}.\n\n"
        "A useful evaluation question:\n"
        f"Can this approach show a measurable before/after result in the {stage} stage of the buying journey?\n\n"
        f"{brand} is building around that standard.\n\n"
        f"CTA: {cta}"
    )


def x_thread_draft(brand: str, campaign: dict[str, Any], theme: str, stage: str) -> str:
    offer = campaign.get("offer", "the offer")
    return (
        f"1/ {theme}: most teams do not need more dashboards. They need a clearer path from problem to action.\n\n"
        f"2/ For {campaign.get('audience', 'buyers')}, {offer} should make the operational decision easier, not just add another tool.\n\n"
        f"3/ In the {stage} stage, the best content proves one thing: what changes after adoption?\n\n"
        f"4/ {brand} campaign CTA: {campaign.get('cta', 'Learn more')}"
    )


def youtube_script_draft(brand: str, campaign: dict[str, Any], theme: str, stage: str) -> str:
    return (
        f"Title: {theme} - {brand} demo\n\n"
        "Hook: Show the costly before-state in the first 10 seconds.\n"
        f"Problem: Explain why {campaign.get('audience', 'buyers')} struggle with {campaign.get('objective', 'the goal')}.\n"
        f"Demo: Walk through how {campaign.get('offer', 'the offer')} changes the workflow.\n"
        "Proof: Show the measurable result, comparison, or operator quote.\n"
        f"CTA: {campaign.get('cta', 'Book a demo')}.\n"
        f"Stage: {stage}"
    )


def blog_brief_draft(brand: str, campaign: dict[str, Any], theme: str, stage: str) -> str:
    offer = campaign.get("offer", "solution")
    return (
        f"SEO Title: {theme}: How {campaign.get('audience', 'buyers')} Evaluate {offer}\n"
        f"Meta Description: Learn how to evaluate {offer}, what outcomes matter, and how {brand} supports {campaign.get('objective', 'better results')}.\n\n"
        "Outline:\n"
        f"- Why {theme.lower()} matters now\n"
        f"- Common mistakes when evaluating {offer}\n"
        "- What metrics to compare\n"
        "- Example workflow or use case\n"
        f"- CTA: {campaign.get('cta', 'Talk to an expert')}\n"
        f"Search stage: {stage}"
    )


def email_draft(brand: str, campaign: dict[str, Any], theme: str, stage: str) -> str:
    return (
        f"Subject: A practical way to think about {theme.lower()}\n\n"
        f"Hi,\n\nTeams trying to {campaign.get('objective', 'improve results')} often start with tools, but the better starting point is the workflow.\n\n"
        f"{campaign.get('offer', 'Our offer')} is designed to help {campaign.get('audience', 'your team')} move from uncertainty to a clear next action.\n\n"
        f"If useful, {brand} can walk through the before/after workflow.\n\n"
        f"{campaign.get('cta', 'Book a consultation')}\n\n"
        f"Stage: {stage}"
    )


def discord_draft(brand: str, campaign: dict[str, Any], theme: str, stage: str) -> str:
    return (
        f"New campaign note from {brand}: {theme}\n\n"
        f"We are focusing on {campaign.get('objective', 'the campaign goal')} for {campaign.get('audience', 'our audience')}.\n"
        f"Core offer: {campaign.get('offer', 'the offer')}.\n"
        f"Next step: {campaign.get('cta', 'Learn more')}.\n\n"
        f"This is a {stage} stage message for review."
    )


def generic_social_draft(brand: str, campaign: dict[str, Any], theme: str, stage: str, channel: str) -> str:
    return (
        f"{brand} - {theme}\n\n"
        f"For {campaign.get('audience', 'buyers')}, {campaign.get('offer', 'the offer')} should support {campaign.get('objective', 'the goal')}.\n\n"
        f"{campaign.get('cta', 'Learn more')}\n\n"
        f"Channel: {channel}. Stage: {stage}."
    )


def parse_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def percent(value: Any) -> str:
    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return "0.0%"


def render_strategy_markdown(strategy: dict[str, Any]) -> str:
    icp = strategy["icp"]
    lines = [
        f"# Marketing Strategy: {strategy['brand']}",
        "",
        "## Positioning",
        strategy["positioning"],
        "",
        "## ICP",
        f"- Primary audience: {icp['primary']}",
        "- Industries: " + ", ".join(icp["industries"]),
        "- Pain points: " + ", ".join(icp["painPoints"]),
        "- Buying triggers: " + ", ".join(icp["buyingTriggers"]),
        "",
        "## Channels",
        *[f"- {channel}" for channel in strategy["channels"]],
        "",
        "## Content Themes",
        *[f"- {theme}" for theme in strategy["themes"]],
        "",
        "## Funnel",
    ]
    for stage in strategy["funnel"]:
        lines.extend([f"### {stage['stage']}", stage["goal"], "Channels: " + ", ".join(stage["channels"]), ""])
    lines.extend(
        [
            "## Brand Voice",
            f"Tone: {strategy['brandVoice']['tone']}",
            *[f"- {rule}" for rule in strategy["brandVoice"]["rules"]],
            "",
            "## SEO + GEO Focus",
            "Keyword clusters:",
            *[f"- {item}" for item in strategy["seoFocus"]["keywordClusters"]],
            "AI answer engine rules:",
            *[f"- {item}" for item in strategy["seoFocus"]["geoFocus"]],
        ]
    )
    return "\n".join(lines)


def render_campaign_markdown(campaign: dict[str, Any]) -> str:
    lines = [
        f"# Campaign: {campaign['name']}",
        "",
        f"- Objective: {campaign['objective']}",
        f"- Audience: {campaign['audience']}",
        f"- Offer: {campaign['offer']}",
        f"- Duration: {campaign['duration']}",
        f"- CTA: {campaign['cta']}",
        "",
        "## Message",
        campaign["message"],
        "",
        "## Themes",
        *[f"- {theme}" for theme in campaign["themes"]],
        "",
        "## Weekly Channel Plan",
    ]
    for item in campaign["weeklyPlan"]:
        lines.extend(
            [
                f"### Week {item['week']}: {item['channel']}",
                f"- Theme: {item['theme']}",
                f"- Angle: {item['angle']}",
                f"- CTA: {item['cta']}",
                "",
            ]
        )
    lines.extend(["## Success Metrics", *[f"- {metric}" for metric in campaign["successMetrics"]]])
    return "\n".join(lines)


def render_content_plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        f"# Content Calendar: {plan['campaign']}",
        "",
        f"- Weeks: {plan['weeks']}",
        f"- Cadence: {plan['cadencePerWeek']} items per week",
        "- Channels: " + ", ".join(plan["channels"]),
        "- Approval: required before publishing",
        "",
        "## Calendar",
    ]
    for item in plan["items"]:
        lines.extend(
            [
                f"### Week {item['week']} / Slot {item['slot']}: {item['channel']}",
                f"- Stage: {item['stage']}",
                f"- Theme: {item['theme']}",
                f"- Format: {item['format']}",
                f"- Angle: {item['angle']}",
                f"- CTA: {item['cta']}",
                "",
            ]
        )
    return "\n".join(lines)


def render_drafts_markdown(drafts: dict[str, Any]) -> str:
    lines = [
        f"# Content Drafts: {drafts['campaign']}",
        "",
        "- Status: draft for review",
        "- Approval: required before publishing",
        "",
    ]
    for draft in drafts["drafts"]:
        lines.extend(
            [
                f"## {draft['channel']} - {draft['theme']}",
                "",
                f"- Format: {draft['format']}",
                f"- Stage: {draft['stage']}",
                f"- Tone: {draft['tone']}",
                "",
                draft["content"],
                "",
            ]
        )
    return "\n".join(lines)


def render_seo_plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        f"# SEO + GEO Plan: {plan['brand']}",
        "",
        f"- Offer: {plan['offer']}",
        f"- Audience: {plan['audience']}",
        f"- Region: {plan['region']}",
        f"- Focus: {plan['focus']}",
        "",
        "## Keyword Clusters",
    ]
    for cluster in plan["keywordClusters"]:
        lines.extend(
            [
                f"### {cluster['primary']}",
                f"- Intent: {cluster['intent']}",
                "- Secondary: " + ", ".join(cluster["secondary"]),
                "- Questions:",
                *[f"  - {question}" for question in cluster["questions"]],
                "",
            ]
        )
    lines.append("## Page Plan")
    for page in plan["pagePlan"]:
        lines.extend(
            [
                f"### {page['title']}",
                f"- Type: {page['type']}",
                f"- Primary keyword: {page['primaryKeyword']}",
                f"- Intent: {page['intent']}",
                f"- CTA: {page['cta']}",
                "- Internal links: " + ", ".join(page["internalLinks"]),
                "",
            ]
        )
    lines.extend(
        [
            "## AI Answer Engine Recommendations",
            *[f"- {item}" for item in plan["geoRecommendations"]],
            "",
            "## Schema Recommendations",
            *[f"- {item}" for item in plan["schemaRecommendations"]],
            "",
            "## Technical Tasks",
            *[f"- {item}" for item in plan["technicalTasks"]],
        ]
    )
    return "\n".join(lines)


def render_blog_briefs_markdown(briefs: dict[str, Any]) -> str:
    lines = [
        f"# SEO Blog Briefs: {briefs['brand']}",
        "",
        f"- Offer: {briefs['offer']}",
        "- Approval: required before publishing",
        "",
    ]
    for brief in briefs["briefs"]:
        lines.extend(
            [
                f"## {brief['title']}",
                "",
                f"- Slug: {brief['slug']}",
                f"- Intent: {brief['intent']}",
                f"- Primary keyword: {brief['primaryKeyword']}",
                "- Secondary keywords: " + ", ".join(brief["secondaryKeywords"]),
                f"- Meta description: {brief['metaDescription']}",
                "",
                "### Outline",
                *[f"- {item}" for item in brief["outline"]],
                "",
                "### AI Answer Summary",
                brief["aiAnswerSummary"],
                "",
                "### Schema",
                *[f"- {item}" for item in brief["schema"]],
                "",
                "### Internal Links",
                *[f"- {item}" for item in brief["internalLinks"]],
                "",
            ]
        )
    return "\n".join(lines)


def render_lead_signals_markdown(lead_signals: dict[str, Any]) -> str:
    lines = [
        f"# Lead Signals: {lead_signals.get('brand', 'Marketing Project')}",
        "",
        f"- Audience: {lead_signals.get('audience', '')}",
        f"- Offer: {lead_signals.get('offer', '')}",
        "- Approval: required before outreach or CRM writes",
        "",
        "## Channels to Monitor",
        *[f"- {channel}" for channel in lead_signals.get("channels", [])],
        "",
        "## Positive Signals",
        *[f"- {signal}" for signal in lead_signals.get("positiveSignals", [])],
        "",
        "## Buying Trigger Phrases",
        *[f"- {signal}" for signal in lead_signals.get("buyingTriggerPhrases", [])],
        "",
        "## Pain Point Phrases",
        *[f"- {signal}" for signal in lead_signals.get("painPointPhrases", [])],
        "",
        "## Negative Signals",
        *[f"- {signal}" for signal in lead_signals.get("negativeSignals", [])],
        "",
        "## Scoring Rules",
        *[f"- {rule}" for rule in lead_signals.get("scoringRules", [])],
    ]
    return "\n".join(lines)


def render_scorecards_markdown(scorecards: list[dict[str, Any]]) -> str:
    lines = ["# Lead Scorecards", "", "- Status: review before outreach or CRM import", ""]
    for scorecard in scorecards:
        lines.extend(
            [
                f"## {scorecard.get('company') or scorecard.get('name') or scorecard.get('id')}",
                "",
                f"- Lead ID: {scorecard.get('id', '')}",
                f"- Name: {scorecard.get('name', '')}",
                f"- Role: {scorecard.get('role', '')}",
                f"- Source: {scorecard.get('source', '')}",
                f"- Channel: {scorecard.get('channel', '')}",
                f"- URL: {scorecard.get('url', '')}",
                f"- Score: {scorecard.get('score', 0)}",
                f"- Grade: {scorecard.get('grade', '')}",
                f"- Suggested action: {scorecard.get('suggestedAction', '')}",
                "",
                "### Matched Signals",
                *[f"- {signal}" for signal in scorecard.get("matchedSignals", [])],
                "",
                "### Rationale",
                str(scorecard.get("rationale", "")),
                "",
                "### Lead Text",
                str(scorecard.get("text", "")),
                "",
            ]
        )
    return "\n".join(lines)


def render_outreach_markdown(drafts: list[dict[str, Any]]) -> str:
    lines = ["# Outreach Drafts", "", "- Status: draft only", "- Approval: required before sending", ""]
    for draft in drafts:
        lines.extend(
            [
                f"## {draft.get('channel', '')}: {draft.get('leadId', '')}",
                "",
                f"- Draft ID: {draft.get('id', '')}",
                f"- Tone: {draft.get('tone', '')}",
                f"- Subject: {draft.get('subject', '')}",
                "",
                "### Body",
                str(draft.get("body", "")),
                "",
                "### Follow-up Schedule",
            ]
        )
        for step in draft.get("followUpSchedule", []):
            lines.append(f"- Day {step.get('dayOffset', 0)}: {step.get('action', '')}")
        lines.append("")
    return "\n".join(lines)


def render_performance_snapshots_markdown(snapshots: list[dict[str, Any]]) -> str:
    lines = ["# Performance Snapshots", "", "- Source: manually supplied or imported metrics", ""]
    for snapshot in snapshots:
        metrics = snapshot.get("metrics", {}) if isinstance(snapshot.get("metrics"), dict) else {}
        derived = snapshot.get("derivedMetrics", {}) if isinstance(snapshot.get("derivedMetrics"), dict) else {}
        lines.extend(
            [
                f"## {snapshot.get('campaign', 'Campaign')} - {snapshot.get('channel', 'all channels')}",
                "",
                f"- Period: {snapshot.get('period', '')}",
                f"- Impressions: {metrics.get('impressions', 0):.0f}",
                f"- Engagements: {metrics.get('engagements', 0):.0f}",
                f"- Clicks: {metrics.get('clicks', 0):.0f}",
                f"- Leads: {metrics.get('leads', 0):.0f}",
                f"- Conversions: {metrics.get('conversions', 0):.0f}",
                f"- Spend: {metrics.get('spend', 0):.2f}",
                f"- Revenue: {metrics.get('revenue', 0):.2f}",
                f"- Engagement rate: {percent(derived.get('engagementRate', 0))}",
                f"- CTR: {percent(derived.get('ctr', 0))}",
                f"- Lead rate: {percent(derived.get('leadRate', 0))}",
                f"- Conversion rate: {percent(derived.get('conversionRate', 0))}",
                "",
                "### Recommendations",
                *[f"- {item}" for item in snapshot.get("recommendations", [])],
                "",
            ]
        )
        if snapshot.get("notes"):
            lines.extend(["### Notes", str(snapshot["notes"]), ""])
    return "\n".join(lines)


def render_review_dashboard_markdown(dashboard: dict[str, Any]) -> str:
    totals = dashboard.get("performanceTotals", {}) if isinstance(dashboard.get("performanceTotals"), dict) else {}
    total_metrics = totals.get("totals", {}) if isinstance(totals.get("totals"), dict) else {}
    derived = totals.get("derivedMetrics", {}) if isinstance(totals.get("derivedMetrics"), dict) else {}
    lead_funnel = dashboard.get("leadFunnel", {}) if isinstance(dashboard.get("leadFunnel"), dict) else {}
    counts = dashboard.get("artifactCounts", {}) if isinstance(dashboard.get("artifactCounts"), dict) else {}
    lines = [
        f"# Manager Review Dashboard: {dashboard.get('brand', 'Marketing Project')}",
        "",
        f"- Focus: {dashboard.get('focus', '')}",
        f"- Period: {dashboard.get('period', '')}",
        "",
        "## Artifact Counts",
    ]
    for key, value in counts.items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Performance Totals",
            f"- Impressions: {total_metrics.get('impressions', 0):.0f}",
            f"- Engagements: {total_metrics.get('engagements', 0):.0f}",
            f"- Clicks: {total_metrics.get('clicks', 0):.0f}",
            f"- Leads: {total_metrics.get('leads', 0):.0f}",
            f"- Conversions: {total_metrics.get('conversions', 0):.0f}",
            f"- Spend: {total_metrics.get('spend', 0):.2f}",
            f"- Revenue: {total_metrics.get('revenue', 0):.2f}",
            f"- CTR: {percent(derived.get('ctr', 0))}",
            f"- Lead rate: {percent(derived.get('leadRate', 0))}",
            f"- ROAS: {derived.get('roas', 0):.2f}",
            "",
            "## Lead Funnel",
            f"- Total leads: {lead_funnel.get('total', 0)}",
            f"- Hot: {lead_funnel.get('hot', 0)}",
            f"- Warm: {lead_funnel.get('warm', 0)}",
            f"- Nurture: {lead_funnel.get('nurture', 0)}",
            f"- Sales-ready rate: {percent(lead_funnel.get('salesReadyRate', 0))}",
            "",
            "## Review Queue",
        ]
    )
    for item in dashboard.get("reviewQueue", []):
        lines.append(f"- {item.get('artifact', '')}: {item.get('count', 0)} - {item.get('action', '')}")
    lines.extend(["", "## Optimization Recommendations"])
    lines.extend(f"- {item}" for item in dashboard.get("optimizationRecommendations", []))
    return "\n".join(lines)


def render_competitor_profiles_markdown(competitors: list[dict[str, Any]]) -> str:
    lines = ["# Competitor Profiles", "", "- Source: user-supplied competitor notes", ""]
    for competitor in competitors:
        lines.extend(
            [
                f"## {competitor.get('name', '')}",
                "",
                f"- ID: {competitor.get('id', '')}",
                f"- URL: {competitor.get('url', '')}",
                f"- Category: {competitor.get('category', '')}",
                f"- Positioning: {competitor.get('positioning', '')}",
                "",
                "### Strengths",
                *[f"- {item}" for item in competitor.get("strengths", [])],
                "",
                "### Weaknesses",
                *[f"- {item}" for item in competitor.get("weaknesses", [])],
                "",
                "### Channels",
                *[f"- {item}" for item in competitor.get("channels", [])],
                "",
                "### Watch Topics",
                *[f"- {item}" for item in competitor.get("watchTopics", [])],
                "",
            ]
        )
    return "\n".join(lines)


def render_competitor_observations_markdown(observations: list[dict[str, Any]]) -> str:
    lines = ["# Competitor Observations", "", "- Source: user-supplied market observations", ""]
    for observation in observations:
        lines.extend(
            [
                f"## {observation.get('competitorName', '')}: {observation.get('eventType', '')}",
                "",
                f"- ID: {observation.get('id', '')}",
                f"- Channel: {observation.get('channel', '')}",
                f"- Impact: {observation.get('impact', '')}",
                f"- URL: {observation.get('url', '')}",
                f"- Tags: {', '.join(observation.get('tags', []))}",
                "",
                "### Summary",
                str(observation.get("summary", "")),
                "",
                "### Response Ideas",
                *[f"- {item}" for item in observation.get("responseIdeas", [])],
                "",
            ]
        )
    return "\n".join(lines)


def render_competitor_report_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Competitor Intelligence Report: {report.get('brand', 'Marketing Project')}",
        "",
        f"- Focus: {report.get('focus', '')}",
        f"- Period: {report.get('period', '')}",
        f"- Competitors: {report.get('competitorCount', 0)}",
        f"- Observations: {report.get('observationCount', 0)}",
        "",
        "## Positioning Gaps",
    ]
    for gap in report.get("positioningGaps", []):
        lines.extend(
            [
                f"### {gap.get('competitor', '')}",
                f"- Risk: {gap.get('risk', '')}",
                f"- Opening: {gap.get('opening', '')}",
                f"- Recommended message: {gap.get('recommendedMessage', '')}",
                "",
            ]
        )
    lines.append("## Market Trends")
    for trend in report.get("marketTrends", []):
        lines.extend([f"- {trend.get('topic', '')}: {trend.get('recommendation', '')}"])
    lines.extend(["", "## Response Campaigns"])
    for campaign in report.get("responseCampaigns", []):
        lines.extend(
            [
                f"### {campaign.get('name', '')}",
                f"- Objective: {campaign.get('objective', '')}",
                f"- Message: {campaign.get('message', '')}",
                "- Channels: " + ", ".join(campaign.get("channels", [])),
                "",
            ]
        )
    lines.append("## Recent Observations")
    for observation in report.get("recentObservations", []):
        lines.append(f"- {observation.get('competitorName', '')}: {observation.get('summary', '')}")
    return "\n".join(lines)


def render_approval_package_markdown(package: dict[str, Any]) -> str:
    lines = [
        f"# Approval Package: {package.get('campaign') or package.get('brand')}",
        "",
        f"- Package ID: {package.get('id', '')}",
        f"- Scope: {package.get('scope', '')}",
        f"- Owner: {package.get('owner', '')}",
        f"- Due: {package.get('due', '')}",
        f"- Status: {package.get('approvalStatus', '')}",
        "- Approval: required before execution",
        "",
        "## Publishing Queue",
    ]
    for item in package.get("publishingQueue", []):
        lines.append(f"- [{item.get('status', '')}] {item.get('source', '')} / {item.get('channel', '')}: {item.get('title', '')} ({item.get('action', '')})")
    lines.extend(["", "## Execution Checklists"])
    for checklist in package.get("executionChecklists", []):
        lines.append(f"### {checklist.get('channel', '')}")
        lines.extend(f"- {item}" for item in checklist.get("items", []))
        lines.append("")
    lines.append("## Risk Review")
    lines.extend(f"- {item}" for item in package.get("riskReview", []))
    return "\n".join(lines)


def render_change_log_markdown(decisions: list[dict[str, Any]]) -> str:
    lines = ["# Approval Change Log", ""]
    for decision in decisions:
        lines.extend(
            [
                f"## {decision.get('decision', '')}: {decision.get('packageId', '')}",
                "",
                f"- Decision ID: {decision.get('id', '')}",
                f"- Approver: {decision.get('approver', '')}",
                f"- Queue items: {decision.get('queueItemCount', 0)}",
                f"- Created: {decision.get('createdAt', '')}",
                "",
                "### Notes",
                str(decision.get("notes", "")),
                "",
            ]
        )
    return "\n".join(lines)


def render_operator_handoff_markdown(handoff: dict[str, Any]) -> str:
    decision = handoff.get("approvalDecision", {}) if isinstance(handoff.get("approvalDecision"), dict) else {}
    lines = [
        f"# Operator Handoff: {handoff.get('packageId', '')}",
        "",
        f"- Operator: {handoff.get('operator', '')}",
        f"- Status: {handoff.get('handoffStatus', '')}",
        f"- Approval decision: {decision.get('decision', 'none')}",
        f"- Approver: {decision.get('approver', '')}",
        "",
        "## Execution Queue",
    ]
    for item in handoff.get("publishingQueue", []):
        lines.append(f"- {item.get('channel', '')}: {item.get('title', '')} - {item.get('action', '')}")
    lines.extend(["", "## Required Evidence"])
    lines.extend(f"- {item}" for item in handoff.get("requiredEvidence", []))
    lines.extend(["", "## Checklists"])
    for checklist in handoff.get("executionChecklists", []):
        lines.append(f"### {checklist.get('channel', '')}")
        lines.extend(f"- {item}" for item in checklist.get("items", []))
        lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    strategy = subparsers.add_parser("create-strategy", help="Create a marketing strategy project and state file.")
    strategy.add_argument("--brand", required=True, help="Brand or company name.")
    strategy.add_argument("--business", required=True, help="What the business sells or does.")
    strategy.add_argument("--audience", required=True, help="Ideal customer profile or target audience.")
    strategy.add_argument("--goal", default="Generate qualified leads", help="Primary marketing goal.")
    strategy.add_argument("--offer", default="Core product or service", help="Primary offer to promote.")
    strategy.add_argument("--tone", default="professional", help="Brand voice or tone.")
    strategy.add_argument("--region", default="global", help="Target region or market.")
    strategy.add_argument("--output-dir", default="generated-marketing", help="Directory where the marketing project is created.")
    strategy.add_argument("--force", action="store_true", help="Update files if the output project already exists.")
    strategy.set_defaults(func=create_strategy)

    campaign = subparsers.add_parser("create-campaign", help="Create a campaign plan from marketing strategy state.")
    campaign.add_argument("--project-dir", default=".", help="Marketing project directory.")
    campaign.add_argument("--name", required=True, help="Campaign name.")
    campaign.add_argument("--objective", required=True, help="Campaign objective.")
    campaign.add_argument("--audience", default="", help="Campaign audience override.")
    campaign.add_argument("--offer", default="", help="Campaign offer override.")
    campaign.add_argument("--channels", default="", help="Comma-separated channel list.")
    campaign.add_argument("--duration", default="4 weeks", help="Campaign duration.")
    campaign.add_argument("--cta", default="Book a consultation", help="Campaign call to action.")
    campaign.set_defaults(func=create_campaign)

    content_plan = subparsers.add_parser("generate-content-plan", help="Generate a weekly content calendar from a campaign.")
    content_plan.add_argument("--project-dir", default=".", help="Marketing project directory.")
    content_plan.add_argument("--campaign", default="", help="Campaign slug. Defaults to latest campaign.")
    content_plan.add_argument("--weeks", type=int, default=4, help="Number of weeks to plan.")
    content_plan.add_argument("--cadence", type=int, default=3, help="Content items per week.")
    content_plan.add_argument("--channels", default="", help="Comma-separated channel override.")
    content_plan.set_defaults(func=generate_content_plan)

    posts = subparsers.add_parser("generate-posts", help="Generate platform-specific draft content from a campaign.")
    posts.add_argument("--project-dir", default=".", help="Marketing project directory.")
    posts.add_argument("--campaign", default="", help="Campaign slug. Defaults to latest campaign.")
    posts.add_argument("--channels", default="", help="Comma-separated channels, such as LinkedIn,X,SEO blog,Email.")
    posts.add_argument("--count", type=int, default=1, help="Drafts per channel.")
    posts.add_argument("--theme", default="", help="Optional content theme override.")
    posts.add_argument("--stage", choices=("awareness", "consideration", "conversion", ""), default="", help="Funnel stage override.")
    posts.set_defaults(func=generate_posts)

    seo = subparsers.add_parser("generate-seo-plan", help="Generate SEO/GEO keyword, page, schema, and internal-link plan.")
    seo.add_argument("--project-dir", default=".", help="Marketing project directory.")
    seo.add_argument("--campaign", default="", help="Campaign slug. Defaults to latest campaign when available.")
    seo.add_argument("--focus", default="", help="SEO focus or product category override.")
    seo.add_argument("--pages", type=int, default=6, help="Number of SEO pages to plan.")
    seo.add_argument("--region", default="", help="Target region override.")
    seo.set_defaults(func=generate_seo_plan)

    briefs = subparsers.add_parser("generate-blog-briefs", help="Generate SEO/GEO blog briefs from the latest SEO plan.")
    briefs.add_argument("--project-dir", default=".", help="Marketing project directory.")
    briefs.add_argument("--count", type=int, default=4, help="Number of blog briefs to create.")
    briefs.add_argument(
        "--intent",
        choices=("informational", "commercial", "comparison", "problem-aware", ""),
        default="",
        help="Search intent override.",
    )
    briefs.set_defaults(func=generate_blog_briefs)

    signals = subparsers.add_parser("define-lead-signals", help="Define reviewable lead detection signals from strategy.")
    signals.add_argument("--project-dir", default=".", help="Marketing project directory.")
    signals.add_argument("--signals", default="", help="Comma-separated custom positive lead signals.")
    signals.add_argument("--channels", default="", help="Comma-separated channels to monitor.")
    signals.add_argument("--negative-signals", default="", help="Comma-separated disqualifying or low-intent signals.")
    signals.set_defaults(func=define_lead_signals)

    lead = subparsers.add_parser("score-lead", help="Score one lead text snippet against lead signals.")
    lead.add_argument("--project-dir", default=".", help="Marketing project directory.")
    lead.add_argument("--name", required=True, help="Lead name or handle.")
    lead.add_argument("--company", default="", help="Lead company.")
    lead.add_argument("--source", default="", help="Where the lead was found.")
    lead.add_argument("--text", required=True, help="Lead text, post, comment, form message, or note to score.")
    lead.add_argument("--url", default="", help="Source URL.")
    lead.add_argument("--role", default="", help="Lead role or title.")
    lead.add_argument("--channel", default="", help="Source channel.")
    lead.set_defaults(func=score_lead)

    outreach = subparsers.add_parser("draft-outreach", help="Draft review-only outreach for a scored lead.")
    outreach.add_argument("--project-dir", default=".", help="Marketing project directory.")
    outreach.add_argument("--lead-id", default="", help="Lead scorecard ID. Defaults to latest scored lead.")
    outreach.add_argument("--channel", choices=("email", "linkedin", "x", "phone", "crm-note"), default="email", help="Outreach channel.")
    outreach.add_argument("--tone", default="", help="Tone override.")
    outreach.add_argument("--cta", default="", help="CTA override.")
    outreach.set_defaults(func=draft_outreach)

    crm = subparsers.add_parser("crm-export", help="Export scored leads and outreach metadata for CRM review/import.")
    crm.add_argument("--project-dir", default=".", help="Marketing project directory.")
    crm.add_argument("--format", choices=("json", "csv"), default="json", help="Export format.")
    crm.add_argument("--owner", default="", help="Optional lead owner.")
    crm.set_defaults(func=crm_export)

    performance = subparsers.add_parser("record-performance", help="Record campaign/channel metrics and generate optimization recommendations.")
    performance.add_argument("--project-dir", default=".", help="Marketing project directory.")
    performance.add_argument("--campaign", default="", help="Campaign slug. Defaults to latest campaign.")
    performance.add_argument("--channel", default="all channels", help="Channel for this metric snapshot.")
    performance.add_argument("--period", default="latest period", help="Reporting period, such as 2026-W20.")
    performance.add_argument(
        "--metrics",
        default="",
        help="Comma-separated key=value metrics: impressions,engagements,clicks,leads,conversions,spend,revenue.",
    )
    performance.add_argument("--notes", default="", help="Optional performance notes.")
    performance.set_defaults(func=record_performance)

    dashboard = subparsers.add_parser("generate-review-dashboard", help="Generate a manager review dashboard from marketing project state.")
    dashboard.add_argument("--project-dir", default=".", help="Marketing project directory.")
    dashboard.add_argument("--focus", default="weekly marketing review", help="Dashboard focus.")
    dashboard.add_argument("--period", default="latest period", help="Reporting period.")
    dashboard.set_defaults(func=generate_review_dashboard)

    competitor = subparsers.add_parser("add-competitor", help="Add or update a competitor profile for market intelligence.")
    competitor.add_argument("--project-dir", default=".", help="Marketing project directory.")
    competitor.add_argument("--name", required=True, help="Competitor name.")
    competitor.add_argument("--url", default="", help="Competitor website or profile URL.")
    competitor.add_argument("--category", default="direct competitor", help="Competitor category.")
    competitor.add_argument("--positioning", default="", help="Observed competitor positioning.")
    competitor.add_argument("--strengths", default="", help="Comma-separated competitor strengths.")
    competitor.add_argument("--weaknesses", default="", help="Comma-separated competitor weaknesses.")
    competitor.add_argument("--channels", default="", help="Comma-separated competitor channels.")
    competitor.set_defaults(func=add_competitor)

    observation = subparsers.add_parser("track-competitor", help="Record one competitor move or market observation.")
    observation.add_argument("--project-dir", default=".", help="Marketing project directory.")
    observation.add_argument("--competitor", default="", help="Competitor ID or name. Defaults to latest competitor.")
    observation.add_argument("--event-type", default="market move", help="Observation type, such as launch, pricing, content, partnership.")
    observation.add_argument("--channel", default="", help="Where the move was observed.")
    observation.add_argument("--summary", required=True, help="Observation summary.")
    observation.add_argument("--url", default="", help="Source URL.")
    observation.add_argument("--impact", choices=("low", "medium", "high"), default="medium", help="Estimated competitive impact.")
    observation.add_argument("--tags", default="", help="Comma-separated tags.")
    observation.set_defaults(func=track_competitor)

    report = subparsers.add_parser("competitor-report", help="Generate positioning gaps, trends, and response campaign recommendations.")
    report.add_argument("--project-dir", default=".", help="Marketing project directory.")
    report.add_argument("--focus", default="competitive intelligence", help="Report focus.")
    report.add_argument("--period", default="latest period", help="Reporting period.")
    report.set_defaults(func=competitor_report)

    approval = subparsers.add_parser("create-approval-package", help="Create a review package and publishing queue for approved execution.")
    approval.add_argument("--project-dir", default=".", help="Marketing project directory.")
    approval.add_argument("--channels", default="", help="Comma-separated channels to include.")
    approval.add_argument("--owner", default="", help="Owner responsible for approval.")
    approval.add_argument("--due", default="", help="Approval due date or time window.")
    approval.add_argument("--scope", default="campaign execution", help="Execution scope.")
    approval.set_defaults(func=create_approval_package)

    approval_decision = subparsers.add_parser("record-approval", help="Record an approval decision in the local change log.")
    approval_decision.add_argument("--project-dir", default=".", help="Marketing project directory.")
    approval_decision.add_argument("--package-id", default="", help="Approval package ID. Defaults to latest package.")
    approval_decision.add_argument("--decision", choices=("approved", "changes_requested", "rejected"), required=True, help="Approval decision.")
    approval_decision.add_argument("--approver", default="", help="Approver name.")
    approval_decision.add_argument("--notes", default="", help="Approval notes or required changes.")
    approval_decision.set_defaults(func=record_approval)

    handoff = subparsers.add_parser("operator-handoff", help="Generate a human operator handoff package for execution.")
    handoff.add_argument("--project-dir", default=".", help="Marketing project directory.")
    handoff.add_argument("--package-id", default="", help="Approval package ID. Defaults to latest package.")
    handoff.add_argument("--operator", default="", help="Human operator name or team.")
    handoff.set_defaults(func=operator_handoff)

    summary = subparsers.add_parser("summary", help="Return a Discord-friendly marketing project status summary.")
    summary.add_argument("--project-dir", default=".", help="Marketing project directory.")
    summary.set_defaults(func=status_summary)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = args.func(args)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
