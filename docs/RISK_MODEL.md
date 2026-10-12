# Operational Risk Model

The project converts technical observations into a simple management-oriented risk model.

## Severity

### Healthy
No material issue detected.

### Low
Informational condition or low operational impact.

### Medium
Condition that should be addressed through planned action.

### High
Significant operational risk requiring timely investigation.

### Critical
Immediate or potentially severe impact requiring urgent action.

## Health Score

The prototype applies weighted penalties:

| Severity | Weight |
|---|---:|
| Healthy | 0 |
| Low | 5 |
| Medium | 15 |
| High | 30 |
| Critical | 50 |

The average penalty is subtracted from 100 and bounded between 0 and 100.

## Risk Level

| Score | Risk level |
|---|---|
| 90–100 | Healthy |
| 75–89 | Low |
| 50–74 | Medium |
| 25–49 | High |
| 0–24 | Critical |

This is a demonstration model, not an enterprise risk standard. In production, thresholds should be calibrated to service criticality, business impact, dependencies and agreed operational policy.
