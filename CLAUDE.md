# CLAUDE.md

Guidance for working in this repository. [SPEC.md](SPEC.md) is the source of truth for scope, architecture, and requirements. When this file and the spec disagree, follow the spec and flag the mismatch.

## Project

**BanglaDub Player (`bdub`)**: an offline, portable desktop video player that dubs foreign-language video into Bangla (বাংলা) entirely on the user's machine. It is a normal media player first and a dubbing tool second, built for **everyday, non-technical users**.

Pipeline: demux → source separation → VAD/ASR → diarization → sentence merge → MT → Bangla text normalization → TTS → time-fit → mix → package (SPEC §5.3).

Status: early stage. The spec is written; the code is being scaffolded. If a file or module named here doesn't exist yet, create it in the layout below rather than inventing a new one.

## Stack

- **Python 3.12**, fully type-annotated
- **PyQt6** on Qt 6.8 LTS (Qt Widgets), imported only through `bdub.qt`
- **libmpv** via `python-mpv` render API inside a `QOpenGLWidget`
- **FFmpeg** via PyAV (decode) and the `ffmpeg` CLI (export mux)
- **onnxruntime**, **CTranslate2** / faster-whisper, whisper.cpp, sherpa-onnx for inference
- NumPy / SciPy / soundfile / pyloudnorm for audio DSP
- **uv**, **ruff**, **mypy**, **pytest** + pytest-qt + hypothesis
- **PyInstaller** (onedir), shipped as a **portable folder** (no installer)

## Commands

```bash
uv sync                              # install deps (runtime + dev groups)
uv run bdub                          # launch the GUI
uv run bdub --role asr --stdio       # run one worker standalone for debugging
uv run bdub dub <file>               # CLI dub (M2+)

uv run ruff check . && uv run ruff format .
uv run mypy src
uv run pytest                        # all tests
uv run pytest tests/unit -q          # fast unit tests
uv run pytest -k normalizer          # targeted
QT_QPA_PLATFORM=offscreen uv run pytest tests/ui   # headless UI tests
```

Run ruff, mypy, and the relevant tests before calling any change done. Add packages with `uv add` (never `pip install` or `uvx`).

## Layout

```
src/bdub/
  __main__.py      # entry: GUI, or `--role <worker>`
  qt.py            # the ONLY place that imports PyQt6
  paths.py         # the ONLY place that decides where files live (portable bdub-data/)
  constants.py     # all limits and defaults (see .claude/references/constants.md)
  app/             # QApplication, main window, menus, settings dialogs
  ui/              # widgets: controls, editor panel, model manager, first-run screen
  player/          # mpv render context, PlayerWidget, tracks/subs
  orchestrator/    # job graph, scheduler, cache, IPC server, worker supervisor, schema (pydantic)
  workers/         # separate, asr, mt, tts, mix, decode
  text/bn/         # Bangla normalizer, lexicon, transliteration, register rules (no Qt)
  audio/           # time-fit planner, stretch, ducking, mixer, loudness (no Qt)
  models/          # model registry, .bdubpack verify/install, tier benchmark
  net/             # ONLY network code (optional model download); excluded from offline-only builds
  resources/       # fonts, icons, .qm translations, default lexicons
tests/             # unit/, component/, e2e/, ui/
tools/             # model conversion and research scripts (not shipped; may use PyTorch)
packaging/         # PyInstaller specs, portable-folder scripts, entitlements
docs/              # LICENSES.md, PORTABLE.md, architecture notes
bdub-data/         # dev data folder (git-ignored)
```

## Hard rules (do not break)

**Offline (SPEC §12)**
- No network code outside `src/bdub/net/`. Never add `requests`, `httpx`, `urllib3`, `aiohttp`, `QtNetwork`, or `QtWebEngine` to the app.
- No TCP sockets, including localhost. IPC is MessagePack over `multiprocessing.connection` (`AF_UNIX` / `AF_PIPE`) using only `send_bytes`/`recv_bytes`.
- Every process installs the network audit hook (`sys.addaudithook`) first thing at startup. Don't bypass or weaken it.
- No telemetry, crash upload, update pings, CDN fonts, or remote anything. Logs stay local, with media paths hashed by default.
- mpv runs with `ytdl=no`, `load-scripts=no`, `config=no`.

**Security (SPEC §14)**
- No pickle anywhere: no `pickle`, `torch.load`, `joblib`, `numpy.load(allow_pickle=True)`, or `multiprocessing` queues for cross-process data.
- Models load only from verified `.bdubpack` files (Ed25519 + SHA-256), in ONNX, GGUF, or CT2 format. No ONNX custom-op libraries.
- Workers accept only paths inside `bdub-data/` or user-selected media. Validate in the orchestrator.
- Archive extraction guards against zip-slip and size bombs.
- Never create, guess, print, or commit signing certificates, keys, or passwords.

**Process and performance (SPEC §5.2, §11)**
- The UI thread never runs inference, decoding, or heavy disk I/O. Use worker processes (CPU/ML) or `QThreadPool` (I/O) and send results back with signals.
- ML packages (`onnxruntime`, `ctranslate2`, `faster_whisper`, `sherpa_onnx`) are imported only inside `src/bdub/workers/`. Cold start target: ≤ 2.0 s.
- No pure-Python loops over audio samples. Vectorize with NumPy or call native libraries.
- Large data (audio) moves between processes as file paths, never over the socket.
- PyTorch is never a runtime dependency. It belongs only in `tools/`.
- T1 hardware (8 GB RAM, no GPU) must keep working.

**Qt**
- Import Qt only through `bdub.qt`.
- `text/`, `audio/`, and `workers/` stay Qt-free.
- python-mpv callbacks never touch widgets directly. Forward them with queued signals.

## Portable app (SPEC §5.6)

The app ships as one self-contained folder that runs from anywhere, including a USB drive, with no install and no admin rights.

- **Every path comes from `bdub.paths`.** It resolves `bdub-data/` next to the executable (next to the `.app` on macOS). Never use `QStandardPaths`, `Path.home()`, `~`, `%APPDATA%`, the registry, or the current working directory for app data.
- **Write only inside `bdub-data/`** (settings, library, models, cache, logs, tmp). Never write inside `_internal/` or the `.app` bundle.
- `QSettings` must always be `QSettings(str(paths.settings_file), QSettings.Format.IniFormat)`. Never use the default constructor.
- Store paths inside `bdub-data/` as **relative** paths. Identify media by content hash, not by absolute path.
- Machine-specific settings (tier, audio device, GPU) are keyed by machine fingerprint.
- No registry keys, shortcuts, file associations, or autostart unless the user explicitly opts in from Advanced. Every opt-in needs a matching "Remove".
- The app must handle a read-only data folder, a drive removed mid-dub, and a folder moved to a new path or drive letter (SPEC §5.6 rules 3–7). Never run elevated.
- Model files stay < 4 GB each (FAT32 USB drives).

## Everyday users first (SPEC §1.3, §7.0)

The target user is non-technical. Every UI change must respect these rules:

- **Simple mode is the default.** New features go into Advanced mode unless an ordinary user needs them. Simple mode shows: play controls, the **Dub to Bangla** button, the **Original / বাংলা** switch, subtitles on/off, and **Save dubbed video**.
- **Never ask what the app can decide.** Tier, models, separation, language, and audio track are automatic.
- **No jargon in Simple mode.** Use the wording in [ui-wording.md](.claude/references/ui-wording.md) (e.g. "Translating to Bangla", not "MT"). Never show ASR, TTS, model, tier, LUFS, RTF, cache, file paths, or error codes.
- **Errors:** one plain sentence saying what happened, one action button, and technical details only behind "Details".
- **Safe by default:** no data loss from any Simple-mode action; confirm and allow undo for destructive actions; mid-dub quits resume.
- **Works on first launch:** the default path never needs a download, an install, or a setup wizard.
- **Every user-facing string** goes through `tr()` with English and plain, everyday Bangladeshi Bangla (আপনি form). If you can't write natural Bangla, add a `# TODO(linguist)` and say so.
- **Accessibility:** accessible names on every interactive widget, click targets ≥ 40 px, full keyboard path, text that scales to 200%.

## Bangla text handling (SPEC §10)

- NFC-normalize all Bangla text. Preserve ZWJ/ZWNJ (e.g. র‍্য, ক্ষ, জ্ঞ).
- Never slice Bangla strings by code point. Use grapheme clusters (`regex` `\X`).
- Handle Bengali (০–৯), Latin, and Eastern Arabic digits.
- Names are transliterated, never translated. The glossary overrides MT and TTS.
- Default register: colloquial standard Bangladeshi Bangla.
- Normalizer changes need test cases. The target is ≥ 1,000 cases plus hypothesis property tests.
- Bundled fonts: Noto Sans Bengali → Hind Siliguri → Noto Serif Bengali.

## Dubbing invariants (SPEC §9)

- Time-fit order: fits → stretch ≤ 1.25× → shorter retranslation (≤ 2 tries) → TTS rate + stretch (total cap 1.35×) → overflow into silence (`S` = 700 ms) → flag "too long". Prefer rewording over speeding up. **Never cut off words.**
- Drift: cumulative offset ≤ 1.0 s. Reset toward zero at pauses ≥ 400 ms by shortening the pause, never the speech.
- Zero overlapping dub speech. Output loudness −16 ±1 LUFS, true peak ≤ −1 dBTP.
- Outputs must be deterministic for the same models, settings, and seed, because the cache depends on it.
- Cache key: xxHash3 of the first, middle, and last 8 MB + size + duration. Settings changes invalidate only the affected stages.
- Persist every utterance result so the pipeline resumes after a crash, a quit, or an unplugged drive.

## Data formats

- Project cache: `bdub-data/cache/<hash>/` with `project.bdub.json`, `audio/`, `text/` (SPEC §8.1). Details in [project-format.md](.claude/references/project-format.md).
- `project.bdub.json` is validated with pydantic v2. Bump `schema` and add a migration for any breaking change. Write it atomically.
- Model packs: [bdubpack-format.md](.claude/references/bdubpack-format.md). Follow the verification order exactly.

## Licensing (SPEC §16)

- Check each new dependency's licence (including bundled native code and model weights) before adding it, and record it in `docs/LICENSES.md`.
- PyQt6 is GPLv3 or commercial. The distribution decision is still open (SPEC Open Question 1, R12).
- Don't add GPL-only libraries (e.g. Rubber Band) or non-commercial models (NLLB, MMS-TTS) as defaults until the user decides. Prefer audiotsm or SoundTouch for time-stretching.
- FFmpeg and libmpv must be LGPL builds with no GPL-only codecs.

## Testing expectations (SPEC §15)

- Unit tests for every pure-logic change: normalizer, time-fit planner, drift scheduler, cache keys, manifest verification.
- Workers get component tests with golden inputs, run as real subprocesses, with tolerances for float audio.
- UI tests use pytest-qt, including the no-jargon and accessible-name checks. Bangla rendering checks use screenshot diffs.
- No test may need the network. The E2E suite must pass with networking disabled.
- Packaging and portability are tested on the frozen build, not only on the source tree.

## Conventions

- Type-annotate everything. mypy runs strict on `src/bdub`.
- Keep modules small and single-purpose, matching the layout above.
- Use `logging` with one logger per module. Never `print` in app code.
- Constants live in `bdub/constants.py`, never duplicated as literals.
- Spec IDs (FP-*, FD-*, FE-*, FX-*, FM-*, PR-*) may be referenced in commit messages and code comments where they explain *why*.

## References (`.claude/references/`)

Implementation detail expanded from the spec. Look things up here before guessing. Index: [README.md](.claude/references/README.md).

- [constants.md](.claude/references/constants.md): all limits and defaults
- [paths.md](.claude/references/paths.md): `bdub-data/` layout and `bdub.paths`
- [ipc-protocol.md](.claude/references/ipc-protocol.md): worker messages, handshake, error codes
- [project-format.md](.claude/references/project-format.md): `project.bdub.json`, stages, invalidation
- [bdubpack-format.md](.claude/references/bdubpack-format.md): model packs, verification order
- [time-fit.md](.claude/references/time-fit.md): time-fit and drift pseudocode + test properties
- [mpv-config.md](.claude/references/mpv-config.md): required mpv options and track commands
- [bangla-numbers.md](.claude/references/bangla-numbers.md): spoken numbers, time, dates, units
- [ui-wording.md](.claude/references/ui-wording.md): approved Bangla/English UI strings

Entries marked **(verify)** are drafts that need the Bangla linguist or a check against the bundled library version.

## Project skills (`.claude/skills/`)

| Skill | Use when |
|---|---|
| `add-worker` | Adding or changing a pipeline worker process or its IPC messages |
| `bangla-normalizer` | Fixing mispronunciations, adding normalization rules or lexicon entries |
| `simple-ui` | Any UI change: widgets, dialogs, strings, errors, settings |
| `offline-audit` | Before finishing changes to dependencies, IPC, model loading, mpv/FFmpeg options, or `bdub.net` |
| `add-dependency` | Adding or upgrading packages, native libs, models, or fonts (licence + offline + size checks) |
| `portable-build` | Building, signing, packaging, or testing the portable folder |

## Project subagents (`.claude/agents/`)

| Agent | Kind | Use when |
|---|---|---|
| `spec-reviewer` | read-only | Checking a finished change or a plan against SPEC.md and these rules |
| `offline-security-auditor` | read-only | Changes to deps, IPC, model loading, decoding, paths, `bdub.net`, packaging; before releases |
| `ux-reviewer` | read-only | Any UI change, judged as a non-technical user |
| `bangla-linguist` | edits translations, lexicon, test expectations only | Any Bangla wording: UI strings, errors, spoken forms, lexicon |
| `pipeline-engineer` | implementer | Workers, orchestrator, time-fit, mixing, cache, model integration |
| `packaging-engineer` | implementer | PyInstaller, portable folder, signing, frozen-only bugs |

Use subagents only when the user asks for them.

## Hooks (`.claude/hooks/`, registered in `.claude/settings.json`)

| Hook | Event | What it does |
|---|---|---|
| `guard_rules.py` | PreToolUse (Edit/Write/Bash) | Blocks new code in `src/bdub/` that breaks a hard rule (pickle, network imports outside `net/`, QtNetwork/WebEngine, PyQt6 outside `qt.py`, Qt in `text/`/`audio/`/`workers/`, ML imports outside `workers/`, home/registry paths outside `paths.py`, default `QSettings()`), blocks writing signing keys/certs, and blocks `pip install` / `uvx` |
| `lint_python.py` | PostToolUse (Edit/Write) | `ruff format` + `ruff check --fix` on edited `.py` files; reports what's left. Skips if ruff isn't installed; never downloads |
| `stop_reminder.py` | Stop | Shows which project checks apply to the areas changed since the last reminder |

If the guard blocks something, fix the code rather than working around it. If the block is wrong, tell the user and suggest a change to the guard.

## Open decisions (don't decide these silently)

From SPEC §22: distribution model and PyQt6 licence (Q1, Q6), source languages for v1 (Q2), voice count and accent (Q3), model hosting (Q4), hardware floor (Q5), freezer choice (Q7), Bangla-first UI default (Q9), full vs. light download (Q10), read-only fallback vs. strict no-traces (Q11). If a task depends on one, ask the user.
