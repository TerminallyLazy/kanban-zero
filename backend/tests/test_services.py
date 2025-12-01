import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.kz.models import EnergyColumn
from backend.kz.services.parser import ParsedTask, TaskParser


@pytest.fixture
def mock_anthropic():
    """Mock Anthropic client."""
    with patch("backend.kz.services.parser.AsyncAnthropic") as mock:
        yield mock


@pytest.mark.asyncio
async def test_parser_extracts_title(mock_anthropic):
    """Test that parser extracts a clean title."""
    mock_client = AsyncMock()

    # Create a mock content object with text attribute
    mock_content = MagicMock()
    mock_content.text = '{"title": "Fix authentication bug", "energy": "quick_win", "tags": ["auth", "bug"]}'

    mock_response = MagicMock()
    mock_response.content = [mock_content]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    parser = TaskParser()
    result = await parser.parse("fix the auth bug thats been bothering me")

    assert result.title == "Fix authentication bug"
    assert result.energy == EnergyColumn.QUICK_WIN


@pytest.mark.asyncio
async def test_parser_extracts_tags(mock_anthropic):
    """Test that parser extracts relevant tags."""
    mock_client = AsyncMock()

    # Create a mock content object with text attribute
    mock_content = MagicMock()
    mock_content.text = '{"title": "Build Slack integration", "energy": "hyperfocus", "tags": ["slack", "integration"]}'

    mock_response = MagicMock()
    mock_response.content = [mock_content]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    parser = TaskParser()
    result = await parser.parse("build the slack integration for notifications")

    assert "slack" in result.tags
    assert result.energy == EnergyColumn.HYPERFOCUS


@pytest.mark.asyncio
async def test_parser_handles_explicit_energy(mock_anthropic):
    """Test that explicit energy override is respected."""
    mock_client = AsyncMock()

    # Create a mock content object with text attribute
    mock_content = MagicMock()
    mock_content.text = '{"title": "Update README", "energy": "quick_win", "tags": ["docs"]}'

    mock_response = MagicMock()
    mock_response.content = [mock_content]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.return_value = mock_client

    parser = TaskParser()
    result = await parser.parse("update readme", energy_override=EnergyColumn.LOW_ENERGY)

    # Override should take precedence
    assert result.energy == EnergyColumn.LOW_ENERGY


@pytest.mark.asyncio
async def test_parser_fallback_on_error(mock_anthropic):
    """Test graceful fallback when AI fails."""
    mock_client = AsyncMock()
    mock_client.messages.create.side_effect = Exception("API error")
    mock_anthropic.return_value = mock_client

    parser = TaskParser()
    result = await parser.parse("some task that fails")

    # Should return input as title, default energy
    assert result.title == "some task that fails"
    assert result.energy == EnergyColumn.QUICK_WIN
    assert result.tags == []
