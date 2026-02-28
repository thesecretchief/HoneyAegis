# Threat Intelligence

HoneyAegis correlates attacker IPs and indicators against multiple threat intelligence feeds to enrich sessions with reputation data and known threat context.

## Supported Feeds

| Feed | Type | API Key Required | Data Provided |
|---|---|---|---|
| **AbuseIPDB** | IP reputation | Yes (free tier available) | Abuse confidence score, report count, categories |
| **AlienVault OTX** | Threat intelligence | Yes (free) | Pulses, indicators, malware families |
| **MISP** | Threat sharing | Yes (self-hosted) | Events, attributes, tags, correlations |
| **VirusTotal** | File/IP analysis | Yes (free tier available) | Detection ratio, community votes, file metadata |

## Configuration

Add API keys to your `.env` file:

```bash
ABUSEIPDB_API_KEY=your-key-here
OTX_API_KEY=your-key-here
MISP_URL=https://misp.your-org.com
MISP_API_KEY=your-key-here
VIRUSTOTAL_API_KEY=your-key-here
```

Feeds with no API key configured are silently skipped. You can enable any combination of feeds.

## Enrichment Flow

When a new session is captured, the enrichment pipeline:

1. Checks the Redis cache for recent lookups on the same IP (TTL: 1 hour).
2. Queries each configured feed in parallel.
3. Aggregates results into a unified `ThreatIntelReport`.
4. Stores the report in PostgreSQL linked to the session.
5. Updates the session risk score based on threat intel hits.

## Risk Score Calculation

The risk score (0-10) is computed from multiple signals:

| Signal | Weight | Example |
|---|---|---|
| AbuseIPDB confidence | 30% | Score > 80 adds 3 points |
| OTX pulse count | 20% | 5+ pulses adds 2 points |
| MISP event match | 20% | Any match adds 2 points |
| VirusTotal detections | 15% | File detected by 10+ engines adds 1.5 points |
| Session behavior | 15% | Malware download attempt adds 1.5 points |

## Dashboard Integration

Threat intel data appears in the session detail view:

- **Reputation badge** -- Color-coded indicator (clean, suspicious, malicious)
- **Feed results** -- Expandable panel showing each feed's response
- **Related sessions** -- Other sessions from the same IP or threat group
- **IOC list** -- Extracted indicators of compromise (IPs, domains, hashes)

## MISP Integration

HoneyAegis can both consume and publish events to MISP:

```bash
# Enable MISP publishing (push new IOCs to your MISP instance)
MISP_PUBLISH_ENABLED=true
MISP_PUBLISH_MIN_RISK_SCORE=7
```

Sessions with a risk score above the threshold are automatically published as MISP events with appropriate tags and attributes.

## Related Pages

- [Data Flow](../architecture/data-flow.md) -- Enrichment pipeline details
- [Alerting](alerting.md) -- Trigger alerts based on threat intel hits
- [SIEM Export](siem-export.md) -- Export enriched events to your SIEM
- [Configuration](../getting-started/configuration.md) -- API key configuration
