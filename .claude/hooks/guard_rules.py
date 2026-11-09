#!/usr/bin/env python3
"""PreToolUse guard for bdub hard rules (CLAUDE.md, SPEC §5.6, §12, §14).

Checks the *new* text of Edit/Write calls on Python files under src/bdub/,
and Bash commands, and blocks (exit 2) with a reason Claude can act on.
Stdlib only. Never blocks on its own errors (exits 0).
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import PurePosixPath

PROJECT = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

# (pattern, allowed path prefixes relative to repo, message)
CODE_RULES: list[tuple[re.Pattern[str], tuple[str, ...], str]] = [
    (
        re.compile(r"^\s*(import|from)\s+(pickle|cPickle|dill|joblib)\b", re.M),
        (),
        "No pickle anywhere (SPEC §14). Use MessagePack/JSON; models load only from verified packs.",
    ),
    (
        re.compile(r"torch\.load\s*\(|allow_pickle\s*=\s*True"),
        (),
        "No pickle-based loading (torch.load / allow_pickle=True) (SPEC §14).",
    ),
    (
        re.compile(
            r"^\s*(import|from)\s+(requests|httpx|urllib3|aiohttp|websockets?|http\.client|urllib\.request)\b",
            re.M,
        ),
        ("src/bdub/net/",),
        "Network code is only allowed in src/bdub/net/ (SPEC §12, PR-1/PR-5).",
    ),
    (
        re.compile(r"\b(QtNetwork|QtWebEngine\w*|QTcpSocket|QNetworkAccessManager)\b"),
        (),
        "QtNetwork/QtWebEngine are excluded from every build (SPEC §12 PR-2). Use stdlib IPC.",
    ),
    (
        re.compile(r"^\s*(import|from)\s+PyQt6\b", re.M),
        ("src/bdub/qt.py",),
        "Import Qt only through bdub.qt (CLAUDE.md, Qt boundary).",
    ),
    (
        re.compile(r"\bQStandardPaths\b|Path\.home\(\)|os\.path\.expanduser|\bwinreg\b|%APPDATA%"),
        ("src/bdub/paths.py",),
        "All locations must come from bdub.paths; write only inside bdub-data/ (SPEC §5.6).",
    ),
    (
        re.compile(r"QSettings\(\s*\)"),
        (),
        "Use QSettings(str(paths.settings_file), QSettings.Format.IniFormat), never the default constructor (SPEC §5.6).",
    ),
    (
        re.compile(
            r"^\s*(import|from)\s+(onnxruntime|ctranslate2|faster_whisper|pywhispercpp|sherpa_onnx|torch)\b",
            re.M,
        ),
        ("src/bdub/workers/",),
        "ML libraries may only be imported inside worker processes (src/bdub/workers/) (SPEC §11.1).",
    ),
    (
        re.compile(r"^\s*(import|from)\s+(bdub\.qt|PyQt6)\b", re.M),
        ("src/bdub/qt.py", "src/bdub/app/", "src/bdub/ui/", "src/bdub/player/", "src/bdub/orchestrator/", "src/bdub/__main__.py", "src/bdub/models/"),
        "src/bdub/text/, src/bdub/audio/, and workers must stay Qt-free (CLAUDE.md).",
    ),
]

SECRET_SUFFIXES = (".p12", ".pfx", ".pem", ".key", ".cer", ".mobileprovision", ".keychain")
SECRET_NAMES = (".env", "notary-credentials", "signing-password")

BASH_RULES: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"(^|[;&|]\s*)(python3?\s+-m\s+)?pip3?\s+install\b"),
        "Use `uv add` (see .claude/skills/add-dependency) instead of pip install, so the licence/offline checks and uv.lock stay correct.",
    ),
    (
        re.compile(r"(^|[;&|]\s*)uvx\s+"),
        "Avoid uvx (it downloads tools ad hoc). Add the tool to the dev group with `uv add --group dev` and use `uv run`.",
    ),
]


def rel(path: str) -> str:
    try:
        return PurePosixPath(os.path.relpath(path, PROJECT)).as_posix()
    except ValueError:
        return path


def strip_comments_and_strings(src: str) -> str:
    """Rough filter so docstrings/comments mentioning a banned name don't trigger."""
    src = re.sub(r'("""|\'\'\')[\s\S]*?\1', "", src)
    return "\n".join(line.split("#", 1)[0] for line in src.splitlines())


def check_file(tool_input: dict) -> list[str]:
    path = tool_input.get("file_path", "")
    r = rel(path)
    name = PurePosixPath(r).name.lower()

    problems: list[str] = []
    if name.endswith(SECRET_SUFFIXES) or name in SECRET_NAMES:
        problems.append(
            f"{r}: never create or write signing certificates, keys, or credentials (packaging-engineer rules). Ask the user to provide them outside the repo."
        )
        return problems

    if not (r.startswith("src/bdub/") and r.endswith(".py")):
        return problems

    new_text = tool_input.get("content") or tool_input.get("new_string") or ""
    if not new_text:
        return problems
    code = strip_comments_and_strings(new_text)

    for pattern, allowed, message in CODE_RULES:
        if allowed and any(r == a or r.startswith(a) for a in allowed):
            continue
        if pattern.search(code):
            problems.append(f"{r}: {message}")
    return problems


def check_bash(tool_input: dict) -> list[str]:
    cmd = tool_input.get("command", "")
    return [msg for pattern, msg in BASH_RULES if pattern.search(cmd)]


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}

    if tool in ("Edit", "Write", "MultiEdit"):
        problems = check_file(tool_input)
    elif tool == "Bash":
        problems = check_bash(tool_input)
    else:
        problems = []

    if problems:
        print("Blocked by bdub hard-rule guard (.claude/hooks/guard_rules.py):", file=sys.stderr)
        for p in problems:
            print(f"- {p}", file=sys.stderr)
        print("If this is a deliberate, approved exception, ask the user to adjust the guard.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
