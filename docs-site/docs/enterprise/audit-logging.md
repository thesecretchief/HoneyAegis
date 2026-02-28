# Audit Logging

HoneyAegis provides structured audit logging for compliance and forensics.

## Audited Events

| Event | Description |
|---|---|
| `auth.login.success` | Successful user login |
| `auth.login.failure` | Failed login attempt |
| `token.created` | Honey token created |
| `token.deleted` | Honey token deleted |
| `webhook.created` | Webhook configured |
| `webhook.deleted` | Webhook removed |
| `webhook.tested` | Webhook test fired |
| `tenant.created` | New tenant provisioned |
| `tenant.updated` | Tenant settings changed |
| `sensor.registered` | New sensor registered |
| `config.updated` | System config changed |
| `plugin.reloaded` | Plugins reloaded |
| `report.generated` | Report exported |
| `session.exported` | Session data exported |
| `honey_token.triggered` | Honey token activated |
| `api_key.rotated` | API key rotated |

## Output Format

### Structured JSON

```json
{
  "@timestamp": "2026-02-28T14:30:00.000Z",
  "event": "auth.login.success",
  "severity": "info",
  "actor": "admin@honeyaegis.local",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "resource_type": "user",
  "ip_address": "192.168.1.100",
  "service": "honeyaegis-api"
}
```

### CEF (Common Event Format)

```
CEF:0|HoneyAegis|HoneyAegis|0.6.0|auth.login.success|auth.login.success|3|src=192.168.1.100
```

### Syslog (RFC 5424)

```
<14>1 2026-02-28T14:30:00.000000Z honeyaegis honeyaegis-api - auth.login.success [honeyaegis@0 actor="admin@honeyaegis.local"]
```

## SIEM Integration

Export audit events to your SIEM:
- **Splunk** — via HEC endpoint (`/api/v1/export/splunk`)
- **Elasticsearch** — via bulk NDJSON (`/api/v1/export/elk`)
- **TheHive** — via alert format (`/api/v1/export/thehive`)
- **Generic** — JSON, CEF, or Syslog formats
