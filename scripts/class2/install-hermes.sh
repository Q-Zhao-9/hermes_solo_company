#!/usr/bin/env bash
# AI Solo Company Class 2: install the class edition of Hermes on Ubuntu/WSL or macOS.
set -Eeuo pipefail

REPO_URL="${HERMES_CLASS_REPO_URL:-https://github.com/Easiio-Inc/hermes_solo_company.git}"
BRANCH="${HERMES_CLASS_BRANCH:-main}"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
INSTALL_DIR="${HERMES_INSTALL_DIR:-$HERMES_HOME/hermes-agent}"
CHECK_ONLY=false
SKIP_SETUP=false

for arg in "$@"; do
  case "$arg" in
    --check) CHECK_ONLY=true ;;
    --skip-setup) SKIP_SETUP=true ;;
    -h|--help)
      printf '%s\n' "Usage: install-hermes.sh [--check] [--skip-setup]"
      exit 0
      ;;
    *) printf 'Unknown option: %s\n' "$arg" >&2; exit 2 ;;
  esac
done

info() { printf '\033[36m[Class 2]\033[0m %s\n' "$*"; }
ok() { printf '\033[32m[OK]\033[0m %s\n' "$*"; }
fail() { printf '\033[31m[ERROR]\033[0m %s\n' "$*" >&2; exit 1; }

case "$(uname -s)" in
  Linux) PLATFORM="linux" ;;
  Darwin) PLATFORM="macos" ;;
  *) fail "This installer supports Ubuntu/WSL and macOS only." ;;
esac

if [ "$PLATFORM" = "linux" ] && [ -r /etc/os-release ]; then
  # shellcheck disable=SC1091
  . /etc/os-release
  if [ "${ID:-}" != "ubuntu" ]; then
    info "Linux detected (${PRETTY_NAME:-unknown}). Ubuntu 24.04 is recommended."
  elif [ "${VERSION_ID:-}" != "24.04" ]; then
    info "Ubuntu ${VERSION_ID:-unknown} detected. The class recommends Ubuntu 24.04."
  fi
fi

if [ "$CHECK_ONLY" = true ]; then
  command -v git >/dev/null || fail "git is missing"
  command -v curl >/dev/null || fail "curl is missing"
  git ls-remote "$REPO_URL" HEAD >/dev/null || fail "Cannot reach $REPO_URL"
  ok "Platform and repository checks passed ($PLATFORM)."
  exit 0
fi

info "Preparing this computer..."
if [ "$PLATFORM" = "linux" ]; then
  if ! command -v sudo >/dev/null; then
    fail "sudo is required. On Windows, open Ubuntu 24.04 once and create your Linux username first."
  fi
  sudo apt-get update
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y git curl ca-certificates build-essential python3-dev libffi-dev
else
  if ! command -v xcode-select >/dev/null || ! xcode-select -p >/dev/null 2>&1; then
    info "macOS will ask you to install Apple's Command Line Tools. Complete that window, then run this installer again."
    xcode-select --install || true
    exit 0
  fi
  command -v git >/dev/null || fail "git is unavailable after Command Line Tools setup."
  command -v curl >/dev/null || fail "curl is unavailable."
fi

mkdir -p "$HERMES_HOME"
if [ -d "$INSTALL_DIR/.git" ]; then
  CURRENT_ORIGIN="$(git -C "$INSTALL_DIR" remote get-url origin 2>/dev/null || true)"
  case "$CURRENT_ORIGIN" in
    *Easiio-Inc/hermes_solo_company.git) info "Existing class installation found; it will be updated." ;;
    *) fail "$INSTALL_DIR already contains another Git repository. Move it aside, then run this installer again." ;;
  esac
elif [ -e "$INSTALL_DIR" ]; then
  fail "$INSTALL_DIR exists but is not a Git repository. Move it aside, then run this installer again."
else
  info "Downloading the AI Solo Company Hermes repository..."
  git clone --branch "$BRANCH" --depth 1 "$REPO_URL" "$INSTALL_DIR"
fi

INSTALL_ARGS=(--branch "$BRANCH" --dir "$INSTALL_DIR" --hermes-home "$HERMES_HOME")
if [ "$SKIP_SETUP" = true ]; then
  INSTALL_ARGS+=(--skip-setup)
fi

info "Installing Hermes. This can take several minutes..."
bash "$INSTALL_DIR/scripts/install.sh" "${INSTALL_ARGS[@]}"

export PATH="$HOME/.local/bin:$PATH"
if ! command -v hermes >/dev/null; then
  fail "Installation finished, but the hermes command was not found. Open a new terminal and run: hermes doctor"
fi

hermes --version
ok "Hermes is installed."
printf '\nNext class steps:\n'
printf '  1. If setup did not run, enter: hermes setup\n'
printf '  2. Check the installation: hermes doctor\n'
printf '  3. Start Hermes: hermes\n'
printf '  4. Ask: Create a simple one-page website for my solo company.\n'
