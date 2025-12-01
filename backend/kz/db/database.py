"""Database connection and session management."""

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from backend.kz.config import get_settings


@lru_cache
def get_async_engine() -> AsyncEngine:
    """Get cached async database engine."""
    settings = get_settings()
    return create_async_engine(
        settings.database_url,
        echo=settings.is_development,
        pool_pre_ping=True,
    )


def get_async_session_maker() -> async_sessionmaker[AsyncSession]:
    """Get async session maker."""
    return async_sessionmaker(
        get_async_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    async_session = get_async_session_maker()
    async with async_session() as session:
        yield session
