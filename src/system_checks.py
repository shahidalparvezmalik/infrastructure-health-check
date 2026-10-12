"""Read-only system health checks using the Python standard library."""

from __future__ import annotations

import os
import platform
import shutil
import time
from typing import Any


def _finding(
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


def classify_threshold(
    value: float,
    *,
    medium: float,
    high: float,
    critical: float,
) -> str:
    if value >= critical:
        return "Critical"
    if value >= high:
        return "High"
    if value >= medium:
        return "Medium"
    return "Healthy"


def check_cpu_sample(value: float) -> dict[str, Any]:
    severity = classify_threshold(value, medium=80, high=90, critical=98)
    status = "Healthy" if severity == "Healthy" else "Attention"
    recommendation = (
        "No action required."
        if status == "Healthy"
        else "Investigate sustained CPU utilization and identify the top consumers."
    )
    return _finding(
        "CPU utilization",
        status,
        severity,
        {"percent": round(value, 1)},
        recommendation,
    )


def check_memory_sample(value: float) -> dict[str, Any]:
    severity = classify_threshold(value, medium=80, high=90, critical=95)
    status = "Healthy" if severity == "Healthy" else "Attention"
    recommendation = (
        "No action required."
        if status == "Healthy"
        else "Review memory pressure and identify processes contributing to sustained utilization."
    )
    return _finding(
        "Memory utilization",
        status,
        severity,
        {"percent": round(value, 1)},
        recommendation,
    )


def check_disk_free(free_percent: float) -> dict[str, Any]:
    if free_percent <= 5:
        severity = "Critical"
    elif free_percent <= 10:
        severity = "High"
    elif free_percent <= 20:
        severity = "Medium"
    else:
        severity = "Healthy"

    status = "Healthy" if severity == "Healthy" else "Attention"
    recommendation = (
        "No action required."
        if status == "Healthy"
        else "Review storage growth, temporary files and application logs; plan capacity action."
    )
    return _finding(
        "Disk free capacity",
        status,
        severity,
        {"free_percent": round(free_percent, 1)},
        recommendation,
    )


def get_host_information() -> dict[str, Any]:
    return {
        "hostname": platform.node() or "unknown",
        "platform": platform.platform(),
        "processor": platform.processor() or "unknown",
        "python_version": platform.python_version(),
    }


def get_disk_free_percent(path: str = os.path.abspath(os.sep)) -> float:
    usage = shutil.disk_usage(path)
    return (usage.free / usage.total) * 100 if usage.total else 0.0


def measure_uptime_seconds(boot_timestamp: float | None = None) -> float:
    """Return elapsed seconds since a supplied boot timestamp.

    This helper avoids privileged OS calls and is easy to replace with
    platform-specific uptime collection in a later version.
    """
    if boot_timestamp is None:
        return 0.0
    return max(0.0, time.time() - boot_timestamp)
