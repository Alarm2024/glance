import pytest

from glance_status import (
    DoctorStatus,
    OverclaimError,
    assert_no_overclaim,
    classify_fault,
    redact,
)

HYGIENE = ["heartbeat ok", "config exclusions applied"]
FAULTS = ["stale feed", "rpc timeout", "eyes desync"]
BANNED = ["guaranteed profit", "risk-free", "live-send armed", "alpha included"]


def test_doctor_status_wire_values():
    assert DoctorStatus.OK.as_str() == "ok"
    assert DoctorStatus.EYES_FAULT.as_str() == "eyes_fault"


def test_classify_blocking():
    assert (
        classify_fault(
            blocking_flag=True,
            lines=["stale feed"],
            hygiene_phrases=HYGIENE,
            fault_phrases=FAULTS,
        )
        == DoctorStatus.BLOCKING
    )


def test_classify_hygiene_excluded():
    assert (
        classify_fault(
            blocking_flag=False,
            lines=["heartbeat ok · all feeds nominal"],
            hygiene_phrases=HYGIENE,
            fault_phrases=FAULTS,
        )
        == DoctorStatus.OK
    )


def test_classify_warn():
    assert (
        classify_fault(
            blocking_flag=False,
            lines=["price-oracle stale feed detected"],
            hygiene_phrases=HYGIENE,
            fault_phrases=FAULTS,
        )
        == DoctorStatus.WARN
    )


def test_classify_eyes_fault():
    assert (
        classify_fault(
            blocking_flag=False,
            lines=["monitor eyes desync on slot boundary"],
            hygiene_phrases=HYGIENE,
            fault_phrases=FAULTS,
        )
        == DoctorStatus.EYES_FAULT
    )


def test_redact_url_query():
    cleaned = redact("see https://api.example.com/v1/status?token=abc123")
    assert "token=abc123" not in cleaned
    assert "[REDACTED]" in cleaned


def test_redact_hex():
    raw = "sig deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    cleaned = redact(raw)
    assert "deadbeef" not in cleaned


def test_assert_no_overclaim_pass():
    assert_no_overclaim("No blocking flags, no active faults", BANNED)


def test_assert_no_overclaim_fail():
    with pytest.raises(OverclaimError) as exc:
        assert_no_overclaim("This bot delivers guaranteed profit daily", BANNED)
    assert exc.value.phrase == "guaranteed profit"
