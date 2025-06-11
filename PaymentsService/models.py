from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum as SqlEnum,
    Boolean,
    Float,
    func,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)
    money = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())


class EventProcessingStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class PaymentEventInbox(Base):
    """Transactional Inbox for incoming payment events."""
    __tablename__ = "payment_event_inbox"
    purchase_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    amount = Column(Integer, nullable=False)
    received_at = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(
        SqlEnum(EventProcessingStatus), default=EventProcessingStatus.PENDING
    )


class PaymentNotificationOutbox(Base):
    """Transactional Outbox for outgoing payment status notifications."""
    __tablename__ = "payment_notification_outbox"
    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    payment_status = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_sent = Column(Boolean, default=False)


class PurchaseInbox(Base):
    __tablename__ = "purchase_processing_inbox"
    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, nullable=False, unique=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    is_processed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class PurchaseStatusOutbox(Base):
    __tablename__ = "purchase_status_outbox"
    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    is_sent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now()) 