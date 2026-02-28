# HoneyAegis Deployment Matrix

Choose the deployment method that fits your infrastructure.

## Quick Comparison

| Method | Complexity | RAM (Light) | RAM (Full) | Best For |
|--------|-----------|-------------|------------|----------|
| Docker Compose | Low | 2 GB | 4+ GB | Homelab, VPS, single server |
| Kubernetes/Helm | Medium | 3 GB | 6+ GB | Cloud, enterprise, auto-scaling |
| Raspberry Pi | Low | 2 GB | N/A | Edge sensors, portable deployments |
| Proxmox LXC | Medium | 2 GB | 4+ GB | Homelab with VM isolation |
| Bare Metal | High | 2 GB | 4+ GB | Maximum performance, custom setups |

---

## 1. Docker Compose (Recommended)

**Best for:** Most deployments. Simple, reliable, single-command deploy.

### Light Profile (default)

```bash
git clone https://github.com/thesecretchief/HoneyAegis.git
cd HoneyAegis
cp .env.example .env
# Edit .env with your settings
docker compose up -d
```

**Services:** PostgreSQL, Redis, Cowrie, Backend, Frontend, Worker

### Full Profile

```bash
OLLAMA_ENABLED=true docker compose --profile full up -d
```

**Additional services:** Ollama (AI), Vector (logs), Traefik (TLS), Prometheus, Grafana

### Resource Limits

| Service | RAM | CPU (idle) |
|---------|-----|------------|
| PostgreSQL | ~150 MB | 2% |
| Redis | ~30 MB | 1% |
| Cowrie | ~120 MB | 5% |
| Backend | ~180 MB | 3% |
| Frontend | ~100 MB | 1% |
| Worker | ~120 MB | 2% |
| **Total (light)** | **~700 MB** | **~14%** |

---

## 2. Kubernetes / Helm

**Best for:** Enterprise, cloud deployments, auto-scaling.

### Prerequisites

- Kubernetes 1.28+
- Helm 3.12+
- kubectl configured
- cert-manager (for TLS)

### Deploy

```bash
helm install honeyaegis ./helm/honeyaegis \
  --namespace honeyaegis \
  --create-namespace \
  --set backend.env.ADMIN_PASSWORD=your-secure-password \
  --set secrets.postgresPassword=your-db-password \
  --set secrets.redisPassword=your-redis-password \
  --set secrets.jwtSecret=$(openssl rand -hex 32)
```

### Custom Values

```yaml
# values-production.yaml
backend:
  replicas: 2
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"

ingress:
  enabled: true
  host: honeyaegis.example.com
  tls: true
  certManager: true
```

```bash
helm install honeyaegis ./helm/honeyaegis -f values-production.yaml
```

---

## 3. Raspberry Pi

**Best for:** Edge sensors, portable honeypots, physical network deployment.

### One-Click Setup

```bash
curl -sSL https://raw.githubusercontent.com/thesecretchief/HoneyAegis/main/scripts/rpi-setup.sh | bash
```

### Manual Setup

See [RPi Blueprint](rpi-blueprint.md) for full hardware guide.

### Supported Hardware

| Board | RAM | Status |
|-------|-----|--------|
| RPi 5 (4GB+) | 4 GB | Full support |
| RPi 5 (2GB) | 2 GB | Light profile only |
| RPi 4 (4GB+) | 4 GB | Full support |
| RPi 4 (2GB) | 2 GB | Light profile only |
| RPi 4 (1GB) | 1 GB | Not recommended |

---

## 4. Proxmox LXC Container

**Best for:** Homelab with VM-level isolation, Proxmox users.

### Create LXC

```bash
# In Proxmox shell or API
pct create 200 local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst \
  --hostname honeyaegis \
  --memory 2048 \
  --swap 1024 \
  --cores 2 \
  --rootfs local-lvm:16 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --features nesting=1 \
  --unprivileged 1

pct start 200
pct enter 200
```

### Inside LXC

```bash
apt update && apt install -y curl git
curl -fsSL https://get.docker.com | sh
git clone https://github.com/thesecretchief/HoneyAegis.git
cd HoneyAegis
cp .env.example .env
docker compose up -d
```

### Notes

- Enable **nesting** in LXC features for Docker support
- Use **unprivileged** containers for security
- Allocate at least 16 GB disk for logs and database

---

## 5. Bare Metal

**Best for:** Maximum performance, custom hardware, airgapped environments.

### Prerequisites

- Ubuntu 22.04+ or Debian 12+
- Python 3.12+
- Node.js 22+
- PostgreSQL 16 with TimescaleDB
- Redis 7

### Install

```bash
# System dependencies
sudo apt install -y python3.12 python3.12-venv python3-pip nodejs npm \
  postgresql-16 redis-server ffmpeg

# TimescaleDB
sudo apt install -y timescaledb-2-postgresql-16

# Clone project
git clone https://github.com/thesecretchief/HoneyAegis.git
cd HoneyAegis

# Backend
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Apply migrations
psql -U honeyaegis -d honeyaegis -f ../db/migrations/001_init.sql

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2

# Frontend (separate terminal)
cd ../frontend
npm ci
npm run build
npm start

# Cowrie (separate terminal)
docker run -d --name cowrie \
  -p 2222:2222 -p 2223:2223 \
  cowrie/cowrie:latest
```

### systemd Service

```ini
# /etc/systemd/system/honeyaegis-backend.service
[Unit]
Description=HoneyAegis Backend
After=postgresql.service redis.service

[Service]
Type=simple
User=honeyaegis
WorkingDirectory=/opt/HoneyAegis/backend
ExecStart=/opt/HoneyAegis/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## Network Architecture

All deployments should follow this network isolation pattern:

```
Internet
    │
    ▼
[Firewall / Router]
    │
    ├── VLAN 10: Production ──── Real servers (ISOLATED)
    │
    ├── VLAN 20: Management ──── HoneyAegis Dashboard (port 3000)
    │                            HoneyAegis API (port 8000)
    │
    └── VLAN 30: Honeypot ────── Cowrie SSH (port 2222)
                                 Cowrie Telnet (port 2223)
```

### Firewall Rules

| Source | Destination | Port | Action |
|--------|-------------|------|--------|
| Internet | VLAN 30 | 22, 23 | ALLOW (forwarded to 2222/2223) |
| VLAN 30 | Internet | * | DENY (block outbound) |
| VLAN 20 | VLAN 30 | 2222, 2223 | ALLOW |
| Admin | VLAN 20 | 3000, 8000 | ALLOW |
| VLAN 30 | VLAN 20 | 8000 | ALLOW (log shipping) |

---

## Upgrading

### Docker Compose

```bash
cd HoneyAegis
./scripts/update.sh
```

### Kubernetes

```bash
helm upgrade honeyaegis ./helm/honeyaegis --namespace honeyaegis
```

### Manual

```bash
cd HoneyAegis
git pull origin main
cd backend && pip install -r requirements.txt
cd ../frontend && npm ci && npm run build
# Restart services
```
