from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VoxHire AI API"
    environment: str = "development"
    log_level: str = "INFO"
    database_url: str = Field(min_length=1)
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=10, ge=1, le=60)
    refresh_token_expire_days: int = Field(default=7, ge=1, le=30)
    refresh_cookie_name: str = "voxhire_refresh_token"
    refresh_cookie_secure: bool = False
    auth_rate_limit_max_attempts: int = Field(default=10, ge=1, le=100)
    auth_rate_limit_window_seconds: int = Field(default=300, ge=10, le=3600)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
