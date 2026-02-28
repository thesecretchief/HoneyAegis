# Advanced Reporting

HoneyAegis provides executive-level reporting for enterprise security teams.

## Executive Report

Generate a comprehensive threat summary for any time period:

```bash
GET /api/v1/reporting/executive?period=7d
```

Supported periods: `24h`, `7d`, `30d`, `90d`

### Report Contents

- **Total sessions** — attack session count
- **Unique IPs** — attacker diversity
- **Alerts** — triggered alert count
- **Malware captures** — captured file count
- **Top attackers** — most active IPs with geo, session count, threat level
- **Attack vectors** — protocol breakdown (SSH, Telnet, etc.)
- **Compliance metrics** — security posture checklist
- **Risk score** — 0-100 aggregate risk with level (low/medium/high/critical)

## Risk Score

The risk score is calculated from four factors:

| Factor | Max Points | Thresholds |
|---|---|---|
| Session volume | 25 | 0 → 10 → 100 → 500 → 1000+ |
| Critical alerts | 30 | 0 → 5 → 20 → 50+ |
| Malware captures | 25 | 0 → 5 → 20+ |
| Attacker diversity | 20 | 0 → 20 → 100 → 500+ |

Risk levels:
- **Low** (0-24): Minimal threat activity
- **Medium** (25-49): Moderate scanning / probing
- **High** (50-74): Active attacks detected
- **Critical** (75-100): Sustained high-volume attacks

## Compliance Metrics

```bash
GET /api/v1/reporting/compliance
```

Returns security posture metrics:
- Non-root containers
- Network isolation
- Encrypted credentials
- Rate limiting
- Audit logging
- TLS termination
- Data retention policy

## Custom Risk Score

Calculate a risk score with custom inputs:

```bash
GET /api/v1/reporting/risk-score?sessions=500&critical_alerts=10&malware=3&unique_ips=150
```
