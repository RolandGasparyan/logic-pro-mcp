# Acid Track v4 → ACE Studio transfer status

**Status: READY TO RUN ON MAC** — 2026-11-22 (Asia/Yerevan)

## Blocker

Cloud agents on Cursor managed Linux cannot reach ACE Studio. Transfer must run on
**ROLAND's Mac Studio** where `acestudio-cli` / `ace-mcp-server` live.

| Field | Value |
|-------|-------|
| Worker | `~/logic-pro-mcp @ ROLAND's Mac Studio` |
| workerId | `c5f0aa26-6d76-5973-852a-3b163cfca718` |
| OS | darwin |
| Last seen | idle, `eligibleForSubagent=true`, `approved=true` |

## How to finish (pick one)

### A) New Cloud Agent on the Mac (preferred)

1. Open Cursor → Cloud Agents → start agent on **Remote Machine: ROLAND's Mac Studio**
2. Repo `RolandGasparyan/logic-pro-mcp`, branch `cursor/ace-studio-v4-transfer-32ac` (or `main` after merge)
3. Prompt:

```text
Open ACE Studio, wait for bridge-ready, then run:
  python3 artifacts/acid-track-composition-v4/import_v4_ace_mcp.py
If MCP tool names fail, fall back to:
  ./artifacts/acid-track-composition-v4/ace-transfer-mac.sh
Save as Acid Track v4 under ~/Music/ACE Studio/Acid Track v4/
Update ACE-TRANSFER-STATUS.md with success, commit, push.
```

### B) Terminal on the Mac

```bash
cd ~/path/to/logic-pro-mcp
git fetch && git checkout cursor/ace-studio-v4-transfer-32ac
open -a "ACE Studio"
"/Applications/ACE Studio.app/Contents/Helpers/acestudio-cli" app status   # bridge-ready
python3 artifacts/acid-track-composition-v4/import_v4_ace_mcp.py
# fallback:
./artifacts/acid-track-composition-v4/ace-transfer-mac.sh
```

## Source

- 11 MIDI files in `midi/` (127 BPM, A minor, 48 bars)
- Specs: `v4-layer-specs.json`, `v4-brief.md`
- MCP importer: `import_v4_ace_mcp.py` (preferred)
- CLI discovery helper: `ace-transfer-mac.sh`

## Not completed from cloud

- Project create / tempo 127 / 11-track import / save / verify inside ACE Studio
