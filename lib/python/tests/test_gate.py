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
    "all-green": "1f4ada1b9487d2af4821accdf82f956c32b69b656fcb1fac0cbeca76dfbcb139",
    "mostly-green": "519e6a04ea1b3f7a8b0051a6b1df13788fdd4a9fba70faa35eeb9eaed6ecb638",
    "fault-board": "f228cabb21c22652f91c85b07da079689295edced88d85520824a678ff801392",
}

BOARD_GATES = frozenset(
    {"fault_indicator_present", "false_green_board", "mostly_green_no_fault"}
)


@pytest.mark.parametrize(
    "fixture_name,reason_code",
    [
        ("stale-oracle.json", "stale_oracle_feed"),
        ("thin-liquidity.json", "thin_liquidity"),
        ("refuse-to-classify.json", "refuse_to_classify"),
        ("all-green.json", "false_green_board"),
        ("mostly-green.json", "mostly_green_no_fault"),
        ("fault-board.json", "fault_indicator_present"),
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


def _board_case_input(
    indicators: list[dict[str, str]], *, process_running: bool = False
) -> dict:
    return {
        "feeds": [{"name": "price-oracle", "state": "ok", "age_seconds": 2}],
        "liquidity_usd": 50000,
        "doctor": {
            "blocking_flag": False,
            "message": "Hygiene checks passed · heartbeat ok",
            "hygiene_phrases": ["hygiene", "passed", "heartbeat ok"],
            "fault_phrases": ["stale", "timeout", "degraded"],
        },
        "indicators": indicators,
        "process_observed_running": process_running,
    }


def test_false_green_and_mostly_green_are_mutually_exclusive() -> None:
    all_green = evaluate_fixture(
        json.loads((_FIXTURES / "all-green.json").read_text(encoding="utf-8"))
    )
    mostly_green = evaluate_fixture(
        json.loads((_FIXTURES / "mostly-green.json").read_text(encoding="utf-8"))
    )
    assert all_green.reason_code == "false_green_board"
    assert mostly_green.reason_code == "mostly_green_no_fault"


def test_mostly_green_evidence_fields() -> None:
    fixture = json.loads((_FIXTURES / "mostly-green.json").read_text(encoding="utf-8"))
    result = evaluate_fixture(fixture)
    board_check = next(
        c for c in result.evidence["checks"] if c["gate"] == "mostly_green_no_fault"
    )
    assert board_check["green_indicator_count"] == 2
    assert board_check["total_indicator_count"] == 3
    assert board_check["process_observed_running"] is False


@pytest.mark.parametrize(
    "bad_value",
    ["false", 0, 1, None, [], {}],
)
def test_process_observed_running_rejects_non_boolean(bad_value: object) -> None:
    fixture = json.loads((_FIXTURES / "all-green.json").read_text(encoding="utf-8"))
    fixture["input"]["process_observed_running"] = bad_value
    with pytest.raises(ValueError, match=r"all-green: process_observed_running must be boolean"):
        evaluate_fixture(fixture)


def _assert_exactly_one_board_gate(result) -> str:
    board_gates = [
        c["gate"] for c in result.evidence["checks"] if c["gate"] in BOARD_GATES
    ]
    assert len(board_gates) == 1, f"expected exactly one board gate, got {board_gates}"
    return board_gates[0]


def test_fault_board_fixture_holds() -> None:
    fixture = json.loads((_FIXTURES / "fault-board.json").read_text(encoding="utf-8"))
    result = evaluate_fixture(fixture)
    assert result.decision == GateDecision.HOLD
    assert result.reason_code == "fault_indicator_present"
    board_check = next(
        c for c in result.evidence["checks"] if c["gate"] == "fault_indicator_present"
    )
    assert board_check["fault_indicator_count"] == 1
    assert board_check["green_indicator_count"] == 2
    assert board_check["total_indicator_count"] == 3
    assert board_check["process_observed_running"] is False


@pytest.mark.parametrize(
    "fault_state",
    ["red", "critical", "banana", ""],
)
def test_fault_indicator_holds_with_dead_process(fault_state: str) -> None:
    result = evaluate_gate(
        f"fault-{fault_state or 'empty'}-dead",
        _board_case_input(
            [
                {"name": "slot-stream", "state": "green"},
                {"name": "rpc-link", "state": "green"},
                {"name": "price-feed", "state": fault_state},
            ],
            process_running=False,
        ),
    )
    assert result.decision == GateDecision.HOLD
    assert result.reason_code == "fault_indicator_present"
    assert _assert_exactly_one_board_gate(result) == "fault_indicator_present"


def test_fault_indicator_holds_with_running_process() -> None:
    """Fault on board fires regardless of process_observed_running."""
    result = evaluate_gate(
        "red-board-running",
        _board_case_input(
            [
                {"name": "slot-stream", "state": "green"},
                {"name": "rpc-link", "state": "green"},
                {"name": "price-feed", "state": "red"},
            ],
            process_running=True,
        ),
    )
    assert result.decision == GateDecision.HOLD
    assert result.reason_code == "fault_indicator_present"
    board_check = next(
        c for c in result.evidence["checks"] if c["gate"] == "fault_indicator_present"
    )
    assert board_check["process_observed_running"] is True


@pytest.mark.parametrize(
    "fixture_name,expected_gate",
    [
        ("all-green.json", "false_green_board"),
        ("mostly-green.json", "mostly_green_no_fault"),
        ("fault-board.json", "fault_indicator_present"),
    ],
)
def test_board_gates_are_mutually_exclusive(
    fixture_name: str, expected_gate: str
) -> None:
    fixture = json.loads((_FIXTURES / fixture_name).read_text(encoding="utf-8"))
    result = evaluate_fixture(fixture)
    assert _assert_exactly_one_board_gate(result) == expected_gate


@pytest.mark.parametrize("bad_value", ["false", 0])
def test_evaluate_gate_rejects_non_boolean_process_observed_running(
    bad_value: object,
) -> None:
    case_input = _board_case_input([{"name": "slot-stream", "state": "green"}])
    case_input["process_observed_running"] = bad_value
    with pytest.raises(ValueError, match="process_observed_running must be boolean"):
        evaluate_gate("bad-process-flag", case_input)


def test_amber_board_with_dead_process_is_mostly_green() -> None:
    result = evaluate_gate(
        "amber-board-dead",
        _board_case_input(
            [
                {"name": "slot-stream", "state": "green"},
                {"name": "rpc-link", "state": "green"},
                {"name": "price-feed", "state": "amber"},
            ],
            process_running=False,
        ),
    )
    assert result.decision == GateDecision.HOLD
    assert result.reason_code == "mostly_green_no_fault"
