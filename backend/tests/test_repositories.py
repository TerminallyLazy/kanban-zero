import pytest
import pytest_asyncio
from sqlalchemy import text

from backend.kz.db.database import get_async_engine, get_async_session_maker
from backend.kz.models import Base, EnergyColumn, TaskCreate
from backend.kz.repositories.task import TaskRepository


@pytest_asyncio.fixture
async def db_session():
    """Create a fresh database session for each test."""
    engine = get_async_engine()

    # Setup: create tables
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Provide session for test
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        yield session

    # Teardown: cleanup
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_task(db_session):
    """Test creating a task."""
    repo = TaskRepository(db_session)
    task_data = TaskCreate(raw_input="fix the auth bug")

    task = await repo.create(task_data, title="Fix the auth bug")

    assert task.id is not None
    assert task.title == "Fix the auth bug"
    assert task.raw_input == "fix the auth bug"
    assert task.energy_column == EnergyColumn.QUICK_WIN.value


@pytest.mark.asyncio
async def test_get_task_by_id(db_session):
    """Test retrieving a task by ID."""
    repo = TaskRepository(db_session)
    task_data = TaskCreate(raw_input="test task")
    created = await repo.create(task_data, title="Test Task")

    retrieved = await repo.get_by_id(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.title == "Test Task"


@pytest.mark.asyncio
async def test_list_tasks_by_column(db_session):
    """Test listing tasks by energy column."""
    repo = TaskRepository(db_session)

    await repo.create(
        TaskCreate(raw_input="quick task", energy_column=EnergyColumn.QUICK_WIN),
        title="Quick Task",
    )
    await repo.create(
        TaskCreate(raw_input="focus task", energy_column=EnergyColumn.HYPERFOCUS),
        title="Focus Task",
    )

    quick_wins = await repo.list_by_column(EnergyColumn.QUICK_WIN)

    assert len(quick_wins) == 1
    assert quick_wins[0].title == "Quick Task"


@pytest.mark.asyncio
async def test_ship_task(db_session):
    """Test shipping (completing) a task."""
    repo = TaskRepository(db_session)
    task = await repo.create(TaskCreate(raw_input="ship me"), title="Ship Me")

    shipped = await repo.ship(task.id)

    assert shipped is not None
    assert shipped.energy_column == EnergyColumn.SHIPPED.value
    assert shipped.shipped_at is not None
