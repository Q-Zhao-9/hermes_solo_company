# Easiio Reusable Modules

This directory contains source-only copies of reusable Easiio modules that students or operators can install into a local Hermes tools directory after pulling this repository.

## Included modules

```text
modules/
  solo_crm/              Lightweight SQLite CRM and MCP server
  website_chatbot/       Embeddable AI chatbot, RAG backend, admin customizer, WordPress plugin source
  easiio_docs_module/    Reusable docs / knowledge-base / RAG module with frontend, backend, Sitelet, WordPress, and export adapters
```

## Install into local Hermes tools and skills

From the repository root:

```bash
scripts/install_easiio_modules.sh
```

Default install targets:

```text
${HERMES_HOME:-$HOME/.hermes}/tools
${HERMES_HOME:-$HOME/.hermes}/skills
```

The installer copies both reusable tools under `modules/` and Easiio-specific skills under `skills/`, including the Class 4 Skill Studio skills.

Dry run first:

```bash
scripts/install_easiio_modules.sh --dry-run
```

Install only one module:

```bash
scripts/install_easiio_modules.sh --module website_chatbot
```

Install only one skill:

```bash
scripts/install_easiio_modules.sh --skill class4/student-lead-followup
```

Install modules only, without skills:

```bash
scripts/install_easiio_modules.sh --no-skills
```

Install to custom target directories:

```bash
scripts/install_easiio_modules.sh --target /path/to/hermes/tools --skills-target /path/to/hermes/skills
```

## Safety rules

The installer copies **source files only** and excludes local/runtime/private artifacts such as:

```text
*.db
*.sqlite
*.env
data/
dist/
__pycache__/
.pytest_cache/
*.pyc
*.zip
uploaded files
```

If a target module directory already exists, the script creates a timestamped source backup before syncing unless `--no-backup` is used.

## After install

Restart or reload Hermes if you want newly installed MCP tools to be discovered.

For Solo CRM MCP, the local server entrypoint should be:

```text
~/.hermes/tools/solo_crm/server.py
```

Example Hermes MCP config shape:

```yaml
mcp_servers:
  solo_crm:
    command: python3
    args:
      - /home/<user>/.hermes/tools/solo_crm/server.py
    timeout: 60
    connect_timeout: 30
```

Do not commit local databases, admin env files, uploaded/downloaded content, API keys, SMTP/Brevo credentials, or student/user data.
