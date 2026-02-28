# Honey Tokens

Honey tokens are decoy credentials and files planted to detect unauthorized access. When an attacker uses a honey token, HoneyAegis immediately triggers an alert and records the activity.

## Token Types

| Type | Description | Use Case |
|---|---|---|
| **Credential pairs** | Fake username/password combinations | Detect credential stuffing or leaked creds |
| **API keys** | Decoy API tokens | Detect unauthorized API access |
| **AWS keys** | Fake AWS access key pairs | Detect cloud credential theft |
| **Database DSNs** | Fake connection strings | Detect lateral movement to databases |
| **Files** | Canary documents (PDF, DOCX) | Detect data exfiltration |
| **DNS records** | Unique subdomains per token | Detect DNS reconnaissance |

## Creating Tokens

### Via Dashboard

Navigate to **Tokens > Create Token** and fill in the token details.

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/tokens \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "credential",
    "name": "staging-db-creds",
    "username": "db_readonly",
    "password": "Staging2026!",
    "description": "Planted in shared wiki page",
    "alert_channels": ["slack", "email"]
  }'
```

## Deployment Strategies

### SSH Honeypot Credentials

Plant credential pairs that Cowrie will accept and flag:

```bash
curl -X POST http://localhost:8000/api/v1/tokens/deploy \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "token_id": "tok_abc123",
    "target": "cowrie",
    "auto_accept": true
  }'
```

When an attacker logs in with the honey token credentials, Cowrie accepts the login and the session is automatically flagged as a token trigger.

### Canary Files

Generate trackable documents that phone home when opened:

```bash
curl -X POST http://localhost:8000/api/v1/tokens \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "type": "file",
    "name": "employee-salaries",
    "file_format": "pdf",
    "tracking_method": "dns",
    "description": "Placed on shared network drive"
  }'
```

### AWS Canary Keys

Generate fake AWS access keys that trigger alerts when used:

```bash
curl -X POST http://localhost:8000/api/v1/tokens \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "type": "aws_key",
    "name": "backup-service-key",
    "description": "Planted in .env file on staging server"
  }'
```

## Token Triggers

When a token is triggered, HoneyAegis:

1. Records the trigger event with full context (source IP, timestamp, method)
2. Sends immediate alerts via configured channels
3. Links the trigger to any associated honeypot session
4. Marks the token as "triggered" in the dashboard

## Dashboard View

The **Tokens** page shows:

- All active tokens with their type and deployment location
- Trigger history with timestamps and source details
- Token health (active, triggered, expired, revoked)
- Quick-deploy buttons for common token types

## Related Pages

- [Alerting](alerting.md) -- Configure alert channels for token triggers
- [Sessions API](../api/sessions.md) -- Sessions linked to token triggers
- [Security Model](../architecture/security-model.md) -- Deception layer in the security model
