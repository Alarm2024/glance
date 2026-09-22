#!/usr/bin/env python3
"""CI self-test — CLEAR LAB case wording gates."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "lib" / "python"))

from glance_status.case_wording import assert_proof_tree  # noqa: E402


def main() -> int:
    try:
        assert_proof_tree(_REPO_ROOT)
    except ValueError as exc:
        print(f"case_wording_selftest failed: {exc}", file=sys.stderr)
        return 1
    print("case_wording_selftest passed — CLEAR LAB copy gates OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
