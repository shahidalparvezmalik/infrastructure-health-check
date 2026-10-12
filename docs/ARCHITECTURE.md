# Architecture

## Objective

The project separates **diagnostic collection** from **risk interpretation** and **management reporting**.

This allows infrastructure checks to evolve without changing the reporting layer.

## Layers

### 1. Diagnostic Layer

Modules such as:

- system checks
- network checks
- DNS checks
- service checks

collect read-only observations.

### 2. Assessment Layer

The health-score module translates findings into:

- severity
- health score
- overall risk level
- severity counts

### 3. Reporting Layer

The reporting module produces:

- complete machine-readable JSON
- priority findings
- management summary

### 4. Integration Layer

Future integrations can feed the same finding structure into:

- ITSM platforms
- monitoring systems
- CMDBs
- Power BI
- approved automation platforms

## Operating Pattern

**Collect → Normalize → Assess → Prioritize → Report → Improve**

The design avoids mixing technical collection logic with management decisions.
