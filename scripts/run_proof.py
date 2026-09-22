#!/usr/bin/env python3
"""Run CLEAR LAB synthetic proof cases — one command after clone.

Usage (from repo root):
  python3 scripts/run_proof.py

Stranger path (fresh clone):
  git clone https://github.com/Alarm2024/glance && cd glance && python3 scripts/run_proof.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running without pip install — lib/python is on the path.
_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "lib" / "python"))

from glance_status.gate import evaluate_fixture  # noqa: E402

FIXTURE_ORDER = (
    "stale-oracle.json",
    "thin-liquidity.json",
    "refuse-to-classify.json",
    "all-green.json",
    "mostly-green.json",
    "fault-board.json",
)


def main() -> int:
    fixtures_dir = _REPO_ROOT / "proof" / "fixtures"
    missing = [name for name in FIXTURE_ORDER if not (fixtures_dir / name).is_file()]
    if missing:
        for name in missing:
            print(f"run_proof: missing fixture: {fixtures_dir / name}", file=sys.stderr)
        return 1

    from glance_status.case_wording import HASH_PROOF_DISCLAIMER

    print("CLEAR LAB — synthetic proof cases (dry HOLD · no live claims)")
    print("No keys · no network · fixtures only")
    print("=" * 64)

    results: list[dict] = []
    for name in FIXTURE_ORDER:
        path = fixtures_dir / name
        fixture = json.loads(path.read_text(encoding="utf-8"))
        result = evaluate_fixture(fixture)
        row = result.as_dict()
        results.append(row)

        print(f"\ncase: {row['case_id']}")
        print(f"  decision:       {row['decision']}")
        print(f"  reason:         {row['reason']}")
        print(f"  reason_code:    {row['reason_code']}")
        print(f"  evidence_hash:  {row['evidence_hash']}")
        print(f"  human_needed:   {row['human_needed']}")

    print("\n" + "=" * 64)
    print(f"cases: {len(results)} · all synthetic · compare hashes to /proof/")
    print(f"hash limit: {HASH_PROOF_DISCLAIMER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
