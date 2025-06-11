import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "kpo3sql"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432

    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
    PURCHASE_QUEUE: str = "purchase_queue"
    PURCHASE_STATUS_QUEUE: str = "purchase_status_queue"

    DB_URL: str = os.getenv("DB_URL", "postgresql+asyncpg://postgres:postgres@postgres:5432/kpo3sql")


settings = Settings() 