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
