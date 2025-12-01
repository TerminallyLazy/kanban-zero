"""Activity log model and schemas."""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.kz.models.base import Base


class Actor(StrEnum):
    """Who performed the action."""

    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class ActivityLog(Base):
    """Activity log database model for audit trail and dopamine fuel."""

    __tablename__ = "activity_log"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    task_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("task.id", ondelete="SET NULL"), nullable=True
    )
    actor: Mapped[str] = mapped_column(String(10), nullable=False, default=Actor.USER.value)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


# Pydantic schemas


class ActivityLogRead(BaseModel):
    """Schema for reading an activity log entry."""

    id: UUID
    task_id: UUID | None
    actor: Actor
    action: str
    details: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}
