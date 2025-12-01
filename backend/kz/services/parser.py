"""AI-powered task parsing service."""

import json
import logging
from dataclasses import dataclass

from anthropic import AsyncAnthropic

from backend.kz.config import get_settings
from backend.kz.models import EnergyColumn

logger = logging.getLogger(__name__)

PARSE_PROMPT = """You are a task parser for a Kanban board. Parse the user's input and extract:

1. **title**: A clean, concise task title (imperative form, e.g., "Fix auth bug" not "Fixing auth bug")
2. **energy**: Which energy column fits best:
   - "hyperfocus" - Deep work, complex, requires concentration (>30 min)
   - "quick_win" - Small tasks, quick dopamine hits (<15 min)
   - "low_energy" - Mindless but useful (docs, cleanup, admin)
3. **tags**: 1-3 relevant lowercase tags (e.g., ["auth", "bug", "backend"])

Respond ONLY with valid JSON:
{{"title": "...", "energy": "...", "tags": ["...", "..."]}}

User input: {input}"""


@dataclass
class ParsedTask:
    """Result of parsing a task input."""

    title: str
    energy: EnergyColumn
    tags: list[str]


class TaskParser:
    """AI-powered task intent parser."""

    def __init__(self) -> None:
        settings = get_settings()
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def parse(
        self,
        raw_input: str,
        energy_override: EnergyColumn | None = None,
    ) -> ParsedTask:
        """Parse raw task input into structured data."""
        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=256,
                messages=[
                    {"role": "user", "content": PARSE_PROMPT.format(input=raw_input)}
                ],
            )

            result = json.loads(response.content[0].text)

            energy = energy_override or EnergyColumn(result.get("energy", "quick_win"))
            tags = result.get("tags", [])
            if isinstance(tags, str):
                tags = [tags]

            return ParsedTask(
                title=result.get("title", raw_input),
                energy=energy,
                tags=[t.lower().strip() for t in tags[:5]],  # Max 5 tags
            )

        except Exception as e:
            logger.warning(f"Failed to parse task with AI: {e}")
            # Graceful fallback
            return ParsedTask(
                title=raw_input,
                energy=energy_override or EnergyColumn.QUICK_WIN,
                tags=[],
            )
