"""Add task command."""

import asyncio
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel

from cli.kz.api_client import APIClient

console = Console()

ENERGY_ICONS = {
    "hyperfocus": "[red]fire[/red]",
    "quick_win": "[yellow]bolt[/yellow]",
    "low_energy": "[blue]self_improvement[/blue]",
    "shipped": "[green]rocket_launch[/green]",
}


def add(
    task: Annotated[str, typer.Argument(help="Task description (free text)")],
    energy: Annotated[
        Optional[str],
        typer.Option(
            "--energy",
            "-e",
            help="Energy column: hyperfocus, quick_win, low_energy",
        ),
    ] = None,
) -> None:
    """Add a new task with AI parsing."""
    asyncio.run(_add_task(task, energy))


async def _add_task(task: str, energy: str | None) -> None:
    """Async implementation of add command."""
    try:
        async with APIClient() as client:
            result = await client.create_task(task, energy_column=energy)

        icon = ENERGY_ICONS.get(result["energy_column"], "")
        console.print(
            Panel(
                f"[bold]{result['title']}[/bold]\n\n"
                f"{icon} {result['energy_column'].replace('_', ' ').title()}",
                title="[green]Task Added[/green]",
                subtitle=f"ID: {result['id'][:8]}",
            )
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
