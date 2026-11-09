---
name: add-dependency
description: Add, upgrade, or replace a Python package, native library, ML model, or font in bdub, including its licence check and docs/LICENSES.md entry. Use whenever pyproject.toml, uv.lock, bundled binaries (libmpv, FFmpeg), model packs, or fonts change.
---

# Add a dependency

Every dependency affects four promises: offline, licence, portable size, and startup time. Check all four before adding it.

References: [bdubpack-format.md](../../references/bdubpack-format.md) for packaging models, [paths.md](../../references/paths.md) for redirecting library caches, [constants.md](../../references/constants.md) for size limits.

## 1. Is it needed?

- Prefer the stdlib or a package already in `uv.lock`.
- Runtime code must not need PyTorch. Training/conversion packages go in the `tools` group only.
- Pure-Python packages that loop over audio samples are not acceptable for hot paths. Use NumPy-based or native-backed ones.

## 2. Licence

Look up the licence of the package **and** of any bundled native code or weights (wheels often bundle C libraries; models have separate weight licences).

| Licence | Status |
|---|---|
| MIT, BSD, Apache-2.0, PSF, ISC, Zlib, OFL (fonts), MPL-2.0 | OK |
| LGPL | OK when dynamically linked (FFmpeg, libmpv, Qt): record it, and note the source-offer obligation |
| GPL / AGPL | **Stop.** Only acceptable if the project decides to be GPLv3 (SPEC Open Question 1, R12). Ask the user. |
| CC-BY-NC, research-only, "non-commercial", gated/unknown | **Stop** for anything shipped by default (SPEC §16, R1). Ask the user. |
| No licence stated | Treat as not usable. |

Never use a GPL or non-commercial item as the default without the user's explicit decision.

## 3. Offline behaviour

- Does it make network calls on import or use (update checks, telemetry, auto-downloading models from a hub)? If yes, find how to disable it (env var/option), set that in `bdub.net_guard`, and add a test that the audit-hook log stays empty.
- It must not load pickled data or arbitrary code from model files.

## 4. Portable and startup cost

- Note the added size to the portable folder (target: program files ≤ 400 MB, SPEC §11.4).
- Check it works when frozen by PyInstaller (hidden imports, data files, native libs). Add hooks in `packaging/` if needed.
- Must not write outside `bdub-data/` (caches, config files in `~`). If it does, redirect via env var/option in `bdub.paths` setup.
- ML/heavy packages may only be imported inside worker processes (cold start target ≤ 2.0 s).
- For models: each file must be < 4 GB (FAT32 USB drives) and ship as a signed `.bdubpack` (ONNX/GGUF/CT2 only).

## 5. Add it

```bash
uv add <package>                 # runtime
uv add --group dev <package>     # dev/test only
uv add --group tools <package>   # conversion/research only, never shipped
```

Pin to a version known to work; `uv.lock` holds hashes.

## 6. Record it

Add or update a row in `docs/LICENSES.md`:

```
| Name | Version | Licence (SPDX) | Used for | Shipped? | Bundled native code / weights licence | Notes / obligations |
```

## 7. Verify

```bash
uv run ruff check . && uv run mypy src && uv run pytest -q
uv run pip-audit
uv run pip-licenses --format=markdown --with-urls   # check it appears as expected
```

Then run the `offline-audit` skill's static checks.

## Report

State: what was added and why, its licence and whether that needs a decision, size impact, and any offline/portability adjustments made.
