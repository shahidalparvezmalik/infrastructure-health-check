"""Run safe, read-only infrastructure diagnostics on the current host."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dns_checks import check_dns_resolution
from health_score import calculate_health_score
from network_checks import check_host_name, check_tcp_connectivity
from report import build_report, management_summary, save_json_report
from service_checks import check_windows_service
from system_checks import (
    check_cpu,
    check_disk_free,
    check_memory,
    get_cpu_percent,
    get_disk_free_percent,
    get_host_information,
    get_memory_percent,
)


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def not_evaluated(check: str, reason: str) -> dict[str, Any]:
    return {
        "check": check,
        "status": "Not Evaluated",
        "severity": "Low",
        "observed": {"reason": reason},
        "recommendation": reason,
    }


def run_checks(
    config: dict[str, Any],
    *,
    skip_network: bool = False,
    skip_dns: bool = False,
    skip_services: bool = False,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    findings: list[dict[str, Any]] = []
    thresholds = config.get("thresholds", {})

    cpu = get_cpu_percent()
    if cpu is None:
        findings.append(
            not_evaluated(
                "CPU utilization",
                "CPU utilization is not available on this operating system.",
            )
        )
    else:
        findings.append(check_cpu(cpu, thresholds.get("cpu_percent")))

    memory = get_memory_percent()
    if memory is None:
        findings.append(
            not_evaluated(
                "Memory utilization",
                "Memory utilization is not available on this operating system.",
            )
        )
    else:
        findings.append(check_memory(memory, thresholds.get("memory_percent")))

    try:
        disk_free = get_disk_free_percent()
        findings.append(check_disk_free(disk_free, thresholds.get("disk_free_percent")))
    except OSError as exc:
        findings.append(
            not_evaluated(
                "Disk free capacity",
                f"Disk capacity could not be evaluated: {exc}",
            )
        )

    if not skip_dns:
        dns_targets = config.get("dns_targets", ["localhost"])
        for hostname in dns_targets:
            findings.append(check_dns_resolution(hostname))

    if not skip_network:
        network = config.get("network", {})
        timeout = float(network.get("default_timeout_seconds", 3))
        for target in config.get("approved_targets", []):
            host = str(target.get("host", "")).strip()
            if not host:
                continue
            findings.append(check_host_name(host))
            for port in target.get("ports", []):
                findings.append(
                    check_tcp_connectivity(host, int(port), timeout_seconds=timeout)
                )

    if not skip_services:
        for service_name in config.get("windows_services", []):
            findings.append(check_windows_service(service_name))

    return get_host_information(), findings


def print_findings(findings: list[dict[str, Any]]) -> None:
    print("\nFindings")
    print("--------")
    for item in findings:
        observed = json.dumps(item.get("observed", {}), sort_keys=True)
        print(
            f"- {item['severity']:<8} | {item['status']:<13} | "
            f"{item['check']} | {observed}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run safe, read-only infrastructure health checks."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "config" / "checks.json",
        help="Path to the JSON configuration file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path for a JSON report.",
    )
    parser.add_argument(
        "--skip-network",
        action="store_true",
        help="Skip TCP and host connectivity checks.",
    )
    parser.add_argument(
        "--skip-dns",
        action="store_true",
        help="Skip DNS resolution checks.",
    )
    parser.add_argument(
        "--skip-services",
        action="store_true",
        help="Skip Windows service checks.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = load_config(args.config)

    host, findings = run_checks(
        config,
        skip_network=args.skip_network,
        skip_dns=args.skip_dns,
        skip_services=args.skip_services,
    )

    # Not-evaluated observations remain visible but do not distort the score.
    scored_findings = [
        item for item in findings if item.get("status") != "Not Evaluated"
    ]
    report = build_report(
        scored_findings,
        host={
            **host,
            "execution_mode": "local read-only diagnostics",
        },
        generated_at=datetime.now(timezone.utc).isoformat(),
    )

    report["all_findings"] = findings
    report["scored_findings"] = scored_findings
    report["health_score"] = calculate_health_score(scored_findings)

    print("\nInfrastructure Health Check")
    print("---------------------------")
    print(f"Host: {host.get('hostname', 'unknown')}")
    print(management_summary(report))
    print_findings(findings)

    if args.output:
        save_json_report(report, args.output)
        print(f"\nJSON report written to: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
