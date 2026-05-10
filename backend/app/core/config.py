from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    app_name: str = "Sorota Backend"
    app_port: int = 8000
    app_debug: bool = True

    database_url: str = "sqlite+pysqlite:///./sorota_local.db"

    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_default_model: str = "gpt-4.1-mini"
    openai_reasoning_model: str = "gpt-4.1"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_prompt_version: str = "v1"

    internal_api_key: str | None = None
    whatsapp_bot_base_url: str = "http://localhost:3001"
    whatsapp_bot_internal_token: str | None = None

    enable_early_warning_auto_send: bool = False
    early_warning_max_per_customer_per_day: int = 1
    early_warning_max_per_customer_per_week: int = 3

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
