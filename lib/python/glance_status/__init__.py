"""Glance status — Python mirror of the Rust glance-status M1 skeleton."""

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


class OverclaimError(Exception):
    """Raised when a status string contains a banned overclaim phrase."""

    def __init__(self, phrase: str) -> None:
        self.phrase = phrase
        super().__init__(f"status string contains banned overclaim phrase: {phrase!r}")


_URL_WITH_QUERY = re.compile(r"https?://[^\s]+?\?[^\s#]+")
_HEX_KEY = re.compile(r"\b[0-9a-fA-F]{32,64}\b")
_BASE58_KEY = re.compile(r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b")
_API_KEY_PREFIX = re.compile(r"\b(sk|pk|api)[_-][A-Za-z0-9][A-Za-z0-9_-]{15,}\b")
_BEARER_TOKEN = re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{20,}\b")

_REDACTED_URL = "[REDACTED_URL]"
_REDACTED_HEX = "[REDACTED_HEX]"
_REDACTED_KEY = "[REDACTED_KEY]"
_REDACTED_SECRET = "[REDACTED_SECRET]"


def classify_fault(
    *,
    blocking: bool,
    message: str,
    hygiene_phrases: Sequence[str] = (),
    fault_phrases: Sequence[str] = (),
    eyes_fault_phrases: Sequence[str] = (),
) -> DoctorStatus:
    """Classify a doctor message (blocking → hygiene → fault allowlist)."""
    if blocking:
        return DoctorStatus.BLOCKING

    msg = message.lower()

    for phrase in hygiene_phrases:
        if phrase.lower() in msg:
            return DoctorStatus.OK

    for phrase in eyes_fault_phrases:
        if phrase.lower() in msg:
            return DoctorStatus.EYES_FAULT

    for phrase in fault_phrases:
        if phrase.lower() in msg:
            return DoctorStatus.WARN

    if not msg.strip():
        return DoctorStatus.UNKNOWN

    return DoctorStatus.OK


def redact(input_text: str) -> str:
    """Strip URLs with query params, key-shaped hex/base58, and API-key patterns."""
    out = _URL_WITH_QUERY.sub(_REDACTED_URL, input_text)
    out = _BEARER_TOKEN.sub(_REDACTED_SECRET, out)
    out = _API_KEY_PREFIX.sub(_REDACTED_SECRET, out)
    out = _HEX_KEY.sub(_REDACTED_HEX, out)
    out = _BASE58_KEY.sub(_REDACTED_KEY, out)
    return out


def assert_no_overclaim(status: str, banned_phrases: Iterable[str]) -> None:
    """Raise OverclaimError if status contains any banned phrase (case-insensitive)."""
    lower = status.lower()
    for phrase in banned_phrases:
        if phrase.lower() in lower:
            raise OverclaimError(phrase)


__all__ = [
    "DoctorStatus",
    "OverclaimError",
    "assert_no_overclaim",
    "classify_fault",
    "redact",
]
