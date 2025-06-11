from pydantic import BaseModel
from datetime import datetime


class WalletBase(BaseModel):
    user_id: int


class WalletCreate(WalletBase):
    pass


class Deposit(BaseModel):
    amount: float


class Wallet(WalletBase):
    id: int
    money: float
    created_at: datetime

    class Config:
        from_attributes = True
