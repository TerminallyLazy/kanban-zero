"""Application configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://kz:kz_dev_password@localhost:5432/kanban_zero"

    # AI
    anthropic_api_key: str = ""

    # App
    kz_env: str = "development"

    @property
    def is_development(self) -> bool:
        return self.kz_env == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
