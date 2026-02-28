"""GeoIP enrichment service — resolve IPs to geographic locations.

Uses MaxMind GeoLite2 local database if available, otherwise falls back
to the free ip-api.com JSON endpoint (rate-limited, no key needed).
"""

import logging
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

# Try to import geoip2 (optional dependency)
try:
    import geoip2.database
    HAS_GEOIP2 = True
except ImportError:
    HAS_GEOIP2 = False

_reader = None


def _get_reader():
    """Lazy-load the MaxMind GeoLite2 reader."""
    global _reader
    if _reader is not None:
        return _reader

    if not HAS_GEOIP2:
        return None

    db_paths = [
        Path("/data/geoip/GeoLite2-City.mmdb"),
        Path("./data/geoip/GeoLite2-City.mmdb"),
    ]
    for path in db_paths:
        if path.exists():
            _reader = geoip2.database.Reader(str(path))
            logger.info("Loaded GeoLite2 database from %s", path)
            return _reader

    logger.info("GeoLite2 database not found, using online fallback")
    return None


def _is_private_ip(ip: str) -> bool:
    """Check if an IP address is private/reserved."""
    import ipaddress
    try:
        addr = ipaddress.ip_address(ip)
        return addr.is_private or addr.is_loopback or addr.is_reserved
    except ValueError:
        return True


async def lookup_ip(ip: str) -> dict:
    """Look up GeoIP data for an IP address.

    Returns dict with: country_code, country_name, city, latitude, longitude, asn, org
    """
    if _is_private_ip(ip):
        return {
            "country_code": "XX",
            "country_name": "Private Network",
            "city": "Local",
            "latitude": 0.0,
            "longitude": 0.0,
            "asn": 0,
            "org": "Private",
        }

    # Try local MaxMind DB first
    reader = _get_reader()
    if reader is not None:
        try:
            response = reader.city(ip)
            return {
                "country_code": response.country.iso_code or "XX",
                "country_name": response.country.name or "Unknown",
                "city": response.city.name or "Unknown",
                "latitude": response.location.latitude or 0.0,
                "longitude": response.location.longitude or 0.0,
                "asn": 0,
                "org": "",
            }
        except Exception as e:
            logger.warning("GeoLite2 lookup failed for %s: %s", ip, e)

    # Fallback to ip-api.com (free, no key, 45 req/min rate limit)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"http://ip-api.com/json/{ip}?fields=status,countryCode,country,city,lat,lon,as,org")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    return {
                        "country_code": data.get("countryCode", "XX"),
                        "country_name": data.get("country", "Unknown"),
                        "city": data.get("city", "Unknown"),
                        "latitude": data.get("lat", 0.0),
                        "longitude": data.get("lon", 0.0),
                        "asn": int(data.get("as", "AS0").split()[0].replace("AS", "")) if data.get("as") else 0,
                        "org": data.get("org", ""),
                    }
    except Exception as e:
        logger.warning("ip-api.com lookup failed for %s: %s", ip, e)

    return {
        "country_code": "XX",
        "country_name": "Unknown",
        "city": "Unknown",
        "latitude": 0.0,
        "longitude": 0.0,
        "asn": 0,
        "org": "",
    }
