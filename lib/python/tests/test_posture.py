"""Tests for eyes-only posture checks and read-only status summary."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from glance_status import (
    StatusSummary,
    assert_dry_posture,
    assert_eyes_only_fixture,
    assert_no_send_suggestions,
    assert_page_sources_dry,
    extract_demo_fixture_from_app_js,
    is_allowed_posture_mode,
    summarize_status,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_allowed_posture_modes():
    assert is_allowed_posture_mode("dry compose")
    assert is_allowed_posture_mode("Dry Compose")
    assert is_allowed_posture_mode("observe-only")
    assert not is_allowed_posture_mode("live send")


def test_demo_fixture_passes_eyes_only():
    payload = json.loads((REPO_ROOT / "demo" / "fixture.json").read_text(encoding="utf-8"))
    assert_eyes_only_fixture(payload, label="demo/fixture.json")


def test_rejects_armed_posture():
    with pytest.raises(ValueError, match="dry compose"):
        assert_dry_posture({"mode": "armed", "detail": "ready to send"})


def test_rejects_send_suggestion_in_doctor():
    fixture = json.loads((REPO_ROOT / "demo" / "fixture.json").read_text(encoding="utf-8"))
    fixture["doctor"] = {"status": "warn", "summary": "click clear to resume"}
    with pytest.raises(ValueError, match="click clear"):
        assert_no_send_suggestions(fixture)


def test_rejects_bare_mint_button_label():
    fixture = json.loads((REPO_ROOT / "demo" / "fixture.json").read_text(encoding="utf-8"))
    fixture["doctor"] = {"status": "warn", "summary": "Mint"}
    with pytest.raises(ValueError, match="mint"):
        assert_no_send_suggestions(fixture)


def test_allows_negated_mint_suggestion():
    fixture = json.loads((REPO_ROOT / "demo" / "fixture.json").read_text(encoding="utf-8"))
    fixture["doctor"] = {"status": "warn", "summary": "no mint — eyes-only demo"}
    assert_no_send_suggestions(fixture)


def test_summarize_demo_fixture():
    payload = json.loads((REPO_ROOT / "demo" / "fixture.json").read_text(encoding="utf-8"))
    summary = summarize_status(payload)
    assert summary in (StatusSummary.OK, StatusSummary.DEGRADED)


def test_summarize_fault_on_blocking():
    fixture = {"doctor": {"status": "blocking"}, "feeds": []}
    assert summarize_status(fixture) == StatusSummary.FAULT


def test_extract_demo_fixture_from_app_js():
    app_js = (REPO_ROOT / "app.js").read_text(encoding="utf-8")
    embedded = extract_demo_fixture_from_app_js(app_js)
    assert embedded["synthetic"] is True
    assert embedded["posture"]["mode"] == "dry compose"


def test_page_sources_dry_integration():
    assert_page_sources_dry(
        fixture_path_text=(REPO_ROOT / "demo" / "fixture.json").read_text(encoding="utf-8"),
        app_js_text=(REPO_ROOT / "app.js").read_text(encoding="utf-8"),
        index_html_text=(REPO_ROOT / "index.html").read_text(encoding="utf-8"),
    )


def test_page_sources_fail_on_live_posture():
    fixture = json.loads((REPO_ROOT / "demo" / "fixture.json").read_text(encoding="utf-8"))
    fixture["posture"]["mode"] = "live armed"
    with pytest.raises(ValueError, match="dry compose"):
        assert_page_sources_dry(
            fixture_path_text=json.dumps(fixture),
            app_js_text=(REPO_ROOT / "app.js").read_text(encoding="utf-8"),
            index_html_text=(REPO_ROOT / "index.html").read_text(encoding="utf-8"),
        )
