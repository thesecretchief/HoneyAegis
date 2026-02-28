# Changelog

All notable changes to HoneyAegis are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-28

### Added
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
