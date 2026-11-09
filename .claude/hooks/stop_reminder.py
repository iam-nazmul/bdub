#!/usr/bin/env python3
"""Stop hook: if source or UI files changed since the last reminder, show the user
which project checks apply (tests, offline audit, UX/Bangla review). Never blocks.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
MARKER = PROJECT / ".claude" / "hooks" / ".last-stop-check"

WATCH = {
    "src/bdub/ui": "UI changed: run the simple-ui checklist; ux-reviewer / bangla-linguist can review.",
    "src/bdub/app": "UI changed: run the simple-ui checklist; ux-reviewer / bangla-linguist can review.",
    "src/bdub/text": "Bangla normalizer changed: run `uv run pytest tests/unit/text -q`.",
    "src/bdub/workers": "Workers changed: run component tests and the offline-audit skill.",
    "src/bdub/orchestrator": "Orchestrator/IPC changed: run component tests and the offline-audit skill.",
    "src/bdub/models": "Model loading changed: run the offline-audit skill (pack verification).",
    "src/bdub/net": "Network code changed: run the offline-audit skill, including the offline-only bundle check.",
    "src/bdub/paths.py": "Paths changed: verify nothing is written outside bdub-data/ (portable rules).",
    "packaging": "Packaging changed: follow the portable-build skill checks.",
    "pyproject.toml": "Dependencies changed: follow the add-dependency skill (licence, offline, size).",
}


def changed_since(root: Path, since: float) -> bool:
    if root.is_file():
        return root.stat().st_mtime > since
    if not root.exists():
        return False
    for p in root.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts and p.stat().st_mtime > since:
            return True
    return False


def main() -> int:
    try:
        json.load(sys.stdin)
    except Exception:
        pass
    since = MARKER.stat().st_mtime if MARKER.exists() else time.time() - 3600

    notes: list[str] = []
    for rel, note in WATCH.items():
        if changed_since(PROJECT / rel, since) and note not in notes:
            notes.append(note)

    MARKER.parent.mkdir(parents=True, exist_ok=True)
    MARKER.touch()

    if notes:
        msg = "bdub checks to consider:\n- " + "\n- ".join(notes)
        print(json.dumps({"systemMessage": msg}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
