import pytest

from glance_status import (
    ClassifyInput,
    DoctorStatus,
    OverclaimError,
    assert_no_overclaim,
    classify_fault,
    redact,
)


def test_doctor_status_values():
    assert DoctorStatus.OK.value == "ok"
    assert DoctorStatus.BLOCKING.value == "blocking"


def test_classify_blocking_first():
    result = classify_fault(
        ClassifyInput(blocking=True, lines=["rpc timeout"]),
        hygiene_patterns=["info:"],
        fault_phrases=["rpc timeout"],
    )
    assert result is DoctorStatus.BLOCKING


def test_classify_hygiene_exclusion():
    result = classify_fault(
        ClassifyInput(blocking=False, lines=["info: heartbeat ok"]),
        hygiene_patterns=["info:"],
        fault_phrases=["rpc down"],
    )
    assert result is DoctorStatus.OK


def test_classify_fault_allowlist():
    result = classify_fault(
        ClassifyInput(blocking=False, lines=["slot lag detected"]),
        hygiene_patterns=["info:"],
        fault_phrases=["slot lag"],
    )
    assert result is DoctorStatus.EYES_FAULT


def test_redact_url_with_query():
    out = redact("see https://api.example.com/v1?token=abc123")
    assert "token=abc123" not in out
    assert "[REDACTED]" in out


def test_redact_hex_key():
    secret = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    out = redact(f"key={secret}")
    assert secret not in out


def test_assert_no_overclaim_passes():
    assert_no_overclaim("observe-only", ["profit"])


def test_assert_no_overclaim_fails():
    with pytest.raises(OverclaimError) as exc:
        assert_no_overclaim("guaranteed profit", ["profit", "guaranteed"])
    assert "profit" in exc.value.matches
