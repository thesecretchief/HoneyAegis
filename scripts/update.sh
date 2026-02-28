#!/usr/bin/env bash
# =============================================================================
# HoneyAegis Auto-Update Script
#
# Usage:
#   ./scripts/update.sh           # Interactive update
#   ./scripts/update.sh --auto    # Non-interactive (for cron)
#
# What it does:
#   1. Pulls latest code from git
#   2. Pulls latest Docker images
#   3. Recreates containers with new images
#   4. Verifies services are healthy
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
AUTO_MODE="${1:-}"
LOG_FILE="${PROJECT_DIR}/logs/update.log"

mkdir -p "$(dirname "$LOG_FILE")"

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE"
}

cd "$PROJECT_DIR"

log "Starting HoneyAegis update..."

# --- Check for updates ---
log "Fetching latest changes..."
git fetch origin main 2>/dev/null

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main 2>/dev/null || echo "$LOCAL")

if [ "$LOCAL" = "$REMOTE" ]; then
    log "Already up to date ($(echo "$LOCAL" | head -c 8))"
    if [ "$AUTO_MODE" = "--auto" ]; then
        exit 0
    fi
    echo ""
    echo "No new updates available."
    echo "Current version: $(echo "$LOCAL" | head -c 8)"
    exit 0
fi

log "Update available: $(echo "$LOCAL" | head -c 8) -> $(echo "$REMOTE" | head -c 8)"

if [ "$AUTO_MODE" != "--auto" ]; then
    echo ""
    echo "Update available!"
    echo "  Current: $(echo "$LOCAL" | head -c 8)"
    echo "  Latest:  $(echo "$REMOTE" | head -c 8)"
    echo ""
    read -r -p "Apply update? [y/N] " confirm
    if [[ ! "$confirm" =~ ^[yY] ]]; then
        echo "Update cancelled."
        exit 0
    fi
fi

# --- Pull code ---
log "Pulling latest code..."
git pull origin main 2>&1 | tee -a "$LOG_FILE"

# --- Pull images and recreate ---
log "Pulling latest Docker images..."
docker compose pull 2>&1 | tee -a "$LOG_FILE"

log "Recreating containers..."
docker compose up -d 2>&1 | tee -a "$LOG_FILE"

# --- Verify ---
log "Waiting for services to become healthy..."
sleep 10

if docker compose ps | grep -q "Up"; then
    NEW_VERSION=$(git rev-parse HEAD | head -c 8)
    log "Update complete! Running version: $NEW_VERSION"
    echo ""
    echo "  HoneyAegis updated successfully!"
    echo "  Version: $NEW_VERSION"
    echo "  Dashboard: http://localhost:3000"
else
    log "WARNING: Some services may not have started correctly"
    echo ""
    echo "  [!] Some services may not have started correctly."
    echo "  Run: docker compose ps"
    echo "  Run: docker compose logs"
    exit 1
fi
