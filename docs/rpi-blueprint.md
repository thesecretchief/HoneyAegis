# Raspberry Pi Sensor Blueprint

Deploy HoneyAegis as a portable honeypot sensor on a Raspberry Pi 4/5.

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Board | RPi 4 (2GB) | RPi 5 (4GB) |
| Storage | 16 GB microSD | 32 GB+ microSD or SSD |
| Network | Ethernet (1 Gbps) | Ethernet + WiFi |
| Power | 5V 3A USB-C | Official RPi PSU |
| Case | Any | With heatsink + fan |

**Estimated cost:** $50-100 per sensor (RPi 4 kit)

## Quick Start

### 1. Flash the OS

Flash **Raspberry Pi OS Lite (64-bit)** to the microSD card using Raspberry Pi Imager.

Enable SSH in the imager settings (no desktop needed).

### 2. Initial Setup

```bash
# SSH into the Pi
ssh pi@raspberrypi.local

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker pi

# Reboot to apply group changes
sudo reboot
```

### 3. Deploy HoneyAegis Sensor (Light Profile)

```bash
# Clone and deploy
git clone https://github.com/thesecretchief/HoneyAegis.git
cd HoneyAegis

# Use the sensor-optimized compose file
cp .env.example .env
# Edit .env: set hub IP if using fleet mode

docker compose up -d postgres redis cowrie backend
```

### 4. Register as Fleet Sensor

On the hub (main server), register this Pi:

```bash
curl -X POST http://HUB_IP:8000/api/v1/sensors/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "rpi-office-01",
    "name": "Office RPi Honeypot",
    "hostname": "raspberrypi",
    "ip_address": "192.168.1.50"
  }'
```

## Network Placement

```
Internet
    │
    ▼
[Router/Firewall]
    │
    ├── VLAN 10: Production ──── Real servers
    │
    └── VLAN 20: Honeypot ───── RPi Sensor (HoneyAegis)
                                  ├── SSH :2222
                                  └── Telnet :2223
```

**Best practices:**
- Place the RPi on a dedicated VLAN
- Forward external ports 22/23 to the Pi's 2222/2223
- Block outbound internet from the Pi (except for updates)
- Monitor RPi CPU/memory via the dashboard

## Resource Usage (RPi 4, 2GB)

| Service | RAM | CPU |
|---------|-----|-----|
| Cowrie | ~120 MB | 5% idle |
| Backend (FastAPI) | ~180 MB | 3% idle |
| PostgreSQL | ~100 MB | 2% idle |
| Redis | ~30 MB | 1% idle |
| **Total** | **~430 MB** | **~11%** |

Leaves ~1.5 GB free on a 2 GB Pi. No AI (Ollama needs 4GB+).

## Pre-Built ARM64 Docker Images

HoneyAegis images are multi-arch (amd64 + arm64). No special build needed for RPi:

```bash
# These pull the correct arm64 images automatically
docker compose pull
docker compose up -d
```

## Auto-Start on Boot

Docker already configures auto-restart. To ensure Docker starts on boot:

```bash
sudo systemctl enable docker
```

## Monitoring

Check sensor status from the hub dashboard under **Sensors** tab. The RPi sends heartbeats every 60 seconds.

SSH into the Pi to check local status:

```bash
# Check container status
docker compose ps

# View Cowrie logs
docker compose logs cowrie --tail 50

# Check resource usage
docker stats --no-stream
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Containers won't start | Check `docker compose logs`, ensure SD card has space |
| No sessions appearing | Verify port forwarding to 2222/2223 |
| High CPU usage | Check if a real attacker is in a session (expected!) |
| SD card corruption | Use a high-endurance card, enable read-only root |
| Network timeout | Check VLAN config, ensure Pi can reach PostgreSQL |
