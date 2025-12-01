"""Rich display helpers for CLI output."""

from rich.console import Console
from rich.table import Table

console = Console()

ENERGY_STYLES = {
    "hyperfocus": ("red", "local_fire_department"),
    "quick_win": ("yellow", "bolt"),
    "low_energy": ("blue", "self_improvement"),
    "shipped": ("green", "rocket_launch"),
}


def display_tasks_table(tasks: list[dict], title: str = "Tasks") -> None:
    """Display tasks in a formatted table."""
    if not tasks:
        console.print("[dim]No tasks found.[/dim]")
        return

    table = Table(title=title, show_header=True, header_style="bold")
    table.add_column("ID", style="dim", width=8)
    table.add_column("Title", style="bold")
    table.add_column("Energy", justify="center")

    for task in tasks:
        energy = task["energy_column"]
        style, icon = ENERGY_STYLES.get(energy, ("white", "task"))
        energy_display = f"[{style}]{icon}[/{style}]"

        table.add_row(
            task["id"][:8],
            task["title"],
            energy_display,
        )

    console.print(table)


def display_tasks_by_column(tasks: list[dict]) -> None:
    """Display tasks grouped by energy column."""
    columns = {
        "hyperfocus": [],
        "quick_win": [],
        "low_energy": [],
    }

    for task in tasks:
        col = task["energy_column"]
        if col in columns:
            columns[col].append(task)

    for col_name, col_tasks in columns.items():
        if col_tasks:
            style, icon = ENERGY_STYLES.get(col_name, ("white", "task"))
            console.print(f"\n[{style} bold]{icon} {col_name.upper().replace('_', ' ')}[/{style} bold]")
            for task in col_tasks:
                console.print(f"  [{style}]•[/{style}] {task['title']} [dim]({task['id'][:8]})[/dim]")
