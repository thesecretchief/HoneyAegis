"""HoneyToken model — decoy credentials and files that trigger alerts on use."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class HoneyToken(Base):
    __tablename__ = "honey_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE")
    )
    token_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "credential", "file", "url", "api_key"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Credential tokens
    username: Mapped[str | None] = mapped_column(String(255))
    password: Mapped[str | None] = mapped_column(String(255))

    # File tokens
    filename: Mapped[str | None] = mapped_column(String(500))
    file_path: Mapped[str | None] = mapped_column(String(1000))

    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    trigger_count: Mapped[int] = mapped_column(Integer, default=0)
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Alert config
    alert_severity: Mapped[str] = mapped_column(String(20), default="critical")
    webhook_url: Mapped[str | None] = mapped_column(String(1000))
    extra_data: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
