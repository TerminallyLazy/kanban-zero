"""End-to-end integration tests for Kanban Zero.

Tests the full task lifecycle through the API:
- Create task (AI parsing)
- List tasks
- Filter by column
- Update task
- Ship task (mark complete)
- Delete task
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from backend.kz.db.database import get_async_engine
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
    await engine.dispose()


@pytest_asyncio.fixture
async def client(setup_db):
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_full_task_lifecycle(client):
    """Test complete task lifecycle: create -> list -> ship.

    This test simulates a typical user workflow:
    1. Create a new task with natural language input
    2. Verify it appears in the task list
    3. Ship (complete) the task
    4. Verify it's marked as shipped
    """
    # Step 1: Create a task
    create_response = await client.post(
        "/api/tasks",
        json={
            "raw_input": "Write integration tests for the API",
            "created_via": "api",
        },
    )
    assert create_response.status_code == 201
    created_task = create_response.json()

    assert created_task["id"] is not None
    assert created_task["raw_input"] == "Write integration tests for the API"
    assert created_task["title"] is not None  # AI should parse a title
    assert created_task["energy_column"] in ["quick_win", "hyperfocus", "low_energy"]
    assert created_task["shipped_at"] is None

    task_id = created_task["id"]

    # Step 2: List all tasks
    list_response = await client.get("/api/tasks")
    assert list_response.status_code == 200
    all_tasks = list_response.json()

    assert len(all_tasks) == 1
    assert all_tasks[0]["id"] == task_id

    # Step 3: Ship the task
    ship_response = await client.post(f"/api/tasks/{task_id}/ship")
    assert ship_response.status_code == 200
    shipped_task = ship_response.json()

    assert shipped_task["id"] == task_id
    assert shipped_task["energy_column"] == "shipped"
    assert shipped_task["shipped_at"] is not None

    # Step 4: Verify shipped tasks don't show in active list
    active_response = await client.get("/api/tasks")
    assert active_response.status_code == 200
    active_tasks = active_response.json()

    # Active tasks should not include shipped tasks
    assert len(active_tasks) == 0


@pytest.mark.asyncio
async def test_column_filtering(client):
    """Test filtering tasks by energy column.

    Create tasks in different columns and verify filtering works correctly.
    """
    # Create tasks in different columns
    quick_win_response = await client.post(
        "/api/tasks",
        json={
            "raw_input": "Quick fix for the button",
            "energy_column": "quick_win",
        },
    )
    assert quick_win_response.status_code == 201

    hyperfocus_response = await client.post(
        "/api/tasks",
        json={
            "raw_input": "Refactor the entire auth system",
            "energy_column": "hyperfocus",
        },
    )
    assert hyperfocus_response.status_code == 201

    low_energy_response = await client.post(
        "/api/tasks",
        json={
            "raw_input": "Review some documentation",
            "energy_column": "low_energy",
        },
    )
    assert low_energy_response.status_code == 201

    # Filter by quick_win
    quick_win_list = await client.get("/api/tasks?column=quick_win")
    assert quick_win_list.status_code == 200
    quick_wins = quick_win_list.json()
    assert len(quick_wins) == 1
    assert quick_wins[0]["energy_column"] == "quick_win"

    # Filter by hyperfocus
    hyperfocus_list = await client.get("/api/tasks?column=hyperfocus")
    assert hyperfocus_list.status_code == 200
    hyperfocus_tasks = hyperfocus_list.json()
    assert len(hyperfocus_tasks) == 1
    assert hyperfocus_tasks[0]["energy_column"] == "hyperfocus"

    # Filter by low_energy
    low_energy_list = await client.get("/api/tasks?column=low_energy")
    assert low_energy_list.status_code == 200
    low_energy_tasks = low_energy_list.json()
    assert len(low_energy_tasks) == 1
    assert low_energy_tasks[0]["energy_column"] == "low_energy"

    # List all active tasks (should get all 3)
    all_response = await client.get("/api/tasks")
    assert all_response.status_code == 200
    all_tasks = all_response.json()
    assert len(all_tasks) == 3


@pytest.mark.asyncio
async def test_task_update(client):
    """Test updating a task's properties."""
    # Create a task
    create_response = await client.post(
        "/api/tasks",
        json={
            "raw_input": "Initial task description",
            "energy_column": "quick_win",
        },
    )
    assert create_response.status_code == 201
    task = create_response.json()
    task_id = task["id"]

    # Update the task's energy column
    update_response = await client.patch(
        f"/api/tasks/{task_id}",
        json={
            "energy_column": "hyperfocus",
        },
    )
    assert update_response.status_code == 200
    updated_task = update_response.json()

    assert updated_task["id"] == task_id
    assert updated_task["energy_column"] == "hyperfocus"
    assert updated_task["raw_input"] == "Initial task description"

    # Verify the update persisted
    get_response = await client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 200
    fetched_task = get_response.json()
    assert fetched_task["energy_column"] == "hyperfocus"


@pytest.mark.asyncio
async def test_task_deletion(client):
    """Test deleting a task."""
    # Create a task
    create_response = await client.post(
        "/api/tasks",
        json={
            "raw_input": "Task to be deleted",
        },
    )
    assert create_response.status_code == 201
    task = create_response.json()
    task_id = task["id"]

    # Delete the task
    delete_response = await client.delete(f"/api/tasks/{task_id}")
    assert delete_response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 404

    # Verify it doesn't show in list
    list_response = await client.get("/api/tasks")
    assert list_response.status_code == 200
    tasks = list_response.json()
    assert len(tasks) == 0


@pytest.mark.asyncio
async def test_multiple_tasks_workflow(client):
    """Test a realistic workflow with multiple tasks.

    Simulates a user:
    1. Adding several tasks
    2. Shipping some of them
    3. Moving tasks between columns
    4. Deleting completed work
    """
    # Add multiple tasks
    tasks = []
    for i, text in enumerate([
        "Fix the CSS bug",
        "Write tests for auth",
        "Deploy to production",
    ]):
        response = await client.post(
            "/api/tasks",
            json={"raw_input": text},
        )
        assert response.status_code == 201
        tasks.append(response.json())

    # Verify we have 3 active tasks
    list_response = await client.get("/api/tasks")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 3

    # Ship the first task
    ship_response = await client.post(f"/api/tasks/{tasks[0]['id']}/ship")
    assert ship_response.status_code == 200

    # Now we should have 2 active tasks
    list_response = await client.get("/api/tasks")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2

    # Move second task to hyperfocus
    update_response = await client.patch(
        f"/api/tasks/{tasks[1]['id']}",
        json={"energy_column": "hyperfocus"},
    )
    assert update_response.status_code == 200

    # Filter for hyperfocus tasks
    hyperfocus_response = await client.get("/api/tasks?column=hyperfocus")
    assert hyperfocus_response.status_code == 200
    hyperfocus_tasks = hyperfocus_response.json()
    assert len(hyperfocus_tasks) == 1
    assert hyperfocus_tasks[0]["id"] == tasks[1]["id"]

    # Delete the third task
    delete_response = await client.delete(f"/api/tasks/{tasks[2]['id']}")
    assert delete_response.status_code == 204

    # Should have 1 active task remaining
    final_list = await client.get("/api/tasks")
    assert final_list.status_code == 200
    assert len(final_list.json()) == 1


@pytest.mark.asyncio
async def test_task_not_found_errors(client):
    """Test appropriate error handling for non-existent tasks."""
    fake_id = "00000000-0000-0000-0000-000000000000"

    # Get non-existent task
    get_response = await client.get(f"/api/tasks/{fake_id}")
    assert get_response.status_code == 404

    # Update non-existent task
    update_response = await client.patch(
        f"/api/tasks/{fake_id}",
        json={"energy_column": "quick_win"},
    )
    assert update_response.status_code == 404

    # Ship non-existent task
    ship_response = await client.post(f"/api/tasks/{fake_id}/ship")
    assert ship_response.status_code == 404

    # Delete non-existent task
    delete_response = await client.delete(f"/api/tasks/{fake_id}")
    assert delete_response.status_code == 404


@pytest.mark.asyncio
async def test_health_check_integration(client):
    """Test health check endpoint as part of integration."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "env" in data
