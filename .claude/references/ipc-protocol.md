# IPC protocol (orchestrator ↔ workers)

Implements SPEC §5.1 (IPC row), §5.2, §14 (IPC).

## Transport

- `multiprocessing.connection.Listener` in the orchestrator; `Client` in the worker.
  - macOS/Linux: `family="AF_UNIX"`, socket file in `bdub-data/ipc/` (dir mode 0700), random name per launch. If `bdub-data/` is on a filesystem that doesn't support Unix sockets (FAT32/exFAT USB), use a short path under the OS temp dir in a 0700 directory instead (verify on macOS/Linux USB).
  - Windows: `family="AF_PIPE"`, name `\\.\pipe\bdub-<random>`.
- **No `authkey`-based pickle handshake reliance:** use `send_bytes`/`recv_bytes` only. The `authkey` may still be set (HMAC challenge), plus our own token below.
- One connection per worker process. Messages are a single MessagePack map per `send_bytes` call. Max message size 1 MB; anything larger is a file path.

## Worker launch

```
<frozen-exe> --role <role> --ipc <address> --data-dir <bdub-data> [--log-level info]
```

The auth token is passed through an environment variable (`BDUB_IPC_TOKEN`), not argv (argv is visible to other users via `ps`).

## Envelope

Every message:

```python
{
  "v": 1,                  # protocol version
  "type": "<message type>",
  "id": "<uuid4 hex>",     # unique per message
  "reply_to": "<id>",      # on responses only
  # ...type-specific fields
}
```

Unknown `type` → respond with `error` code `unknown_type`. Unknown fields are ignored (forward compatible). A different major `v` → `error` code `version_mismatch` and exit.

## Handshake

1. Worker → `hello {role, pid, version, token}`
2. Orchestrator checks token; on mismatch closes the connection (worker exits).
3. Orchestrator → `welcome {settings: {...threads, gpu, tier, seed...}}`

## Messages

| Type | Direction | Fields |
|---|---|---|
| `hello` | W → O | `role`, `pid`, `version`, `token` |
| `welcome` | O → W | `settings` |
| `job` | O → W | `job_id`, `op` (role-specific, e.g. `transcribe`, `translate`, `synthesize`, `fit`, `mix`, `separate`, `decode`), `project` (hash), `inputs` (map of name → relative path or value), `params` |
| `progress` | W → O | `job_id`, `done`, `total`, `stage` (internal stage name) |
| `result` | W → O | `job_id`, `outputs` (map of name → relative path or value), `metrics` (e.g. `rtf`, `peak_rss_mb`, `ms`) |
| `error` | W → O | `job_id` (if any), `code`, `message` (English, for logs), `retryable` (bool) |
| `cancel` | O → W | `job_id` |
| `ping` / `pong` | both | — (health check every 10 s; 3 missed → restart worker) |
| `shutdown` | O → W | — (worker finishes current write, then exits 0) |

## Error codes

| Code | Retryable | Meaning |
|---|---|---|
| `bad_path` | no | Path outside allowed locations |
| `bad_input` | no | Schema validation failed |
| `model_missing` | no | Required pack not installed / failed verification |
| `out_of_memory` | yes (after unloading) | Allocation failed |
| `io_error` | yes | Disk read/write failed (e.g. USB removed) |
| `media_error` | no | Decode failed / corrupt / protected |
| `cancelled` | no | Job cancelled |
| `internal` | yes | Anything else (log the traceback in the worker log) |

## Rules

- Validate every incoming message against its schema (pydantic) before use.
- Paths in `inputs`/`outputs` are relative to `bdub-data/` unless the key is `media`, which is an absolute user-selected path the orchestrator has already validated.
- Workers must be safe to kill at any time: write outputs to `tmp/` then `os.replace` into place.
- Orchestrator retries `retryable` errors up to 2 times (constants.md), then marks the utterance/chunk as failed.
