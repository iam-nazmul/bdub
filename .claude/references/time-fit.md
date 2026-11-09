# Time-fit and drift algorithm

Implements SPEC §9.3–9.4. Constants are in [constants.md](constants.md). Lives in `src/bdub/audio/timefit.py` (pure, Qt-free, deterministic).

## Definitions

- For utterance *i*: source span `[s_i, e_i]`, next utterance start `s_{i+1}`.
- `gap_after_i = s_{i+1} - e_i` (∞ for the last one).
- Window `W_i = (e_i - s_i) + min(S, gap_after_i)` with `S = 700 ms`.
- `D_i` = synthesized duration at native rate.
- `offset` = cumulative drift (placed start − source start), starts at 0.

## Per-utterance plan

```
def plan(u, W, D, offset):
    start = u.s + offset            # start-aligned (option: center-aligned)
    if D <= W:                      # 1. fits
        return place(start, stretch=1.0)
    if D <= W * 1.25:               # 2. small stretch
        return place(start, stretch=D / W)
    for attempt in 1..2:            # 3. shorter translation
        D = resynthesize(retranslate_shorter(u, attempt))
        if D <= W * 1.25:
            return place(start, stretch=max(1.0, D / W), flag="retranslated")
    rate = min(1.20, D / W)         # 4. native rate + stretch, total ≤ 1.35
    D_rate = D / rate
    stretch = min(1.35 / rate, max(1.0, D_rate / W))
    D_final = D_rate / stretch
    if D_final <= W:
        return place(start, rate, stretch)
    overflow = D_final - W          # 5. overflow into the next gap / shift later
    if overflow fits in the remaining gap and offset + overflow <= 1.0 s:
        return place(start, rate, stretch, flag="overflow")
    return place(start, rate, stretch, flag="too_long")   # 6. play at cap, flag in editor
```

Step 3 is only possible when the MT worker is available; in batch planning, run steps 1–2 for all utterances first, then collect the step-3 candidates into one MT job.

## Drift control

- After placing *i*, `offset = placed_end_i - e_i` if positive, else 0.
- At a source pause `gap_after_i ≥ 400 ms`, reduce the offset by shortening the pause: `offset = max(0, offset - (gap_after_i - 400 ms))` (keep at least a 400 ms pause, never shorten speech).
- If `offset > 1.0 s` at any point, re-plan the next utterances with steps 3–4 forced (aggressive mode) until it is back under the cap.

## Properties to test (hypothesis)

1. No two placed clips overlap (`placed_end_i ≤ placed_start_{i+1}`).
2. `offset` never exceeds 1.0 s after an utterance that wasn't flagged `too_long`.
3. Every clip is played in full: `placed_duration == D_final` (no truncation).
4. `stretch ≤ 1.25` when `rate == 1.0`; `rate * stretch ≤ 1.35` always.
5. Placed start never precedes source start (start-aligned mode).
6. Same inputs → identical plan (determinism).
7. If `D ≤ W` for all utterances, all `stretch == 1.0`, `offset == 0`, and no flags.

## Ducking (no separation, T1)

Gain envelope over the original audio from VAD speech regions: target −22 dB (range 18–25) during speech, 80 ms attack, 300 ms release, computed vectorized (NumPy) at a 10 ms control rate, then interpolated to sample rate.
