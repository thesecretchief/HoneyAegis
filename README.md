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
git clone https://github.com/thesecretchief/HoneyAegis.git
cd HoneyAegis
cp .env.example .env
# Edit .env with your settings (timezone, passwords, alert endpoints)
```

### 2. Deploy (light profile — Cowrie + PostgreSQL + Dashboard)

```bash
docker compose up -d
```

### 3. Deploy (full profile — all honeypots + AI + monitoring)

```bash
# Enable AI summaries (Ollama downloads phi3:mini on first run ~2GB)
OLLAMA_ENABLED=true docker compose --profile full up -d
```

> **RAM Note:** The full profile with Ollama requires **4 GB+ RAM**. The phi3:mini model uses ~1.5 GB during inference. On systems with less RAM, use the light profile (2 GB minimum) which skips AI but keeps all other features.

### 4. Verify deployment

```bash
docker compose ps   # all services should show "Up (healthy)"
```

### 5. Access the dashboard

Open `http://your-server:3000` in your browser.
Default credentials: `admin` / `changeme` (change immediately).

> **Security Warning:** Never expose honeypot ports (22/23) on production internet-facing servers. Always deploy HoneyAegis on an isolated network segment or behind a cloud firewall. The honeypot intentionally attracts malicious traffic — keep it separated from real infrastructure.

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
│   │   ├── services/     # Business logic (webhooks, plugins, ingestion)
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
├── helm/                 # Kubernetes Helm chart
├── plugins/              # Custom plugin directory
│   └── examples/         # Example plugins (IP blocklist)
├── scripts/              # Helper scripts (install, update)
├── docs/                 # Documentation (MSP guide, RPi blueprint)
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

### One-Click Install

```bash
curl -sSL https://raw.githubusercontent.com/thesecretchief/HoneyAegis/main/scripts/install.sh | bash
```

The installer checks prerequisites, clones the repo, generates secure passwords, and starts the light profile automatically.

## Roadmap

- [x] **Iteration 0** — Foundation: repo skeleton, Docker Compose, Cowrie, CI/CD
- [x] **Iteration 1** — MVP: session capture, real-time dashboard, alerts, GeoIP, video export
- [x] **Iteration 2** — Enhanced: local AI summaries, fleet management, config UI, polish
- [x] **Iteration 3** — MSP: multi-tenant, client portals, PDF/JSON reports, auto-update
- [x] **Iteration 4** — Advanced: Kubernetes/Helm, honey tokens, webhooks, plugins, RPi blueprints
- [ ] **Iteration 5+** — SaaS relay, marketplace, advanced threat intelligence

## Features (Iteration 4 — Advanced Capabilities)

### Honey Tokens
- **Decoy credentials** — plant fake usernames/passwords that trigger instant alerts when used
- **File tokens** — deploy decoy files that alert on access
- **Trigger tracking** — count and timestamp every token activation
- **Severity control** — set alert severity per token (critical, high, medium, low)
- **Auto-detection** — ingestion pipeline automatically checks login attempts against active tokens
- **Dashboard UI** — create, manage, and monitor tokens from the web interface

### Auto-Response Webhooks
- **Event-driven hooks** — trigger HTTP webhooks on alerts, sessions, honey tokens, or malware captures
- **Severity filtering** — fire webhooks only for specific severity levels
- **HMAC signatures** — webhooks include `X-HoneyAegis-Signature` header for verification
- **Test endpoint** — verify webhook connectivity from the dashboard
- **Execution tracking** — monitor delivery status, response codes, and execution counts
- **Multi-service** — connect to Slack, Discord, PagerDuty, custom APIs

### Plugin System
- **Python plugins** — drop `.py` files into `/plugins` to extend HoneyAegis
- **Plugin types** — emulators, enrichers, exporters, and event hooks
- **Auto-discovery** — plugins loaded on startup, reloadable via API
- **Event hooks** — plugins receive real-time events for custom processing
- **Example included** — IP blocklist plugin demonstrates the hook pattern
- **Superuser management** — reload plugins via API (admin only)

### Kubernetes & Helm Chart
- **Production Helm chart** — deploy HoneyAegis on any Kubernetes cluster
- **Full profile only** — Helm deployment for enterprise/cloud environments
- **Configurable** — backend, frontend, cowrie, PostgreSQL, Redis, Ollama all templated
- **Ingress support** — TLS termination via cert-manager / Let's Encrypt
- **Secret management** — Kubernetes secrets for all sensitive values

### Raspberry Pi Blueprints
- **Hardware guide** — RPi 4/5 sensor deployment (2GB+ RAM)
- **Docker-native** — multi-arch images (amd64 + arm64) work out of the box
- **Resource profiled** — ~430 MB RAM total (fits in 2 GB)
- **Network placement** — VLAN isolation, port forwarding, security best practices
- **Fleet integration** — register RPi as a remote sensor via the hub API
- **Auto-start** — systemd + Docker restart policies for unattended operation

See [docs/rpi-blueprint.md](docs/rpi-blueprint.md) for the full deployment guide.

## Features (Iteration 3 — MSP Ready)

> **Screenshots:** See the GIFs below for client portal, PDF reports, and tenant branding in action.

### Multi-Tenant Isolation
- **Tenant-scoped data** — every table has `tenant_id`, enforced at the query level
- **JWT tenant claims** — tenant context propagated through authentication
- **Cross-tenant protection** — sensors, sessions, alerts fully isolated between tenants
- **Default tenant** — single-tenant deployments work out of the box

### White-Label Branding
- **Per-tenant branding** — custom logo, primary color, display name
- **Client portal theming** — branding applied to view-only portals
- **Report branding** — PDF reports include tenant logo and colors

<!-- TODO: Add GIF: tenant branding config UI -->
<!-- ![Tenant Branding](docs/assets/tenant-branding.gif) -->

### Client Portals
- **View-only access** — clients see their incidents without configuration access
- **No auth required** — portals identified by tenant slug (`/client/acme-corp`)
- **Real-time stats** — attack counts, unique IPs, alert status
- **Session table** — browseable attack sessions with filtering
- **Auto-refresh** — portals update every 30 seconds

<!-- TODO: Add GIF: client portal with custom branding -->
<!-- ![Client Portal](docs/assets/client-portal.gif) -->

### PDF/JSON Forensic Reports
- **WeasyPrint PDF** — polished, styled reports with session data + AI summaries
- **Single session** — detailed report for one specific attack session
- **Aggregate** — summary report across all sessions for a tenant
- **MITRE ATT&CK** — TTP mapping included in reports
- **One-click export** — download buttons on session detail page

<!-- TODO: Add GIF: PDF report download -->
<!-- ![PDF Report](docs/assets/pdf-report.gif) -->

### Auto-Update System
- **Update script** — `./scripts/update.sh` pulls code + images and recreates containers
- **Cron support** — `./scripts/update.sh --auto` for unattended daily updates
- **Version tracking** — git-based versioning with update log

### One-Click Installer
- **curl | bash** — single command deploys HoneyAegis from scratch
- **Prerequisite checks** — verifies Docker and Docker Compose
- **Secure by default** — auto-generates random passwords for all services
- **Credential display** — shows admin password once at install time

### Security Documentation
- **[SECURITY.md](SECURITY.md)** — vulnerability reporting, security architecture
- **[MSP Guide](docs/msp-guide.md)** — tenant setup, branding, sensor registration, scaling

## Features (Iteration 2 — Enhanced)

### Local AI Threat Analysis
- **Ollama integration** — 100% local LLM inference, no data leaves your network
- **Auto-summarize** — AI generates threat summaries on session close
- **MITRE ATT&CK mapping** — automatic TTP identification (e.g. T1078, T1059.004)
- **Threat scoring** — AI assigns critical/high/medium/low/info threat levels
- **Video overlay** — AI summary burned into exported MP4/GIF as ffmpeg drawtext
- **On-demand** — regenerate summaries anytime from the session detail page

```
Example AI Summary:
┌──────────────────────────────────────────────────────────────┐
│ Threat Level: HIGH                                           │
│                                                              │
│ Attacker from CN (Beijing) brute-forced SSH credentials     │
│ and gained access as root. Executed reconnaissance commands  │
│ (whoami, uname -a, cat /etc/passwd) before attempting to    │
│ download a cryptominer from a known malicious domain.       │
│                                                              │
│ MITRE ATT&CK: T1078 (Valid Accounts), T1059.004 (Unix      │
│ Shell), T1105 (Ingress Tool Transfer)                       │
│                                                              │
│ Recommendation: Block source IP and monitor for lateral     │
│ movement indicators from the same ASN.                      │
└──────────────────────────────────────────────────────────────┘
```

### Multi-Sensor Fleet Management
- **Register sensors** — add RPi nodes, VPS instances, homelab servers
- **Heartbeat monitoring** — track sensor status (online/stale/offline)
- **Session attribution** — link sessions to specific sensors
- **Dashboard integration** — fleet-wide sensor count on main dashboard

### Configuration UI
- **Honeypot management** — view enabled/disabled services and their ports
- **Alert rules** — toggle session alerts, malware alerts, set cooldown periods
- **AI status** — check Ollama connection and model availability
- **Fleet mode** — standalone or hub-and-spoke topology

### Polish
- **Loading skeletons** — smooth loading states across all pages
- **Error boundaries** — graceful error recovery with retry buttons
- **Mobile responsive** — bottom nav bar on mobile, responsive grids
- **Refined dark theme** — consistent gray-950/900/800 palette throughout

## Features (Iteration 1 — MVP)

### Real-Time Dashboard
- **Live stats cards** — attacks today, unique IPs, auth successes, active sensors
- **WebSocket live feed** — real-time event stream from honeypot
- **Top countries / ports / usernames** — aggregated attack intelligence
- **Auto-refresh** — dashboard polls every 15 seconds

### Animated Attack Map
- **Leaflet** map with dark CARTO tiles
- **GeoIP enrichment** — IPs resolved to country, city, lat/lon via MaxMind GeoLite2 or ip-api.com fallback
- **Circle markers** — size scaled by session count, clickable popups with details

### Session Capture & Replay
- **Full Cowrie tty recording** — SSH/Telnet keystrokes captured
- **Asciinema-style replay** — play back attacker sessions in the browser terminal
- **Command history** — every command captured and indexed
- **Video export** — download session as MP4 or GIF (ffmpeg-powered)

### Incidents List
- **Sortable, filterable table** — protocol, source IP, location, duration, commands
- **Risk scoring** — automatic Low/Medium/High/Critical based on auth success, commands, duration
- **Pagination** — handle thousands of sessions efficiently

### Alerting
- **Apprise integration** — email, Slack, Discord, ntfy, Gotify, Teams, SMS (Twilio)
- **Celery-powered** — async alert delivery on new sessions and malware captures
- **Configurable** — per-channel alert thresholds via `.env`

### Enrichment
- **GeoIP** — MaxMind GeoLite2 local DB or free ip-api.com fallback
- **AbuseIPDB** — optional reputation scoring (requires free API key)
- **Cached** — results stored in PostgreSQL to minimize API calls

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security

HoneyAegis is designed to be deployed as a honeypot — it intentionally exposes services to attract attackers. **Always deploy on isolated networks and never on production infrastructure.**

See [SECURITY.md](SECURITY.md) for our security policy, architecture details, and deployment checklist.

To report security vulnerabilities, please see [SECURITY.md](SECURITY.md) or open a private security advisory on GitHub.

## Project Rules

See [CLAUDE.md](CLAUDE.md) for development rules, conventions, and agent instructions.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with purpose. Open source forever.
</p>
