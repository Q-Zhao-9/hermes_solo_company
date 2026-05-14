#!/usr/bin/env python3
"""Deterministic helpers for Hermes marketing and SEO agency workflows.

Phase 1 focuses on strategy and campaign memory. It avoids network access and
does not publish, message, email, or modify external systems.
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
        return {"version": 1, "strategies": [], "campaigns": []}
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"version": 1, "strategies": [], "campaigns": []}
    if not isinstance(data, dict):
        return {"version": 1, "strategies": [], "campaigns": []}
    data.setdefault("version", 1)
    data.setdefault("strategies", [])
    data.setdefault("campaigns", [])
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
