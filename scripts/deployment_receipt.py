#!/usr/bin/env python3
"""Read-only deployment receipt — fetch declared public assets and fingerprint bytes.

For each asset in a manifest, this tool fetches the declared URL (never a
redirect target), hashes the response body when a 2xx body is read, and prints
one JSON record per asset. It never writes to the repo or the target.

The hostname is resolved during validation and again when connecting. A hostile
resolver can answer with a public address and then a private one. This is not
closed. Closing it requires pinning the resolved address and connecting to it
directly.
"""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol
from urllib import error, parse, request

_CGNAT = ipaddress.ip_network("100.64.0.0/10")


class AddressPolicy(Protocol):
    def validate_url(self, url: str) -> str | None:
        """Return an error string when the URL must be rejected, else None."""


class StrictPublicAddressPolicy:
    """Reject non-public HTTPS targets before any fetch."""

    def validate_url(self, url: str) -> str | None:
        parsed = parse.urlparse(url)
        if parsed.scheme != "https":
            return f"scheme must be https, got {parsed.scheme!r}"
        if parsed.username is not None or parsed.password is not None:
            return "userinfo is not allowed"
        hostname = parsed.hostname
        if not hostname:
            return "hostname is required"
        if hostname == "localhost" or hostname.endswith(".localhost"):
            return f"localhost hostnames are not allowed: {hostname!r}"
        try:
            infos = socket.getaddrinfo(
                hostname,
                parsed.port or 443,
                type=socket.SOCK_STREAM,
            )
        except socket.gaierror as exc:
            return f"DNS resolution failed: {exc}"

        if not infos:
            return "DNS resolution returned no addresses"

        seen: set[str] = set()
        for _family, _type, _proto, _canonname, sockaddr in infos:
            ip_str = sockaddr[0]
            if ip_str in seen:
                continue
            seen.add(ip_str)
            try:
                ip = ipaddress.ip_address(ip_str)
            except ValueError:
                return f"invalid resolved address: {ip_str!r}"
            reason = _reject_address(ip)
            if reason is not None:
                return f"{hostname} resolves to disallowed address {ip_str}: {reason}"
        return None


class PermissiveAddressPolicy:
    """Allow any URL — for self-tests only; not exposed via CLI or env."""

    def validate_url(self, url: str) -> str | None:
        return None


def _reject_address(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> str | None:
    if ip.is_loopback:
        return "loopback"
    if ip.is_link_local:
        return "link-local"
    if ip.is_private:
        return "private"
    if ip.version == 4 and ip in _CGNAT:
        return "CGNAT 100.64/10"
    if ip.is_reserved:
        return "reserved"
    if ip.is_unspecified:
        return "unspecified"
    if ip.is_multicast:
        return "multicast"
    return None


class NoRedirectHandler(request.HTTPRedirectHandler):
    """Refuse redirects so the receipt records what the declared URL served."""

    def redirect_request(  # noqa: N802 — urllib API name
        self,
        req: request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> request.Request | None:
        return None


def _fetched_at_minute() -> str:
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    return now.strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize_sha256(value: str) -> str:
    cleaned = value.strip().lower()
    if len(cleaned) != 64 or any(ch not in "0123456789abcdef" for ch in cleaned):
        raise ValueError(f"expected_sha256 must be 64 hex digits, got {value!r}")
    return cleaned


def load_manifest(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"manifest invalid: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError("manifest invalid: root must be a JSON object")

    assets = payload.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError("manifest invalid: assets must be a non-empty array")

    normalized: list[dict[str, Any]] = []
    for index, asset in enumerate(assets):
        label = f"assets[{index}]"
        if not isinstance(asset, dict):
            raise ValueError(f"manifest invalid: {label} must be an object")
        url = asset.get("url")
        if not isinstance(url, str) or not url.strip():
            raise ValueError(f"manifest invalid: {label}.url must be a non-empty string")
        expected = asset.get("expected_sha256")
        if not isinstance(expected, str):
            raise ValueError(
                f"manifest invalid: {label}.expected_sha256 must be a string"
            )
        try:
            expected_sha256 = _normalize_sha256(expected)
        except ValueError as exc:
            raise ValueError(f"manifest invalid: {label}: {exc}") from exc

        stale_sha256: str | None = None
        if "stale_sha256" in asset:
            stale_value = asset.get("stale_sha256")
            if not isinstance(stale_value, str):
                raise ValueError(
                    f"manifest invalid: {label}.stale_sha256 must be a string"
                )
            try:
                stale_sha256 = _normalize_sha256(stale_value)
            except ValueError as exc:
                raise ValueError(f"manifest invalid: {label}: {exc}") from exc

        normalized.append(
            {
                "url": url,
                "expected_sha256": expected_sha256,
                "stale_sha256": stale_sha256,
            }
        )
    return normalized


def _make_record(
    *,
    url: str,
    status: int | None,
    etag: str | None,
    last_modified: str | None,
    body: bytes | None,
    expected_sha256: str,
    result: str,
    error: str | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "url": url,
        "fetched_at_minute": _fetched_at_minute(),
        "status": status,
        "etag": etag,
        "last_modified": last_modified,
        "bytes": len(body) if body is not None else None,
        "sha256": hashlib.sha256(body).hexdigest() if body is not None else None,
        "expected_sha256": expected_sha256,
        "result": result,
    }
    if error is not None:
        record["error"] = error
    return record


def inspect_asset(
    asset: dict[str, Any],
    *,
    opener: request.OpenerDirector,
) -> dict[str, Any]:
    url = asset["url"]
    expected_sha256 = asset["expected_sha256"]
    stale_sha256 = asset.get("stale_sha256")

    req = request.Request(url, method="GET")
    try:
        with opener.open(req, timeout=30) as response:
            status = response.status
            headers = response.headers
            etag = headers.get("ETag")
            last_modified = headers.get("Last-Modified")
            if 200 <= status <= 299:
                body = response.read()
                digest = hashlib.sha256(body).hexdigest()
                if digest == expected_sha256:
                    result = "CURRENT"
                elif stale_sha256 is not None and digest == stale_sha256:
                    result = "STALE"
                else:
                    result = "CHANGED"
                return _make_record(
                    url=url,
                    status=status,
                    etag=etag,
                    last_modified=last_modified,
                    body=body,
                    expected_sha256=expected_sha256,
                    result=result,
                )
            return _make_record(
                url=url,
                status=status,
                etag=etag,
                last_modified=last_modified,
                body=None,
                expected_sha256=expected_sha256,
                result="NO_READ",
            )
    except error.HTTPError as exc:
        return _make_record(
            url=url,
            status=exc.code,
            etag=exc.headers.get("ETag") if exc.headers else None,
            last_modified=exc.headers.get("Last-Modified") if exc.headers else None,
            body=None,
            expected_sha256=expected_sha256,
            result="NO_READ",
            error=str(exc.reason) if exc.reason else None,
        )
    except error.URLError as exc:
        reason = exc.reason
        message = str(reason) if reason is not None else str(exc)
        return _make_record(
            url=url,
            status=None,
            etag=None,
            last_modified=None,
            body=None,
            expected_sha256=expected_sha256,
            result="NO_READ",
            error=message,
        )


def exit_code_for_results(results: list[dict[str, Any]]) -> int:
    values = {record["result"] for record in results}
    if values <= {"CURRENT"}:
        return 0
    if "CHANGED" in values or "STALE" in values:
        return 1
    if values <= {"CURRENT", "NO_READ"}:
        return 3
    return 1


def run_receipt(
    manifest_path: Path,
    *,
    address_policy: AddressPolicy,
) -> tuple[list[dict[str, Any]], int]:
    try:
        assets = load_manifest(manifest_path)
    except ValueError:
        return [], 2

    for asset in assets:
        policy_error = address_policy.validate_url(asset["url"])
        if policy_error is not None:
            return [], 2

    redirect_handler = NoRedirectHandler()
    opener = request.build_opener(redirect_handler)

    records = [inspect_asset(asset, opener=opener) for asset in assets]
    return records, exit_code_for_results(records)


def main(
    argv: list[str] | None = None,
    *,
    address_policy: AddressPolicy | None = None,
) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch declared public assets and print one JSON receipt line per asset."
    )
    parser.add_argument(
        "manifest",
        type=Path,
        help="Path to a JSON manifest with an assets array",
    )
    args = parser.parse_args(argv)

    policy = address_policy if address_policy is not None else StrictPublicAddressPolicy()
    records, exit_code = run_receipt(args.manifest, address_policy=policy)

    if exit_code == 2 and not records:
        return 2

    for record in records:
        print(json.dumps(record, sort_keys=True, separators=(",", ":")))

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
