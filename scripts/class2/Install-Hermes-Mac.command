#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
clear
printf '\nAI Solo Company Class 2 - Hermes Installer for macOS\n\n'
bash "$SCRIPT_DIR/install-hermes.sh"
printf '\nInstallation window can now be closed.\n'
read -r -p "Press Enter to close..." _
