"""Glance status — Python port of the glance-status Rust crate."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class DoctorStatus(str, Enum):
    OK = "ok"
    WARN = "warn"
    EYES_FAULT = "eyes_fault"
    BLOCKING = "blocking"
    UNKNOWN = "unknown"


@dataclass
class ClassifyInput:
    blocking_flag: bool
    raw_message: str
    hygiene_phrases: list[str] = field(default_factory=list)
    fault_phrases: list[str] = field(default_factory=list)


_URL_WITH_QUERY = re.compile(r"https?://[^\s]+?\?[^\s#]+")
_HEX_KEY = re.compile(r"\b[0-9a-fA-F]{32,64}\b")
_BASE58_KEY = re.compile(r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b")
_API_KEY_PREFIX = re.compile(r"\b(sk|pk|api)[_-][A-Za-z0-9][A-Za-z0-9_-]{15,}\b")
_BEARER_TOKEN = re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{20,}\b")

_REDACTED_URL = "[REDACTED_URL]"
_REDACTED_HEX = "[REDACTED_HEX]"
_REDACTED_KEY = "[REDACTED_KEY]"
_REDACTED_SECRET = "[REDACTED_SECRET]"


def classify(input: ClassifyInput) -> DoctorStatus:
    """Classify a doctor message (blocking → hygiene → fault allowlist → unknown)."""
    if input.blocking_flag:
        return DoctorStatus.BLOCKING

    msg = input.raw_message.lower()

    for phrase in input.hygiene_phrases:
        if phrase.lower() in msg:
            return DoctorStatus.OK

    for phrase in input.fault_phrases:
        if phrase.lower() in msg:
            return DoctorStatus.WARN

    return DoctorStatus.UNKNOWN


def redact(input_text: str) -> str:
    """Strip URLs with query params, key-shaped hex/base58, and API-key patterns."""
    out = _URL_WITH_QUERY.sub(_REDACTED_URL, input_text)
    out = _BEARER_TOKEN.sub(_REDACTED_SECRET, out)
    out = _API_KEY_PREFIX.sub(_REDACTED_SECRET, out)
    out = _HEX_KEY.sub(_REDACTED_HEX, out)
    out = _BASE58_KEY.sub(_REDACTED_KEY, out)
    return out


def assert_no_overclaim(status_text: str, banned: Iterable[str]) -> None:
    """Raise ValueError if status_text contains any banned phrase (case-insensitive)."""
    lower = status_text.lower()
    for phrase in banned:
        if phrase.lower() in lower:
            raise ValueError(
                f"status string contains banned overclaim phrase: {phrase!r}"
            )


from glance_status.gate import (
    GateDecision,
    GateResult,
    LIQUIDITY_FLOOR_USD,
    ORACLE_STALE_THRESHOLD_SECONDS,
    compute_evidence_hash,
    evaluate_fixture,
    evaluate_gate,
)
from glance_status.posture import (
    ALLOWED_POSTURE_MODES,
    StatusSummary,
    assert_dry_posture,
    assert_eyes_only_fixture,
    assert_no_send_suggestions,
    assert_page_sources_dry,
    extract_demo_fixture_from_app_js,
    is_allowed_posture_mode,
    summarize_status,
)

__all__ = [
    "GateDecision",
    "GateResult",
    "LIQUIDITY_FLOOR_USD",
    "ORACLE_STALE_THRESHOLD_SECONDS",
    "compute_evidence_hash",
    "evaluate_fixture",
    "evaluate_gate",
    "ALLOWED_POSTURE_MODES",
    "ClassifyInput",
    "DoctorStatus",
    "StatusSummary",
    "assert_dry_posture",
    "assert_eyes_only_fixture",
    "assert_no_overclaim",
    "assert_no_send_suggestions",
    "assert_page_sources_dry",
    "classify",
    "extract_demo_fixture_from_app_js",
    "is_allowed_posture_mode",
    "redact",
    "summarize_status",
]
