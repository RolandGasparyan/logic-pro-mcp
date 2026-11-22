#!/usr/bin/env bash
# Acid Track v4 → ACE Studio transfer (run on ROLAND's Mac Studio only).
# Discovers acestudio-cli subcommands via --help, then creates a project,
# sets 127 BPM, imports 11 MIDI files, renames tracks, saves, verifies.
set -euo pipefail

ACE_CLI="${ACE_CLI:-/Applications/ACE Studio.app/Contents/Helpers/acestudio-cli}"
MIDI_DIR="$(cd "$(dirname "$0")/midi" && pwd)"
PROJECT_NAME="${PROJECT_NAME:-Acid Track v4}"
TEMPO="${TEMPO:-127}"
SAVE_DIR="${SAVE_DIR:-$HOME/Music/ACE Studio/Acid Track v4}"

MIDI_FILES=(
  v4_909_kick.mid
  v4_909_clap_snare.mid
  v4_909_hats.mid
  v4_house_percussion.mid
  v4_acid_main_303.mid
  v4_acid_answer_303.mid
  v4_sub_pump.mid
  v4_rave_chord_stabs.mid
  v4_metallic_lead.mid
  v4_vocal_like_synth.mid
  v4_noise_transitions.mid
)

die() { echo "ERROR: $*" >&2; exit 1; }

[[ -x "$ACE_CLI" ]] || die "acestudio-cli not found/executable at: $ACE_CLI"
[[ -d "$MIDI_DIR" ]] || die "MIDI dir missing: $MIDI_DIR"

echo "==> CLI: $ACE_CLI"
"$ACE_CLI" --help 2>&1 | head -80 || true
echo
"$ACE_CLI" app status 2>&1 || true
echo

# Launch ACE if needed (best-effort; do not kill other apps)
if ! "$ACE_CLI" app status 2>&1 | grep -qi 'bridge-ready'; then
  echo "==> Launching ACE Studio…"
  open -a "ACE Studio" || true
  for i in $(seq 1 30); do
    if "$ACE_CLI" app status 2>&1 | grep -qi 'bridge-ready'; then
      break
    fi
    sleep 2
  done
fi

STATUS="$("$ACE_CLI" app status 2>&1 || true)"
echo "$STATUS"
echo "$STATUS" | grep -qi 'bridge-ready' || die "ACE Studio not bridge-ready"

# Dump help for discovery (parent/agent reuse)
mkdir -p "$SAVE_DIR"
HELP_DIR="$SAVE_DIR/_cli-help"
mkdir -p "$HELP_DIR"
"$ACE_CLI" --help >"$HELP_DIR/root.txt" 2>&1 || true
for sub in app project track tracks midi import file transport tempo; do
  "$ACE_CLI" "$sub" --help >"$HELP_DIR/${sub}.txt" 2>&1 || true
done

pick_cmd() {
  # pick_cmd <helpfile> <regex> → prints first matching non-empty line's suggested argv after ACE_CLI
  local helpfile="$1" regex="$2"
  [[ -f "$helpfile" ]] || return 1
  if grep -Eiq "$regex" "$helpfile"; then
    return 0
  fi
  return 1
}

echo "==> Creating new project: $PROJECT_NAME"
# Try common shapes; stop at first success
created=0
for attempt in \
  "project new --name \"$PROJECT_NAME\"" \
  "project create --name \"$PROJECT_NAME\"" \
  "project new \"$PROJECT_NAME\"" \
  "project create \"$PROJECT_NAME\"" \
  "file new" \
  "app new-project"
do
  echo "try: $ACE_CLI $attempt"
  if eval "\"$ACE_CLI\" $attempt" 2>&1; then
    created=1
    break
  fi
done
[[ "$created" -eq 1 ]] || echo "WARN: could not auto-create project; continuing with whatever is open (prefer user new project first)"

echo "==> Set tempo $TEMPO BPM"
for attempt in \
  "project set-tempo $TEMPO" \
  "project tempo set $TEMPO" \
  "tempo set $TEMPO" \
  "transport set-tempo $TEMPO" \
  "project set --tempo $TEMPO"
do
  echo "try: $ACE_CLI $attempt"
  if eval "\"$ACE_CLI\" $attempt" 2>&1; then
    break
  fi
done

# 4/4 if supported
for attempt in \
  "project set-time-signature 4 4" \
  "project time-signature set 4/4" \
  "tempo set-signature 4 4"
do
  eval "\"$ACE_CLI\" $attempt" 2>&1 || true
done

echo "==> Importing ${#MIDI_FILES[@]} MIDI files from $MIDI_DIR"
idx=0
for f in "${MIDI_FILES[@]}"; do
  path="$MIDI_DIR/$f"
  [[ -f "$path" ]] || die "missing MIDI: $path"
  name="${f%.mid}"
  echo "-- [$idx] $name"
  imported=0
  for attempt in \
    "midi import \"$path\"" \
    "import midi \"$path\"" \
    "file import \"$path\"" \
    "project import-midi \"$path\"" \
    "track import-midi \"$path\""
  do
    if eval "\"$ACE_CLI\" $attempt" 2>&1; then
      imported=1
      break
    fi
  done
  [[ "$imported" -eq 1 ]] || echo "WARN: import failed for $f"

  # Rename newest/selected track when possible
  for attempt in \
    "track rename \"$name\"" \
    "tracks rename --name \"$name\"" \
    "track set-name \"$name\""
  do
    eval "\"$ACE_CLI\" $attempt" 2>&1 || true
  done
  idx=$((idx + 1))
done

echo "==> Save project under $SAVE_DIR"
mkdir -p "$SAVE_DIR"
for attempt in \
  "project save --path \"$SAVE_DIR/$PROJECT_NAME.ace\"" \
  "project save-as \"$SAVE_DIR/$PROJECT_NAME.ace\"" \
  "file save-as \"$SAVE_DIR/$PROJECT_NAME.ace\"" \
  "project save \"$SAVE_DIR\"" \
  "project save"
do
  echo "try: $ACE_CLI $attempt"
  if eval "\"$ACE_CLI\" $attempt" 2>&1; then
    break
  fi
done

echo "==> Verify"
for attempt in \
  "project info" \
  "project get" \
  "project status" \
  "tracks list" \
  "track list"
do
  eval "\"$ACE_CLI\" $attempt" 2>&1 || true
done

echo
echo "DONE. Help dumps: $HELP_DIR"
echo "Save dir: $SAVE_DIR"
echo "Confirm tempo ~$TEMPO and ~11 tracks with MIDI content in ACE Studio UI."
