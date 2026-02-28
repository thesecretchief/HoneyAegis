# Architecture Overview

HoneyAegis is a modular, Docker-native platform built from purpose-specific containers that communicate over isolated Docker networks.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Traefik (Reverse Proxy)                  │
│               TLS termination, Let's Encrypt                 │
├──────────────┬──────────────┬────────────────────────────────┤
│  Honeypots   │   Backend    │         Frontend               │
│              │              │                                │
│  Cowrie      │  FastAPI     │  Next.js 15 (App Router)       │
│  OpenCanary  │  Celery      │  Tailwind CSS + shadcn/ui      │
│  Dionaea     │  WebSockets  │  Recharts + Leaflet            │
│  Beelzebub   │              │                                │
├──────────────┴──────────────┴────────────────────────────────┤
│                        Data Layer                            │
│  PostgreSQL 16 + TimescaleDB  │  Redis 7 (queue + cache)     │
├───────────────────────────────┴──────────────────────────────┤
│                      Integrations                            │
│  Ollama (local AI)  │  Apprise (alerts)  │  Vector (logs)    │
└──────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Role | Port |
|---|---|---|
| **Cowrie** | SSH/Telnet honeypot with full session recording | 2222/2223 |
| **OpenCanary** | Multi-protocol honeypot (HTTP, FTP, SMB, etc.) | various |
| **Dionaea** | Malware-capturing honeypot | 445/1433/3306 |
| **Beelzebub** | Lightweight HTTP honeypot with AI-driven responses | 8080 |
| **FastAPI Backend** | REST API, WebSocket server, event processing | 8000 |
| **Celery Workers** | Background tasks: GeoIP, alerting, video conversion | -- |
| **Next.js Frontend** | Dashboard, session replay, configuration UI | 3000 |
| **PostgreSQL** | Persistent storage with TimescaleDB for time-series | 5432 |
| **Redis** | Celery broker, WebSocket pub/sub, caching | 6379 |
| **Ollama** | Local LLM inference for threat summaries | 11434 |
| **Vector** | Log shipping and transformation (full profile) | 8686 |
| **Traefik** | Reverse proxy with automatic TLS certificates | 80/443 |

## Docker Networks

HoneyAegis uses three isolated Docker networks:

- **`honeypot_net`** -- Honeypot containers only. No outbound internet access.
- **`backend_net`** -- Backend, database, Redis, and Celery workers.
- **`frontend_net`** -- Frontend and Traefik. Only network with public exposure.

The backend bridges `honeypot_net` and `backend_net` to ingest honeypot logs without giving honeypots direct database access.

## Deployment Profiles

| Profile | Containers | RAM | Use Case |
|---|---|---|---|
| **Light** | Cowrie, Backend, Frontend, PostgreSQL, Redis | 2 GB | Homelab, single VPS |
| **Full** | Light + Ollama, Vector, Prometheus, Grafana, Traefik | 4 GB+ | Production |

```bash
# Light profile
docker compose up -d

# Full profile
docker compose --profile full up -d
```

## Related Pages

- [Data Flow](data-flow.md) -- How events travel from capture to dashboard
- [Security Model](security-model.md) -- Container isolation and hardening
- [Docker Compose Deployment](../deployment/docker-compose.md) -- Production deployment guide
