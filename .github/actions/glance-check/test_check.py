"""Exit codes for glance-check: missing file (2), clean file (0), banned phrase (1), zero files (1)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_CHECK_PY = Path(__file__).resolve().with_name("check.py")


@pytest.fixture
def glance_check():
    spec = importlib.util.spec_from_file_location("glance_check_under_test", _CHECK_PY)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))
    monkeypatch.delenv("GLANCE_CHECK_BANNED", raising=False)
    monkeypatch.delenv("GLANCE_CHECK_PATHS", raising=False)
    return tmp_path


def test_missing_explicit_path_exits_2(glance_check, workspace, monkeypatch, capsys):
    # #28: a missing listed file is its own failure, not a banned phrase.
    monkeypatch.setenv("GLANCE_CHECK_PATHS", "status.json")
    assert glance_check.main() == glance_check.EXIT_MISSING_FILE == 2
    err = capsys.readouterr().err
    assert "missing file: status.json" in err
    assert "does not exist" in err
    assert "banned" not in err


def test_mixed_existing_and_missing_paths_exits_2(glance_check, workspace, monkeypatch, capsys):
    # One listed file exists (and even holds a banned phrase); one does not.
    # The missing file decides the outcome, names only the missing entry, and
    # nothing is scanned, so no banned-phrase finding is reported.
    (workspace / "status.json").write_text('{"doctor": "alpha signal"}\n', encoding="utf-8")
    monkeypatch.setenv("GLANCE_CHECK_PATHS", "status.json\nreports/missing.json\n")
    assert glance_check.main() == 2
    err = capsys.readouterr().err
    assert "1 of 2 path(s)" in err
    assert "missing file: reports/missing.json" in err
    assert "missing file: status.json" not in err
    assert "banned" not in err


def test_banned_phrase_and_missing_file_use_different_exit_codes(glance_check):
    assert glance_check.EXIT_FINDINGS == 1
    assert glance_check.EXIT_MISSING_FILE == 2


def test_clean_file_exits_0(glance_check, workspace, monkeypatch, capsys):
    (workspace / "status.json").write_text(
        '{"doctor": "feed stale for 47s"}\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("GLANCE_CHECK_PATHS", "status.json")
    assert glance_check.main() == 0
    assert "passed" in capsys.readouterr().out


def test_banned_phrase_exits_1(glance_check, workspace, monkeypatch, capsys):
    (workspace / "status.json").write_text(
        '{"doctor": "guaranteed profit"}\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("GLANCE_CHECK_PATHS", "status.json")
    assert glance_check.main() == 1
    assert "guaranteed" in capsys.readouterr().err


def test_empty_workspace_no_paths_exits_1(glance_check, workspace, capsys):
    # G1: no `paths` input and no default candidates -> fail closed.
    assert glance_check.main() == 1
    err = capsys.readouterr().err
    assert "no files to scan" in err
    assert "`paths`" in err


def test_no_paths_with_demo_fixture_exits_0(glance_check, workspace, capsys):
    # The demo/fixture.json default still works when `paths` is empty.
    (workspace / "demo").mkdir()
    (workspace / "demo" / "fixture.json").write_text(
        '{"doctor": "feed stale for 47s"}\n',
        encoding="utf-8",
    )
    assert glance_check.main() == 0
    assert "passed" in capsys.readouterr().out


def test_blank_paths_input_keeps_auto_discovery(glance_check, workspace, monkeypatch, capsys):
    # Whitespace-only `paths` is "not set": the defaults are discovered, and
    # absent defaults are skipped rather than reported as missing files.
    (workspace / "status.json").write_text('{"doctor": "feed stale for 47s"}\n', encoding="utf-8")
    monkeypatch.setenv("GLANCE_CHECK_PATHS", "  \n  ")
    assert glance_check.main() == 0
    captured = capsys.readouterr()
    assert "passed" in captured.out
    assert "missing file" not in captured.err
