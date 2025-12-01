"""CLI configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class CLISettings(BaseSettings):
    """CLI settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_base_url: str = "http://localhost:8000"


@lru_cache
def get_cli_settings() -> CLISettings:
    """Get cached CLI settings."""
    return CLISettings()
