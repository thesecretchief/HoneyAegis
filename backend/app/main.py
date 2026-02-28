"""HoneyAegis Backend - FastAPI Application."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, sessions, events, auth, alerts, replay, video, websocket, ai, sensors, config
from app.core.config import settings
from app.core.database import engine, Base

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

    # Startup: launch Cowrie log watcher as background task
    watcher_task = asyncio.create_task(_start_log_watcher())

    yield

    # Shutdown
    watcher_task.cancel()
    await engine.dispose()


async def _ensure_admin_user():
    """Create the default admin user on first run."""
    from sqlalchemy import select
    from app.core.database import async_session
    from app.core.security import get_password_hash
    from app.models.user import User

    async with async_session() as db:
        result = await db.execute(select(User).where(User.email == settings.admin_email))
        if result.scalar_one_or_none() is None:
            admin = User(
                email=settings.admin_email,
                hashed_password=get_password_hash(settings.admin_password),
                full_name="Admin",
                is_active=True,
                is_superuser=True,
            )
            db.add(admin)
            await db.commit()
            logger.info("Created default admin user: %s", settings.admin_email)


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
    version="0.3.0",
    lifespan=lifespan,
)

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
