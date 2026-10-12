"""Read-only service diagnostics.

Windows service inspection is provided through the built-in sc.exe command
when available. The function degrades safely on non-Windows systems.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
from typing import Any


def check_windows_service(service_name: str) -> dict[str, Any]:
    if platform.system().lower() != "windows" or shutil.which("sc.exe") is None:
        return {
            "check": f"Windows service: {service_name}",
            "status": "Not Evaluated",
            "severity": "Low",
            "observed": {"supported": False},
            "recommendation": "Run this check on an authorized Windows host where sc.exe is available.",
        }

    completed = subprocess.run(
        ["sc.exe", "query", service_name],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    output = (completed.stdout + "\n" + completed.stderr).strip()

    if completed.returncode != 0:
        return {
            "check": f"Windows service: {service_name}",
            "status": "Attention",
            "severity": "High",
            "observed": {"return_code": completed.returncode, "output": output[:1000]},
            "recommendation": "Verify that the service exists and review the Windows Service Control Manager.",
        }

    running = "RUNNING" in output
    return {
        "check": f"Windows service: {service_name}",
        "status": "Healthy" if running else "Attention",
        "severity": "Healthy" if running else "High",
        "observed": {"running": running, "output": output[:1000]},
        "recommendation": (
            "No action required."
            if running
            else "Investigate the service state, dependent services and recent system events."
        ),
    }
