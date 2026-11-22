#!/usr/bin/env bash
# Install every skill in this repo into the user Cursor skills directory.
# Run on macOS/Linux. Idempotent — re-run to refresh after git pull.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SRC="${LOGIC_PRO_MCP_SKILLS_SRC:-$REPO_ROOT/.cursor/skills}"
SKILLS_DEST="${CURSOR_SKILLS_DEST:-$HOME/.cursor/skills}"
AGENT_STORE="${CURSOR_AGENT_STORE_SKILLS:-}"
DRY_RUN=0
REGENERATE=1

usage() {
  cat <<'EOF'
Usage: install-cursor-skills.sh [--dry-run] [--no-regenerate]

  --dry-run        Print actions only
  --no-regenerate  Skip Scripts/generate-workflow-cursor-skills.py

Environment:
  CURSOR_SKILLS_DEST            default ~/.cursor/skills
  CURSOR_AGENT_STORE_SKILLS     optional extra skills tree (e.g. Agent Store mount)
  LOGIC_PRO_MCP_SKILLS_SRC      default <repo>/.cursor/skills
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --no-regenerate) REGENERATE=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

log() { printf '%s\n' "$*"; }

if [[ "$REGENERATE" -eq 1 && -f "$REPO_ROOT/Scripts/generate-workflow-cursor-skills.py" ]]; then
  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "Would run: python3 $REPO_ROOT/Scripts/generate-workflow-cursor-skills.py"
  else
    python3 "$REPO_ROOT/Scripts/generate-workflow-cursor-skills.py"
  fi
fi

if [[ ! -d "$SKILLS_SRC" ]]; then
  echo "ERROR: skills source missing: $SKILLS_SRC" >&2
  exit 1
fi

install_tree() {
  local src="$1"
  local label="$2"
  shopt -s nullglob
  local dirs=("$src"/*/)
  shopt -u nullglob
  if [[ ${#dirs[@]} -eq 0 ]]; then
    log "No skill folders under $src ($label)"
    return 0
  fi
  for dir in "${dirs[@]}"; do
    [[ -f "${dir}SKILL.md" ]] || continue
    local name
    name="$(basename "$dir")"
    if [[ "$DRY_RUN" -eq 1 ]]; then
      log "Would install skill: $name ($label) -> $SKILLS_DEST/$name"
    else
      mkdir -p "$SKILLS_DEST/$name"
      if command -v rsync >/dev/null 2>&1; then
        rsync -a --exclude '.git' "${dir%/}/" "$SKILLS_DEST/$name/"
      else
        rm -rf "$SKILLS_DEST/$name"
        mkdir -p "$SKILLS_DEST/$name"
        cp -a "${dir%/}/." "$SKILLS_DEST/$name/"
      fi
      log "Installed skill: $name ($label)"
    fi
  done
}

if [[ "$DRY_RUN" -eq 1 ]]; then
  log "Would mkdir -p $SKILLS_DEST"
else
  mkdir -p "$SKILLS_DEST"
fi

install_tree "$SKILLS_SRC" "repo"

if [[ -n "$AGENT_STORE" && -d "$AGENT_STORE" ]]; then
  install_tree "$AGENT_STORE" "agent-store"
elif [[ -n "$AGENT_STORE" ]]; then
  log "WARN: CURSOR_AGENT_STORE_SKILLS set but not a directory: $AGENT_STORE"
fi

log ""
log "Cursor skills destination: $SKILLS_DEST"
log "Restart Cursor or open a new Agent chat so skill changes load."