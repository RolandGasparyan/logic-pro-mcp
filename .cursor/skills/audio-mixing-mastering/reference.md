# Audio Mixing & Mastering — Reference Tables v1.0

Companion to `SKILL.md`. All numbers are defaults; always measure first.

## FREQUENCY MAP

Band        | Range (Hz)    | Fix
------------|---------------|----------------------------------
Sub         | 20-60         | Mono, HPF mix at 20-30
Low         | 60-120        | Carve 80-100 kick<->bass
Low-mid     | 120-350       | -2..-4 dB narrow cut 200-300
Mid         | 350-2000      | Vocal presence 800-1500
Upper-mid   | 2000-5000     | Watch 2.5-3.5 k masking
Presence    | 5000-8000     | Vocal +1..+3 dB 5-7 k
Air         | 8000-16000    | +1..+2 dB shelf
Ultra       | 16000-20000   | Optional LPF 18-20 k

Masking priority: kick<->bass -> snare<->vocal -> guitars<->vocal ->
                  synths<->vocal -> reverb returns.

## LOUDNESS STANDARDS

Platform                | Normalization | Delivery
------------------------|---------------|---------------------
Spotify/Apple/YouTube   | -14 LUFS-I    | -9..-14 per genre
Tidal / Amazon          | -14 LUFS-I    | same
EBU R128 broadcast      | -23 LUFS-I    | TP -1.0
Club/DJ                 | none          | -7..-9 LUFS, TP -0.5
Vinyl                   | engineer      | TP -3.0, PLR >= 10

## GENRE MATRIX — MASTER TARGETS

Genre             | LUFS-I    | dBTP | PLR   | Signature
------------------|-----------|------|-------|-------------------------------
Pop               | -10..-8   | -1.0 | 7-10  | Vocal-forward, sidechain reverb
K-Pop             | -9..-7    | -1.0 | 6-9   | Section jumps, heavy parallel comp
Synth-pop         | -10..-8   | -1.0 | 8-10  | Gated snare reverb
Rock              | -11..-9   | -1.0 | 8-11  | Parallel drum bus crush
Indie Rock        | -12..-10  | -1.0 | 9-12  | Room mics prominent
Punk              | -10..-8   | -1.0 | 7-9   | Fast comp, low reverb
Metal             | -10..-8   | -1.0 | 7-9   | Guitars 100% L/R, MBC guitars
Hip-Hop/Trap      | -9..-7    | -1.0 | 6-9   | Sidechain 808 to kick
Drill             | -9..-7    | -1.0 | 6-8   | Sliding 808 pitch automation
Phonk             | -9..-7    | -1.0 | 6-8   | Cowbell + tape sat
R&B               | -11..-9   | -1.0 | 8-10  | Vocal stacking + tuning
Soul/Funk         | -12..-10  | -1.0 | 9-12  | Live-feel, minimal grid
Gospel            | -10..-8   | -1.0 | 8-10  | Choir bus parallel comp
Jazz              | -14..-11  | -1.0 | 11-16 | No limiting, dynamics preserved
Blues             | -13..-10  | -1.0 | 10-14 | Amp mic blend
Country           | -12..-10  | -1.0 | 9-12  | Fiddle/steel wide
Folk/Acoustic     | -14..-11  | -1.0 | 10-14 | Room + close mic
Singer-Songwriter | -14..-11  | -1.0 | 11-15 | Intimate, 200 Hz warmth
House             | -9..-7    | -1.0 | 6-9   | Sidechain pump 4/4
Techno            | -8..-6    | -0.8 | 5-8   | Distortion on bus
Trance            | -9..-7    | -1.0 | 6-8   | Long reverb + supersaw
Drum & Bass       | -8..-6    | -0.8 | 5-8   | Reese + break layers
Dubstep/Riddim    | -8..-6    | -0.8 | 5-7   | LFO bass + multiband
Future Bass       | -9..-7    | -1.0 | 6-8   | Chord stacks + sidechain
Lo-Fi             | -14..-11  | -1.0 | 10-14 | Vinyl noise + wow/flutter
Ambient           | -18..-14  | -1.0 | 14-20 | Long reverbs, no transients
Hyperpop          | -8..-6    | -0.8 | 5-7   | Bitcrush + clipping
Classical         | -20..-16  | -1.0 | 12-20 | No limiting, Decca tree
Cinematic         | -14..-11  | -1.0 | 8-12  | Sub drops, impact hits
Reggaeton         | -9..-7    | -1.0 | 6-8   | Dembow + sidechain
Afrobeat          | -10..-8   | -1.0 | 7-9   | Percussion layering
Reggae            | -12..-9   | -1.0 | 9-12  | Delay throws, one-drop
World/Ethnic      | -13..-10  | -1.0 | 10-14 | Preserve timbre

## MIX SETUP — GENRE FAMILIES

### Pop / K-Pop / Synth-pop
DRUMS:  Kick HPF 30, cut 300, +3 @ 3-5k | Snare 200 body, 5k crack
        Parallel crush: 1176 all-buttons, -18 dB blend
BASS:   Mono <120 Hz | Sidechain -3 dB kick | 2nd harmonic sat
GTR:    Hard L/R | HPF 100 | cut 800 | presence 3k
VOCAL:  HPF 80 -> de-ess 6-8k -> comp 3:1 (3 dB GR) -> +2 @ 3k ->
        comp 2:1 parallel -> sat -> delay 1/8 dotted
BUS:    SSL comp 2:1, 2-3 dB GR, 30ms attack | tape 0.5 dB

### Rock / Indie / Punk / Metal
DRUMS:  Room +6 dB (rock) / gated (metal) | Kick 4-6k click
GTR:    Double L/R | HPF 80-100 | cut 400 | +2 @ 2.5k
        Metal: MBC 200-500 + 3-5k
BASS:   DI + amp | HPF 40 | cut 250 | parallel distortion
VOCAL:  Comp 4:1 fast | cut 2-3k harshness | parallel scream bus
BUS:    Neve sat | comp 2:1, 2 dB GR

### Hip-Hop / Trap / Drill / Phonk
808:    Mono | tuned to key | 2nd/3rd sat | sidechain -4 dB kick
KICK:   HPF 25 | cut 200 | click 3-5k | clip for punch
HATS:   Wide, HPF 400 | slight de-ess 8-10k
SNARE:  Layered body+clap+rim | 200 Hz + 4k
VOCAL:  HPF 90 -> cut 400 -> comp 4:1 -> de-ess 6-8k ->
        sat -> +2 @ 3k -> parallel -> light tune
BUS:    Soft clip 0.5-1 dB | no heavy bus comp

### R&B / Soul / Funk / Gospel
DRUMS:  Natural, room-heavy | brushes/perc wide
BASS:   Round 80-150 | comp 3:1 slow attack
KEYS:   Rhodes/Wurli wide | chorus
VOCAL:  Stacks 4-8 | lead comp 3:1 -> air +2 @ 10k
        Choir bus: parallel comp 4:1
BUS:    Gentle tube sat | comp 2:1, 1-2 dB GR

### Electronic (House / Techno / Trance / DnB / Dubstep / Future Bass)
KICK:   Tuned to key | mono <120 | distortion (techno)
BASS:   Reese (DnB): mid-side, mono <100
        Sidechain: 4/4 house, 1/8 DnB
SYNTH:  Supersaw wide | LFO growl | chord stacks
FX:     Riser -> impact -> sub drop | reverb 2-4s on leads
BUS:    Comp 2:1 | MBC sub control | soft clip 1 dB

### Acoustic / Folk / Country / Blues / Jazz / Singer-Songwriter
DRUMS:  Minimal, room, no sample replace
BASS:   Upright: mic + DI, HPF 40, no sub boost
ACOU:   Close + room, HPF 80, cut 200, +1 @ 8k
VOCAL:  Natural, comp 2:1, minimal de-ess, breath kept
BUS:    No comp (jazz) | light 1-2 dB (country)

### Classical / Orchestral / Cinematic
MICS:   Decca tree + spots | phase-align all
EQ:     Surgical only | no HPF <40
DYN:    No comp on master | micro-dynamics preserved
WIDTH:  Natural hall, M/S only if needed
MASTER: Limiter bypassed or 0.5 dB max | -20..-16 LUFS

### Latin / Reggaeton / Afrobeat / Reggae
DEMBOW: Kick 50-70 mono | snare/clap 200 + 3k
BASS:   Warm 60-120 | sidechain kick
PERCS:  Wide, HPF 300 | delay throws
VOCAL:  +2 @ 4-6k | de-ess 7-9k | delay 1/8
BUS:    Comp 2:1 | sat for afro warmth

### Ambient / Lo-Fi / Hyperpop
LO-FI:    Tape sat, wow/flutter, vinyl noise, LPF 12-14k
AMBIENT:  No transients, reverb 6-12s, very wide
HYPERPOP: Bitcrush, hard clip, pitched vox, extreme width
MASTER:   Lo-fi -14 LUFS | Hyperpop -7 LUFS

## MASTERING CHAIN (strict order)

1. High-pass filter       20-30 Hz (classical 30-40 gentle)
2. Corrective EQ          narrow cuts, <=3 dB single point
3. Dynamic EQ / MBC       genre-dependent
4. Broadband compression  1-3 dB GR (bypass: classical, jazz)
5. Stereo imaging         mono <100-120 Hz, M/S width
6. Tonal EQ               broad shelves +/-1-2 dB
7. Saturation             0.3-1 dB genre-dependent
8. Limiter                to target LUFS, TP ceiling
9. Dither                 24->16 bit, FINAL

Per-family deltas:

Family      | HPF      | MBC             | Bus comp | Width     | Sat      | Lim GR
------------|----------|-----------------|----------|-----------|----------|-------
Pop         | 25       | 3-band light    | 1-2      | +10% M/S  | 0.5      | 4-6
Rock        | 30       | 3-band guitars  | 1-2      | neutral   | 0.5      | 4-6
Hip-Hop     | 25       | sub-only        | bypass   | mono sub  | 1.0      | 5-7
R&B         | 30       | light           | 1        | +5%       | 0.3      | 3-5
Electronic  | 25       | sub+low-mid     | bypass   | mono<100  | 1.0      | 5-7
Acoustic    | 35       | bypass          | bypass   | neutral   | 0        | 2-3
Classical   | 30 gentle| bypass          | bypass   | neutral   | 0        | 0-1
Latin       | 30       | light           | 1        | +5%       | 0.5      | 4-6
Ambient     | 30       | bypass          | bypass   | wide      | tape 1   | 1-3

## DIAGNOSTIC THRESHOLDS

Return to mix if:
- Single-point corrective EQ > 3 dB
- Cumulative corrective EQ > 6 dB
- True peak after limiter > -0.5 dBTP at target LUFS
- Mono compatibility loss > 3 dB @ 100 Hz
- Noise floor > -60 dBFS in quiet passages
- Source clipping at 0 dBFS

Fix order: arrangement -> performance -> recording -> mixing -> mastering

Loudness warnings:
- PLR < 5 = crushed
- PLR > 20 at -9 LUFS = impossible without distortion

## DELIVERY SPECS

Output          | Format | Bit | SR        | Notes
----------------|--------|-----|-----------|------------------------------
Streaming       | WAV    | 24  | 44.1/48   | TP -1.0 dBTP
CD              | WAV    | 16  | 44.1      | TP -0.3 dBFS, dither
Vinyl pre       | WAV    | 24  | 44.1/48   | TP -3.0, mono bass, PLR >= 10
Club/DJ         | WAV    | 24  | 44.1/48   | -7..-9 LUFS, TP -0.5
Instrumental/TV | WAV    | 24  | session   | no limiter
Stems           | WAV    | 24  | session   | -6 dBFS headroom

## QC CHECKLIST (before delivery)

[ ] Mono check passed (bass, kick, lead vocal)
[ ] Phase correlation > 0 in low band
[ ] True peak measured <= target
[ ] LUFS-I within genre range
[ ] PLR within genre range
[ ] No sample > 0 dBFS in source
[ ] Level-matched A/B vs 2 refs
[ ] Dither applied once, last
[ ] File naming: Artist_Title_Master_v1_24-48.wav
[ ] Metadata + ISRC embedded
