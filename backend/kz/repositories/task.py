"""Task repository for database operations."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.kz.models import EnergyColumn, Task, TaskCreate, TaskUpdate


class TaskRepository:
    """Repository for Task database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: TaskCreate, title: str, body: str | None = None) -> Task:
        """Create a new task."""
        task = Task(
            title=title,
            body=body,
            raw_input=data.raw_input,
            energy_column=data.energy_column.value,
            created_via=data.created_via.value,
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_by_id(self, task_id: UUID) -> Task | None:
        """Get a task by ID."""
        result = await self.session.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    async def get_by_short_id(self, short_id: str) -> Task | None:
        """Get a task by partial ID match (first N characters)."""
        result = await self.session.execute(
            select(Task).where(Task.id.cast(str).startswith(short_id))
        )
        return result.scalar_one_or_none()

    async def list_by_column(self, column: EnergyColumn) -> list[Task]:
        """List all tasks in a specific energy column."""
        result = await self.session.execute(
            select(Task)
            .where(Task.energy_column == column.value)
            .order_by(Task.position, Task.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_active(self) -> list[Task]:
        """List all non-shipped tasks."""
        result = await self.session.execute(
            select(Task)
            .where(Task.energy_column != EnergyColumn.SHIPPED.value)
            .order_by(Task.energy_column, Task.position, Task.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, task_id: UUID, data: TaskUpdate) -> Task | None:
        """Update a task."""
        task = await self.get_by_id(task_id)
        if task is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "energy_column" and value is not None:
                value = value.value
            setattr(task, key, value)

        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def ship(self, task_id: UUID) -> Task | None:
        """Mark a task as shipped."""
        task = await self.get_by_id(task_id)
        if task is None:
            return None

        task.energy_column = EnergyColumn.SHIPPED.value
        task.shipped_at = datetime.now(timezone.utc)

        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, task_id: UUID) -> bool:
        """Delete a task."""
        task = await self.get_by_id(task_id)
        if task is None:
            return False

        await self.session.delete(task)
        await self.session.commit()
        return True
