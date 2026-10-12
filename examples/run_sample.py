"""Generate a deterministic sample infrastructure health report."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from health_score import summarize_findings
from report import build_report, management_summary, save_json_report
from system_checks import check_cpu_sample, check_disk_free, check_memory_sample


def main() -> None:
    findings = [
        check_cpu_sample(62.5),
        check_memory_sample(83.0),
        check_disk_free(7.5),
        {
            "check": "Critical application service",
            "status": "Attention",
            "severity": "High",
            "observed": {"running": False},
            "recommendation": "Investigate service dependencies and restore the approved service.",
        },
        {
            "check": "DNS resolution",
            "status": "Healthy",
            "severity": "Healthy",
            "observed": {"response_ms": 18.4},
            "recommendation": "No action required.",
        },
    ]

    report = build_report(
        findings,
        host={
            "hostname": "sample-server-01",
            "environment": "synthetic",
            "purpose": "portfolio demonstration",
        },
        generated_at="2026-01-01T00:00:00+00:00",
    )

    output_path = ROOT / "sample-data" / "sample_report.json"
    save_json_report(report, output_path)

    print(management_summary(report))
    print(json.dumps(summarize_findings(findings), indent=2))
    print(f"Report written to: {output_path}")


if __name__ == "__main__":
    main()
