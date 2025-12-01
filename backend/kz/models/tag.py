"""Tag model and schemas."""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Float, ForeignKey, String, func, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.kz.models.base import Base


class Tag(Base):
    """Tag database model."""

    __tablename__ = "tag"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)  # hex color
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)  # Material icon
    auto_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    tasks: Mapped[list["TaskTag"]] = relationship(back_populates="tag")


class TaskTag(Base):
    """Many-to-many junction table for tasks and tags."""

    __tablename__ = "task_tag"

    task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("task.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True
    )
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-1 if AI-assigned
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    tag: Mapped["Tag"] = relationship(back_populates="tasks")


# Pydantic schemas


class TagCreate(BaseModel):
    """Schema for creating a tag."""

    name: str = Field(..., min_length=1, max_length=100)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: str | None = Field(None, max_length=50)


class TagRead(BaseModel):
    """Schema for reading a tag."""

    id: UUID
    name: str
    color: str | None
    icon: str | None
    auto_generated: bool

    model_config = {"from_attributes": True}
