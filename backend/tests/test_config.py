import os
from backend.core.config import (
    DevSettings,
    StagingSettings,
    ProdSettings,
    SecretManager,
    get_settings,
)


def test_dev_settings():
    os.environ["ENVIRONMENT"] = "dev"
    s = get_settings()
    assert isinstance(s, DevSettings)
    assert s.ENVIRONMENT == "dev"
    assert s.DEBUG is True
    assert s.LOG_LEVEL == "DEBUG"


def test_staging_settings():
    os.environ["ENVIRONMENT"] = "staging"
    s = get_settings()
    assert isinstance(s, StagingSettings)
    assert s.ENVIRONMENT == "staging"
    assert s.DEBUG is False
    assert s.LOG_LEVEL == "INFO"


def test_prod_settings_secret_manager():
    os.environ["ENVIRONMENT"] = "prod"
    os.environ["PROD_GROQ_API_KEY"] = "mock_prod_groq_key_123"
    s = get_settings()
    assert isinstance(s, ProdSettings)
    assert s.ENVIRONMENT == "prod"
    assert s.DEBUG is False
    assert s.LOG_LEVEL == "WARNING"
    assert s.GROQ_API_KEY == "mock_prod_groq_key_123"


def test_secret_manager_standalone():
    sm = SecretManager(provider="aws_secrets_manager")
    secret = sm.get_secret("GROQ_API_KEY", default="default_key")
    assert secret != "" or secret == "default_key"
