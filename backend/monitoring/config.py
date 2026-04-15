from pydantic_settings import BaseSettings, SettingsConfigDict


class MonitoringSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENABLE_MONITORING: bool = True
    MONITORING_INTERVAL_SECONDS: int = 300
    MONITORING_OVERLAP_SECONDS: int = 180
    MONITORING_DUE_SOON_HOURS: int = 48
    MONITORING_STALE_DAYS: int = 7
    MONITORING_ALERT_COOLDOWN_SECONDS: int = 3600

    REDMINE_URL: str
    REDMINE_API_KEY: str
    REDMINE_PAGE_SIZE: int = 100

    SLACK_WEBHOOK_URL: str | None = None
    SQLITE_PATH: str = "monitoring.db"


settings = MonitoringSettings()