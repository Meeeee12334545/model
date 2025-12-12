from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")

    env: str = Field(default="dev")
    debug: bool = Field(default=True)
    secret_key: str = Field(default="changeme")
    database_url: str = Field(
        default="sqlite+aiosqlite:///./app.db",
        description="SQLAlchemy database URL; prefer Postgres in production",
    )
    app_name: str = Field(default="Sewer Flow Model API")
    cors_allow_origins: list[str] = Field(default_factory=lambda: ["*"])


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
