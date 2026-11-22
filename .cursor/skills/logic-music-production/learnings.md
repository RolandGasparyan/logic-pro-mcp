# Logic / ACE self-upgrade log

Verified or sticky lessons from live sessions. Agents: append dated bullets
after recording to `/api/agent-learning/record`. Prefer measurable facts.

## Seed (system)

- 2026-11-15 — Always recall `skill=logic-music-production` + `domain=daw` before Logic/ACE mutations; record after.
- 2026-11-15 — Mix bus target ≈ −6 dBFS before master; streaming TP ≤ −1.0 dBTP.
- 2026-11-15 — Logic MCP `set_volume` / `set_pan` require explicit `track` ≥ 0 (no silent default to 0).
- 2026-11-15 — Dual-DAW: confirm ACE `bridge-ready` and Logic document open before `studio_link` play/sync.
- 2026-11-15 — CoreMIDI ownership conflicts on LogicProMCP: refresh/restart stale LogicProMCP processes before MCU/MIDI paths.

## Session upgrades

<!-- Append below. Format: - YYYY-MM-DD — lesson (hits/verified if known) -->
- 2026-11-22 — KARIQ rename: Logic MCP `tracks.rename` often fails/times out on stacked/off-screen headers; use Track > Search and Select Track… on a unique neighbor, arrow to target, then Track > Rename Track. Keep Logic frontmost and Escape any open rename field before the next op.
- 2026-11-22 — KARIQ mix: Read automation locks mixer AX faders (disabled); unlock with Mix → Delete Automation → Delete All Automation on Selected Track (after Select All), then logic_mixer.set_volume/set_pan work (State A).
- 2026-11-22 — KARIQ listen: bounce bars 34–95 with Normalize Off to ~/Music/Logic/Bounces/KARIQ-mix-listen.aif before judge; measured −25.1 LUFS / −1.46 dBTP / PLR 23.5 / phase 0.91 — mix too quiet after desk pull, not clipping.
- 2026-11-22 — KARIQ delivery: raise drums/bass/vocal stacks to ~−9 LUFS, then render_master with TP limit; streaming master landed −9.9 LUFS / −2.0 dBTP. qc_check may fail JSON bool serialize — trust analyze_audio numbers.
