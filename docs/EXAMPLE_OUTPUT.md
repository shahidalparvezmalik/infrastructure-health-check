# Example Output

This example uses the repository's deterministic synthetic sample data. It is **not** a report from a production or employer environment.

## Management Summary

```text
Infrastructure Health Check
---------------------------
Host: sample-server-01
Health score: 85/100
Risk level: Low
Findings: 5
Critical: 0
High: 2
Medium: 1
Low: 0
Healthy: 2
```

## Findings

```text
Severity  Status       Check
--------  -----------  ----------------------------
Healthy   Healthy      CPU utilization
Medium    Attention    Memory utilization
High      Attention    Disk free capacity
High      Attention    Critical application service
Healthy   Healthy      DNS resolution
```

## Management Interpretation

**Overall assessment:** Low risk in this synthetic example.

Two high-priority findings require attention:

1. **Disk free capacity** — review storage growth, temporary files and application logs.
2. **Critical application service** — investigate service dependencies and restore the approved service.

The memory condition is classified as **Medium** and should be addressed through planned investigation.

## Operational View

```text
Technical signal
       ↓
Health finding
       ↓
Severity
       ↓
Operational risk
       ↓
Recommended action
```

The purpose of the example is to demonstrate the transition from raw infrastructure measurements to a management-oriented operational view.

> **Note:** The health score and risk level are produced by the prototype's demonstration model. Production thresholds should be calibrated to service criticality, business impact, dependencies and approved operational policy.
