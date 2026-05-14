#!/usr/bin/env python3
"""Deterministic helpers for Hermes marketing and SEO agency workflows.

Phase 1 focuses on strategy and campaign memory. Phase 2 adds content planning
and draft generation. It avoids network access and does not publish, message,
email, or modify external systems.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
from pathlib import Path
from typing import Any


STATE_PATH = Path("docs") / "hermes-marketing-state.json"
CONTENT_DIR = Path("docs") / "content"


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
        return {"version": 1, "strategies": [], "campaigns": [], "contentPlans": [], "contentDrafts": []}
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"version": 1, "strategies": [], "campaigns": [], "contentPlans": [], "contentDrafts": []}
    if not isinstance(data, dict):
        return {"version": 1, "strategies": [], "campaigns": [], "contentPlans": [], "contentDrafts": []}
    data.setdefault("version", 1)
    data.setdefault("strategies", [])
    data.setdefault("campaigns", [])
    data.setdefault("contentPlans", [])
    data.setdefault("contentDrafts", [])
    return data


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


def select_campaign(state: dict[str, Any], campaign_slug: str) -> dict[str, Any]:
    if campaign_slug:
        for campaign in state.get("campaigns", []):
            if isinstance(campaign, dict) and campaign.get("slug") == campaign_slug:
                return campaign
        return {}
    campaign = state.get("lastCampaign", {})
    return campaign if isinstance(campaign, dict) else {}


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
    lines.append("")
    lines.append("Next: create a campaign, generate content plan, or prepare SEO/GEO tasks.")
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
