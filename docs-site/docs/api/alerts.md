# Alerts API

Manage alert rules, notification history, and alert channels.

## Endpoints

### List Alerts

```
GET /api/v1/alerts
Authorization: Bearer <token>
```

Returns paginated alert history for the current tenant.

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `page` | int | Page number (default: 1) |
| `per_page` | int | Results per page (default: 50) |
| `status` | string | Filter: `sent`, `failed`, `suppressed` |
| `channel` | string | Filter by channel: `slack`, `email`, `discord`, etc. |
| `since` | datetime | Alerts after this timestamp (ISO 8601) |

**Example:**

```bash
curl "http://localhost:8000/api/v1/alerts?status=sent&per_page=20" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**

```json
{
    "items": [
        {
            "id": "alert_abc123",
            "session_id": "sess_xyz789",
            "type": "session",
            "channel": "slack",
            "status": "sent",
            "src_ip": "185.220.101.42",
            "risk_score": 7.2,
            "sent_at": "2026-02-28T10:15:05Z",
            "message_preview": "[HoneyAegis] New SSH Session from 185.220.101.42..."
        }
    ],
    "total": 156,
    "page": 1,
    "per_page": 20
}
```

### Get Alert Detail

```
GET /api/v1/alerts/{alert_id}
Authorization: Bearer <token>
```

Returns the full alert record including the complete message body and delivery status.

### Create Alert Rule

```
POST /api/v1/alerts
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "SSH Brute Force",
  "type": "session",
  "severity": "high",
  "enabled": true,
  "channels": ["slack", "email"],
  "condition": {
      "protocol": "ssh",
      "min_risk_score": 7,
      "country_not_in": ["US", "CA", "GB"]
  },
  "cooldown_minutes": 10
}
```

### Update Alert Rule

```
PUT /api/v1/alerts/{rule_id}
Authorization: Bearer <token>
```

### Delete Alert Rule

```
DELETE /api/v1/alerts/{rule_id}
Authorization: Bearer <token>
```

### Test Alert

```
POST /api/v1/alerts/test
Authorization: Bearer <token>
```

Sends a test notification to all configured channels and returns delivery results.

### Suppress Alert

```
POST /api/v1/alerts/{alert_id}/suppress
Authorization: Bearer <token>

{"duration_hours": 24, "reason": "Known scanner"}
```

Suppresses future alerts from the same source IP for the specified duration.

## Alert Types

| Type | Trigger | Description |
|---|---|---|
| `session` | New SSH/Telnet session | Fires on new honeypot connections |
| `malware` | File download detected | Fires when attacker downloads files |
| `honey_token` | Decoy credential used | Fires when a planted credential is attempted |
| `high_risk` | Risk score threshold | Fires when AI risk score exceeds threshold |
| `sensor_offline` | Missed heartbeats | Fires when a sensor goes offline |

## Alert Statuses

| Status | Description |
|---|---|
| `sent` | Successfully delivered to the channel |
| `failed` | Delivery failed (see error field for details) |
| `suppressed` | Matched a suppression rule |
| `throttled` | Rate limit or cooldown prevented delivery |

## Notification Channels

HoneyAegis uses [Apprise](https://github.com/caronc/apprise) for multi-channel alerting:

- **Email** -- SMTP relay
- **Slack** -- Webhook URL
- **Discord** -- Webhook URL
- **Microsoft Teams** -- Connector URL
- **ntfy** -- Push notifications
- **SMS** -- Twilio integration
- **PagerDuty** -- Events v2 API
- **Telegram** -- Bot API

Configure channels via the `APPRISE_URLS` environment variable or the dashboard settings page.

## Related Pages

- [Alerting Feature](../features/alerting.md) -- Configuration and channel setup
- [Webhooks API](webhooks.md) -- Custom webhook integrations
- [Sessions API](sessions.md) -- Session data referenced by alerts
