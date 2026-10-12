from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Apex AI"
    app_environment: str = "development"
    debug: bool = False

    database_url: str | None = None

    mistral_api_key: str | None = None
    mistral_model: str = "codestral-2508"

    expense_mcp_url: str = "https://priteshv1.fastmcp.app/mcp"
    expense_mcp_token: str | None = None
    mcp_allowed_tools: str = ""

    tavily_api_key: str | None = None

    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()