# HoneyAegis Roadmap

> Professional-grade, Docker-native honeypot platform.
> *"StingBox but 10x better and free forever."*

---

## Roadmap Overview

| Iteration 0: Foundation | Iteration 1: MVP | Iteration 2: Enhanced | Iteration 3: V1 MSP-Ready | Iteration 4+: Future |
|---|---|---|---|---|
| **Week 1** | **Weeks 2-4** | **Weeks 5-8** | **Weeks 9-12** | **Community-driven** |
| Repo skeleton | Full session capture | Ollama AI integration | Multi-tenant isolation | Kubernetes support |
| docker-compose.yml | Asciinema replay | LangChain threat summaries | White-label portals | Honey tokens |
| Light + full profiles | ttyrec -> MP4/GIF export | Session video + AI overlay | Client portals | Auto-block hooks |
| .env.example | Real-time dashboard | Config UI (services) | PDF/JSON forensic reports | Hardware blueprints |
| Cowrie container | Incidents list | Multi-sensor fleet | Auto-update system | Plugin marketplace |
| PostgreSQL + TimescaleDB | Live attack map | Registration flow | Full documentation | Community plugins |
| CI/CD (GitHub Actions) | Statistics panel | | One-click installer | |
| Multi-arch builds | Email + webhook alerts | | | |
| | GeoIP enrichment | | | |
| | AbuseIPDB enrichment | | | |

---

## Iteration 0: Foundation (Week 1) -- CURRENT

**Goal:** Establish the project skeleton, Docker orchestration, and core infrastructure.

### Deliverables

| # | Deliverable | Status |
|---|---|---|
| 0.1 | Repo skeleton with full directory structure | Done |
| 0.2 | `docker-compose.yml` with light + full profiles | Done |
| 0.3 | `.env.example` with all configuration variables | Done |
| 0.4 | Cowrie SSH/Telnet honeypot container + config | Done |
| 0.5 | PostgreSQL + TimescaleDB schema (sessions, events, commands, downloads) | Done |
| 0.6 | FastAPI backend skeleton (auth, sessions, events, health) | Done |
| 0.7 | Next.js 15 frontend skeleton (dashboard layout, stats cards) | Done |
| 0.8 | GitHub Actions CI/CD (tests, lint, multi-arch Docker builds) | Done |
| 0.9 | Vector log shipper + Traefik reverse proxy configs | Done |
| 0.10 | Setup script (`scripts/setup.sh`) for one-command deploy | Done |

### Tech Stack Established

- **Backend:** FastAPI (Python 3.12) + Celery + SQLAlchemy (async)
- **Frontend:** Next.js 15 + TypeScript + Tailwind CSS
- **Database:** PostgreSQL 16 + TimescaleDB + Redis 7
- **Honeypot:** Cowrie (SSH/Telnet with full tty recording)
- **CI/CD:** GitHub Actions with QEMU multi-arch (amd64/arm64)
- **Infra:** Docker Compose, Vector, Traefik

---

## Iteration 1: MVP -- "StingBox Killer Core" (Weeks 2-4) -- COMPLETE

**Goal:** Deliver a functional honeypot with real-time dashboard and alerting.

### Deliverables

| # | Deliverable | Status |
|---|---|---|
| 1.1 | Full session capture pipeline (Cowrie -> Backend file watcher -> DB) | Done |
| 1.2 | Asciinema session replay in dashboard (ttylog parser + browser player) | Done |
| 1.3 | ttyrec -> MP4/GIF video converter (ffmpeg) | Done |
| 1.4 | Real-time dashboard with WebSocket live feed | Done |
| 1.5 | Incidents list with filtering, pagination, and risk scoring | Done |
| 1.6 | Live attack map (Leaflet + GeoIP + dark CARTO tiles) | Done |
| 1.7 | Statistics panel (top countries, ports, usernames, daily stats) | Done |
| 1.8 | Email + webhook + ntfy alerts (Apprise + Celery) | Done |
| 1.9 | GeoIP enrichment (MaxMind GeoLite2 + ip-api.com fallback) | Done |
| 1.10 | AbuseIPDB reputation enrichment (optional) | Done |
| 1.11 | Login page with JWT authentication | Done |
| 1.12 | Session detail page with commands + replay + video export | Done |
| 1.13 | Alerts page with severity badges + acknowledge action | Done |

---

## Iteration 2: Enhanced -- Local AI & Polish (Weeks 5-8)

**Goal:** Add AI-powered threat analysis and fleet management.

### Deliverables

| # | Deliverable | Status |
|---|---|---|
| 2.1 | Ollama integration (local LLM) | Pending |
| 2.2 | LangChain threat summaries with MITRE ATT&CK mapping | Pending |
| 2.3 | Session video export with AI overlay annotations | Pending |
| 2.4 | Configuration UI (enable/disable honeypot services) | Pending |
| 2.5 | Multi-sensor fleet registration and management | Pending |
| 2.6 | Sensor health monitoring and heartbeat | Pending |

---

## Iteration 3: V1 -- MSP Ready (Weeks 9-12)

**Goal:** Production-ready with multi-tenant support for managed service providers.

### Deliverables

| # | Deliverable | Status |
|---|---|---|
| 3.1 | Multi-tenant isolation (org-based data separation) | Pending |
| 3.2 | White-label client portals | Pending |
| 3.3 | PDF/JSON forensic report generation | Pending |
| 3.4 | Auto-update system for containers | Pending |
| 3.5 | Full documentation site | Pending |
| 3.6 | One-click installer script (curl | bash) | Pending |
| 3.7 | Helm chart for Kubernetes | Pending |

---

## Iteration 4+: Future (Community-Driven)

| Feature | Description |
|---|---|
| Kubernetes native | Full K8s operator with auto-scaling |
| Honey tokens | Canary tokens (AWS keys, URLs, DNS) |
| Auto-block hooks | iptables/nftables integration for blocking |
| Hardware blueprints | Pre-loaded RPi kit specifications |
| Plugin marketplace | Community-contributed honeypot plugins |
| SaaS relay | Optional cloud relay for NAT-traversal |
| Threat intelligence feeds | STIX/TAXII integration |

---

## Architecture

```
Sensors (Cowrie, OpenCanary, Beelzebub)
    |
    v
Vector/Fluent Bit (Log Shipping)
    |
    v
FastAPI Backend + Celery Workers
    |
    +--> PostgreSQL + TimescaleDB (persistence)
    +--> Redis (queue/cache)
    +--> Ollama + LangChain (AI summaries)
    +--> Apprise (notifications)
    |
    v
Next.js Dashboard + Leaflet Attack Map
```

---

## Monetization Strategy

| Tier | Model | Price |
|---|---|---|
| Core | MIT open-source, self-hosted forever | Free |
| Premium Cloud Console | Hosted fleet management (10+ sensors) | $9/sensor/mo or $99/mo unlimited |
| Hardware Kits | Pre-loaded RPi (white-label for MSPs) | Per unit |
| Support | Paid support contracts + custom integrations | Contract |

---

*Last updated: February 2026*
*Project Lead (Vision Owner): Grok*
*License: MIT*
