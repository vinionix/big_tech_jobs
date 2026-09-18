from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    log_level: str = "INFO"
    api_port: int = 8000
    cors_allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    database_url: str = (
        "postgresql+asyncpg://big_tech_jobs:change-me-for-local-development"
        "@localhost:5432/big_tech_jobs"
    )
    redis_url: str = "redis://localhost:6379/0"
    ollama_base_url: str | None = "http://localhost:11434"
    ollama_model: str | None = None
    ollama_timeout_seconds: float = 2.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
