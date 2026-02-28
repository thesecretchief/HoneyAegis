# MSP Deployment Guide

This guide covers deploying HoneyAegis as a **Managed Security Service Provider (MSP)** with multi-tenant support, white-label branding, and client portals.

## Overview

HoneyAegis v0.4.0 introduces full multi-tenant support, enabling MSPs to:

- **Isolate client data** with tenant-scoped database queries
- **White-label the dashboard** with per-tenant branding (logo, colors, display name)
- **Provide client portals** for view-only access to incident data
- **Generate forensic reports** in PDF and JSON format per tenant
- **Manage sensor fleets** across multiple client sites

## Architecture

```
MSP Admin Dashboard (full access)
├── Tenant A: Acme Corp
│   ├── Sensors: office-ssh, dmz-cowrie
│   ├── Sessions, Alerts, Reports
│   └── Client Portal: /client/acme-corp
├── Tenant B: Globex Inc
│   ├── Sensors: hq-sensor-01
│   ├── Sessions, Alerts, Reports
│   └── Client Portal: /client/globex-inc
└── Tenant C: Initech
    ├── Sensors: branch-01, branch-02
    ├── Sessions, Alerts, Reports
    └── Client Portal: /client/initech
```

## Setup

### 1. Deploy HoneyAegis

```bash
# One-click install
curl -sSL https://raw.githubusercontent.com/thesecretchief/HoneyAegis/main/scripts/install.sh | bash

# Or manual
git clone https://github.com/thesecretchief/HoneyAegis.git
cd HoneyAegis
cp .env.example .env
# Edit .env with secure passwords
docker compose up -d
```

### 2. Create Tenants

Log in as the superuser admin, then use the API to create tenants:

```bash
# Get auth token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@honeyaegis.local&password=YOUR_PASSWORD" \
  | jq -r '.access_token')

# Create a tenant
curl -X POST http://localhost:8000/api/v1/tenants/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "acme-corp",
    "name": "Acme Corporation",
    "display_name": "Acme Security",
    "primary_color": "#2563eb",
    "logo_url": "https://example.com/acme-logo.png"
  }'
```

### 3. Configure White-Label Branding

Each tenant can have custom branding that appears in:
- The client portal header
- PDF forensic reports
- Email alert templates

```bash
# Update tenant branding
curl -X PATCH http://localhost:8000/api/v1/tenants/{tenant_id} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Acme Security Operations",
    "primary_color": "#2563eb",
    "logo_url": "https://example.com/acme-logo.png"
  }'
```

Branding fields:
| Field | Description | Example |
|-------|-------------|---------|
| `display_name` | Name shown in portal header | "Acme Security" |
| `primary_color` | Hex color for accents | "#2563eb" |
| `logo_url` | URL to logo image (PNG/SVG) | "https://..." |
| `portal_domain` | Custom subdomain (future) | "acme.honeyaegis.io" |

### 4. Register Sensors Per Tenant

Deploy honeypot sensors at each client site and register them:

```bash
# Register a sensor for Acme Corp (use Acme admin's token)
curl -X POST http://localhost:8000/api/v1/sensors/register \
  -H "Authorization: Bearer $ACME_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "acme-office-ssh",
    "name": "Acme Office SSH Honeypot",
    "hostname": "honeypot-01.acme.local",
    "ip_address": "10.0.1.50"
  }'
```

Sensors automatically heartbeat every 60 seconds. Sessions from each sensor are tagged with the sensor's tenant, ensuring data isolation.

### 5. Set Up Client Portals

Client portals are automatically available at:
```
http://your-server:3000/client/{tenant-slug}
```

For example:
- `http://localhost:3000/client/acme-corp`
- `http://localhost:3000/client/globex-inc`

Client portals provide:
- **View-only** access to session data
- Attack statistics and trends
- No access to passwords, configuration, or other tenants' data

No login is required for client portals — they are identified by tenant slug and only show that tenant's data.

### 6. Generate Reports

Generate forensic reports for client meetings:

```bash
# Aggregate PDF report for a tenant
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/reports/pdf" \
  -o report.pdf

# Single session PDF report
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/reports/pdf?session_id=SESSION_UUID" \
  -o session-report.pdf

# JSON report
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/reports/json" \
  -o report.json
```

PDF reports include:
- Session metadata (IP, protocol, location, duration)
- Commands executed by the attacker
- AI threat analysis (if Ollama is enabled)
- MITRE ATT&CK technique mapping
- Tenant branding in the header

## Tenant Isolation

### How It Works

Every database table that stores tenant-specific data includes a `tenant_id` column:

| Table | Tenant Scoped |
|-------|:------------:|
| `tenants` | N/A (root table) |
| `users` | Yes |
| `sessions` | Yes |
| `sensors` | Yes |
| `alerts` | Yes |
| `events` | Via session |
| `commands` | Via session |
| `downloads` | Via session |
| `ai_summaries` | Via session |
| `geoip_cache` | No (shared) |

### Enforcement

Tenant isolation is enforced at two levels:

1. **FastAPI Dependency Injection**: Every authenticated endpoint uses `get_tenant_id()` which extracts the tenant from the JWT token
2. **Database Queries**: Every SELECT, UPDATE, and DELETE query includes `.where(tenant_id == tenant_id)` filtering

### Testing Isolation

To verify tenant isolation:

```python
# Test: User from Tenant A cannot see Tenant B's sessions
response = client.get("/api/v1/sessions/", headers=tenant_a_headers)
for session in response.json()["sessions"]:
    assert session["tenant_id"] == tenant_a_id

# Test: Cross-tenant sensor registration is rejected
response = client.post("/api/v1/sensors/register",
    headers=tenant_b_headers,
    json={"sensor_id": "acme-sensor-01", ...})  # owned by Tenant A
assert response.status_code == 403
```

## Auto-Updates

Keep your MSP deployment up to date:

```bash
# Manual update
./scripts/update.sh

# Automatic updates via cron (check daily at 3 AM)
echo "0 3 * * * cd /path/to/HoneyAegis && ./scripts/update.sh --auto >> /var/log/honeyaegis-update.log 2>&1" | crontab -

# Check current version
git rev-parse --short HEAD
```

## Scaling

### Multiple Honeypot Profiles

| Profile | RAM | Use Case |
|---------|-----|----------|
| Light (default) | < 4 GB | Single client, basic SSH monitoring |
| Full | 6-8 GB | Multi-client, AI summaries, all honeypots |

### Resource Planning

| Clients | Sensors | Recommended RAM | Recommended CPU |
|---------|---------|----------------|-----------------|
| 1-5 | 1-10 | 4 GB | 2 cores |
| 5-20 | 10-50 | 8 GB | 4 cores |
| 20-50 | 50-100 | 16 GB | 8 cores |

### Database Maintenance

For high-volume deployments, consider:

```sql
-- Archive sessions older than 90 days
DELETE FROM sessions WHERE started_at < NOW() - INTERVAL '90 days';

-- Vacuum after large deletes
VACUUM ANALYZE sessions;
```

## Support

- GitHub Issues: https://github.com/thesecretchief/HoneyAegis/issues
- Security Issues: See [SECURITY.md](../SECURITY.md)
