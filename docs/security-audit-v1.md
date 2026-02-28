# HoneyAegis v1.0.0 Security Audit Checklist

Pre-release security review for HoneyAegis v1.0.0.

## Authentication & Authorization

- [x] JWT tokens with HS256 signing and configurable expiry
- [x] bcrypt password hashing (12 rounds) via passlib
- [x] Rate limiting on auth endpoints (10 req/s per IP)
- [x] Token invalidation on password change
- [x] Tenant-scoped JWT claims for multi-tenant isolation
- [x] Superuser-only routes for admin operations

## Input Validation

- [x] Pydantic schemas validate all API input
- [x] SQL injection prevented via SQLAlchemy parameterized queries
- [x] Path traversal prevented (UUID-based resource access)
- [x] Query parameter validation (limit, offset, format)
- [x] File upload restricted to expected types (downloads only)

## Network Security

- [x] Non-root containers (USER honeyaegis / USER nextjs)
- [x] Read-only filesystem on Cowrie container
- [x] Isolated Docker networks (internal vs honeypot)
- [x] Ports bound to 127.0.0.1 for internal services
- [x] cap_drop: ALL + cap_add: NET_BIND_SERVICE on Cowrie
- [x] No host network mode
- [x] Traefik TLS termination with Let's Encrypt (full profile)

## Data Protection

- [x] Secrets via environment variables (never hardcoded)
- [x] PostgreSQL credentials randomized by installer
- [x] Redis AUTH enabled with password
- [x] No PII stored beyond attacker IPs (which are public threat intel)
- [x] Audit logging for all security-relevant actions

## SIEM & Monitoring

- [x] Structured JSON audit logs
- [x] CEF and Syslog export for enterprise SIEMs
- [x] Prometheus metrics endpoint
- [x] Grafana dashboards for operational monitoring

## CI/CD Security

- [x] Bandit SAST scanning (Python) — fail on HIGH/CRITICAL
- [x] Trivy container scanning — informational for base image, fail for app code
- [x] npm audit — fail on CRITICAL
- [x] Dependency pinning in requirements.txt and package-lock.json

## Container Security

- [x] Multi-stage builds (frontend)
- [x] Minimal base images (python:3.12-slim, node:22-alpine)
- [x] No secrets in Docker images
- [x] .dockerignore excludes sensitive files
- [x] Resource limits in docker-compose (Redis maxmemory 256MB)

## Known Limitations

| Issue | Severity | Mitigation |
|-------|----------|------------|
| JWT HS256 (symmetric) | Low | Acceptable for single-deployment; HSA256 is standard |
| In-memory rate limiting | Low | Resets on restart; Redis-backed option for production scale |
| No CSRF protection | Low | API is token-based (no cookies), CSRF not applicable |
| No request body size limit | Medium | Add in Traefik/nginx reverse proxy |
| GeoIP data accuracy | Info | Uses MaxMind GeoLite2 (free tier accuracy) |

## Recommendations for Production

1. **Always deploy behind a reverse proxy** (Traefik, nginx) with TLS
2. **Rotate JWT secrets** periodically (change JWT_SECRET_KEY in .env)
3. **Use the full profile** for monitoring (Prometheus + Grafana)
4. **Enable audit logging** and export to your SIEM
5. **Keep images updated** — run `./scripts/update.sh` regularly
6. **Isolate the honeypot network** — never share VLANs with production
7. **Monitor disk usage** — session recordings can grow large over time
