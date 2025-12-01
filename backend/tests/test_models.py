import pytest
from sqlalchemy import text

from backend.kz.db.database import get_async_engine
from backend.kz.models.base import Base
from backend.kz.models.task import EnergyColumn, Task, TaskCreate
from backend.kz.models.tag import Tag, TagCreate, TaskTag
from backend.kz.models.activity import ActivityLog, Actor, ActivityLogRead


def test_task_create_schema():
    """Test TaskCreate pydantic schema."""
    task = TaskCreate(raw_input="fix the auth bug")
    assert task.raw_input == "fix the auth bug"
    assert task.energy_column == EnergyColumn.QUICK_WIN  # default


def test_task_create_with_energy():
    """Test TaskCreate with explicit energy column."""
    task = TaskCreate(raw_input="design the system", energy_column=EnergyColumn.HYPERFOCUS)
    assert task.energy_column == EnergyColumn.HYPERFOCUS


@pytest.mark.asyncio
async def test_task_table_creation():
    """Test that task table can be created."""
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Verify table exists
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE tablename = 'task'")
        )
        assert result.scalar() == "task"


def test_tag_create_schema():
    """Test TagCreate pydantic schema."""
    tag = TagCreate(name="auth")
    assert tag.name == "auth"
    assert tag.color is None
    assert tag.icon is None


def test_tag_create_with_color():
    """Test TagCreate with color and icon."""
    tag = TagCreate(name="frontend", color="#3B82F6", icon="code")
    assert tag.color == "#3B82F6"
    assert tag.icon == "code"


@pytest.mark.asyncio
async def test_tag_table_creation():
    """Test that tag and task_tag tables can be created."""
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE tablename = 'tag'")
        )
        assert result.scalar() == "tag"

        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE tablename = 'task_tag'")
        )
        assert result.scalar() == "task_tag"


def test_activity_log_read_schema():
    """Test ActivityLogRead schema has correct fields."""
    # Just verify the schema exists and has expected fields
    assert hasattr(ActivityLogRead, "model_fields")
    assert "id" in ActivityLogRead.model_fields
    assert "action" in ActivityLogRead.model_fields
    assert "actor" in ActivityLogRead.model_fields


@pytest.mark.asyncio
async def test_activity_log_table_creation():
    """Test that activity_log table can be created."""
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE tablename = 'activity_log'")
        )
        assert result.scalar() == "activity_log"
