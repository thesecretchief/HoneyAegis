# Contributing to HoneyAegis

Thank you for your interest in contributing to HoneyAegis! This guide covers everything you need to get started.

## Code of Conduct

Be respectful, constructive, and collaborative. We welcome contributors of all experience levels.

## Getting Started

### Prerequisites

- Docker Engine 24+ and Docker Compose v2
- Python 3.12+ (backend development)
- Node.js 22+ (frontend development)
- Git

### Development Setup

```bash
# Clone the repository
git clone https://github.com/thesecretchief/HoneyAegis.git
cd HoneyAegis

# Start infrastructure
docker compose up -d postgres redis cowrie

# Backend setup
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend
cd backend && pytest -v

# Frontend
cd frontend && npm run lint && npm run build
```

## How to Contribute

### Reporting Bugs

1. Check [existing issues](https://github.com/thesecretchief/HoneyAegis/issues) first
2. Use the bug report template
3. Include: expected behavior, actual behavior, steps to reproduce, environment details

### Suggesting Features

1. Open a [feature request](https://github.com/thesecretchief/HoneyAegis/issues/new)
2. Describe the use case and expected behavior
3. Consider implementation complexity and alignment with project goals

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Follow the coding conventions below
4. Write tests for new functionality
5. Update documentation if needed
6. Commit with conventional commits: `git commit -m 'feat: add amazing feature'`
7. Push and open a PR against `main`

## Coding Conventions

### Python (Backend)

- **Type hints required** on all function signatures
- **Async by default** for database operations
- **Structured logging** — use `logging.getLogger(__name__)`, never `print()`
- **Pydantic schemas** for all API request/response models
- **SQLAlchemy models** with `Mapped` type annotations

### TypeScript (Frontend)

- **Strict mode** enabled
- **Server components** preferred where possible
- **Tailwind CSS** for styling (no CSS modules or styled-components)
- **No `any` in new code** — use proper types

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add honey token trigger notifications
fix: resolve tenant isolation in webhook queries
docs: update plugin development guide
test: add webhook HMAC signature tests
chore: bump prometheus-client to 0.21.1
```

### File Organization

| What | Where |
|------|-------|
| Backend API endpoints | `backend/app/api/` |
| Backend models | `backend/app/models/` |
| Backend services | `backend/app/services/` |
| Backend tests | `backend/tests/` |
| Frontend pages | `frontend/src/app/` |
| Frontend components | `frontend/src/components/` |
| Frontend API client | `frontend/src/lib/api.ts` |
| Honeypot configs | `honeypots/<service>/` |
| Plugins | `plugins/` |
| Documentation | `docs/` |
| SQL migrations | `db/migrations/` |

## Architecture Overview

```
Attacker → Cowrie → Log Files → Backend (FastAPI) → PostgreSQL
                                      ↓
                              WebSocket → Dashboard (Next.js)
                                      ↓
                              Prometheus → Grafana
```

### Key Design Decisions

- **Docker-first** — every component runs in containers
- **Multi-tenant** — all data scoped by `tenant_id`
- **Plugin system** — extend via Python modules in `/plugins`
- **Local AI** — Ollama for on-premises LLM inference
- **MIT licensed** — no vendor lock-in, free forever

## Deployment Matrix

| Environment | Command | RAM | Profile |
|------------|---------|-----|---------|
| Development | `docker compose up -d postgres redis cowrie` | 1 GB | Infra only |
| Light | `docker compose up -d` | 2 GB | Core services |
| Full | `docker compose --profile full up -d` | 4 GB+ | All services |
| Kubernetes | `helm install honeyaegis helm/honeyaegis/` | 4 GB+ | Full |
| Raspberry Pi | See [RPi Blueprint](rpi-blueprint.md) | 2 GB | Light |

## Security

- **Never commit secrets** — use `.env` files and environment variables
- **Non-root containers** — all Docker images run as non-root users
- **Network isolation** — honeypot and internal networks are separated
- **Rate limiting** — API endpoints have token-bucket rate limits
- **HMAC signatures** — webhooks are signed for verification

See [SECURITY.md](../SECURITY.md) for the full security policy.

## Need Help?

- Open a [GitHub Discussion](https://github.com/thesecretchief/HoneyAegis/discussions)
- Check the [docs/](.) directory for guides
- Read the [CLAUDE.md](../CLAUDE.md) for AI agent development rules
