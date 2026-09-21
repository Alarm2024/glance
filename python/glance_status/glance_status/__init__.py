"""Thin Python mirror of the glance-status Rust crate."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Sequence


class DoctorStatus(str, Enum):
    OK = "ok"
    WARN = "warn"
    EYES_FAULT = "eyes_fault"
    BLOCKING = "blocking"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ClassifyInput:
    blocking: bool
    lines: Sequence[str]


def classify_fault(
    input: ClassifyInput,
    hygiene_patterns: Iterable[str],
    fault_phrases: Iterable[str],
) -> DoctorStatus:
    """Order: blocking flag → hygiene/info exclusion → fault-phrase allowlist."""
    if input.blocking:
        return DoctorStatus.BLOCKING

    hygiene = list(hygiene_patterns)
    faults = list(fault_phrases)
    saw_actionable = False

    for line in input.lines:
        trimmed = line.strip()
        if not trimmed:
            continue
        if any(pattern in trimmed for pattern in hygiene):
            continue

        saw_actionable = True
        if any(phrase in trimmed for phrase in faults):
            return DoctorStatus.EYES_FAULT

    if saw_actionable:
        return DoctorStatus.WARN
    return DoctorStatus.OK


_URL_WITH_QUERY = re.compile(r"https?://[^\s/?#]+[^\s]*\?[^\s]+")
_HEX_KEY = re.compile(r"\b(?:0x)?[0-9a-fA-F]{32,64}\b")
_BASE58_KEY = re.compile(r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b")
_API_KEY = re.compile(r"\b(?:sk|pk|api|token|key)[-_][A-Za-z0-9-]{16,}\b")
_WALLET_LIKE = re.compile(r"\b[1-9A-HJ-NP-Za-km-z]{43,44}\b")
_REDACTED = "[REDACTED]"


def redact(input: str) -> str:
    """Strip URLs with query params, key-shaped hex/base58, wallet/API-key shapes."""
    out = input
    for pattern in (
        _URL_WITH_QUERY,
        _API_KEY,
        _WALLET_LIKE,
        _BASE58_KEY,
        _HEX_KEY,
    ):
        out = pattern.sub(_REDACTED, out)
    return out


class OverclaimError(ValueError):
    def __init__(self, matches: list[str]):
        self.matches = matches
        super().__init__(
            "status string contains banned overclaim phrase(s): "
            + ", ".join(matches)
        )


def assert_no_overclaim(status: str, banned_phrases: Iterable[str]) -> None:
    """Raise OverclaimError when status contains any banned phrase."""
    lower = status.lower()
    matches = [phrase for phrase in banned_phrases if phrase and phrase.lower() in lower]
    if matches:
        raise OverclaimError(matches)
