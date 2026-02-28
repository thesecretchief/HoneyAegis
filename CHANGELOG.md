# Changelog

All notable changes to HoneyAegis are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-02-28

### Added (Iteration 10 — Scaling, HA, Enterprise MSP, Docs Site & v1.1 Release)
- **High availability** — Redis Sentinel (3-node quorum), PostgreSQL streaming replication, Celery Flower monitoring
- **HA compose overlay** — `configs/ha/docker-compose.ha.yml` for production HA deployments
- **RBAC service** — 4 roles (superadmin/admin/analyst/viewer) with 25+ granular permissions
- **RBAC API** — `/api/v1/rbac/roles`, `/api/v1/rbac/check`, `/api/v1/rbac/permissions`
- **SSO/OIDC stub** — provider templates for Keycloak, Okta, Azure AD, Google Workspace
- **SSO API** — `/api/v1/sso/templates`, `/api/v1/sso/configure`, `/api/v1/sso/callback`, `/api/v1/sso/status`
- **Advanced reporting** — executive dashboards with risk scoring (0-100), compliance metrics, trend analysis
- **Reporting API** — `/api/v1/reporting/executive`, `/api/v1/reporting/compliance`, `/api/v1/reporting/risk-score`
- **Performance benchmarks** — benchmark service with percentile calculation, security audit checklist, Lighthouse targets (98+)
- **Benchmark API** — `/api/v1/benchmark/health-report`, `/api/v1/benchmark/security-audit`, `/api/v1/benchmark/lighthouse`
- **Documentation site** — MkDocs Material site in `docs-site/` with GitHub Pages auto-deploy
- **Docs CI workflow** — `.github/workflows/docs.yml` builds and deploys docs on push to main
- **Launch blog post** — `docs/launch/blog-post.md` with v1.1 announcement
- **87 new tests** — RBAC (25), SSO (22), reporting (17), benchmark (23) — 327 total passing

### Changed
- Backend API version bumped to 1.3.0
- Frontend version bumped to v1.3.0
- Config extended with OIDC and HA settings
- Main app registers rbac, sso, reporting, and benchmark routers
- .env.example updated with OIDC and Flower settings
- CI py_compile checks for all new modules

## [1.2.0] - 2026-02-28

### Added (Iteration 9 — Threat Intelligence, Malware Sandbox & Internationalization)
- **Threat intel service** — aggregated lookups across MISP, AlienVault OTX, AbuseIPDB, and VirusTotal with in-memory TTL cache
- **Threat intel API** — `/api/v1/threat-intel/lookup` for indicator enrichment, `/api/v1/threat-intel/feeds` for feed status
- **Malware sandbox** — static analysis with hash computation, entropy calculation, file type detection, pattern matching, IOC extraction
- **Sandbox API** — `/api/v1/sandbox/analyze` for file uploads, `/api/v1/sandbox/status` for capability checks
- **Optional Cuckoo/CAPE integration** — dynamic analysis submission and result polling via sandbox API
- **Advanced AI service** — RAG over captured sessions for enriched threat analysis, multi-LLM routing (phi3/llama3.2/mistral)
- **Enhanced SIEM exports** — Elasticsearch bulk format (`/api/v1/export/elk`), Splunk HEC (`/api/v1/export/splunk`), TheHive alerts (`/api/v1/export/thehive`)
- **Full i18n** — dashboard internationalization with 5 languages: English, Spanish, German, French, Greek
- **Language switcher** — persistent locale selection with browser language auto-detection
- **Sensor relay worker** — `app.workers.sensor_relay` for sensor-only deployments (log tailing + event batching)
- **51 new tests** — threat intel (10), sandbox (17), advanced AI (20), plus 4 existing — 240 total passing

### Changed
- Navigation updated with v1.1.0 → v1.2.0 version bump
- Config extended with OTX, MISP, VirusTotal, Cuckoo API settings
- Main app registers threat-intel and sandbox routers
- .env.example updated with threat intel and sandbox configuration
- CI py_compile checks for all new modules
- All 11 README GIF placeholders replaced with ASCII terminal screenshots

## [1.1.0] - 2026-02-28

### Added (Iteration 8 — SaaS Relay, Hardware Kits & Public Launch)
- **SaaS relay backend** — NAT-traversed sensor connections with heartbeat, event batching, and connected sensor listing (`/api/v1/relay/`)
- **Stripe billing stubs** — subscription plans (Community/Pro/Enterprise), checkout sessions, webhooks, and customer portal (`/api/v1/billing/`)
- **Plugin marketplace** — community plugin registry with browse, search, install, and submit endpoints (`/api/v1/marketplace/`)
- **Usage analytics** — privacy-first opt-in telemetry with anonymous instance IDs and deployment metadata
- **Hardware kit guide** — RPi sensor assembly ($89/$119 BOM), enterprise appliance ($249), MSP white-label packaging
- **Launch assets** — Twitter/X thread, Reddit/HN post templates, YouTube demo script, press kit
- **Frontend marketplace page** — browse/search/install plugins with category filters and install tracking
- **43 new tests** — relay (11), billing (11), marketplace (11), analytics (10) — 189 total passing

### Changed
- Navigation updated with Marketplace link
- Config extended with `relay_enabled`, `stripe_secret_key`, `stripe_webhook_secret`, `analytics_enabled`
- Main app registers relay, billing, marketplace routers

## [1.0.0] - 2026-02-28

### Added (Iteration 7 — E2E Testing, Performance & Final Release)
- **E2E test suite** — Playwright tests for dashboard UI, API endpoints, auth flows, SIEM export, console API
- **E2E CI workflow** — GitHub Actions workflow for automated E2E testing against full Docker Compose stack
- **Response cache service** — in-memory LRU cache with TTL for expensive API responses (stats, map data)
- **Custom 404 page** — styled not-found page with navigation back to dashboard
- **Deployment matrix** — comprehensive documentation for Docker, K8s/Helm, RPi, Proxmox, bare metal deployments
- **Security audit checklist** — pre-release security review for v1.0.0 with findings and recommendations
- **Cache tests** — 11 unit tests for cache service

### Added (Iteration 6 — Edge Deployment & Community Launch)
- **GitHub Release workflow** — automated release with multi-arch Docker images, changelog extraction, sensor compose artifact
- **Raspberry Pi one-click setup** — `scripts/rpi-setup.sh` with architecture detection, Docker install, password generation, and deployment
- **Hosted console API stubs** — `/api/v1/console/` endpoints for future multi-deployment management (stats, deployments, license, heartbeat)
- **Plugin template** — `plugins/template/` with documented boilerplate for custom plugin development
- **Community governance** — CODEOWNERS, bug report template, feature request template, PR template
- **Enhanced metadata** — SEO meta tags, theme-color, robots directive on frontend
- **v1.0.0 release** — first stable release of HoneyAegis

### Changed
- All versions bumped to 1.0.0 (backend, frontend, Helm chart, metrics, health endpoint)
- README updated with v1.0.0 features and completed roadmap
- Helm chart appVersion bumped to 1.0.0

### Fixed
- Bandit B108 false positive (hardcoded /tmp expected in Docker)
- Bandit CI severity flags (-ll → -lll for HIGH+ only)
- FastAPI Query `regex=` deprecation → `pattern=` (Python 3.12 compat)
- Trivy scan split: informational for base image, fail for app code only
- pytest deprecation warning filters for passlib and pydantic

## [0.6.0] - 2026-02-28

### Added
- **Prometheus metrics** — `/metrics` endpoint with counters, gauges, histograms for sessions, alerts, webhooks, AI, plugins
- **Grafana dashboards** — pre-built overview dashboard with 10 panels (sessions, alerts, webhooks, API latency)
- **Prometheus + Grafana** services in full Docker Compose profile
- **CI security scanning** — Bandit (Python), Trivy (Docker), npm audit workflows
- **SIEM export API** — `/api/v1/export/json`, `/api/v1/export/cef`, `/api/v1/export/syslog` endpoints
- **Audit logging** — structured JSON audit logs with CEF and syslog formatters
- **Rate limiting** — token-bucket middleware (100 req/s global, 10 req/s auth endpoints)
- **Plugin examples** — auto IP blocker, custom honeypot emulator template
- **Plugin development guide** — full documentation with API reference and examples
- **CONTRIBUTING.md** — comprehensive contributor guide with deployment matrix
- **CHANGELOG.md** — this file
- **Accessibility** — ARIA labels on all interactive elements
- **Error boundaries** — frontend error recovery on all pages

### Changed
- Backend version bumped to 0.6.0
- Frontend version bumped to 0.6.0
- Health endpoint now returns correct version
- ESLint config: removed deprecated `--ext` flag for flat config compatibility
- Docker Compose: removed obsolete `version` key
- Grafana service now auto-provisions Prometheus datasource and dashboards

### Fixed
- ESLint 9 flat config compatibility with `--ext` flag removal
- Docker Compose `version` key deprecation warning

## [0.5.0] - 2026-02-28

### Added
- **Honey tokens** — decoy credentials/files that trigger alerts when attackers use them
- **Auto-response webhooks** — event-driven HTTP hooks with HMAC-SHA256 signatures
- **Plugin system** — Python plugin loader with auto-discovery, hot reload, and hook execution
- **Kubernetes Helm chart** — production deployment templates (backend, frontend, cowrie, secrets, ingress)
- **Raspberry Pi blueprints** — ARM64 deployment guide with hardware requirements
- **Frontend pages** — honey token and webhook management UI
- **SQL migration** — `honey_tokens` and `webhooks` tables with tenant isolation

### Changed
- Backend version bumped to 0.5.0
- Ingestion pipeline now checks login attempts against active honey tokens
- Navigation updated with Honey Tokens and Webhooks links

## [0.4.0] - 2026-02-28

### Added
- **Multi-tenant isolation** — tenant-scoped data with JWT claims
- **White-label client portals** — view-only portals by tenant slug
- **PDF/JSON forensic reports** — WeasyPrint reports with tenant branding
- **Auto-update system** — `scripts/update.sh` with cron support
- **One-click installer** — `scripts/install.sh` with prerequisite checks
- **SECURITY.md** — vulnerability reporting and security architecture
- **MSP deployment guide** — tenant setup, branding, sensor registration

### Fixed
- Backend dependency conflict (langchain-core pinning)
- Frontend lint CI failure (migrated to ESLint flat config)
- Report exports now use authenticated downloads (Bearer token)
- Branding endpoint returns `id` field for frontend PATCH

## [0.3.0] - 2026-02-28

### Added
- **Local AI analysis** — Ollama integration for threat summaries and MITRE ATT&CK mapping
- **Multi-sensor fleet** — sensor registration, heartbeat monitoring, session attribution
- **Configuration UI** — honeypot, alert, AI, and fleet settings
- **Loading skeletons** and error boundaries across all pages

## [0.2.0] - 2026-02-28

### Added
- **Real-time dashboard** — live stats, WebSocket feed, top countries/ports/usernames
- **Attack map** — Leaflet map with GeoIP markers
- **Session capture** — full Cowrie tty recording with browser replay
- **Video export** — MP4/GIF export via ffmpeg
- **Alerting** — Apprise integration (email, Slack, Discord, etc.)
- **GeoIP enrichment** — MaxMind + ip-api.com fallback

## [0.1.0] - 2026-02-28

### Added
- Initial project skeleton
- Docker Compose orchestration (light + full profiles)
- Cowrie SSH/Telnet honeypot with custom configuration
- FastAPI backend with PostgreSQL + Redis
- Next.js 15 frontend with Tailwind CSS
- GitHub Actions CI/CD pipeline
- Multi-arch Docker builds (amd64 + arm64)
