#!/usr/bin/env bash
# Export this repo's Graphify graph into the Obsidian second brain.
# Cursor stop hooks pass JSON on stdin. Missing CLI or vault is a no-op.
cat >/dev/null || true

if ! command -v graphify >/dev/null 2>&1; then
  printf '{}\n'
  exit 0
fi

VAULT="${GRAPHIFY_OBSIDIAN_VAULT:-$HOME/Obsidian_Second_Brain}"
if [[ ! -d "$VAULT" ]]; then
  printf '{}\n'
  exit 0
fi

ROOT="${CURSOR_PROJECT_DIR:-}"
if [[ -z "$ROOT" ]]; then
  ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi
cd "$ROOT" || { printf '{}\n'; exit 0; }

case "$ROOT" in
  "$VAULT"|"$VAULT"/*)
    printf '{}\n'
    exit 0
    ;;
esac

NAME="$(basename "$ROOT")"
LOG="${TMPDIR:-/tmp}/graphify-brain-sync.log"
mkdir -p graphify-out

HEAD="$(git rev-parse HEAD 2>/dev/null || echo nogit)"
STAMP="graphify-out/.brain-sync-rev"
DIRTY=0
if git status --porcelain 2>/dev/null | grep -E '\.(py|ts|tsx|js|jsx|mjs|cjs|go|rs|swift|kt|kts|java|rb|php|cs|cpp|cc|c|h|hpp|sql|vue|svelte)$' >/dev/null; then
  DIRTY=1
fi

NEED=0
if [[ ! -f graphify-out/graph.json ]]; then
  NEED=1
elif [[ "$DIRTY" == 1 ]] || [[ "$(cat "$STAMP" 2>/dev/null || true)" != "$HEAD" ]]; then
  NEED=1
fi

if [[ "$NEED" == 1 ]]; then
  if [[ -f graphify-out/graph.json ]]; then
    graphify update . >>"$LOG" 2>&1 || graphify extract . --code-only --no-cluster --global --as "$NAME" >>"$LOG" 2>&1 || true
  else
    graphify extract . --code-only --global --as "$NAME" >>"$LOG" 2>&1 || true
  fi
  if [[ -f graphify-out/graph.json ]]; then
    graphify global add graphify-out/graph.json --as "$NAME" >>"$LOG" 2>&1 || true
    if [[ "$DIRTY" == 0 ]]; then
      printf '%s\n' "$HEAD" > "$STAMP"
    fi
  fi
fi

if [[ -f graphify-out/graph.json ]]; then
  DEST="$VAULT/03_Resources/Graphify/$NAME"
  mkdir -p "$DEST" "$VAULT/02_Areas/Agents" "$VAULT/03_Resources/Graphify"
  graphify export obsidian --dir "$DEST" >>"$LOG" 2>&1 || true
fi

GLOBAL="$(graphify global path 2>/dev/null || true)"
if [[ -n "$GLOBAL" && -f "$GLOBAL" ]]; then
  if stat -c %Y "$GLOBAL" >/dev/null 2>&1; then
    MT="$(stat -c %Y "$GLOBAL")"
  else
    MT="$(stat -f %m "$GLOBAL")"
  fi
  GSTAMP="${HOME}/.graphify/.brain-global-mtime"
  mkdir -p "${HOME}/.graphify"
  OLD="$(cat "$GSTAMP" 2>/dev/null || echo 0)"
  if [[ "$MT" != "$OLD" ]]; then
    graphify export obsidian --graph "$GLOBAL" --dir "$VAULT/03_Resources/Graphify/_all-projects" >>"$LOG" 2>&1 || true
    printf '%s\n' "$MT" > "$GSTAMP"
  fi
fi

VAULT="$VAULT" python3 - <<'PY'
import os
from pathlib import Path
vault = Path(os.environ["VAULT"])
root = vault / "03_Resources" / "Graphify"
projects = []
if root.is_dir():
    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if child.is_dir() and not child.name.startswith("."):
            projects.append(child.name)
lines = ["## Projects", ""]
if projects:
    for name in projects:
        lines.append(f"- `{name}` — `03_Resources/Graphify/{name}/`")
else:
    lines.append("- No project graphs exported yet.")
lines.append("")
block = "\n".join(lines)
start, end = "<!-- graphify-projects:start -->", "<!-- graphify-projects:end -->"
note = vault / "02_Areas" / "Agents" / "Graphify.md"
note.parent.mkdir(parents=True, exist_ok=True)
body = f"""---
tags:
  - graphify
  - agents
---

# Graphify

Code knowledge graphs for the projects, built locally with Graphify and written into this vault. Each project is a folder of linked notes under `03_Resources/Graphify/`. `_all-projects` is the combined graph. Notes Graphify does not own are left untouched.

{start}
{block}
{end}
"""
if note.exists():
    text = note.read_text(encoding="utf-8")
    if start in text and end in text:
        pre, rest = text.split(start, 1)
        _, post = rest.split(end, 1)
        note.write_text(pre + start + "\n" + block + "\n" + end + post, encoding="utf-8")
    else:
        note.write_text(text.rstrip() + "\n\n" + start + "\n" + block + "\n" + end + "\n", encoding="utf-8")
else:
    note.write_text(body, encoding="utf-8")

needle = "[[Graphify]]"
for moc in vault.rglob("Agents_MOC.md"):
    try:
        moc_text = moc.read_text(encoding="utf-8")
    except OSError:
        continue
    if needle in moc_text:
        continue
    moc.write_text(moc_text.rstrip() + "\n\n- [[Graphify]] — code knowledge graphs for the projects\n", encoding="utf-8")
    break
PY

printf '{}\n'
exit 0
