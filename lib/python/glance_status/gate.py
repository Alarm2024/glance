"""Operator CLEAR gate — synthetic proof cases for HOLD vs CLEAR decisions."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from glance_status import ClassifyInput, DoctorStatus, classify

# Thresholds — fixed; do not lower for prettier decisions.
ORACLE_STALE_THRESHOLD_SECONDS = 30
LIQUIDITY_FLOOR_USD = 5000.0

ORACLE_FEED_NAMES: frozenset[str] = frozenset(
    {"price-oracle", "oracle", "price_oracle"}
)

DEFAULT_HYGIENE_PHRASES: tuple[str, ...] = (
    "hygiene",
    "passed",
    "heartbeat ok",
    "config exclusion",
)

DEFAULT_FAULT_PHRASES: tuple[str, ...] = (
    "stale",
    "timeout",
    "degraded",
    "fault",
    "error",
    "blocking",
)

INDICATOR_FAULT_STATES: frozenset[str] = frozenset(
    {"fault", "error", "down", "blocking", "eyes_fault"}
)
INDICATOR_GREEN_STATE = "green"


class GateDecision(str, Enum):
    HOLD = "HOLD"
    CLEAR = "CLEAR"


@dataclass(frozen=True)
class GateResult:
    case_id: str
    decision: GateDecision
    reason: str
    reason_code: str
    evidence: dict[str, Any]
    evidence_hash: str
    human_needed: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "decision": self.decision.value,
            "reason": self.reason,
            "reason_code": self.reason_code,
            "evidence": self.evidence,
            "evidence_hash": self.evidence_hash,
            "human_needed": self.human_needed,
        }


def compute_evidence_hash(evidence: Mapping[str, Any]) -> str:
    """SHA-256 of canonical JSON evidence — reproducible across runner and page."""
    canonical = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _feed_is_oracle(name: str) -> bool:
    normalized = name.strip().lower().replace("_", "-")
    return normalized in ORACLE_FEED_NAMES or "oracle" in normalized


def _oracle_stale_check(feeds: list[Mapping[str, Any]]) -> dict[str, Any] | None:
    for feed in feeds:
        name = str(feed.get("name", ""))
        if not _feed_is_oracle(name):
            continue
        age_seconds = feed.get("age_seconds")
        state = str(feed.get("state", "")).lower()
        stale = state == "stale" or (
            isinstance(age_seconds, (int, float))
            and age_seconds > ORACLE_STALE_THRESHOLD_SECONDS
        )
        if stale:
            return {
                "gate": "oracle_stale",
                "passed": False,
                "feed": name,
                "state": state,
                "age_seconds": age_seconds,
                "threshold_seconds": ORACLE_STALE_THRESHOLD_SECONDS,
            }
    return None


def _liquidity_check(case_input: Mapping[str, Any]) -> dict[str, Any] | None:
    liquidity = case_input.get("liquidity_usd")
    floor = case_input.get("liquidity_floor_usd", LIQUIDITY_FLOOR_USD)
    if liquidity is None:
        return None
    if not isinstance(liquidity, (int, float)):
        raise ValueError("liquidity_usd must be numeric when present")
    if not isinstance(floor, (int, float)):
        raise ValueError("liquidity_floor_usd must be numeric when present")
    if liquidity < floor:
        return {
            "gate": "thin_liquidity",
            "passed": False,
            "liquidity_usd": liquidity,
            "floor_usd": floor,
        }
    return None


def _normalize_indicator_state(state: Any) -> str:
    return str(state).strip().lower()


def _indicator_is_fault(state: str) -> bool:
    return state in INDICATOR_FAULT_STATES


def _indicator_is_green(state: str) -> bool:
    return state == INDICATOR_GREEN_STATE


def _validate_process_observed_running(
    case_id: str, case_input: Mapping[str, Any]
) -> None:
    """Reject non-boolean process_observed_running at fixture validation."""
    if "process_observed_running" not in case_input:
        return
    value = case_input["process_observed_running"]
    if type(value) is not bool:
        raise ValueError(f"{case_id}: process_observed_running must be boolean")


def _board_indicator_stats(indicators: list[Mapping[str, Any]]) -> dict[str, Any]:
    total = len(indicators)
    green_count = 0
    fault_count = 0
    for indicator in indicators:
        state = _normalize_indicator_state(indicator.get("state", ""))
        if _indicator_is_fault(state):
            fault_count += 1
        elif _indicator_is_green(state):
            green_count += 1
    return {
        "total_indicator_count": total,
        "green_indicator_count": green_count,
        "fault_indicator_count": fault_count,
        "all_green": green_count == total and total > 0,
        "any_not_green": green_count < total and fault_count == 0,
        "any_fault": fault_count > 0,
    }


def _false_green_check(case_input: Mapping[str, Any]) -> dict[str, Any] | None:
    """Case 4 — all indicators green, no fault, process not observed running."""
    indicators = case_input.get("indicators")
    if not isinstance(indicators, list) or not indicators:
        return None
    process_running = case_input.get("process_observed_running")
    if process_running is not False:
        return None

    stats = _board_indicator_stats(indicators)
    if stats["any_fault"] or not stats["all_green"]:
        return None

    return {
        "gate": "false_green_board",
        "passed": False,
        "green_indicator_count": stats["green_indicator_count"],
        "total_indicator_count": stats["total_indicator_count"],
        "process_observed_running": process_running,
    }


def _mostly_green_no_fault_check(case_input: Mapping[str, Any]) -> dict[str, Any] | None:
    """Case 5 — at least one non-green, no fault, process not observed running."""
    indicators = case_input.get("indicators")
    if not isinstance(indicators, list) or not indicators:
        return None
    process_running = case_input.get("process_observed_running")
    if process_running is not False:
        return None

    stats = _board_indicator_stats(indicators)
    if stats["any_fault"] or not stats["any_not_green"]:
        return None

    return {
        "gate": "mostly_green_no_fault",
        "passed": False,
        "green_indicator_count": stats["green_indicator_count"],
        "total_indicator_count": stats["total_indicator_count"],
        "process_observed_running": process_running,
    }


def _doctor_check(doctor: Mapping[str, Any]) -> dict[str, Any]:
    blocking_flag = bool(doctor.get("blocking_flag", False))
    message = str(doctor.get("message", ""))
    hygiene = list(doctor.get("hygiene_phrases", DEFAULT_HYGIENE_PHRASES))
    faults = list(doctor.get("fault_phrases", DEFAULT_FAULT_PHRASES))

    status = classify(
        ClassifyInput(
            blocking_flag=blocking_flag,
            raw_message=message,
            hygiene_phrases=hygiene,
            fault_phrases=faults,
        )
    )

    return {
        "gate": "doctor_classify",
        "blocking_flag": blocking_flag,
        "message": message,
        "doctor_status": status.value,
        "passed": status in {DoctorStatus.OK, DoctorStatus.WARN},
        "refuse_to_classify": status == DoctorStatus.UNKNOWN,
    }


def evaluate_gate(case_id: str, case_input: Mapping[str, Any]) -> GateResult:
    """Evaluate one synthetic proof case — fixed gate order, no live wiring."""
    checks: list[dict[str, Any]] = []

    blocking_flag = bool(case_input.get("blocking_flag", False))
    blocking_check = {"gate": "blocking_flag", "passed": not blocking_flag, "value": blocking_flag}
    checks.append(blocking_check)
    if blocking_flag:
        evidence = _build_evidence(case_id, checks, "blocking_flag")
        return _hold(
            case_id,
            "Blocking flag set — operator gate stays HOLD",
            "blocking_flag",
            evidence,
            "Operator must clear blocking condition before any CLEAR.",
        )

    feeds = case_input.get("feeds", [])
    if not isinstance(feeds, list):
        raise ValueError("feeds must be a list")

    oracle_check = _oracle_stale_check(feeds)
    if oracle_check:
        checks.append(oracle_check)
        evidence = _build_evidence(case_id, checks, "stale_oracle_feed")
        return _hold(
            case_id,
            f"Oracle feed stale ({oracle_check.get('feed')}) — price reference unreliable",
            "stale_oracle_feed",
            evidence,
            "Operator must confirm oracle freshness or switch reference before CLEAR.",
        )
    checks.append({"gate": "oracle_stale", "passed": True})

    liquidity_check = _liquidity_check(case_input)
    if liquidity_check:
        checks.append(liquidity_check)
        evidence = _build_evidence(case_id, checks, "thin_liquidity")
        return _hold(
            case_id,
            f"Depth ${liquidity_check['liquidity_usd']:,.0f} below floor ${liquidity_check['floor_usd']:,.0f}",
            "thin_liquidity",
            evidence,
            "Operator must accept slippage risk or wait for depth before CLEAR.",
        )
    if case_input.get("liquidity_usd") is not None:
        checks.append({"gate": "thin_liquidity", "passed": True})

    doctor = case_input.get("doctor")
    if isinstance(doctor, Mapping):
        doctor_result = _doctor_check(doctor)
        checks.append(doctor_result)
        if doctor_result.get("refuse_to_classify"):
            evidence = _build_evidence(case_id, checks, "refuse_to_classify")
            return _hold(
                case_id,
                "REFUSE TO CLASSIFY — doctor message unmatched by hygiene or fault allowlists",
                "refuse_to_classify",
                evidence,
                "Operator must classify the doctor message, update allowlists, or accept HOLD.",
            )
        if doctor_result.get("doctor_status") == DoctorStatus.BLOCKING.value:
            evidence = _build_evidence(case_id, checks, "doctor_blocking")
            return _hold(
                case_id,
                "Doctor blocking — gate stays HOLD",
                "doctor_blocking",
                evidence,
                "Operator must resolve blocking doctor status before CLEAR.",
            )
        if doctor_result.get("doctor_status") == DoctorStatus.WARN.value:
            evidence = _build_evidence(case_id, checks, "doctor_warn")
            return _hold(
                case_id,
                "Doctor warn — gate stays HOLD until operator review",
                "doctor_warn",
                evidence,
                "Operator must review warn-level doctor message before CLEAR.",
            )

    false_green = _false_green_check(case_input)
    if false_green:
        checks.append(false_green)
        evidence = _build_evidence(case_id, checks, "false_green_board")
        return _hold(
            case_id,
            "Board reports all green while no running process was observed",
            "false_green_board",
            evidence,
            "Operator must confirm the process is running before CLEAR.",
        )

    mostly_green = _mostly_green_no_fault_check(case_input)
    if mostly_green:
        checks.append(mostly_green)
        evidence = _build_evidence(case_id, checks, "mostly_green_no_fault")
        return _hold(
            case_id,
            "Board reports no fault while no running process was observed",
            "mostly_green_no_fault",
            evidence,
            "Operator must confirm the process is running before CLEAR.",
        )

    checks.append({"gate": "all_gates", "passed": True})
    evidence = _build_evidence(case_id, checks, "clear")
    evidence_hash = compute_evidence_hash(evidence)
    return GateResult(
        case_id=case_id,
        decision=GateDecision.CLEAR,
        reason="All gates passed — operator may CLEAR (human gate still required)",
        reason_code="clear",
        evidence=evidence,
        evidence_hash=evidence_hash,
        human_needed="Operator must still explicitly CLEAR — no auto-send.",
    )


def _build_evidence(
    case_id: str, checks: list[dict[str, Any]], reason_code: str
) -> dict[str, Any]:
    return {
        "version": "1",
        "case_id": case_id,
        "reason_code": reason_code,
        "thresholds": {
            "oracle_stale_seconds": ORACLE_STALE_THRESHOLD_SECONDS,
            "liquidity_floor_usd": LIQUIDITY_FLOOR_USD,
        },
        "checks": checks,
    }


def _hold(
    case_id: str,
    reason: str,
    reason_code: str,
    evidence: dict[str, Any],
    human_needed: str,
) -> GateResult:
    evidence_hash = compute_evidence_hash(evidence)
    return GateResult(
        case_id=case_id,
        decision=GateDecision.HOLD,
        reason=reason,
        reason_code=reason_code,
        evidence=evidence,
        evidence_hash=evidence_hash,
        human_needed=human_needed,
    )


def evaluate_fixture(fixture: Mapping[str, Any]) -> GateResult:
    """Evaluate a proof fixture JSON object."""
    if fixture.get("synthetic") is not True:
        raise ValueError("proof fixture must set synthetic: true")
    case_id = fixture.get("case_id")
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError("proof fixture missing case_id")
    case_input = fixture.get("input")
    if not isinstance(case_input, Mapping):
        raise ValueError("proof fixture missing input object")
    _validate_process_observed_running(case_id, case_input)
    return evaluate_gate(case_id, case_input)


__all__ = [
    "GateDecision",
    "GateResult",
    "LIQUIDITY_FLOOR_USD",
    "ORACLE_STALE_THRESHOLD_SECONDS",
    "compute_evidence_hash",
    "evaluate_fixture",
    "evaluate_gate",
]
