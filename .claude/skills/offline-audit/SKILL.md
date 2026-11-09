---
name: offline-audit
description: Check that bdub never touches the network and never loads pickled or unsigned code, as required by SPEC §12 and §14. Use before finishing any change that adds a dependency, touches IPC, model loading, mpv/FFmpeg options, or bdub.net, and when the user asks to verify offline/privacy guarantees.
---

# Offline and privacy audit

The core promise: after models are present, the app never makes a network connection (SPEC §1.2, §12). Run this audit on the change you made, and report the results plainly.

References: [mpv-config.md](../../references/mpv-config.md) (required mpv options), [ipc-protocol.md](../../references/ipc-protocol.md), [bdubpack-format.md](../../references/bdubpack-format.md) (verification order), [paths.md](../../references/paths.md) (library cache redirects).

## 1. Static checks on the source

Run from the repo root:

```bash
# Network libraries or Qt networking outside bdub/net/
rg -n --glob '!src/bdub/net/**' -e '\b(import|from)\s+(requests|httpx|urllib3|aiohttp|websocket|socket|http\.client|urllib\.request)\b' -e 'QtNetwork|QtWebEngine|QTcpSocket|QNetworkAccessManager' src/

# Pickle and unsafe loaders anywhere
rg -n -e '\bpickle\b' -e 'torch\.load' -e 'joblib' -e 'allow_pickle\s*=\s*True' -e '\.send\(' -e '\.recv\(' src/

# Telemetry / remote URLs
rg -n -e 'https?://' src/ --glob '!src/bdub/net/**'
```

Expected: no hits, except:
- `socket` is allowed only in `bdub.net_guard` / the IPC module, and only for `AF_UNIX`.
- `.send(`/`.recv(` hits must be reviewed: on a `multiprocessing.connection` object only `send_bytes`/`recv_bytes` are allowed.
- URLs in comments/docs strings are fine if they are never fetched. Note them.

Then run `uv run ruff check .` (the banned-API rules live in `pyproject.toml`).

## 2. Configuration checks

- mpv is created with `ytdl=no`, `load-scripts=no`, `config=no` (grep `src/bdub/player/`).
- FFmpeg/PyAV opens inputs with `protocol_whitelist` `file,pipe` (grep `src/bdub/workers/decode.py`).
- Every process entry point installs the audit hook before anything else (`__main__.py` for GUI and each `--role`).
- Model loading goes only through `bdub.models` and verifies the Ed25519 signature + SHA-256 before use.
- External links use `QDesktopServices.openUrl` only after a user click and a confirmation.

## 3. Runtime checks

```bash
uv run pytest tests -m "offline" -q          # audit-hook tests: log must be empty
```

On Linux (CI or a dev box), the full E2E under no network:

```bash
unshare -rn uv run pytest tests/e2e -q
```

If the change touched `bdub.net`, also verify the offline-only build excludes it:

```bash
BDUB_OFFLINE_ONLY=1 uv run pyinstaller packaging/bdub.spec --noconfirm
uv run python packaging/check_bundle.py dist/BanglaDub   # asserts no bdub.net, QtNetwork, QtWebEngine, requests/httpx/urllib3
```

## 4. New dependency?

If the change adds a package, also follow the `add-dependency` skill. Check whether the package phones home on import (update checks, telemetry, hub downloads such as `huggingface_hub`). If it does, find the env var or option that disables it, set it in `bdub.net_guard`, and add a test.

## Report

Summarize as a short list: each check → pass / fail / not applicable, with file:line for any finding. If something couldn't be run (e.g. `unshare` on macOS), say so; don't mark it as passed.
