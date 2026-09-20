"""Glance status — thin Python mirror of the Rust glance-status crate."""

from __future__ import annotations

import re
from enum import Enum
from typing import Iterable, Sequence


class DoctorStatus(str, Enum):
    OK = "ok"
    WARN = "warn"
    EYES_FAULT = "eyes_fault"
    BLOCKING = "blocking"
    UNKNOWN = "unknown"

    def as_str(self) -> str:
        return self.value


class OverclaimError(Exception):
    """Raised when a status string contains a banned overclaim phrase."""

    def __init__(self, phrase: str) -> None:
        self.phrase = phrase
        super().__init__(f"status string contains banned overclaim phrase: {phrase}")


_URL_WITH_QUERY = re.compile(r"https?://[^\s?]+(\?[^\s]*)")
_HEX_KEY = re.compile(r"\b[0-9a-fA-F]{32,64}\b")
_BASE58_KEY = re.compile(r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b")
_API_KEY_PREFIX = re.compile(
    r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*\S+|bearer\s+\S+"
)
_SK_PREFIX = re.compile(r"\bsk-[a-zA-Z0-9_-]{8,}\b")
_REDACTED = "[REDACTED]"


def classify_fault(
    *,
    blocking_flag: bool,
    lines: Sequence[str],
    hygiene_phrases: Sequence[str],
    fault_phrases: Sequence[str],
) -> DoctorStatus:
    """Classify doctor status: blocking → hygiene exclusion → fault allowlist."""
    if blocking_flag:
        return DoctorStatus.BLOCKING

    saw_fault = False
    saw_eyes = False

    for line in lines:
        lower = line.lower()
        if any(p.lower() in lower for p in hygiene_phrases):
            continue
        for phrase in fault_phrases:
            if phrase.lower() in lower:
                saw_fault = True
                if "eye" in phrase.lower():
                    saw_eyes = True

    if saw_eyes:
        return DoctorStatus.EYES_FAULT
    if saw_fault:
        return DoctorStatus.WARN
    if not lines:
        return DoctorStatus.UNKNOWN
    return DoctorStatus.OK


def redact(text: str) -> str:
    """Strip URLs with query params, key-shaped hex/base58, and API-key patterns."""
    out = _URL_WITH_QUERY.sub(_REDACTED, text)
    out = _API_KEY_PREFIX.sub(_REDACTED, out)
    out = _SK_PREFIX.sub(_REDACTED, out)
    out = _HEX_KEY.sub(_REDACTED, out)
    out = _BASE58_KEY.sub(_REDACTED, out)
    return out


def assert_no_overclaim(text: str, banned: Iterable[str]) -> None:
    """Raise OverclaimError if text contains any banned phrase (case-insensitive)."""
    lower = text.lower()
    for phrase in banned:
        if phrase.lower() in lower:
            raise OverclaimError(phrase)


__all__ = [
    "DoctorStatus",
    "OverclaimError",
    "assert_no_overclaim",
    "classify_fault",
    "redact",
]
