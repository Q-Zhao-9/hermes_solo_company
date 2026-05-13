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
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_PORT = 3010
STATE_PATH = Path("docs") / "hermes-website-state.json"


@dataclass(frozen=True)
class SiteSpec:
    name: str
    description: str
    audience: str
    goal: str
    tone: str
    platform: str
    slug: str


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


def build_spec(args: argparse.Namespace) -> SiteSpec:
    name = args.name.strip()
    description = args.description.strip()
    platform = choose_platform(args.platform, description)
    return SiteSpec(
        name=name,
        description=description,
        audience=args.audience.strip(),
        goal=args.goal.strip(),
        tone=args.tone.strip(),
        platform=platform,
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

    record_project_created(root, spec)
    preview = preview_plan(root, port=args.port)
    return {
        "ok": True,
        "projectDir": str(root),
        "platform": spec.platform,
        "slug": spec.slug,
        "files": sorted(str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()),
        "preview": preview,
        "nextSteps": [
            f"cd {root}",
            preview["command"],
            "Use the preview URL to review the first draft.",
        ],
    }


def write_project_docs(root: Path, spec: SiteSpec) -> None:
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
          <p class="eyebrow">{escape_html(spec.tone)} website experience</p>
          <h1>{escape_html(spec.name)} helps {escape_html(spec.audience)} move faster.</h1>
          <p>{escape_html(spec.description)}</p>
          <a class="button" href="#contact">{escape_html(spec.goal)}</a>
        </div>
      </section>

      <section class="proof" aria-label="Key strengths">
        <span>Clear strategy</span>
        <span>Responsive design</span>
        <span>SEO-ready content</span>
      </section>

      <section id="services" class="section">
        <p class="eyebrow">Capabilities</p>
        <h2>Built around the customer journey</h2>
        <div class="grid">
          <article>
            <h3>Positioning</h3>
            <p>Translate the business value into a focused message visitors can understand quickly.</p>
          </article>
          <article>
            <h3>Conversion</h3>
            <p>Place calls to action, trust points, and service details where they support decisions.</p>
          </article>
          <article>
            <h3>Launch Ready</h3>
            <p>Prepare clean files, metadata, and a preview path before publishing.</p>
          </article>
        </div>
      </section>

      <section id="process" class="section band">
        <p class="eyebrow">Process</p>
        <h2>A simple path from idea to preview</h2>
        <ol>
          <li>Clarify the brief and sitemap.</li>
          <li>Create the design and content system.</li>
          <li>Build, preview, QA, and revise.</li>
        </ol>
      </section>

      <section id="contact" class="section cta">
        <p class="eyebrow">Next step</p>
        <h2>Ready to review the first version?</h2>
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


def write_nextjs_project(root: Path, spec: SiteSpec) -> None:
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
        f"""const capabilities = ["Positioning", "Conversion", "Launch Ready"];

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
        <p className="eyebrow">{escape_js(spec.tone)} website experience</p>
        <h1>{escape_js(spec.name)} helps {escape_js(spec.audience)} move faster.</h1>
        <p>{escape_js(spec.description)}</p>
        <a className="button" href="#contact">{escape_js(spec.goal)}</a>
      </section>

      <section id="services" className="section">
        <p className="eyebrow">Capabilities</p>
        <h2>Built around the customer journey</h2>
        <div className="grid">
          {{capabilities.map((item) => (
            <article key={{item}}>
              <h3>{{item}}</h3>
              <p>Clear structure, conversion-focused copy, and responsive implementation for the first preview.</p>
            </article>
          ))}}
        </div>
      </section>

      <section id="process" className="section band">
        <p className="eyebrow">Process</p>
        <h2>A simple path from idea to preview</h2>
        <ol>
          <li>Clarify the brief and sitemap.</li>
          <li>Create the design and content system.</li>
          <li>Build, preview, QA, and revise.</li>
        </ol>
      </section>

      <section id="contact" className="section cta">
        <p className="eyebrow">Next step</p>
        <h2>Ready to review the first version?</h2>
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
    write_text(state_file, json.dumps(state, indent=2))


def record_project_created(project_dir: Path, spec: SiteSpec) -> None:
    state_file = project_dir / STATE_PATH
    state = read_state(state_file)
    state["project"] = {
        "name": spec.name,
        "description": spec.description,
        "audience": spec.audience,
        "goal": spec.goal,
        "tone": spec.tone,
        "platform": spec.platform,
        "slug": spec.slug,
        "createdAt": state.get("project", {}).get("createdAt") or datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }
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
    create.add_argument("--output-dir", default="generated-sites", help="Directory where the site folder is created.")
    create.add_argument("--port", type=int, default=DEFAULT_PORT)
    create.add_argument("--force", action="store_true", help="Update files if the output project already exists.")
    create.set_defaults(func=create_site)

    preview = subparsers.add_parser("build-preview", help="Create or start a preview plan for a website project.")
    preview.add_argument("--project-dir", default=".", help="Website project directory.")
    preview.add_argument("--port", type=int, default=DEFAULT_PORT)
    preview.add_argument("--start", action="store_true", help="Start the preview process in the background.")
    preview.add_argument("--log-file", help="Log file for --start.")
    preview.set_defaults(func=build_preview)

    qa = subparsers.add_parser("qa", help="Run website QA checks and record the report.")
    qa.add_argument("--project-dir", default=".", help="Website project directory.")
    qa.add_argument("--run-build", action="store_true", help="Run npm run build for Node/Next.js projects.")
    qa.add_argument("--build-timeout", type=int, default=120)
    qa.set_defaults(func=run_qa)

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
