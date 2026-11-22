#!/usr/bin/env bash
# One-shot: balance Logic mix + vocal pitch correction on the Mac Studio.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
[[ "$(uname -s)" == "Darwin" ]] || { echo "Run on macOS only." >&2; exit 1; }
export LOGIC_PRO_MCP_BIN="${LOGIC_PRO_MCP_BIN:-$HOME/.local/bin/LogicProMCP}"
open -a "Logic Pro" 2>/dev/null || open -a "Logic Pro Creator Studio" 2>/dev/null || true
sleep 2
exec python3 "$ROOT/Scripts/mac_balance_mix_tune_vocals.py" "$@"