"""Management-friendly reporting for infrastructure findings."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from health_score import summarize_findings


def build_report(
    findings: list[dict[str, Any]],
    *,
    host: dict[str, Any] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    timestamp = generated_at or datetime.now(timezone.utc).isoformat()
    summary = summarize_findings(findings)

    priority = [
        item for item in findings if item.get("severity") in {"Critical", "High", "Medium"}
    ]
    priority.sort(
        key=lambda item: {"Critical": 0, "High": 1, "Medium": 2}.get(
            item.get("severity", "Low"), 3
        )
    )

    return {
        "generated_at": timestamp,
        "host": host or {},
        "summary": summary,
        "priority_findings": priority,
        "findings": findings,
    }


def save_json_report(report: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return path


def management_summary(report: dict[str, Any]) -> str:
    summary = report["summary"]
    return (
        f"Health score: {summary['health_score']}/100 | "
        f"Risk level: {summary['risk_level']} | "
        f"Findings: {summary['total_findings']} | "
        f"Critical: {summary['severity_counts'].get('Critical', 0)} | "
        f"High: {summary['severity_counts'].get('High', 0)}"
    )
