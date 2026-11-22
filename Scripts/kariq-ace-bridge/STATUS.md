# KARIQ → ACE Studio bridge

**Status: READY TO RUN ON MAC** — 2026-11-22 (Asia/Yerevan)

This cloud agent (`Kariq project bridge`) ran on **Cursor managed Linux**. Logic Pro and ACE Studio live on **ROLAND's Mac Studio**. The Task tool on this run only accepts `same_machine | new_cloud_vm`, so `self_hosted_worker` placement was refused at the schema discriminator even though worker `c5f0aa26-6d76-5973-852a-3b163cfca718` was idle, approved, and `eligibleForSubagent=true`.

The live bridge is not done until the Mac runner below reports `DONE` and ACE has a saved **KARIQ** project.

## What this kit does

1. Opens ACE Studio and waits for `bridge-ready`.
2. Copies known KARIQ mix/vocal bounces into `~/Music/ACE Studio/KARIQ-bridge/`.
3. Creates/opens an ACE project named **KARIQ**, sets tempo if a tool exists, imports mix + vocals (and MIDI if present).
4. Attempts Vocal to MIDI on the lead vocal audio.
5. Saves under `~/Music/ACE Studio/KARIQ/`.
6. Prints the ACE Bridge 2 AU steps to run inside Logic (live MIDI/audio link).

It does **not** remix KARIQ, generate Acid Track v4, or run `hip_hop_beat`.

## Known KARIQ session (from prior Mac mix work)

| Field | Value |
| --- | --- |
| Vocals | Lead kuplet, Pripev, LEAD, LEAD 2, LEAD 2 DBL, LEAD DBL |
| Flex | Monophonic already on vocal lanes |
| Mix window used for listen | bars 34–95 |
| Bounces | `~/Music/Logic/Bounces/KARIQ-mix-listen.aif`, `KARIQ-mix-final.aif`, `KARIQ-vocals-cleaned.aif` |
| Loudness (last measured master) | −9.9 LUFS / −2.0 dBTP |
| Bad Save As name | `Lead kuplet.logicx` — do not treat as canonical |

Tempo and key were not logged in those sessions. The runner reads them from Logic/ACE when possible and otherwise leaves ACE at the open project's tempo.

## Finish on the Mac (pick one)

### A) New Cloud Agent on ROLAND's Mac Studio (preferred)

Start a Cloud Agent with **Remote Machine: ROLAND's Mac Studio**, repo `RolandGasparyan/logic-pro-mcp`, branch `cursor/kariq-ace-bridge-1492`. Prompt:

```text
You are on Darwin. Bridge KARIQ from Logic to ACE. Do not generate beats.

1. uname -s must be Darwin or STOP.
2. Keep Logic frontmost. Open KARIQ (not Acid Track v4, not Lead kuplet.logicx unless that is the only copy).
3. open -a "ACE Studio" and wait for acestudio-cli app status = bridge-ready.
4. cd the logic-pro-mcp checkout and run:
     bash Scripts/kariq-ace-bridge/bridge-kariq-mac.sh
5. Then in Logic: Software Instrument track → Audio Units → ACE Bridge 2.
   Connect, link to the KARIQ lead vocal in ACE.
   Logic Settings → Audio → General → turn OFF Playback Pre-roll.
6. Save ACE as KARIQ and Save the Logic project with an explicit KARIQ filename.
7. Report ACE project path, track list, tempo, Bridge connected yes/no.
```

### B) Terminal on the Mac

```bash
cd ~/logic-pro-mcp   # or the worker-dir checkout
git fetch origin cursor/kariq-ace-bridge-1492
git checkout cursor/kariq-ace-bridge-1492
git pull
open -a "Logic Pro" || open -a "Logic Pro X"
open -a "ACE Studio"
bash Scripts/kariq-ace-bridge/bridge-kariq-mac.sh
```

Then complete ACE Bridge 2 inside Logic using `Scripts/kariq-ace-bridge/ACE-BRIDGE-2.md`.

## Worker last seen

| Field | Value |
| --- | --- |
| displayName | `~/logic-pro-mcp @ ROLAND's Mac Studio` |
| workerId | `c5f0aa26-6d76-5973-852a-3b163cfca718` |
| OS | darwin |
| ACE CLI | `/Applications/ACE Studio.app/Contents/Helpers/acestudio-cli` |
| ACE MCP | `/Applications/ACE Studio.app/Contents/Helpers/ace-mcp-server` |
| LogicProMCP | `/Users/rolandgasparyan/.local/bin/LogicProMCP` |
