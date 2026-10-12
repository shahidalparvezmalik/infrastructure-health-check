"""Unit tests for the infrastructure health-check proof of concept."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from health_score import calculate_health_score, risk_level
from report import build_report, management_summary
from system_checks import (
    check_disk_free,
    classify_threshold,
    get_cpu_percent,
    get_memory_percent,
)


class HealthCheckTests(unittest.TestCase):
    def test_threshold_classification(self) -> None:
        self.assertEqual(
            classify_threshold(95, medium=80, high=90, critical=98),
            "High",
        )
        self.assertEqual(
            classify_threshold(99, medium=80, high=90, critical=98),
            "Critical",
        )

    def test_disk_severity(self) -> None:
        self.assertEqual(check_disk_free(4)["severity"], "Critical")
        self.assertEqual(check_disk_free(12)["severity"], "Medium")
        self.assertEqual(check_disk_free(40)["severity"], "Healthy")

    def test_health_score_is_bounded(self) -> None:
        findings = [
            {"severity": "Critical"},
            {"severity": "High"},
            {"severity": "Medium"},
        ]
        score = calculate_health_score(findings)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        self.assertEqual(risk_level(score), "Medium")

    def test_local_resource_readers_return_valid_values(self) -> None:
        cpu = get_cpu_percent()
        memory = get_memory_percent()

        if cpu is not None:
            self.assertGreaterEqual(cpu, 0.0)
            self.assertLessEqual(cpu, 100.0)

        if memory is not None:
            self.assertGreaterEqual(memory, 0.0)
            self.assertLessEqual(memory, 100.0)

    def test_report_has_management_summary(self) -> None:
        findings = [{"check": "DNS", "severity": "Healthy", "status": "Healthy"}]
        report = build_report(
            findings,
            host={"hostname": "test"},
            generated_at="2026-01-01T00:00:00+00:00",
        )
        self.assertEqual(report["summary"]["health_score"], 100)
        self.assertIn("Health score", management_summary(report))


if __name__ == "__main__":
    unittest.main()
