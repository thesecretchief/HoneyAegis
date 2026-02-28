# Security Model

HoneyAegis is designed to be deployed on internet-facing infrastructure. Security is enforced at every layer through container isolation, network segmentation, and least-privilege defaults.

## Principles

1. **Defense in depth** -- Multiple independent security controls at each layer.
2. **Least privilege** -- Every container runs as a non-root user with minimal capabilities.
3. **Network isolation** -- Honeypots cannot reach the database, frontend, or the internet.
4. **No secrets in code** -- All credentials are injected via environment variables at runtime.

## Container Hardening

All HoneyAegis containers follow these security practices:

```yaml
# Applied to every service in docker-compose.yml
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
read_only: true
tmpfs:
  - /tmp
```

| Control | Description |
|---|---|
| Non-root user | All containers run as UID 1000+ |
| Read-only filesystem | Writable only via explicit `tmpfs` or volume mounts |
| No new privileges | Prevents privilege escalation via `setuid` binaries |
| Dropped capabilities | All Linux capabilities dropped; only required ones added back |
| Resource limits | CPU and memory limits set per container |

## Network Segmentation

```
┌───────────────────────────────────┐
│         frontend_net              │
│   Frontend ◄──► Traefik          │
│       │                          │
├───────┼──────────────────────────┤
│       ▼     backend_net          │
│   Backend ◄──► PostgreSQL        │
│       │    ◄──► Redis            │
│       │    ◄──► Celery           │
├───────┼──────────────────────────┤
│       ▼     honeypot_net         │
│   Cowrie    OpenCanary           │
│   Dionaea   Beelzebub            │
│   (no internet, no DB access)    │
└───────────────────────────────────┘
```

- **`honeypot_net`** is fully isolated. Honeypot containers have no route to the internet or to internal services. The backend mounts their log volumes read-only.
- **`backend_net`** hosts the API, database, and workers. Not exposed to the public internet.
- **`frontend_net`** is the only network with public-facing ports (80/443 via Traefik).

## Authentication and Authorization

- **JWT tokens** with configurable expiry (default 30 minutes).
- **Role-Based Access Control (RBAC)** with four roles: Super Admin, Admin, Analyst, Viewer.
- **Rate limiting** on all API endpoints (token bucket algorithm).
- **CORS** restricted to configured origins in production.

See [Authentication API](../api/authentication.md) and [RBAC](../enterprise/rbac.md) for details.

## Rate Limiting

The API enforces rate limits using a token bucket algorithm backed by Redis:

| Endpoint Group | Burst | Sustained |
|---|---|---|
| Global | 100 req | 50 req/s |
| Authentication | 10 req | 5 req/s |
| Ingest | 500 req | 200 req/s |
| Export | 20 req | 10 req/s |

## Secrets Management

| Secret | Source | Notes |
|---|---|---|
| `JWT_SECRET_KEY` | `.env` file | 64+ character random string |
| `POSTGRES_PASSWORD` | `.env` file | Never committed to version control |
| `REDIS_PASSWORD` | `.env` file | Optional but recommended |
| API keys (TI feeds) | `.env` file | AbuseIPDB, OTX, MISP, VirusTotal |

!!! warning "Production Checklist"
    - Change all default passwords before deploying to the internet
    - Enable TLS via Traefik or an external reverse proxy
    - Restrict dashboard access to your management network
    - Regularly update container images for security patches

## Honeypot Escape Prevention

Honeypot containers are sandboxed to prevent an attacker from pivoting:

- No outbound network access from `honeypot_net`
- `seccomp` and `AppArmor` profiles applied where available
- File system is read-only except for designated log directories
- No access to Docker socket or host namespace

## Related Pages

- [Architecture Overview](overview.md) -- Component layout
- [RBAC](../enterprise/rbac.md) -- Role-based access control details
- [Authentication API](../api/authentication.md) -- JWT token management
