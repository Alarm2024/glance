#!/usr/bin/env python3
"""CI posture self-test — fixture + page sources must stay dry / eyes-only."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from glance_status.posture import assert_page_sources_dry


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    fixture_path = repo_root / "demo" / "fixture.json"
    app_js_path = repo_root / "app.js"
    index_html_path = repo_root / "index.html"

    missing = [p for p in (fixture_path, app_js_path, index_html_path) if not p.is_file()]
    if missing:
        for path in missing:
            print(f"posture-selftest: missing required file: {path}", file=sys.stderr)
        return 1

    try:
        assert_page_sources_dry(
            fixture_path_text=fixture_path.read_text(encoding="utf-8"),
            app_js_text=app_js_path.read_text(encoding="utf-8"),
            index_html_text=index_html_path.read_text(encoding="utf-8"),
        )
    except ValueError as exc:
        print(f"posture-selftest FAILED: {exc}", file=sys.stderr)
        return 1

    from glance_status.posture import assert_eyes_only_fixture

    demo_dir = repo_root / "demo"
    extra_fixtures = sorted(demo_dir.glob("fixture*.json"))
    for path in extra_fixtures:
        if path.name == "fixture.json":
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        try:
            assert_eyes_only_fixture(payload, label=str(path.relative_to(repo_root)))
        except ValueError as exc:
            print(f"posture-selftest FAILED: {exc}", file=sys.stderr)
            return 1

    print("posture-selftest passed — dry compose / eyes-only across fixture + page sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
