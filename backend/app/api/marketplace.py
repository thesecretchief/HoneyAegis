"""Plugin marketplace registry API.

Provides a community plugin registry where users can discover, publish,
and install plugins. Currently backed by a static registry with stub
install/publish endpoints.
"""

import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.api.auth import get_tenant_id

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class MarketplacePlugin(BaseModel):
    """A plugin listing in the marketplace."""

    plugin_id: str
    name: str
    version: str
    author: str
    description: str
    plugin_type: str
    downloads: int
    rating: float
    tags: list[str]
    repo_url: str | None = None
    icon_url: str | None = None
    created_at: str
    updated_at: str


class PluginSubmission(BaseModel):
    """Submit a plugin to the marketplace."""

    name: str
    version: str
    description: str
    plugin_type: str
    repo_url: str
    tags: list[str] = []


# ---------------------------------------------------------------------------
# Static registry (will be database-backed later)
# ---------------------------------------------------------------------------
_REGISTRY: list[MarketplacePlugin] = [
    MarketplacePlugin(
        plugin_id="ip-blocklist",
        name="IP Blocklist Enricher",
        version="1.0.0",
        author="HoneyAegis Community",
        description="Enriches sessions with IP reputation data from community blocklists. Checks against known malicious IP databases.",
        plugin_type="enricher",
        downloads=342,
        rating=4.5,
        tags=["enrichment", "threat-intel", "reputation"],
        repo_url="https://github.com/thesecretchief/HoneyAegis/tree/main/plugins/examples/ip_blocklist.py",
        created_at="2026-01-15T00:00:00Z",
        updated_at="2026-02-28T00:00:00Z",
    ),
    MarketplacePlugin(
        plugin_id="auto-ip-block",
        name="Auto IP Blocker",
        version="1.0.0",
        author="HoneyAegis Community",
        description="Automatically blocks IPs after repeated failed login attempts. Configurable threshold and block duration.",
        plugin_type="hook",
        downloads=218,
        rating=4.7,
        tags=["security", "automation", "blocking"],
        repo_url="https://github.com/thesecretchief/HoneyAegis/tree/main/plugins/examples/auto_ip_block.py",
        created_at="2026-02-01T00:00:00Z",
        updated_at="2026-02-28T00:00:00Z",
    ),
    MarketplacePlugin(
        plugin_id="slack-notifier",
        name="Slack Session Notifier",
        version="0.9.0",
        author="Community",
        description="Sends rich Slack notifications with attack details when new sessions are detected. Includes command previews and threat scores.",
        plugin_type="hook",
        downloads=156,
        rating=4.2,
        tags=["alerts", "slack", "notifications"],
        created_at="2026-02-10T00:00:00Z",
        updated_at="2026-02-25T00:00:00Z",
    ),
    MarketplacePlugin(
        plugin_id="virustotal-enricher",
        name="VirusTotal File Scanner",
        version="0.8.0",
        author="Community",
        description="Submits captured malware files to VirusTotal for analysis. Adds detection ratios and vendor results to session data.",
        plugin_type="enricher",
        downloads=89,
        rating=4.0,
        tags=["malware", "virustotal", "enrichment"],
        created_at="2026-02-15T00:00:00Z",
        updated_at="2026-02-20T00:00:00Z",
    ),
    MarketplacePlugin(
        plugin_id="custom-emulator",
        name="Custom Command Emulator",
        version="1.0.0",
        author="HoneyAegis Community",
        description="Template for creating custom command emulators. Simulate specific commands or services to increase attacker engagement.",
        plugin_type="emulator",
        downloads=127,
        rating=4.3,
        tags=["emulation", "template", "commands"],
        repo_url="https://github.com/thesecretchief/HoneyAegis/tree/main/plugins/examples/custom_emulator.py",
        created_at="2026-02-01T00:00:00Z",
        updated_at="2026-02-28T00:00:00Z",
    ),
]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.get("/plugins")
async def list_marketplace_plugins(
    plugin_type: str | None = Query(default=None, description="Filter by type: enricher, hook, emulator"),
    search: str | None = Query(default=None, description="Search by name or description"),
    sort: str = Query(default="downloads", description="Sort by: downloads, rating, updated"),
    limit: int = Query(default=20, le=100),
) -> dict:
    """Browse available plugins in the marketplace."""
    results = list(_REGISTRY)

    if plugin_type:
        results = [p for p in results if p.plugin_type == plugin_type]

    if search:
        search_lower = search.lower()
        results = [
            p for p in results
            if search_lower in p.name.lower()
            or search_lower in p.description.lower()
            or any(search_lower in t for t in p.tags)
        ]

    if sort == "rating":
        results.sort(key=lambda p: p.rating, reverse=True)
    elif sort == "updated":
        results.sort(key=lambda p: p.updated_at, reverse=True)
    else:
        results.sort(key=lambda p: p.downloads, reverse=True)

    return {
        "plugins": results[:limit],
        "total": len(results),
        "page": 1,
    }


@router.get("/plugins/{plugin_id}")
async def get_marketplace_plugin(plugin_id: str) -> MarketplacePlugin:
    """Get details of a specific marketplace plugin."""
    for plugin in _REGISTRY:
        if plugin.plugin_id == plugin_id:
            return plugin
    raise HTTPException(status_code=404, detail="Plugin not found")


@router.post("/plugins/{plugin_id}/install")
async def install_plugin(
    plugin_id: str,
    tenant_id: UUID = Depends(get_tenant_id),
) -> dict:
    """Install a plugin from the marketplace.

    Stub: Acknowledges install but does not download.
    In production, this would download the plugin file from the
    registry and place it in the /plugins directory.
    """
    for plugin in _REGISTRY:
        if plugin.plugin_id == plugin_id:
            logger.info("Plugin install requested: %s (tenant=%s)", plugin_id, tenant_id)
            return {
                "status": "installed",
                "plugin_id": plugin_id,
                "plugin_name": plugin.name,
                "version": plugin.version,
                "message": "Plugin installed. Restart or reload plugins to activate.",
            }
    raise HTTPException(status_code=404, detail="Plugin not found")


@router.post("/plugins/submit")
async def submit_plugin(
    submission: PluginSubmission,
    tenant_id: UUID = Depends(get_tenant_id),
) -> dict:
    """Submit a plugin to the marketplace for review.

    Stub: Acknowledges submission but does not store.
    """
    logger.info(
        "Plugin submission: name=%s author=tenant-%s repo=%s",
        submission.name,
        tenant_id,
        submission.repo_url,
    )
    return {
        "status": "submitted",
        "message": "Plugin submitted for review. It will appear in the marketplace after approval.",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
