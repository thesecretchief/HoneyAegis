# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.4.x   | Yes                |
| < 0.4   | No                 |

## Reporting a Vulnerability

If you discover a security vulnerability in HoneyAegis, please report it responsibly.

**DO NOT** open a public GitHub issue for security vulnerabilities.

### How to Report

1. Email: security@honeyaegis.local (or open a private security advisory on GitHub)
2. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We aim to acknowledge reports within **48 hours** and provide a fix within **7 days** for critical issues.

## Security Architecture

### Container Isolation

- All containers run as **non-root users**
- Docker network namespaces isolate honeypot traffic from management traffic
- Honeypot containers have no access to the host filesystem beyond mounted log volumes
- The backend container cannot reach the internet (except for GeoIP lookups)

### Network Security

```
Internet → Traefik (TLS) → Frontend / API
                          → Honeypots (isolated network)

┌─────────────────────────────────────────┐
│ honeyaegis_frontend (public)            │
│   - Traefik reverse proxy               │
│   - Next.js dashboard                   │
│   - FastAPI backend                     │
├─────────────────────────────────────────┤
│ honeyaegis_backend (internal)           │
│   - PostgreSQL                          │
│   - Redis                               │
│   - Ollama (optional)                   │
├─────────────────────────────────────────┤
│ honeyaegis_honeypot (isolated)          │
│   - Cowrie SSH/Telnet                   │
│   - OpenCanary                          │
│   - Dionaea                             │
│   - Beelzebub                           │
└─────────────────────────────────────────┘
```

### Authentication & Authorization

- **JWT tokens** with configurable expiry (default: 8 hours)
- **bcrypt** password hashing (12 rounds)
- **Multi-tenant isolation**: Every data query is scoped by `tenant_id`
- **Role-based access**: Superuser vs. tenant admin vs. client portal (view-only)
- **Rate limiting**: Login endpoint rate-limited to prevent brute force

### Multi-Tenant Security

- All database tables include a `tenant_id` foreign key
- FastAPI dependency injection enforces tenant scoping on every API endpoint
- Cross-tenant data access is prevented at the query level
- Client portals provide view-only access (no configuration, no passwords exposed)
- Tenant isolation is tested with dedicated test cases

### Data Security

- **Passwords**: Attacker passwords captured by honeypots are stored in the database but excluded from client portal responses and reports
- **Secrets**: All secrets (database passwords, JWT secrets, API keys) are managed via environment variables, never committed to code
- **TLS**: Traefik provides automatic HTTPS via Let's Encrypt in production
- **.env files**: Excluded from git via `.gitignore`

### Honeypot Safety

- Honeypots are designed to be **sacrificial** — they emulate vulnerable services
- Attacker-uploaded files are stored in isolated volumes
- No real services are exposed; all interactions are simulated
- Cowrie's fake filesystem prevents actual file system access
- Downloaded malware samples are quarantined and hashed (SHA-256)

## Security Checklist for Deployment

- [ ] Change all default passwords in `.env`
- [ ] Enable HTTPS via Traefik (set `TRAEFIK_ACME_EMAIL`)
- [ ] Place honeypots on a DMZ or isolated VLAN
- [ ] Monitor honeypot container resource usage
- [ ] Enable alert notifications (email/Slack/Discord)
- [ ] Regularly pull updates (`./scripts/update.sh`)
- [ ] Back up the PostgreSQL database regularly
- [ ] Review captured sessions for signs of targeted attacks
- [ ] Restrict dashboard access to trusted IPs if possible

## Dependencies

HoneyAegis uses pinned dependency versions where possible. Key dependencies:

- **Python**: FastAPI, SQLAlchemy, Pydantic, WeasyPrint
- **Node.js**: Next.js, React, Tailwind CSS
- **Infrastructure**: PostgreSQL 16, Redis 7, Docker

All Docker images are pulled from official sources. We recommend running `docker compose pull` regularly to get security patches.
