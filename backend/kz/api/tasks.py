"""Task API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.kz.db.database import get_async_session
from backend.kz.models import EnergyColumn, TaskCreate, TaskRead, TaskUpdate
from backend.kz.repositories.task import TaskRepository
from backend.kz.services.parser import TaskParser

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_async_session)]


def get_task_repository(session: DbSession) -> TaskRepository:
    """Dependency for task repository."""
    return TaskRepository(session)


TaskRepo = Annotated[TaskRepository, Depends(get_task_repository)]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TaskRead)
async def create_task(data: TaskCreate, repo: TaskRepo) -> TaskRead:
    """Create a new task with AI parsing."""
    parser = TaskParser()
    parsed = await parser.parse(data.raw_input, energy_override=data.energy_column)

    task = await repo.create(
        data=TaskCreate(
            raw_input=data.raw_input,
            energy_column=parsed.energy,
            created_via=data.created_via,
        ),
        title=parsed.title,
    )
    return TaskRead.model_validate(task)


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    repo: TaskRepo,
    column: EnergyColumn | None = None,
) -> list[TaskRead]:
    """List tasks, optionally filtered by column."""
    if column:
        tasks = await repo.list_by_column(column)
    else:
        tasks = await repo.list_active()
    return [TaskRead.model_validate(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: UUID, repo: TaskRepo) -> TaskRead:
    """Get a specific task by ID."""
    task = await repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.model_validate(task)


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(task_id: UUID, data: TaskUpdate, repo: TaskRepo) -> TaskRead:
    """Update a task."""
    task = await repo.update(task_id, data)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID, repo: TaskRepo) -> None:
    """Delete a task."""
    deleted = await repo.delete(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")


@router.post("/{task_id}/ship", response_model=TaskRead)
async def ship_task(task_id: UUID, repo: TaskRepo) -> TaskRead:
    """Mark a task as shipped (completed)."""
    task = await repo.ship(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.model_validate(task)
