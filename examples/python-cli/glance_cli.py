#!/usr/bin/env python3
"""Minimal CLI demo for classify, redact, and assert_no_overclaim."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from glance_status import (
    ClassifyInput,
    DoctorStatus,
    assert_no_overclaim,
    classify,
    redact,
    summarize_status,
)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "usage: glance_cli.py {classify|redact|assert-no-overclaim|summarize|demo} [args...]",
            file=sys.stderr,
        )
        raise SystemExit(1)

    cmd = sys.argv[1]

    if cmd == "classify":
        message = sys.argv[2] if len(sys.argv) > 2 else "Hygiene checks passed"
        status = classify(
            ClassifyInput(
                blocking_flag=False,
                raw_message=message,
                hygiene_phrases=["hygiene", "passed"],
                fault_phrases=["stale", "timeout", "degraded"],
            )
        )
        print(status.value)

    elif cmd == "redact":
        text = " ".join(sys.argv[2:])
        if not text:
            print("usage: glance_cli.py redact <text>", file=sys.stderr)
            raise SystemExit(1)
        print(redact(text))

    elif cmd == "assert-no-overclaim":
        if len(sys.argv) < 3:
            print(
                "usage: glance_cli.py assert-no-overclaim <status> [banned...]",
                file=sys.stderr,
            )
            raise SystemExit(1)
        status_text = sys.argv[2]
        banned = sys.argv[3:] or ["guaranteed", "profit", "alpha"]
        try:
            assert_no_overclaim(status_text, banned)
            print("ok")
        except ValueError as exc:
            print(exc, file=sys.stderr)
            raise SystemExit(1) from exc

    elif cmd == "summarize":
        if len(sys.argv) > 2:
            payload = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        else:
            payload = json.load(sys.stdin)
        print(summarize_status(payload).value)

    elif cmd == "demo":
        status = classify(
            ClassifyInput(
                blocking_flag=False,
                raw_message="Feed stale for 47s",
                hygiene_phrases=["hygiene"],
                fault_phrases=["stale"],
            )
        )
        assert status == DoctorStatus.WARN
        safe = redact("see https://example.com/x?token=secret")
        assert_no_overclaim(safe, ["guaranteed profit"])
        print(f"demo ok · status={status.value} · redacted={safe}")

    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
