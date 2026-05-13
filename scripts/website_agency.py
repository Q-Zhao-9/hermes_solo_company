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
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_PORT = 3010
STATE_PATH = Path("docs") / "hermes-website-state.json"
DEPLOY_DIR = Path("dist") / "hermes-deploy"


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


def record_revision(project_dir: Path, revision: dict[str, Any]) -> None:
    state_file = project_dir / STATE_PATH
    state = read_state(state_file)
    revisions = state.setdefault("revisions", [])
    record = dict(revision)
    record["createdAt"] = datetime.now(timezone.utc).isoformat()
    revisions.append(record)
    state["lastRevision"] = record
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

    deploy = subparsers.add_parser("deploy-prep", help="Prepare deployment artifacts and notes.")
    deploy.add_argument("--project-dir", default=".", help="Website project directory.")
    deploy.add_argument(
        "--target",
        choices=("auto", "static-zip", "vercel", "netlify", "github-pages"),
        default="auto",
        help="Deployment target to prepare.",
    )
    deploy.set_defaults(func=deploy_prep)

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
