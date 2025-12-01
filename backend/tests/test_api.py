import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from backend.kz.db.database import get_async_engine, get_async_session_maker
from backend.kz.main import app
from backend.kz.models import Base


@pytest_asyncio.fixture
async def setup_db():
    """Set up clean database for each test."""
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Dispose engine after test
    await engine.dispose()


@pytest_asyncio.fixture
async def client(setup_db):
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_task(client):
    """Test creating a task via API."""
    response = await client.post(
        "/api/tasks",
        json={"raw_input": "fix the auth bug", "energy_column": "quick_win"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["raw_input"] == "fix the auth bug"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_tasks(client):
    """Test listing tasks."""
    # Create a task first
    await client.post(
        "/api/tasks",
        json={"raw_input": "test task"},
    )

    response = await client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_ship_task(client):
    """Test shipping a task."""
    # Create a task
    create_response = await client.post(
        "/api/tasks",
        json={"raw_input": "ship me"},
    )
    task_id = create_response.json()["id"]

    # Ship it
    response = await client.post(f"/api/tasks/{task_id}/ship")
    assert response.status_code == 200
    data = response.json()
    assert data["energy_column"] == "shipped"
    assert data["shipped_at"] is not None
