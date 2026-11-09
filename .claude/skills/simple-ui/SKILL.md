---
name: simple-ui
description: Build or change any bdub user interface (PyQt6 widgets, dialogs, menus, buttons, messages, errors, progress, settings) so non-technical users can use it. Use for every UI change, including adding a user-facing string, error message, or setting.
---

# UI for everyday users

The user is a student, parent, or teacher, not a technical person. Read SPEC §1.3 and §7.0 before designing a screen.

Reference: [ui-wording.md](../../references/ui-wording.md) has the approved Bangla/English strings for actions, progress steps, notices, errors, and the never-show list. Reuse those strings; add new ones there first.

## Decide where it goes

Ask: would an ordinary user need this to watch a video in Bangla?

- **Yes** → Simple mode. Simple mode contains only: play controls, **Dub to Bangla** button, **Original / বাংলা** audio switch, subtitles on/off, **Save dubbed video**, and basic settings (language, text size, subtitle size, clear space).
- **No** → Advanced mode only. Gate it with the mode setting (`settings.advanced_mode`).
- **Can the app decide it itself?** → Then don't show it at all. Pick a smart default (tier, models, separation, language, audio track are always automatic).

## Rules

- **No jargon in Simple mode.** Use the SPEC §7.0 wording table. Banned in Simple mode: ASR, MT, TTS, VAD, model, tier, LUFS, RTF, diarization, cache, file paths, error codes.
- **Every string goes through `self.tr()`** (or `QCoreApplication.translate()` outside widgets). Add both English and plain everyday Bangla. If you can't write natural Bangla, add the English string and a `# TODO(linguist)` note, and say so in your summary.
- **Errors** use the shared helper (`bdub.ui.messages.show_problem(...)`):
  - one plain sentence: what happened
  - one button: what to do ("Find video…", "Try again", "Free up space")
  - technical details only behind "Details"
  - never a raw exception text, stack trace, or path in the main message
- **Progress**: one bar, one step name from the wording table, human time ("about 10 minutes left"). No per-stage percentages in Simple mode.
- **Safe to click**: destructive actions confirm first and support undo (`QUndoStack`). Nothing in Simple mode can lose work.
- **Accessibility**:
  - `setAccessibleName` (and description where useful) on every interactive widget
  - custom-painted widgets implement `QAccessibleInterface`
  - click targets ≥ 40 px, tab order set explicitly, visible focus
  - tooltips on every button
  - respect UI scale up to 200%; no fixed pixel sizes for text
- **Bangla rendering**: use the bundled font stack (Noto Sans Bengali → Hind Siliguri). Never set a Latin-only font on a widget that can show Bangla.
- **Qt imports only via `bdub.qt`.** Never import PyQt6 directly.
- **Never block the UI thread.** Anything over ~16 ms goes to a worker process or `QThreadPool`, with results delivered through signals.
- Keyboard shortcuts are `QAction`s with `QKeySequence`, listed in SPEC §7.5.

## Steps

1. Sketch the screen in a comment or the PR description: what the user sees in Simple mode vs. Advanced mode.
2. Implement the widget in `src/bdub/ui/` (or `app/` for main-window wiring).
3. Add the strings, then run `pylupdate6` to update `.ts` files (see `resources/translations/`).
4. Tests in `tests/ui/` with pytest-qt:
   - the main action works with keyboard only
   - in Simple mode, no widget text contains a banned word (use the shared `assert_no_jargon(widget)` helper)
   - every focusable widget has an accessible name (`assert_accessible(widget)`)
   - a screenshot diff for any new Bangla text rendering
5. Run `QT_QPA_PLATFORM=offscreen uv run pytest tests/ui -q`, then launch with `uv run bdub` and click through it once in both modes and both languages.

## Checklist before done

- [ ] Simple mode still has one obvious main action
- [ ] No new question the app could have answered itself
- [ ] Bangla and English strings present (or linguist TODO flagged)
- [ ] Errors have one plain sentence + one action
- [ ] Keyboard and screen reader usable
