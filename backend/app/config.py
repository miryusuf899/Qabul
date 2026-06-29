from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import AnyUrl, BeforeValidator, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


def _split_origins(value: str | list[str]) -> list[str]:
    if isinstance(value, list):
        return value
    return [origin.strip() for origin in value.split(",") if origin.strip()]


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/qabul"
    secret_key: str = "change_this_secret_key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    cors_origins: Annotated[list[str], NoDecode, BeforeValidator(_split_origins)] = Field(
        default_factory=lambda: DEFAULT_CORS_ORIGINS.copy()
    )
    ai_provider: str = "mock"
    gemini_api_key: str | None = None
    groq_api_key: str | None = None
    openai_api_key: str | None = None
    telegram_bot_token: str | None = None
    default_business_id: int = 1
    backend_api_url: str = "http://localhost:8000/api/v1"
    timezone: str = "Asia/Dushanbe"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins")
    @classmethod
    def validate_origins(cls, origins: list[str]) -> list[str]:
        if "*" in origins:
            return origins
        for origin in origins:
            AnyUrl(origin)
        return origins


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
