"""HoneyAegis Backend - FastAPI Application."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, sessions, events, auth, alerts, replay, video, websocket, ai, sensors, config, tenants, reports, client_portal, honey_tokens, webhooks, plugins, metrics, export, console
from app.core.config import settings
from app.core.database import engine, Base
from app.services.rate_limiter import RateLimitMiddleware

logging.basicConfig(
    level=logging.DEBUG if settings.honeyaegis_debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup: create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Startup: create default admin user if not exists
    await _ensure_admin_user()

    # Startup: discover plugins
    from app.services.plugin_service import discover_plugins
    discover_plugins()

    # Startup: launch Cowrie log watcher as background task
    watcher_task = asyncio.create_task(_start_log_watcher())

    yield

    # Shutdown
    watcher_task.cancel()
    await engine.dispose()


async def _ensure_admin_user():
    """Create the default tenant and admin user on first run."""
    from sqlalchemy import select
    from app.core.database import async_session
    from app.core.security import get_password_hash
    from app.models.tenant import Tenant
    from app.models.user import User

    async with async_session() as db:
        # Ensure default tenant exists
        result = await db.execute(select(Tenant).where(Tenant.slug == "default"))
        tenant = result.scalar_one_or_none()
        if tenant is None:
            tenant = Tenant(
                slug="default",
                name="Default Organization",
                display_name="HoneyAegis",
                primary_color="#f59e0b",
                is_active=True,
            )
            db.add(tenant)
            await db.flush()
            logger.info("Created default tenant")

        # Ensure admin user exists
        result = await db.execute(select(User).where(User.email == settings.admin_email))
        if result.scalar_one_or_none() is None:
            admin = User(
                email=settings.admin_email,
                hashed_password=get_password_hash(settings.admin_password),
                full_name="Admin",
                is_active=True,
                is_superuser=True,
                tenant_id=tenant.id,
            )
            db.add(admin)
            logger.info("Created default admin user: %s", settings.admin_email)

        await db.commit()


async def _start_log_watcher():
    """Start the Cowrie log file watcher."""
    try:
        from app.services.ingestion_service import watch_cowrie_logs
        await watch_cowrie_logs()
    except asyncio.CancelledError:
        logger.info("Log watcher shutting down")
    except Exception as e:
        logger.error("Log watcher error: %s", e, exc_info=True)


app = FastAPI(
    title="HoneyAegis API",
    description="Professional-grade honeypot platform API",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate limiting
app.add_middleware(RateLimitMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(events.router, prefix="/api/v1/events", tags=["events"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(replay.router, prefix="/api/v1/sessions", tags=["replay"])
app.include_router(video.router, prefix="/api/v1/sessions", tags=["video"])
app.include_router(websocket.router, tags=["websocket"])
app.include_router(ai.router, prefix="/api/v1/sessions", tags=["ai"])
app.include_router(sensors.router, prefix="/api/v1/sensors", tags=["sensors"])
app.include_router(config.router, prefix="/api/v1/config", tags=["config"])
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["tenants"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(client_portal.router, prefix="/api/v1/client", tags=["client-portal"])
app.include_router(honey_tokens.router, prefix="/api/v1/honey-tokens", tags=["honey-tokens"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
app.include_router(plugins.router, prefix="/api/v1/plugins", tags=["plugins"])
app.include_router(metrics.router, tags=["metrics"])
app.include_router(export.router, prefix="/api/v1/export", tags=["export"])
app.include_router(console.router, prefix="/api/v1/console", tags=["console"])
