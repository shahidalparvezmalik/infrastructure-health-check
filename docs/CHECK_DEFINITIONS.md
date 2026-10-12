# Check Definitions

## System Checks

### CPU utilization
Measures processor utilization against configurable thresholds.

### Memory utilization
Measures memory utilization against configurable thresholds.

### Disk free capacity
Measures available storage capacity. Lower free capacity increases operational risk.

## Network Checks

### TCP connectivity
Attempts a TCP connection to an approved host and port using a bounded timeout.

### Host lookup
Confirms that a hostname can be resolved before deeper connectivity checks.

## DNS Checks

### DNS resolution
Records successful/failed resolution and response time.

## Service Checks

### Windows service
On authorized Windows hosts, uses the built-in Service Control Manager command to inspect a named service.

On non-Windows hosts, the check is marked **Not Evaluated** rather than failing the complete report.

## Design Rule

Checks should remain:

- read-only
- bounded by timeouts
- explicit about unsupported environments
- easy to test
- safe to disable individually
