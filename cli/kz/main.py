"""Kanban Zero CLI entry point."""

from typing import Annotated, Optional

import typer

from cli.kz import __version__
from cli.kz.commands.add import add
from cli.kz.commands.list import list_tasks
from cli.kz.commands.ship import ship
from cli.kz.commands.wins import wins

app = typer.Typer(
    name="kz",
    help="Kanban Zero - AI-native, energy-aware task management for ADHD brains",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"Kanban Zero CLI v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """Kanban Zero - Your ADHD-friendly task companion."""
    pass


# Register commands
app.command()(add)
app.command("list")(list_tasks)
app.command()(ship)
app.command()(wins)


if __name__ == "__main__":
    app()
