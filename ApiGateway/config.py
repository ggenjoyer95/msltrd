import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    WALLET_SERVICE_URL: str = os.getenv("PAYMENTS_SERVICE_URL", "http://payments_service:8000")
    PURCHASE_SERVICE_URL: str = os.getenv("ORDERS_SERVICE_URL", "http://orders_service:8000")


settings = Settings() 