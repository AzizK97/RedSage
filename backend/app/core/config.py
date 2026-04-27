import os
from dataclasses import dataclass, field

@dataclass
class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "RedSage API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    ENV: str = os.getenv("ENV", "dev")

    PLATFORM_POSTGRES_URL: str = os.getenv("PLATFORM_POSTGRES_URL", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6380/0")
    REDMINE_URL: str = os.getenv("REDMINE_URL", "")
    REDMINE_API_KEY: str = os.getenv("REDMINE_API_KEY", "")
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")

    ENABLE_MONITORING: bool = os.getenv("ENABLE_MONITORING", "false").lower() == "true"
    MONITORING_INTERVAL_SECONDS: int = int(os.getenv("MONITORING_INTERVAL_SECONDS", "1800"))
    MONITORING_ALERT_COOLDOWN_SECONDS: int = int(os.getenv("MONITORING_ALERT_COOLDOWN_SECONDS", "3600"))
    MONITORING_DUE_SOON_HOURS: int = int(os.getenv("MONITORING_DUE_SOON_HOURS", "48"))
    MONITORING_CACHE_TTL_SECONDS: int = int(os.getenv("MONITORING_CACHE_TTL_SECONDS", "120"))

    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me")
    JWT_ALG: str = os.getenv("JWT_ALG", "HS256")
    JWT_ISSUER: str = os.getenv("JWT_ISSUER", "")
    JWT_AUDIENCE: str = os.getenv("JWT_AUDIENCE", "")

    CORS_ORIGINS: list[str] = field(
        default_factory=lambda: [
            o.strip()
            for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
            if o.strip()
        ]
    )

settings = Settings()