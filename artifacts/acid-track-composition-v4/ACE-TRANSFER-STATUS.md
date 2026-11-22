# Acid Track v4 → ACE Studio transfer status

**Status: BLOCKED (wrong runtime)** — 2026-11-22

## What happened

The agent tasked with this transfer ran on Cursor **managed cloud Linux**
(`agent/runtime=managed`, `usePrivateWorker=false`, hostname `cursor`), not on
**ROLAND's Mac Studio**. ACE Studio / `acestudio-cli` are macOS-only and are
not present in this VM.

## Mac worker ready for re-dispatch

| Field | Value |
|-------|-------|
| Worker display | `~/logic-pro-mcp @ ROLAND's Mac Studio` |
| workerId | `c5f0aa26-6d76-5973-852a-3b163cfca718` |
| OS | darwin |
| State when blocked | idle, `eligibleForSubagent=true`, `approved=true`, `sharedAssignmentAllowed=true` |

**Action for parent:** re-spawn this transfer as a subagent / CreateAgent with
`privateWorkerId=c5f0aa26-6d76-5973-852a-3b163cfca718` (or Remote Machine =
ROLAND's Mac Studio). Do not run it on managed cloud.

## Source MIDI (repo)

`artifacts/acid-track-composition-v4/midi/` — 11 files, 127 BPM, A minor, 48 bars.

Import order:

1. `v4_909_kick.mid`
2. `v4_909_clap_snare.mid`
3. `v4_909_hats.mid`
4. `v4_house_percussion.mid`
5. `v4_acid_main_303.mid`
6. `v4_acid_answer_303.mid`
7. `v4_sub_pump.mid`
8. `v4_rave_chord_stabs.mid`
9. `v4_metallic_lead.mid`
10. `v4_vocal_like_synth.mid`
11. `v4_noise_transitions.mid`

## Mac-side helper

Once on the Mac, run (full permissions / unsandboxed so ACE bridge sockets work):

```bash
chmod +x artifacts/acid-track-composition-v4/ace-transfer-mac.sh
./artifacts/acid-track-composition-v4/ace-transfer-mac.sh
```

Or discover commands first:

```bash
ACE="/Applications/ACE Studio.app/Contents/Helpers/acestudio-cli"
"$ACE" --help
"$ACE" app status   # must show bridge-ready
"$ACE" project --help
"$ACE" midi --help || "$ACE" import --help || "$ACE" file --help
```

Target save path: `~/Music/ACE Studio/Acid Track v4/`

## Not completed

- bridge status (unreachable from cloud)
- project create / tempo 127 / 11-track MIDI import / save / verify
