# Raspberry Pi Deployment

Deploy HoneyAegis as a standalone honeypot or edge sensor on a Raspberry Pi. The ARM64 images are optimized for low-power operation.

## Requirements

- Raspberry Pi 4 or 5 (2 GB+ RAM)
- 16 GB+ microSD card (32 GB recommended)
- ARM64 OS: Raspberry Pi OS 64-bit or Ubuntu Server 22.04+
- Wired Ethernet connection (recommended)
- Power supply appropriate for your Pi model

## One-Click Setup

The automated setup script handles Docker installation, configuration, and initial deployment:

```bash
curl -sSL https://raw.githubusercontent.com/thesecretchief/HoneyAegis/main/scripts/rpi-setup.sh | bash
```

The script will:

1. Detect ARM64 architecture and verify hardware compatibility
2. Install Docker Engine and Docker Compose
3. Clone HoneyAegis and generate secure random passwords
4. Configure swap (1 GB) for stability
5. Start the light profile
6. Display the dashboard URL and credentials

## Manual Setup

If you prefer manual installation:

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# Configure swap (recommended for 2 GB models)
sudo dphys-swapfile swapoff
echo "CONF_SWAPSIZE=1024" | sudo tee /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Clone and deploy
git clone https://github.com/thesecretchief/HoneyAegis.git
cd HoneyAegis
cp .env.example .env
nano .env  # Set secure passwords
docker compose up -d
```

## Resource Usage

| Component | RAM | CPU |
|---|---|---|
| PostgreSQL | ~120 MB | Low |
| Redis | ~30 MB | Minimal |
| Backend (FastAPI) | ~150 MB | Low |
| Frontend (Next.js) | ~80 MB | Low |
| Cowrie | ~60 MB | Low |
| **Total** | **~440 MB** | -- |

!!! note
    On a 2 GB Raspberry Pi, the light profile leaves approximately 1.5 GB free for the OS and file cache. Ollama (AI) is not recommended on 2 GB models.

## Fleet Integration

Register the Raspberry Pi as a remote sensor reporting to a central HoneyAegis hub:

```bash
# On the central hub, create a sensor token
curl -X POST http://hub:8000/api/v1/sensors \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "rpi-office-01", "location": "Office reception"}'

# On the Raspberry Pi, configure as sensor
cat >> .env <<EOF
FLEET_MODE=sensor
CENTRAL_URL=https://honeyaegis.example.com
SENSOR_TOKEN=your-sensor-token
EOF

docker compose restart backend
```

See [Fleet Management](../features/fleet-management.md) for full fleet setup.

## Performance Tuning

```bash
# Reduce PostgreSQL memory usage for 2 GB models
echo "POSTGRES_SHARED_BUFFERS=64MB" >> .env
echo "POSTGRES_WORK_MEM=2MB" >> .env

# Disable AI analysis (saves ~1.5 GB)
echo "OLLAMA_ENABLED=false" >> .env
```

## Recommendations

- Use a wired Ethernet connection for reliability
- Place the sensor on an isolated VLAN or DMZ
- Enable Docker auto-start: `sudo systemctl enable docker`
- Use a high-endurance microSD card (A2 rated)
- Set up log rotation to prevent SD card wear
- Consider USB SSD boot for better I/O and longevity

## Related Pages

- [Hardware Kits](hardware-kits.md) -- Pre-configured hardware bundles
- [Fleet Management](../features/fleet-management.md) -- Central sensor management
- [Docker Compose Deployment](docker-compose.md) -- Full deployment reference
- [Sensors API](../api/sensors.md) -- Sensor registration endpoints
