# SIEM Export

HoneyAegis exports enriched honeypot events to external Security Information and Event Management (SIEM) systems and incident response platforms.

## Supported Formats

| Format | Description | Use Case |
|---|---|---|
| **JSON** | Structured JSON over HTTP/file | Custom integrations |
| **CEF** | Common Event Format (ArcSight) | ArcSight, QRadar |
| **Syslog** | RFC 5424 syslog over TCP/UDP | Any syslog collector |
| **Elastic (ECS)** | Elastic Common Schema | Elasticsearch, Kibana |
| **Splunk HEC** | HTTP Event Collector | Splunk |
| **TheHive** | Case/alert format | TheHive incident response |

## Configuration

### Syslog Export

```bash
SIEM_SYSLOG_ENABLED=true
SIEM_SYSLOG_HOST=syslog.example.com
SIEM_SYSLOG_PORT=514
SIEM_SYSLOG_PROTOCOL=tcp    # tcp or udp
SIEM_SYSLOG_FORMAT=cef      # cef or rfc5424
```

### Elasticsearch / ELK

```bash
SIEM_ELASTIC_ENABLED=true
SIEM_ELASTIC_URL=https://elasticsearch.example.com:9200
SIEM_ELASTIC_INDEX=honeyaegis-events
SIEM_ELASTIC_API_KEY=your-api-key
```

### Splunk HEC

```bash
SIEM_SPLUNK_ENABLED=true
SIEM_SPLUNK_HEC_URL=https://splunk.example.com:8088
SIEM_SPLUNK_HEC_TOKEN=your-hec-token
SIEM_SPLUNK_INDEX=honeypot
SIEM_SPLUNK_SOURCETYPE=honeyaegis
```

### TheHive

```bash
SIEM_THEHIVE_ENABLED=true
SIEM_THEHIVE_URL=https://thehive.example.com
SIEM_THEHIVE_API_KEY=your-api-key
SIEM_THEHIVE_MIN_RISK_SCORE=5    # Only export sessions above this score
```

## Export API

Manually export sessions in any supported format:

```bash
# Export sessions as JSON (last 24 hours)
curl -X GET "http://localhost:8000/api/v1/export?format=json&hours=24" \
  -H "Authorization: Bearer $TOKEN" \
  -o events.json

# Export as CEF
curl -X GET "http://localhost:8000/api/v1/export?format=cef&hours=24" \
  -H "Authorization: Bearer $TOKEN" \
  -o events.cef

# Export specific sessions
curl -X POST http://localhost:8000/api/v1/export \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"session_ids": ["sess_abc", "sess_def"], "format": "elastic"}'
```

## Event Schema (JSON)

Exported events follow this schema:

```json
{
    "event_id": "evt_abc123",
    "timestamp": "2026-02-28T12:00:00Z",
    "sensor": "prod-vps-01",
    "src_ip": "185.220.101.42",
    "src_port": 54321,
    "dst_port": 22,
    "protocol": "ssh",
    "session_id": "sess_abc123",
    "commands": ["uname -a", "cat /etc/passwd"],
    "geoip": {"country": "DE", "city": "Frankfurt", "asn": "AS24940"},
    "threat_intel": {"abuseipdb_score": 95, "otx_pulses": 3},
    "risk_score": 7.2,
    "ai_summary": "Reconnaissance activity targeting credential files..."
}
```

## CEF Format Example

```
CEF:0|HoneyAegis|HoneyAegis|1.0|ssh_session|SSH Session|7|src=185.220.101.42 spt=54321 dst=10.0.0.5 dpt=22 cs1=sess_abc123 cs1Label=SessionID msg=Reconnaissance activity
```

## Scheduling

Configure automatic exports on a schedule:

```bash
SIEM_EXPORT_INTERVAL=300     # Export every 5 minutes
SIEM_EXPORT_BATCH_SIZE=100   # Events per batch
```

## Related Pages

- [Export API](../api/export.md) -- Full API reference for exports
- [Threat Intelligence](threat-intel.md) -- Enrichment data included in exports
- [Alerting](alerting.md) -- Real-time alerts vs batch SIEM export
