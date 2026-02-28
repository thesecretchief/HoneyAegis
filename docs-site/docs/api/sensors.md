# Sensors API

Manage the multi-sensor fleet from a central hub. Register, monitor, and configure remote honeypot sensors.

## Endpoints

### List Sensors

```
GET /api/v1/sensors
Authorization: Bearer <token>
```

Returns all registered sensors with their current status and health metrics.

**Response:**

```json
{
    "items": [
        {
            "id": "sens_abc123",
            "name": "prod-vps-01",
            "location": "Frankfurt, DE",
            "status": "online",
            "tags": ["production", "ssh"],
            "last_heartbeat": "2026-02-28T12:00:30Z",
            "version": "1.0.0",
            "active_sessions": 3,
            "total_sessions": 1284,
            "cpu_percent": 12.5,
            "memory_percent": 45.2
        }
    ],
    "total": 5
}
```

### Register Sensor

```
POST /api/v1/sensors/register
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "rpi-dmz-02",
  "location": "Office DMZ",
  "tags": ["edge", "raspberry-pi"],
  "honeypots": ["cowrie"]
}
```

**Response:**

```json
{
    "id": "sens_def456",
    "name": "rpi-dmz-02",
    "sensor_token": "stok_eyJhbGciOiJIUzI1NiIs...",
    "created_at": "2026-02-28T12:00:00Z"
}
```

!!! warning
    The `sensor_token` is shown only once at registration. Store it securely on the sensor host.

### Get Sensor Detail

```
GET /api/v1/sensors/{sensor_id}
Authorization: Bearer <token>
```

Returns full sensor details including health metrics history.

### Update Sensor

```
PUT /api/v1/sensors/{sensor_id}
Authorization: Bearer <token>
```

Update sensor metadata (name, location, tags).

### Sensor Heartbeat

```
POST /api/v1/sensors/heartbeat
Authorization: Bearer <sensor-token>
```

Called by the sensor agent every 30 seconds. Includes CPU, memory, disk usage, and active session count.

### Rotate Sensor Token

```
POST /api/v1/sensors/{sensor_id}/rotate-token
Authorization: Bearer <token>
```

Generates a new authentication token and invalidates the old one.

### Sensor Health History

```
GET /api/v1/sensors/{sensor_id}/health?hours=24&interval=5m
Authorization: Bearer <token>
```

Returns time-series health data for monitoring dashboards.

### Remove Sensor

```
DELETE /api/v1/sensors/{sensor_id}
Authorization: Bearer <token>
```

Deregisters a sensor. Historical session data is preserved.

## Sensor Status

| Status | Condition |
|---|---|
| `online` | Heartbeat received within last 60 seconds |
| `degraded` | No heartbeat for 1-5 minutes |
| `offline` | No heartbeat for 5+ minutes |
| `disabled` | Manually disabled by admin |

## Related Pages

- [Fleet Management](../features/fleet-management.md) -- Fleet architecture and setup
- [Raspberry Pi Deployment](../deployment/raspberry-pi.md) -- Deploy sensors on RPi
- [Authentication API](authentication.md) -- Token authentication details
