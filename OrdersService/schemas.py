from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    NEW = "NEW"
    FINISHED = "FINISHED"
    CANCELLED = "CANCELLED"

class PurchaseBase(BaseModel):
    user_id: int
    description: str
    amount: float

class PurchaseCreate(PurchaseBase):
    pass

class Purchase(PurchaseBase):
    id: int
    status: OrderStatus
    created_at: datetime

    class Config:
        from_attributes = True

class PurchaseList(BaseModel):
    purchases: list[Purchase]

    class Config:
        from_attributes = True 