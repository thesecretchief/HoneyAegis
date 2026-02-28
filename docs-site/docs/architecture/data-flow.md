# Data Flow

This page describes how attacker activity flows from initial honeypot capture through enrichment to the real-time dashboard.

## Overview

```
Attacker ──► Honeypot ──► Log File ──► Backend Ingestion ──► PostgreSQL
                                              │
                                    ┌─────────┼──────────┐
                                    ▼         ▼          ▼
                                 GeoIP    AI Summary   Alerts
                                    │         │          │
                                    └─────────┼──────────┘
                                              ▼
                                     WebSocket Broadcast
                                              ▼
                                        Dashboard
```

## Light Profile Flow

In the default (light) deployment, log ingestion uses a file watcher:

1. **Capture** -- Cowrie writes JSON log lines to a mounted volume (`/data/cowrie/log/`).
2. **File Watcher** -- The FastAPI backend runs an `asyncio` file watcher that tails Cowrie log files.
3. **Parsing** -- Each JSON line is parsed into a `SessionEvent` model with fields like `src_ip`, `dst_port`, `command`, `timestamp`.
4. **Database Insert** -- The event is inserted into the `session_events` TimescaleDB hypertable via async SQLAlchemy.
5. **Enrichment** -- A Celery task is dispatched for GeoIP lookup and optional threat intel correlation.
6. **WebSocket Broadcast** -- The backend publishes the event to all connected dashboard clients via Redis pub/sub.
7. **AI Summary** -- If Ollama is enabled, a background task sends the session transcript to the local LLM for analysis.

## Full Profile Flow

The full profile adds Vector as a log shipper for higher throughput and structured routing:

1. **Capture** -- Honeypots write logs to mounted volumes.
2. **Vector** -- Vector watches log files, parses JSON, adds metadata, and forwards to the backend API (`POST /api/v1/ingest`).
3. **API Ingestion** -- The backend validates, deduplicates, and stores events.
4. **Enrichment Pipeline** -- Same as light profile but with parallel Celery workers for higher throughput.

## Enrichment Pipeline

Each new session triggers a chain of Celery tasks:

```python
# Celery task chain for a new session
chain(
    enrich_geoip.s(session_id),
    enrich_threat_intel.s(),
    generate_ai_summary.s(),
    send_alerts.s(),
)
```

| Stage | Description | Latency |
|---|---|---|
| **GeoIP** | MaxMind GeoLite2 lookup for country, city, ASN | < 1 ms |
| **Threat Intel** | AbuseIPDB / OTX / MISP correlation | 200-500 ms |
| **AI Summary** | Ollama inference on session transcript | 2-10 s |
| **Alerts** | Apprise notification dispatch | 100-300 ms |

## WebSocket Protocol

The dashboard connects to `ws://backend:8000/ws` and receives JSON frames:

```json
{
    "type": "new_session",
    "data": {
        "id": "sess_abc123",
        "src_ip": "185.220.101.42",
        "country": "DE",
        "protocol": "ssh",
        "commands": ["uname -a", "cat /etc/passwd"],
        "risk_score": 7.2,
        "ai_summary": "Reconnaissance activity targeting credential files..."
    }
}
```

## Data Retention

By default, TimescaleDB compression and retention policies manage storage:

| Data Type | Retention | Compression |
|---|---|---|
| Session events | 90 days | After 7 days |
| Raw logs | 30 days | After 3 days |
| AI summaries | 180 days | After 30 days |
| Malware samples | Indefinite | None (binary) |

Configure retention in `.env`:

```bash
DATA_RETENTION_SESSIONS_DAYS=90
DATA_RETENTION_LOGS_DAYS=30
```

## Related Pages

- [Architecture Overview](overview.md) -- High-level component map
- [Dashboard](../features/dashboard.md) -- Real-time WebSocket dashboard
- [AI Analysis](../features/ai-analysis.md) -- Ollama threat summaries
