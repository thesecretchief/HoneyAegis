# Development Setup

Set up a local development environment for contributing to HoneyAegis.

## Prerequisites

- Docker Engine 24+ and Docker Compose v2
- Python 3.12+ (backend development)
- Node.js 22+ and npm (frontend development)
- Git

## Clone and Configure

```bash
git clone https://github.com/thesecretchief/HoneyAegis.git
cd HoneyAegis
cp .env.example .env
```

Edit `.env` to set development-friendly defaults:

```bash
HONEYAEGIS_ENV=development
HONEYAEGIS_DEBUG=true
POSTGRES_PASSWORD=devpassword
REDIS_PASSWORD=devpassword
JWT_SECRET_KEY=dev-secret-key-change-in-production-minimum-64-chars-long-xxxxx
ADMIN_PASSWORD=admin
```

## Start Infrastructure

Launch only the infrastructure containers (database, cache, honeypot):

```bash
docker compose up -d postgres redis cowrie
```

## Backend Development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the development server with hot-reload
uvicorn app.main:app --reload --port 8000
```

The API is now available at `http://localhost:8000`. API docs are at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc` (ReDoc).

## Frontend Development

```bash
cd frontend
npm install
npm run dev
```

The dashboard is now available at `http://localhost:3000` with hot-reload enabled.

## Running Tests

```bash
# Backend tests
cd backend && pytest

# Backend tests with coverage
cd backend && pytest --cov=app --cov-report=html

# Frontend tests
cd frontend && npm test

# Frontend tests in watch mode
cd frontend && npm test -- --watch
```

## Code Quality

```bash
# Python type checking and linting
cd backend && python -m py_compile app/main.py
cd backend && pip install bandit && bandit -r app/ -c pyproject.toml

# Frontend linting
cd frontend && npm run lint

# Format check
cd frontend && npx prettier --check "src/**/*.{ts,tsx}"
```

## Database Migrations

```bash
# Create a new migration
cd backend && alembic revision --autogenerate -m "describe your change"

# Run migrations
cd backend && alembic upgrade head

# Rollback one migration
cd backend && alembic downgrade -1
```

## Useful Ports

| Service | Port | Description |
|---|---|---|
| Frontend | 3000 | Next.js dashboard |
| Backend | 8000 | FastAPI API + Swagger docs |
| Cowrie SSH | 2222 | SSH honeypot |
| Cowrie Telnet | 2223 | Telnet honeypot |
| PostgreSQL | 5432 | Database (for local tools) |
| Redis | 6379 | Cache/queue (for local tools) |
| Grafana | 3001 | Monitoring (full profile) |
| Flower | 5555 | Celery monitoring (HA profile) |

## Troubleshooting

### Backend cannot connect to PostgreSQL

Ensure the postgres container is running and healthy:

```bash
docker compose ps postgres
docker compose logs postgres
```

### Frontend shows connection errors

Verify the backend is running on port 8000 and CORS is configured for development:

```bash
HONEYAEGIS_DEBUG=true  # Enables permissive CORS
```

### Cowrie not producing logs

Check Cowrie container logs and verify the log volume mount:

```bash
docker compose logs cowrie
ls -la data/cowrie/log/
```

## Related Pages

- [Code Conventions](conventions.md) -- Style guide and standards
- [Architecture Overview](../architecture/overview.md) -- Component overview
- [Quick Start](../getting-started/quick-start.md) -- Production deployment
