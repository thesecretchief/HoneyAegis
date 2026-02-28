# Contributing to HoneyAegis

Thank you for your interest in contributing to HoneyAegis! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- Docker Engine 24+ and Docker Compose v2
- Python 3.12+ (backend development)
- Node.js 22+ (frontend development)
- Git

### Local Development

1. Fork and clone the repository
2. Copy `.env.example` to `.env` and configure
3. Start infrastructure: `docker compose up -d postgres redis cowrie`
4. Set up the backend:
   ```bash
   cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
5. Set up the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Pull Request Guidelines

- Every PR must include tests and documentation updates
- Follow existing code style and conventions
- Keep PRs focused on a single change
- Write clear commit messages
- Ensure CI passes before requesting review

## Security

- All containers must run as non-root
- Use network namespaces for isolation
- Implement rate limiting on all endpoints
- Never store secrets in code

## Code of Conduct

Be respectful, inclusive, and constructive. We're building something great together.
