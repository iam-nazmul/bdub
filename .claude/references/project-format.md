# Project format and cache

Implements SPEC §8.1–8.2 and FD-10.

## Cache key

`media_hash = "xxh3:" + xxh3_128(first 8 MB ‖ middle 8 MB ‖ last 8 MB ‖ size_le64 ‖ duration_ms_le64).hexdigest()`

Files ≤ 24 MB are hashed whole. Duration comes from the container (PyAV); if unknown, use 0. The project folder is `bdub-data/cache/<hex part of hash>/`.

## Stages

Internal stage names (also used in IPC `progress.stage` and `project.bdub.json.stages`):

| Stage | Depends on | Output |
|---|---|---|
| `decode` | media, `audio_track` | `audio/source.wav` (optional to keep) |
| `separate` | decode, `separation` | `audio/vocals.flac`, `audio/background.flac` |
| `asr` | decode/separate, `src_lang`, ASR model | `text/asr.json` |
| `diarize` | asr, diarization model | speakers in `asr.json` |
| `segment` | asr/diarize | `utterances[]` |
| `mt` | segment, MT model, `register`, glossary | `utterances[].bn`, `text/translation.json` |
| `normalize` | mt, lexicon | `utterances[].bn_spoken` |
| `tts` | normalize, voices, TTS model | `audio/dub_clips/<utt_id>.flac` |
| `fit` | tts | `utterances[].tts.rate/offset_ms/flags` |
| `mix` | fit, separate or ducking, mix settings | `audio/dub_mix.m4a`, `audio/dub_only.m4a` |
| `subs` | mt (and asr for original) | `text/subs_bn.srt`, `text/subs_src.srt` |

Status values: `pending`, `running`, `done`, `failed`, `stale` (inputs changed; needs rerun).

## Invalidation

When a setting changes, mark the first stage that depends on it and everything downstream as `stale`. Examples:

| Change | First stale stage |
|---|---|
| Source audio track | `decode` |
| Separation level | `separate` |
| Source language / ASR model | `asr` |
| Register, glossary, MT model | `mt` |
| Lexicon | `normalize` |
| Voice, rate, pitch, TTS model | `tts` |
| Mix balance, ducking | `mix` |

Per-utterance edits (FE-2) only mark that utterance's `mt`/`normalize`/`tts`/`fit` stale, then re-run `mix` for its time range.

## `project.bdub.json` fields

| Field | Type | Notes |
|---|---|---|
| `schema` | int | Bump on breaking change + write a migration in `orchestrator/migrations.py` |
| `app_version` | str | Version that last wrote the file |
| `media.path` | str | Last-known absolute path (not identity) |
| `media.hash` | str | Identity |
| `media.size`, `media.duration_ms` | int | |
| `media.audio_track` | int | |
| `settings` | object | `src_lang`, `tgt_lang` (`bn`), `tier`, `separation` (`off`/`light`/`full`), `register` (`colloquial_bd`/`formal`/`colloquial_wb`), `voices` {speaker → voice id}, `mix` {`dub_gain_db`, `bg_gain_db`, `duck_db`}, `seed` |
| `stages` | object | stage → status |
| `models` | object | stage → `"<pack-id>@<version>"` |
| `utterances[]` | array | see below |
| `keep` | bool | Never evicted by LRU (FM-6) |
| `last_opened` | ISO 8601 | For LRU |

Utterance:

| Field | Type | Notes |
|---|---|---|
| `id` | str | `u0001`… stable across edits; new ones get new ids |
| `start_ms`, `end_ms` | int | Source speech span |
| `speaker` | str | `S1`… |
| `src` | str | Source text |
| `src_words` | array | `[start_ms, end_ms, word, confidence]` |
| `bn` | str | Translation |
| `bn_candidates` | array of str | Top-k (FE-5) |
| `bn_spoken` | str | After normalization |
| `tts` | object | `voice`, `rate`, `pitch`, `gain_db`, `dur_ms`, `offset_ms`, `stretch`, `file` (relative) |
| `keep_original` | bool | FD-9 |
| `flags` | array | `edited_by_user`, `too_long`, `overflow`, `retranslated`, `failed` |

All file paths are relative to the project folder. Write the JSON atomically (write `*.tmp`, `fsync`, `os.replace`).
