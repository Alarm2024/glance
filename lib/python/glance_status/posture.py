"""Eyes-only posture checks and read-only status summary for Glance fixtures."""

from __future__ import annotations

import json
import re
from enum import Enum
from typing import Any, Iterable, Mapping

# Posture modes that satisfy dry / eyes-only compose (case-insensitive match).
ALLOWED_POSTURE_MODES: frozenset[str] = frozenset(
    {
        "dry compose",
        "dry simulate",
        "observe-only",
        "eyes only",
        "eyes-only",
    }
)

# Substrings that must not appear in posture mode/detail (live send paths).
BANNED_POSTURE_PHRASES: tuple[str, ...] = (
    "armed",
    "auto-arm",
    "auto arm",
    "auto-send",
    "auto send",
    "clear+",
    "clear +",
    "live send",
    "live mode",
    "mint",
)

# Action phrases status cards must never suggest (read-only eyes).
BANNED_ACTION_SUGGESTIONS: tuple[str, ...] = (
    "click clear",
    "press clear",
    "send now",
    "auto-send",
    "auto send",
    "enable send",
    "flip dry",
    "go live",
    "arm now",
    "mint",
    "mint now",
)

# Card keys that are display-only — never action CTAs.
READ_ONLY_CARD_KEYS: frozenset[str] = frozenset(
    {"online", "doctor", "feeds", "last_signal", "build"}
)

_POSTURE_MODE_RE = re.compile(
    r"posture\s*:\s*\{[^}]*mode\s*:\s*['\"]([^'\"]+)['\"]",
    re.DOTALL,
)
_SYNTHETIC_RE = re.compile(r"synthetic\s*:\s*true\b")
_LABEL_RE = re.compile(r"label\s*:\s*['\"]([^'\"]+)['\"]")


class StatusSummary(str, Enum):
    OK = "OK"
    DEGRADED = "DEGRADED"
    FAULT = "FAULT"


def _normalize_mode(mode: str) -> str:
    return " ".join(mode.strip().lower().split())


def _contains_banned_phrase(text: str, phrase: str) -> bool:
    """Match banned phrase unless clearly negated (e.g. 'no auto-send')."""
    lower = text.lower()
    start = 0
    while True:
        pos = lower.find(phrase, start)
        if pos == -1:
            return False
        window = lower[max(0, pos - 5) : pos]
        if window.endswith("no ") or window.endswith("no-"):
            start = pos + len(phrase)
            continue
        return True


def is_allowed_posture_mode(mode: str) -> bool:
    """Return True when mode is an allowed dry / eyes-only posture label."""
    normalized = _normalize_mode(mode)
    if normalized in ALLOWED_POSTURE_MODES:
        return True
    return "dry" in normalized or "observe" in normalized or "eyes" in normalized


def assert_dry_posture(posture: Mapping[str, Any], *, label: str = "posture") -> None:
    """Raise ValueError unless posture.mode is dry compose or equivalent."""
    if not posture:
        raise ValueError(f"{label}: missing posture object")

    mode = posture.get("mode")
    if not isinstance(mode, str) or not mode.strip():
        raise ValueError(f"{label}: posture.mode must be a non-empty string")

    normalized = _normalize_mode(mode)
    if not is_allowed_posture_mode(mode):
        raise ValueError(
            f"{label}: posture.mode must be dry compose or equivalent, got {mode!r}"
        )

    detail = posture.get("detail", "")
    if isinstance(detail, str):
        for phrase in BANNED_POSTURE_PHRASES:
            if _contains_banned_phrase(detail, phrase):
                raise ValueError(
                    f"{label}: posture.detail contains banned phrase {phrase!r}"
                )

    for phrase in BANNED_POSTURE_PHRASES:
        if _contains_banned_phrase(normalized, phrase):
            raise ValueError(
                f"{label}: posture.mode contains banned phrase {phrase!r}"
            )


def _collect_card_strings(card: Any) -> list[str]:
    strings: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, str):
            strings.append(value)
        elif isinstance(value, Mapping):
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(card)
    return strings


def assert_no_send_suggestions(
    fixture: Mapping[str, Any], *, label: str = "fixture"
) -> None:
    """Raise ValueError if read-only cards suggest CLEAR, send, arm, or mint."""
    for key in READ_ONLY_CARD_KEYS:
        if key not in fixture:
            continue
        for text in _collect_card_strings(fixture[key]):
            for phrase in BANNED_ACTION_SUGGESTIONS:
                if _contains_banned_phrase(text, phrase):
                    raise ValueError(
                        f"{label}: {key} suggests action {phrase!r} in {text!r}"
                    )


def assert_eyes_only_fixture(
    fixture: Mapping[str, Any], *, label: str = "fixture"
) -> None:
    """Validate synthetic demo fixture stays eyes-only with dry posture."""
    if fixture.get("synthetic") is not True:
        raise ValueError(f"{label}: synthetic must be true for demo fixtures")

    banner = fixture.get("label", "")
    if not isinstance(banner, str) or "synthetic" not in banner.lower():
        raise ValueError(
            f"{label}: label must clearly mark synthetic demo data, got {banner!r}"
        )

    posture = fixture.get("posture")
    if not isinstance(posture, Mapping):
        raise ValueError(f"{label}: missing posture object")
    assert_dry_posture(posture, label=label)
    assert_no_send_suggestions(fixture, label=label)


def summarize_status(fixture: Mapping[str, Any]) -> StatusSummary:
    """One-line OK / DEGRADED / FAULT summary for operator status JSON (read-only)."""
    doctor = fixture.get("doctor") or {}
    if isinstance(doctor, Mapping):
        doctor_status = str(doctor.get("status", "")).lower()
        if doctor_status in {"blocking", "eyes_fault"}:
            return StatusSummary.FAULT
        if doctor_status == "warn":
            return StatusSummary.DEGRADED

    online = fixture.get("online") or {}
    if isinstance(online, Mapping):
        online_status = str(online.get("status", "")).lower()
        if online_status not in {"", "connected", "ok"}:
            return StatusSummary.FAULT

    feeds = fixture.get("feeds")
    if isinstance(feeds, list) and feeds:
        for feed in feeds:
            if not isinstance(feed, Mapping):
                continue
            state = str(feed.get("state", "")).lower()
            if state in {"fault", "error", "down", "blocking"}:
                return StatusSummary.FAULT
            if state in {"stale", "warn", "degraded", "unknown"}:
                return StatusSummary.DEGRADED

    return StatusSummary.OK


def extract_demo_fixture_from_app_js(source: str) -> dict[str, Any]:
    """Extract posture fields from the DEMO_FIXTURE object in app.js."""
    if "DEMO_FIXTURE" not in source:
        raise ValueError("app.js: could not find DEMO_FIXTURE object")
    if not _SYNTHETIC_RE.search(source):
        raise ValueError("app.js: DEMO_FIXTURE must set synthetic: true")

    mode_match = _POSTURE_MODE_RE.search(source)
    if not mode_match:
        raise ValueError("app.js: DEMO_FIXTURE missing posture.mode")
    label_match = _LABEL_RE.search(source)
    label = label_match.group(1) if label_match else ""

    return {
        "synthetic": True,
        "label": label,
        "posture": {"mode": mode_match.group(1), "detail": ""},
    }


def assert_page_sources_dry(
    *,
    fixture_path_text: str,
    app_js_text: str,
    index_html_text: str,
) -> None:
    """CI helper: fixture file, embedded page JSON, and static HTML stay eyes-only."""
    fixture = json.loads(fixture_path_text)
    if not isinstance(fixture, dict):
        raise ValueError("demo/fixture.json must be a JSON object")
    assert_eyes_only_fixture(fixture, label="demo/fixture.json")

    embedded = extract_demo_fixture_from_app_js(app_js_text)
    assert_eyes_only_fixture(embedded, label="app.js DEMO_FIXTURE")

    embedded_mode = _normalize_mode(str(embedded.get("posture", {}).get("mode", "")))
    file_mode = _normalize_mode(str(fixture.get("posture", {}).get("mode", "")))
    if embedded_mode != file_mode:
        raise ValueError(
            f"app.js DEMO_FIXTURE posture.mode {embedded_mode!r} "
            f"!= demo/fixture.json {file_mode!r}"
        )

    html_lower = index_html_text.lower()
    if "dry compose" not in html_lower:
        raise ValueError("index.html: static posture badge must show dry compose")
    if "synthetic" not in html_lower and "demo" not in html_lower:
        raise ValueError(
            "index.html: must clearly label synthetic demo (banner or hint)"
        )

    banned_in_html = ("send now", "click clear", "enable send", "go live", "armed")
    for phrase in banned_in_html:
        if phrase in html_lower:
            raise ValueError(f"index.html: contains banned action phrase {phrase!r}")


__all__ = [
    "ALLOWED_POSTURE_MODES",
    "BANNED_ACTION_SUGGESTIONS",
    "BANNED_POSTURE_PHRASES",
    "READ_ONLY_CARD_KEYS",
    "StatusSummary",
    "assert_dry_posture",
    "assert_eyes_only_fixture",
    "assert_no_send_suggestions",
    "assert_page_sources_dry",
    "extract_demo_fixture_from_app_js",
    "is_allowed_posture_mode",
    "summarize_status",
]
