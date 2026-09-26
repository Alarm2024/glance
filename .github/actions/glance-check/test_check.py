"""Exit codes for glance-check: missing path, clean file, banned phrase."""

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
    return tmp_path


def test_missing_path_exits_1(glance_check, workspace, monkeypatch, capsys):
    monkeypatch.setenv("GLANCE_CHECK_PATHS", "status.json")
    assert glance_check.main() == 1
    err = capsys.readouterr().err
    assert "status.json" in err
    assert "does not exist" in err


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
