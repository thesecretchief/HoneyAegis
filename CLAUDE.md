# CLAUDE.md — HoneyAegis Development Rules

This file provides context and rules for AI agents and developers working on HoneyAegis.

## Project Overview

HoneyAegis is an open-source, Docker-first, self-hosted honeypot platform. It emulates vulnerable services, captures full attacker sessions, enriches with AI, and delivers a real-time dashboard.

**Mission:** "StingBox but 10x better and free forever" — no cloud dependency, no subscriptions, full data sovereignty.

## Tech Stack (Do Not Deviate)

- **Orchestration:** Docker Compose (multi-arch amd64/arm64)
- **Honeypots:** Cowrie (SSH/Telnet), OpenCanary, Dionaea, Beelzebub
- **Backend:** FastAPI (Python 3.12) + Celery + SQLAlchemy (async)
- **Database:** PostgreSQL 16 + TimescaleDB + Redis 7
- **Frontend:** Next.js 15 (App Router, TypeScript) + Tailwind CSS + Recharts + Leaflet
- **AI:** Ollama (local LLM) + LangChain
- **Alerts:** Apprise (email, ntfy, Slack, Discord, Teams, SMS)
- **Proxy:** Traefik + Let's Encrypt
- **CI/CD:** GitHub Actions

## Development Rules

1. **MIT license, open-source first.** Never add cloud vendor lock-in.
2. **One-command deploy.** `docker compose up -d` must always work.
3. **Light profile < 4 GB RAM.** Keep the default footprint small.
4. **Security:** Non-root containers, network namespaces, rate limiting. Never store real secrets in code.
5. **Every PR must include tests + documentation updates.**
6. **Use ONLY the defined tech stack.** Do not introduce new frameworks or languages.
7. **Backend code** goes in `backend/app/` following the existing module structure (api/, core/, models/, schemas/, services/, workers/).
8. **Frontend code** goes in `frontend/src/` following the Next.js App Router convention.
9. **Honeypot configs** go in `honeypots/<service>/`.
10. **Scripts** go in `scripts/`.
11. **Database migrations** go in `db/migrations/` (numbered SQL files) and/or `backend/alembic/`.

## Code Conventions

- Python: Type hints required, async by default for DB operations.
- TypeScript: Strict mode, prefer server components where possible.
- Commit messages: Conventional Commits format (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
- No `print()` in production code — use structured logging.

## Architecture Notes

- **Logging flow (light):** Cowrie → mounted volume → Backend file watcher → PostgreSQL
- **Logging flow (full):** Cowrie → mounted volume → Vector → Backend API → PostgreSQL
- **Real-time:** WebSocket on `/ws` broadcasts new events to dashboard
- **Background tasks:** Celery workers for GeoIP enrichment, alerting, video conversion

## Commands

```bash
# Development
docker compose up -d postgres redis cowrie    # Start infra only
cd backend && uvicorn app.main:app --reload   # Backend dev server
cd frontend && npm run dev                    # Frontend dev server

# Testing
cd backend && pytest                          # Backend tests
cd frontend && npm test                       # Frontend tests

# Production
docker compose up -d                          # Light profile
docker compose --profile full up -d           # Full profile
```
