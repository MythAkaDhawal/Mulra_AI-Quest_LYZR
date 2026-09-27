import logging
import os
from typing import Dict
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class SecretManager:
    """
    Mock Cloud Secret Manager utility class.
    Stub for AWS Secrets Manager or Google Secret Manager.
    """

    def __init__(self, provider: str = "aws_secrets_manager"):
        self.provider = provider
        # Simulated cloud secret vault for production environment secret fetching
        self._cloud_secrets: Dict[str, str] = {
            "GROQ_API_KEY": os.getenv("PROD_GROQ_API_KEY", os.getenv("GROQ_API_KEY", "")),
            "LYZR_API_KEY": os.getenv("PROD_LYZR_API_KEY", os.getenv("LYZR_API_KEY", "")),
        }

    def get_secret(self, secret_name: str, default: str = "") -> str:
        """Fetch secret securely from cloud secret vault."""
        logger.info(f"Fetching secret '{secret_name}' securely via {self.provider}")
        secret_val = self._cloud_secrets.get(secret_name)
        if secret_val:
            return secret_val
        return os.getenv(secret_name, default)


class Settings(BaseSettings):
    """Base settings configuration shared across environments."""

    ENVIRONMENT: str = "dev"
    GROQ_API_KEY: str = ""
    LYZR_API_KEY: str = ""
    GROQ_MODEL_ID: str = "openai/gpt-oss-20b"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class DevSettings(Settings):
    """Development environment settings."""

    ENVIRONMENT: str = "dev"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.dev"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


class StagingSettings(Settings):
    """Staging environment settings."""

    ENVIRONMENT: str = "staging"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.staging"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ProdSettings(Settings):
    """Production environment settings integrating secure SecretManager."""

    ENVIRONMENT: str = "prod"
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"

    def model_post_init(self, __context) -> None:
        """Fetch production secrets via SecretManager interface."""
        secret_mgr = SecretManager(provider="aws_secrets_manager")
        prod_groq = secret_mgr.get_secret("GROQ_API_KEY")
        if prod_groq:
            self.GROQ_API_KEY = prod_groq
        prod_lyzr = secret_mgr.get_secret("LYZR_API_KEY")
        if prod_lyzr:
            self.LYZR_API_KEY = prod_lyzr

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.prod"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    """Factory function resolving settings dynamically based on ENVIRONMENT variable."""
    env = os.getenv("ENVIRONMENT", os.getenv("APP_ENV", "dev")).lower()
    if env in ("prod", "production"):
        return ProdSettings()
    elif env in ("staging", "stage"):
        return StagingSettings()
    return DevSettings()


settings = get_settings()
