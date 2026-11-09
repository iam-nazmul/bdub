# Constants and limits

All numbers from SPEC.md in one place. Code should define these once (e.g. `src/bdub/constants.py`) and import them; never hard-code them in several places.

## Dubbing and timing (SPEC §9)

| Name | Value | Source |
|---|---|---|
| Utterance length | 1–12 s | §9.2 |
| Merge pause (same speaker) | < 400 ms | §9.2 |
| Silence extension limit `S` | 700 ms | §9.3 |
| Max stretch (speed-up) | 1.25× | §9.3 step 2 |
| Max TTS native rate increase | +20% | §9.3 step 4 |
| Max combined speed-up | 1.35× | §9.3 step 4 |
| Retranslation attempts | 2 | §9.3 step 3 |
| Drift reset pause | ≥ 400 ms | §9.4 |
| Drift hard cap | 1.0 s | §9.4 |
| Sync target | 90% start within ±250 ms | §9.1 |
| Overflow target | ≤ 5% of utterances | §9.1 |
| Overlapping dub speech | 0 | §9.1 |

## Audio (SPEC §5.3, §9.5)

| Name | Value |
|---|---|
| Working sample rates | 48 kHz stereo (mix), 16 kHz mono (VAD/ASR) |
| Loudness target | −16 ±1 LUFS (stereo, EBU R128) |
| True peak max | −1 dBTP |
| Ducking depth (no separation) | 18–25 dB, default "keep underneath" −22 dB |
| Ducking attack / release | 80 ms / 300 ms |

## Subtitles (SPEC §10.3)

| Name | Value |
|---|---|
| Max line width | 42 Latin-equivalent columns |
| Max lines | 2 |
| Max reading speed | 17 chars/s |
| Contrast | ≥ 4.5:1 |
| Max subtitle size | 200% |

## Performance (SPEC §11.1)

| Name | T1 | T2 | T3 |
|---|---|---|---|
| Pipeline speed (processing ÷ media time) | ≤ 3.0× | ≤ 1.0× | ≤ 0.4× |
| First dubbed audio (progressive) | n/a | ≤ 90 s | ≤ 30 s |
| Peak RAM (all processes) | ≤ 5.5 GB | ≤ 10 GB | ≤ 20 GB |

| Name | Value |
|---|---|
| Cold start to window | ≤ 2.0 s |
| Open file to first frame | ≤ 1.0 s |
| Dub toggle latency | ≤ 150 ms |
| UI thread max block | 16 ms (watchdog logs > 100 ms) |
| Worker idle exit | 120 s |
| Progressive buffer | 60 s |
| Worker retries per chunk | 2 |
| Tier benchmark duration | ≈ 20 s |

## Storage and portability (SPEC §5.6, §6.5, §11.4, §18)

| Name | Value |
|---|---|
| Cache cap | min(20 GB, 50% of free space on the `bdub-data/` drive) |
| Low-space warning (removable drive) | < 2 GB free |
| Max single model file | < 4 GB (FAT32) |
| Program files size | ≤ 400 MB |
| Full portable download | ≈ 2.5–3 GB |
| Log cap | 50 MB rotating |
| Content hash | xxHash3 over first / middle / last 8 MB + size + duration |

## UI (SPEC §7.0, §7.4, §1.3)

| Name | Value |
|---|---|
| Min click target | 40 px |
| UI scale max | 200% |
| Clicks from opened file to dubbing | ≤ 3 |
| Battery pause threshold (option) | 30% |
