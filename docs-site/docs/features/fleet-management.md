# Fleet Management

HoneyAegis supports managing multiple honeypot sensors from a single dashboard. Deploy sensors across VPS instances, homelab servers, and Raspberry Pi devices, then monitor them all from one console.

## Architecture

```
┌──────────────────────────────────────────┐
│           HoneyAegis Central             │
│   Backend + Dashboard + PostgreSQL       │
│              ▲     ▲     ▲               │
└──────────────┼─────┼─────┼───────────────┘
               │     │     │
        ┌──────┘     │     └──────┐
        ▼            ▼            ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Sensor 1│ │ Sensor 2│ │ Sensor 3│
   │ VPS     │ │ Homelab │ │ RPi     │
   │ Cowrie  │ │ Full    │ │ Cowrie  │
   └─────────┘ └─────────┘ └─────────┘
```

Each sensor runs a lightweight agent that forwards events to the central backend over an authenticated HTTPS connection.

## Registering a Sensor

### 1. Generate a Sensor Token

From the central dashboard, navigate to **Fleet > Add Sensor** or use the API:

```bash
curl -X POST http://localhost:8000/api/v1/sensors \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "prod-vps-01",
    "location": "Frankfurt, DE",
    "tags": ["production", "ssh"]
  }'

# Response includes the sensor_token
```

### 2. Deploy the Sensor Agent

On the remote machine:

```bash
# Download and run the sensor setup script
curl -sSL https://raw.githubusercontent.com/thesecretchief/HoneyAegis/main/scripts/sensor-setup.sh | bash

# Configure the agent
cat > /etc/honeyaegis/sensor.env <<EOF
CENTRAL_URL=https://honeyaegis.example.com
SENSOR_TOKEN=your-sensor-token-here
SENSOR_NAME=prod-vps-01
EOF

# Start the sensor
docker compose -f docker-compose.sensor.yml up -d
```

### 3. Verify Connectivity

The sensor appears in the Fleet dashboard within 30 seconds. Status indicators:

| Status | Meaning |
|---|---|
| **Online** | Heartbeat received within last 60 seconds |
| **Degraded** | Heartbeat delayed (60-300 seconds) |
| **Offline** | No heartbeat for 5+ minutes |

## Fleet Dashboard

The fleet view provides:

- **Sensor map** -- Geographic view of all sensors with status indicators
- **Aggregate statistics** -- Combined session counts, top attacking IPs, protocol breakdown
- **Per-sensor drill-down** -- Click any sensor to view its individual sessions
- **Health monitoring** -- CPU, memory, disk usage, and uptime per sensor
- **Remote configuration** -- Update sensor settings from the central dashboard

## Sensor Heartbeat

Each sensor sends a heartbeat every 30 seconds containing:

```json
{
    "sensor_id": "sens_abc123",
    "timestamp": "2026-02-28T12:00:00Z",
    "uptime": 86400,
    "active_sessions": 3,
    "cpu_percent": 12.5,
    "memory_percent": 45.2,
    "disk_percent": 30.0,
    "version": "1.0.0"
}
```

## Related Pages

- [Sensors API](../api/sensors.md) -- Sensor management endpoints
- [Raspberry Pi Deployment](../deployment/raspberry-pi.md) -- Deploy sensors on RPi
- [High Availability](../enterprise/high-availability.md) -- HA central deployment
