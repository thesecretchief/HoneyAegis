# Docker Compose Deployment

Docker Compose is the recommended deployment method for HoneyAegis. It provides a one-command setup with configurable profiles for different resource budgets.

## Prerequisites

- Docker Engine 24+ and Docker Compose v2
- Linux host (Ubuntu 22.04+, Debian 12+, or compatible)
- 2 GB RAM minimum (light profile) / 4 GB+ (full profile)
- 10 GB+ free disk space

## Light Profile (Default)

The light profile runs Cowrie, the FastAPI backend, Next.js frontend, PostgreSQL, and Redis:

```bash
git clone https://github.com/thesecretchief/HoneyAegis.git
cd HoneyAegis
cp .env.example .env

# Edit .env with secure passwords
nano .env

docker compose up -d
```

**Resource requirements:** 2 GB RAM, 10 GB disk.

## Full Profile

The full profile adds Ollama (AI), Vector (log shipping), Traefik (reverse proxy), Prometheus, and Grafana:

```bash
docker compose --profile full up -d
```

**Resource requirements:** 4 GB+ RAM, 20 GB disk.

## High Availability Profile

Add Redis Sentinel and PostgreSQL replication for production resilience:

```bash
docker compose -f docker-compose.yml \
  -f configs/ha/docker-compose.ha.yml \
  --profile full up -d
```

See [High Availability](../enterprise/high-availability.md) for details.

## TLS with Traefik

The full profile includes Traefik for automatic TLS certificates via Let's Encrypt:

```bash
# Set your domain in .env
TRAEFIK_DOMAIN=honeyaegis.example.com
TRAEFIK_ACME_EMAIL=admin@example.com

docker compose --profile full up -d
```

The dashboard will be available at `https://honeyaegis.example.com`.

## Updating

```bash
# Pull latest images and restart
docker compose pull
docker compose up -d

# Check that all services are healthy
docker compose ps
```

## Useful Commands

```bash
docker compose ps                    # Check service status
docker compose logs -f backend       # Follow backend logs
docker compose logs -f cowrie        # Follow honeypot logs
docker compose exec backend bash     # Shell into backend container
docker compose down                  # Stop all services
docker compose down -v               # Stop and remove volumes (data loss!)
```

## Custom Docker Compose Overrides

For site-specific customizations, create a `docker-compose.override.yml`:

```yaml
services:
  backend:
    environment:
      - HONEYAEGIS_DEBUG=true
    ports:
      - "8000:8000"
  cowrie:
    ports:
      - "22:2222"    # Map real SSH port to honeypot
```

This file is automatically merged by Docker Compose and should not be committed to version control.

## Environment Variables

See [Configuration](../getting-started/configuration.md) for the full list of environment variables including database credentials, alert channels, AI settings, and feature flags.

## Related Pages

- [Quick Start](../getting-started/quick-start.md) -- Simplified first-run guide
- [Kubernetes Deployment](kubernetes.md) -- Helm chart for Kubernetes clusters
- [Raspberry Pi Deployment](raspberry-pi.md) -- Edge sensor on ARM64
- [Architecture Overview](../architecture/overview.md) -- Container roles and networking
