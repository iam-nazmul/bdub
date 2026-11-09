# References

Lookup material for working on bdub. SPEC.md stays the source of truth; these files expand parts of it into implementation detail. If a reference and the spec disagree, follow the spec and fix the reference.

| File | Contents | Used by |
|---|---|---|
| [constants.md](constants.md) | Every numeric limit and default from the spec in one table | everyone |
| [paths.md](paths.md) | `bdub-data/` layout, per-OS resolution, read-only fallback, what may be written where | `bdub.paths`, packaging |
| [ipc-protocol.md](ipc-protocol.md) | Orchestrator ↔ worker message format, handshake, message types, errors | `add-worker`, pipeline-engineer |
| [project-format.md](project-format.md) | `project.bdub.json` fields, stage names and statuses, cache keys, invalidation | pipeline-engineer |
| [bdubpack-format.md](bdubpack-format.md) | Model pack and shared-dub file formats, signing and verification order | `add-dependency`, security auditor |
| [time-fit.md](time-fit.md) | Time-fit and drift algorithm as pseudocode with test properties | pipeline-engineer |
| [mpv-config.md](mpv-config.md) | Required mpv options, properties used for tracks and subtitles | player code |
| [bangla-numbers.md](bangla-numbers.md) | Spoken Bangla numbers 0–100, scales, ordinals, time, units for the normalizer | `bangla-normalizer`, bangla-linguist |
| [ui-wording.md](ui-wording.md) | Approved Bangla/English wording for Simple mode, stages, buttons, errors | `simple-ui`, ux-reviewer, bangla-linguist |

Items marked **(verify)** are best-effort and need confirmation (by the Bangla linguist, or by testing against the bundled library version) before they are relied on.
