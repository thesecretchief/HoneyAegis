# Configuration

HoneyAegis is configured via environment variables in the `.env` file.

## Core Settings

| Variable | Default | Description |
|---|---|---|
| `HONEYAEGIS_ENV` | `production` | Environment mode (`production`, `development`) |
| `HONEYAEGIS_DEBUG` | `false` | Enable debug logging and permissive CORS |
| `HONEYAEGIS_SECRET_KEY` | (required) | Application secret key (64+ chars) |
| `HONEYAEGIS_TIMEZONE` | `UTC` | Timezone for logs and displays |

## Database

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_HOST` | `postgres` | PostgreSQL hostname |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_DB` | `honeyaegis` | Database name |
| `POSTGRES_USER` | `honeyaegis` | Database user |
| `POSTGRES_PASSWORD` | (required) | Database password |

## Authentication

| Variable | Default | Description |
|---|---|---|
| `JWT_SECRET_KEY` | (required) | JWT signing secret |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiry |
| `ADMIN_EMAIL` | `admin@honeyaegis.local` | Default admin email |
| `ADMIN_PASSWORD` | `changeme` | Default admin password |

## AI (Ollama)

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_ENABLED` | `false` | Enable local AI summaries |
| `OLLAMA_HOST` | `ollama` | Ollama host |
| `OLLAMA_PORT` | `11434` | Ollama port |
| `OLLAMA_MODEL` | `phi3:mini` | LLM model to use |

## Threat Intelligence

| Variable | Default | Description |
|---|---|---|
| `ABUSEIPDB_API_KEY` | (empty) | AbuseIPDB API key |
| `OTX_API_KEY` | (empty) | AlienVault OTX API key |
| `MISP_URL` | (empty) | MISP server URL |
| `MISP_API_KEY` | (empty) | MISP API key |
| `VIRUSTOTAL_API_KEY` | (empty) | VirusTotal API key |

## Alerting (Apprise)

| Variable | Default | Description |
|---|---|---|
| `APPRISE_URLS` | (empty) | Apprise notification URLs (comma-separated) |
| `ALERT_ON_NEW_SESSION` | `true` | Alert on new honeypot sessions |
| `ALERT_ON_MALWARE_CAPTURE` | `true` | Alert on malware file captures |
| `ALERT_COOLDOWN_MINUTES` | `5` | Minimum time between alerts |

## Rate Limiting

| Variable | Default | Description |
|---|---|---|
| `RATE_LIMIT_GLOBAL_CAPACITY` | `100` | Global rate limit (req/burst) |
| `RATE_LIMIT_AUTH_CAPACITY` | `10` | Auth endpoint rate limit |
