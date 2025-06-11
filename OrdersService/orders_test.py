import os
import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

os.environ["DB_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["RABBITMQ_URL"] = "amqp://guest:guest@localhost:5672/"

from main import app, Base, engine, AsyncSessionLocal
from models import Order, OutboxItem, OrderStatus

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

def test_list_orders_empty():
    r = client.get("/purchases")
    assert r.status_code == 200 and r.json()["purchases"] == []

def test_create_and_get_order():
<<<<<<< HEAD
    r1 = client.post("/purchases", json={"user_id": 1, "amount": 42, "description": "Test"})
    assert r1.status_code == 200
    data = r1.json()
    assert data["id"] == 1 and data["status"] == "NEW"
=======
    r1 = client.post("/purchases", json={"user_id": 1, "amount": 42, "product_description": "Test"})
    assert r1.status_code == 200
    data = r1.json()
    assert data["id"] == 1 and data["status"] == "PENDING"
>>>>>>> 8920008b2aafe9ef0737f46560bc2ee9d67f7662
    r2 = client.get(f"/purchases/{data['id']}")
    assert r2.status_code == 200 and r2.json()["id"] == 1

def test_get_order_not_found():
    r = client.get("/purchases/999")
    assert r.status_code == 404

def test_list_orders_after_creations():
<<<<<<< HEAD
    client.post("/purchases", json={"user_id": 2, "amount": 5, "description": ""})
    client.post("/purchases", json={"user_id": 3, "amount": 7, "description": ""})
=======
    client.post("/purchases", json={"user_id": 2, "amount": 5, "product_description": ""})
    client.post("/purchases", json={"user_id": 3, "amount": 7, "product_description": ""})
>>>>>>> 8920008b2aafe9ef0737f46560bc2ee9d67f7662
    r = client.get("/purchases")
    arr = r.json()["purchases"]
    assert len(arr) == 2
    assert arr[0]["user_id"] == 3

def test_outbox_created():
<<<<<<< HEAD
    client.post("/purchases", json={"user_id": 8, "amount": 9, "description": "X"})
=======
    client.post("/purchases", json={"user_id": 8, "amount": 9, "product_description": "X"})
>>>>>>> 8920008b2aafe9ef0737f46560bc2ee9d67f7662
    async def _check():
        async with AsyncSessionLocal() as s:
            res = await s.execute(select(OutboxItem))
            items = res.scalars().all()
            assert items and items[0].purchase_id == 1
    asyncio.get_event_loop().run_until_complete(_check())
