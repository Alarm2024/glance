"""Tests for CLEAR LAB gate evaluation and evidence hashes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from glance_status.gate import (
    GateDecision,
    evaluate_fixture,
    evaluate_gate,
)

_REPO = Path(__file__).resolve().parents[3]
_FIXTURES = _REPO / "proof" / "fixtures"
_MANIFEST = _REPO / "proof" / "manifest.json"

GOLDEN_HASHES = {
    "stale-oracle": "703ad4b4c199499aeb1b1e5ed0518297367ad28331807b1f12e0913a1c4ad993",
    "thin-liquidity": "5b36d6bc6ffa715dd70cfaa8a76ddee22501a423e400dfe1d00f876517708552",
    "refuse-to-classify": "008f6948f3fd63b6a8955aab763f204d03dd8bb91cc8c123e3ca2fb34b3af47e",
}


@pytest.mark.parametrize(
    "fixture_name,reason_code",
    [
        ("stale-oracle.json", "stale_oracle_feed"),
        ("thin-liquidity.json", "thin_liquidity"),
        ("refuse-to-classify.json", "refuse_to_classify"),
    ],
)
def test_proof_fixtures_hold(fixture_name: str, reason_code: str) -> None:
    fixture = json.loads((_FIXTURES / fixture_name).read_text(encoding="utf-8"))
    result = evaluate_fixture(fixture)
    assert result.decision == GateDecision.HOLD
    assert result.reason_code == reason_code
    assert len(result.evidence_hash) == 64


@pytest.mark.parametrize("case_id,expected_hash", list(GOLDEN_HASHES.items()))
def test_golden_evidence_hashes(case_id: str, expected_hash: str) -> None:
    fixture = json.loads((_FIXTURES / f"{case_id}.json").read_text(encoding="utf-8"))
    result = evaluate_fixture(fixture)
    assert result.evidence_hash == expected_hash, (
        f"{case_id}: hash drift — update proof/manifest.json and proof/index.html"
    )


def test_manifest_matches_runner_output() -> None:
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    for entry in manifest["cases"]:
        fixture = json.loads((_FIXTURES / Path(entry["fixture"]).name).read_text(encoding="utf-8"))
        result = evaluate_fixture(fixture)
        assert result.decision.value == entry["decision"]
        assert result.evidence_hash == entry["evidence_hash"]
        assert result.reason_code == entry["reason_code"]


def test_refuse_to_classify_is_unknown_doctor() -> None:
    fixture = json.loads((_FIXTURES / "refuse-to-classify.json").read_text(encoding="utf-8"))
    result = evaluate_fixture(fixture)
    doctor_check = next(c for c in result.evidence["checks"] if c["gate"] == "doctor_classify")
    assert doctor_check["doctor_status"] == "unknown"
    assert doctor_check["refuse_to_classify"] is True


def test_stale_oracle_does_not_skip_threshold() -> None:
    """Age 25s with ok state should not HOLD on oracle alone."""
    result = evaluate_gate(
        "oracle-edge-ok",
        {
            "feeds": [{"name": "price-oracle", "state": "ok", "age_seconds": 25}],
            "liquidity_usd": 10000,
        },
    )
    assert result.decision == GateDecision.CLEAR


def test_thin_liquidity_at_floor_is_clear() -> None:
    result = evaluate_gate(
        "liquidity-at-floor",
        {
            "feeds": [{"name": "price-oracle", "state": "ok", "age_seconds": 2}],
            "liquidity_usd": 5000,
            "liquidity_floor_usd": 5000,
        },
    )
    assert result.decision == GateDecision.CLEAR
