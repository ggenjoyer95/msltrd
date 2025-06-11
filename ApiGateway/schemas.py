from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import List


class OrderStatus(str, Enum):
    NEW = "NEW"
    FINISHED = "FINISHED"
    CANCELLED = "CANCELLED"


class WalletRegistration(BaseModel):
    user_id: int
    money: float = 0


class WalletDetails(BaseModel):
    user_id: int
    money: float


class FundDeposit(BaseModel):
    amount: float


class NewPurchaseContract(BaseModel):
    user_id: int
    amount: float
    description: str


class PurchaseRecord(BaseModel):
    id: int
    user_id: int
    amount: float
    description: str
    status: OrderStatus
    created_at: datetime


class PurchaseList(BaseModel):
    purchases: List[PurchaseRecord] 