"""Tests for CLEAR LAB case wording gates."""

from __future__ import annotations

from pathlib import Path

import pytest

from glance_status.case_wording import (
    AI_ASSISTED_FINDING_LABEL,
    HASH_PROOF_DISCLAIMER,
    assert_case_copy,
    assert_fixture_no_outcome_fields,
    assert_hash_proof_disclaimer_present,
    assert_no_counterfactual_outcomes,
    assert_no_earn_schedule_reference,
    assert_proof_tree,
    assert_stale_oracle_age_consistent,
)

_REPO = Path(__file__).resolve().parents[3]


def test_counterfactual_phrases_rejected() -> None:
    with pytest.raises(ValueError, match="counterfactual"):
        assert_no_counterfactual_outcomes("The refusal costs money.")
    with pytest.raises(ValueError, match="counterfactual"):
        assert_no_counterfactual_outcomes("a gap that really would have paid")


def test_observed_refusal_copy_allowed() -> None:
    assert_case_copy(
        "HOLD, on feed age. price-oracle stale · 47s. "
        "We do not claim it would have filled — we cannot know that."
    )


def test_earn_schedule_blocked() -> None:
    with pytest.raises(ValueError, match="earn-schedule"):
        assert_no_earn_schedule_reference("See the earn schedule on page 35.")


def test_hash_disclaimer_required_on_proof_page() -> None:
    page = (_REPO / "proof" / "index.html").read_text(encoding="utf-8")
    assert_hash_proof_disclaimer_present(page)
    assert HASH_PROOF_DISCLAIMER in page


def test_stale_oracle_fixture_uses_47s() -> None:
    import json

    fixture = json.loads(
        (_REPO / "proof" / "fixtures" / "stale-oracle.json").read_text(encoding="utf-8")
    )
    assert_stale_oracle_age_consistent(fixture, label="stale-oracle.json")


def test_proof_tree_passes() -> None:
    assert_proof_tree(_REPO)


def test_ai_assisted_label_constant() -> None:
    assert AI_ASSISTED_FINDING_LABEL == "AI-assisted analysis of public pages."


def test_fixture_gap_closed_seconds_rejected() -> None:
    fixture = {
        "case_id": "stale-oracle",
        "input": {"gap_closed_seconds": 41},
    }
    with pytest.raises(ValueError, match="fixture outcome field banned"):
        assert_fixture_no_outcome_fields(fixture, label="proof/fixtures/X.json")


def test_fixture_counterfactual_note_string_rejected() -> None:
    fixture = {
        "case_id": "thin-liquidity",
        "input": {"note": "the gap would have paid"},
    }
    with pytest.raises(ValueError, match="fixture outcome field banned"):
        assert_fixture_no_outcome_fields(fixture, label="proof/fixtures/X.json")


def test_fixture_camelcase_gap_closed_rejected() -> None:
    fixture = {
        "case_id": "thin-liquidity",
        "input": {"gapClosed": True},
    }
    with pytest.raises(ValueError, match="fixture outcome field banned"):
        assert_fixture_no_outcome_fields(fixture, label="proof/fixtures/X.json")


def test_shipped_fixtures_pass_outcome_gate() -> None:
    import json

    for name in (
        "stale-oracle.json",
        "thin-liquidity.json",
        "refuse-to-classify.json",
        "all-green.json",
        "mostly-green.json",
    ):
        fixture = json.loads(
            (_REPO / "proof" / "fixtures" / name).read_text(encoding="utf-8")
        )
        assert_fixture_no_outcome_fields(fixture, label=f"proof/fixtures/{name}")
