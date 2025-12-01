"""HTTP client for Kanban Zero API."""

from types import TracebackType
from typing import Any, Self

import httpx

from cli.kz.config import get_cli_settings


class APIClient:
    """Async HTTP client for the Kanban Zero API."""

    def __init__(self) -> None:
        settings = get_cli_settings()
        self.base_url = settings.api_base_url
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> Self:
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Client not initialized. Use 'async with APIClient()' context.")
        return self._client

    async def create_task(
        self,
        raw_input: str,
        energy_column: str | None = None,
        created_via: str = "cli",
    ) -> dict[str, Any]:
        """Create a new task."""
        payload: dict[str, Any] = {
            "raw_input": raw_input,
            "created_via": created_via,
        }
        if energy_column:
            payload["energy_column"] = energy_column

        response = await self.client.post("/api/tasks", json=payload)
        response.raise_for_status()
        return response.json()

    async def list_tasks(self, column: str | None = None) -> list[dict[str, Any]]:
        """List tasks, optionally filtered by column."""
        params = {}
        if column:
            params["column"] = column
        response = await self.client.get("/api/tasks", params=params)
        response.raise_for_status()
        return response.json()

    async def ship_task(self, task_id: str) -> dict[str, Any]:
        """Ship (complete) a task."""
        response = await self.client.post(f"/api/tasks/{task_id}/ship")
        response.raise_for_status()
        return response.json()

    async def get_task(self, task_id: str) -> dict[str, Any]:
        """Get a specific task."""
        response = await self.client.get(f"/api/tasks/{task_id}")
        response.raise_for_status()
        return response.json()
