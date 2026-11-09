---
name: add-worker
description: Create or change a bdub pipeline worker process (separate, asr, mt, tts, mix, decode, or a new role). Use when adding a pipeline stage, changing a worker's IPC messages, loading a new model in a worker, or debugging worker crashes/restarts.
---

# Add or change a pipeline worker

Workers are separate processes started by the orchestrator. They do all heavy work (ML inference, decoding, DSP) so the UI never freezes. Read SPEC §5.2–5.3 and §11.2 first if the stage is new.

References: [ipc-protocol.md](../../references/ipc-protocol.md) (message format, handshake, error codes), [project-format.md](../../references/project-format.md) (stage names, outputs, invalidation), [paths.md](../../references/paths.md), [constants.md](../../references/constants.md).

## Rules that must hold

- Entry point is the same frozen binary: `bdub --role <name>`. Register the role in `src/bdub/__main__.py`.
- Install the network audit hook **first thing** in the worker's `main()` (from `bdub.net_guard` or the shared startup helper). Nothing runs before it.
- Import ML libraries (`onnxruntime`, `ctranslate2`, `faster_whisper`, `sherpa_onnx`, etc.) **inside the worker module only**, never at package import time of anything the GUI imports.
- IPC: MessagePack frames over `multiprocessing.connection` using **only** `send_bytes` / `recv_bytes`. Never `send()`/`recv()` (they pickle).
- First message from the orchestrator is the per-launch auth token. Reject and exit if it doesn't match.
- Audio and other large data move as **file paths inside `bdub-data/cache/<hash>/`**, never over the socket. Validate every incoming path with `bdub.paths` (must be inside `bdub-data/` or a user-selected media path the orchestrator passed).
- Load models lazily on first request, only from verified packs via `bdub.models`. No pickle-based loaders.
- Exit after the idle timeout (default 120 s) to free memory.
- Deterministic: pass seeds explicitly; same input + settings + models → same output.
- No pure-Python loops over audio samples. Use NumPy or the native library.
- Log with `logging.getLogger(__name__)` to the per-process log in `bdub-data/logs/`. Enable `faulthandler` at startup.

## Steps

1. **Define messages** in `src/bdub/orchestrator/protocol.py` (or the existing protocol module): a request and a result type per operation, as pydantic models or TypedDicts with a `type` field and a protocol `version`. Include `job_id`, `utt_id`/chunk id, and paths, never raw audio.
2. **Write the worker** in `src/bdub/workers/<role>.py`:
   - `main(argv)` → install guard → connect → auth → loop: `recv_bytes` → decode → dispatch → `send_bytes` result or error.
   - Send progress messages (`{"type": "progress", "job_id", "done", "total"}`) for anything longer than ~1 s, so the UI can show a single plain-language progress bar.
   - Catch exceptions per request and return `{"type": "error", "code", "message"}`; only crash for unrecoverable states.
3. **Register in the supervisor** (`src/bdub/orchestrator/supervisor.py`): spawn via `QProcess`, restart on crash, retry the chunk at most 2 times, then flag the utterance (SPEC §11.2).
4. **Persist results** per utterance or chunk in the project cache, so a quit or crash resumes (SPEC §11.2). Update stage status in `project.bdub.json`.
5. **Map to Simple-mode wording**: give the stage a user-facing step name from the SPEC §7.0 table (both Bangla and English, via `tr()`).
6. **Tests** in `tests/component/test_worker_<role>.py`:
   - Launch the worker as a real subprocess, send golden input, compare output with tolerances for float audio.
   - Test bad auth token → worker exits.
   - Test a path outside `bdub-data/` → error, not processed.
   - Test that the audit-hook log is empty after the run.
   - Use a tiny test model or a stub model from `tests/fixtures/`. Tests must not need the network.
7. Run `uv run ruff check . && uv run mypy src && uv run pytest tests/component -k <role>`.

## Debugging

- Run standalone: `uv run bdub --role <name> --stdio` (reads/writes length-prefixed frames on stdio for manual testing).
- Worker logs: `bdub-data/logs/<role>-*.log`. Native crashes: the `faulthandler` trace in the same folder.
- Memory check: the performance HUD (Ctrl/Cmd+Shift+P) shows RSS per process.
