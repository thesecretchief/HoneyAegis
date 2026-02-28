<p align="center">
  <h1 align="center">HoneyAegis</h1>
  <p align="center">
    Professional-grade, Docker-native honeypot platform.<br/>
    Deploy a full deception network in under 5 minutes.
  </p>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <img src="https://img.shields.io/badge/docker-ready-blue?logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/platform-amd64%20%7C%20arm64-green" alt="Multi-arch">
</p>

---

## What is HoneyAegis?

HoneyAegis turns any VPS, homelab server, or Raspberry Pi into a professional-grade deception network. It emulates vulnerable services, captures full attacker sessions (including keystrokes with polished video replays), enriches events with local AI summaries, and delivers a real-time web dashboard with attack maps, trends, and one-click alerts.

**No cloud dependency. No subscriptions. Full data sovereignty.**

### Key Features

- **One-command deploy** — `docker compose up -d` and you're live
- **Full session capture** — SSH/Telnet keystrokes recorded, exportable as MP4/GIF
- **Local AI analysis** — Ollama-powered threat summaries (no data leaves your network)
- **Real-time dashboard** — Live attack map, incident timeline, statistics
- **Multi-sensor fleet** — Manage sensors across VPS, homelab, RPi from one console
- **Extensible** — Plugin system for custom honeypot services
- **MSP-ready** — Multi-tenant isolation, white-label client portals

### How It Compares

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

## Quick Start

### Prerequisites

- Docker Engine 24+ and Docker Compose v2
- 2 GB RAM minimum (light profile) / 4 GB+ recommended (full profile)
- Linux host (Ubuntu 22.04+, Debian 12+, or compatible)

### 1. Clone and configure

```bash
git clone https://github.com/honeyaegis/honeyaegis.git
cd honeyaegis
cp .env.example .env
# Edit .env with your settings (timezone, passwords, alert endpoints)
```

### 2. Deploy (light profile — Cowrie + PostgreSQL + Dashboard)

```bash
docker compose up -d
```

### 3. Deploy (full profile — all honeypots + AI + monitoring)

```bash
docker compose --profile full up -d
```

### 4. Access the dashboard

Open `http://your-server:3000` in your browser.
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

## Project Structure

```
honeyaegis/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/          # REST + WebSocket endpoints
│   │   ├── core/         # Config, security, database
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── workers/      # Celery tasks
│   ├── alembic/          # Database migrations
│   └── tests/
├── frontend/             # Next.js dashboard
├── honeypots/
│   └── cowrie/           # Cowrie SSH/Telnet honeypot
├── configs/
│   ├── vector/           # Log shipper config
│   └── traefik/          # Reverse proxy config
├── db/
│   └── migrations/       # SQL migration scripts
├── scripts/              # Helper scripts
├── docs/                 # Documentation
├── docker-compose.yml    # Orchestration
└── .env.example          # Configuration template
```

## Development

### Running locally

```bash
# Start infrastructure (database, redis, cowrie)
docker compose up -d postgres redis cowrie

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Running tests

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test
```

## Roadmap

- [x] **Iteration 0** — Foundation: repo skeleton, Docker Compose, Cowrie, CI/CD
- [ ] **Iteration 1** — MVP: session capture, dashboard, alerts, GeoIP
- [ ] **Iteration 2** — AI integration, fleet management, config UI
- [ ] **Iteration 3** — MSP: multi-tenant, client portals, reports
- [ ] **Iteration 4+** — Kubernetes, honey tokens, plugin marketplace

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security

HoneyAegis is designed to be deployed as a honeypot — it intentionally exposes services to attract attackers. **Always deploy on isolated networks and never on production infrastructure.**

To report security vulnerabilities, please open a private security advisory on GitHub.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with purpose. Open source forever.
</p>
