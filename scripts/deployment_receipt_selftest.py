#!/usr/bin/env python3
"""Self-test for deployment_receipt.py — local server only, no outside network."""

from __future__ import annotations

import hashlib
import io
import json
import sys
import tempfile
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Iterator

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import deployment_receipt  # noqa: E402


class _HitCounter:
    def __init__(self) -> None:
        self.redirect_target_hits = 0


def _make_handler(
    routes: dict[str, tuple[int, bytes, dict[str, str] | None]],
    counter: _HitCounter | None = None,
):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            del format, args

        def do_GET(self) -> None:  # noqa: N802
            if counter is not None and self.path == "/redirect-target":
                counter.redirect_target_hits += 1
                body = b"never-should-be-used"
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            route = routes.get(self.path)
            if route is None:
                self.send_response(404)
                self.end_headers()
                return

            status, body, extra_headers = route
            if status in (301, 302, 303, 307, 308):
                location = (extra_headers or {}).get("Location", "")
                self.send_response(status)
                self.send_header("Location", location)
                self.end_headers()
                return

            self.send_response(status)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(body)))
            if extra_headers:
                for key, value in extra_headers.items():
                    self.send_header(key, value)
            self.end_headers()
            if status >= 200 and status <= 299:
                self.wfile.write(body)

    return Handler


@contextmanager
def local_server(
    routes: dict[str, tuple[int, bytes, dict[str, str] | None]],
    *,
    counter: _HitCounter | None = None,
) -> Iterator[str]:
    server = HTTPServer(("127.0.0.1", 0), _make_handler(routes, counter))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    base = f"http://127.0.0.1:{port}"
    try:
        yield base
    finally:
        server.shutdown()
        thread.join(timeout=5)


def _write_manifest(payload: dict) -> Path:
    handle = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(payload, handle)
    handle.flush()
    handle.close()
    return Path(handle.name)


def _run_main(
    manifest_path: Path,
    *,
    policy: deployment_receipt.AddressPolicy | None = None,
) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = stdout, stderr
    try:
        code = deployment_receipt.main(
            [str(manifest_path)],
            address_policy=policy,
        )
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr
    return code, stdout.getvalue(), stderr.getvalue()


def _parse_records(output: str) -> list[dict]:
    lines = [line for line in output.splitlines() if line.strip()]
    return [json.loads(line) for line in lines]


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_all_four_results() -> None:
    current_body = b"current-bytes"
    stale_body = b"stale-bytes"
    changed_body = b"changed-bytes"
    routes = {
        "/current": (200, current_body, {"ETag": '"cur"', "Last-Modified": "Mon, 01 Jan 2024 00:00:00 GMT"}),
        "/stale": (200, stale_body, None),
        "/changed": (200, changed_body, None),
        "/missing": (404, b"not found", None),
    }
    with local_server(routes) as base:
        manifest = _write_manifest(
            {
                "assets": [
                    {
                        "url": f"{base}/current",
                        "expected_sha256": hashlib.sha256(current_body).hexdigest(),
                    },
                    {
                        "url": f"{base}/stale",
                        "expected_sha256": hashlib.sha256(current_body).hexdigest(),
                        "stale_sha256": hashlib.sha256(stale_body).hexdigest(),
                    },
                    {
                        "url": f"{base}/changed",
                        "expected_sha256": hashlib.sha256(current_body).hexdigest(),
                    },
                    {
                        "url": f"{base}/missing",
                        "expected_sha256": hashlib.sha256(current_body).hexdigest(),
                    },
                ]
            }
        )
        try:
            code, output, _stderr = _run_main(
                manifest,
                policy=deployment_receipt.PermissiveAddressPolicy(),
            )
            records = _parse_records(output)
            results = {record["result"] for record in records}
            _assert(results == {"CURRENT", "STALE", "CHANGED", "NO_READ"}, f"results set: {results}")
            by_result = {record["result"]: record for record in records}
            _assert(by_result["CURRENT"]["sha256"] == by_result["CURRENT"]["expected_sha256"], "CURRENT hash")
            _assert(by_result["STALE"]["sha256"] != by_result["STALE"]["expected_sha256"], "STALE differs")
            _assert(by_result["CHANGED"]["sha256"] not in {
                by_result["CHANGED"]["expected_sha256"],
            }, "CHANGED differs")
            _assert(by_result["NO_READ"]["sha256"] is None, "NO_READ has no sha256")
            _assert(by_result["NO_READ"]["bytes"] is None, "NO_READ has no bytes")
            _assert(code == 1, f"expected exit 1 for mixed STALE/CHANGED, got {code}")
        finally:
            manifest.unlink(missing_ok=True)


def test_exit_all_current() -> None:
    body = b"all-good"
    digest = hashlib.sha256(body).hexdigest()
    with local_server({"/ok": (200, body, None)}) as base:
        manifest = _write_manifest(
            {"assets": [{"url": f"{base}/ok", "expected_sha256": digest}]}
        )
        try:
            code, output, _stderr = _run_main(
                manifest,
                policy=deployment_receipt.PermissiveAddressPolicy(),
            )
            records = _parse_records(output)
            _assert(code == 0, f"expected exit 0, got {code}")
            _assert(all(record["result"] == "CURRENT" for record in records), "all CURRENT")
        finally:
            manifest.unlink(missing_ok=True)


def test_exit_current_and_no_read() -> None:
    body = b"readable"
    digest = hashlib.sha256(body).hexdigest()
    routes = {
        "/ok": (200, body, None),
        "/gone": (503, b"unavailable", None),
    }
    with local_server(routes) as base:
        manifest = _write_manifest(
            {
                "assets": [
                    {"url": f"{base}/ok", "expected_sha256": digest},
                    {"url": f"{base}/gone", "expected_sha256": digest},
                ]
            }
        )
        try:
            code, output, _stderr = _run_main(
                manifest,
                policy=deployment_receipt.PermissiveAddressPolicy(),
            )
            records = _parse_records(output)
            results = {record["result"] for record in records}
            _assert(code == 3, f"expected exit 3, got {code}")
            _assert(results == {"CURRENT", "NO_READ"}, f"unexpected results: {results}")
        finally:
            manifest.unlink(missing_ok=True)


def test_exit_changed() -> None:
    body = b"live-bytes"
    with local_server({"/asset": (200, body, None)}) as base:
        manifest = _write_manifest(
            {
                "assets": [
                    {
                        "url": f"{base}/asset",
                        "expected_sha256": hashlib.sha256(b"expected-bytes").hexdigest(),
                    }
                ]
            }
        )
        try:
            code, output, _stderr = _run_main(
                manifest,
                policy=deployment_receipt.PermissiveAddressPolicy(),
            )
            records = _parse_records(output)
            _assert(code == 1, f"expected exit 1, got {code}")
            _assert(records[0]["result"] == "CHANGED", "expected CHANGED")
        finally:
            manifest.unlink(missing_ok=True)


def test_exit_invalid_manifest() -> None:
    manifest = _write_manifest({"not_assets": []})
    try:
        code, output, _stderr = _run_main(
            manifest,
            policy=deployment_receipt.PermissiveAddressPolicy(),
        )
        _assert(code == 2, f"expected exit 2, got {code}")
        _assert(output == "", f"expected empty stdout, got {output!r}")
    finally:
        manifest.unlink(missing_ok=True)


def test_redirect_to_local_target_not_fetched() -> None:
    counter = _HitCounter()
    routes = {
        "/redirect": (
            302,
            b"",
            {"Location": "/redirect-target"},
        ),
        "/redirect-target": (200, b"target-body", None),
    }
    with local_server(routes, counter=counter) as base:
        manifest = _write_manifest(
            {
                "assets": [
                    {
                        "url": f"{base}/redirect",
                        "expected_sha256": hashlib.sha256(b"target-body").hexdigest(),
                    }
                ]
            }
        )
        try:
            code, output, _stderr = _run_main(
                manifest,
                policy=deployment_receipt.PermissiveAddressPolicy(),
            )
            records = _parse_records(output)
            _assert(code == 3, f"expected exit 3, got {code}")
            _assert(records[0]["result"] == "NO_READ", "redirect must be NO_READ")
            _assert(records[0]["status"] == 302, "redirect status preserved")
            _assert(records[0]["url"] == f"{base}/redirect", "declared URL preserved")
            _assert(counter.redirect_target_hits == 0, "redirect target must not be fetched")
        finally:
            manifest.unlink(missing_ok=True)


def test_redirect_to_ftp_is_no_read() -> None:
    routes = {
        "/to-ftp": (
            302,
            b"",
            {"Location": "ftp://example.com/file"},
        ),
    }
    with local_server(routes) as base:
        manifest = _write_manifest(
            {
                "assets": [
                    {
                        "url": f"{base}/to-ftp",
                        "expected_sha256": "0" * 64,
                    }
                ]
            }
        )
        try:
            code, output, _stderr = _run_main(
                manifest,
                policy=deployment_receipt.PermissiveAddressPolicy(),
            )
            records = _parse_records(output)
            _assert(code == 3, f"expected exit 3, got {code}")
            _assert(records[0]["result"] == "NO_READ", "ftp redirect must be NO_READ")
            _assert(records[0]["sha256"] is None, "no body hash on ftp redirect")
        finally:
            manifest.unlink(missing_ok=True)


def test_strict_policy_rejects_before_fetch() -> None:
    rejected_urls = [
        "file:///etc/passwd",
        "http://example.com/asset",
        "https://127.0.0.1/asset",
        "https://169.254.169.254/latest/meta-data/",
        "https://[::1]/asset",
        "https://user:pw@example.com/asset",
        "ftp://example.com/asset",
        "http://localhost/asset",
    ]
    for url in rejected_urls:
        manifest = _write_manifest(
            {"assets": [{"url": url, "expected_sha256": "0" * 64}]}
        )
        try:
            code, output, _stderr = _run_main(
                manifest,
                policy=deployment_receipt.StrictPublicAddressPolicy(),
            )
            _assert(code == 2, f"{url}: expected exit 2, got {code}")
            _assert(output == "", f"{url}: expected empty stdout, got {output!r}")
        finally:
            manifest.unlink(missing_ok=True)


def main() -> int:
    tests = [
        test_all_four_results,
        test_exit_all_current,
        test_exit_current_and_no_read,
        test_exit_changed,
        test_exit_invalid_manifest,
        test_redirect_to_local_target_not_fetched,
        test_redirect_to_ftp_is_no_read,
        test_strict_policy_rejects_before_fetch,
    ]
    for test in tests:
        test()
    print("deployment_receipt_selftest passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
