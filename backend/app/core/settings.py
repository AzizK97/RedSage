import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load .env file immediately when this module is imported
# This ensures environment variables are available before Settings is instantiated
_backend_root = Path(__file__).parent.parent.parent
_env_path = _backend_root / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

@dataclass
class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "RedSage API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    ENV: str = os.getenv("ENV", "dev")

    PLATFORM_POSTGRES_URL: str = os.getenv("PLATFORM_POSTGRES_URL", "")
    REDMINE_URL: str = os.getenv("REDMINE_URL", "")
    REDMINE_API_KEY: str = os.getenv("REDMINE_API_KEY", "")

    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me")
    JWT_ALG: str = os.getenv("JWT_ALG", "HS256")
    JWT_ISSUER: str = os.getenv("JWT_ISSUER", "")
    JWT_AUDIENCE: str = os.getenv("JWT_AUDIENCE", "")

    # LLM Configuration (Ollama)
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemma4:26b")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://192.168.130.177:11434")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "1.0"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    LLM_TOP_P: float = float(os.getenv("LLM_TOP_P", "0.95"))
    LLM_TOP_K: int = int(os.getenv("LLM_TOP_K", "64"))

    CORS_ORIGINS: list[str] = field(
        default_factory=lambda: [
            o.strip()
            for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
            if o.strip()
        ]
    )

settings = Settings()


def get_settings() -> Settings:
    """Return the singleton settings instance."""
    return settings