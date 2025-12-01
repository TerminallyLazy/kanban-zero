"""List tasks command."""

import asyncio
from typing import Annotated, Optional

import typer
from rich.console import Console

from cli.kz.api_client import APIClient
from cli.kz.display import display_tasks_by_column, display_tasks_table

console = Console()


def list_tasks(
    column: Annotated[
        Optional[str],
        typer.Option(
            "--column",
            "-c",
            help="Filter by energy column: hyperfocus, quick_win, low_energy",
        ),
    ] = None,
    table: Annotated[
        bool,
        typer.Option("--table", "-t", help="Display as table instead of grouped"),
    ] = False,
) -> None:
    """List all active tasks."""
    asyncio.run(_list_tasks(column, table))


async def _list_tasks(column: str | None, as_table: bool) -> None:
    """Async implementation of list command."""
    try:
        async with APIClient() as client:
            tasks = await client.list_tasks(column=column)

        if as_table:
            display_tasks_table(tasks)
        else:
            display_tasks_by_column(tasks)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
