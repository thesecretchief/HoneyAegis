# Export API

The Export API provides batch and scheduled export of honeypot event data in multiple formats for SIEM integration, reporting, and archiving.

## Endpoints

### Export Events

```
GET /api/v1/export
```

Export events in the specified format.

**Query Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `format` | string | `json` | Output format: `json`, `cef`, `csv`, `elastic`, `splunk` |
| `hours` | int | `24` | Lookback period in hours |
| `since` | datetime | -- | Start timestamp (ISO 8601), overrides `hours` |
| `until` | datetime | -- | End timestamp (ISO 8601) |
| `protocol` | string | -- | Filter by protocol |
| `min_risk` | float | -- | Minimum risk score |
| `sensor_id` | string | -- | Filter by sensor |
| `limit` | int | `1000` | Maximum events to return |

**Example:**

```bash
# Export last 24 hours as JSON
curl "http://localhost:8000/api/v1/export?format=json&hours=24" \
  -H "Authorization: Bearer $TOKEN" \
  -o events.json

# Export high-risk SSH sessions as CEF
curl "http://localhost:8000/api/v1/export?format=cef&protocol=ssh&min_risk=7" \
  -H "Authorization: Bearer $TOKEN" \
  -o high_risk.cef

# Export as CSV for spreadsheet analysis
curl "http://localhost:8000/api/v1/export?format=csv&hours=168" \
  -H "Authorization: Bearer $TOKEN" \
  -o weekly_report.csv
```

### Format-Specific Endpoints

These convenience endpoints mirror the generic export with a fixed format:

```
GET /api/v1/export/json?limit=100       # Raw JSON array
GET /api/v1/export/cef?limit=100        # Common Event Format (ArcSight, QRadar)
GET /api/v1/export/syslog?limit=100     # RFC 5424 syslog
GET /api/v1/export/elk?limit=100        # NDJSON with ECS field mapping
GET /api/v1/export/splunk?limit=100     # Splunk HTTP Event Collector format
GET /api/v1/export/thehive?limit=100    # TheHive alert format with TLP/PAP
```

All format endpoints accept `limit`, `since`, and `until` query parameters.

### Export Specific Sessions

```
POST /api/v1/export
```

Export a specific set of sessions by ID.

```bash
curl -X POST http://localhost:8000/api/v1/export \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_ids": ["sess_abc", "sess_def"],
    "format": "json",
    "include_commands": true,
    "include_ai_summary": true,
    "include_threat_intel": true
  }'
```

### Export Malware IOCs

```
GET /api/v1/export/iocs
```

Export indicators of compromise from malware analysis.

```bash
curl "http://localhost:8000/api/v1/export/iocs?format=stix&hours=72" \
  -H "Authorization: Bearer $TOKEN" \
  -o iocs.stix.json
```

Supported IOC formats: `json`, `csv`, `stix`, `misp`

### Scheduled Exports

#### List Schedules

```
GET /api/v1/export/schedules
```

#### Create Schedule

```
POST /api/v1/export/schedules
```

```bash
curl -X POST http://localhost:8000/api/v1/export/schedules \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Daily ELK Export",
    "format": "elastic",
    "destination": "https://elk.example.com:9200/honeyaegis",
    "interval": "daily",
    "time": "02:00",
    "filters": {"min_risk": 3},
    "enabled": true
  }'
```

#### Delete Schedule

```
DELETE /api/v1/export/schedules/{schedule_id}
```

## Rate Limits

Export endpoints have dedicated rate limits to prevent resource exhaustion:

| Endpoint | Burst | Sustained |
|---|---|---|
| `GET /api/v1/export` | 20 req | 10 req/s |
| `POST /api/v1/export` | 10 req | 5 req/s |
| `GET /api/v1/export/iocs` | 10 req | 5 req/s |

All exports are tenant-scoped and require authentication.

## Related Pages

- [SIEM Export Feature](../features/siem-export.md) -- Configuration and format details
- [Sessions API](sessions.md) -- Individual session access
- [Webhooks API](webhooks.md) -- Real-time event delivery
