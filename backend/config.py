"""
Application configuration.
Settings are loaded from environment variables and the .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "sqlite:///./app.db"

    # Security
    secret_key: str = "dev-secret-key-change-in-production"

    # Application
    app_env: str = "development"
    debug: bool = True
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    # WhatsApp
    whatsapp_live_mode: bool = False
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_webhook_verify_token: str = ""

    # Clustering
    clustering_random_seed: int = 42
    clustering_k_min: int = 2
    clustering_k_max: int = 10

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
