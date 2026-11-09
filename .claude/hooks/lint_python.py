#!/usr/bin/env python3
"""PostToolUse: format and lint an edited Python file with ruff.

Uses `uv run ruff` when pyproject.toml exists, else `ruff` on PATH.
Never downloads anything (no uvx). Skips silently if ruff isn't available.
Remaining lint errors are fed back to Claude (exit 2) so it can fix them.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def ruff_cmd() -> list[str] | None:
    if (PROJECT / "pyproject.toml").exists() and shutil.which("uv"):
        probe = subprocess.run(
            ["uv", "run", "--offline", "--no-sync", "ruff", "--version"],
            cwd=PROJECT, capture_output=True, text=True, timeout=30,
        )
        if probe.returncode == 0:
            return ["uv", "run", "--offline", "--no-sync", "ruff"]
    if shutil.which("ruff"):
        return ["ruff"]
    return None


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    tool_input = data.get("tool_input") or {}
    path = tool_input.get("file_path") or (data.get("tool_response") or {}).get("filePath") or ""
    if not path.endswith(".py") or not Path(path).exists():
        return 0

    ruff = ruff_cmd()
    if ruff is None:
        return 0

    subprocess.run([*ruff, "format", "--quiet", path], cwd=PROJECT, capture_output=True, timeout=60)
    subprocess.run([*ruff, "check", "--fix", "--quiet", path], cwd=PROJECT, capture_output=True, timeout=60)
    result = subprocess.run(
        [*ruff, "check", "--output-format", "concise", path],
        cwd=PROJECT, capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0 and result.stdout.strip():
        print(f"ruff found issues it could not auto-fix in {path}:", file=sys.stderr)
        print(result.stdout.strip()[:4000], file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
