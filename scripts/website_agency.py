#!/usr/bin/env python3
"""Deterministic helpers for Hermes website agency workflows.

This script gives the website-builder skills a reliable execution layer for
the first MVP platforms: static HTML and Next.js. It avoids network access and
does not install dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_PORT = 3010


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

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = args.func(args)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
