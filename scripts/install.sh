#!/usr/bin/env bash
# =============================================================================
# HoneyAegis One-Click Installer
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/thesecretchief/HoneyAegis/main/scripts/install.sh | bash
#
# What it does:
#   1. Checks prerequisites (Docker, Docker Compose)
#   2. Clones the HoneyAegis repo
#   3. Generates .env from .env.example with random passwords
#   4. Starts the light profile
#   5. Prints dashboard URL
# =============================================================================
set -euo pipefail

REPO_URL="https://github.com/thesecretchief/HoneyAegis.git"
INSTALL_DIR="${HONEYAEGIS_DIR:-$HOME/HoneyAegis}"

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║     HoneyAegis One-Click Installer       ║"
echo "  ║  Professional Honeypot Platform           ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

# --- Check prerequisites ---
echo "[*] Checking prerequisites..."

if ! command -v docker &>/dev/null; then
    echo "[!] Docker is not installed."
    echo "    Install Docker: https://docs.docker.com/engine/install/"
    exit 1
fi

if ! docker compose version &>/dev/null; then
    echo "[!] Docker Compose v2 is not installed."
    echo "    Install: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "[+] Docker $(docker --version | grep -oP 'Docker version \K[0-9.]+')"
echo "[+] Docker Compose $(docker compose version --short)"

# --- Clone or update ---
if [ -d "$INSTALL_DIR" ]; then
    echo "[*] HoneyAegis directory already exists at $INSTALL_DIR"
    echo "    Pulling latest changes..."
    cd "$INSTALL_DIR"
    git pull origin main 2>/dev/null || echo "[!] Git pull failed (not a git repo?)"
else
    echo "[*] Cloning HoneyAegis to $INSTALL_DIR..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# --- Generate .env ---
if [ ! -f .env ]; then
    echo "[*] Generating .env from template..."
    cp .env.example .env

    # Generate random passwords
    PG_PASS=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 32)
    REDIS_PASS=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 32)
    JWT_SECRET=$(openssl rand -base64 48 | tr -dc 'a-zA-Z0-9' | head -c 64)
    ADMIN_PASS=$(openssl rand -base64 16 | tr -dc 'a-zA-Z0-9' | head -c 16)

    sed -i "s/change-me-postgres-password/$PG_PASS/g" .env
    sed -i "s/change-me-redis-password/$REDIS_PASS/g" .env
    sed -i "s/change-me-to-a-random-jwt-secret/$JWT_SECRET/g" .env
    sed -i "s/ADMIN_PASSWORD=changeme/ADMIN_PASSWORD=$ADMIN_PASS/g" .env

    echo "[+] Generated secure passwords in .env"
    echo ""
    echo "    Admin credentials:"
    echo "    Email:    admin@honeyaegis.local"
    echo "    Password: $ADMIN_PASS"
    echo ""
    echo "    SAVE THESE CREDENTIALS — they won't be shown again!"
    echo ""
else
    echo "[*] .env already exists, keeping current configuration"
fi

# --- Start services ---
echo "[*] Starting HoneyAegis (light profile)..."
docker compose up -d

echo ""
echo "[*] Waiting for services to become healthy..."
sleep 10

# Check if services are running
if docker compose ps | grep -q "Up"; then
    echo ""
    echo "  ╔══════════════════════════════════════════╗"
    echo "  ║  HoneyAegis is running!                  ║"
    echo "  ║                                          ║"
    echo "  ║  Dashboard: http://localhost:3000         ║"
    echo "  ║  API:       http://localhost:8000/docs    ║"
    echo "  ║                                          ║"
    echo "  ║  To enable AI summaries:                 ║"
    echo "  ║  OLLAMA_ENABLED=true \\                   ║"
    echo "  ║    docker compose --profile full up -d   ║"
    echo "  ╚══════════════════════════════════════════╝"
    echo ""
else
    echo "[!] Some services may not have started correctly."
    echo "    Run: docker compose ps"
    echo "    Run: docker compose logs"
fi
