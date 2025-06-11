import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    DB_URL: str = os.getenv("DB_URL", "postgresql+asyncpg://postgres:postgres@postgres:5432/kpo3sql")
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")

    PURCHASE_PROCESSING_QUEUE: str = "purchase_processing_queue"
    PURCHASE_PROCESSING_EXCHANGE: str = "purchase_processing_exchange"

    PURCHASE_STATUS_QUEUE: str = "purchase_status_queue"
    PURCHASE_STATUS_EXCHANGE: str = "purchase_status_exchange"
    PURCHASE_STATUS_ROUTING_KEY: str = "purchase_status_key"

    PURCHASE_QUEUE: str = "purchase_queue"


settings = Settings() 