"""Quick wins shortcut command."""

import asyncio

import typer
from rich.console import Console

from cli.kz.api_client import APIClient
from cli.kz.display import display_tasks_table

console = Console()


def wins() -> None:
    """Show quick win tasks only. Easy dopamine hits!"""
    asyncio.run(_show_wins())


async def _show_wins() -> None:
    """Async implementation of wins command."""
    try:
        async with APIClient() as client:
            tasks = await client.list_tasks(column="quick_win")

        if not tasks:
            console.print("[yellow]No quick wins right now. Add some![/yellow]")
            console.print("[dim]kz add 'small task' --energy quick_win[/dim]")
            return

        console.print("[yellow bold]bolt QUICK WINS[/yellow bold]\n")
        display_tasks_table(tasks, title="Ready for easy wins?")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
