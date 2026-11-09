# `.bdubpack` and `.bdubproj` formats

Implements SPEC §8.3, FM-3, FM-4, FM-7, §14.

## `.bdubpack` (model pack)

A ZIP (stored or deflate; no ZIP64 needed for files < 4 GB) containing:

```
manifest.json
manifest.sig            # Ed25519 signature over the exact bytes of manifest.json
files/...               # model files
LICENSE.txt             # licence text(s) for the contents
```

`manifest.json`:

```json
{
  "format": 1,
  "id": "asr-whisper-small-int8",
  "version": "1.0.0",
  "type": "asr",                       // asr | vad | diarize | separate | mt | tts | voice | lexicon
  "runtime": "ctranslate2",            // onnxruntime | ctranslate2 | whisper.cpp | sherpa-onnx
  "runtime_min_version": "4.0",
  "min_tier": "T1",
  "size_bytes": 512000000,
  "license_spdx": "MIT",
  "license_notes": "",
  "commercial_ok": true,
  "source_url": "https://…",            // informational only, never fetched
  "files": [
    {"path": "files/model.bin", "sha256": "…", "size": 123}
  ],
  "voices": [                          // tts packs only
    {"id": "bn-female-1", "label_bn": "নারী কণ্ঠ ১", "label_en": "Female voice 1", "gender": "female"}
  ]
}
```

### Verification order (must follow exactly)

1. Open the ZIP without extracting. Reject entries with absolute paths, `..`, backslashes, symlinks, or names not listed in the manifest (except `manifest.*`, `LICENSE.txt`).
2. Verify `manifest.sig` against `manifest.json` with the embedded public key (`cryptography` Ed25519). Fail → reject.
3. Validate the manifest schema; check `format`, `runtime_min_version`, each file size < 4 GB, total size vs. free space.
4. Extract each file to `bdub-data/tmp/pack-<id>/`, streaming, enforcing the declared size, computing SHA-256 while writing. Mismatch → delete and reject.
5. `os.replace` the folder to `bdub-data/models/<id>/` (after removing any older version only when the new one is verified).
6. Record in `library.sqlite`.

Only ONNX / GGUF / CT2 files are allowed. Do not register ONNX custom-op libraries from a pack.

## `.bdubproj` (shared dub, FM-7, P1)

A ZIP of one project folder **without** source audio stems and without the video:

```
project.bdub.json
text/*.srt, text/*.json
audio/dub_mix.m4a, audio/dub_only.m4a
audio/dub_clips/*.flac      # optional, enables editing on the other machine
```

Unsigned (user-made), so treat as untrusted: same path checks as step 1, size limits, schema validation, and paths inside it must stay inside the new project folder. Import keys it by `media.hash`; the dub attaches automatically when the matching video is opened.
