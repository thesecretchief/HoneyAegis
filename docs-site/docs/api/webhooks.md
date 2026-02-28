# Webhooks API

Configure auto-response webhooks that fire on honeypot events.

## Endpoints

### List Webhooks

```
GET /api/v1/webhooks
Authorization: Bearer <token>
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
  "enabled": true
}
```

### Test Webhook

```
POST /api/v1/webhooks/{webhook_id}/test
Authorization: Bearer <token>
```

### Delete Webhook

```
DELETE /api/v1/webhooks/{webhook_id}
Authorization: Bearer <token>
```

## Signature Verification

All payloads include an `X-HoneyAegis-Signature` header with HMAC-SHA256 signature.
