"""Unit tests for glance_status — mirrors Rust glance-status test cases."""

import pytest

from glance_status import (
    ClassifyInput,
    DoctorStatus,
    assert_no_overclaim,
    classify,
    redact,
)


def test_doctor_status_values():
    assert DoctorStatus.OK.value == "ok"
    assert DoctorStatus.BLOCKING.value == "blocking"


def test_classify_blocking_overrides_everything():
    status = classify(
        ClassifyInput(
            blocking_flag=True,
            raw_message="Hygiene checks passed · stale feed",
        )
    )
    assert status == DoctorStatus.BLOCKING


def test_classify_hygiene_never_classifies_as_fault():
    status = classify(
        ClassifyInput(
            blocking_flag=False,
            raw_message="Hygiene checks passed · stale ignored for now",
            hygiene_phrases=["hygiene", "heartbeat ok", "passed"],
            fault_phrases=["stale", "timeout", "degraded"],
        )
    )
    assert status == DoctorStatus.OK


def test_classify_warn_from_fault_allowlist():
    status = classify(
        ClassifyInput(
            blocking_flag=False,
            raw_message="Feed stale for 47s",
            hygiene_phrases=["hygiene", "heartbeat ok", "passed"],
            fault_phrases=["stale", "timeout", "degraded"],
        )
    )
    assert status == DoctorStatus.WARN


def test_classify_unknown_on_empty_message():
    status = classify(
        ClassifyInput(
            blocking_flag=False,
            raw_message="   ",
            hygiene_phrases=[],
            fault_phrases=[],
        )
    )
    assert status == DoctorStatus.UNKNOWN


def test_classify_unknown_when_no_phrase_matches():
    status = classify(
        ClassifyInput(
            blocking_flag=False,
            raw_message="All nominal",
            hygiene_phrases=["hygiene", "heartbeat ok", "passed"],
            fault_phrases=["stale", "timeout", "degraded"],
        )
    )
    assert status == DoctorStatus.UNKNOWN


def test_redact_url_query():
    out = redact("see https://example.com/x?token=secret for detail")
    assert "token=secret" not in out
    assert "[REDACTED_URL]" in out


def test_redact_hex():
    raw = "key=deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    assert "[REDACTED_HEX]" in redact(raw)


def test_redact_base58():
    raw = "owner 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU signed"
    assert "[REDACTED_KEY]" in redact(raw)


def test_redact_api_key_prefix():
    raw = "auth sk-live-abcdefghijklmnopqrstuvwxyz failed"
    out = redact(raw)
    assert "[REDACTED_SECRET]" in out
    assert "sk-live" not in out


def test_redact_bearer_token():
    raw = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.sig"
    out = redact(raw)
    assert "[REDACTED_SECRET]" in out
    assert "eyJhbGci" not in out


def test_redact_leaves_benign_text():
    raw = "Process heartbeat OK (demo fixture)"
    assert redact(raw) == raw


def test_assert_no_overclaim_passes():
    assert_no_overclaim("No active faults", ["profit", "guaranteed"])


def test_assert_no_overclaim_catches_banned_phrase():
    with pytest.raises(ValueError, match="guaranteed"):
        assert_no_overclaim("Guaranteed stable", ["guaranteed"])


def test_assert_no_overclaim_case_insensitive():
    with pytest.raises(ValueError, match="alpha"):
        assert_no_overclaim("ALPHA leak detected", ["alpha"])
