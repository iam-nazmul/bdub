# Paths and the portable data folder

Implements SPEC §5.6. `src/bdub/paths.py` is the **only** module that decides where files live.

## Finding the app root

| Situation | App root | Data folder |
|---|---|---|
| Frozen, Windows | folder containing `BanglaDub.exe` (`Path(sys.executable).parent`) | `<root>/bdub-data/` |
| Frozen, Linux AppImage | folder containing the AppImage (`Path(os.environ["APPIMAGE"]).parent`) | `<root>/bdub-data/` |
| Frozen, macOS | folder containing `BanglaDub.app` (go up from `sys.executable` = `.../BanglaDub.app/Contents/MacOS/BanglaDub` three levels, then parent) | `<root>/bdub-data/` |
| Development (`uv run bdub`) | repo root | `<repo>/bdub-data/` (git-ignored) |
| Override (tests, debugging) | — | `BDUB_DATA_DIR` env var |

Detect "frozen" with `getattr(sys, "frozen", False)`.

## Layout

```
bdub-data/
  settings.ini        QSettings(IniFormat)
  library.sqlite      project index (WAL mode)
  models/<pack-id>/   installed packs
  cache/<hash>/       dub projects (see project-format.md)
  lexicon/            user lexicon + glossary
  logs/               one rotating log per process + faulthandler traces
  tmp/                scratch; emptied on start and on clean exit
  ipc/                local sockets (mode 0700, macOS/Linux)
  .bdub-data          marker file with data-format version
```

## API sketch

```python
class Paths:
    root: Path            # app root
    data: Path            # bdub-data/
    settings_file: Path
    library_db: Path
    models: Path
    cache: Path
    lexicon: Path
    logs: Path
    tmp: Path
    ipc: Path
    read_only_fallback: bool   # True when data/ was not writable

    def project(self, media_hash: str) -> Path: ...
    def is_inside_data(self, p: Path) -> bool: ...   # resolve() + is_relative_to; reject symlink escapes
    def to_relative(self, p: Path) -> str: ...       # for storing in JSON / SQLite
    def from_relative(self, s: str) -> Path: ...

def get_paths() -> Paths: ...   # computed once at startup, before Qt or logging
```

## Writable check and fallback

At startup, try to create and delete `bdub-data/tmp/.write-test`. If that fails (read-only USB, `Program Files`, macOS App Translocation):

| OS | Fallback data folder |
|---|---|
| macOS | `~/Library/Application Support/BanglaDub/` |
| Windows | `%LOCALAPPDATA%\BanglaDub\` |
| Linux | `${XDG_DATA_HOME:-~/.local/share}/bangladub/` |

Then set `read_only_fallback = True`, and show the plain message from [ui-wording.md](ui-wording.md). Whether this fallback is allowed at all is SPEC Open Question 11. Keep it behind one function so it can be switched to "refuse and explain".

**macOS App Translocation** is detected when the executable path contains `/AppTranslocation/`.

## Redirecting library caches

Set before importing the libraries (in `__main__` for workers):

| Variable / option | Value |
|---|---|
| `TMPDIR` / `TEMP` / `TMP` | `bdub-data/tmp` |
| `HF_HUB_OFFLINE=1`, `HF_HOME` | `bdub-data/tmp/hf` (only if a dependency pulls in huggingface_hub) |
| `XDG_CACHE_HOME` (Linux, in workers) | `bdub-data/tmp/xdg-cache` |
| `MPLCONFIGDIR` (if matplotlib ever appears) | `bdub-data/tmp/mpl` |
| onnxruntime CoreML EP cache | `ModelCacheDirectory` provider option → `bdub-data/cache/_ort` (verify option name for bundled ORT) |

Anything that still writes outside `bdub-data/` must be listed in `docs/PORTABLE.md` with the reason.

## Rules

- Never call `QStandardPaths`, `Path.home()`, `os.path.expanduser`, `winreg`, or rely on the current working directory for app data (except the fallback table above, inside `paths.py`).
- Store paths **relative to `bdub-data/`** in JSON and SQLite. Media outside `bdub-data/` is stored as last-known absolute path + content hash.
- Validate every path that comes from IPC or a project file with `is_inside_data()` (or the user-selected media allowlist).
