"""Unit tests for glance_status Python mirror."""

import pytest

from glance_status import (
    DoctorStatus,
    OverclaimError,
    assert_no_overclaim,
    classify_fault,
    redact,
)


def test_doctor_status_values():
    assert DoctorStatus.OK.value == "ok"
    assert DoctorStatus.BLOCKING.value == "blocking"


def test_classify_blocking_wins():
    assert (
        classify_fault(blocking=True, message="anything")
        == DoctorStatus.BLOCKING
    )


def test_classify_hygiene_exclusion():
    status = classify_fault(
        blocking=False,
        message="Hygiene checks passed",
        hygiene_phrases=["hygiene"],
        fault_phrases=["stale"],
    )
    assert status == DoctorStatus.OK


def test_classify_eyes_fault():
    status = classify_fault(
        blocking=False,
        message="Observer fault on stream",
        eyes_fault_phrases=["observer fault"],
    )
    assert status == DoctorStatus.EYES_FAULT


def test_classify_warn():
    status = classify_fault(
        blocking=False,
        message="Feed stale for 47s",
        fault_phrases=["stale"],
    )
    assert status == DoctorStatus.WARN


def test_redact_url_query():
    out = redact("see https://example.com/x?token=secret for detail")
    assert "token=secret" not in out
    assert "[REDACTED_URL]" in out


def test_redact_hex():
    raw = "key=deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    assert "[REDACTED_HEX]" in redact(raw)


def test_assert_no_overclaim_passes():
    assert_no_overclaim("No active faults", ["profit", "guaranteed"])


def test_assert_no_overclaim_fails():
    with pytest.raises(OverclaimError) as exc:
        assert_no_overclaim("Guaranteed stable", ["guaranteed"])
    assert exc.value.phrase == "guaranteed"
