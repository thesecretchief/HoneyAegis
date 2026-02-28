"""Webhook model — auto-response hooks triggered by alerts and events."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Webhook(Base):
    __tablename__ = "webhooks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    secret: Mapped[str | None] = mapped_column(String(255))

    # Trigger conditions
    trigger_on: Mapped[str] = mapped_column(
        String(50), nullable=False, default="alert"
    )  # "alert", "session", "honey_token", "malware"
    severity_filter: Mapped[str | None] = mapped_column(
        String(50)
    )  # "critical", "high", "medium", "low" or null for all

    # HTTP config
    http_method: Mapped[str] = mapped_column(String(10), default="POST")
    headers: Mapped[dict] = mapped_column(JSONB, default=dict)
    payload_template: Mapped[dict | None] = mapped_column(JSONB)

    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    last_executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_status_code: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
