#!/usr/bin/env python3
"""Deterministic helpers for Hermes website agency workflows.

This script gives the website-builder skills a reliable execution layer for
the first MVP platforms: static HTML and Next.js. It avoids network access and
does not install dependencies.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_PORT = 3010
STATE_PATH = Path("docs") / "hermes-website-state.json"
DEPLOY_DIR = Path("dist") / "hermes-deploy"
WORDPRESS_DIR = Path("dist") / "hermes-wordpress"
MEDIA_DIR = Path("assets") / "images"


@dataclass(frozen=True)
class SiteSpec:
    name: str
    description: str
    audience: str
    goal: str
    tone: str
    platform: str
    template: str
    slug: str


@dataclass(frozen=True)
class PageSpec:
    title: str
    slug: str
    page_type: str
    goal: str
    description: str


def slugify(value: str, fallback: str = "website") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    return slug[:64].strip("-") or fallback


def choose_platform(requested: str, description: str) -> str:
    if requested != "auto":
        return requested
    lowered = description.lower()
    nextjs_markers = (
        "saas",
        "dashboard",
        "portal",
        "login",
        "auth",
        "database",
        "api",
        "app",
        "stripe",
        "subscription",
    )
    if any(marker in lowered for marker in nextjs_markers):
        return "nextjs"
    return "static"


def choose_template(requested: str, description: str) -> str:
    if requested != "auto":
        return requested
    lowered = description.lower()
    markers = {
        "restaurant": ("restaurant", "cafe", "coffee", "bakery", "bar", "menu", "dining", "food"),
        "saas": ("saas", "software", "dashboard", "platform", "portal", "login", "subscription", "api"),
        "portfolio": ("portfolio", "designer", "photographer", "artist", "resume", "creative work"),
        "ecommerce": ("ecommerce", "e-commerce", "shop", "store", "product", "collection", "retail"),
        "consultant": ("consultant", "consulting", "advisor", "agency", "studio", "strategy", "service firm"),
        "local-service": ("dentist", "clinic", "plumber", "roofer", "salon", "cleaning", "law firm", "local"),
    }
    for template, words in markers.items():
        if any(word in lowered for word in words):
            return template
    return "local-service"


def template_profile(spec: SiteSpec) -> dict[str, Any]:
    profiles: dict[str, dict[str, Any]] = {
        "local-service": {
            "eyebrow": "Local service website",
            "hero": f"{spec.name} makes it easier for {spec.audience} to get trusted help.",
            "proof": ["Fast response", "Clear pricing", "Trusted local team"],
            "section_eyebrow": "Services",
            "section_heading": "Practical help, delivered with care",
            "cards": [
                ("Service clarity", "Explain what customers can book, request, or compare before they call."),
                ("Trust signals", "Show proof, reviews, credentials, and local expertise where decisions happen."),
                ("Lead capture", "Make the next step obvious with phone, form, and appointment CTAs."),
            ],
            "process": ["Request a quote or appointment.", "Confirm the service details.", "Get clear follow-through."],
            "final_heading": "Ready to get started?",
        },
        "restaurant": {
            "eyebrow": "Restaurant website",
            "hero": f"{spec.name} brings memorable dining moments to {spec.audience}.",
            "proof": ["Seasonal menu", "Easy reservations", "Private events"],
            "section_eyebrow": "Menu highlights",
            "section_heading": "Designed to turn hungry visitors into guests",
            "cards": [
                ("Signature dishes", "Feature the dishes, drinks, and specials that define the experience."),
                ("Reservations", "Keep booking, hours, location, and contact details easy to find."),
                ("Events", "Promote catering, private dining, and group occasions with clear next steps."),
            ],
            "process": ["Explore the menu.", "Reserve a table or order.", "Visit and enjoy the experience."],
            "final_heading": "Plan your next visit",
        },
        "saas": {
            "eyebrow": "SaaS website",
            "hero": f"{spec.name} helps {spec.audience} turn daily work into measurable progress.",
            "proof": ["Product clarity", "Workflow automation", "Scalable platform"],
            "section_eyebrow": "Product value",
            "section_heading": "Built for teams that need traction, not noise",
            "cards": [
                ("Use case focus", "Show the strongest workflow and the business result it creates."),
                ("Product confidence", "Explain security, integrations, onboarding, and support expectations."),
                ("Conversion path", "Guide visitors toward demos, trials, pricing, or sales conversations."),
            ],
            "process": ["Map the workflow.", "Launch the workspace.", "Measure and improve results."],
            "final_heading": "Ready to see the product?",
        },
        "consultant": {
            "eyebrow": "Consulting website",
            "hero": f"{spec.name} gives {spec.audience} sharper strategy and cleaner execution.",
            "proof": ["Senior guidance", "Focused roadmap", "Execution support"],
            "section_eyebrow": "Advisory services",
            "section_heading": "A clear path from insight to implementation",
            "cards": [
                ("Strategy", "Clarify positioning, opportunities, and the decisions that need momentum."),
                ("Systems", "Turn recommendations into repeatable processes, content, and operating rhythm."),
                ("Partnership", "Support implementation with practical guidance and measurable next steps."),
            ],
            "process": ["Diagnose the current state.", "Prioritize the roadmap.", "Execute and refine."],
            "final_heading": "Start the conversation",
        },
        "ecommerce": {
            "eyebrow": "Ecommerce concept",
            "hero": f"{spec.name} helps {spec.audience} discover products with confidence.",
            "proof": ["Curated products", "Clear benefits", "Smooth purchase path"],
            "section_eyebrow": "Shop experience",
            "section_heading": "Built to support discovery, trust, and conversion",
            "cards": [
                ("Product story", "Highlight hero products, benefits, materials, and customer outcomes."),
                ("Collection flow", "Organize categories, recommendations, and bundles for easier browsing."),
                ("Purchase confidence", "Clarify shipping, returns, reviews, and support before checkout."),
            ],
            "process": ["Browse the collection.", "Compare the right fit.", "Buy with confidence."],
            "final_heading": "Explore the collection",
        },
        "portfolio": {
            "eyebrow": "Portfolio website",
            "hero": f"{spec.name} presents the work, story, and proof {spec.audience} need to take action.",
            "proof": ["Selected work", "Clear story", "Contact-ready"],
            "section_eyebrow": "Featured work",
            "section_heading": "A portfolio structured for credibility and inquiry",
            "cards": [
                ("Case studies", "Show the problem, process, craft, and outcome behind important work."),
                ("Point of view", "Make the creator's style, values, and strengths easy to understand."),
                ("Inquiry path", "Give clients, recruiters, or collaborators a simple way to start."),
            ],
            "process": ["Review selected work.", "Understand the approach.", "Start a collaboration."],
            "final_heading": "Let us build something",
        },
    }
    return profiles.get(spec.template, profiles["local-service"])


def build_spec(args: argparse.Namespace) -> SiteSpec:
    name = args.name.strip()
    description = args.description.strip()
    platform = choose_platform(args.platform, description)
    template = choose_template(args.template, description)
    return SiteSpec(
        name=name,
        description=description,
        audience=args.audience.strip(),
        goal=args.goal.strip(),
        tone=args.tone.strip(),
        platform=platform,
        template=template,
        slug=slugify(name),
    )


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def create_site(args: argparse.Namespace) -> dict[str, Any]:
    spec = build_spec(args)
    root = Path(args.output_dir).expanduser().resolve() / spec.slug
    if root.exists() and not args.force:
        return {
            "ok": False,
            "error": f"output already exists: {root}",
            "hint": "Pass --force to update generated files in this project.",
        }

    root.mkdir(parents=True, exist_ok=True)
    write_project_docs(root, spec)
    if spec.platform == "nextjs":
        write_nextjs_project(root, spec)
    else:
        write_static_project(root, spec)
    pages = parse_page_specs(args.pages, spec)
    if len(pages) > 1:
        write_site_pages(root, spec, pages)

    record_project_created(root, spec, pages)
    preview = preview_plan(root, port=args.port)
    return {
        "ok": True,
        "projectDir": str(root),
        "platform": spec.platform,
        "template": spec.template,
        "slug": spec.slug,
        "files": sorted(str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()),
        "preview": preview,
        "nextSteps": [
            f"cd {root}",
            preview["command"],
            "Use the preview URL to review the first draft.",
        ],
    }


def parse_page_specs(value: str, spec: SiteSpec) -> list[PageSpec]:
    requested = [item.strip() for item in (value or "home").split(",") if item.strip()]
    if not requested:
        requested = ["home"]
    pages: list[PageSpec] = []
    seen: set[str] = set()
    for raw in requested:
        page_type = slugify(raw, fallback="page")
        if page_type in seen:
            continue
        seen.add(page_type)
        pages.append(default_page_spec(page_type, spec))
    if not any(page.slug == "home" for page in pages):
        pages.insert(0, default_page_spec("home", spec))
    return pages


def default_page_spec(page_type: str, spec: SiteSpec) -> PageSpec:
    normalized = slugify(page_type, fallback="page")
    titles = {
        "home": "Home",
        "about": "About",
        "services": "Services",
        "service": "Services",
        "contact": "Contact",
        "faq": "FAQ",
        "pricing": "Pricing",
        "blog": "Blog",
        "products": "Products",
        "product": "Products",
    }
    goals = {
        "home": spec.goal,
        "about": "Build trust with the team and story",
        "services": "Help visitors choose the right service",
        "service": "Help visitors choose the right service",
        "contact": "Make it easy to start a conversation",
        "faq": "Answer common buying questions",
        "pricing": "Help visitors understand package fit",
        "blog": "Educate visitors and support search intent",
        "products": "Help visitors compare products",
        "product": "Help visitors compare products",
    }
    descriptions = {
        "home": spec.description,
        "about": f"{spec.name} explains its mission, proof, and approach for {spec.audience}.",
        "services": f"{spec.name} presents clear service options for {spec.audience}.",
        "service": f"{spec.name} presents clear service options for {spec.audience}.",
        "contact": f"{spec.name} gives {spec.audience} a direct path to {spec.goal}.",
        "faq": f"{spec.name} answers the questions {spec.audience} ask before taking action.",
        "pricing": f"{spec.name} explains packages, value, and next steps for {spec.audience}.",
        "blog": f"{spec.name} shares practical guidance for {spec.audience}.",
        "products": f"{spec.name} organizes product choices for {spec.audience}.",
        "product": f"{spec.name} organizes product choices for {spec.audience}.",
    }
    title = titles.get(normalized, normalized.replace("-", " ").title())
    return PageSpec(
        title=title,
        slug="home" if normalized == "home" else normalized,
        page_type=normalized,
        goal=goals.get(normalized, spec.goal),
        description=descriptions.get(normalized, f"{spec.name} {title.lower()} page for {spec.audience}."),
    )


def write_project_docs(root: Path, spec: SiteSpec) -> None:
    profile = template_profile(spec)
    write_text(
        root / "docs" / "website-brief.md",
        f"""# Website Brief: {spec.name}

## Business
{spec.description}

## Target Audience
{spec.audience}

## Primary Goal
{spec.goal}

## Brand Tone
{spec.tone}

## Platform
{spec.platform}

## Template
{spec.template}

## Assumptions
- Build a polished first draft suitable for preview.
- Keep navigation simple and conversion-focused.
- Use accessible colors, semantic headings, and responsive layout.
""",
    )
    write_text(
        root / "docs" / "sitemap.md",
        f"""# Sitemap

- Home: positioning, proof, services, process, FAQ, CTA
- About: company credibility and differentiators
- Contact: lead capture path

For the MVP, the Home page is implemented first.
""",
    )
    write_text(
        root / "docs" / "design-system.md",
        f"""# Design System

## Direction
Tone: {spec.tone}

## Core Rules
- Use a clean, professional layout with strong section hierarchy.
- Keep buttons high-contrast and action-oriented.
- Use readable type sizes and generous mobile spacing.
- Avoid decorative clutter that distracts from the conversion goal.

## Palette
- Ink: #18212f
- Surface: #f8fafc
- Accent: #0f766e
- Accent dark: #134e4a
- Border: #d9e2ec
""",
    )
    write_text(
        root / "docs" / "content-plan.md",
        f"""# Content Plan

## Homepage Message
{spec.name} helps {spec.audience} achieve: {spec.goal}.

## Required Sections
- Hero with clear promise and CTA
- Trust/proof strip
- Services or capabilities
- Process
- FAQ
- Final CTA
""",
    )
    write_text(
        root / "docs" / "qa-report.md",
        """# QA Report

Status: generated, not yet manually reviewed.

## Before Publishing
- Run the preview command.
- Check desktop and mobile layout.
- Confirm CTA destination and contact method.
- Review title, meta description, headings, and alt text.
""",
    )


def write_static_project(root: Path, spec: SiteSpec) -> None:
    profile = template_profile(spec)
    cards = profile["cards"]
    proof = profile["proof"]
    process = profile["process"]
    write_text(
        root / "index.html",
        f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape_html(spec.name)} | Professional Website</title>
    <meta name="description" content="{escape_html(spec.description[:150])}" />
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <header class="site-header">
      <a class="brand" href="#top">{escape_html(spec.name)}</a>
      <nav aria-label="Primary navigation">
        <a href="#services">Services</a>
        <a href="#process">Process</a>
        <a href="#contact">Contact</a>
      </nav>
    </header>

    <main id="top">
      <section class="hero">
        <div>
          <p class="eyebrow">{escape_html(profile["eyebrow"])}</p>
          <h1>{escape_html(profile["hero"])}</h1>
          <p>{escape_html(spec.description)}</p>
          <a class="button" href="#contact">{escape_html(spec.goal)}</a>
        </div>
      </section>

      <section class="proof" aria-label="Key strengths">
        <span>{escape_html(proof[0])}</span>
        <span>{escape_html(proof[1])}</span>
        <span>{escape_html(proof[2])}</span>
      </section>

      <section id="services" class="section">
        <p class="eyebrow">{escape_html(profile["section_eyebrow"])}</p>
        <h2>{escape_html(profile["section_heading"])}</h2>
        <div class="grid">
          <article>
            <h3>{escape_html(cards[0][0])}</h3>
            <p>{escape_html(cards[0][1])}</p>
          </article>
          <article>
            <h3>{escape_html(cards[1][0])}</h3>
            <p>{escape_html(cards[1][1])}</p>
          </article>
          <article>
            <h3>{escape_html(cards[2][0])}</h3>
            <p>{escape_html(cards[2][1])}</p>
          </article>
        </div>
      </section>

      <section id="process" class="section band">
        <p class="eyebrow">Process</p>
        <h2>A simple path from idea to preview</h2>
        <ol>
          <li>{escape_html(process[0])}</li>
          <li>{escape_html(process[1])}</li>
          <li>{escape_html(process[2])}</li>
        </ol>
      </section>

      <section id="contact" class="section cta">
        <p class="eyebrow">Next step</p>
        <h2>{escape_html(profile["final_heading"])}</h2>
        <p>Use this draft as the starting point for edits, preview, and deployment.</p>
        <a class="button" href="mailto:hello@example.com">Contact us</a>
      </section>
    </main>
  </body>
</html>
""",
    )
    write_text(
        root / "styles.css",
        """* {
  box-sizing: border-box;
}

body {
  margin: 0;
  color: #18212f;
  background: #f8fafc;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.55;
}

a {
  color: inherit;
}

.site-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 20px clamp(20px, 5vw, 64px);
  background: rgba(248, 250, 252, 0.94);
  border-bottom: 1px solid #d9e2ec;
  position: sticky;
  top: 0;
}

.brand {
  font-weight: 800;
  text-decoration: none;
}

nav {
  display: flex;
  gap: 18px;
  font-size: 0.95rem;
}

nav a {
  text-decoration: none;
}

.hero,
.section {
  padding: clamp(56px, 9vw, 104px) clamp(20px, 5vw, 64px);
}

.hero {
  min-height: 68vh;
  display: grid;
  align-items: center;
  background:
    linear-gradient(135deg, rgba(15, 118, 110, 0.12), rgba(24, 33, 47, 0.02)),
    #ffffff;
}

.hero > div,
.section {
  max-width: 1120px;
  margin: 0 auto;
}

.eyebrow {
  color: #0f766e;
  font-size: 0.82rem;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

h1,
h2,
h3,
p {
  margin-top: 0;
}

h1 {
  max-width: 820px;
  font-size: clamp(2.4rem, 6vw, 5rem);
  line-height: 1.02;
  margin-bottom: 24px;
}

h2 {
  font-size: clamp(2rem, 4vw, 3.4rem);
  line-height: 1.08;
}

.hero p {
  max-width: 720px;
  font-size: 1.18rem;
}

.button {
  display: inline-flex;
  align-items: center;
  min-height: 48px;
  padding: 0 20px;
  margin-top: 12px;
  color: #ffffff;
  background: #0f766e;
  border-radius: 6px;
  font-weight: 800;
  text-decoration: none;
}

.proof {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border-block: 1px solid #d9e2ec;
  background: #ffffff;
}

.proof span {
  padding: 22px;
  text-align: center;
  font-weight: 800;
}

.proof {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border-block: 1px solid #d9e2ec;
  background: #ffffff;
}

.proof span {
  padding: 22px;
  text-align: center;
  font-weight: 800;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
  margin-top: 28px;
}

article {
  padding: 24px;
  background: #ffffff;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
}

.band {
  background: #e6f3f1;
  max-width: none;
}

.band > * {
  max-width: 1120px;
  margin-left: auto;
  margin-right: auto;
}

ol {
  max-width: 760px;
  padding-left: 24px;
}

.cta {
  text-align: center;
}

@media (max-width: 720px) {
  .site-header,
  nav {
    align-items: flex-start;
    flex-direction: column;
  }

  .proof,
  .grid {
    grid-template-columns: 1fr;
  }
}
""",
    )


def write_site_pages(root: Path, spec: SiteSpec, pages: list[PageSpec]) -> None:
    if detect_platform(root) == "nextjs":
        write_nextjs_pages(root, spec, pages)
        return
    write_static_pages(root, spec, pages)


def write_static_pages(root: Path, spec: SiteSpec, pages: list[PageSpec]) -> None:
    for page in pages:
        path = static_page_path(root, page)
        write_text(path, render_static_page(spec, page, pages))
    write_text(root / "docs" / "sitemap.md", render_sitemap(pages))


def static_page_path(root: Path, page: PageSpec) -> Path:
    return root / "index.html" if page.slug == "home" else root / f"{page.slug}.html"


def render_static_page(spec: SiteSpec, page: PageSpec, pages: list[PageSpec]) -> str:
    profile = template_profile(spec)
    nav = "\n        ".join(
        f'<a href="{escape_html(page_href(item))}">{escape_html(item.title)}</a>' for item in pages[:6]
    )
    page_body = page_sections(spec, page, profile, pages)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape_html(page.title)} | {escape_html(spec.name)}</title>
    <meta name="description" content="{escape_html(page.description[:150])}" />
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <header class="site-header">
      <a class="brand" href="index.html">{escape_html(spec.name)}</a>
      <nav aria-label="Primary navigation">
        {nav}
      </nav>
    </header>

    <main id="top">
{page_body}
    </main>
  </body>
</html>
"""


def page_href(page: PageSpec) -> str:
    return "index.html" if page.slug == "home" else f"{page.slug}.html"


def page_sections(spec: SiteSpec, page: PageSpec, profile: dict[str, Any], pages: list[PageSpec]) -> str:
    if page.slug == "home":
        cards = profile["cards"]
        proof = profile["proof"]
        process = profile["process"]
        return f"""      <section class="hero">
        <div>
          <p class="eyebrow">{escape_html(profile["eyebrow"])}</p>
          <h1>{escape_html(profile["hero"])}</h1>
          <p>{escape_html(spec.description)}</p>
          <a class="button" href="{escape_html(contact_href(pages))}">{escape_html(spec.goal)}</a>
        </div>
      </section>

      <section class="proof" aria-label="Key strengths">
        <span>{escape_html(proof[0])}</span>
        <span>{escape_html(proof[1])}</span>
        <span>{escape_html(proof[2])}</span>
      </section>

      <section id="services" class="section">
        <p class="eyebrow">{escape_html(profile["section_eyebrow"])}</p>
        <h2>{escape_html(profile["section_heading"])}</h2>
        <div class="grid">
          <article><h3>{escape_html(cards[0][0])}</h3><p>{escape_html(cards[0][1])}</p></article>
          <article><h3>{escape_html(cards[1][0])}</h3><p>{escape_html(cards[1][1])}</p></article>
          <article><h3>{escape_html(cards[2][0])}</h3><p>{escape_html(cards[2][1])}</p></article>
        </div>
      </section>

      <section id="process" class="section band">
        <p class="eyebrow">Process</p>
        <h2>A simple path from idea to preview</h2>
        <ol>
          <li>{escape_html(process[0])}</li>
          <li>{escape_html(process[1])}</li>
          <li>{escape_html(process[2])}</li>
        </ol>
      </section>

      <section id="contact" class="section cta">
        <p class="eyebrow">Next step</p>
        <h2>{escape_html(profile["final_heading"])}</h2>
        <p>Use this draft as the starting point for edits, preview, and deployment.</p>
        <a class="button" href="mailto:hello@example.com">Contact us</a>
      </section>"""

    cards = page_cards(page)
    return f"""      <section class="hero page-hero">
        <div>
          <p class="eyebrow">{escape_html(page.title)}</p>
          <h1>{escape_html(page_heading(spec, page))}</h1>
          <p>{escape_html(page.description)}</p>
        <a class="button" href="{escape_html(contact_href(pages))}">{escape_html(page.goal)}</a>
        </div>
      </section>

      <section class="section">
        <p class="eyebrow">What to know</p>
        <h2>{escape_html(page_subheading(page))}</h2>
        <div class="grid">
          <article><h3>{escape_html(cards[0][0])}</h3><p>{escape_html(cards[0][1])}</p></article>
          <article><h3>{escape_html(cards[1][0])}</h3><p>{escape_html(cards[1][1])}</p></article>
          <article><h3>{escape_html(cards[2][0])}</h3><p>{escape_html(cards[2][1])}</p></article>
        </div>
      </section>

      <section class="section cta">
        <p class="eyebrow">Next step</p>
        <h2>{escape_html(page.goal)}</h2>
        <p>Use this page as a structured first draft for review, edits, and approval.</p>
        <a class="button" href="mailto:hello@example.com">Contact us</a>
      </section>"""


def contact_href(pages: list[PageSpec]) -> str:
    return "contact.html" if any(page.slug == "contact" for page in pages) else "mailto:hello@example.com"


def page_heading(spec: SiteSpec, page: PageSpec) -> str:
    if page.page_type == "about":
        return f"About {spec.name}"
    if page.page_type in {"services", "service"}:
        return f"Services for {spec.audience}"
    if page.page_type == "contact":
        return f"Contact {spec.name}"
    if page.page_type == "faq":
        return "Questions, answered clearly"
    return f"{page.title} for {spec.audience}"


def page_subheading(page: PageSpec) -> str:
    mapping = {
        "about": "A clearer story, proof, and reason to choose the team",
        "services": "Organized options with practical next steps",
        "service": "Organized options with practical next steps",
        "contact": "Simple ways to reach the team",
        "faq": "Answers that reduce friction before conversion",
        "pricing": "Packages, value, and fit",
        "blog": "Useful ideas and search-friendly topics",
    }
    return mapping.get(page.page_type, "Focused content for this page")


def page_cards(page: PageSpec) -> list[tuple[str, str]]:
    mapping = {
        "about": [
            ("Positioning", "Explain who the business serves and why the work matters."),
            ("Proof", "Show credentials, outcomes, experience, and local trust signals."),
            ("Approach", "Describe how the team works with customers from first contact to follow-through."),
        ],
        "services": [
            ("Core service", "Describe the primary offer and the problem it solves."),
            ("Service fit", "Clarify who this is for and what outcomes they can expect."),
            ("Next action", "Make the consultation, quote, booking, or purchase path obvious."),
        ],
        "contact": [
            ("Fast response", "Set expectations for replies, scheduling, and intake details."),
            ("Useful details", "Ask for the information needed to route the request well."),
            ("Clear handoff", "Confirm what happens after the visitor reaches out."),
        ],
        "faq": [
            ("Buying questions", "Answer cost, timing, process, and fit questions plainly."),
            ("Trust questions", "Address proof, guarantees, credentials, and support."),
            ("Next questions", "Invite visitors to ask what was not covered."),
        ],
    }
    return mapping.get(page.page_type, mapping["services"])


def render_sitemap(pages: list[PageSpec]) -> str:
    lines = ["# Sitemap", ""]
    for page in pages:
        lines.append(f"- {page.title}: {page.description}")
    lines.extend(["", "Generated pages are tracked in `docs/hermes-website-state.json`."])
    return "\n".join(lines)


def write_nextjs_pages(root: Path, spec: SiteSpec, pages: list[PageSpec]) -> None:
    for page in pages:
        if page.slug == "home":
            continue
        write_text(root / "app" / page.slug / "page.tsx", render_nextjs_page(spec, page))
    update_nextjs_home_navigation(root, pages)
    write_text(root / "docs" / "sitemap.md", render_sitemap(pages))


def update_nextjs_home_navigation(root: Path, pages: list[PageSpec]) -> None:
    page_path = root / "app" / "page.tsx"
    if not page_path.exists():
        return
    nav = "\n          ".join(
        f'<a href="{"/" if page.slug == "home" else "/" + page.slug}">{escape_js(page.title)}</a>' for page in pages[:6]
    )
    text = page_path.read_text(encoding="utf-8")
    updated = re.sub(
        r'(<nav aria-label="Primary navigation">\n)(.*?)(\n        </nav>)',
        rf"\1          {nav}\3",
        text,
        count=1,
        flags=re.DOTALL,
    )
    page_path.write_text(updated, encoding="utf-8")


def render_nextjs_page(spec: SiteSpec, page: PageSpec) -> str:
    cards = page_cards(page)
    return f"""export default function {page.slug.title().replace("-", "")}Page() {{
  return (
    <main>
      <header className="siteHeader">
        <a className="brand" href="/">{escape_js(spec.name)}</a>
        <nav aria-label="Primary navigation">
          <a href="/">Home</a>
          <a href="/services">Services</a>
          <a href="/about">About</a>
          <a href="/contact">Contact</a>
        </nav>
      </header>
      <section className="hero">
        <p className="eyebrow">{escape_js(page.title)}</p>
        <h1>{escape_js(page_heading(spec, page))}</h1>
        <p>{escape_js(page.description)}</p>
        <a className="button" href="/contact">{escape_js(page.goal)}</a>
      </section>
      <section className="section">
        <p className="eyebrow">What to know</p>
        <h2>{escape_js(page_subheading(page))}</h2>
        <div className="grid">
          <article><h3>{escape_js(cards[0][0])}</h3><p>{escape_js(cards[0][1])}</p></article>
          <article><h3>{escape_js(cards[1][0])}</h3><p>{escape_js(cards[1][1])}</p></article>
          <article><h3>{escape_js(cards[2][0])}</h3><p>{escape_js(cards[2][1])}</p></article>
        </div>
      </section>
    </main>
  );
}}
"""


def write_nextjs_project(root: Path, spec: SiteSpec) -> None:
    profile = template_profile(spec)
    capabilities = json.dumps([card[0] for card in profile["cards"]])
    card_descriptions = json.dumps({card[0]: card[1] for card in profile["cards"]})
    proof = json.dumps(profile["proof"])
    process = profile["process"]
    write_text(
        root / "package.json",
        f"""{{
  "name": "{spec.slug}",
  "version": "0.1.0",
  "private": true,
  "scripts": {{
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }},
  "dependencies": {{
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  }},
  "devDependencies": {{
    "typescript": "^5.0.0",
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0"
  }}
}}
""",
    )
    write_text(
        root / "app" / "layout.tsx",
        f"""import type {{ Metadata }} from "next";
import "./globals.css";

export const metadata: Metadata = {{
  title: "{escape_js(spec.name)}",
  description: "{escape_js(spec.description[:150])}",
}};

export default function RootLayout({{
  children,
}}: Readonly<{{
  children: React.ReactNode;
}}>) {{
  return (
    <html lang="en">
      <body>{{children}}</body>
    </html>
  );
}}
""",
    )
    write_text(
        root / "app" / "page.tsx",
        f"""const capabilities = {capabilities};
const capabilityDescriptions: Record<string, string> = {card_descriptions};
const proof = {proof};

export default function Home() {{
  return (
    <main>
      <header className="siteHeader">
        <a className="brand" href="#top">{escape_js(spec.name)}</a>
        <nav aria-label="Primary navigation">
          <a href="#services">Services</a>
          <a href="#process">Process</a>
          <a href="#contact">Contact</a>
        </nav>
      </header>

      <section id="top" className="hero">
        <p className="eyebrow">{escape_js(profile["eyebrow"])}</p>
        <h1>{escape_js(profile["hero"])}</h1>
        <p>{escape_js(spec.description)}</p>
        <a className="button" href="#contact">{escape_js(spec.goal)}</a>
      </section>

      <section className="proof" aria-label="Key strengths">
        {{proof.map((item) => (
          <span key={{item}}>{{item}}</span>
        ))}}
      </section>

      <section id="services" className="section">
        <p className="eyebrow">{escape_js(profile["section_eyebrow"])}</p>
        <h2>{escape_js(profile["section_heading"])}</h2>
        <div className="grid">
          {{capabilities.map((item) => (
            <article key={{item}}>
              <h3>{{item}}</h3>
              <p>{{capabilityDescriptions[item]}}</p>
            </article>
          ))}}
        </div>
      </section>

      <section id="process" className="section band">
        <p className="eyebrow">Process</p>
        <h2>A simple path from idea to preview</h2>
        <ol>
          <li>{escape_js(process[0])}</li>
          <li>{escape_js(process[1])}</li>
          <li>{escape_js(process[2])}</li>
        </ol>
      </section>

      <section id="contact" className="section cta">
        <p className="eyebrow">Next step</p>
        <h2>{escape_js(profile["final_heading"])}</h2>
        <p>Use this draft as the starting point for edits, preview, and deployment.</p>
        <a className="button" href="mailto:hello@example.com">Contact us</a>
      </section>
    </main>
  );
}}
""",
    )
    write_text(root / "app" / "globals.css", STATIC_CSS_FOR_NEXT)
    write_text(
        root / "tsconfig.json",
        """{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{"name": "next"}]
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
""",
    )
    write_text(root / "next-env.d.ts", "/// <reference types=\"next\" />\n/// <reference types=\"next/image-types/global\" />")


STATIC_CSS_FOR_NEXT = """* {
  box-sizing: border-box;
}

body {
  margin: 0;
  color: #18212f;
  background: #f8fafc;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.55;
}

a {
  color: inherit;
}

.siteHeader {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 20px clamp(20px, 5vw, 64px);
  background: rgba(248, 250, 252, 0.94);
  border-bottom: 1px solid #d9e2ec;
  position: sticky;
  top: 0;
}

.brand {
  font-weight: 800;
  text-decoration: none;
}

nav {
  display: flex;
  gap: 18px;
  font-size: 0.95rem;
}

nav a {
  text-decoration: none;
}

.hero,
.section {
  padding: clamp(56px, 9vw, 104px) clamp(20px, 5vw, 64px);
}

.hero {
  min-height: 68vh;
  background: linear-gradient(135deg, rgba(15, 118, 110, 0.12), rgba(24, 33, 47, 0.02)), #ffffff;
}

.eyebrow {
  color: #0f766e;
  font-size: 0.82rem;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

h1 {
  max-width: 820px;
  font-size: clamp(2.4rem, 6vw, 5rem);
  line-height: 1.02;
}

h2 {
  font-size: clamp(2rem, 4vw, 3.4rem);
  line-height: 1.08;
}

.hero p {
  max-width: 720px;
  font-size: 1.18rem;
}

.button {
  display: inline-flex;
  align-items: center;
  min-height: 48px;
  padding: 0 20px;
  color: #ffffff;
  background: #0f766e;
  border-radius: 6px;
  font-weight: 800;
  text-decoration: none;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

article {
  padding: 24px;
  background: #ffffff;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
}

.band {
  background: #e6f3f1;
}

.cta {
  text-align: center;
}

@media (max-width: 720px) {
  .siteHeader,
  nav {
    align-items: flex-start;
    flex-direction: column;
  }

  .grid {
    grid-template-columns: 1fr;
  }

  .proof {
    grid-template-columns: 1fr;
  }
}
"""


def detect_platform(project_dir: Path) -> str:
    if (project_dir / "package.json").exists():
        package_text = (project_dir / "package.json").read_text(encoding="utf-8", errors="replace")
        if '"next"' in package_text or "'next'" in package_text:
            return "nextjs"
        return "node"
    if (project_dir / "index.html").exists():
        return "static"
    if (project_dir / "app").exists():
        return "nextjs"
    return "unknown"


def preview_plan(project_dir: Path, port: int = DEFAULT_PORT) -> dict[str, Any]:
    project_dir = project_dir.expanduser().resolve()
    platform = detect_platform(project_dir)
    local_url = f"http://127.0.0.1:{port}/"
    lan_url = f"http://0.0.0.0:{port}/"
    if platform == "nextjs":
        command = f"npm run dev -- --hostname 0.0.0.0 --port {port}"
    elif platform == "static":
        command = f"{sys.executable} -m http.server {port} --bind 0.0.0.0"
    elif platform == "node":
        command = f"npm run dev -- --host 0.0.0.0 --port {port}"
    else:
        command = f"{sys.executable} -m http.server {port} --bind 0.0.0.0"

    return {
        "projectDir": str(project_dir),
        "platform": platform,
        "port": port,
        "command": command,
        "localUrl": local_url,
        "windowsWslUrl": local_url,
        "bindUrl": lan_url,
        "proxyHint": f"scripts/start_hermes_proxy_connector.py --target {local_url}",
    }


def build_preview(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    plan = preview_plan(project_dir, port=args.port)
    result: dict[str, Any] = {"ok": True, "preview": plan}
    if args.start:
        process = start_preview_process(project_dir, plan["command"], args.log_file)
        result["process"] = process
    return result


def visual_qa(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    platform = detect_platform(project_dir)
    checks = check_visual_source(project_dir, platform)
    screenshots: list[dict[str, Any]] = []
    if args.screenshots:
        screenshots = capture_playwright_screenshots(
            url=args.url,
            output_dir=Path(args.output_dir).expanduser().resolve() if args.output_dir else project_dir / "docs" / "screenshots",
        )
        checks.extend(screenshot_checks(screenshots))
    summary = summarize_checks(checks)
    report = {
        "ok": summary["failures"] == 0,
        "projectDir": str(project_dir),
        "platform": platform,
        "summary": summary,
        "checks": checks,
        "screenshots": screenshots,
        "reportPath": str(project_dir / "docs" / "visual-qa-report.md"),
        "statePath": str(project_dir / STATE_PATH),
    }
    write_visual_qa_report(project_dir, report)
    record_visual_qa(project_dir, report)
    return report


def check_visual_source(project_dir: Path, platform: str) -> list[dict[str, Any]]:
    page_path = primary_page_path(project_dir, platform)
    css_path = primary_css_path(project_dir, platform)
    page = read_optional(page_path) if page_path else ""
    css = read_optional(css_path) if css_path else ""
    checks = [
        check_bool("stylesheet", bool(css), "Stylesheet found.", "No primary stylesheet was found."),
        check_bool("responsive-media-query", "@media" in css, "Responsive media query found.", "No responsive media query found."),
        check_bool(
            "mobile-grid-collapse",
            bool(re.search(r"@media[^{]+max-width[\s\S]+grid-template-columns\s*:\s*1fr", css)),
            "Mobile grid collapse rule found.",
            "No mobile grid collapse rule found.",
        ),
        check_bool(
            "button-touch-target",
            bool(re.search(r"min-height\s*:\s*(4[4-9]|[5-9]\d)px", css)),
            "Button touch target minimum appears present.",
            "No >=44px button touch target minimum found.",
        ),
        check_bool(
            "no-negative-letter-spacing",
            not re.search(r"letter-spacing\s*:\s*-\d", css),
            "No negative letter spacing found.",
            "Negative letter spacing found.",
        ),
    ]
    fixed_widths = re.findall(r"\b(?:width|min-width)\s*:\s*(\d{3,})px", css)
    checks.append(
        {
            "name": "fixed-width-risk",
            "status": "warning" if fixed_widths else "pass",
            "message": f"Large fixed widths found: {', '.join(fixed_widths[:5])}px" if fixed_widths else "No large fixed widths found.",
        }
    )
    if platform == "static":
        checks.append(
            check_bool(
                "viewport-meta",
                'name="viewport"' in page or "name='viewport'" in page,
                "Viewport meta tag found.",
                "Viewport meta tag is missing.",
            )
        )
    else:
        checks.append(
            {
                "name": "viewport-meta",
                "status": "skip",
                "message": "Next.js manages viewport metadata at runtime unless explicitly configured.",
            }
        )
    return checks


def capture_playwright_screenshots(url: str, output_dir: Path) -> list[dict[str, Any]]:
    if not url:
        return [{"ok": False, "viewport": "all", "error": "--url is required when --screenshots is used."}]
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        return [{"ok": False, "viewport": "all", "error": f"Playwright is not available: {exc}"}]

    output_dir.mkdir(parents=True, exist_ok=True)
    viewports = [
        ("desktop", {"width": 1440, "height": 1000}),
        ("mobile", {"width": 390, "height": 844}),
    ]
    captures = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for name, viewport in viewports:
                page = browser.new_page(viewport=viewport)
                page.goto(url, wait_until="networkidle", timeout=15000)
                path = output_dir / f"{name}.png"
                page.screenshot(path=str(path), full_page=True)
                captures.append({"ok": True, "viewport": name, "path": str(path), "url": url})
                page.close()
            browser.close()
    except Exception as exc:
        captures.append({"ok": False, "viewport": "all", "error": str(exc)})
    return captures


def screenshot_checks(screenshots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not screenshots:
        return []
    return [
        {
            "name": f"screenshot:{item.get('viewport', 'unknown')}",
            "status": "pass" if item.get("ok") else "warning",
            "message": item.get("path") or item.get("error") or "Screenshot check finished.",
        }
        for item in screenshots
    ]


def write_visual_qa_report(project_dir: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Visual QA Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Platform: {report['platform']}",
        f"Status: {'PASS' if report['ok'] else 'NEEDS WORK'}",
        "",
        "## Summary",
        "",
        f"- Total checks: {report['summary']['total']}",
        f"- Passed: {report['summary']['passes']}",
        f"- Warnings: {report['summary']['warnings']}",
        f"- Failures: {report['summary']['failures']}",
        "",
        "## Checks",
        "",
    ]
    for check in report["checks"]:
        lines.append(f"- {str(check.get('status', 'warning')).upper()}: {check.get('name')} - {check.get('message')}")
    if report.get("screenshots"):
        lines.extend(["", "## Screenshots", ""])
        for shot in report["screenshots"]:
            lines.append(f"- {shot.get('viewport')}: {shot.get('path') or shot.get('error')}")
    write_text(project_dir / "docs" / "visual-qa-report.md", "\n".join(lines))


def status_summary(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    state = read_state(project_dir / STATE_PATH)
    markdown = format_discord_summary(project_dir, state)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "summary": markdown,
        "statePath": str(project_dir / STATE_PATH),
    }


def format_discord_summary(project_dir: Path, state: dict[str, Any]) -> str:
    project = state.get("project", {}) if isinstance(state.get("project"), dict) else {}
    name = project.get("name") or project_dir.name
    lines = [f"**Website Status: {name}**"]
    if project.get("platform"):
        lines.append(f"Platform: `{project['platform']}`")

    preview = state.get("lastPreview", {}) if isinstance(state.get("lastPreview"), dict) else {}
    if preview.get("publicUrl"):
        lines.append(f"Preview: {preview['publicUrl']}")

    approval = state.get("lastApproval", {}) if isinstance(state.get("lastApproval"), dict) else {}
    if approval.get("decision"):
        lines.append(f"Approval: `{approval['decision']}` for `{approval.get('target', 'project')}`")

    qa = state.get("lastQa", {}) if isinstance(state.get("lastQa"), dict) else {}
    if qa.get("summary"):
        summary = qa["summary"]
        lines.append(
            f"QA: `{summary.get('passes', 0)} passed`, `{summary.get('warnings', 0)} warnings`, `{summary.get('failures', 0)} failures`"
        )

    visual = state.get("lastVisualQa", {}) if isinstance(state.get("lastVisualQa"), dict) else {}
    if visual.get("summary"):
        summary = visual["summary"]
        lines.append(
            f"Visual QA: `{summary.get('passes', 0)} passed`, `{summary.get('warnings', 0)} warnings`, `{summary.get('failures', 0)} failures`"
        )

    revision = state.get("lastRevision", {}) if isinstance(state.get("lastRevision"), dict) else {}
    if revision.get("type"):
        files = ", ".join(revision.get("files", [])) if isinstance(revision.get("files"), list) else ""
        lines.append(f"Last edit: `{revision['type']}` {files}".strip())

    deployment = state.get("lastDeployment", {}) if isinstance(state.get("lastDeployment"), dict) else {}
    if deployment.get("artifact"):
        lines.append(f"Deploy artifact: `{deployment['artifact']}`")

    lines.append("")
    lines.append("Next: run `/build-preview`, `/edit-section`, `/seo-optimize`, or `/deploy-site` as needed.")
    return "\n".join(lines)


def approval_request(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    reference = normalize_approval_reference(project_dir, args.reference)
    request = {
        "id": approval_id(args.target, reference),
        "type": "approval-request",
        "target": args.target,
        "reference": reference,
        "summary": args.summary,
        "previewUrl": args.preview_url or latest_preview_url(project_dir),
        "decision": "pending",
    }
    record_approval(project_dir, request)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "approval": request,
        "statePath": str(project_dir / STATE_PATH),
        "message": "Approval request recorded. Share the preview and record the decision with approval-record.",
    }


def approval_record(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    reference = normalize_approval_reference(project_dir, args.reference)
    decision = {
        "id": approval_id(args.target, reference),
        "type": "approval-decision",
        "target": args.target,
        "reference": reference,
        "decision": args.decision,
        "approver": args.approver,
        "notes": args.notes,
    }
    record_approval(project_dir, decision)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "approval": decision,
        "statePath": str(project_dir / STATE_PATH),
        "message": f"Approval decision recorded: {args.decision}.",
    }


def approval_id(target: str, reference: str) -> str:
    return slugify(f"{target}-{reference}", fallback=target)


def normalize_approval_reference(project_dir: Path, reference: str) -> str:
    value = (reference or "").strip()
    if not value:
        preview = read_state(project_dir / STATE_PATH).get("lastPreview", {})
        if isinstance(preview, dict) and preview.get("publicUrl"):
            return str(preview["publicUrl"])
        return "project"
    path = Path(value).expanduser()
    if path.is_absolute():
        try:
            return str(path.resolve().relative_to(project_dir))
        except ValueError:
            return str(path)
    return value


def latest_preview_url(project_dir: Path) -> str:
    state = read_state(project_dir / STATE_PATH)
    preview = state.get("lastPreview", {}) if isinstance(state.get("lastPreview"), dict) else {}
    return str(preview.get("publicUrl") or preview.get("siteletUrl") or preview.get("generatedUrl") or "")


def has_approval(project_dir: Path, target: str, reference: str) -> bool:
    state = read_state(project_dir / STATE_PATH)
    expected_id = approval_id(target, normalize_approval_reference(project_dir, reference))
    approvals = state.get("approvals", [])
    if not isinstance(approvals, list):
        return False
    for item in reversed(approvals):
        if not isinstance(item, dict):
            continue
        if item.get("id") == expected_id and item.get("decision") in {"revision_requested", "rejected"}:
            return False
        if item.get("id") == expected_id and item.get("decision") == "approved":
            return True
    return False


def deploy_prep(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    platform = detect_platform(project_dir)
    target = args.target
    if target == "auto":
        target = "static-zip" if platform == "static" else "vercel"

    deploy_dir = project_dir / DEPLOY_DIR
    deploy_dir.mkdir(parents=True, exist_ok=True)
    if target == "static-zip":
        result = prepare_static_zip(project_dir, deploy_dir)
    elif target in {"vercel", "netlify"}:
        result = prepare_node_hosting(project_dir, deploy_dir, target, platform)
    elif target == "github-pages":
        result = prepare_github_pages(project_dir, deploy_dir, platform)
    else:
        return {"ok": False, "error": f"Unsupported deploy target: {target}"}

    deployment = {
        "type": "deploy-prep",
        "target": target,
        "platform": platform,
        "artifact": result.get("artifact"),
        "notesPath": result.get("notesPath"),
    }
    record_deployment(project_dir, deployment)
    result.update(
        {
            "ok": True,
            "projectDir": str(project_dir),
            "platform": platform,
            "target": target,
            "statePath": str(project_dir / STATE_PATH),
        }
    )
    return result


def add_page(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    project = state.get("project", {}) if isinstance(state.get("project"), dict) else {}
    spec = SiteSpec(
        name=str(project.get("name") or project_dir.name.replace("-", " ").title()),
        description=str(project.get("description") or args.description or f"{args.title} page."),
        audience=str(project.get("audience") or "target customers"),
        goal=str(project.get("goal") or args.goal or "Contact us"),
        tone=str(project.get("tone") or "professional"),
        platform=detect_platform(project_dir),
        template=str(project.get("template") or "local-service"),
        slug=str(project.get("slug") or project_dir.name),
    )
    page = PageSpec(
        title=args.title.strip(),
        slug=slugify(args.slug or args.title, fallback="page"),
        page_type=slugify(args.page_type or args.title, fallback="page"),
        goal=args.goal or default_page_spec(args.page_type or args.title, spec).goal,
        description=args.description or default_page_spec(args.page_type or args.title, spec).description,
    )
    existing_pages = pages_from_state(project_dir, state, spec)
    pages = [item for item in existing_pages if item.slug != page.slug]
    pages.append(page)
    write_site_pages(project_dir, spec, pages)
    record_pages(project_dir, pages, {"type": "add-page", "page": page.__dict__})
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "page": page.__dict__,
        "path": str((project_dir / ("index.html" if page.slug == "home" else f"{page.slug}.html")) if spec.platform == "static" else (project_dir / "app" / page.slug / "page.tsx")),
        "statePath": str(project_dir / STATE_PATH),
    }


def media_plan(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    state = read_state(project_dir / STATE_PATH)
    project = state.get("project", {}) if isinstance(state.get("project"), dict) else {}
    spec = SiteSpec(
        name=str(project.get("name") or project_dir.name.replace("-", " ").title()),
        description=str(project.get("description") or ""),
        audience=str(project.get("audience") or "target customers"),
        goal=str(project.get("goal") or "Contact us"),
        tone=str(project.get("tone") or "professional"),
        platform=detect_platform(project_dir),
        template=str(project.get("template") or "local-service"),
        slug=str(project.get("slug") or project_dir.name),
    )
    pages = pages_from_state(project_dir, state, spec)
    if args.pages:
        wanted = {slugify(item.strip(), fallback="page") for item in args.pages.split(",") if item.strip()}
        pages = [page for page in pages if page.slug in wanted]
    assets = build_media_assets(spec, pages, args.style, max(1, args.per_page))
    media_dir = project_dir / MEDIA_DIR
    media_dir.mkdir(parents=True, exist_ok=True)
    if args.placeholders:
        for asset in assets:
            write_text(project_dir / asset["path"], render_placeholder_svg(asset, spec))
    manifest_path = project_dir / "docs" / "media-plan.json"
    notes_path = project_dir / "docs" / "media-plan.md"
    write_text(manifest_path, json.dumps({"version": 1, "assets": assets}, indent=2))
    write_media_plan_markdown(notes_path, assets)
    record_media(project_dir, {"type": "media-plan", "assets": assets, "manifestPath": str(manifest_path.relative_to(project_dir))})
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "assets": assets,
        "manifestPath": str(manifest_path),
        "notesPath": str(notes_path),
        "statePath": str(project_dir / STATE_PATH),
    }


def build_media_assets(spec: SiteSpec, pages: list[PageSpec], style: str, per_page: int) -> list[dict[str, Any]]:
    assets = []
    for page in pages:
        for index in range(per_page):
            slot = "hero" if index == 0 else f"supporting-{index + 1}"
            filename = f"{page.slug}-{slot}.svg"
            prompt = (
                f"{style} website image for {spec.name}, {page.title} page, "
                f"serving {spec.audience}, professional composition, no text in image"
            )
            assets.append(
                {
                    "id": slugify(f"{page.slug}-{slot}", fallback="asset"),
                    "page": page.slug,
                    "slot": slot,
                    "title": f"{page.title} {slot.title()} Image",
                    "filename": filename,
                    "path": str(MEDIA_DIR / filename),
                    "altText": f"{spec.name} {page.title.lower()} visual for {spec.audience}",
                    "prompt": prompt,
                    "status": "placeholder",
                }
            )
    return assets


def render_placeholder_svg(asset: dict[str, Any], spec: SiteSpec) -> str:
    title = escape_html(str(asset.get("title") or "Website image"))
    subtitle = escape_html(spec.name)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="720" viewBox="0 0 1200 720" role="img" aria-label="{escape_html(str(asset.get("altText") or title))}">
  <rect width="1200" height="720" fill="#e6f3f1"/>
  <rect x="72" y="72" width="1056" height="576" rx="28" fill="#ffffff" stroke="#d9e2ec" stroke-width="3"/>
  <circle cx="218" cy="238" r="82" fill="#0f766e" opacity="0.18"/>
  <rect x="348" y="208" width="562" height="34" rx="17" fill="#0f766e" opacity="0.28"/>
  <rect x="348" y="272" width="430" height="24" rx="12" fill="#18212f" opacity="0.16"/>
  <rect x="168" y="412" width="864" height="116" rx="20" fill="#f8fafc" stroke="#d9e2ec"/>
  <text x="168" y="592" fill="#18212f" font-family="Arial, Helvetica, sans-serif" font-size="34" font-weight="700">{title}</text>
  <text x="168" y="632" fill="#0f766e" font-family="Arial, Helvetica, sans-serif" font-size="22">{subtitle}</text>
</svg>"""


def write_media_plan_markdown(path: Path, assets: list[dict[str, Any]]) -> None:
    lines = ["# Media Plan", ""]
    for asset in assets:
        lines.extend(
            [
                f"## {asset['title']}",
                "",
                f"- Page: `{asset['page']}`",
                f"- Slot: `{asset['slot']}`",
                f"- File: `{asset['path']}`",
                f"- Alt text: {asset['altText']}",
                f"- Prompt: {asset['prompt']}",
                "",
            ]
        )
    write_text(path, "\n".join(lines))


def media_apply(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    manifest = load_media_manifest(project_dir, args.manifest)
    if not manifest:
        return {"ok": False, "error": "No media assets found. Run media-plan first."}
    platform = detect_platform(project_dir)
    changed: list[str] = []
    if platform != "static":
        return {"ok": False, "error": "media-apply currently supports generated static HTML projects."}
    for asset in manifest:
        if asset.get("slot") != "hero":
            continue
        page_path = project_dir / ("index.html" if asset.get("page") == "home" else f"{asset.get('page')}.html")
        if not page_path.exists():
            continue
        html = page_path.read_text(encoding="utf-8")
        if f'src="{asset.get("path")}"' in html:
            continue
        figure = (
            f'\n          <figure class="media-figure">'
            f'<img src="{escape_html(str(asset.get("path")))}" alt="{escape_html(str(asset.get("altText")))}" />'
            "</figure>"
        )
        updated = re.sub(r"(</div>\s*</section>)", figure + r"\n        \1", html, count=1)
        if updated != html:
            page_path.write_text(updated, encoding="utf-8")
            changed.append(str(page_path.relative_to(project_dir)))
    if changed:
        ensure_media_css(project_dir / "styles.css")
    record_media(project_dir, {"type": "media-apply", "files": changed})
    return {"ok": True, "projectDir": str(project_dir), "files": changed, "statePath": str(project_dir / STATE_PATH)}


def load_media_manifest(project_dir: Path, manifest: str) -> list[dict[str, Any]]:
    path = Path(manifest).expanduser() if manifest else project_dir / "docs" / "media-plan.json"
    if not path.is_absolute():
        path = project_dir / path
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    assets = payload.get("assets") if isinstance(payload, dict) else None
    return assets if isinstance(assets, list) else []


def ensure_media_css(css_path: Path) -> None:
    css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    if ".media-figure" in css:
        return
    css_path.write_text(
        css.rstrip()
        + """

.media-figure {
  margin: 28px 0 0;
}

.media-figure img {
  display: block;
  width: min(100%, 760px);
  height: auto;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
}
""",
        encoding="utf-8",
    )


def media_add(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    source = Path(args.file).expanduser().resolve()
    if not source.exists() or not source.is_file():
        return {"ok": False, "error": f"asset file does not exist: {source}"}
    filename = args.filename or f"{slugify(args.title or source.stem, fallback='asset')}{source.suffix.lower()}"
    dest = project_dir / MEDIA_DIR / filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    asset = {
        "id": slugify(args.asset_id or Path(filename).stem, fallback="asset"),
        "page": args.page or "home",
        "slot": args.slot or "supporting",
        "title": args.title or Path(filename).stem.replace("-", " ").title(),
        "filename": filename,
        "path": str(dest.relative_to(project_dir)),
        "altText": args.alt_text,
        "prompt": "",
        "status": "provided",
    }
    upsert_media_asset(project_dir, asset)
    return {"ok": True, "projectDir": str(project_dir), "asset": asset, "statePath": str(project_dir / STATE_PATH)}


def wordpress_media_upload(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    manifest = load_media_manifest(project_dir, args.manifest)
    if args.asset_id:
        manifest = [asset for asset in manifest if asset.get("id") == args.asset_id]
    uploads = []
    for asset in manifest:
        source_url = args.url or asset.get("sourceUrl") or asset.get("publicUrl")
        if not source_url:
            uploads.append({"ok": False, "assetId": asset.get("id"), "error": "asset has no public URL for WordPress upload"})
            continue
        result = call_wordpress_mcp_tool(
            args.mcp_url or os.getenv("WORDPRESS_MCP_URL", os.getenv("HERMES_WORDPRESS_MCP_URL", "")),
            args.mcp_token or os.getenv("WORDPRESS_MCP_TOKEN", os.getenv("HERMES_WORDPRESS_MCP_TOKEN", "")),
            "upload_media_from_url",
            {"url": source_url, "title": asset.get("title", ""), "alt_text": asset.get("altText", "")},
        )
        result["assetId"] = asset.get("id")
        result["ok"] = True
        uploads.append(result)
    record_media(project_dir, {"type": "wordpress-media-upload", "uploads": uploads})
    return {"ok": all(item.get("ok") for item in uploads), "projectDir": str(project_dir), "uploads": uploads}


def pages_from_state(project_dir: Path, state: dict[str, Any], spec: SiteSpec) -> list[PageSpec]:
    raw_pages = state.get("pages", [])
    pages: list[PageSpec] = []
    if isinstance(raw_pages, list):
        for item in raw_pages:
            if not isinstance(item, dict):
                continue
            pages.append(
                PageSpec(
                    title=str(item.get("title") or "Page"),
                    slug=str(item.get("slug") or slugify(str(item.get("title") or "page"))),
                    page_type=str(item.get("page_type") or item.get("pageType") or item.get("slug") or "page"),
                    goal=str(item.get("goal") or spec.goal),
                    description=str(item.get("description") or ""),
                )
            )
    if not pages:
        pages = [default_page_spec("home", spec)]
        if (project_dir / "about.html").exists():
            pages.append(default_page_spec("about", spec))
        if (project_dir / "services.html").exists():
            pages.append(default_page_spec("services", spec))
        if (project_dir / "contact.html").exists():
            pages.append(default_page_spec("contact", spec))
    if not any(page.slug == "home" for page in pages):
        pages.insert(0, default_page_spec("home", spec))
    return pages


def wordpress_package(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    title = args.title or infer_project_title(project_dir)
    slug = args.slug or slugify(title)
    content = resolve_wordpress_content(project_dir, args.content, args.content_file)
    if not content.strip():
        return {"ok": False, "error": "No WordPress content could be generated."}

    wp_dir = project_dir / WORDPRESS_DIR
    wp_dir.mkdir(parents=True, exist_ok=True)
    content_path = wp_dir / f"{slug}.html"
    spec_path = wp_dir / f"{slug}.json"
    notes_path = wp_dir / "WORDPRESS.md"
    write_text(content_path, content)
    spec = {
        "title": title,
        "slug": slug,
        "status": args.status,
        "siteName": args.site_name,
        "excerpt": args.excerpt,
        "contentFile": str(content_path.relative_to(project_dir)),
        "sourceProject": str(project_dir),
    }
    write_text(spec_path, json.dumps(spec, indent=2))
    write_text(
        notes_path,
        f"""# WordPress Draft Package

## Page

- Title: {title}
- Slug: {slug}
- Status: {args.status}
- Content: `{content_path.relative_to(project_dir)}`
- Spec: `{spec_path.relative_to(project_dir)}`

## Workflow

1. Preview this draft with `wordpress-preview`.
2. Review the Sitelet URL with the user.
3. After approval, create or update the WordPress page as `{args.status}`.
4. Do not publish live unless the user explicitly approves production publish.
""",
    )
    record_wordpress(
        project_dir,
        {
            "type": "wordpress-package",
            "title": title,
            "slug": slug,
            "status": args.status,
            "contentFile": str(content_path.relative_to(project_dir)),
            "specPath": str(spec_path.relative_to(project_dir)),
        },
    )
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "title": title,
        "slug": slug,
        "status": args.status,
        "contentFile": str(content_path),
        "specPath": str(spec_path),
        "notesPath": str(notes_path),
        "statePath": str(project_dir / STATE_PATH),
    }


def wordpress_preview(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    title = args.title
    slug = args.slug
    status = args.status
    excerpt = args.excerpt
    content = ""
    if args.spec:
        spec_path = Path(args.spec).expanduser()
        if not spec_path.is_absolute():
            spec_path = project_dir / spec_path
        if not spec_path.exists():
            return {"ok": False, "error": f"WordPress spec does not exist: {spec_path}"}
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        title = title or spec.get("title", "")
        slug = slug or spec.get("slug", "")
        status = status or spec.get("status", "draft")
        excerpt = excerpt or spec.get("excerpt", "")
        content_file = spec.get("contentFile", "")
        if content_file:
            content_path = project_dir / content_file
            content = content_path.read_text(encoding="utf-8") if content_path.exists() else ""
    content = resolve_wordpress_content(project_dir, args.content or content, args.content_file)
    if not title:
        title = infer_project_title(project_dir)
    if not slug:
        slug = slugify(title)
    if not content.strip():
        return {"ok": False, "error": "WordPress preview content is empty."}

    result = publish_wordpress_preview(
        title=title,
        content=content,
        site_name=args.site_name,
        slug=slug,
        excerpt=excerpt,
        status=status or "draft",
        base_url=args.sitelet_base_url,
        api_token=args.sitelet_api_token,
    )
    record = {
        "type": "wordpress-preview",
        "title": title,
        "slug": slug,
        "status": status or "draft",
        "siteletUrl": result.get("siteletUrl"),
        "generatedUrl": result.get("generatedUrl"),
        "ok": bool(result.get("ok")),
    }
    record_wordpress(project_dir, record)
    return {
        "ok": bool(result.get("ok")),
        "projectDir": str(project_dir),
        "title": title,
        "slug": slug,
        "status": status or "draft",
        "preview": result,
        "statePath": str(project_dir / STATE_PATH),
    }


def wordpress_publish(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    if not args.approved and not has_approval(project_dir, "wordpress-publish", args.spec):
        return {
            "ok": False,
            "error": (
                "Publishing to WordPress requires explicit approval. "
                "Record approval with approval-record or re-run with --approved after the preview is approved."
            ),
        }

    try:
        package = load_wordpress_package(project_dir, args.spec)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}
    title = args.title or package.get("title") or infer_project_title(project_dir)
    slug = args.slug or package.get("slug") or slugify(title)
    status = args.status or package.get("status") or "draft"
    excerpt = args.excerpt or package.get("excerpt") or ""
    content = package.get("content", "")
    content = resolve_wordpress_content(project_dir, args.content or content, args.content_file)
    if not content.strip():
        return {"ok": False, "error": "WordPress publish content is empty."}

    result = publish_wordpress_content(
        endpoint=args.mcp_url,
        api_token=args.mcp_token,
        title=title,
        content=content,
        slug=slug,
        excerpt=excerpt,
        status=status,
        content_type=args.content_type,
        wordpress_id=args.wordpress_id,
        update_existing=not args.no_update_existing,
    )
    record = {
        "type": "wordpress-publish",
        "title": title,
        "slug": slug,
        "status": status,
        "contentType": args.content_type,
        "wordpressId": result.get("id"),
        "editUrl": result.get("edit_link"),
        "publicUrl": result.get("link"),
        "tool": result.get("tool"),
        "approval": "flag" if args.approved else approval_id("wordpress-publish", normalize_approval_reference(project_dir, args.spec)),
        "ok": bool(result.get("ok")),
    }
    record_wordpress(project_dir, record)
    return {
        "ok": bool(result.get("ok")),
        "projectDir": str(project_dir),
        "title": title,
        "slug": slug,
        "status": status,
        "contentType": args.content_type,
        "wordpress": result,
        "statePath": str(project_dir / STATE_PATH),
    }


def load_wordpress_package(project_dir: Path, spec: str) -> dict[str, Any]:
    if not spec:
        return {}
    spec_path = Path(spec).expanduser()
    if not spec_path.is_absolute():
        spec_path = project_dir / spec_path
    if not spec_path.exists():
        raise FileNotFoundError(f"WordPress spec does not exist: {spec_path}")
    payload = json.loads(spec_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"WordPress spec must be a JSON object: {spec_path}")
    content_file = payload.get("contentFile", "")
    content = ""
    if content_file:
        content_path = project_dir / str(content_file)
        if content_path.exists():
            content = content_path.read_text(encoding="utf-8")
    payload["content"] = content
    return payload


def resolve_wordpress_content(project_dir: Path, content: str, content_file: str) -> str:
    if content_file:
        path = Path(content_file).expanduser()
        if not path.is_absolute():
            path = project_dir / path
        if path.exists():
            return path.read_text(encoding="utf-8")
    if content and content.strip():
        return content
    return generate_wordpress_content_from_project(project_dir)


def generate_wordpress_content_from_project(project_dir: Path) -> str:
    platform = detect_platform(project_dir)
    source_path = primary_page_path(project_dir, platform)
    if source_path:
        sections = extract_sections(source_path, platform)
        if sections:
            parts = []
            for section in sections:
                heading = section.get("heading", "").strip()
                body = section.get("body", "").strip()
                if heading:
                    parts.append(f"<!-- wp:heading --><h2>{escape_html(heading)}</h2><!-- /wp:heading -->")
                if body:
                    parts.append(f"<!-- wp:paragraph --><p>{escape_html(body)}</p><!-- /wp:paragraph -->")
            if parts:
                return "\n\n".join(parts)
    content_plan = project_dir / "docs" / "content-plan.md"
    if content_plan.exists():
        text = content_plan.read_text(encoding="utf-8")
        paragraphs = [line.strip("-# ") for line in text.splitlines() if line.strip() and not line.startswith("#")]
        return "\n\n".join(f"<!-- wp:paragraph --><p>{escape_html(item)}</p><!-- /wp:paragraph -->" for item in paragraphs)
    return ""


def infer_project_title(project_dir: Path) -> str:
    state = read_state(project_dir / STATE_PATH)
    project = state.get("project", {}) if isinstance(state.get("project"), dict) else {}
    if project.get("name"):
        return str(project["name"])
    return project_dir.name.replace("-", " ").title()


def publish_wordpress_preview(
    title: str,
    content: str,
    site_name: str,
    slug: str,
    excerpt: str,
    status: str,
    base_url: str,
    api_token: str,
) -> dict[str, Any]:
    try:
        from tools.sitelet_tool import wordpress_preview_publish

        raw = wordpress_preview_publish(
            title=title,
            content=content,
            site_name=site_name or "WordPress Preview",
            slug=slug,
            excerpt=excerpt,
            status=status,
            base_url=base_url or os.getenv("SITELET_BASE_URL", ""),
            api_token=api_token or os.getenv("SITELET_API_TOKEN", ""),
        )
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    parsed = parse_json_output(raw)
    return parsed or {"ok": False, "error": raw}


def publish_wordpress_content(
    endpoint: str,
    api_token: str,
    title: str,
    content: str,
    slug: str,
    excerpt: str,
    status: str,
    content_type: str,
    wordpress_id: int,
    update_existing: bool = True,
) -> dict[str, Any]:
    resolved_endpoint = (endpoint or os.getenv("WORDPRESS_MCP_URL") or os.getenv("HERMES_WORDPRESS_MCP_URL") or "").strip()
    resolved_token = (api_token or os.getenv("WORDPRESS_MCP_TOKEN") or os.getenv("HERMES_WORDPRESS_MCP_TOKEN") or "").strip()
    if not resolved_endpoint:
        return {"ok": False, "error": "WORDPRESS_MCP_URL is not configured."}
    if not resolved_token:
        return {"ok": False, "error": "WORDPRESS_MCP_TOKEN is not configured."}

    post_type = "page" if content_type == "page" else "post"
    target_id = int(wordpress_id or 0)
    try:
        if target_id:
            tool = f"update_{post_type}"
            payload = wordpress_update_payload(target_id, title, content, slug, excerpt, status)
            result = call_wordpress_mcp_tool(resolved_endpoint, resolved_token, tool, payload)
            result.update({"ok": True, "tool": tool, "matchedExisting": True})
            return result

        if update_existing:
            existing = find_existing_wordpress_content(resolved_endpoint, resolved_token, post_type, title, slug)
            if existing:
                tool = f"update_{post_type}"
                payload = wordpress_update_payload(int(existing["id"]), title, content, slug, excerpt, status)
                result = call_wordpress_mcp_tool(resolved_endpoint, resolved_token, tool, payload)
                result.update({"ok": True, "tool": tool, "matchedExisting": True})
                return result

        if post_type == "page":
            tool = "create_draft_page"
            payload = wordpress_create_payload(title, content, slug, excerpt, status)
            result = call_wordpress_mcp_tool(resolved_endpoint, resolved_token, tool, payload)
            result.update({"ok": True, "tool": tool, "matchedExisting": False})
            return result

        tool = "create_draft_post"
        payload = wordpress_create_payload(title, content, slug, excerpt, "draft")
        result = call_wordpress_mcp_tool(resolved_endpoint, resolved_token, tool, payload)
        if status and status != "draft" and result.get("id"):
            tool = "update_post"
            payload = wordpress_update_payload(int(result["id"]), title, content, slug, excerpt, status)
            result = call_wordpress_mcp_tool(resolved_endpoint, resolved_token, tool, payload)
        result.update({"ok": True, "tool": tool, "matchedExisting": False})
        return result
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def wordpress_create_payload(title: str, content: str, slug: str, excerpt: str, status: str) -> dict[str, Any]:
    payload = {"title": title, "content": content, "slug": slug, "excerpt": excerpt}
    if status:
        payload["status"] = status
    return {key: value for key, value in payload.items() if value not in {"", None}}


def wordpress_update_payload(content_id: int, title: str, content: str, slug: str, excerpt: str, status: str) -> dict[str, Any]:
    payload = wordpress_create_payload(title, content, slug, excerpt, status)
    payload["id"] = content_id
    return payload


def find_existing_wordpress_content(endpoint: str, api_token: str, post_type: str, title: str, slug: str) -> dict[str, Any] | None:
    tool = "list_pages" if post_type == "page" else "list_posts"
    search = slug or title
    result = call_wordpress_mcp_tool(endpoint, api_token, tool, {"status": "any", "search": search, "limit": 20})
    items = result.get("items") if isinstance(result.get("items"), list) else []
    wanted_slug = slugify(slug or title)
    wanted_title = normalize_title(title)
    for item in items:
        item_slug = str(item.get("slug") or "")
        item_title = normalize_title(str(item.get("title") or ""))
        if item_slug == wanted_slug or item_title == wanted_title:
            return item
    return None


def normalize_title(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", value or "")).strip().lower()


def call_wordpress_mcp_tool(endpoint: str, api_token: str, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "jsonrpc": "2.0",
        "id": f"hermes-{name}",
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments},
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}",
            "User-Agent": "Hermes-Agent WordPress Publisher",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"WordPress MCP call failed with HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach WordPress MCP endpoint: {exc.reason}") from exc

    parsed = json.loads(raw)
    if "error" in parsed:
        error = parsed["error"]
        message = error.get("message") if isinstance(error, dict) else str(error)
        raise RuntimeError(message or "WordPress MCP returned an error.")
    result = parsed.get("result", {})
    content_items = result.get("content") if isinstance(result, dict) else None
    if isinstance(content_items, list):
        for item in content_items:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text", "")
                tool_result = parse_json_output(text)
                if tool_result:
                    return tool_result
    return result if isinstance(result, dict) else {}


def prepare_static_zip(project_dir: Path, deploy_dir: Path) -> dict[str, Any]:
    package_dir = deploy_dir / "static-site"
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True, exist_ok=True)

    include_names = ["index.html", "styles.css", "assets", "images", "public"]
    copied: list[str] = []
    for name in include_names:
        source = project_dir / name
        if not source.exists():
            continue
        dest = package_dir / name
        if source.is_dir():
            shutil.copytree(source, dest)
        else:
            shutil.copy2(source, dest)
        copied.append(name)

    notes_path = deploy_dir / "DEPLOYMENT.md"
    write_text(
        notes_path,
        """# Static Website Deployment

## Artifact

Upload `static-site.zip` to static hosting, cPanel public_html, Netlify drag-and-drop,
Vercel static import, S3, or GitHub Pages.

## Checklist

- Confirm the latest preview was approved.
- Upload the zip contents, not the parent folder, when using cPanel/public_html.
- Confirm the homepage loads as `/index.html`.
- Re-run QA after deployment if the host rewrites links or paths.
""",
    )

    zip_path = deploy_dir / "static-site.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(package_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(package_dir))

    return {
        "artifact": str(zip_path),
        "packageDir": str(package_dir),
        "notesPath": str(notes_path),
        "files": copied,
        "commands": ["unzip static-site.zip", "upload contents to your static host"],
    }


def prepare_node_hosting(project_dir: Path, deploy_dir: Path, target: str, platform: str) -> dict[str, Any]:
    if platform not in {"nextjs", "node"}:
        return {
            "artifact": "",
            "notesPath": str(deploy_dir / "DEPLOYMENT.md"),
            "warning": f"{target} prep is intended for Next.js/Node projects; detected {platform}.",
            "commands": [],
        }

    build_command = "npm run build"
    dev_command = "npm run dev"
    install_command = "npm install"
    if target == "vercel":
        settings = {
            "framework": "Next.js",
            "installCommand": install_command,
            "buildCommand": build_command,
            "outputDirectory": ".next",
            "devCommand": dev_command,
        }
        commands = ["npm install", "npm run build", "vercel deploy"]
        title = "Vercel Deployment"
    else:
        settings = {
            "framework": "Next.js",
            "installCommand": install_command,
            "buildCommand": build_command,
            "publishDirectory": ".next",
        }
        commands = ["npm install", "npm run build", "netlify deploy --build"]
        title = "Netlify Deployment"

    settings_path = deploy_dir / f"{target}-settings.json"
    write_text(settings_path, json.dumps(settings, indent=2))
    notes_path = deploy_dir / "DEPLOYMENT.md"
    write_text(
        notes_path,
        f"""# {title}

## Recommended Settings

See `{settings_path.name}`.

## Commands

```bash
{chr(10).join(commands)}
```

## Checklist

- Confirm environment variables before deploying.
- Run `scripts/website_agency.py qa --project-dir . --run-build` before publish.
- Use preview deployment first when possible.
- Do not connect production domains until the user approves the preview.
""",
    )
    return {
        "artifact": str(settings_path),
        "notesPath": str(notes_path),
        "settings": settings,
        "commands": commands,
    }


def prepare_github_pages(project_dir: Path, deploy_dir: Path, platform: str) -> dict[str, Any]:
    if platform != "static":
        notes = "GitHub Pages prep currently supports static HTML projects only."
        notes_path = deploy_dir / "DEPLOYMENT.md"
        write_text(notes_path, f"# GitHub Pages Deployment\n\n{notes}\n")
        return {"artifact": "", "notesPath": str(notes_path), "warning": notes, "commands": []}

    result = prepare_static_zip(project_dir, deploy_dir)
    notes_path = deploy_dir / "DEPLOYMENT.md"
    write_text(
        notes_path,
        """# GitHub Pages Deployment

## Artifact

Use `static-site.zip` or commit the static files directly to a repository.

## Repository Setup

1. Put `index.html`, `styles.css`, and assets at the repository root, or in `/docs`.
2. In GitHub, open Settings -> Pages.
3. Select the branch and folder that contains `index.html`.
4. Wait for the Pages URL to publish.

## Checklist

- Confirm the latest preview was approved.
- Confirm all local links work after publishing.
""",
    )
    result["notesPath"] = str(notes_path)
    result["commands"] = ["commit static files", "enable GitHub Pages in repository settings"]
    return result


def list_sections(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    platform = detect_platform(project_dir)
    source_path = primary_page_path(project_dir, platform)
    if not source_path:
        return {"ok": False, "error": f"Could not find an editable page for platform: {platform}"}
    sections = extract_sections(source_path, platform)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "platform": platform,
        "file": str(source_path),
        "sections": sections,
    }


def edit_section(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    platform = detect_platform(project_dir)
    source_path = primary_page_path(project_dir, platform)
    if not source_path:
        return {"ok": False, "error": f"Could not find an editable page for platform: {platform}"}

    original = source_path.read_text(encoding="utf-8")
    updated, changes = apply_section_edits(
        original,
        section=args.section,
        heading=args.heading,
        body=args.body,
        cta=args.cta,
        platform=platform,
    )
    if updated == original:
        return {
            "ok": False,
            "error": f"No editable content was changed for section '{args.section}'.",
            "availableSections": extract_sections(source_path, platform),
        }
    source_path.write_text(updated, encoding="utf-8")
    revision = {
        "type": "edit-section",
        "section": args.section,
        "request": args.request or "",
        "changes": changes,
        "files": [str(source_path.relative_to(project_dir))],
    }
    record_revision(project_dir, revision)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "platform": platform,
        "revision": revision,
        "statePath": str(project_dir / STATE_PATH),
    }


def change_style(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}
    platform = detect_platform(project_dir)
    css_path = primary_css_path(project_dir, platform)
    if not css_path:
        return {"ok": False, "error": f"Could not find an editable stylesheet for platform: {platform}"}

    original = css_path.read_text(encoding="utf-8")
    palette = style_palette(args.preset, args.accent, args.ink, args.surface)
    updated = replace_palette(original, palette)
    if updated == original:
        return {"ok": False, "error": "No stylesheet colors were changed."}
    css_path.write_text(updated, encoding="utf-8")
    revision = {
        "type": "change-style",
        "preset": args.preset,
        "palette": palette,
        "files": [str(css_path.relative_to(project_dir))],
    }
    record_revision(project_dir, revision)
    return {
        "ok": True,
        "projectDir": str(project_dir),
        "platform": platform,
        "revision": revision,
        "statePath": str(project_dir / STATE_PATH),
    }


def primary_page_path(project_dir: Path, platform: str) -> Path | None:
    candidates = [project_dir / "index.html"] if platform == "static" else [project_dir / "app" / "page.tsx"]
    for path in candidates:
        if path.exists():
            return path
    return None


def primary_css_path(project_dir: Path, platform: str) -> Path | None:
    candidates = [project_dir / "styles.css"] if platform == "static" else [project_dir / "app" / "globals.css"]
    for path in candidates:
        if path.exists():
            return path
    return None


class SectionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sections: list[dict[str, str]] = []
        self._current: dict[str, str] | None = None
        self._capture: str | None = None
        self._depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {name.lower(): value or "" for name, value in attrs}
        lowered = tag.lower()
        if lowered == "section":
            section_id = attr.get("id") or infer_section_name(attr.get("class", ""))
            self._current = {"id": section_id or f"section-{len(self.sections) + 1}", "heading": "", "body": ""}
            self._depth = 1
            return
        if self._current:
            self._depth += 1
            if lowered in {"h1", "h2"} and not self._current["heading"]:
                self._capture = "heading"
            elif lowered == "p" and not self._current["body"] and "eyebrow" not in attr.get("class", ""):
                self._capture = "body"

    def handle_endtag(self, tag: str) -> None:
        if self._current:
            if tag.lower() in {"h1", "h2", "p"}:
                self._capture = None
            if tag.lower() == "section":
                self.sections.append(self._current)
                self._current = None
                self._depth = 0
            else:
                self._depth = max(0, self._depth - 1)

    def handle_data(self, data: str) -> None:
        if self._current and self._capture:
            self._current[self._capture] = (self._current[self._capture] + data).strip()


def extract_sections(source_path: Path, platform: str) -> list[dict[str, str]]:
    text = source_path.read_text(encoding="utf-8", errors="replace")
    if platform == "static":
        parser = SectionParser()
        parser.feed(text)
        return parser.sections
    sections = []
    for match in re.finditer(r"<section\b(?P<attrs>[^>]*)>(?P<body>.*?)</section>", text, flags=re.DOTALL):
        attrs = match.group("attrs")
        body = match.group("body")
        section_id = attr_value(attrs, "id") or infer_section_name(attr_value(attrs, "className"))
        heading = first_tag_text(body, "h1") or first_tag_text(body, "h2")
        para = first_body_paragraph_text(body)
        sections.append({"id": section_id or f"section-{len(sections) + 1}", "heading": heading, "body": para})
    return sections


def apply_section_edits(
    text: str,
    section: str,
    heading: str,
    body: str,
    cta: str,
    platform: str,
) -> tuple[str, list[str]]:
    section_pattern = re.compile(r"(<section\b(?P<attrs>[^>]*)>)(?P<body>.*?)(</section>)", re.DOTALL)
    changes: list[str] = []

    def replace(match: re.Match[str]) -> str:
        attrs = match.group("attrs")
        content = match.group("body")
        section_id = attr_value(attrs, "id") or infer_section_name(attr_value(attrs, "className" if platform == "nextjs" else "class"))
        if normalize_section(section_id) != normalize_section(section):
            return match.group(0)
        new_content = content
        if heading:
            new_content, changed = replace_first_tag(new_content, ("h1", "h2"), escape_for_platform(heading, platform))
            if changed:
                changes.append("heading")
        if body:
            new_content, changed = replace_first_body_paragraph(new_content, escape_for_platform(body, platform))
            if changed:
                changes.append("body")
        if cta:
            new_content, changed = replace_first_anchor_text(new_content, escape_for_platform(cta, platform))
            if changed:
                changes.append("cta")
        return f"{match.group(1)}{new_content}{match.group(4)}"

    return section_pattern.sub(replace, text), changes


def attr_value(attrs: str, name: str) -> str:
    match = re.search(rf"\b{name}=[\"']([^\"']+)[\"']", attrs or "")
    return match.group(1) if match else ""


def infer_section_name(class_value: str) -> str:
    classes = set((class_value or "").replace("{", " ").replace("}", " ").split())
    for candidate in ("hero", "services", "process", "contact", "cta", "proof"):
        if candidate in classes:
            return "top" if candidate == "hero" else candidate
    return ""


def normalize_section(value: str) -> str:
    return slugify(value or "", fallback="")


def first_tag_text(body: str, tag: str) -> str:
    match = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", body, flags=re.DOTALL)
    if not match:
        return ""
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def first_body_paragraph_text(body: str) -> str:
    for match in re.finditer(r"<p\b(?P<attrs>[^>]*)>(?P<body>.*?)</p>", body, flags=re.DOTALL):
        class_value = attr_value(match.group("attrs"), "class") or attr_value(match.group("attrs"), "className")
        if "eyebrow" in class_value:
            continue
        return re.sub(r"<[^>]+>", "", match.group("body")).strip()
    return ""


def replace_first_tag(content: str, tags: tuple[str, ...], replacement: str) -> tuple[str, bool]:
    for tag in tags:
        pattern = re.compile(rf"(<{tag}\b[^>]*>)(.*?)(</{tag}>)", re.DOTALL)
        if pattern.search(content):
            return pattern.sub(lambda match: f"{match.group(1)}{replacement}{match.group(3)}", content, count=1), True
    return content, False


def replace_first_body_paragraph(content: str, replacement: str) -> tuple[str, bool]:
    pattern = re.compile(r"(<p\b(?P<attrs>[^>]*)>)(.*?)(</p>)", re.DOTALL)
    for match in pattern.finditer(content):
        class_value = attr_value(match.group("attrs"), "class") or attr_value(match.group("attrs"), "className")
        if "eyebrow" in class_value:
            continue
        start, end = match.span()
        return f"{content[:start]}{match.group(1)}{replacement}{match.group(4)}{content[end:]}", True
    if pattern.search(content):
        return pattern.sub(lambda match: f"{match.group(1)}{replacement}{match.group(4)}", content, count=1), True
    return content, False


def replace_first_anchor_text(content: str, replacement: str) -> tuple[str, bool]:
    pattern = re.compile(r"(<a\b[^>]*>)(.*?)(</a>)", re.DOTALL)
    if not pattern.search(content):
        return content, False
    return pattern.sub(lambda match: f"{match.group(1)}{replacement}{match.group(3)}", content, count=1), True


def escape_for_platform(value: str, platform: str) -> str:
    return escape_js(value) if platform == "nextjs" else escape_html(value)


def style_palette(preset: str, accent: str, ink: str, surface: str) -> dict[str, str]:
    presets = {
        "professional": {"accent": "#0f766e", "accentDark": "#134e4a", "ink": "#18212f", "surface": "#f8fafc"},
        "luxury": {"accent": "#9f7a2f", "accentDark": "#5f4517", "ink": "#17130d", "surface": "#fbfaf7"},
        "modern": {"accent": "#2563eb", "accentDark": "#1e3a8a", "ink": "#111827", "surface": "#f9fafb"},
        "warm": {"accent": "#b45309", "accentDark": "#7c2d12", "ink": "#24140f", "surface": "#fffaf3"},
    }
    palette = dict(presets.get(preset, presets["professional"]))
    if accent:
        palette["accent"] = accent
    if ink:
        palette["ink"] = ink
    if surface:
        palette["surface"] = surface
    return palette


def replace_palette(css: str, palette: dict[str, str]) -> str:
    replacements = {
        "#0f766e": palette["accent"],
        "#16756f": palette["accent"],
        "#134e4a": palette["accentDark"],
        "#18212f": palette["ink"],
        "#172033": palette["ink"],
        "#f8fafc": palette["surface"],
    }
    updated = css
    for before, after in replacements.items():
        updated = updated.replace(before, after)
    return updated


def run_qa(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}

    platform = detect_platform(project_dir)
    checks: list[dict[str, Any]] = []
    checks.extend(check_required_docs(project_dir))
    if platform == "static":
        checks.extend(check_static_html(project_dir))
    elif platform == "nextjs":
        checks.extend(check_nextjs_source(project_dir))
    else:
        checks.append(
            {
                "name": "project-type",
                "status": "warning",
                "message": f"Unknown project type: {platform}. QA is limited to shared docs checks.",
            }
        )

    if args.run_build:
        checks.append(run_build_check(project_dir, platform, timeout=args.build_timeout))

    summary = summarize_checks(checks)
    report = {
        "ok": summary["failures"] == 0,
        "projectDir": str(project_dir),
        "platform": platform,
        "summary": summary,
        "checks": checks,
        "reportPath": str(project_dir / "docs" / "qa-report.md"),
        "statePath": str(project_dir / STATE_PATH),
    }
    write_qa_report(project_dir, report)
    record_qa(project_dir, report)
    return report


def check_required_docs(project_dir: Path) -> list[dict[str, Any]]:
    required = [
        "docs/website-brief.md",
        "docs/sitemap.md",
        "docs/design-system.md",
        "docs/content-plan.md",
    ]
    checks = []
    for rel in required:
        path = project_dir / rel
        checks.append(
            {
                "name": f"required-doc:{rel}",
                "status": "pass" if path.exists() and path.read_text(encoding="utf-8", errors="replace").strip() else "warning",
                "message": "Present." if path.exists() else "Missing generated website planning artifact.",
            }
        )
    return checks


class HtmlAuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.meta_description = ""
        self.h1_count = 0
        self.images_missing_alt: list[str] = []
        self.links: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {name.lower(): value or "" for name, value in attrs}
        lowered = tag.lower()
        if lowered == "title":
            self._in_title = True
        elif lowered == "meta" and attr.get("name", "").lower() == "description":
            self.meta_description = attr.get("content", "").strip()
        elif lowered == "h1":
            self.h1_count += 1
        elif lowered == "img":
            if "alt" not in attr:
                self.images_missing_alt.append(attr.get("src", "[inline image]"))
        elif lowered == "a" and attr.get("href"):
            self.links.append(attr["href"])

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data


def check_static_html(project_dir: Path) -> list[dict[str, Any]]:
    index_path = project_dir / "index.html"
    if not index_path.exists():
        return [{"name": "static-index", "status": "fail", "message": "index.html is missing."}]

    parser = HtmlAuditParser()
    parser.feed(index_path.read_text(encoding="utf-8", errors="replace"))
    checks = [
        check_bool("html-title", bool(parser.title.strip()), "Page has a <title>.", "Missing <title>."),
        check_bool(
            "meta-description",
            bool(parser.meta_description),
            "Page has a meta description.",
            "Missing meta description.",
        ),
        check_bool("single-h1", parser.h1_count == 1, "Page has exactly one H1.", f"Expected one H1, found {parser.h1_count}."),
        check_bool(
            "image-alt",
            not parser.images_missing_alt,
            "All images have alt attributes.",
            f"Images missing alt text: {', '.join(parser.images_missing_alt[:5])}",
        ),
    ]
    checks.extend(check_links(project_dir, parser.links))
    return checks


def check_nextjs_source(project_dir: Path) -> list[dict[str, Any]]:
    layout = read_optional(project_dir / "app" / "layout.tsx")
    page = read_optional(project_dir / "app" / "page.tsx")
    package_json = project_dir / "package.json"
    checks = [
        check_bool("package-json", package_json.exists(), "package.json exists.", "package.json is missing."),
        check_bool("next-layout", bool(layout), "app/layout.tsx exists.", "app/layout.tsx is missing."),
        check_bool("next-page", bool(page), "app/page.tsx exists.", "app/page.tsx is missing."),
        check_bool("metadata-title", "title" in layout, "Metadata title is present.", "Metadata title is missing."),
        check_bool(
            "metadata-description",
            "description" in layout,
            "Metadata description is present.",
            "Metadata description is missing.",
        ),
        check_bool("page-h1", "<h1" in page, "Page source contains an H1.", "Page source does not contain an H1."),
    ]
    image_tags = re.findall(r"<img\b[^>]*>", page)
    missing_alt = [tag for tag in image_tags if not re.search(r"\balt=", tag)]
    checks.append(
        check_bool(
            "image-alt",
            not missing_alt,
            "All explicit img tags include alt.",
            f"{len(missing_alt)} explicit img tag(s) are missing alt.",
        )
    )
    return checks


def check_links(project_dir: Path, links: list[str]) -> list[dict[str, Any]]:
    checks = []
    for href in links:
        if href.startswith(("#", "mailto:", "tel:", "http://", "https://", "//")):
            continue
        target = href.split("#", 1)[0].split("?", 1)[0]
        if not target:
            continue
        path = (project_dir / target).resolve()
        try:
            path.relative_to(project_dir.resolve())
        except ValueError:
            checks.append({"name": "internal-link", "status": "fail", "message": f"Link escapes project directory: {href}"})
            continue
        checks.append(
            {
                "name": "internal-link",
                "status": "pass" if path.exists() else "fail",
                "message": f"{href} exists." if path.exists() else f"Broken local link: {href}",
            }
        )
    if not checks:
        checks.append({"name": "internal-links", "status": "pass", "message": "No broken local file links found."})
    return checks


def run_build_check(project_dir: Path, platform: str, timeout: int) -> dict[str, Any]:
    if platform not in {"nextjs", "node"}:
        return {"name": "build", "status": "skip", "message": f"No build command required for {platform} project."}
    package_path = project_dir / "package.json"
    if not package_path.exists():
        return {"name": "build", "status": "fail", "message": "package.json is missing."}
    try:
        package = json.loads(package_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"name": "build", "status": "fail", "message": f"package.json is invalid JSON: {exc}"}
    scripts = package.get("scripts") if isinstance(package, dict) else None
    if not isinstance(scripts, dict) or "build" not in scripts:
        return {"name": "build", "status": "warning", "message": "No npm build script is defined."}
    try:
        completed = subprocess.run(
            ["npm", "run", "build"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=max(5, int(timeout)),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"name": "build", "status": "fail", "message": f"Build could not complete: {exc}"}
    output = ((completed.stdout or "") + "\n" + (completed.stderr or "")).strip()
    if len(output) > 2000:
        output = output[-2000:]
    return {
        "name": "build",
        "status": "pass" if completed.returncode == 0 else "fail",
        "message": "npm run build passed." if completed.returncode == 0 else "npm run build failed.",
        "exitCode": completed.returncode,
        "outputTail": output,
    }


def check_bool(name: str, condition: bool, pass_message: str, fail_message: str) -> dict[str, Any]:
    return {"name": name, "status": "pass" if condition else "fail", "message": pass_message if condition else fail_message}


def summarize_checks(checks: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"pass": 0, "warning": 0, "fail": 0, "skip": 0}
    for check in checks:
        status = str(check.get("status") or "warning")
        counts[status] = counts.get(status, 0) + 1
    return {
        "total": len(checks),
        "passes": counts.get("pass", 0),
        "warnings": counts.get("warning", 0),
        "failures": counts.get("fail", 0),
        "skipped": counts.get("skip", 0),
    }


def write_qa_report(project_dir: Path, report: dict[str, Any]) -> None:
    lines = [
        "# QA Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Platform: {report['platform']}",
        f"Status: {'PASS' if report['ok'] else 'NEEDS WORK'}",
        "",
        "## Summary",
        "",
        f"- Total checks: {report['summary']['total']}",
        f"- Passed: {report['summary']['passes']}",
        f"- Warnings: {report['summary']['warnings']}",
        f"- Failures: {report['summary']['failures']}",
        f"- Skipped: {report['summary']['skipped']}",
        "",
        "## Checks",
        "",
    ]
    for check in report["checks"]:
        status = str(check.get("status", "warning")).upper()
        lines.append(f"- {status}: {check.get('name')} - {check.get('message')}")
    write_text(project_dir / "docs" / "qa-report.md", "\n".join(lines))


def read_optional(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def preview_share(args: argparse.Namespace) -> dict[str, Any]:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        return {"ok": False, "error": f"project directory does not exist: {project_dir}"}

    plan = preview_plan(project_dir, port=args.port)
    attempts: list[dict[str, Any]] = []
    local_process: dict[str, Any] | None = None
    if args.start_local:
        local_process = start_preview_process(project_dir, plan["command"], args.log_file)

    if args.prefer in {"hermesproxy", "auto"}:
        proxy_result = start_hermes_proxy(
            target=plan["localUrl"],
            site=args.site or project_dir.name,
            base_url=args.proxy_base_url,
            token=args.proxy_token,
            wait_seconds=args.wait_seconds,
        )
        proxy_result.setdefault("method", "hermesproxy")
        attempts.append(proxy_result)
        if proxy_result.get("ok"):
            preview = {
                "method": "hermesproxy",
                "projectDir": str(project_dir),
                "platform": plan["platform"],
                "localUrl": plan["localUrl"],
                "publicUrl": proxy_result.get("publicUrl"),
                "site": proxy_result.get("site") or args.site or project_dir.name,
                "tunnelId": proxy_result.get("tunnelId"),
            }
            record_preview(project_dir, preview, attempts)
            return {"ok": True, "preview": preview, "process": local_process, "attempts": attempts}

    wants_sitelet = args.prefer == "sitelet" or args.fallback in {"sitelet", "auto"}
    if wants_sitelet and plan["platform"] == "static":
        sitelet_result = publish_sitelet_static(
            project_dir=project_dir,
            title=args.title or project_dir.name,
            base_url=args.sitelet_base_url,
            api_token=args.sitelet_api_token,
        )
        sitelet_result.setdefault("method", "sitelet")
        attempts.append(sitelet_result)
        if sitelet_result.get("ok"):
            preview = {
                "method": "sitelet",
                "projectDir": str(project_dir),
                "platform": plan["platform"],
                "localUrl": plan["localUrl"],
                "publicUrl": sitelet_result.get("siteletUrl") or sitelet_result.get("generatedUrl"),
                "siteletUrl": sitelet_result.get("siteletUrl"),
                "generatedUrl": sitelet_result.get("generatedUrl"),
            }
            record_preview(project_dir, preview, attempts)
            return {"ok": True, "preview": preview, "process": local_process, "attempts": attempts}

    message = "No shareable preview URL was created."
    if plan["platform"] != "static":
        message += " Sitelet fallback only supports static HTML projects."
    return {
        "ok": False,
        "error": message,
        "preview": plan,
        "process": local_process,
        "attempts": attempts,
    }


def start_hermes_proxy(
    target: str,
    site: str,
    base_url: str = "",
    token: str = "",
    wait_seconds: float = 8,
) -> dict[str, Any]:
    script = Path(__file__).resolve().parent / "start_hermes_proxy_connector.py"
    if not script.exists():
        return {"ok": False, "method": "hermesproxy", "error": f"connector helper not found: {script}"}

    command = [
        sys.executable,
        str(script),
        "--target",
        target,
        "--site",
        site,
        "--wait-seconds",
        str(wait_seconds),
    ]
    if base_url:
        command.extend(["--base-url", base_url])
    if token:
        command.extend(["--token", token])

    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=max(10, int(wait_seconds) + 8))
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "method": "hermesproxy", "error": str(exc)}

    payload = parse_json_output(completed.stdout)
    if not payload:
        payload = {"ok": False, "error": completed.stderr.strip() or completed.stdout.strip()}
    payload.setdefault("method", "hermesproxy")
    if completed.returncode != 0:
        payload["ok"] = False
        payload.setdefault("error", completed.stderr.strip() or "Hermes proxy connector failed.")
    return payload


def publish_sitelet_static(
    project_dir: Path,
    title: str,
    base_url: str = "",
    api_token: str = "",
) -> dict[str, Any]:
    index_path = project_dir / "index.html"
    if not index_path.exists():
        return {"ok": False, "method": "sitelet", "error": f"static index.html not found: {index_path}"}

    html = inline_static_css(index_path)
    try:
        from tools.sitelet_tool import sitelet_publish

        raw = sitelet_publish(
            title=title,
            html=html,
            source="website-agency-preview",
            base_url=base_url or os.getenv("SITELET_BASE_URL", ""),
            api_token=api_token or os.getenv("SITELET_API_TOKEN", ""),
        )
    except Exception as exc:
        return {"ok": False, "method": "sitelet", "error": str(exc)}

    payload = parse_json_output(raw)
    if not payload:
        return {"ok": False, "method": "sitelet", "error": raw}
    payload.setdefault("method", "sitelet")
    return payload


def inline_static_css(index_path: Path) -> str:
    html = index_path.read_text(encoding="utf-8")
    project_dir = index_path.parent

    def replace_link(match: re.Match[str]) -> str:
        attrs = match.group(0)
        href_match = re.search(r'href=["\']([^"\']+)["\']', attrs, flags=re.IGNORECASE)
        if not href_match:
            return attrs
        href = href_match.group(1)
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href) or href.startswith("//"):
            return attrs
        css_path = (project_dir / href).resolve()
        try:
            css_path.relative_to(project_dir.resolve())
        except ValueError:
            return attrs
        if not css_path.exists() or not css_path.is_file():
            return attrs
        css = css_path.read_text(encoding="utf-8")
        return f"<style>\n{css}\n</style>"

    return re.sub(
        r"<link\b(?=[^>]*rel=[\"']stylesheet[\"'])(?=[^>]*href=[\"'][^\"']+[\"'])[^>]*>",
        replace_link,
        html,
        flags=re.IGNORECASE,
    )


def parse_json_output(value: str) -> dict[str, Any]:
    text = (value or "").strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(text[start : end + 1])
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def record_preview(project_dir: Path, preview: dict[str, Any], attempts: list[dict[str, Any]]) -> None:
    state_file = project_dir / STATE_PATH
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state = read_state(state_file)
    previews = state.setdefault("previews", [])
    previews.append(
        {
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "preview": preview,
            "attempts": sanitize_attempts(attempts),
        }
    )
    state["lastPreview"] = preview
    state["workflowState"] = "preview_shared"
    write_text(state_file, json.dumps(state, indent=2))


def record_project_created(project_dir: Path, spec: SiteSpec, pages: list[PageSpec] | None = None) -> None:
    state_file = project_dir / STATE_PATH
    state = read_state(state_file)
    state["project"] = {
        "name": spec.name,
        "description": spec.description,
        "audience": spec.audience,
        "goal": spec.goal,
        "tone": spec.tone,
        "platform": spec.platform,
        "template": spec.template,
        "slug": spec.slug,
        "createdAt": state.get("project", {}).get("createdAt") or datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }
    if pages:
        state["pages"] = [page.__dict__ for page in pages]
        state["lastPage"] = {"type": "create-site", "pages": [page.__dict__ for page in pages]}
    write_text(state_file, json.dumps(state, indent=2))


def record_pages(project_dir: Path, pages: list[PageSpec], event: dict[str, Any]) -> None:
    state_file = project_dir / STATE_PATH
    state = read_state(state_file)
    state["pages"] = [page.__dict__ for page in pages]
    events = state.setdefault("pageEvents", [])
    record = dict(event)
    record["createdAt"] = datetime.now(timezone.utc).isoformat()
    events.append(record)
    state["lastPage"] = record
    write_text(state_file, json.dumps(state, indent=2))


def record_media(project_dir: Path, event: dict[str, Any]) -> None:
    state_file = project_dir / STATE_PATH
    state = read_state(state_file)
    events = state.setdefault("mediaEvents", [])
    record = dict(event)
    record["createdAt"] = datetime.now(timezone.utc).isoformat()
    events.append(record)
    state["lastMedia"] = record
    if event.get("assets"):
        state["mediaAssets"] = event["assets"]
    write_text(state_file, json.dumps(state, indent=2))


def upsert_media_asset(project_dir: Path, asset: dict[str, Any]) -> None:
    state_file = project_dir / STATE_PATH
    state = read_state(state_file)
    assets = state.setdefault("mediaAssets", [])
    if not isinstance(assets, list):
        assets = []
    assets = [item for item in assets if not isinstance(item, dict) or item.get("id") != asset.get("id")]
    assets.append(asset)
    state["mediaAssets"] = assets
    event = {"type": "media-add", "asset": asset, "createdAt": datetime.now(timezone.utc).isoformat()}
    state.setdefault("mediaEvents", []).append(event)
    state["lastMedia"] = event
    write_text(state_file, json.dumps(state, indent=2))


def record_qa(project_dir: Path, report: dict[str, Any]) -> None:
    state_file = project_dir / STATE_PATH
    state = read_state(state_file)
    qa_reports = state.setdefault("qaReports", [])
    record = {
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "ok": report["ok"],
        "platform": report["platform"],
        "summary": report["summary"],
        "reportPath": report["reportPath"],
    }
    qa_reports.append(record)
    state["lastQa"] = record
    write_text(state_file, json.dumps(state, indent=2))


def record_revision(project_dir: Path, revision: dict[str, Any]) -> None:
    state_file = project_dir / STATE_PATH
    state = read_state(state_file)
    revisions = state.setdefault("revisions", [])
    record = dict(revision)
    record["createdAt"] = datetime.now(timezone.utc).isoformat()
    revisions.append(record)
    state["lastRevision"] = record
    state["workflowState"] = "revision_in_progress"
    write_text(state_file, json.dumps(state, indent=2))


def record_deployment(project_dir: Path, deployment: dict[str, Any]) -> None:
    state_file = project_dir / STATE_PATH
    state = read_state(state_file)
    deployments = state.setdefault("deployments", [])
    record = dict(deployment)
    record["createdAt"] = datetime.now(timezone.utc).isoformat()
    deployments.append(record)
    state["lastDeployment"] = record
    write_text(state_file, json.dumps(state, indent=2))


def record_wordpress(project_dir: Path, event: dict[str, Any]) -> None:
    state_file = project_dir / STATE_PATH
    state = read_state(state_file)
    events = state.setdefault("wordpress", [])
    record = dict(event)
    record["createdAt"] = datetime.now(timezone.utc).isoformat()
    events.append(record)
    state["lastWordPress"] = record
    if record.get("type") == "wordpress-preview" and record.get("ok"):
        state["workflowState"] = "preview_shared"
    elif record.get("type") == "wordpress-publish" and record.get("ok"):
        state["workflowState"] = "published"
    write_text(state_file, json.dumps(state, indent=2))


def record_approval(project_dir: Path, event: dict[str, Any]) -> None:
    state_file = project_dir / STATE_PATH
    state = read_state(state_file)
    approvals = state.setdefault("approvals", [])
    record = dict(event)
    record["createdAt"] = datetime.now(timezone.utc).isoformat()
    approvals.append(record)
    state["lastApproval"] = record
    decision = record.get("decision")
    if decision == "pending":
        state["workflowState"] = "approval_requested"
    elif decision == "approved":
        state["workflowState"] = "approved_for_publish"
    elif decision == "revision_requested":
        state["workflowState"] = "revision_requested"
    elif decision == "rejected":
        state["workflowState"] = "approval_rejected"
    write_text(state_file, json.dumps(state, indent=2))


def record_visual_qa(project_dir: Path, report: dict[str, Any]) -> None:
    state_file = project_dir / STATE_PATH
    state = read_state(state_file)
    reports = state.setdefault("visualQaReports", [])
    record = {
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "ok": report["ok"],
        "platform": report["platform"],
        "summary": report["summary"],
        "reportPath": report["reportPath"],
        "screenshots": report.get("screenshots", []),
    }
    reports.append(record)
    state["lastVisualQa"] = record
    write_text(state_file, json.dumps(state, indent=2))


def read_state(state_file: Path) -> dict[str, Any]:
    if not state_file.exists():
        return {"version": 1, "previews": []}
    try:
        parsed = json.loads(state_file.read_text(encoding="utf-8"))
        return parsed if isinstance(parsed, dict) else {"version": 1, "previews": []}
    except json.JSONDecodeError:
        return {"version": 1, "previews": []}


def sanitize_attempts(attempts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sanitized = []
    for attempt in attempts:
        item = dict(attempt)
        for key in ("token", "api_token", "apiToken"):
            if key in item:
                item[key] = "[redacted]"
        sanitized.append(item)
    return sanitized


def start_preview_process(project_dir: Path, command: str, log_file: str | None) -> dict[str, Any]:
    log_path = Path(log_file).expanduser().resolve() if log_file else Path("/tmp") / f"hermes-website-preview-{project_dir.name}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_handle = log_path.open("ab")
    process = subprocess.Popen(
        shlex.split(command),
        cwd=str(project_dir),
        stdin=subprocess.DEVNULL,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    return {
        "pid": process.pid,
        "logFile": str(log_path),
        "message": "Preview process started in the background.",
    }


def escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def escape_js(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create-site", help="Create a static HTML or Next.js website project.")
    create.add_argument("--name", required=True, help="Business or website name.")
    create.add_argument("--description", required=True, help="Business description or site purpose.")
    create.add_argument("--audience", default="target customers", help="Target audience.")
    create.add_argument("--goal", default="Book a consultation", help="Primary conversion goal or CTA.")
    create.add_argument("--tone", default="professional", help="Brand tone.")
    create.add_argument("--platform", choices=("auto", "static", "nextjs"), default="auto")
    create.add_argument(
        "--template",
        choices=("auto", "local-service", "restaurant", "saas", "consultant", "ecommerce", "portfolio"),
        default="auto",
        help="Website template profile to use.",
    )
    create.add_argument("--output-dir", default="generated-sites", help="Directory where the site folder is created.")
    create.add_argument("--port", type=int, default=DEFAULT_PORT)
    create.add_argument("--force", action="store_true", help="Update files if the output project already exists.")
    create.add_argument("--pages", default="home", help="Comma-separated pages to generate, for example home,about,services,contact.")
    create.set_defaults(func=create_site)

    preview = subparsers.add_parser("build-preview", help="Create or start a preview plan for a website project.")
    preview.add_argument("--project-dir", default=".", help="Website project directory.")
    preview.add_argument("--port", type=int, default=DEFAULT_PORT)
    preview.add_argument("--start", action="store_true", help="Start the preview process in the background.")
    preview.add_argument("--log-file", help="Log file for --start.")
    preview.set_defaults(func=build_preview)

    deploy = subparsers.add_parser("deploy-prep", help="Prepare deployment artifacts and notes.")
    deploy.add_argument("--project-dir", default=".", help="Website project directory.")
    deploy.add_argument(
        "--target",
        choices=("auto", "static-zip", "vercel", "netlify", "github-pages"),
        default="auto",
        help="Deployment target to prepare.",
    )
    deploy.set_defaults(func=deploy_prep)

    add_page_parser = subparsers.add_parser("add-page", help="Add a generated page and update site navigation/history.")
    add_page_parser.add_argument("--project-dir", default=".", help="Website project directory.")
    add_page_parser.add_argument("--title", required=True, help="Page title, such as About or Services.")
    add_page_parser.add_argument("--slug", default="", help="Page slug. Defaults to title.")
    add_page_parser.add_argument("--page-type", default="", help="Page type such as about, services, contact, faq, pricing, blog.")
    add_page_parser.add_argument("--description", default="", help="Page meta description and hero copy.")
    add_page_parser.add_argument("--goal", default="", help="Page CTA or conversion goal.")
    add_page_parser.set_defaults(func=add_page)

    media_plan_parser = subparsers.add_parser("media-plan", help="Create a page-by-page media plan with alt text and placeholders.")
    media_plan_parser.add_argument("--project-dir", default=".", help="Website project directory.")
    media_plan_parser.add_argument("--pages", default="", help="Optional comma-separated page slugs to plan.")
    media_plan_parser.add_argument("--style", default="professional editorial", help="Image style prompt.")
    media_plan_parser.add_argument("--per-page", type=int, default=1, help="Assets to plan per page.")
    media_plan_parser.add_argument("--no-placeholders", dest="placeholders", action="store_false", help="Do not create local SVG placeholders.")
    media_plan_parser.set_defaults(func=media_plan, placeholders=True)

    media_apply_parser = subparsers.add_parser("media-apply", help="Apply planned hero media to generated static pages.")
    media_apply_parser.add_argument("--project-dir", default=".", help="Website project directory.")
    media_apply_parser.add_argument("--manifest", default="", help="Media manifest path, defaults to docs/media-plan.json.")
    media_apply_parser.set_defaults(func=media_apply)

    media_add_parser = subparsers.add_parser("media-add", help="Copy a provided media file into the project and record metadata.")
    media_add_parser.add_argument("--project-dir", default=".", help="Website project directory.")
    media_add_parser.add_argument("--file", required=True, help="Local media file to copy into assets/images.")
    media_add_parser.add_argument("--asset-id", default="", help="Stable asset ID.")
    media_add_parser.add_argument("--filename", default="", help="Destination filename.")
    media_add_parser.add_argument("--page", default="home", help="Page slug.")
    media_add_parser.add_argument("--slot", default="supporting", help="Asset slot, such as hero or supporting.")
    media_add_parser.add_argument("--title", default="", help="Asset title.")
    media_add_parser.add_argument("--alt-text", default="", help="Accessible alt text.")
    media_add_parser.set_defaults(func=media_add)

    wp_media_parser = subparsers.add_parser("wordpress-media-upload", help="Upload public media URLs to WordPress through Hermes MCP.")
    wp_media_parser.add_argument("--project-dir", default=".", help="Website project directory.")
    wp_media_parser.add_argument("--manifest", default="", help="Media manifest path, defaults to docs/media-plan.json.")
    wp_media_parser.add_argument("--asset-id", default="", help="Only upload one asset ID.")
    wp_media_parser.add_argument("--url", default="", help="Public URL override for the selected asset.")
    wp_media_parser.add_argument("--mcp-url", default=os.getenv("WORDPRESS_MCP_URL", os.getenv("HERMES_WORDPRESS_MCP_URL", "")))
    wp_media_parser.add_argument("--mcp-token", default=os.getenv("WORDPRESS_MCP_TOKEN", os.getenv("HERMES_WORDPRESS_MCP_TOKEN", "")))
    wp_media_parser.set_defaults(func=wordpress_media_upload)

    wp_package = subparsers.add_parser("wordpress-package", help="Create a WordPress-ready draft package.")
    wp_package.add_argument("--project-dir", default=".", help="Website project directory.")
    wp_package.add_argument("--title", default="", help="WordPress page/post title.")
    wp_package.add_argument("--slug", default="", help="WordPress slug.")
    wp_package.add_argument("--status", default="draft", help="Proposed WordPress status, usually draft or pending.")
    wp_package.add_argument("--site-name", default="WordPress Preview", help="Target WordPress site name.")
    wp_package.add_argument("--excerpt", default="", help="Optional WordPress excerpt.")
    wp_package.add_argument("--content", default="", help="Explicit WordPress/Gutenberg HTML content.")
    wp_package.add_argument("--content-file", default="", help="File containing WordPress/Gutenberg HTML content.")
    wp_package.set_defaults(func=wordpress_package)

    wp_preview = subparsers.add_parser("wordpress-preview", help="Publish a WordPress draft package to Sitelet preview.")
    wp_preview.add_argument("--project-dir", default=".", help="Website project directory.")
    wp_preview.add_argument("--spec", default="", help="WordPress package JSON path, relative to project dir if needed.")
    wp_preview.add_argument("--title", default="", help="Override WordPress title.")
    wp_preview.add_argument("--slug", default="", help="Override WordPress slug.")
    wp_preview.add_argument("--status", default="", help="Override WordPress status.")
    wp_preview.add_argument("--site-name", default="WordPress Preview", help="Target WordPress site name.")
    wp_preview.add_argument("--excerpt", default="", help="Optional WordPress excerpt.")
    wp_preview.add_argument("--content", default="", help="Explicit WordPress/Gutenberg HTML content.")
    wp_preview.add_argument("--content-file", default="", help="File containing WordPress/Gutenberg HTML content.")
    wp_preview.add_argument("--sitelet-base-url", default=os.getenv("SITELET_BASE_URL", ""))
    wp_preview.add_argument("--sitelet-api-token", default=os.getenv("SITELET_API_TOKEN", ""))
    wp_preview.set_defaults(func=wordpress_preview)

    wp_publish = subparsers.add_parser("wordpress-publish", help="Publish an approved WordPress package through Hermes MCP.")
    wp_publish.add_argument("--project-dir", default=".", help="Website project directory.")
    wp_publish.add_argument("--spec", default="", help="WordPress package JSON path, relative to project dir if needed.")
    wp_publish.add_argument("--title", default="", help="Override WordPress title.")
    wp_publish.add_argument("--slug", default="", help="Override WordPress slug.")
    wp_publish.add_argument("--status", default="", help="Override WordPress status, usually draft or pending.")
    wp_publish.add_argument("--excerpt", default="", help="Optional WordPress excerpt.")
    wp_publish.add_argument("--content", default="", help="Explicit WordPress/Gutenberg HTML content.")
    wp_publish.add_argument("--content-file", default="", help="File containing WordPress/Gutenberg HTML content.")
    wp_publish.add_argument("--content-type", choices=("page", "post"), default="page", help="WordPress content type.")
    wp_publish.add_argument("--wordpress-id", type=int, default=0, help="Existing WordPress page/post ID to update.")
    wp_publish.add_argument("--no-update-existing", action="store_true", help="Do not search by title/slug before creating.")
    wp_publish.add_argument("--mcp-url", default=os.getenv("WORDPRESS_MCP_URL", os.getenv("HERMES_WORDPRESS_MCP_URL", "")))
    wp_publish.add_argument("--mcp-token", default=os.getenv("WORDPRESS_MCP_TOKEN", os.getenv("HERMES_WORDPRESS_MCP_TOKEN", "")))
    wp_publish.add_argument("--approved", action="store_true", help="Required acknowledgement that the preview was approved.")
    wp_publish.set_defaults(func=wordpress_publish)

    approval_req = subparsers.add_parser("approval-request", help="Record a preview approval request.")
    approval_req.add_argument("--project-dir", default=".", help="Website project directory.")
    approval_req.add_argument("--target", default="publish", help="Action needing approval, such as wordpress-publish or deploy.")
    approval_req.add_argument("--reference", default="", help="Spec path, preview URL, deployment artifact, or project reference.")
    approval_req.add_argument("--summary", default="", help="Short approval request summary.")
    approval_req.add_argument("--preview-url", default="", help="Preview URL shown to the approver.")
    approval_req.set_defaults(func=approval_request)

    approval_rec = subparsers.add_parser("approval-record", help="Record an approval, rejection, or revision request.")
    approval_rec.add_argument("--project-dir", default=".", help="Website project directory.")
    approval_rec.add_argument("--target", default="publish", help="Action being approved, such as wordpress-publish or deploy.")
    approval_rec.add_argument("--reference", default="", help="Spec path, preview URL, deployment artifact, or project reference.")
    approval_rec.add_argument("--decision", choices=("approved", "revision_requested", "rejected"), required=True)
    approval_rec.add_argument("--approver", default="", help="Person or channel that approved/rejected.")
    approval_rec.add_argument("--notes", default="", help="Decision notes.")
    approval_rec.set_defaults(func=approval_record)

    sections = subparsers.add_parser("list-sections", help="List editable sections in a generated website.")
    sections.add_argument("--project-dir", default=".", help="Website project directory.")
    sections.set_defaults(func=list_sections)

    edit = subparsers.add_parser("edit-section", help="Apply a structured section edit and record a revision.")
    edit.add_argument("--project-dir", default=".", help="Website project directory.")
    edit.add_argument("--section", required=True, help="Section id/name such as top, services, process, contact.")
    edit.add_argument("--heading", default="", help="Replacement H1/H2 text for the section.")
    edit.add_argument("--body", default="", help="Replacement first paragraph text for the section.")
    edit.add_argument("--cta", default="", help="Replacement first link/button text for the section.")
    edit.add_argument("--request", default="", help="Original natural-language edit request for history.")
    edit.set_defaults(func=edit_section)

    style = subparsers.add_parser("change-style", help="Apply a core color style change and record a revision.")
    style.add_argument("--project-dir", default=".", help="Website project directory.")
    style.add_argument("--preset", choices=("professional", "luxury", "modern", "warm"), default="professional")
    style.add_argument("--accent", default="", help="Override accent color, for example #2563eb.")
    style.add_argument("--ink", default="", help="Override primary text color.")
    style.add_argument("--surface", default="", help="Override page surface color.")
    style.set_defaults(func=change_style)

    qa = subparsers.add_parser("qa", help="Run website QA checks and record the report.")
    qa.add_argument("--project-dir", default=".", help="Website project directory.")
    qa.add_argument("--run-build", action="store_true", help="Run npm run build for Node/Next.js projects.")
    qa.add_argument("--build-timeout", type=int, default=120)
    qa.set_defaults(func=run_qa)

    visual = subparsers.add_parser("visual-qa", help="Run visual/responsive QA checks and optional screenshots.")
    visual.add_argument("--project-dir", default=".", help="Website project directory.")
    visual.add_argument("--screenshots", action="store_true", help="Capture desktop/mobile screenshots when Playwright is installed.")
    visual.add_argument("--url", default="", help="Preview URL for screenshot capture.")
    visual.add_argument("--output-dir", default="", help="Screenshot output directory.")
    visual.set_defaults(func=visual_qa)

    summary = subparsers.add_parser("summary", help="Return a Discord-friendly website project status summary.")
    summary.add_argument("--project-dir", default=".", help="Website project directory.")
    summary.set_defaults(func=status_summary)

    share = subparsers.add_parser("preview-share", help="Create a shareable preview URL, preferring Hermes proxy.")
    share.add_argument("--project-dir", default=".", help="Website project directory.")
    share.add_argument("--port", type=int, default=DEFAULT_PORT)
    share.add_argument("--prefer", choices=("auto", "hermesproxy", "sitelet"), default="hermesproxy")
    share.add_argument("--fallback", choices=("auto", "sitelet", "none"), default="auto")
    share.add_argument("--site", help="Hermes proxy site name.")
    share.add_argument("--title", help="Sitelet preview title.")
    share.add_argument("--proxy-base-url", default=os.getenv("HERMES_PROXY_BASE_URL", ""))
    share.add_argument("--proxy-token", default=os.getenv("HERMES_PROXY_TOKEN", ""))
    share.add_argument("--sitelet-base-url", default=os.getenv("SITELET_BASE_URL", ""))
    share.add_argument("--sitelet-api-token", default=os.getenv("SITELET_API_TOKEN", ""))
    share.add_argument("--wait-seconds", type=float, default=8)
    share.add_argument("--no-start-local", dest="start_local", action="store_false")
    share.add_argument("--log-file", help="Local preview server log file.")
    share.set_defaults(func=preview_share, start_local=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = args.func(args)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
