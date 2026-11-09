# mpv configuration

Implements SPEC §5.1 (playback), FP-2–FP-6, FD-5, §12, §14. Player code lives in `src/bdub/player/`. Option names must be checked against the bundled libmpv version in M0. Items marked **(verify)** depend on version.

## Create-time options (security and embedding)

| Option | Value | Why |
|---|---|---|
| `vo` | `libmpv` | Render API into `QOpenGLWidget` |
| `config` | `no` | Ignore user's mpv config files |
| `load-scripts` | `no` | No Lua/JS scripts |
| `ytdl` | `no` | No youtube-dl / network fetches |
| `osc` | `no` | We draw our own controls |
| `input-default-bindings` | `no` | Keys handled by Qt |
| `input-vo-keyboard` | `no` | |
| `load-stats-overlay`, `load-osd-console`, `load-auto-profiles`, `load-select` | `no` | Disable built-in scripts **(verify)** |
| `demuxer-lavf-o` | `protocol_whitelist=[file,pipe,fd,crypto]`-style value restricting to local protocols **(verify exact syntax)** | No network protocols |
| `hwdec` | `auto-safe` | Hardware decode where safe |
| `sub-fonts-dir` | `<_internal>/resources/fonts` | Bundled Bangla fonts |
| `sub-font` | `Noto Sans Bengali` | Default subtitle font |
| `embeddedfonts` | `yes` | Allow fonts embedded in MKV |
| `sub-ass-force-style`/`sub-ass-override` | per user style settings | FP-6 |
| `audio-pitch-correction` | `yes` | FP-3 speed changes |
| `keep-open` | `yes` | Stay on last frame at end |
| `terminal`, `msg-level` | `no`, `all=warn` → our logger | Logs go to `bdub-data/logs/` |

## Tracks

| Purpose | Command / property |
|---|---|
| Add Bangla dub | `audio-add <dub_only.m4a> auto "Bangla Dub (generated)" bn` |
| Add Bangla mix | `audio-add <dub_mix.m4a> auto "Bangla Mix" bn` |
| Switch audio (FD-5, ≤ 150 ms) | set `aid` to the track id from `track-list` |
| Add Bangla subtitles | `sub-add <subs_bn.srt> auto "Bangla (generated)" bn` |
| Add original subtitles | `sub-add <subs_src.srt> auto "Original (ASR)" <src_lang>` |
| Dual subtitles | `sid` = Bangla, `secondary-sid` = original |
| Reload after re-dub | `audio-reload <id>` / `sub-reload <id>` **(verify on active track)** |
| Track list | observe `track-list` property |

Simple-mode **Original / বাংলা** switch: `aid` = original track ↔ "Bangla Mix" track (mix keeps music and effects).

## Progressive mode (FD-3)

The dub track grows while dubbing runs. Options (decide in M3):

1. Render the mix in fixed-length segments and expose them as one growing file; on reaching unready time, pause or switch `aid` to original.
2. Observe `time-pos`; compare with `ready_until_ms` from the orchestrator; when `time-pos` > `ready_until_ms − 2 s`, pause with "Dubbing is catching up…" or switch to original (user setting), then resume.

## Observed properties

`time-pos`, `duration`, `pause`, `eof-reached`, `track-list`, `aid`, `sid`, `secondary-sid`, `volume`, `mute`, `speed`, `chapter-list`. Use observers, not polling.

## Threading

python-mpv callbacks arrive on mpv's threads. Never touch Qt widgets from them. Forward to the UI thread with a Qt signal (queued connection). The render context's update callback must only schedule `QOpenGLWidget.update()` via a signal.
