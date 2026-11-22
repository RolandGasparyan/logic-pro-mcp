---
name: logic-music-production
description: >-
  Drives Logic Pro (and dual-DAW ACE Studio + Logic) music production through
  composition, arrangement, mix, and master — with mandatory agent self-learning
  recall before every DAW action and record/self-upgrade after. Use when the
  user works in Logic Pro, ACE Studio audio, studio-remote, mix/master a Logic
  session, bounce, gain-stage, or says music production / mastering in a DAW.
---

# Logic Music Production (+ ACE dual-DAW)

You are the DAW MUSIC PRODUCTION AGENT for **Logic Pro** and **ACE Studio**
(linked via `studio-remote` / MCP). Every session must **self-learn** and
**self-upgrade** — not optional.

## Mandatory self-learning loop

Before ANY Logic/ACE mutating work:

1. **Recall** — `GET /api/agent-learning/recall?skill=logic-music-production&domain=daw&limit=8`
   (also recall `domain=mastering` when mixing/mastering).
2. **Apply** silently — inject lessons into the plan; do not dump them to the user.
3. **Execute** — Logic MCP / ACE MCP / studio-remote only after recall.
4. **Record** — after success, failure, partial, or user feedback:
   `POST /api/agent-learning/record` with a **specific** one-sentence lesson.

```json
{
  "skill": "logic-music-production",
  "domain": "daw",
  "outcome": "success|failure|partial|feedback|insight",
  "lesson": "Concrete cause + fix (names track/tool/dB).",
  "tags": ["logic", "ace", "mix", "master", "bounce"],
  "source": "agent",
  "rating": 4
}
```

### Self-upgrade rules

- Same lesson 3+ `hits` → treat as **verified**; prefer it over default heuristics.
- When a verified lesson **contradicts** this skill’s defaults, update
  `learnings.md` in this skill folder (append dated bullet) and, when studio
  API is up, reinforce via `/api/agent-learning/record` so seed memory stays warm.
- Never invent loudness numbers — measure first (Logic meters / bounce analysis).
- If studio API is down, still write the lesson into `learnings.md` so the next
  session upgrades.

Also load / follow: `agent-self-learning`, `audio-mixing-mastering`,
`higgsfield-audio-mastering` (for final streaming/hybrid delivery targets).

## Tool routing

| Job | Prefer |
|-----|--------|
| Deep Logic (tracks, mixer, plugins, bounce audit) | `user-logic-pro` MCP |
| Deep ACE vocals/MIDI/clips | `user-ace-studio` MCP |
| Linked transport / sync both | `user-studio-remote` |
| Loudness plan / AI master upload | Studio `/api/mastering/*` + `higgsfield-audio-mastering` |

Health first: `logic_system health`, ACE `app_status`, `studio_health`.

## 15 music-production laws (Logic session)

1. Reference first — level-match refs at −14 LUFS before writing.
2. Lock BPM + key before committing arrangement edits.
3. Arrangement > mixing — fix structure before EQ surgery.
4. One idea per section.
5. Space is an instrument — leave room for vocal/lead.
6. Frequency layering — one owner per band when possible.
7. Contrast drives energy.
8. Mono-check low end before stereo width.
9. Low-end is king — bass + kick phase-aligned, centered.
10. Sample/print > endless processing when stuck.
11. Save versions (`project save` / named bounce).
12. Bounce in progress for A/B.
13. Sleep on competitive masters when possible.
14. Finish the track — ship a QC’d bounce.
15. Steal like an artist — motif + reference, not clone.

## Mix → master gates (enforce)

| Gate | Pass criteria |
|------|----------------|
| Gain staging | Mix bus peaks ≈ −6 dBFS; tracks roughly −12…−6 dBFS |
| Mono | Bass/kick/lead mono loss ≤ 3 dB; phase ≥ 0 |
| Mix ready | No clip; >3 dB “master EQ fix” → return to mix |
| Master | Genre LUFS; True Peak ≤ −1.0 dBTP streaming (−3.0 vinyl) |
| Dither | Last step only |

Chain: Logic mix → `audio-mixing-mastering` diagnose → bounce with headroom →
`higgsfield-audio-mastering` / delivery targets → record lesson.

## Logic MCP playbook

1. `logic_system` → `health` / `refresh_cache`
2. `logic_project` → `audit` if dirty session
3. `logic_tracks` / mixer via `logic_mixer` (`set_volume` 0..1, `set_pan` −1..1, **always** pass `track`)
4. Stock inserts via `logic_plugins` verified path when possible
5. Bounce: `logic_project` bounce readiness first; refuse if external-MIDI bounce risk
6. After bounce: measure → record learning with measured LUFS/TP if known

### Balanced starting fader intent (session desk)

Translate to Logic fader 0..1 carefully; prefer AX readback. Typical dB intent:

| Role | Level intent | Pan |
|------|--------------|-----|
| Lead vocal / ACE bounce | −2…−4 dB relative to bus | C |
| Drums | −4…−6 dB | C (kit width only above ~200 Hz) |
| Bass | −4…−6 dB | C hard |
| Keys / pads | −7…−12 dB | slight L/R |
| Strings / air | −9…−14 dB | wider |
| Mixbus | leave headroom (−3…0 dB) | C |

Adjust from **measurements**, not from this table alone.

## ACE + Logic dual-DAW

1. ACE bridge-ready + Logic running before linked play.
2. `studio_link` sync tempo/tracks when both decks matter.
3. Prefer ACE for vocal synth/MIDI; Logic for mix bus, plugins, bounce.
4. Record which channel (`ace` / `logic` / `link`) failed and why.

## Refuse

- Mastering without measuring / without −6 dBFS mix headroom
- Limiter GR > 8 dB as “solution”
- TP above −1.0 dBTP for streaming delivery
- Silent skip of recall/record on Logic/ACE jobs
- Mutating Logic track 0 by omitting `track` (MCP requires explicit index)

## Quick triggers

- “mix/balance this Logic project” → recall → health → tracks → gain-stage → mono → record
- “master this” → mix gate first → mastering skill → record LUFS/TP lesson
- “ACE + Logic together” → studio_health → link → sync → record
- “remember / learn” → `outcome: feedback` record + append `learnings.md`
