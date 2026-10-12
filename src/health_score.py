"""Translate technical findings into an operational health score."""

from __future__ import annotations

from collections import Counter
from typing import Any

SEVERITY_WEIGHT = {
    "Healthy": 0,
    "Low": 5,
    "Medium": 15,
    "High": 30,
    "Critical": 50,
}


def severity_weight(severity: str) -> int:
    return SEVERITY_WEIGHT.get(severity, 10)


def calculate_health_score(findings: list[dict[str, Any]]) -> int:
    if not findings:
        return 100

    penalty = sum(severity_weight(item.get("severity", "Low")) for item in findings)
    normalized_penalty = round(penalty / len(findings))
    return max(0, min(100, 100 - normalized_penalty))


def risk_level(score: int) -> str:
    if score >= 90:
        return "Healthy"
    if score >= 75:
        return "Low"
    if score >= 50:
        return "Medium"
    if score >= 25:
        return "High"
    return "Critical"


def summarize_findings(findings: list[dict[str, Any]]) -> dict[str, Any]:
    severities = Counter(item.get("severity", "Low") for item in findings)
    statuses = Counter(item.get("status", "Unknown") for item in findings)
    score = calculate_health_score(findings)
    return {
        "health_score": score,
        "risk_level": risk_level(score),
        "total_findings": len(findings),
        "severity_counts": dict(severities),
        "status_counts": dict(statuses),
    }
