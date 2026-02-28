# Sessions API

The Sessions API provides access to captured honeypot sessions, including metadata, commands, TTY recordings, and AI summaries.

## Endpoints

### List Sessions

```
GET /api/v1/sessions
```

Returns a paginated list of sessions with optional filtering.

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `page` | int | Page number (default: 1) |
| `per_page` | int | Results per page (default: 50, max: 200) |
| `protocol` | string | Filter by protocol (`ssh`, `telnet`, `http`, `smb`) |
| `src_ip` | string | Filter by source IP |
| `country` | string | Filter by country code (e.g., `DE`, `US`) |
| `min_risk` | float | Minimum risk score (0-10) |
| `max_risk` | float | Maximum risk score (0-10) |
| `sensor_id` | string | Filter by sensor |
| `since` | datetime | Sessions after this timestamp (ISO 8601) |
| `until` | datetime | Sessions before this timestamp (ISO 8601) |

**Example:**

```bash
curl "http://localhost:8000/api/v1/sessions?protocol=ssh&min_risk=5&per_page=10" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**

```json
{
    "items": [
        {
            "id": "sess_abc123",
            "src_ip": "185.220.101.42",
            "src_port": 54321,
            "dst_port": 22,
            "protocol": "ssh",
            "sensor_id": "sens_xyz",
            "started_at": "2026-02-28T10:15:00Z",
            "ended_at": "2026-02-28T10:17:30Z",
            "duration": 150,
            "command_count": 8,
            "risk_score": 7.2,
            "country": "DE",
            "city": "Frankfurt",
            "ai_summary": "Reconnaissance and cryptominer download attempt..."
        }
    ],
    "total": 342,
    "page": 1,
    "per_page": 10
}
```

### Get Session Detail

```
GET /api/v1/sessions/{session_id}
```

Returns full session details including commands, credentials, and threat intel.

```bash
curl http://localhost:8000/api/v1/sessions/sess_abc123 \
  -H "Authorization: Bearer $TOKEN"
```

### Get Session Commands

```
GET /api/v1/sessions/{session_id}/commands
```

Returns the ordered list of commands executed during the session.

### Get Session Replay

```
GET /api/v1/sessions/{session_id}/replay
```

Returns the TTY recording as a JSON timeline for the browser-based player.

### Export Session Video

```
POST /api/v1/sessions/{session_id}/export
```

Triggers video export (MP4, GIF, or asciicast). Returns a task ID for polling.

```bash
curl -X POST http://localhost:8000/api/v1/sessions/sess_abc123/export \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"format": "mp4", "speed": 4}'
```

### Delete Session

```
DELETE /api/v1/sessions/{session_id}
```

Permanently deletes a session and its associated data. Requires Admin role.

## Bulk Operations

### Bulk Export

```
POST /api/v1/sessions/bulk/export
```

```bash
curl -X POST http://localhost:8000/api/v1/sessions/bulk/export \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "session_ids": ["sess_abc", "sess_def", "sess_ghi"],
    "format": "json"
  }'
```

### Bulk Delete

```
POST /api/v1/sessions/bulk/delete
```

Requires Admin role. Accepts an array of session IDs.

## Related Pages

- [Session Replay](../features/session-replay.md) -- Browser-based TTY replay
- [AI Analysis](../features/ai-analysis.md) -- AI summary details
- [Export API](export.md) -- Batch export to SIEM
