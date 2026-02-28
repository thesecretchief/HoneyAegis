#!/usr/bin/env bash
# =============================================================================
# Download MaxMind GeoLite2 City database
# Requires MAXMIND_LICENSE_KEY environment variable or .env file
# =============================================================================
set -euo pipefail

GEOIP_DIR="${1:-./data/geoip}"
DB_FILE="$GEOIP_DIR/GeoLite2-City.mmdb"

# Load .env if exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep MAXMIND_LICENSE_KEY | xargs)
fi

if [ -z "${MAXMIND_LICENSE_KEY:-}" ]; then
    echo "[!] MAXMIND_LICENSE_KEY not set."
    echo "    Get a free license key at: https://www.maxmind.com/en/geolite2/signup"
    echo "    Set it in .env or export MAXMIND_LICENSE_KEY=your_key"
    echo ""
    echo "[*] Falling back to IP-based geolocation via ip-api.com (no local DB)."
    echo "    The backend will use the online fallback automatically."
    exit 0
fi

mkdir -p "$GEOIP_DIR"

echo "[*] Downloading GeoLite2-City database..."
DOWNLOAD_URL="https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=${MAXMIND_LICENSE_KEY}&suffix=tar.gz"

TMP_FILE=$(mktemp)
curl -sS -o "$TMP_FILE" "$DOWNLOAD_URL"

echo "[*] Extracting..."
tar -xzf "$TMP_FILE" -C "$GEOIP_DIR" --strip-components=1 --wildcards "*.mmdb"
rm -f "$TMP_FILE"

if [ -f "$DB_FILE" ]; then
    echo "[+] GeoLite2-City.mmdb saved to $DB_FILE"
    echo "[+] Size: $(du -h "$DB_FILE" | cut -f1)"
else
    echo "[!] Failed to extract database. Check your license key."
    exit 1
fi
