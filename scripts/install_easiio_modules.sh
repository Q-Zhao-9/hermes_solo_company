#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Install Easiio reusable modules from this repository into a local Hermes tools directory.

Usage:
  scripts/install_easiio_modules.sh [options]

Options:
  --module NAME       Install only one module: solo_crm, website_chatbot, or easiio_docs_module.
                      Can be passed multiple times. Default: install all modules.
  --skill PATH        Install only one skill path under skills/, for example class4/student-lead-followup.
                      Can be passed multiple times. Default: install all repo-provided Easiio skills.
  --no-skills         Install modules only; skip skills/.
  --target DIR        Hermes tools directory. Default: ${HERMES_HOME:-$HOME/.hermes}/tools
  --skills-target DIR Hermes skills directory. Default: ${HERMES_HOME:-$HOME/.hermes}/skills
  --dry-run           Show what would be copied without changing files.
  --no-backup         Do not create timestamped backups of existing target source files.
  --help              Show this help.

Examples:
  scripts/install_easiio_modules.sh
  scripts/install_easiio_modules.sh --dry-run
  scripts/install_easiio_modules.sh --module website_chatbot --target ~/.hermes/tools
  scripts/install_easiio_modules.sh --skill class4/student-lead-followup --skills-target ~/.hermes/skills

Safety:
  - Copies source files from modules/<name>/ to the target tools directory.
  - Copies reusable skill source from skills/<path>/ to the target skills directory.
  - Preserves local runtime data and secrets by excluding data/, *.db, *.env, dist/, caches, uploads, and generated artifacts.
  - Existing target directories are backed up before update unless --no-backup is used.
USAGE
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_ROOT="$REPO_ROOT/modules"
SKILLS_SOURCE_ROOT="$REPO_ROOT/skills"
TARGET_ROOT="${HERMES_HOME:-$HOME/.hermes}/tools"
SKILLS_TARGET_ROOT="${HERMES_HOME:-$HOME/.hermes}/skills"
DRY_RUN=0
BACKUP=1
INSTALL_SKILLS=1
MODULES=()
SKILLS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --module)
      [[ $# -ge 2 ]] || { echo "ERROR: --module requires a value" >&2; exit 2; }
      MODULES+=("$2")
      shift 2
      ;;
    --skill)
      [[ $# -ge 2 ]] || { echo "ERROR: --skill requires a value" >&2; exit 2; }
      SKILLS+=("$2")
      shift 2
      ;;
    --no-skills)
      INSTALL_SKILLS=0
      shift
      ;;
    --target)
      [[ $# -ge 2 ]] || { echo "ERROR: --target requires a value" >&2; exit 2; }
      TARGET_ROOT="$2"
      shift 2
      ;;
    --skills-target)
      [[ $# -ge 2 ]] || { echo "ERROR: --skills-target requires a value" >&2; exit 2; }
      SKILLS_TARGET_ROOT="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --no-backup)
      BACKUP=0
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ${#MODULES[@]} -eq 0 ]]; then
  MODULES=(solo_crm website_chatbot easiio_docs_module)
fi

if [[ "$INSTALL_SKILLS" -eq 1 && ${#SKILLS[@]} -eq 0 ]]; then
  SKILLS=(
    class4/class-skill-studio-implementation
    class4/student-lead-followup
    web-development/website-chatbot-solo-crm
    web-development/website-wiki-module
  )
fi

VALID_MODULES=" solo_crm website_chatbot easiio_docs_module "
for module in "${MODULES[@]}"; do
  if [[ "$VALID_MODULES" != *" $module "* ]]; then
    echo "ERROR: unsupported module '$module'" >&2
    exit 2
  fi
  if [[ ! -d "$SOURCE_ROOT/$module" ]]; then
    echo "ERROR: source module missing: $SOURCE_ROOT/$module" >&2
    exit 1
  fi
done

if [[ "$INSTALL_SKILLS" -eq 1 ]]; then
  for skill in "${SKILLS[@]}"; do
    if [[ "$skill" == /* || "$skill" == *".."* || "$skill" != */* ]]; then
      echo "ERROR: invalid skill path '$skill'" >&2
      exit 2
    fi
    if [[ ! -d "$SKILLS_SOURCE_ROOT/$skill" ]]; then
      echo "ERROR: source skill missing: $SKILLS_SOURCE_ROOT/$skill" >&2
      exit 1
    fi
    if [[ ! -f "$SKILLS_SOURCE_ROOT/$skill/SKILL.md" ]]; then
      echo "ERROR: skill is missing SKILL.md: $SKILLS_SOURCE_ROOT/$skill" >&2
      exit 1
    fi
  done
fi

RSYNC_EXCLUDES=(
  "--exclude=__pycache__/"
  "--exclude=.pytest_cache/"
  "--exclude=*.pyc"
  "--exclude=*.pyo"
  "--exclude=*.db"
  "--exclude=*.sqlite"
  "--exclude=*.sqlite3"
  "--exclude=*.env"
  "--exclude=.env"
  "--exclude=.env.*"
  "--exclude=data/"
  "--exclude=dist/"
  "--exclude=*.zip"
  "--exclude=*.pdf"
  "--exclude=*.bak"
  "--exclude=*.bak-*"
)

if ! command -v rsync >/dev/null 2>&1; then
  echo "ERROR: rsync is required for safe source-only sync." >&2
  exit 1
fi

mkdir_cmd=(mkdir -p "$TARGET_ROOT" "$SKILLS_TARGET_ROOT")
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "DRY RUN: ${mkdir_cmd[*]}"
else
  "${mkdir_cmd[@]}"
fi

STAMP="$(date +%Y%m%d%H%M%S)"
for module in "${MODULES[@]}"; do
  src="$SOURCE_ROOT/$module/"
  dest="$TARGET_ROOT/$module"
  echo "==> Installing $module"
  echo "    source: $src"
  echo "    target: $dest"

  if [[ -d "$dest" && "$BACKUP" -eq 1 ]]; then
    backup="$TARGET_ROOT/${module}.source-backup.$STAMP"
    if [[ "$DRY_RUN" -eq 1 ]]; then
      echo "DRY RUN: create source backup at $backup"
    else
      mkdir -p "$backup"
      rsync -a "${RSYNC_EXCLUDES[@]}" "$dest/" "$backup/"
      echo "    backup: $backup"
    fi
  fi

  rsync_cmd=(rsync -a --delete "${RSYNC_EXCLUDES[@]}" "$src" "$dest/")
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "DRY RUN: ${rsync_cmd[*]}"
  else
    mkdir -p "$dest"
    "${rsync_cmd[@]}"
    mkdir -p "$dest/data"
  fi

done

if [[ "$INSTALL_SKILLS" -eq 1 ]]; then
  for skill in "${SKILLS[@]}"; do
    src="$SKILLS_SOURCE_ROOT/$skill/"
    dest="$SKILLS_TARGET_ROOT/$skill"
    echo "==> Installing skill $skill"
    echo "    source: $src"
    echo "    target: $dest"

    if [[ -d "$dest" && "$BACKUP" -eq 1 ]]; then
      backup="$SKILLS_TARGET_ROOT/${skill}.source-backup.$STAMP"
      if [[ "$DRY_RUN" -eq 1 ]]; then
        echo "DRY RUN: create skill backup at $backup"
      else
        mkdir -p "$backup"
        rsync -a "${RSYNC_EXCLUDES[@]}" "$dest/" "$backup/"
        echo "    backup: $backup"
      fi
    fi

    rsync_cmd=(rsync -a --delete "${RSYNC_EXCLUDES[@]}" "$src" "$dest/")
    if [[ "$DRY_RUN" -eq 1 ]]; then
      echo "DRY RUN: ${rsync_cmd[*]}"
    else
      mkdir -p "$dest"
      "${rsync_cmd[@]}"
    fi
  done
fi

cat <<EOF

Install complete.

Target tools directory:
  $TARGET_ROOT

Target skills directory:
  $SKILLS_TARGET_ROOT

Installed modules:
$(printf '  - %s\n' "${MODULES[@]}")

Installed skills:
$(if [[ "$INSTALL_SKILLS" -eq 1 ]]; then printf '  - %s\n' "${SKILLS[@]}"; else printf '  - skipped\n'; fi)

Notes:
  - Runtime databases, .env files, data stores, uploads, packaged zips, and caches were not copied.
  - If Hermes is already running, restart/reload Hermes so MCP/tool and skill changes are discovered.
  - Solo CRM MCP config may need to point at:
      $TARGET_ROOT/solo_crm/server.py
EOF
