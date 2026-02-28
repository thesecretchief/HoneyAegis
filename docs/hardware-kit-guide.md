# HoneyAegis Hardware Kit Guide

Pre-built Raspberry Pi sensor kits and white-label MSP packaging for HoneyAegis.

## Kit Options

### Kit A — RPi Sensor Node ($89 BOM)

| Component | Specification | Est. Cost |
|-----------|---------------|-----------|
| Raspberry Pi 4 Model B | 4 GB RAM | $55 |
| MicroSD Card | 32 GB A2 (SanDisk Extreme) | $10 |
| USB-C Power Supply | 5V 3A (official RPi PSU) | $8 |
| Ethernet Cable | Cat6 1m | $3 |
| Case | Official RPi 4 case (passive cooling) | $8 |
| Label | HoneyAegis sticker (optional) | $5 |

### Kit B — RPi 5 Sensor Node ($119 BOM)

| Component | Specification | Est. Cost |
|-----------|---------------|-----------|
| Raspberry Pi 5 | 4 GB RAM | $60 |
| MicroSD Card | 64 GB A2 | $12 |
| USB-C Power Supply | 5V 5A (official RPi 5 PSU) | $12 |
| Active Cooler | Official RPi 5 cooler | $5 |
| Ethernet Cable | Cat6 1m | $3 |
| Case | Argon ONE V3 (passive + fan) | $20 |
| Label | HoneyAegis branded sticker | $7 |

### Kit C — Enterprise Appliance ($249 BOM)

| Component | Specification | Est. Cost |
|-----------|---------------|-----------|
| Intel N100 Mini PC | 8 GB RAM, 256 GB NVMe | $180 |
| Ethernet Cable | Cat6 2m | $4 |
| Power Adapter | 12V barrel (included) | $0 |
| USB Drive | 16 GB recovery/install USB | $8 |
| Case Label | HoneyAegis branded sticker | $7 |
| Quick Start Card | Printed setup instructions | $5 |
| Pelican-style Case | Hardened transport case | $45 |

## Assembly Guide — Kit A (RPi 4)

### Step 1: Flash the MicroSD Card

```bash
# Download the HoneyAegis RPi image (pre-configured)
wget https://github.com/thesecretchief/HoneyAegis/releases/latest/download/honeyaegis-rpi.img.xz

# Flash with Raspberry Pi Imager or balena Etcher
# OR use dd:
xz -d honeyaegis-rpi.img.xz
sudo dd if=honeyaegis-rpi.img of=/dev/sdX bs=4M status=progress
sync
```

Alternatively, use the one-click installer on a fresh Raspberry Pi OS:

```bash
curl -sSL https://raw.githubusercontent.com/thesecretchief/HoneyAegis/main/scripts/rpi-setup.sh | bash
```

### Step 2: Hardware Assembly

1. Insert the flashed MicroSD card into the RPi
2. Attach the RPi to the case (snap-fit for official case)
3. Connect the Ethernet cable to the RPi and your network switch
4. Connect the USB-C power supply (do NOT power on yet)
5. Apply the HoneyAegis sticker to the case lid (optional)

### Step 3: Network Setup

1. Connect the Ethernet cable to an isolated VLAN or DMZ port
2. Ensure the VLAN has internet access for Docker image pulls
3. Configure your firewall to allow:
   - **Inbound:** TCP 22, 23 (honeypot ports) from attacker-facing network
   - **Outbound:** TCP 443 (Docker Hub, GitHub), TCP 8000 (relay to hub)
   - **Block:** all other inbound traffic

### Step 4: First Boot

1. Plug in the USB-C power supply
2. Wait 2-3 minutes for first boot (Docker images download)
3. Find the RPi's IP address on your network:
   ```bash
   # From another machine on the same network
   nmap -sn 192.168.1.0/24 | grep -i raspberry
   ```
4. SSH into the RPi (default: `pi` / `raspberry`, change immediately):
   ```bash
   ssh pi@<rpi-ip>
   sudo passwd pi  # Change default password
   ```

### Step 5: Register with Hub

If running in hub-and-spoke mode:

```bash
# On the RPi sensor
cd /opt/honeyaegis
cat .env | grep SENSOR_ID  # Note the auto-generated sensor ID

# On your hub dashboard (Settings → Sensors → Register)
# Enter the sensor ID and the RPi's hostname
```

### Step 6: Verify

```bash
# Check services are running
docker compose ps

# Check honeypot is listening
ss -tlnp | grep -E ':(22|23)\s'

# Check logs
docker compose logs -f cowrie --tail 50
```

## White-Label MSP Packaging

### Branding Customization

MSPs can white-label the sensor kits for their clients:

1. **Case labels** — replace HoneyAegis branding with your MSP logo
2. **Dashboard branding** — set `display_name`, `logo_url`, `primary_color` per tenant
3. **Quick start cards** — customize printed instructions with your support contact

### Tenant Provisioning Script

```bash
#!/bin/bash
# provision-client.sh — Create a new MSP client tenant
# Usage: ./provision-client.sh <client-slug> <client-name> <admin-email>

CLIENT_SLUG="$1"
CLIENT_NAME="$2"
ADMIN_EMAIL="$3"

curl -X POST http://localhost:8000/api/v1/tenants/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"slug\": \"$CLIENT_SLUG\",
    \"name\": \"$CLIENT_NAME\",
    \"display_name\": \"$CLIENT_NAME\",
    \"primary_color\": \"#3b82f6\",
    \"is_active\": true
  }"

echo "Tenant created: $CLIENT_SLUG"
echo "Client portal: http://your-hub:3000/client/$CLIENT_SLUG"
```

### Bulk Sensor Registration

For deploying multiple sensors to a client site:

```bash
#!/bin/bash
# register-sensors.sh — Bulk register sensors for a client
# Usage: ./register-sensors.sh <tenant-id> <count>

TENANT_ID="$1"
COUNT="${2:-5}"

for i in $(seq 1 "$COUNT"); do
  SENSOR_ID="sensor-$(openssl rand -hex 4)"
  curl -X POST http://localhost:8000/api/v1/sensors/ \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"sensor_id\": \"$SENSOR_ID\",
      \"name\": \"Client Sensor $i\",
      \"tenant_id\": \"$TENANT_ID\"
    }"
  echo "Registered: $SENSOR_ID"
done
```

### Pricing Guidelines for MSPs

| Tier | Sensors | Monthly | Setup Fee |
|------|---------|---------|-----------|
| Starter | 1-5 | $49/mo | $199 |
| Professional | 6-25 | $149/mo | $499 |
| Enterprise | 26-100 | $399/mo | $999 |
| Unlimited | 100+ | Custom | Custom |

Pricing is a guideline — MSPs set their own rates. HoneyAegis is MIT-licensed and free forever.

## Pre-Built RPi Image

### Creating a Custom Image

For MSPs who want to distribute pre-flashed SD cards:

```bash
# 1. Start with a fresh Raspberry Pi OS Lite (64-bit)
# 2. Run the setup script
curl -sSL https://raw.githubusercontent.com/thesecretchief/HoneyAegis/main/scripts/rpi-setup.sh | bash

# 3. Clean up for imaging
sudo apt clean
sudo rm -rf /tmp/* /var/tmp/*
history -c

# 4. Shut down and create image from the SD card
sudo shutdown -h now
# On your workstation:
sudo dd if=/dev/sdX of=honeyaegis-rpi.img bs=4M status=progress
xz -9 honeyaegis-rpi.img
```

### Image Contents

The pre-built image includes:

- Raspberry Pi OS Lite (64-bit, Bookworm)
- Docker Engine + Docker Compose v2
- HoneyAegis repository cloned to `/opt/honeyaegis`
- Docker images pre-pulled (backend, frontend, cowrie, postgres, redis)
- Systemd service for auto-start on boot
- SSH enabled with password authentication (change on first login)
- Swap configured (1 GB) for stability on 2 GB models

## Troubleshooting

### Sensor won't connect to hub

1. Check network connectivity: `ping <hub-ip>`
2. Verify relay is enabled on hub: `curl http://<hub-ip>:8000/api/v1/relay/status`
3. Check sensor token: `cat /opt/honeyaegis/.env | grep RELAY_TOKEN`
4. Review logs: `docker compose logs backend --tail 100`

### High CPU on RPi

1. Check if Ollama is running (disable for RPi): `OLLAMA_ENABLED=false`
2. Monitor: `docker stats`
3. Reduce log verbosity: `HONEYAEGIS_DEBUG=false`

### SD card corruption

1. Use A2-rated cards (SanDisk Extreme recommended)
2. Enable read-only filesystem: add `ro` to `/etc/fstab` for `/`
3. Use tmpfs for logs: already configured in the pre-built image
4. Schedule regular backups: `scripts/backup-sensor.sh`
