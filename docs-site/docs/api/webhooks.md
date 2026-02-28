# Webhooks API

Configure auto-response webhooks that fire on honeypot events. Webhooks deliver JSON payloads over HTTPS when specified events occur.

## Endpoints

### List Webhooks

```
GET /api/v1/webhooks
Authorization: Bearer <token>
```

**Response:**

```json
{
    "items": [
        {
            "id": "wh_abc123",
            "name": "SOAR Integration",
            "url": "https://soar.example.com/api/ingest",
            "events": ["session.new", "session.end", "malware.captured"],
            "enabled": true,
            "created_at": "2026-01-20T10:00:00Z",
            "last_triggered": "2026-02-28T11:45:00Z",
            "failure_count": 0
        }
    ],
    "total": 3
}
```

### Create Webhook

```
POST /api/v1/webhooks
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Slack Security Channel",
  "url": "https://hooks.slack.com/services/T00/B00/xxx",
  "events": ["session.new", "alert.fired"],
  "secret": "my-webhook-secret",
  "enabled": true,
  "headers": {
      "X-Custom-Header": "honeyaegis"
  }
}
```

### Update Webhook

```
PUT /api/v1/webhooks/{webhook_id}
Authorization: Bearer <token>
```

### Test Webhook

```
POST /api/v1/webhooks/{webhook_id}/test
Authorization: Bearer <token>
```

Sends a test payload and returns the response status and latency.

### Get Delivery Log

```
GET /api/v1/webhooks/{webhook_id}/deliveries
Authorization: Bearer <token>
```

Returns recent delivery attempts with status codes and response times.

### Delete Webhook

```
DELETE /api/v1/webhooks/{webhook_id}
Authorization: Bearer <token>
```

## Event Types

| Event | Description |
|---|---|
| `session.new` | New honeypot session started |
| `session.end` | Session ended |
| `session.high_risk` | Risk score exceeds threshold |
| `malware.captured` | Malware file captured |
| `token.triggered` | Honey token used |
| `sensor.offline` | Sensor went offline |
| `alert.fired` | Alert dispatched |

## Payload Format

```json
{
    "event": "session.new",
    "timestamp": "2026-02-28T12:00:00Z",
    "webhook_id": "wh_abc123",
    "data": {
        "session_id": "sess_xyz789",
        "src_ip": "185.220.101.42",
        "protocol": "ssh",
        "sensor": "prod-vps-01",
        "risk_score": 7.2
    }
}
```

## Signature Verification

All payloads include an `X-HoneyAegis-Signature` header with HMAC-SHA256 signature of the request body:

```python
import hmac, hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

## Retry Policy

Failed deliveries are retried with exponential backoff: 30 seconds, 2 minutes, 10 minutes, 1 hour. After 4 failed retries, the delivery is marked as failed. Webhooks with 10+ consecutive failures are automatically disabled.

## Related Pages

- [Alerting Feature](../features/alerting.md) -- Apprise-based alerting (simpler alternative)
- [SIEM Export](../features/siem-export.md) -- Batch export to SIEM platforms
- [Alerts API](alerts.md) -- Alert management endpoints
