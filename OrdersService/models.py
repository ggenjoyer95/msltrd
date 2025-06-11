from sqlalchemy import Column, Integer, String, Float, DateTime, func, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.orm import declarative_base
from schemas import OrderStatus

Base = declarative_base()

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    status = Column(SQLAlchemyEnum(OrderStatus), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class PurchaseOutbox(Base):
    __tablename__ = "purchase_outbox"
    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, nullable=False, unique=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    is_sent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now()) 