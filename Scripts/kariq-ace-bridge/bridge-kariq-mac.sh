#!/usr/bin/env bash
# KARIQ Logic → ACE Studio transfer. Darwin / ACE Studio only.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "ERROR: bridge-kariq-mac.sh must run on ROLAND's Mac Studio (Darwin)." >&2
  echo "This host is $(uname -s) $(hostname)." >&2
  exit 2
fi

ACE_CLI="${ACE_CLI:-/Applications/ACE Studio.app/Contents/Helpers/acestudio-cli}"
ACE_MCP="${ACE_MCP:-/Applications/ACE Studio.app/Contents/Helpers/ace-mcp-server}"
WORK="${KARIQ_BRIDGE_DIR:-$HOME/Music/ACE Studio/KARIQ-bridge}"
SAVE="${KARIQ_ACE_SAVE:-$HOME/Music/ACE Studio/KARIQ}"

mkdir -p "$WORK" "$SAVE"

open -a "ACE Studio" 2>/dev/null || true
open -a "Logic Pro" 2>/dev/null || open -a "Logic Pro X" 2>/dev/null || true

copy_bounce() {
  local src="$1"
  if [[ -f "$src" ]]; then
    cp -n "$src" "$WORK/" && echo "copied $src"
  fi
}

copy_bounce "$HOME/Music/Logic/Bounces/KARIQ-mix-final.aif"
copy_bounce "$HOME/Music/Logic/Bounces/KARIQ-mix-listen.aif"
copy_bounce "$HOME/Music/Logic/Bounces/KARIQ-vocals-cleaned.aif"
# Catch renamed/dated bounces without overwriting.
shopt -s nullglob
for f in "$HOME/Music/Logic/Bounces/"*KARIQ* "$HOME/Music/Logic/Bounces/"*kariq*; do
  copy_bounce "$f" || true
done
shopt -u nullglob

if [[ -x "$ACE_CLI" ]]; then
  echo "==> ACE CLI help"
  "$ACE_CLI" --help 2>&1 | head -80 || true
  echo "==> ACE app status"
  "$ACE_CLI" app status || true
else
  echo "WARN: missing $ACE_CLI" >&2
fi

if [[ -d "$HOME/Projects/ace-mcp" && -x "$HOME/Projects/ace-mcp/scripts/check-bridge-environment.sh" ]]; then
  echo "==> ACE Bridge 2 environment"
  bash "$HOME/Projects/ace-mcp/scripts/check-bridge-environment.sh" || true
fi

exec python3 "$ROOT/Scripts/kariq-ace-bridge/bridge_kariq.py" \
  --work-dir "$WORK" \
  --save-dir "$SAVE" \
  --cli "$ACE_CLI" \
  --mcp "$ACE_MCP" \
  "$@"
