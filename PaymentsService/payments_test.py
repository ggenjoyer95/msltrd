import os
import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

os.environ["DB_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["RABBITMQ_URL"] = "amqp://guest:guest@localhost:5672/"

from main import app, Base, engine, AsyncSessionLocal
from models import Wallet, Transaction, TransactionType

client = TestClient(app)

@pytest.fixture(autouse=True)
def prepare_db():
    asyncio.get_event_loop().run_until_complete(_create())
    yield
    asyncio.get_event_loop().run_until_complete(_drop())

async def _create():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def _drop():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

def test_create_wallet():
    r = client.post("/wallets", json={"user_id": 1})
    assert r.status_code == 200
    data = r.json()
    assert data["user_id"] == 1 and data["money"] == 0

def test_create_duplicate_wallet():
    client.post("/wallets", json={"user_id": 1})
    r = client.post("/wallets", json={"user_id": 1})
    assert r.status_code == 400

def test_get_wallet():
    client.post("/wallets", json={"user_id": 1})
    r = client.get("/wallets/1")
    assert r.status_code == 200
    data = r.json()
    assert data["user_id"] == 1

def test_get_nonexistent_wallet():
    r = client.get("/wallets/999")
    assert r.status_code == 404

def test_deposit_money():
    client.post("/wallets", json={"user_id": 1})
    r = client.post("/wallets/1/deposit", json={"amount": 100})
    assert r.status_code == 200
    data = r.json()
    assert data["money"] == 100

def test_deposit_to_nonexistent_wallet():
    r = client.post("/wallets/999/deposit", json={"amount": 100})
    assert r.status_code == 404
