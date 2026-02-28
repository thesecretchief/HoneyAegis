# High Availability

HoneyAegis supports HA deployments for enterprise environments.

## Architecture

```
                    ┌──────────────┐
                    │   Traefik    │
                    │   (L7 LB)   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────┴─────┐ ┌───┴─────┐ ┌───┴──────┐
        │ Backend 1 │ │Backend 2│ │ Worker   │
        └─────┬─────┘ └───┬─────┘ └───┬──────┘
              │            │           │
    ┌─────────┴────────────┴───────────┴──────┐
    │                                          │
┌───┴────┐  ┌─────────────────┐  ┌────────────┴┐
│ Redis  │  │ Redis Sentinel  │  │ PostgreSQL  │
│Primary │  │  (3x quorum)    │  │  Primary    │
└────────┘  └─────────────────┘  └──────┬──────┘
                                        │
                                 ┌──────┴──────┐
                                 │ PostgreSQL  │
                                 │  Replica    │
                                 └─────────────┘
```

## Deploy HA Profile

```bash
docker compose -f docker-compose.yml \
    -f configs/ha/docker-compose.ha.yml \
    --profile full up -d
```

## Components

### Redis Sentinel (3-node)
- Automatic failover with 2-node quorum
- 5-second down-after-milliseconds
- 10-second failover timeout
- Password-protected sentinel monitoring

### PostgreSQL Streaming Replication
- Primary + read replica
- Replica available on port 5433
- Automatic health checks

### Celery Flower
- Task queue monitoring dashboard
- Available at `http://localhost:5555`
- Protected with basic auth (`FLOWER_USER` / `FLOWER_PASSWORD`)

## Requirements

- **8 GB+ RAM** for the full HA stack
- Full profile (`--profile full`) required
- Only for enterprise / production environments
