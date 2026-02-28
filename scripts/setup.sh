#!/usr/bin/env bash
# =============================================================================
# HoneyAegis Quick Setup Script
# One-command deploy for HoneyAegis
# =============================================================================
set -euo pipefail

echo "======================================"
echo "  HoneyAegis Setup"
echo "  Professional Honeypot Platform"
echo "======================================"
echo ""

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Error: Docker is required but not installed."; exit 1; }
command -v docker compose version >/dev/null 2>&1 || { echo "Error: Docker Compose v2 is required."; exit 1; }

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "[*] Creating .env from .env.example..."
    cp .env.example .env

    # Generate random secrets
    RANDOM_SECRET=$(openssl rand -hex 32 2>/dev/null || head -c 64 /dev/urandom | base64 | tr -d '=/+' | head -c 64)
    RANDOM_JWT=$(openssl rand -hex 32 2>/dev/null || head -c 64 /dev/urandom | base64 | tr -d '=/+' | head -c 64)
    RANDOM_PG=$(openssl rand -hex 16 2>/dev/null || head -c 32 /dev/urandom | base64 | tr -d '=/+' | head -c 32)
    RANDOM_REDIS=$(openssl rand -hex 16 2>/dev/null || head -c 32 /dev/urandom | base64 | tr -d '=/+' | head -c 32)

    sed -i "s/change-me-to-a-random-64-char-string/$RANDOM_SECRET/" .env
    sed -i "s/change-me-to-a-random-jwt-secret/$RANDOM_JWT/" .env
    sed -i "s/change-me-postgres-password/$RANDOM_PG/" .env
    sed -i "s/change-me-redis-password/$RANDOM_REDIS/" .env

    echo "[+] Generated random secrets in .env"
else
    echo "[*] .env already exists, skipping..."
fi

# Select profile
PROFILE=""
if [ "${1:-}" = "--full" ] || [ "${1:-}" = "-f" ]; then
    PROFILE="--profile full"
    echo "[*] Starting with FULL profile (all services)..."
else
    echo "[*] Starting with LIGHT profile (core services)..."
    echo "    Use './scripts/setup.sh --full' for all services"
fi

echo ""
echo "[*] Building and starting containers..."
docker compose $PROFILE up -d --build

echo ""
echo "======================================"
echo "  HoneyAegis is running!"
echo ""
echo "  Dashboard:  http://localhost:3000"
echo "  API:        http://localhost:8000"
echo "  API Docs:   http://localhost:8000/docs"
echo ""
echo "  Default login:"
echo "    Email:    admin@honeyaegis.local"
echo "    Password: (check your .env file)"
echo ""
echo "  Cowrie SSH honeypot on port ${COWRIE_EXTERNAL_SSH_PORT:-2222}"
echo "======================================"
