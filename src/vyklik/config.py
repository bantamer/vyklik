from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    postgres_dsn: str = Field(..., alias="POSTGRES_DSN")

    poll_interval_seconds: int = Field(30, alias="POLL_INTERVAL_SECONDS")
    work_hours: str = Field("mon=8-16,tue=8-16,wed=8-16,thu=8-16,fri=8-16", alias="WORK_HOURS")

    # Telegram chat id that /feedback messages are delivered to. Kept server-side
    # so users never see the owner's account. Empty disables /feedback.
    feedback_chat_id: int | None = Field(None, alias="FEEDBACK_CHAT_ID")

    duw_status_url: str = Field(
        "https://rezerwacje.duw.pl/app/webroot/status_kolejek/query.php?status",
        alias="DUW_STATUS_URL",
    )
    insecure_tls: bool = Field(False, alias="INSECURE_TLS")

    log_level: str = Field("INFO", alias="LOG_LEVEL")


settings = Settings()  # type: ignore[call-arg]
