"""Ship (complete) task command."""

import asyncio
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from cli.kz.api_client import APIClient

console = Console()


def ship(
    task_id: Annotated[str, typer.Argument(help="Task ID (full or partial)")],
) -> None:
    """Ship (complete) a task. Celebrate!"""
    asyncio.run(_ship_task(task_id))


async def _ship_task(task_id: str) -> None:
    """Async implementation of ship command."""
    try:
        async with APIClient() as client:
            result = await client.ship_task(task_id)

        console.print(
            Panel(
                f"[bold green]{result['title']}[/bold green]\n\n"
                f"[green]rocket_launch[/green] Shipped!",
                title="[green bold]Task Completed![/green bold]",
                border_style="green",
            )
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
