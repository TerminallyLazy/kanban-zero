"""Task model and schemas."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.kz.models.base import Base


class EnergyColumn(StrEnum):
    """Energy-based Kanban columns."""

    HYPERFOCUS = "hyperfocus"
    QUICK_WIN = "quick_win"
    LOW_ENERGY = "low_energy"
    SHIPPED = "shipped"


class CreatedVia(StrEnum):
    """How the task was created."""

    CLI = "cli"
    SLACK = "slack"
    WEB = "web"
    API = "api"


class Task(Base):
    """Task database model."""

    __tablename__ = "task"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_input: Mapped[str] = mapped_column(Text, nullable=False)

    energy_column: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EnergyColumn.QUICK_WIN.value
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    shipped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_via: Mapped[str] = mapped_column(
        String(20), nullable=False, default=CreatedVia.CLI.value
    )


# Pydantic schemas


class TaskCreate(BaseModel):
    """Schema for creating a task."""

    raw_input: str = Field(..., min_length=1, max_length=5000)
    energy_column: EnergyColumn = EnergyColumn.QUICK_WIN
    created_via: CreatedVia = CreatedVia.CLI


class TaskRead(BaseModel):
    """Schema for reading a task."""

    id: UUID
    title: str
    body: str | None
    raw_input: str
    energy_column: EnergyColumn
    position: int
    created_at: datetime
    updated_at: datetime
    shipped_at: datetime | None
    created_via: CreatedVia

    model_config = {"from_attributes": True}


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: str | None = None
    body: str | None = None
    energy_column: EnergyColumn | None = None
    position: int | None = None
