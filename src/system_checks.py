"""Read-only system health checks using the Python standard library."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
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


def check_cpu(
    value: float,
    thresholds: dict[str, float] | None = None,
) -> dict[str, Any]:
    limits = thresholds or {"medium": 80, "high": 90, "critical": 98}
    severity = classify_threshold(
        value,
        medium=limits["medium"],
        high=limits["high"],
        critical=limits["critical"],
    )
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


def check_memory(
    value: float,
    thresholds: dict[str, float] | None = None,
) -> dict[str, Any]:
    limits = thresholds or {"medium": 80, "high": 90, "critical": 95}
    severity = classify_threshold(
        value,
        medium=limits["medium"],
        high=limits["high"],
        critical=limits["critical"],
    )
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


def check_disk_free(
    free_percent: float,
    thresholds: dict[str, float] | None = None,
) -> dict[str, Any]:
    limits = thresholds or {"medium": 20, "high": 10, "critical": 5}
    if free_percent <= limits["critical"]:
        severity = "Critical"
    elif free_percent <= limits["high"]:
        severity = "High"
    elif free_percent <= limits["medium"]:
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


# Backward-compatible aliases used by the deterministic sample runner.
check_cpu_sample = check_cpu
check_memory_sample = check_memory


def _run_powershell(expression: str, timeout_seconds: float = 5.0) -> str | None:
    """Execute a read-only PowerShell expression on Windows."""
    if platform.system().lower() != "windows":
        return None
    try:
        completed = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", expression],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    value = completed.stdout.strip()
    return value or None


def get_cpu_percent() -> float | None:
    """Return current CPU utilization where the platform exposes it safely."""
    windows_value = _run_powershell(
        "[math]::Round((Get-CimInstance Win32_Processor | "
        "Measure-Object -Property LoadPercentage -Average).Average, 1)"
    )
    if windows_value is not None:
        try:
            return max(0.0, min(100.0, float(windows_value)))
        except ValueError:
            pass

    if hasattr(os, "getloadavg"):
        try:
            load_1m = os.getloadavg()[0]
            cpu_count = max(1, os.cpu_count() or 1)
            return max(0.0, min(100.0, (load_1m / cpu_count) * 100))
        except (OSError, IndexError, TypeError, ZeroDivisionError):
            pass

    return None


def get_memory_percent() -> float | None:
    """Return memory utilization using Windows CIM or Linux /proc data."""
    windows_value = _run_powershell(
        "$os=Get-CimInstance Win32_OperatingSystem; "
        "[math]::Round((1-($os.FreePhysicalMemory/$os.TotalVisibleMemorySize))*100,1)"
    )
    if windows_value is not None:
        try:
            return max(0.0, min(100.0, float(windows_value)))
        except ValueError:
            pass

    meminfo = "/proc/meminfo"
    if os.path.exists(meminfo):
        values: dict[str, int] = {}
        try:
            with open(meminfo, "r", encoding="utf-8") as handle:
                for line in handle:
                    key, separator, value = line.partition(":")
                    if separator and value.strip().endswith(" kB"):
                        values[key] = int(value.strip()[:-3])
            total = values.get("MemTotal")
            available = values.get("MemAvailable")
            if total and available is not None and total > 0:
                return max(0.0, min(100.0, (1 - (available / total)) * 100))
        except (OSError, ValueError):
            pass

    return None
