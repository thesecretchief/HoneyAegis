# Quick Start

Get HoneyAegis running in under 5 minutes.

## Prerequisites

- Docker Engine 24+ and Docker Compose v2
- 2 GB RAM minimum (light profile) / 4 GB+ recommended (full profile)
- Linux host (Ubuntu 22.04+, Debian 12+, or compatible)

## Step 1: Clone and Configure

```bash
git clone https://github.com/thesecretchief/HoneyAegis.git
cd HoneyAegis
cp .env.example .env
```

Edit `.env` with your settings — at minimum, change the default passwords:

```bash
POSTGRES_PASSWORD=your-secure-password
REDIS_PASSWORD=your-secure-password
JWT_SECRET_KEY=your-random-64-char-string
ADMIN_PASSWORD=your-admin-password
```

## Step 2: Deploy (Light Profile)

The light profile runs Cowrie (SSH/Telnet honeypot), PostgreSQL, Redis, and the dashboard:

```bash
docker compose up -d
```

## Step 3: Deploy (Full Profile)

The full profile adds Ollama (AI), Vector (log shipping), Prometheus + Grafana (monitoring), and Traefik (reverse proxy):

```bash
OLLAMA_ENABLED=true docker compose --profile full up -d
```

!!! note "RAM Requirements"
    The full profile with Ollama requires **4 GB+ RAM**. The phi3:mini model uses ~1.5 GB during inference.

## Step 4: Verify

```bash
docker compose ps   # all services should show "Up (healthy)"
```

## Step 5: Access Dashboard

Open `http://your-server:3000` in your browser.
Default credentials: `admin` / `changeme` (change immediately).

!!! warning "Security"
    Never expose honeypot ports (22/23) on production servers. Deploy on an isolated network segment.

## Next Steps

- [Configuration Guide](configuration.md) — customize alerts, AI, fleet mode
- [Deployment Matrix](deployment-matrix.md) — Docker, Kubernetes, Raspberry Pi, Bare Metal
- [Plugin Marketplace](../plugins/marketplace.md) — extend with community plugins
