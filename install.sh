#!/usr/bin/env bash
# install.sh — installs the acm-debug skill into a project or globally
# Usage:
#   ./install.sh              → installs to current project (.claude/commands/)
#   ./install.sh --global     → installs to user global (~/.claude/commands/)
#   ./install.sh --project /path/to/project  → installs to a specific project

set -euo pipefail

SKILL_FILE="commands/debug.md"
COMMAND_NAME="debug.md"
GLOBAL=false
TARGET_DIR=""

print_usage() {
  echo "Usage:"
  echo "  ./install.sh                        Install to current project"
  echo "  ./install.sh --global               Install globally (~/.claude/commands/)"
  echo "  ./install.sh --project <path>       Install to a specific project directory"
}

for arg in "$@"; do
  case $arg in
    --global)
      GLOBAL=true
      ;;
    --project)
      TARGET_DIR="${2:-}"
      shift
      ;;
    --help|-h)
      print_usage
      exit 0
      ;;
    *)
      ;;
  esac
done

# Resolve destination
if [ "$GLOBAL" = true ]; then
  DEST="$HOME/.claude/commands"
elif [ -n "$TARGET_DIR" ]; then
  DEST="$TARGET_DIR/.claude/commands"
else
  DEST="$(pwd)/.claude/commands"
fi

# Check source file exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$SCRIPT_DIR/$SKILL_FILE"

if [ ! -f "$SRC" ]; then
  echo "Error: skill file not found at $SRC"
  echo "Make sure you are running this script from the acm-debug repository root."
  exit 1
fi

# Create destination and copy
mkdir -p "$DEST"
cp "$SRC" "$DEST/$COMMAND_NAME"

echo ""
echo "  acm-debug skill installed successfully!"
echo ""
echo "  Location : $DEST/$COMMAND_NAME"
echo ""
echo "  Usage:"
echo "    /debug src/app.py           Full debug report for a file"
echo "    /debug src/app.py --fix     Debug and auto-apply critical fixes"
echo "    /debug src/app.py --quick   Critical and logic errors only"
echo ""
