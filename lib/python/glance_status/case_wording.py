"""CLEAR LAB case wording gates — load-bearing copy constraints."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable, Mapping

HASH_PROOF_DISCLAIMER = (
    "Same fixture in, same decision out. This proves the case was not "
    "changed after the fact. It does not prove the decision was right."
)

AI_ASSISTED_FINDING_LABEL = "AI-assisted analysis of public pages."

# No counterfactual outcomes: a quote is not a fill; refusal does not "cost" money.
COUNTERFACTUAL_BANNED_PHRASES: tuple[str, ...] = (
    "would have paid",
    "would have filled",
    "would have landed",
    "would have worked",
    "refusal costs",
    "costs money",
    "costs opportunity",
    "cost money",
    "really would have paid",
    "gap that really would have paid",
    "favorable window",
    "favorable spread",
    "skip a favorable",
    "missed profit",
    "lost money",
    "lost opportunity",
    "we cannot know that it would",
)

# Cases that reference earn schedule cannot ship until page 35 defines what a credit is for.
EARN_SCHEDULE_MARKERS: tuple[str, ...] = (
    "earn schedule",
    "earning schedule",
    "credit schedule",
    "credits earned",
    "credit earned",
)

# Reproducible proof cases must not require live credentials or network services.
FIXTURE_CREDENTIAL_MARKERS: tuple[str, ...] = (
    "redis_url",
    "rpc_url",
    "api_key",
    "api-key",
    "bearer ",
    "private_key",
    "secret_key",
    "process.env",
    "os.environ",
)

# Fixture fields must record inputs and the decision — not counterfactual outcomes.
FIXTURE_OUTCOME_BANNED_KEYS: tuple[str, ...] = (
    "gap_bps",
    "gap_size",
    "gap_closed",
    "gap_closed_seconds",
    "close_seconds",
    "spread_captured",
    "missed_profit",
    "missed_pnl",
    "forgone",
    "would_have",
    "would_have_paid",
    "would_have_filled",
    "would_have_landed",
    "opportunity_cost",
    "profit_if",
    "pnl_if",
    "could_have",
)

_FIXTURE_OUTCOME_BANNED_KEYS_NORMALIZED = frozenset(
    key.lower().replace("-", "").replace("_", "") for key in FIXTURE_OUTCOME_BANNED_KEYS
)

_FIXTURE_OUTCOME_FIELD_MESSAGE = (
    "A fixture records inputs and the decision. What did not happen is not an input."
)

_ORACLE_AGE_DISPLAY = re.compile(
    r"price-oracle[^·\n]*stale\s*·\s*(\d+)s",
    re.IGNORECASE,
)
_STALE_ORACLE_CANONICAL_SECONDS = 47


def _price_oracle_age_seconds(fixture: Mapping[str, object]) -> float | None:
    case_input = fixture.get("input")
    if not isinstance(case_input, Mapping):
        return None
    feeds = case_input.get("feeds")
    if not isinstance(feeds, list):
        return None
    for feed in feeds:
        if not isinstance(feed, Mapping):
            continue
        name = str(feed.get("name", "")).strip().lower().replace("_", "-")
        if name != "price-oracle":
            continue
        age = feed.get("age_seconds")
        if isinstance(age, (int, float)):
            return float(age)
    return None


_NEGATION_PREFIXES = (
    "do not claim",
    "does not claim",
    "cannot claim",
    "can't claim",
    "we do not claim",
    "we cannot know",
    "cannot know",
    "does not prove",
    "do not prove",
    "does not decide on outcome",
    "system does not decide on outcome",
)


def _counterfactual_in_positive_context(text: str, phrase: str) -> bool:
    """True when phrase appears outside an explicit disclaimer negation."""
    lower = text.lower()
    needle = phrase.lower()
    start = 0
    while True:
        idx = lower.find(needle, start)
        if idx == -1:
            return False
        window = lower[max(0, idx - 96) : idx]
        if not any(marker in window for marker in _NEGATION_PREFIXES):
            return True
        start = idx + len(needle)


def assert_no_counterfactual_outcomes(text: str, *, label: str = "case copy") -> None:
    """Raise ValueError when copy states or implies refused trades would have paid."""
    for phrase in COUNTERFACTUAL_BANNED_PHRASES:
        if _counterfactual_in_positive_context(text, phrase):
            raise ValueError(
                f"{label}: counterfactual outcome banned — found {phrase!r}. "
                "State what was observed and what was refused; never what would have happened."
            )


def assert_no_earn_schedule_reference(text: str, *, label: str = "case copy") -> None:
    """Block earn-schedule cases until page 35 defines what a credit is for."""
    lower = text.lower()
    for marker in EARN_SCHEDULE_MARKERS:
        if marker in lower:
            raise ValueError(
                f"{label}: earn-schedule reference blocked — found {marker!r}. "
                "Page 35 must state what a credit is for before such cases ship."
            )


def assert_case_copy(text: str, *, label: str = "case copy") -> None:
    """Apply all CLEAR LAB wording gates to one string."""
    assert_no_counterfactual_outcomes(text, label=label)
    assert_no_earn_schedule_reference(text, label=label)


def assert_hash_proof_disclaimer_present(text: str, *, label: str = "proof page") -> None:
    if HASH_PROOF_DISCLAIMER not in text:
        raise ValueError(f"{label}: missing hash proof disclaimer")


def _normalize_fixture_key(key: str) -> str:
    return key.lower().replace("-", "").replace("_", "")


def _fixture_outcome_field_error(label: str, key_path: str, detail: str) -> ValueError:
    return ValueError(
        f"fixture outcome field banned — {label} {key_path}. "
        f"{detail} {_FIXTURE_OUTCOME_FIELD_MESSAGE}"
    )


def assert_fixture_no_outcome_fields(fixture: Mapping[str, object], *, label: str) -> None:
    """Reject fixture keys or string values that describe outcomes that did not occur."""

    def _walk(value: object, path: str) -> None:
        if isinstance(value, Mapping):
            for key, item in value.items():
                key_path = f"{path}.{key}" if path else str(key)
                normalized = _normalize_fixture_key(str(key))
                if normalized in _FIXTURE_OUTCOME_BANNED_KEYS_NORMALIZED:
                    raise _fixture_outcome_field_error(
                        label,
                        key_path,
                        f"Banned outcome key {key!r}.",
                    )
                _walk(item, key_path)
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                _walk(item, f"{path}[{idx}]")
        elif isinstance(value, str):
            for phrase in COUNTERFACTUAL_BANNED_PHRASES:
                if _counterfactual_in_positive_context(value, phrase):
                    raise _fixture_outcome_field_error(
                        label,
                        path,
                        f"Counterfactual phrase {phrase!r} in string value.",
                    )

    _walk(fixture, "")


def assert_fixture_self_contained(fixture: Mapping[str, object], *, label: str) -> None:
    """Proof fixtures must run offline with no keys or network dependencies."""
    raw = json.dumps(fixture, sort_keys=True)
    lower = raw.lower()
    for marker in FIXTURE_CREDENTIAL_MARKERS:
        if marker.lower() in lower:
            raise ValueError(
                f"{label}: fixture requires credentials or env ({marker!r}) — "
                "seal the fixture or do not ship the case."
            )
    assert_fixture_no_outcome_fields(fixture, label=label)


def assert_stale_oracle_age_consistent(
    fixture: Mapping[str, object],
    *,
    label: str,
    canonical_seconds: int = _STALE_ORACLE_CANONICAL_SECONDS,
) -> None:
    """stale-oracle fixture must use the same age as the demo card (47s)."""
    if fixture.get("case_id") != "stale-oracle":
        return
    age = _price_oracle_age_seconds(fixture)
    if age is None:
        raise ValueError(f"{label}: stale-oracle fixture missing price-oracle age_seconds")
    if age != canonical_seconds:
        raise ValueError(
            f"{label}: price-oracle age_seconds must be {canonical_seconds}, got {age}"
        )


def assert_proof_page_oracle_display(text: str, *, label: str = "proof page") -> None:
    """Published copy for stale-oracle must show stale · 47s when using that fixture."""
    if "stale-oracle" not in text and "price-oracle" not in text:
        return
    match = _ORACLE_AGE_DISPLAY.search(text)
    if match and int(match.group(1)) != _STALE_ORACLE_CANONICAL_SECONDS:
        raise ValueError(
            f"{label}: price-oracle display must read stale · {_STALE_ORACLE_CANONICAL_SECONDS}s"
        )


def scan_case_strings(paths: Iterable[Path]) -> list[tuple[str, str]]:
    """Return (label, text) pairs from JSON string values and raw file text."""
    pairs: list[tuple[str, str]] = []
    for path in paths:
        label = str(path)
        text = path.read_text(encoding="utf-8")
        pairs.append((label, text))
        if path.suffix.lower() == ".json":
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                continue
            strings: list[str] = []

            def _walk(value: object) -> None:
                if isinstance(value, str):
                    strings.append(value)
                elif isinstance(value, dict):
                    for item in value.values():
                        _walk(item)
                elif isinstance(value, list):
                    for item in value:
                        _walk(item)

            _walk(payload)
            for idx, string in enumerate(strings):
                pairs.append((f"{label}#{idx}", string))
    return pairs


def assert_proof_tree(repo_root: Path) -> None:
    """CI helper — scan proof fixtures, manifest, page, and gate runner copy."""
    proof_dir = repo_root / "proof"
    paths = [
        proof_dir / "index.html",
        proof_dir / "manifest.json",
        repo_root / "lib" / "python" / "glance_status" / "gate.py",
        repo_root / "scripts" / "run_proof.py",
    ]
    paths.extend(sorted((proof_dir / "fixtures").glob("*.json")))

    for label, text in scan_case_strings(paths):
        assert_case_copy(text, label=label)

    page = (proof_dir / "index.html").read_text(encoding="utf-8")
    assert_hash_proof_disclaimer_present(page)
    assert_proof_page_oracle_display(page)

    for fixture_path in sorted((proof_dir / "fixtures").glob("*.json")):
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"{fixture_path}: expected JSON object")
        assert_fixture_self_contained(payload, label=str(fixture_path))
        assert_stale_oracle_age_consistent(payload, label=str(fixture_path))


__all__ = [
    "AI_ASSISTED_FINDING_LABEL",
    "COUNTERFACTUAL_BANNED_PHRASES",
    "EARN_SCHEDULE_MARKERS",
    "FIXTURE_OUTCOME_BANNED_KEYS",
    "HASH_PROOF_DISCLAIMER",
    "assert_case_copy",
    "assert_fixture_no_outcome_fields",
    "assert_fixture_self_contained",
    "assert_hash_proof_disclaimer_present",
    "assert_no_counterfactual_outcomes",
    "assert_no_earn_schedule_reference",
    "assert_proof_page_oracle_display",
    "assert_proof_tree",
    "assert_stale_oracle_age_consistent",
    "scan_case_strings",
]
