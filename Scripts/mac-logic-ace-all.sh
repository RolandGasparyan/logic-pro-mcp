#!/usr/bin/env bash
# Logic Pro MCP + ACE Studio + studio-remote — one shot on macOS (not Linux cloud).
set -euo pipefail

LOGIC_REPO_URL="${LOGIC_PRO_MCP_GIT_URL:-https://github.com/RolandGasparyan/logic-pro-mcp.git}"
LOGIC_DEST="${LOGIC_PRO_MCP_SOURCE:-$HOME/logic-pro-mcp}"
ACE_GIT_URL="${ACE_MCP_GIT_URL:-https://origin.cursor.com/git/roland-gasparyan/ace-mcp.git}"
ACE_DEST="${ACE_MCP_SOURCE:-$HOME/Projects/ace-mcp}"
WORKER_NAME="${CURSOR_WORKER_NAME:-Rolands-Mac-Studio}"

log() { printf '\n== %s ==\n' "$*"; }

[[ "$(uname -s)" == "Darwin" ]] || {
  echo "Run on macOS only." >&2
  exit 1
}

export PATH="$HOME/.local/bin:$PATH"

ensure_ace_repo() {
  if [[ -d "$ACE_DEST/.git" ]]; then
  :
  elif [[ -d "$HOME/ace-mcp/.git" ]]; then
    ACE_DEST="$HOME/ace-mcp"
  else
    log "Cloning ace-mcp → $ACE_DEST"
    mkdir -p "$(dirname "$ACE_DEST")"
    if ! git clone "$ACE_GIT_URL" "$ACE_DEST" 2>/dev/null; then
      log "Origin clone failed; trying shallow fetch or use: export ACE_MCP_SOURCE=/path/to/ace-mcp"
      [[ -d "$ACE_DEST" ]] || {
        echo "Could not clone ace-mcp. Install Origin CLI or set ACE_MCP_SOURCE." >&2
        exit 1
      }
    fi
  fi
  cd "$ACE_DEST"
  if git remote get-url origin 2>/dev/null | grep -q '^git@'; then
    git remote set-url origin "$ACE_GIT_URL" || true
  fi
  git pull --ff-only 2>/dev/null || true
}

run_logic_bootstrap() {
  if [[ -x "$LOGIC_DEST/Scripts/mac-bootstrap-all.sh" ]]; then
    bash "$LOGIC_DEST/Scripts/mac-bootstrap-all.sh"
    return 0
  fi
  log "Logic bootstrap script missing; running mac-full-mcp-connect if present"
  if [[ -x "$LOGIC_DEST/Scripts/mac-full-mcp-connect.sh" ]]; then
    bash "$LOGIC_DEST/Scripts/mac-full-mcp-connect.sh"
  else
    log "Clone logic-pro-mcp first: git clone $LOGIC_REPO_URL $LOGIC_DEST"
    git clone "$LOGIC_REPO_URL" "$LOGIC_DEST"
    bash "$LOGIC_DEST/Scripts/mac-bootstrap-all.sh"
  fi
}

main() {
  if [[ ! -d "$LOGIC_DEST/.git" ]]; then
    git clone "$LOGIC_REPO_URL" "$LOGIC_DEST"
  fi
  cd "$LOGIC_DEST"
  git remote set-url origin "$LOGIC_REPO_URL" 2>/dev/null || true
  git pull --ff-only origin main 2>/dev/null || true
  run_logic_bootstrap
  ensure_ace_repo
  log "ACE Studio + studio-remote (opens ACE + Logic, writes ~/.cursor/mcp.json)"
  bash "$ACE_DEST/scripts/go-mac.sh"
  log "Cloud agent on this Mac (keep Terminal open; repo = ace-mcp):"
  printf '  export PATH="$HOME/.local/bin:$PATH"\n'
  printf '  agent login\n'
  printf '  cd %q\n' "$ACE_DEST"
  printf '  agent worker --computer-use --name %q start\n' "$WORKER_NAME"
  log "In Cursor: Settings → MCP → reload ace-studio + studio-remote + logic-pro"
  log "Then ask: Check studio health, then play ACE and Logic together."
}

main "$@"