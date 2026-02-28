# HoneyAegis Documentation

**Professional-grade, Docker-native honeypot platform.**
Deploy a full deception network in under 5 minutes.

---

## What is HoneyAegis?

HoneyAegis turns any VPS, homelab server, or Raspberry Pi into a professional-grade deception network. It emulates vulnerable services, captures full attacker sessions (including keystrokes with polished video replays), enriches events with local AI summaries, and delivers a real-time web dashboard with attack maps, trends, and one-click alerts.

**No cloud dependency. No subscriptions. Full data sovereignty.**

## Key Features

- **One-command deploy** — `docker compose up -d` and you're live
- **Full session capture** — SSH/Telnet keystrokes recorded, exportable as MP4/GIF
- **Local AI analysis** — Ollama-powered threat summaries (no data leaves your network)
- **Threat intelligence** — Aggregated feeds from MISP, OTX, AbuseIPDB, VirusTotal
- **Malware sandbox** — Static analysis with hash, entropy, pattern matching, IOC extraction
- **Real-time dashboard** — Live attack map, incident timeline, statistics
- **Multi-sensor fleet** — Manage sensors across VPS, homelab, RPi from one console
- **Enterprise-ready** — Multi-tenant, RBAC, SSO/OIDC, audit logging, HA support
- **Extensible** — Plugin system + marketplace for custom honeypot services
- **i18n** — Available in English, Spanish, German, French, and Greek

## Quick Start

```bash
# Clone and configure
git clone https://github.com/thesecretchief/HoneyAegis.git
cd HoneyAegis
cp .env.example .env

# Deploy (light profile — Cowrie + PostgreSQL + Dashboard)
docker compose up -d

# Open dashboard
open http://localhost:3000
```

Default credentials: `admin` / `changeme` (change immediately).

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    HoneyAegis Stack                      │
├──────────────┬──────────────┬───────────────────────────┤
│  Honeypots   │   Backend    │        Frontend           │
│              │              │                           │
│  Cowrie      │  FastAPI     │  Next.js 15               │
│  OpenCanary  │  Celery      │  Tailwind + shadcn/ui     │
│  Dionaea     │  WebSockets  │  Recharts + Leaflet       │
│  Beelzebub   │              │                           │
├──────────────┼──────────────┼───────────────────────────┤
│           Data Layer        │       Integrations        │
│                             │                           │
│  PostgreSQL + TimescaleDB   │  Ollama (local AI)        │
│  Redis (queue/cache)        │  Apprise (alerts)         │
│  Vector (log shipping)      │  Traefik (reverse proxy)  │
└─────────────────────────────┴───────────────────────────┘
```

## Comparison

| Feature | HoneyAegis | StingBox | T-Pot |
|---|---|---|---|
| Self-hosted | Yes | Cloud-only | Yes |
| AI summaries | Local (Ollama) | Cloud AI | No |
| Deploy time | < 5 min | Varies | 15-30 min |
| Session video | Native MP4/GIF | Limited | No |
| Multi-tenant | Yes | No | No |
| ARM64 support | Yes | No | Partial |
| License | MIT | Proprietary | GPL |
| RAM minimum | 2 GB (light) | N/A | 8 GB |

## Getting Help

- [GitHub Issues](https://github.com/thesecretchief/HoneyAegis/issues) — bug reports and feature requests
- [GitHub Discussions](https://github.com/thesecretchief/HoneyAegis/discussions) — community Q&A
- [Security Policy](https://github.com/thesecretchief/HoneyAegis/blob/main/SECURITY.md) — vulnerability reporting
