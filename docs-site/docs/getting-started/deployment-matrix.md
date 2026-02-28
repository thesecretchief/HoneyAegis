# Deployment Matrix

HoneyAegis supports multiple deployment targets.

## Comparison

| Target | RAM | Difficulty | Use Case |
|---|---|---|---|
| Docker Compose (light) | 2 GB | Easy | Homelab, VPS |
| Docker Compose (full) | 4 GB | Easy | Production with AI + monitoring |
| Kubernetes / Helm | 4 GB+ | Medium | Cloud / enterprise |
| Raspberry Pi | 2 GB | Easy | Edge sensor |
| Bare Metal | 2 GB | Hard | Custom deployments |

## Docker Compose

See the [Quick Start](quick-start.md) guide.

## Kubernetes / Helm

```bash
helm install honeyaegis ./helm/honeyaegis \
    --namespace honeyaegis --create-namespace \
    --set backend.env.POSTGRES_PASSWORD=secure \
    --set backend.env.JWT_SECRET_KEY=random-64-chars
```

## Raspberry Pi

```bash
curl -sSL https://raw.githubusercontent.com/thesecretchief/HoneyAegis/main/scripts/rpi-setup.sh | bash
```

See [Raspberry Pi Deployment](../deployment/raspberry-pi.md) for the full guide.

## High Availability

For HA deployments with Redis Sentinel and PostgreSQL replication:

```bash
docker compose -f docker-compose.yml \
    -f configs/ha/docker-compose.ha.yml \
    --profile full up -d
```

See [High Availability](../enterprise/high-availability.md) for details.
