"""Read-only network connectivity checks."""

from __future__ import annotations

import socket
import time
from typing import Any


def _result(
    check: str,
    status: str,
    severity: str,
    observed: Any,
    recommendation: str,
) -> dict[str, Any]:
    return {
        "check": check,
        "status": status,
        "severity": severity,
        "observed": observed,
        "recommendation": recommendation,
    }


def check_tcp_connectivity(
    host: str,
    port: int,
    timeout_seconds: float = 3.0,
) -> dict[str, Any]:
    started = time.perf_counter()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout_seconds)
    try:
        code = sock.connect_ex((host, port))
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
    except OSError as exc:
        return _result(
            f"TCP connectivity {host}:{port}",
            "Attention",
            "High",
            {"reachable": False, "error": str(exc)},
            "Verify routing, firewall policy, service availability and endpoint configuration.",
        )
    finally:
        sock.close()

    if code == 0:
        return _result(
            f"TCP connectivity {host}:{port}",
            "Healthy",
            "Healthy",
            {"reachable": True, "latency_ms": latency_ms},
            "No action required.",
        )

    return _result(
        f"TCP connectivity {host}:{port}",
        "Attention",
        "High",
        {"reachable": False, "socket_error": code, "latency_ms": latency_ms},
        "Verify routing, firewall policy, service availability and endpoint configuration.",
    )


def check_host_name(host: str) -> dict[str, Any]:
    try:
        address = socket.gethostbyname(host)
    except OSError as exc:
        return _result(
            f"Host reachability lookup: {host}",
            "Attention",
            "High",
            {"resolved": False, "error": str(exc)},
            "Check DNS, routing and endpoint availability.",
        )

    return _result(
        f"Host reachability lookup: {host}",
        "Healthy",
        "Healthy",
        {"resolved": True, "address": address},
        "No action required.",
    )
