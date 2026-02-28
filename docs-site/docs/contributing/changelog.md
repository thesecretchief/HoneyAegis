# Changelog

All notable changes to HoneyAegis are documented here. For the full commit history, see [CHANGELOG.md](https://github.com/thesecretchief/HoneyAegis/blob/main/CHANGELOG.md) in the repository root.

This project follows [Semantic Versioning](https://semver.org/) and [Conventional Commits](https://www.conventionalcommits.org/).

## v1.3.0 (2026-02-28)

### Added

- High availability deployment with Redis Sentinel and PostgreSQL replication
- Celery Flower monitoring dashboard for background task inspection
- RBAC with 4 roles (Super Admin, Admin, Analyst, Viewer) and 25+ granular permissions
- SSO/OIDC integration templates for Keycloak, Okta, Azure AD, Google Workspace
- Advanced reporting with executive dashboards and automated risk scoring
- Performance benchmarks and security audit API endpoints
- MkDocs documentation site with GitHub Pages deployment
- 87 new tests (327 total passing)

### Changed

- Upgraded FastAPI to 0.115.x
- Improved WebSocket reconnection logic with exponential backoff
- Reduced Docker image sizes by 30% with multi-stage builds

### Fixed

- WebSocket disconnections under high event volume
- GeoIP lookup failures for IPv6 addresses
- Session replay timing drift on long sessions

## v1.2.0 (2026-02-28)

### Added

- Threat intelligence feeds: MISP, AlienVault OTX, AbuseIPDB, VirusTotal
- Malware sandbox with static analysis (hashing, entropy, YARA, string extraction)
- Advanced AI analysis with RAG (Retrieval-Augmented Generation) and multi-LLM routing
- Enhanced SIEM exports: Elasticsearch (ECS), Splunk HEC, TheHive
- Internationalization support (English, Spanish, German, French, Greek)
- Honey token system for decoy credentials and canary files

### Changed

- Migrated to TimescaleDB for time-series data with automatic compression
- Improved alert throttling to prevent notification floods

## v1.1.0 (2026-02-28)

### Added

- SaaS relay backend for NAT traversal (sensors behind firewalls)
- Stripe billing integration for managed service providers
- Plugin marketplace with community registry
- Hardware kit guides for Raspberry Pi and Intel N100 appliances
- Fleet management with multi-sensor support

### Changed

- Reduced light profile RAM usage to under 500 MB
- Faster session replay rendering with WebGL acceleration

## v1.0.0 (2026-02-28)

### Added

- First stable release
- Cowrie SSH/Telnet honeypot with full session recording
- FastAPI backend with async SQLAlchemy and PostgreSQL
- Next.js 15 dashboard with real-time WebSocket updates
- Live attack map with Leaflet and GeoIP
- Ollama AI threat summaries (local inference)
- Apprise alerting (email, Slack, Discord, Teams, ntfy, SMS)
- Session replay with MP4/GIF export
- JWT authentication with role-based access
- Docker Compose deployment (light and full profiles)
- Kubernetes Helm chart
- Raspberry Pi one-click setup script
- End-to-end test suite with Playwright
- GitHub Actions CI/CD with automated releases

## Related Pages

- [Quick Start](../getting-started/quick-start.md) -- Get started with the latest version
- [Code Conventions](conventions.md) -- Contributing guidelines
- [Development Setup](setup.md) -- Set up a local development environment
