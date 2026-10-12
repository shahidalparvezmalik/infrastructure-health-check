"""DNS resolution diagnostics."""

from __future__ import annotations

import socket
import time
from typing import Any


def check_dns_resolution(hostname: str) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        canonical_name, aliases, addresses = socket.gethostbyname_ex(hostname)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "check": f"DNS resolution: {hostname}",
            "status": "Healthy",
            "severity": "Healthy",
            "observed": {
                "canonical_name": canonical_name,
                "aliases": aliases,
                "addresses": addresses,
                "response_ms": elapsed_ms,
            },
            "recommendation": "No action required.",
        }
    except OSError as exc:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "check": f"DNS resolution: {hostname}",
            "status": "Attention",
            "severity": "High",
            "observed": {"resolved": False, "response_ms": elapsed_ms, "error": str(exc)},
            "recommendation": "Check DNS server availability, records, search domains and network connectivity.",
        }
