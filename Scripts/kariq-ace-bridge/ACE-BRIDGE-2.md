# ACE Bridge 2 — KARIQ (Logic → ACE live link)

Content transfer (audio/MIDI import) is separate from the live AU link. Do this after `bridge-kariq-mac.sh` has a saved KARIQ ACE project.

## Setup

1. ACE Studio is already running (required before Connect).
2. In Logic, create a **Software Instrument** track.
3. Instrument slot → **Audio Units → ACE Bridge 2** (not an audio FX slot).
4. Click **Connect**, then **+** to create a voice or **link** the existing KARIQ lead-vocal track in ACE.
5. Logic Settings → Audio → General → turn **Playback Pre-roll off** (otherwise time signature jumps one bar early).
6. One Bridge instance per ACE track. Duplicate the SI track for extra voices.

## Playback

- DAW MIDI on that track → Bridge records into the linked ACE track.
- ACE clips on the linked track → Bridge plays synthesized audio back into Logic.
- Keep ACE's piano sampler in mind while recording MIDI; switch to the AI voice for playback.

## Optional ARA tempo map (Apple Silicon)

Only if KARIQ has a real tempo map, not a single BPM:

1. Open Logic in **Rosetta**.
2. In Bridge click **SYNC TEMPO**, drop the silent dummy onto an audio track.
3. Insert **ACE Bridge ARA** as the first Audio FX on that dummy clip and connect it.

For a fixed-tempo song, skip ARA.

## Probe

If `~/Projects/ace-mcp` exists:

```bash
bash ~/Projects/ace-mcp/scripts/check-bridge-environment.sh
```

Otherwise search `~/Library/Audio/Plug-Ins/Components` and `/Library/Audio/Plug-Ins/Components` for ACE Bridge.
