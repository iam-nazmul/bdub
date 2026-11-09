# SPEC: Offline Bangla Dubbing Video Player

| | |
|---|---|
| **Working name** | BanglaDub Player (`bdub`) |
| **Platforms** | macOS 12+ (Apple Silicon + Intel), Windows 10 22H2+/11 (x64, ARM64 best-effort), Linux (x64; glibc 2.31+, X11 + Wayland) |
| **Stack** | Python 3.12 + PyQt6 (Qt 6.8 LTS) desktop app, libmpv playback, ONNX Runtime / CTranslate2 inference |
| **Distribution** | **Portable**: one self-contained folder per OS, runs from any folder or USB drive, no installation, no admin rights (§5.6) |
| **Status** | Draft v1.1 |
| **Date** | 2026-11-09 |
| **Owner** | Nazmul |

> **Changes in v1.1:** App stack moved from Tauri 2 + Rust + React to **Python 3.12 + PyQt6**. Affected sections: §5 (architecture, new §5.5 dev setup), §6.6–6.7, §7.4, §10.1, §11, §12, §14, §15, §16, §17, §19–§22. Product scope, pipeline, and quality targets are unchanged.
>
> **Also in v1.1:** ease of use for non-technical users is now a core principle: new §1.3, goal G9, Simple/Advanced modes (§7.0), no-setup installer (FM-1), usability acceptance criteria (§15.3 item 8).
>
> **Also in v1.1:** the app is **portable**: new §5.6, goal G10, and updates to packaging (§5.1, §17), models/storage (§6.5), settings (§6.6), cache (§8.1), security (§14), acceptance (§15.3), and risks (R16–R17). Installers move to P2.

---

## 1. Summary

BanglaDub Player is a desktop video player that takes a video in a foreign language (English first; Hindi, Arabic, Urdu, Spanish, Japanese, etc. later) and plays it back with a **Bangla (বাংলা) dubbed audio track**, generated **entirely on the user's machine with no network connection**.

Pipeline: separate speech from background → transcribe → translate to Bangla → synthesize Bangla speech → fit it to the original timing → mix with the preserved background audio → play in sync, optionally with Bangla subtitles.

The product is both a normal, good media player (any local file plays with no dubbing) and a dubbing tool (dub once, cache the result, play instantly afterwards, optionally export).

### 1.1 Why

- Hundreds of millions of Bangla speakers lack accessible dubbed educational, documentary, and entertainment content.
- Cloud dubbing services need uploads, accounts, and fees, and they expose private or copyrighted videos to third parties.
- Many users have unreliable or expensive internet. Local-first processing is a real requirement, not a nice-to-have.

### 1.2 Core principle

**After the one-time model download (or a bundled-models installer), the app must never require or attempt network access.** This is verifiable (see §12, §14).

### 1.3 Built for everyday users

The primary user is **not technical**: a student, a parent, a teacher. They know how to open a video and press play. They do not know what ASR, a model, a tier, or LUFS is, and they should never need to.

Design rules that apply to every screen:

1. **Works right after unzipping.** No installer, no setup choices, no separate model download in the default path. Unzip (or copy from USB) → double-click → open a video → "Dub to Bangla".
2. **One obvious action per screen.** The main window shows one big **"বাংলায় ডাব করুন / Dub to Bangla"** button. Everything else is secondary.
3. **Smart defaults, never asked.** Hardware tier, models, separation, source language, and audio track are chosen automatically. The user is never asked a question the app can answer itself.
4. **No jargon.** The UI never shows words like ASR, MT, TTS, VAD, model, tier, LUFS, RTF, or diarization in Simple mode (glossary in §7.0).
5. **Bangla first.** UI text, help, and error messages are written in plain, everyday Bangla first, with English as the second language.
6. **Plain-language errors with a next step.** Every error says what happened and what to do, with one button for it. No stack traces, codes, or file paths unless the user opens "Details".
7. **Safe to click anything.** Nothing the user does in Simple mode can lose their work or break the app. Destructive actions ask first and can be undone.
8. **Power lives behind "Advanced".** The editor, voices per speaker, glossary, quality settings, and export options stay available, but they live in Advanced mode (§7.0).

---

## 2. Goals and Non-Goals

### 2.1 Goals

| ID | Goal |
|----|------|
| G1 | Fully offline operation: ASR, translation, TTS, separation, and playback all run locally. |
| G2 | Natural, intelligible Bangla dubbing that stays in sync with the picture (≤ 250 ms typical drift, hard cap in §9.4). |
| G3 | Preserve music and effects; replace only the speech. |
| G4 | Same feature set and near-identical behavior on macOS, Windows, and Linux. |
| G5 | Usable on mid-range hardware (8 GB RAM, no discrete GPU) via a "Pre-process then play" mode. |
| G6 | Excellent Bangla text handling: correct shaping of conjuncts (যুক্তাক্ষর), Bengali numerals, numbers/dates read aloud properly. |
| G7 | Every pipeline stage is inspectable and editable (transcript, translation, voice, timing) so users can fix mistakes. |
| G8 | Shippable as a signed, portable app on each OS, with its own bundled Python runtime (users never install Python). |
| G9 | **Easy for non-technical users:** a first-time user starts the app and gets a dubbed video playing with **no help and no settings changed**, in ≤ 3 clicks after opening the file (see usability criteria in §15.3). |
| G10 | **Portable:** the whole app (program, models, settings, dubs) lives in one folder that can be copied to another computer or a USB drive and keeps working there, with no installation, no admin rights, and no traces left on the host computer. |

### 2.2 Non-Goals (v1)

- Cloud or hosted processing, user accounts, telemetry, ads.
- Lip-sync / video re-rendering of faces.
- Streaming-service DRM content (Netflix, etc.). The app plays local, non-DRM files only.
- Voice cloning of a named real person without a consent gate (see §13). Basic cloning is a v1.5 feature.
- Mobile apps and web version.
- Live broadcast or webcam dubbing (a "Live mode" exists only as an experimental stretch, §7.6).
- Dubbing *into* languages other than Bangla (architecture must allow it, UI will not expose it in v1).

---

## 3. Users and Use Cases

### 3.1 Personas

1. **Rahim, student (Dhaka).** Watches English lectures and documentaries. Laptop with 8 GB RAM, no GPU. Wants Bangla audio and Bangla subtitles.
2. **Shirin, parent.** Wants children's cartoons and educational videos in Bangla. Needs a one-click flow.
3. **Tanvir, content creator.** Dubs his own English videos for a Bangla audience. Wants to edit the translation and export an MP4/MKV with a Bangla audio track.
4. **Accessibility user.** Low vision or low literacy in English. Needs reliable audio dub plus large Bangla subtitles.
5. **NGO or educator with poor connectivity.** Runs on shared offline laptops or lab PCs without admin rights. Carries the app, models, and already-dubbed videos on one USB drive from computer to computer.

### 3.2 Key user stories

- U1. As a user, I drag a video onto the window and it plays immediately in original audio. I click **"Dub to Bangla"** and see progress. When ready, the Bangla track is selectable.
- U2. I can start watching while dubbing is still processing (progressive playback). Dubbed sections play as they become ready; not-yet-ready sections fall back to original audio with a subtitle notice.
- U3. I can switch audio between Original / Bangla Dub / Mix (Bangla louder, original quietly underneath) at any moment.
- U4. I can open the transcript editor, fix a mistranslated line, re-synthesize only that line, and hear it.
- U5. I can choose a voice (e.g., female / male / child / neutral) and speaking style, and assign voices per detected speaker.
- U6. I can export the video with the dub as an additional audio track, a replaced track, or an audio-only file, plus an `.srt`/`.vtt` Bangla subtitle file.
- U7. Next time I open the same file, the cached dub loads instantly.
- U8. I can verify the app never touches the network.

---

## 4. Product Scope Overview

```
┌──────────────────────────────────────────────────────────────┐
│              Desktop App (Python 3.12 + PyQt6)               │
│  ┌────────────┐   ┌──────────────┐   ┌────────────────────┐  │
│  │  Player UI │◄──┤ Orchestrator │──►│  Model Manager     │  │
│  │ (Qt Widgets│   │ (job graph,  │   │ (install, verify,  │  │
│  │  controls, │   │  cache, IPC) │   │  hardware select)  │  │
│  │  editor)   │   └──────┬───────┘   └────────────────────┘  │
│  └─────┬──────┘          │                                    │
│        │          ┌──────▼─────────────────────────────┐      │
│   Playback        │   Dubbing Pipeline (worker procs)  │      │
│   engine          │ Demux → Separate → VAD/ASR →       │      │
│   (libmpv in      │ Diarize → Translate → Normalize →  │      │
│   QOpenGLWidget)  │ TTS → Time-fit → Mix → Track       │      │
│        ▲          └──────┬─────────────────────────────┘      │
│        │                 │                                    │
│   ┌────┴─────────────────▼───────┐                            │
│   │  Project cache (.bdub dir)   │                            │
│   └──────────────────────────────┘                            │
└──────────────────────────────────────────────────────────────┘
```

---

## 5. Architecture

### 5.1 Technology choices

| Layer | Choice | Rationale |
|---|---|---|
| Language | **Python 3.12** (CPython), fully type-annotated | One language for UI, orchestration, and ML glue; fast iteration; the ML ecosystem (ONNX Runtime, CTranslate2, sherpa-onnx) ships first-class Python wheels. |
| App shell and UI | **PyQt6** on **Qt 6.8 LTS**, Qt Widgets (QML optional for animated overlays only) | Native look on 3 OSes, mature accessibility (VoiceOver/NVDA/Orca), HarfBuzz text shaping for Bangla in every widget, Qt Linguist i18n. No embedded browser. |
| Qt import boundary | All Qt imports go through one internal module `bdub.qt` | Keeps a future switch to PySide6 (LGPL) cheap if licensing requires it (§16, R12). |
| Playback | **libmpv** via **`python-mpv`** (ctypes), using the **render API** (`MpvRenderContext`) drawing into a `QOpenGLWidget` | Best-in-class format and codec support, hardware decode, precise A/V sync, ASS subtitle rendering (libass + HarfBuzz → correct Bangla shaping). Render API works on Wayland and macOS where `wid` embedding does not. |
| Media processing | **FFmpeg** (bundled LGPL shared build) used via **PyAV** for decode/resample and the `ffmpeg` CLI binary for export muxing | Demux, resample, encode, mux. No GPL/nonfree components. |
| Audio DSP | **NumPy**, **SciPy**, **soundfile** (libsndfile), **pyloudnorm** (EBU R128) | Vectorized mixing, ducking, crossfades, loudness. |
| ML runtime | **onnxruntime** (CPU, CoreML EP on macOS, DirectML EP on Windows, CUDA EP optional), **faster-whisper / CTranslate2** or **pywhispercpp** (whisper.cpp: Metal/Vulkan/CUDA/CPU), **ctranslate2** for MT, **sherpa-onnx** for VAD/diarization/TTS where it fits | Mature cross-platform inference with GPU acceleration where available. **PyTorch is not a runtime dependency.** |
| ML workers | Separate **worker processes** started by the orchestrator through `QProcess`, running the same frozen interpreter with a role argument (`bdub-worker --role asr`) | Avoids the GIL for heavy work, crash isolation, memory isolation, lets us unload models by ending the process. |
| IPC | **MessagePack** frames over stdlib **`multiprocessing.connection`** (`AF_UNIX` socket on macOS/Linux, `AF_PIPE` named pipe on Windows), using only `send_bytes`/`recv_bytes` (never pickle). A reader `QThread` per worker turns incoming messages into Qt signals. | No TCP sockets, including localhost; all socket use goes through Python so the network audit hook (§12) sees it. `PyQt6.QtNetwork` is not bundled at all. |
| Concurrency in the main process | Qt event loop + `QThreadPool` for I/O-bound jobs; signals/slots to the UI | The UI thread never runs inference or disk-heavy work. |
| Storage | SQLite (`sqlite3` stdlib: project index, settings) + files on disk (audio, JSON) | Simple, robust, portable. |
| Packaging | **PyInstaller** (onedir) as default, **Nuitka** standalone evaluated in M0. **Portable folder** per OS (§5.6): `.zip` (Windows), `.zip` containing the `.app` plus data folder (macOS, notarized), `.AppImage` + data folder in a `.tar.gz` (Linux). Traditional installers (`.msi`, `.dmg` drag-install, `.deb`/`.rpm`, Flatpak) are P2. | No install step and no admin rights; the onedir layout is portable by nature. Bundled interpreter, Qt, libmpv, FFmpeg. |

> **Rule:** the shipped app contains its own Python interpreter and all dependencies; nothing is installed into the user's system Python. Heavy compute runs only in native-backed libraries (NumPy, ONNX Runtime, CTranslate2, whisper.cpp). Pure-Python hot loops over audio samples are not allowed. PyTorch and other training tools are used only for model conversion and research scripts in `tools/`, never at runtime.

### 5.2 Process model

1. **Main process (Python + PyQt6):** `QApplication`, main window, menus, file access, orchestrator, job scheduler, cache, settings, IPC hub (`multiprocessing.connection.Listener`).
2. **Player surface:** `PlayerWidget(QOpenGLWidget)` hosting an `MpvRenderContext`; mpv runs its own decode/audio threads in-process. Qt widgets (controls, subtitles notice, progress strip) are layered on top as child widgets.
3. **Worker processes** (each launched on demand, killable, same frozen binary with a role flag):
   - `bdub-worker --role separate` (source separation)
   - `bdub-worker --role asr` (VAD + speech recognition + optional diarization)
   - `bdub-worker --role mt` (translation)
   - `bdub-worker --role tts` (Bangla text normalization + synthesis)
   - `bdub-worker --role mix` (time-fit, loudness, mixing, track render)
   - `bdub-worker --role decode` (FFmpeg demux/decode of untrusted media, §14)
4. Workers talk to the orchestrator using length-prefixed MessagePack over local IPC. Large payloads (audio) are passed as file paths in the project cache, never sent over the socket.
5. Workers inherit the network audit hook (§12, PR-3) and exit after an idle timeout.

### 5.3 Pipeline detail

| # | Stage | Input → Output | Default model (candidate) | Notes |
|---|---|---|---|---|
| 1 | Demux and decode | Video → 16-bit PCM 48 kHz stereo + 16 kHz mono | FFmpeg via PyAV | Handles multi-audio-track files; user picks source track. |
| 2 | Source separation | Audio → `vocals.wav` + `background.wav` | Demucs-class (htdemucs, ONNX) or lighter MDX-Net/BS-RoFormer variant, run on onnxruntime | Optional. Skipped on low-end tier (fallback: ducking, §9.5). Chunked, with overlap-add in NumPy. |
| 3 | VAD | 16 kHz mono → speech segments | Silero VAD (ONNX, via onnxruntime or sherpa-onnx) | Drives segmentation and skipping of non-speech. |
| 4 | ASR | Speech segments → text with word timestamps, language ID | Whisper-family (faster-whisper/CTranslate2 or whisper.cpp via pywhispercpp), sizes tiny→large-v3-turbo by hardware tier | Auto language detect with manual override. |
| 5 | Diarization (optional) | Segments → speaker labels | sherpa-onnx speaker segmentation + speaker embedding | Used for per-speaker voices. Verify model licenses (§16). |
| 6 | Sentence merge/split | Raw ASR → dubbing units (utterances) | Rules + punctuation restore (Python) | Units ≈ 1–12 s, respecting sentence boundaries; keep source word timestamps. |
| 7 | Machine translation | Source text → Bangla text | NLLB-200 distilled (CTranslate2, int8) and/or IndicTrans2-class models; selectable | Context window of neighboring units; glossary support; length-aware decoding (§9.3). |
| 8 | Bangla text normalization | Bangla text → speakable text | Rule engine (pure Python package `bdub.text.bn`) | Numbers, dates, times, currency (৳, $), units, abbreviations, Latin-script words, Bengali/Arabic digits, punctuation. See §10. Text-only, so pure Python is fast enough. |
| 9 | TTS | Normalized text + voice → waveform | VITS/Piper-class ONNX Bangla voices (onnxruntime / sherpa-onnx); shortlist in §16 | Real-time factor target ≤ 0.5× on tier-2 hardware. Multi-voice. |
| 10 | Time-fit | TTS clip + target window → fitted clip | Rule-based planner (Python) + WSOLA/phase-vocoder time stretch (audiotsm, SoundTouch bindings, or Rubber Band; ±25%) and retranslate-shorter loop | See §9.3 and licence notes in §16. |
| 11 | Mix | Dub clips + background + (optional) original → output track | NumPy mixer + pyloudnorm (EBU R128, −16 LUFS stereo target) | Ducking, crossfades, per-speaker gain. |
| 12 | Package | Track + subtitles + metadata → cache / export | FFmpeg mux | Writes `.bdub` project (§8). |

Stages 4–12 run **per chunk** so progressive playback (§7.2) can begin before the full file is done.

### 5.4 Hardware tiers (auto-detected, user-overridable)

| Tier | Typical hardware | Defaults |
|---|---|---|
| **T1 Lite** | ≤ 8 GB RAM, no usable GPU, older CPU | Whisper small/base int8, NLLB-600M int8, no source separation (ducking instead), 1 voice, pre-process mode only. |
| **T2 Standard** | 16 GB RAM, modern 6+ core CPU or Apple M-series / integrated GPU | Whisper medium/turbo, NLLB-1.3B, light separation, multi-voice, progressive playback. |
| **T3 Pro** | 32 GB+ RAM, discrete GPU (≥ 8 GB VRAM) or M-series Pro/Max | Whisper large-v3(-turbo), larger MT model, full separation, high-quality TTS, faster than real time. |

The Model Manager benchmarks the machine on first run (≈ 20 s synthetic test, run in a worker process) and recommends a tier.

### 5.5 Development setup and repository layout

**Toolchain**

| Concern | Tool |
|---|---|
| Python version | 3.12 (pinned in `.python-version`) |
| Env and dependency management | **uv** (`pyproject.toml` + `uv.lock`), separate dependency groups: `runtime`, `dev`, `tools` (conversion; may include PyTorch) |
| Lint and format | **ruff** (lint + format) |
| Type checking | **mypy** (strict on `bdub/*` except generated code) or pyright |
| Tests | **pytest**, **pytest-qt**, **hypothesis** (normalizer and time-fit property tests), pytest-benchmark |
| Qt resources and i18n | `pylupdate6` → Qt Linguist `.ts` → `lrelease` `.qm`; `.ui` files optional (Qt Designer), loaded via `uic` at build time |
| Pre-commit | ruff, mypy, license-header check, `uv lock --check` |
| Freezing | PyInstaller spec per OS in `packaging/` |

**Layout**

```
bdub/
  pyproject.toml  uv.lock
  src/bdub/
    __main__.py          # entry: GUI or `--role <worker>`
    qt.py                # single Qt import boundary (PyQt6)
    app/                 # QApplication setup, main window, menus, settings dialogs
    ui/                  # widgets: player controls, editor panel, model manager, wizard
    player/              # mpv render context, PlayerWidget, track/sub management
    orchestrator/        # job graph, scheduler, cache, IPC server, worker supervisor
    workers/             # separate.py asr.py mt.py tts.py mix.py decode.py
    text/bn/             # normalizer, lexicon, transliteration, register rules
    audio/               # time-fit planner, stretch, ducking, mixer, loudness
    models/              # model registry, .bdubpack verify/install, tier benchmark
    net/                 # ONLY network code (model download/update); excluded in offline-only build
    resources/           # fonts, icons, translations (.qm), default lexicons
  tests/                 # unit, component, e2e, ui
  tools/                 # model conversion and research scripts (not shipped)
  packaging/             # PyInstaller specs, installer scripts, entitlements, AppImage recipe
  docs/                  # LICENSES.md, architecture notes
```

Developers run the app with `uv run bdub` (GUI) and individual workers with `uv run bdub --role asr --stdio` for debugging. In development the data folder is `./bdub-data/` in the repo root (git-ignored).

### 5.6 Portable mode

The app is distributed and runs as one self-contained folder. Nothing is installed, and nothing is written outside this folder except OS temp files that are cleaned up on exit.

**Folder layout (Windows and Linux)**

```
BanglaDub/
  BanglaDub.exe            # or BanglaDub.AppImage on Linux
  _internal/               # frozen Python, Qt, libmpv, FFmpeg, ML runtimes (read-only)
  bdub-data/               # everything the app writes
    settings.ini           # QSettings, IniFormat, explicit path
    library.sqlite         # project index
    models/                # installed model packs (starter pack shipped here)
    cache/<hash>/          # dub projects (§8.1)
    lexicon/               # user pronunciation lexicon, glossary
    logs/
    tmp/                   # scratch files, cleared on start and exit
  README-বাংলা.txt / README.txt
```

**macOS:** `BanglaDub/BanglaDub.app` + `BanglaDub/bdub-data/` side by side. Data is never written inside the `.app` bundle, since that breaks its code signature.

**Rules**

1. **One path resolver.** All locations come from `bdub.paths`, which finds `bdub-data/` next to the executable (or next to the `.app` on macOS). Code must never call `QStandardPaths`, `os.path.expanduser("~")`, `%APPDATA%`, or the Windows registry for app data.
2. **No traces on the host.** No registry keys, no files in the user profile, no shortcuts, no file associations, no services, no autostart. Qt settings use `QSettings(path, IniFormat)`. Temp files go to `bdub-data/tmp/` where possible. Runtime caches that libraries write elsewhere (e.g. CoreML compiled models) are redirected via env/options or listed in `docs/PORTABLE.md`.
3. **Read-only fallback.** If `bdub-data/` is not writable (read-only USB, `Program Files`, macOS App Translocation from a quarantined download), the app falls back to a per-user data folder and shows one plain message: "Running in read-only place. Your dubs will be saved on this computer instead." On macOS the message also explains to move the folder out of Downloads/unzip it first.
4. **Moves between computers.** Paths stored in `project.bdub.json` and the library are **relative** to `bdub-data/` for anything inside it. Media files are found by content hash (§8.1), so a video on a different drive letter or mount point is re-linked automatically; if the video is missing, the user gets "Find video…" with the dub still intact.
5. **Hardware re-detection.** The hardware tier (§5.4) is stored per machine (keyed by a hashed machine fingerprint), so moving the folder to a weaker or stronger computer picks the right defaults automatically.
6. **USB-friendly I/O.** Writes are batched and sequential (FLAC/M4A, not many tiny files); the SQLite DB uses WAL with periodic checkpoints; the app tolerates the drive being slow. If the folder is on a removable drive with < 2 GB free, the app warns before dubbing. Model files must stay < 4 GB each so they work on FAT32 drives; exFAT/NTFS is recommended in the README.
7. **Safe removal.** If the drive is unplugged mid-dub, the app shows "The drive was removed. Plug it back in to continue." and resumes from the last saved utterance (§11.2), with no database corruption.
8. **Optional OS integration (Advanced, opt-in).** "Make BanglaDub the default video player" and "Add desktop shortcut" are user-triggered, per-user (no admin), and have a matching "Remove" button. They are off by default.
9. **Updating** means replacing the program files (`BanglaDub.exe` + `_internal/`, or the `.app`) and keeping `bdub-data/`. The app migrates settings and the project schema on first start of a newer version and never downgrades data silently.
10. **Size.** The default portable download includes the starter model pack (≈ 2.5–3 GB). A "light" download without models also exists; it asks for a `.bdubpack` file on first dub.

---

## 6. Functional Requirements

Priority: **P0** = must ship in v1.0, **P1** = v1.0 if time permits / v1.1, **P2** = later.

### 6.1 Player core

| ID | Requirement | Pri |
|---|---|---|
| FP-1 | Open files via dialog, drag-and-drop (onto the window or onto the app icon/executable), CLI argument, and recent list. OS "Open with"/default-player registration only when the user opts in (§5.6 rule 8). | P0 |
| FP-2 | Play MP4, MKV, WebM, AVI, MOV, TS, FLV, OGV, plus common audio-only files, using libmpv codecs. Hardware decode where available. | P0 |
| FP-3 | Standard controls: play/pause, seek (click, drag, ±5/±10 s keys), speed 0.25–4× (audio pitch-corrected), volume/mute, fullscreen, frame-step, A-B loop. | P0 |
| FP-4 | Audio track menu lists every embedded track plus **"Bangla Dub (generated)"** and **"Bangla Mix"** (added to mpv as external audio tracks via `audio-add`). | P0 |
| FP-5 | Subtitle menu: embedded tracks, external `.srt/.ass/.vtt` load, plus **"Bangla (generated)"** and **"Original (ASR)"**. Dual-subtitle display (original + Bangla, via mpv `secondary-sid`) supported. | P0 |
| FP-6 | Subtitle styling: font, size, color, outline, background box, position. Default Bangla font stack: Noto Sans Bengali → Hind Siliguri → system fallback; bundled, registered with `QFontDatabase.addApplicationFont` for the UI and passed to mpv via `sub-fonts-dir`. | P0 |
| FP-7 | Playlist and folder queue, next/previous, remember position per file. | P1 |
| FP-8 | Chapters and thumbnails on the seek bar. | P1 |
| FP-9 | Picture-in-picture / always-on-top. | P2 |

### 6.2 Dubbing

| ID | Requirement | Pri |
|---|---|---|
| FD-1 | **One-click "Dub to Bangla"** using the recommended tier settings. | P0 |
| FD-2 | **Pre-process mode:** process the whole file in the background with a progress panel (per-stage, ETA, cancel/pause/resume). | P0 |
| FD-3 | **Progressive mode:** begin playback once the first N seconds (default 60 s buffer) are dubbed; continue processing ahead of the playhead; auto-pause with "Dubbing is catching up…" if the playhead overtakes (user-configurable: pause vs. fall back to original). | P0 (T2/T3) |
| FD-4 | Source language: auto-detect, override per file. Supported at launch: English (P0); Hindi, Urdu, Arabic, Spanish, French, German, Chinese, Japanese, Korean, Russian, Turkish (P1). | P0/P1 |
| FD-5 | Instantly toggle Original / Dub / Mix during playback with no re-processing and ≤ 150 ms switch latency. | P0 |
| FD-6 | Per-speaker voice assignment when diarization is on; default auto-assign by detected gender/age-class heuristic. | P1 |
| FD-7 | Voice catalog with preview; at least 2 distinct Bangla voices (1 female, 1 male) at v1.0, more over time. Speaking-rate and pitch sliders. | P0 |
| FD-8 | Glossary: user-defined source→Bangla term mappings (names, brands, technical terms), plus "do not translate / transliterate" list. Applied during MT and TTS. | P1 |
| FD-9 | Keep-original-for-segments: user can mark ranges (songs, foreign interviews) to leave in the original language. Singing detection to auto-suggest. | P1 |
| FD-10 | Cached results: a re-opened file with identical content hash and settings loads dub instantly. Settings changes invalidate only the affected stages. | P0 |
| FD-11 | Batch dubbing queue for multiple files. | P1 |
| FD-12 | Voice cloning from a short reference sample, with consent gate. | P2 |
| FD-13 | Emotion / emphasis carry-over from source prosody. | P2 |

### 6.3 Editor (transcript / translation / voice / timing)

| ID | Requirement | Pri |
|---|---|---|
| FE-1 | Side panel (`QTableView` + custom model/delegate) lists utterances: timecode, speaker, source text, Bangla text, status. Click seeks the video; playback highlights the current row. | P0 |
| FE-2 | Edit source text or Bangla text inline; **"Re-dub line"** re-runs MT (if source edited) → normalize → TTS → time-fit → mix for that utterance only and hot-swaps the audio. | P0 |
| FE-3 | Adjust utterance start/end, split, merge, delete, add. | P1 |
| FE-4 | Per-utterance voice, rate, pitch, gain override. | P1 |
| FE-5 | Alternative translations: show top-k MT candidates and choose. | P1 |
| FE-6 | Undo/redo across the edit session (`QUndoStack`). | P0 |
| FE-7 | Import/export transcript and translation as SRT/VTT/JSON/CSV. Importing a user-provided Bangla SRT skips MT and goes straight to TTS ("bring your own translation"). | P1 |

### 6.4 Export

| ID | Requirement | Pri |
|---|---|---|
| FX-1 | Export video with dub **added** as new audio track (original kept), or **replacing** the audio. Container choice: MKV, MP4. Video stream copied (no re-encode) by default. | P0 |
| FX-2 | Export audio-only (WAV, FLAC, MP3, AAC/M4A, Opus) for dub-only or mix. | P0 |
| FX-3 | Export subtitles (SRT, VTT, ASS) for original and Bangla. | P0 |
| FX-4 | Hard-burned Bangla subtitles (re-encode) with codec/quality presets (H.264/H.265/AV1, hardware encoders when present). | P1 |
| FX-5 | Export stems (vocals/background/dub) for use in other editors. | P2 |

### 6.5 Models and storage

| ID | Requirement | Pri |
|---|---|---|
| FM-1 | **No setup needed by default:** the standard portable download includes a starter model pack (T1 models + 2 voices) in `bdub-data/models/`, so dubbing works on first launch with no wizard. A short first-run screen asks only for UI language (pre-selected from the OS locale) and shows a 3-step "how it works" card. Higher-quality packs are offered later as an optional upgrade ("Get better quality") from a file/USB or, if the user chooses, from the internet. | P0 |
| FM-2 | Model Manager screen: lists installed models, sizes, versions, licenses, hash-verified status; install, update, remove; disk usage. | P0 |
| FM-3 | Models distributed as signed archives with SHA-256 manifest; verified before use. | P0 |
| FM-4 | Import models from a local `.bdubpack` file (for offline-only distribution via USB, shared drives). | P0 |
| FM-5 | The only network feature, **optional "Download models" and "Check for updates"**, is off until the user explicitly initiates it, runs in a separate, clearly labeled dialog, lives entirely in the `bdub.net` package (stdlib `urllib.request` over HTTPS), and is fully removable via the **offline-only build** (`BDUB_OFFLINE_ONLY=1` at freeze time excludes `bdub.net` from the bundle). | P0 |
| FM-6 | Cache management: per-project size, "Clear cache", auto-evict by LRU above a user-set cap (default 20 GB, or 50% of free space on the drive holding `bdub-data/`, whichever is smaller). Projects the user marked "Keep" are never evicted. | P0 |
| FM-7 | **Share a dub:** export a single dub project as a `.bdubproj` file (subtitles, dub track, settings; no models, no source video) and import it on another copy of the app, so a dub made once can be carried to other computers. | P1 |

### 6.6 Settings

Stored in `bdub-data/settings.ini` via `QSettings(path, QSettings.Format.IniFormat)` plus `bdub-data/library.sqlite` for project data (§5.6). Machine-specific values (hardware tier, audio device, GPU choice) are stored per machine fingerprint so they don't carry over wrongly to another computer.

General (language, theme, UI scale, default folders), Playback (hardware decode, audio device, output sample rate, normalization), Dubbing (default tier, default voice, mix balance, ducking depth, progressive buffer, source-language preference), Subtitles (style), Performance (worker threads, GPU use on/off, memory cap, pause-when-on-battery), Privacy (offline guard, log level, crash reports **local only**), Advanced (model paths, custom ffmpeg flags).

### 6.7 UI localization

App UI languages at v1.0: **Bangla (বাংলা) and English**. All strings wrapped in `self.tr()` / `QCoreApplication.translate()`, extracted with `pylupdate6`, translated in Qt Linguist, shipped as `.qm`. Plurals use Qt's `%n` forms. Bangla numerals optional for UI numbers (formatted via `QLocale(QLocale.Language.Bengali, QLocale.Country.Bangladesh)`).

---

## 7. User Experience

### 7.0 Simple mode and Advanced mode

The app opens in **Simple mode**, which is the default for everyone. A user switches with *Menu → Advanced mode*, and the choice is remembered.

| | Simple mode (default) | Advanced mode |
|---|---|---|
| Main window | Video, play controls, big **Dub to Bangla** button, audio switch (**Original / বাংলা**), subtitles on/off | Adds the editor panel, full audio/subtitle track menus, stage-by-stage progress |
| Dub options | Voice: **Female / Male**; Quality: **Faster / Better**. Nothing else. | Everything in §7.3 |
| Settings | Language, text size, subtitle size, "Clear space used by dubs" | All of §6.6 |
| Export | **Save dubbed video** (one button: MP4, dub added as an extra track, Bangla subtitles included) | All of §6.4 |
| Errors | Plain message + one action button + "Details" link | Same, with technical details expanded |

**Words shown to users (Simple mode)**

| Internal term | Shown in English | Shown in Bangla |
|---|---|---|
| Separation | Separating voices from music | কণ্ঠ ও সংগীত আলাদা করা হচ্ছে |
| ASR | Listening to the video | ভিডিও শোনা হচ্ছে |
| MT | Translating to Bangla | বাংলায় অনুবাদ করা হচ্ছে |
| TTS | Creating Bangla voice | বাংলা কণ্ঠ তৈরি হচ্ছে |
| Time-fit + mix | Matching the voice to the video | ভিডিওর সাথে মেলানো হচ্ছে |
| Tier / model | Quality: Faster / Better | মান: দ্রুত / উন্নত |
| Cache | Space used by dubs | ডাবের জন্য ব্যবহৃত জায়গা |

Bangla wording is reviewed by the Bangla linguist for plain, everyday register (not formal/literary).

**Simple-mode behaviour rules**

- Progress shows one bar, one plain-language step name, and a human time estimate ("about 10 minutes left"). Never percent per stage or RTF.
- When dubbing finishes, the audio switches to Bangla automatically (users can turn this off in Settings).
- If the machine is slow, the app quietly uses pre-process mode and says "Your dub will be ready in about N minutes. You can keep watching in the original language."
- A file the app cannot play or dub gets one sentence explaining why (e.g., "This video is protected and can't be dubbed").
- Leaving the app mid-dub is safe: on reopening the video the app says "Continue dubbing?" and resumes.
- Tooltips on every button, in the UI language.

### 7.1 Main window

```
┌────────────────────────────────────────────────────────────────┐
│ File  Playback  Dub  Subtitles  Tools  Help                    │
├──────────────────────────────────────────┬─────────────────────┤
│                                          │ ▸ Dub  ▸ Transcript │
│               VIDEO                      │ ───────────────────  │
│                                          │ 00:12 [S1] Hello…   │
│     (Bangla subtitle rendered here)      │       হ্যালো…        │
│                                          │ 00:15 [S2] …        │
├──────────────────────────────────────────┤                     │
│ ▶ ━━━━●━━━━━━━━━━━━━━  12:03 / 48:20     │ [Re-dub line]       │
│ 🔊  Audio: [Bangla Dub ▾]  Sub: [Bangla ▾]│                     │
│ Dubbing: ████████░░ 78% · ETA 6 min      │                     │
└──────────────────────────────────────────┴─────────────────────┘
```

This is the **Advanced mode** layout. In Simple mode the editor panel is hidden, and the bottom bar shows only play controls, the **Dub to Bangla** button (which becomes the **Original / বাংলা** switch once a dub exists), and a subtitles toggle.

Implemented as a `QMainWindow` with the player as the central widget and the editor as a `QDockWidget` (dockable, collapsible).

### 7.2 Primary flow

1. Open video → plays instantly (original audio).
2. Banner: **"Dub to Bangla"** (with a small ⚙ for options).
3. Language detected, chosen tier/voice shown. Click **Start**.
4. Progress strip shows stage and ETA; the user may watch (progressive mode), or minimize.
5. When ready: toast "বাংলা ডাব প্রস্তুত / Bangla dub ready" (and an OS notification via `QSystemTrayIcon.showMessage`) and audio switches (if the user enabled auto-switch).

### 7.3 Dub options dialog

Source language, source audio track, voice(s), quality tier (Fast / Balanced / Best), separation (Off / Light / Full), subtitles (generate Bangla / also original / none), Bangla register (see §10.4), mode (Pre-process / Progressive).

### 7.4 Accessibility

- Large click targets (≥ 40 px) and readable default text size; UI scale follows the OS and can be raised to 200%.
- Full keyboard navigation; visible focus rings; tab order set explicitly on every dialog.
- Every interactive widget has `accessibleName` / `accessibleDescription`; custom widgets (seek bar, utterance delegate) implement `QAccessibleInterface` so they are exposed to VoiceOver (macOS), NVDA/Narrator (Windows, UI Automation), and Orca (Linux, AT-SPI).
- High-contrast theme (Qt palette + stylesheet); subtitle size up to 200%; reduced-motion mode.
- Subtitles meet WCAG contrast (≥ 4.5:1) by default.

### 7.5 Keyboard shortcuts (defaults; rebindable)

`Space` play/pause · `←/→` ±5 s · `Shift+←/→` ±30 s · `↑/↓` volume · `M` mute · `F` fullscreen · `A` cycle audio track · `S` cycle subtitle · `D` toggle Original/Dub · `[ ]` speed · `E` open editor · `Ctrl/Cmd+D` start dubbing · `Ctrl/Cmd+O` open · `Esc` leave fullscreen.

Implemented with `QAction` + `QKeySequence` (standard keys mapped per platform); bindings stored in settings.

### 7.6 Experimental: Live mode (P2, off by default)

Dub in near real time (target end-to-end latency ≤ 8 s) with a delayed video stream. Only offered on T3 hardware. Marked "Experimental" in the UI.

---

## 8. Data Model and File Formats

### 8.1 Project cache layout

Per video, keyed by content hash (xxHash3 via the `xxhash` package, of first/last/middle 8 MB plus size + duration) so renamed/moved files are recognized:

```
<cache_root>/<hash>/
  project.bdub.json        # manifest, settings snapshot, stage status, schema version
  audio/
    source.wav             # decoded (optional, can be regenerated)
    vocals.flac
    background.flac
    dub_clips/<utt_id>.flac
    dub_mix.m4a            # rendered full track (when complete)
  text/
    asr.json               # words + timestamps + confidences
    translation.json       # per-utterance MT output + candidates
    subs_bn.srt / subs_src.srt
  logs/
```

`<cache_root>` is `bdub-data/cache/` (§5.6). `media.path` is stored as last-known location only; the content hash is the real identity, so moved or re-lettered drives re-link automatically.

### 8.2 `project.bdub.json` (excerpt)

Validated with **pydantic v2** models (`bdub.orchestrator.schema`); `schema` field drives migrations.

```json
{
  "schema": 1,
  "media": { "path": "/Users/x/lec01.mp4", "hash": "xxh3:9a1f…", "duration_ms": 2900000, "audio_track": 0 },
  "settings": {
    "src_lang": "en", "tgt_lang": "bn", "tier": "T2",
    "separation": "light", "register": "colloquial_bd",
    "voices": { "S1": "bn-female-1", "S2": "bn-male-1" }
  },
  "stages": { "asr": "done", "mt": "done", "tts": "running", "mix": "pending" },
  "utterances": [
    {
      "id": "u0001", "start_ms": 12040, "end_ms": 15120, "speaker": "S1",
      "src": "Hello and welcome to the course.",
      "bn": "কোর্সে আপনাদের স্বাগতম।",
      "bn_spoken": "কোর্সে আপনাদের স্বাগতম।",
      "tts": { "voice": "bn-female-1", "rate": 1.08, "dur_ms": 2950, "file": "dub_clips/u0001.flac" },
      "flags": ["edited_by_user"]
    }
  ],
  "models": { "asr": "whisper-medium-int8@1.2", "mt": "nllb-1.3b-int8@1.0", "tts": "bn-vits-v2@1.1" }
}
```

### 8.3 Model pack (`.bdubpack`)

A zip containing `manifest.json` (id, version, type, size, SHA-256 per file, license SPDX, source URL, required runtime version, minimum tier) plus model files. Manifest is signed with the project's Ed25519 key (verified with the `cryptography` package); the public key is embedded in the app. Extraction guards against path traversal (zip-slip) and size bombs.

---

## 9. Dubbing Quality Requirements

### 9.1 Targets (measured on the benchmark set, §15)

| Metric | Target (v1.0, English→Bangla, T2) |
|---|---|
| ASR WER (clean English speech) | ≤ 8% (≤ 15% on noisy/accented set) |
| MT quality | chrF++ ≥ baseline NLLB-1.3B on FLORES-200 eng→ben; human adequacy ≥ 3.8/5 |
| TTS intelligibility | CER via Bangla ASR round-trip ≤ 6%; MOS ≥ 3.8/5 (listener panel) |
| A/V sync | 90% of utterances start within ±250 ms of source speech start; none drift > 1.0 s |
| Speech overflow | ≤ 5% of utterances need to run into the next gap; 0 overlapping dub speech |
| Loudness | Output mix −16 ±1 LUFS (stereo), true peak ≤ −1 dBTP |

### 9.2 Segmentation

Dubbing units follow sentence boundaries where possible, 1–12 s, merged across short pauses (< 400 ms) when same speaker. Bangla is SOV and often differs in length; segmenting by sentence keeps MT coherent.

### 9.3 Time-fit strategy (critical)

Bangla output often differs in duration from English. For each utterance with available window `W` (source speech span, extended into adjacent silence up to a limit `S`, default 700 ms), and synthesized duration `D`:

1. If `D ≤ W`: place at source start (default anchor: start-aligned, option: center-aligned). Done.
2. If `D ≤ W·1.25`: time-stretch the clip by `D/W` (max +25% speed; WSOLA / Rubber Band-class, formants preserved).
3. Else, **length-constrained retranslation**: re-run MT with a shorter-output constraint (length penalty / "concise" prompt style / drop filler words), then re-synthesize; repeat up to 2 times.
4. Else, raise the TTS native speaking rate (up to +20%) and combine with stretch (total cap 1.35×; beyond this intelligibility degrades).
5. Else, **allow overflow** into following silence up to `S`; if still too long, shift later within the *gap budget* but cap cumulative drift (§9.4).
6. Else, flag the utterance "too long" in the editor and subtitle, and play it at the cap.

Always prefer rewording over speeding up. Never cut off words.

### 9.4 Drift control

A global scheduler tracks cumulative offset. Rule: at each natural pause ≥ 400 ms the offset resets toward zero (shorten pause, never the speech). Hard cap: offset ≤ 1.0 s; beyond it, enforce steps 3–4 more aggressively.

### 9.5 Background preservation

- **Full/Light separation:** mix = `background × g_b + dub × g_d`.
- **No separation (T1):** ducking: original audio attenuated by 18–25 dB during speech (VAD-driven, 80 ms attack / 300 ms release) or fully muted outside music-only regions, with the user-selectable "Keep original quietly underneath" (default −22 dB).
- Dub speech is equalized (light de-ess, gentle compression) and optionally given a small room reverb matched to the original (P2).

### 9.6 Non-speech sound

Laughter, applause, music, effects remain from the background stem. Singing is detected (music classifier) and left in the original by default (FD-9).

---

## 10. Bangla Language Requirements

### 10.1 Text normalization for TTS (rule engine, unit tested)

Implemented as the pure-Python package `bdub.text.bn` (no Qt dependency, so it can be tested and reused on its own).

- Numbers (cardinal, ordinal, decimal, fraction, percent, ranges): `1,250` → "এক হাজার দুইশো পঞ্চাশ"; `3rd` → "তৃতীয়"; `25%` → "পঁচিশ শতাংশ".
- Bengali (০–৯), Latin (0–9), and Eastern Arabic digits all handled.
- Dates and times in Gregorian and Bangla calendar contexts; `12:30 PM` → "দুপুর সাড়ে বারোটা" or digital style (setting).
- Currency: ৳ / Tk / BDT, ₹, $, €, £ and units (km, kg, °C, GB…) → spoken Bangla.
- Abbreviations and acronyms (spelled out vs. word-read, dictionary + heuristics), e.g. "AI", "NASA", "Dr.".
- **Latin-script words:** transliterate to Bangla script using a pronunciation lexicon (names, brands, technical terms); fallback G2P. Glossary overrides.
- Punctuation → prosody cues (দাঁড়ি `।`, comma pauses, question intonation).
- Unicode NFC normalization (`unicodedata.normalize`); handle ZWJ/ZWNJ correctly (e.g., র‍্য, ক্ষ, জ্ঞ) so TTS front-end and subtitle renderer both treat conjuncts consistently. Grapheme-cluster-aware operations use the `regex` package (`\X`), never naive `str` slicing.

### 10.2 Grapheme-to-phoneme and prosody

Use the TTS model's own G2P/phoneme set; maintain a fixable pronunciation lexicon (`lexicon.bn.tsv`) the user can extend in the editor ("Fix pronunciation").

### 10.3 Subtitles and rendering

- Video subtitles: shaping via HarfBuzz (libass inside libmpv). UI text (editor, menus): shaping via Qt's HarfBuzz text engine. Bundled fonts: Noto Sans Bengali, Hind Siliguri, Noto Serif Bengali. Test corpus covering all conjuncts and reph/vowel-sign reordering.
- Line breaking by Bangla word boundaries and length (≤ 42 Latin-equivalent columns, ≤ 2 lines, ≤ 17 chars/s reading speed by default; configurable).
- Optional Bengali numerals in subtitles.

### 10.4 Register and dialect

Setting **Bangla register**:
- **Colloquial Standard (Bangladesh)**: default for conversation, vlogs.
- **Formal / Shuddho**: news, documentaries, lectures.
- **Colloquial (West Bengal)** (P1).
Implemented via MT prompt/style tags where the model supports it and via post-edit rules (verb forms: করছি/করতেছি excluded; pronouns তুমি/আপনি/তুই selected by speaker relationship heuristics + editor override). Honorific level (আপনি/তুমি) is a visible per-speaker setting.

### 10.5 Names

Person and place names transliterated, not translated; glossary-first. NER-assisted protection of names during MT.

---

## 11. Non-Functional Requirements

### 11.1 Performance

| Metric | T1 | T2 | T3 |
|---|---|---|---|
| Full pipeline speed (processing time ÷ media time) | ≤ 3.0× | ≤ 1.0× | ≤ 0.4× |
| Time to first dubbed audio (progressive mode) | n/a | ≤ 90 s | ≤ 30 s |
| Peak RAM during dubbing (all processes) | ≤ 5.5 GB | ≤ 10 GB | ≤ 20 GB |
| Playback-only CPU (1080p, HW decode) | ≤ 8% of one core class | same | same |
| Cold start to window | ≤ 2.0 s | | |
| Open file to first frame | ≤ 1.0 s | | |
| Dub toggle latency | ≤ 150 ms | | |

Python-specific rules:

- The main window must appear before any ML library is imported. ML packages (`onnxruntime`, `ctranslate2`, `faster_whisper`, `sherpa_onnx`) are imported **only inside worker processes**.
- Frozen builds use PyInstaller **onedir** (not onefile) to avoid unpack-on-launch delay.
- The UI thread never blocks for > 16 ms; a debug-build watchdog logs any event-loop stall > 100 ms.

Workers load models lazily and exit after idle (default 120 s). Pipeline stages are scheduled to avoid simultaneous peak-memory models (stage-serialized on T1).

### 11.2 Reliability

- Pipeline is **resumable**: every utterance result is persisted; a crash or quit resumes at the last completed chunk.
- Worker crash does not take down the player; the orchestrator detects `QProcess` exit, restarts the worker, and retries the chunk (max 2), then flags it.
- Corrupt/partial media tolerated; clear error messages.
- Deterministic outputs given same models, settings, and seed (for cache validity).
- Unhandled exceptions in the main process are caught by a `sys.excepthook` that writes a local crash report and shows a dialog instead of exiting; `faulthandler` is enabled in all processes and writes native crash traces to the local log directory.

### 11.3 Power and thermals

"Quiet mode" caps CPU/GPU utilization (worker thread counts, ORT intra-op threads, lowered process priority); auto-throttle on battery (option to pause dubbing on battery below 30%).

### 11.4 Disk

Typical cache for 1 hour of video: ≈ 0.8–1.5 GB with FLAC stems (configurable lossy). Models: T1 bundle ≈ 2.5 GB, T2 ≈ 6 GB, T3 ≈ 12 GB (to be fixed after model selection). Program files (interpreter + Qt + libmpv + FFmpeg + ML runtimes, no models): target ≤ 400 MB. Portable download with starter pack: ≈ 2.5–3 GB.

### 11.5 Compatibility

macOS 12+ (Metal; CoreML for ONNX where it helps), Windows 10 22H2+/11 (DirectX 11/12; DirectML), Linux (Vulkan/OpenGL; PulseAudio/PipeWire/ALSA output). Qt 6.8 LTS platform plugins bundled: `cocoa` (macOS), `windows` (Windows), `xcb` + `wayland` (Linux). OpenGL 3.3 core (or GLES 3.0) required for the mpv render path; software fallback via mpv's `vo=gpu` with a separate native window if GL init fails.

---

## 12. Offline and Privacy Requirements

| ID | Requirement |
|---|---|
| PR-1 | No outbound network connections during normal operation. No analytics, telemetry, crash upload, update ping, font/CDN loading, or license checks. |
| PR-2 | The app embeds no browser engine and no Qt networking: `QtWebEngine*` and `QtNetwork` are excluded from every build (enforced in the PyInstaller spec and by a bundle-content check). All socket use is in Python (stdlib), so the audit hook in PR-3 covers it. External links open in the default browser (`QDesktopServices.openUrl`) only on a user click and after a confirmation. |
| PR-3 | **Runtime network guard:** every process installs a `sys.addaudithook` at startup that blocks and logs `socket.connect`, `socket.getaddrinfo`, and `socket.sendto` for any non-`AF_UNIX` family (except inside an explicit user-started `bdub.net` session in non-offline builds). A **"Network guard"** self-test in *Settings → Privacy* runs the pipeline under an OS-level deny-network check and reports "0 connection attempts". CI also runs full E2E under `unshare -n` (Linux) / firewall rules (Win/macOS runners). |
| PR-4 | Media, transcripts, and voices never leave the machine. Logs stay local, with media paths hashed unless the user opts in to full paths for debugging. |
| PR-5 | Optional model/update download (FM-5) is a separate, explicit, auditable code path (`bdub.net`); the offline-only build removes it entirely, and a CI check asserts that the frozen offline-only bundle contains no `bdub.net`, no `QtNetwork`/`QtWebEngine`, and no `requests`/`httpx`/`urllib3`. |
| PR-6 | Installers and model packs are verifiable offline (signature + hash). |

> Note: the audit hook catches Python-level socket use. Native libraries (onnxruntime, libmpv, FFmpeg) are configured to avoid network use (mpv `ytdl=no`, FFmpeg built without network protocols or with `protocol_whitelist=file,pipe`), and the OS-level test in PR-3 is the backstop.

---

## 13. Safety, Legal, and Ethics

- **Copyright:** Product dubs files the user already has locally; it does not circumvent DRM and must refuse encrypted/DRM-protected streams. EULA states users are responsible for rights to the content.
- **Synthetic voice labeling:** Exported dubbed files get a metadata tag (`comment`/`encoded_by`: "AI-generated Bangla dub, BanglaDub Player") unless disabled in advanced settings; the UI displays an "AI dub" badge during playback by default.
- **Voice cloning (P2):** requires an explicit consent checkbox ("I have the right/permission to use this voice"), no bundled celebrity voices, and no cloning from the video's own speakers without confirmation.
- **Model licenses:** Every bundled model's license must be compatible with the distribution model (§16, Risks R1). The Model Manager displays licenses; non-commercial models are excluded from the default distribution or flagged "non-commercial only".
- **Content accuracy:** MT may err. First-run notice and a persistent "Machine translated" label on generated subtitles; the editor makes corrections easy.
- **Children's content:** no special handling, but no network means no data collection from minors (a documented plus).

---

## 14. Security

- **File access:** only user-selected paths (dialogs, drag-and-drop, CLI args) plus the app's own `bdub-data/` folder (§5.6). The app writes nowhere else on the host computer.
- **Portable-specific:** the app never needs admin/root rights and refuses to run elevated (it shows a message instead), so a shared lab PC isn't modified. DLL search order on Windows is restricted to the app's own `_internal/` folder (`SetDefaultDllDirectories`) to prevent DLL planting from the USB drive's root or the current directory. No arbitrary path access from IPC messages: workers receive paths only inside the project cache or ones the user selected, and the orchestrator validates them.
- **Workers:** run as child processes with reduced privileges; on Linux apply Landlock (filesystem) and seccomp (no `socket(AF_INET*)`) where available; on macOS, App Sandbox with entitlements for user-selected files only; on Windows, Job Objects with restricted tokens (best effort).
- **Media parsing** (FFmpeg/libmpv) is the main attack surface: keep dependencies pinned and patched; fuzz the demux path in CI (Atheris + FFmpeg's own fuzzers); decode untrusted files in the separate `decode` worker. mpv runs with `ytdl=no`, `load-scripts=no`, `config=no`, and no Lua/JS script loading.
- **Model loading:** packs verified by Ed25519 signatures; only ONNX/GGUF/CT2 weight formats; **no pickle** (`torch.load`, `joblib`, `numpy.load(allow_pickle=True)` are banned by a ruff rule and CI grep); ONNX custom-op libraries disabled.
- **IPC:** MessagePack only (no pickle, so `multiprocessing` queues are not used for cross-process data); local socket created in a per-user, mode-0700 directory with a random name; first message is a per-launch random token.
- **Code signing:** macOS hardened runtime + notarization (every bundled `.so`/`.dylib` signed; entitlements kept minimal and documented, e.g. `com.apple.security.cs.allow-unsigned-executable-memory` only if ctypes/libffi requires it, verified in M0); Windows Authenticode on every `.exe`/`.dll`/`.pyd`; Linux detached signatures + checksums.
- **Dependency policy:** hashes pinned in `uv.lock`; `pip-audit` in CI; licence scan (`pip-licenses`) against an allowlist; SBOM (CycloneDX via `cyclonedx-py`) shipped with each release.

---

## 15. Testing and Quality

### 15.1 Test layers

| Layer | What | Tooling |
|---|---|---|
| Static | Lint, format, types, banned APIs (pickle, network imports outside `bdub.net`) | ruff, mypy, custom ruff/CI rules |
| Unit | Text normalizer (≥ 1,000 Bangla cases + property tests), time-fit planner, drift scheduler, cache keys, manifest/signature verification | pytest, hypothesis |
| Component | Each worker with golden inputs → stable outputs (tolerances for float audio); IPC protocol round-trips | pytest (workers launched as real subprocesses) |
| Pipeline E2E | 20 reference clips (see below) run per tier, assert on sync, loudness, no-crash, no-network | pytest on CI runners (3 OS), run against the **frozen** build as well as the source tree |
| UI | Widget behavior (pytest-qt `qtbot`), scripted libmpv playback, screenshot diffs (`QWidget.grab()`) for Bangla subtitle and UI rendering | pytest-qt, offscreen + real GL runners |
| Performance | RTF, RAM, startup measured per tier on pinned hardware | Nightly benchmark job (pytest-benchmark + custom harness); fail on > 10% regression |
| Human eval | Bangla-native panel rates adequacy, fluency, naturalness, sync (5-point) per release | Rubric + spreadsheet |
| Accessibility | Automated check that every focusable widget has an accessible name (walk `QAccessible` tree in tests); manual screen-reader pass per release (VoiceOver, NVDA, Orca) plus Accessibility Insights (Windows) / Accessibility Inspector (macOS) | pytest-qt, manual |
| Packaging | Frozen app launches, plays a clip, and dubs a 10 s clip on clean VMs; no missing Qt plugins or shared libs | CI smoke job per OS |
| Portability | Run as a standard (non-admin) user; diff the file system and registry before/after a full session and assert no changes outside `bdub-data/` and temp; move the folder to another path/drive letter and reopen an existing dub; run from a read-only location and check the fallback; unplug-during-dub test on a USB drive | CI per OS (filesystem/registry snapshot), manual USB pass per release |
| Offline | Full E2E under network-denied sandbox (PR-3); audit-hook log must be empty | `unshare -n`, Windows Firewall rules, `pfctl` |

### 15.2 Benchmark corpus

20 CC-licensed clips (≈ 2 h total): lectures, interviews, documentaries, cartoons, two-speaker dialogue, noisy field recordings, music-heavy, fast speech, numbers/dates-heavy, technical jargon, mixed-language speech. Each has reference transcripts and, for 10, reference Bangla translations by professional translators.

### 15.3 Acceptance criteria for v1.0

1. All P0 requirements implemented on all three OSes.
2. Metrics in §9.1 met on T2 reference hardware; T1 meets ≥ 90% of targets with the documented reduced configuration.
3. Network guard test passes: zero connection attempts across the full E2E suite.
4. 50-hour soak test (rotating playback + dubbing) with no crash, no memory growth > 5% after warm-up (main process tracked with `tracemalloc` snapshots plus RSS).
5. Bangla rendering test (≥ 300 conjunct/vowel-sign combinations) renders without broken glyphs in subtitles and UI on all OSes.
6. The signed, notarized portable build runs on clean VMs (macOS 12/14, Win 10/11, Ubuntu 22.04/24.04, Fedora current) as a **standard user with no admin rights** and no system Python present. Windows shows no SmartScreen "unknown publisher" warning, and macOS shows no Gatekeeper block.
7. **Portability:** after a full session (dub, edit, export), nothing has changed on the host outside `bdub-data/` and temp (no registry keys, no profile files). The same folder copied to a USB drive runs on a second computer of each OS and opens the existing dubs instantly.
8. **Usability test** with ≥ 8 non-technical Bangla-speaking participants (mixed age, mostly on T1-class laptops), unassisted:
   - ≥ 90% install the app and get a dubbed video playing on their own.
   - ≥ 90% switch between original and Bangla audio on their own.
   - ≥ 80% save a dubbed video on their own.
   - No participant sees a technical term from the §7.0 list or an untranslated English error in Bangla UI.
   - Median time from opening the app to pressing "Dub to Bangla" ≤ 60 s.

---

## 16. Models, Dependencies, and Licensing (to verify before commit)

> Model names below are **candidates**. Each must pass a licence review, quality bake-off on the benchmark set, and an ONNX/CT2/GGUF conversion + performance check before being locked in M1. Do not ship any model whose licence forbids redistribution or commercial use unless the product is explicitly non-commercial.

| Component | Candidates | Licence notes to check |
|---|---|---|
| **UI toolkit** | **PyQt6** (Riverbank), Qt 6.8 LTS | **PyQt6 is GPLv3 or Riverbank commercial licence.** A closed-source or proprietary build needs the commercial PyQt licence (Qt itself is LGPLv3 for the modules we use). If the product is open source under GPLv3, no extra licence is needed. Fallback: PySide6 (LGPLv3) behind the `bdub.qt` boundary. |
| ASR | Whisper (OpenAI, MIT) via faster-whisper/CTranslate2 or whisper.cpp (pywhispercpp); Distil-/turbo variants | Weights MIT. Check each derivative. |
| VAD | Silero VAD | MIT |
| Diarization | sherpa-onnx pipelines (pyannote segmentation + speaker embeddings) | pyannote models may have gated terms; confirm redistribution rights or substitute. |
| Separation | Demucs family (MIT), MDX-Net variants | Check weights licences. |
| MT | NLLB-200 (CC-BY-NC 4.0, **non-commercial**), IndicTrans2 (MIT code; check weights), MADLAD-400 (Apache 2.0 / check), Seamless variants | **NLLB weights are non-commercial**: a hard blocker for a commercial product. Prefer permissive alternatives or negotiate/fine-tune. |
| Bangla TTS | AI4Bharat Indic-TTS/Indic Parler-TTS (check licences), Meta MMS-TTS `ben` (CC-BY-NC 4.0, non-commercial), Piper/VITS voices trained on open Bangla corpora (e.g., OpenSLR SLR53/SLR37, check licences) | MMS is non-commercial. Plan to train/fine-tune our own VITS-class voices on permissively licensed or commissioned data. |
| Time stretch | audiotsm (MIT, WSOLA/phase vocoder), SoundTouch (LGPL), Rubber Band via pylibrb/pyrubberband (GPL / commercial licence) | Rubber Band GPL is compatible only with a GPL app; otherwise buy its commercial licence or use audiotsm/SoundTouch. |
| Playback | libmpv (LGPL build) + python-mpv (GPLv2+ or LGPLv2.1+, dual), FFmpeg (LGPL build) + PyAV (BSD) | Dynamic linking, ship source offer, no GPL-only codecs (x264 etc.) in bundled build; hardware encoders used for export where licensing permits. Confirm PyAV wheel's bundled FFmpeg configuration or bundle our own. |
| Python libs | NumPy/SciPy (BSD), soundfile (BSD), pyloudnorm (MIT), msgpack (Apache 2.0), pydantic (MIT), cryptography (Apache/BSD), xxhash (BSD), regex (Apache 2.0) | OK; licence scan enforced in CI. |
| Freezer | PyInstaller (GPLv2 with bootloader exception), Nuitka (Apache 2.0) | Bootloader exception permits distributing frozen apps under any licence. |
| Fonts | Noto Sans Bengali (OFL), Hind Siliguri (OFL) | OK |
| Runtime | CPython (PSF), ONNX Runtime (MIT), CTranslate2 (MIT), whisper.cpp (MIT), sherpa-onnx (Apache 2.0) | OK |

**A written licence matrix (`docs/LICENSES.md`) is a milestone deliverable (M1).** The PyQt6 licensing decision (GPLv3 app vs. commercial PyQt licence vs. PySide6) must be made in M0, since it constrains the Rubber Band and model choices too.

---

## 17. Platform-Specific Notes

### macOS
- Separate arm64 and x86_64 builds (PyInstaller does not produce universal2 reliably with all native wheels); prefer arm64 optimizations (Metal for whisper.cpp, CoreML EP for ONNX where beneficial).
- Portable `.zip` with `BanglaDub.app` + `bdub-data/`; notarized and stapled so it opens offline with no Gatekeeper prompt; hardened runtime; every nested binary signed (deep signing of PyInstaller output in a defined order). Entitlements: audio output and file access to user-selected files; **no** network client entitlement in the offline-only build. The app is **not** sandboxed (App Sandbox would block writing to `bdub-data/` next to the app).
- **App Translocation:** a quarantined app opened from Downloads runs from a random read-only path. The app detects this and tells the user in plain language to move the `BanglaDub` folder (e.g., to Applications or a USB drive) and open it again; until then the read-only fallback (§5.6 rule 3) is used.
- `QOpenGLWidget` + mpv render API (OpenGL on macOS is deprecated but still available; track a Metal path via Qt RHI as a later option).
- Media keys and "Now Playing" integration (P1, via `pyobjc` `MPNowPlayingInfoCenter`).

### Windows
- PyInstaller onedir → portable `.zip` (`BanglaDub.exe` + `_internal/` + `bdub-data/`). No installer, no admin, no WebView2. The Microsoft Visual C++ runtime DLLs are bundled app-local so nothing needs installing. An `.msi` is P2.
- Sign every `.exe`, `.dll`, and `.pyd` to reduce antivirus false positives on frozen Python apps; submit releases to Microsoft Defender for analysis.
- DirectML for ONNX; CUDA optional download pack. mpv render API via OpenGL (ANGLE fallback) in `QOpenGLWidget`; WASAPI audio (exclusive mode optional).
- File associations only via the opt-in "Make default player" (per-user `HKCU`, removable); long-path support (manifest `longPathAware`).

### Linux
- `.AppImage` + `bdub-data/` in a `.tar.gz` (the AppImage finds `bdub-data/` next to itself via `$APPIMAGE`). `.deb`, `.rpm`, and Flatpak are P2 (`--share=network` omitted in an offline-only Flatpak, a nice proof of PR-1).
- USB drives mounted `noexec` cannot run the AppImage directly; the README and a first-failure message explain copying the folder to the home directory.
- Wayland and X11 (`QT_QPA_PLATFORM` auto, `wayland;xcb`); PipeWire/PulseAudio/ALSA; VA-API/NVDEC hardware decode; Vulkan whisper.cpp backend.
- MPRIS integration (P1, via `QtDBus`).
- Bundle Qt platform plugins (`xcb`, `wayland`), `libmpv`, FFmpeg, and `libxcb-cursor0` in the AppImage; rely only on the host's glibc, GL/EGL drivers, and audio server.

---

## 18. Telemetry and Diagnostics (local only)

- Local rotating logs via the stdlib `logging` module with `RotatingFileHandler` (default 50 MB cap), one log per process, with levels; **"Export diagnostics"** produces a zip (system info, tier, versions, anonymized logs, `faulthandler` traces) that the user can attach to a bug report by hand.
- Built-in performance HUD (Ctrl/Cmd+Shift+P): stage timings, RTF, RAM (per process via `psutil`), VRAM where the runtime reports it, event-loop latency.

---

## 19. Milestones

| Milestone | Scope | Exit criteria |
|---|---|---|
| **M0 Foundations** (3 wks) | Repo, uv/ruff/mypy/pytest setup, CI on 3 OSes, PyQt6 main window, libmpv render API in `QOpenGLWidget` with working playback, Bangla subtitle rendering via libass, basic settings, **frozen PyInstaller build + signing spike on all 3 OSes**, PyQt6 licensing decision. | Frozen app plays files on all OSes; Bangla subtitle test passes; licence path decided. |
| **M1 Model bake-off and licensing** (4 wks, parallel to M0) | Evaluate ASR/MT/TTS/separation candidates on benchmark; licence matrix; decide stack; conversion scripts (`tools/`); tier benchmarks. | Signed-off model list (§16) and measured RTF per tier. |
| **M2 Pipeline alpha** (6 wks) | Worker processes, IPC, ASR → MT → normalize → TTS → time-fit → mix producing a cached dub track via CLI (`bdub dub <file>`) and UI; pre-process mode. | End-to-end dub of benchmark clips; first human eval round. |
| **M3 Player integration** (4 wks) | Audio-track injection into libmpv, instant toggle, Bangla subtitles, progress UI, cache. | Watch a dubbed video with seamless toggling on all OSes. |
| **M4 Editor and progressive mode** (5 wks) | Transcript editor, re-dub line, glossary, progressive playback, resume/pause, voices. | Meets FE-1/2/6, FD-3. |
| **M5 Export and Model Manager** (3 wks) | Export paths, `.bdubpack` import, first-run screen, portable packages (with and without starter pack), read-only fallback, USB tests. | Portable folder runs from USB on clean VMs of all 3 OSes as a standard user, leaving no traces. |
| **M6 Hardening** (5 wks) | Performance tuning per tier, startup time, soak tests, network guard, accessibility, security review, Bangla UI localization, **usability testing with non-technical users** (a first paper/prototype round also runs during M3). | §15.3 acceptance criteria met. |
| **v1.0 Release** | Signed installers, docs, sample content. | |
| **v1.1** | P1 items: multi-language sources, diarization voices, batch, playlist, burned subtitles, West Bengal register. | |
| **v1.5+** | Voice cloning (consent-gated), Live mode, emotion transfer, more voices. | |

(Estimated 30 engineer-weeks critical path with a 3–4 person team plus 1 Bangla linguistics/QA contractor.)

---

## 20. Team and Roles

Python/systems engineer (orchestrator, worker processes, IPC, packaging and signing), ML engineer (model conversion, tiers, TTS/MT adaptation), Qt desktop engineer (PyQt6 UI, editor, libmpv integration, accessibility), Bangla linguist/QA (normalizer rules, evaluation panel, glossary defaults), designer (UX, accessibility). Release/DevOps shared.

---

## 21. Risks and Mitigations

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Best MT/TTS models carry non-commercial licences | High | High | Licence matrix in M1; use permissive models; fine-tune own; or scope product as non-commercial/free. |
| R2 | Bangla TTS naturalness insufficient or limited voices | Med | High | Early listening tests; budget for data collection/fine-tuning; prosody post-processing; ship fewer but better voices. |
| R3 | Bangla longer/shorter than source breaks sync | High | Med | Time-fit planner with retranslation loop; drift control; editor for manual fixes. |
| R4 | Low-end hardware too slow | Med | High | Tiered models, pre-process mode, quantization (int8), lighter separation/no separation, chunked background processing. |
| R5 | Cross-platform GPU acceleration inconsistency | Med | Med | CPU baseline always works; GPU is an optimization; per-OS CI hardware benchmarks. |
| R6 | libmpv embedding in Qt (Wayland, macOS OpenGL deprecation, Windows GL drivers) | Med | Med | Render API in `QOpenGLWidget` from M0; fallback: mpv's own native window with a Qt overlay window, or `wid` embedding on X11/Windows. |
| R7 | Model size (several GB) makes distribution hard for low-bandwidth users | Med | Med | Tier packs, `.bdubpack` USB sharing, delta updates, offline installers. |
| R8 | Media parser vulnerabilities | Low | High | Decode isolation, fuzzing, pinned patched libs. |
| R9 | Hallucinated/incorrect translations erode trust | Med | Med | Visible machine-translation label, editor, optional bilingual subtitles, confidence highlighting. |
| R10 | Whisper hallucination on silence/music | Med | Med | VAD gating, no-speech threshold, repetition filter, music detection. |
| R11 | Misuse for deceptive voice synthesis | Low | Med | Consent gates, AI-dub labeling, no cloning in v1. |
| R12 | **PyQt6 GPLv3 licence** forces the whole app to be GPLv3 unless a commercial licence is bought | High | High | Decide in M0 (Open Question 1); budget for a Riverbank commercial licence if closed-source; keep all Qt imports behind `bdub.qt` so PySide6 (LGPL) is a low-cost switch. |
| R13 | Freezing/packaging pain: missing Qt plugins or native libs, large bundles, macOS notarization of many binaries, antivirus false positives on Windows | High | Med | Packaging spike in M0; packaged-build smoke tests on clean VMs in CI; sign every binary; evaluate Nuitka as alternative; onedir builds. |
| R14 | GIL / Python overhead makes the UI stutter or slows the pipeline | Med | Med | All heavy work in worker processes with native libraries; no per-sample Python loops; event-loop stall watchdog; profile with py-spy. |
| R15 | Startup time of a frozen Python + Qt app exceeds target | Med | Low | Lazy imports, ML imports only in workers, onedir, measure in nightly perf job. |
| R16 | Running from slow USB drives makes startup, model loading, and dubbing slow | High | Med | Measure on a cheap USB 2.0/3.0 stick in perf tests; optional "Copy models to this computer for speed" (Advanced, opt-in, removable); sequential I/O; warn about slow drives. |
| R17 | Host restrictions break portability: macOS App Translocation, Linux `noexec` mounts, Windows AppLocker/SmartScreen on USB, antivirus scanning many DLLs on first run | Med | Med | Detect each case and explain the fix in plain language; signed binaries; notarized + stapled macOS build; document in README. |

---

## 22. Open Questions

1. **Distribution model:** free/open-source (GPLv3, compatible with PyQt6 as-is), freemium, or commercial (needs PyQt6 commercial licence or PySide6)? This also decides which model licences are acceptable (R1, R12).
2. **Primary source language scope for v1:** English only, or English + Hindi/Urdu from day one?
3. **Voice count and character:** how many Bangla voices at launch, and is a Bangladeshi accent mandatory (vs. West Bengal)?
4. **Hosting of model packs** (if any online download is allowed at all): mirror strategy and bandwidth cost, or offline-only distribution?
5. **Minimum supported hardware floor:** is 8 GB RAM/no-GPU truly a must (affects model choice)?
6. **PyQt6 vs. PySide6:** confirm PyQt6 given licensing (R12). APIs are near-identical; the `bdub.qt` boundary keeps this reversible until M3.
7. **Freezer:** PyInstaller (default) vs. Nuitka (faster startup, smaller, longer builds). Decide after the M0 spike.
8. **Content rating of the benchmark set** and rights to redistribute test clips.
9. **Business language of the UI:** proposed **Bangla-first** (default when the OS locale is Bangla, otherwise offered on the first-run screen), per §1.3. Confirm.
10. **Starter pack size:** the default portable download with models is ≈ 2.5–3 GB, with a "light" download without models as the alternative (§5.6 rule 10). Confirm both are wanted.
11. **Read-only fallback location:** when `bdub-data/` isn't writable, is falling back to a per-user folder on the host acceptable, or should the app refuse to dub and ask the user to move the folder (strict no-traces)?

---

## 23. Glossary

- **ASR:** Automatic Speech Recognition (speech → text).
- **MT:** Machine Translation.
- **TTS:** Text-to-Speech.
- **VAD:** Voice Activity Detection.
- **Diarization:** Labeling who spoke when.
- **Ducking:** Temporarily lowering one audio source under another.
- **RTF:** Real-Time Factor (processing time ÷ media duration).
- **LUFS:** Loudness Units relative to Full Scale (EBU R128 loudness measure).
- **Utterance:** A dubbing unit: one sentence or short group of sentences by one speaker.
- **Conjunct (যুক্তাক্ষর):** A Bangla consonant cluster rendered as a single glyph.
- **`.bdubpack`:** Signed model archive for offline installation.
- **Tier (T1/T2/T3):** Hardware-based quality/performance profile.
- **Frozen build:** The app packaged with its own Python interpreter and dependencies (PyInstaller/Nuitka), so users need no Python install.
- **Portable app:** An app that runs from its own folder (including a USB drive) without installation, keeping all its data in that folder (`bdub-data/`).
- **GIL:** CPython's Global Interpreter Lock; reason heavy work runs in separate worker processes.
- **Render API (mpv):** libmpv interface that draws video into a host-provided OpenGL context (here, a `QOpenGLWidget`).
