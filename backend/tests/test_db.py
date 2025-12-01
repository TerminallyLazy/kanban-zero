import pytest
from sqlalchemy import text

from backend.kz.db.database import get_async_engine


@pytest.mark.asyncio
async def test_database_connection():
    """Verify we can connect to the database."""
    engine = get_async_engine()
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_pgvector_extension():
    """Verify pgvector extension is available."""
    engine = get_async_engine()
    async with engine.connect() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        result = await conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        )
        assert result.scalar() == "vector"
