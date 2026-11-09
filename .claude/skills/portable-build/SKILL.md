---
name: portable-build
description: Build, package, and verify the portable BanglaDub folder (PyInstaller onedir + bdub-data) for macOS, Windows, or Linux, including signing/notarization steps and portability checks. Use when the user asks to build, package, release, or test the app as a portable/USB app, or when packaging breaks.
---

# Build the portable app

Distribution is a self-contained folder with no installer (SPEC §5.6, §17). Build on the target OS: PyInstaller does not cross-compile.

References: [paths.md](../../references/paths.md) (data folder resolution, fallback, cache redirects), [constants.md](../../references/constants.md) (size and startup limits), [ui-wording.md](../../references/ui-wording.md) (translocation / noexec / read-only messages).

## Output layout

```
dist/BanglaDub/
  BanglaDub.exe | BanglaDub.AppImage | BanglaDub.app
  _internal/            # (Windows/Linux) frozen runtime, read-only
  bdub-data/
    models/             # starter pack (full build only)
    README.txt  README-বাংলা.txt
```

On macOS the `.app` and `bdub-data/` sit side by side; never put data inside the `.app`.

## Steps

1. **Clean and check the source first**
   ```bash
   uv sync --frozen
   uv run ruff check . && uv run mypy src && uv run pytest -q
   ```
2. **Freeze**
   ```bash
   uv run pyinstaller packaging/bdub.spec --noconfirm --clean
   ```
   - Mode is **onedir** (never onefile: slow start, and it unpacks to temp).
   - The spec must exclude `PyQt6.QtNetwork`, `PyQt6.QtWebEngine*`, `tkinter`, `torch`, and test packages.
   - Include the Qt platform plugins (`cocoa` / `windows` / `xcb` + `wayland`), libmpv, FFmpeg, bundled fonts, `.qm` translations.
   - For an offline-only build set `BDUB_OFFLINE_ONLY=1` (excludes `bdub.net`).
3. **Assemble the portable folder**
   ```bash
   uv run python packaging/make_portable.py --variant full   # or --variant light (no models)
   ```
   This creates `bdub-data/` with the starter `.bdubpack` installed (full variant) and the READMEs.
4. **Check bundle contents**
   ```bash
   uv run python packaging/check_bundle.py dist/BanglaDub
   ```
   It must confirm: no `bdub.net` (offline-only), no QtNetwork/QtWebEngine, no `requests`/`httpx`/`urllib3`, every model file < 4 GB, program files ≤ 400 MB.
5. **Sign (per OS).** Signing needs the user's certificates. Never invent or commit credentials. If they're not configured, stop here and tell the user what's missing.
   - **Windows:** Authenticode-sign every `.exe`, `.dll`, `.pyd` (`signtool sign /fd sha256 /tr <timestamp-url> ...`). Bundle the VC++ runtime DLLs app-local.
   - **macOS:** sign inside-out (dylibs/.so → frameworks → executables → `.app`) with hardened runtime and `packaging/macos/entitlements.plist` (no App Sandbox, no network entitlement). Then `xcrun notarytool submit --wait` and `xcrun stapler staple BanglaDub.app`, so it opens offline.
   - **Linux:** build the AppImage (`packaging/linux/build_appimage.sh`), then create detached signatures + SHA-256 checksums.
6. **Archive**
   - Windows/macOS: `.zip` of `BanglaDub/` (macOS: use `ditto -c -k --keepParent` to keep signatures and symlinks).
   - Linux: `tar -czf BanglaDub-linux-x64.tar.gz BanglaDub/`.

## Portability checks (SPEC §15.1, §15.3 item 7)

Run on a clean VM as a **standard (non-admin) user**:

1. Snapshot the file system (and on Windows the registry with `reg export HKCU`) before.
2. Unzip, launch, play a clip, dub a 10 s clip, save the dubbed video, quit.
3. Snapshot after and diff: no changes outside `BanglaDub/bdub-data/` and temp. Any other change is a bug.
4. Move the folder to another path / USB drive (different drive letter on Windows), relaunch: the existing dub opens instantly.
5. Make the folder read-only (or, on macOS, run straight from Downloads to trigger App Translocation): the app shows the plain-language fallback message and still works.
6. On a USB drive, unplug during a dub, plug back in: the app resumes without corruption.
7. Linux: on a `noexec` mount, the app shows the "copy to home folder" message.

`packaging/portable_smoke.py` automates steps 1–4 where the OS allows it.

## Common failures

| Symptom | Likely cause |
|---|---|
| "Could not find the Qt platform plugin" | Plugin not collected; fix `packaging/bdub.spec` `datas`/hooks |
| mpv fails to load | libmpv not bundled or wrong arch; check `_internal/` |
| macOS "app is damaged" | A nested binary is unsigned, or the zip lost signatures (use `ditto`) |
| Windows SmartScreen warning | Unsigned or newly signed binary without reputation; sign all files, submit to Microsoft |
| App writes to `~/Library` or `%APPDATA%` | Some code path bypassed `bdub.paths` or a library's default cache; fix and add a test |

## Report

List: OS, variant (full/light, offline-only or not), folder size, signing status (done / skipped: reason), and each portability check → pass / fail / not run.
