#!/usr/bin/env python3
"""Scan repo status strings and fail on banned overclaim phrases.

Exit codes:
  0  every listed file was scanned and no banned phrase was found
  1  a banned phrase was found, or zero files were scanned (fail closed)
  2  GLANCE_CHECK_PATHS lists a file that does not exist (nothing is scanned)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Iterable

from glance_status import assert_no_overclaim


def _collect_strings(value: object, out: list[str]) -> None:
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            _collect_strings(item, out)
    elif isinstance(value, list):
        for item in value:
            _collect_strings(item, out)


def _read_strings(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return [text]
        strings: list[str] = []
        _collect_strings(payload, strings)
        return strings
    return [line for line in text.splitlines() if line.strip()]


def _default_paths(repo_root: Path) -> list[Path]:
    candidates = [
        repo_root / "demo" / "fixture.json",
        repo_root / "status.json",
    ]
    return [path for path in candidates if path.is_file()]


def _resolve_paths(repo_root: Path) -> tuple[list[Path], list[str]]:
    raw = os.environ.get("GLANCE_CHECK_PATHS", "").strip()
    if not raw:
        return _default_paths(repo_root), []

    paths: list[Path] = []
    missing: list[str] = []
    for line in raw.splitlines():
        entry = line.strip()
        if not entry:
            continue
        path = Path(entry)
        if not path.is_absolute():
            path = repo_root / path
        if path.is_file():
            paths.append(path)
        else:
            missing.append(entry)
    return paths, missing


EXIT_FINDINGS = 1
EXIT_MISSING_FILE = 2


def _banned_phrases() -> list[str]:
    raw = os.environ.get("GLANCE_CHECK_BANNED", "guaranteed,profit,alpha")
    return [part.strip() for part in raw.split(",") if part.strip()]


def main() -> int:
    workspace = os.environ.get("GITHUB_WORKSPACE")
    if workspace:
        repo_root = Path(workspace)
    else:
        repo_root = Path(__file__).resolve().parents[3]
    paths, missing = _resolve_paths(repo_root)
    banned = _banned_phrases()

    if missing:
        # Not a banned-phrase finding: the gate was pointed at a file that is
        # not there, so nothing was scanned. Its own message and exit code let
        # a caller tell the two apart.
        print(
            f"glance-check: missing file — {len(missing)} of "
            f"{len(missing) + len(paths)} path(s) in `paths` do not exist; "
            "nothing was scanned:",
            file=sys.stderr,
        )
        for entry in missing:
            print(f"  • missing file: {entry} (requested path does not exist)", file=sys.stderr)
        return EXIT_MISSING_FILE

    if not paths:
        # Fail closed: a gate that scans nothing must not pass silently.
        print(
            "glance: no files to scan - set `paths` "
            "(zero files scanned; failing closed)",
            file=sys.stderr,
        )
        return EXIT_FINDINGS

    failures: list[str] = []
    checked = 0

    for path in paths:
        try:
            label = str(path.relative_to(repo_root))
        except ValueError:
            label = str(path)
        for status in _read_strings(path):
            checked += 1
            try:
                assert_no_overclaim(status, banned)
            except ValueError as exc:
                preview = status if len(status) <= 80 else status[:77] + "..."
                failures.append(f"{label}: {exc} in {preview!r}")

    if failures:
        print("glance-check failed — banned overclaim phrase(s) found:", file=sys.stderr)
        for line in failures:
            print(f"  • {line}", file=sys.stderr)
        return EXIT_FINDINGS

    print(f"glance-check passed ({checked} string(s) scanned across {len(paths)} file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
