from unittest.mock import AsyncMock, patch

from typer.testing import CliRunner

from cli.kz.main import app

runner = CliRunner()


def test_app_version():
    """Test --version flag."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_app_help():
    """Test --help flag."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Kanban Zero" in result.stdout


def test_add_command_help():
    """Test add command shows help."""
    result = runner.invoke(app, ["add", "--help"])
    assert result.exit_code == 0
    assert "Add a new task" in result.stdout


@patch("cli.kz.commands.add.APIClient")
def test_add_task(mock_client_class):
    """Test adding a task."""
    mock_client = AsyncMock()
    mock_client.create_task.return_value = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Fix the auth bug",
        "energy_column": "quick_win",
    }
    mock_client_class.return_value.__aenter__.return_value = mock_client

    result = runner.invoke(app, ["add", "fix the auth bug"])

    assert result.exit_code == 0
    assert "Fix the auth bug" in result.stdout


@patch("cli.kz.commands.add.APIClient")
def test_add_task_with_energy(mock_client_class):
    """Test adding a task with explicit energy."""
    mock_client = AsyncMock()
    mock_client.create_task.return_value = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Refactor the whole thing",
        "energy_column": "hyperfocus",
    }
    mock_client_class.return_value.__aenter__.return_value = mock_client

    result = runner.invoke(app, ["add", "refactor the whole thing", "--energy", "hyperfocus"])

    assert result.exit_code == 0
    mock_client.create_task.assert_called_once()


@patch("cli.kz.commands.list.APIClient")
def test_list_tasks(mock_client_class):
    """Test listing tasks."""
    mock_client = AsyncMock()
    mock_client.list_tasks.return_value = [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Task One",
            "energy_column": "quick_win",
            "created_at": "2025-01-01T00:00:00Z",
        },
        {
            "id": "223e4567-e89b-12d3-a456-426614174000",
            "title": "Task Two",
            "energy_column": "hyperfocus",
            "created_at": "2025-01-01T00:00:00Z",
        },
    ]
    mock_client_class.return_value.__aenter__.return_value = mock_client

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "Task One" in result.stdout
    assert "Task Two" in result.stdout


@patch("cli.kz.commands.list.APIClient")
def test_list_tasks_by_column(mock_client_class):
    """Test listing tasks filtered by column."""
    mock_client = AsyncMock()
    mock_client.list_tasks.return_value = [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Quick Task",
            "energy_column": "quick_win",
            "created_at": "2025-01-01T00:00:00Z",
        },
    ]
    mock_client_class.return_value.__aenter__.return_value = mock_client

    result = runner.invoke(app, ["list", "--column", "quick_win"])

    assert result.exit_code == 0
    mock_client.list_tasks.assert_called_once_with(column="quick_win")


@patch("cli.kz.commands.ship.APIClient")
def test_ship_task(mock_client_class):
    """Test shipping a task."""
    mock_client = AsyncMock()
    mock_client.ship_task.return_value = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Completed Task",
        "energy_column": "shipped",
        "shipped_at": "2025-01-01T12:00:00Z",
    }
    mock_client_class.return_value.__aenter__.return_value = mock_client

    result = runner.invoke(app, ["ship", "123e4567"])

    assert result.exit_code == 0
    assert "Shipped" in result.stdout or "shipped" in result.stdout.lower()


@patch("cli.kz.commands.wins.APIClient")
def test_wins_command(mock_client_class):
    """Test wins command (quick_win shortcut)."""
    mock_client = AsyncMock()
    mock_client.list_tasks.return_value = [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Quick Win",
            "energy_column": "quick_win",
            "created_at": "2025-01-01T00:00:00Z",
        },
    ]
    mock_client_class.return_value.__aenter__.return_value = mock_client

    result = runner.invoke(app, ["wins"])

    assert result.exit_code == 0
    mock_client.list_tasks.assert_called_once_with(column="quick_win")
