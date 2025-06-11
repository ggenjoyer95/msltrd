import pytest
import json
from fastapi.testclient import TestClient
import httpx

from main import app, client as async_client

client = TestClient(app)

class DummyResponse:
    def __init__(self, status_code: int, json_data, headers=None):
        self.status_code = status_code
        self._json = json_data
        self.content = json.dumps(json_data).encode()
        self.headers = headers or {"content-type": "application/json"}

    def json(self):
        return self._json

@pytest.fixture(autouse=True)
def mock_httpx_request(monkeypatch):
    async def fake_request(method, url, headers=None, content=None, timeout=None):
        if url.startswith("http://purchase"):
            if method == "GET":
                if url.rstrip("/").endswith("/purchases"):
                    return DummyResponse(200, {"purchases": [{"id": 1, "user_id": 1, "amount": 10,
                                                "product_description": None, "status":"PENDING",
                                                "created_at":"2025-06-07T00:00:00"}]})
                else:
                    return DummyResponse(200, {"id": 1, "user_id": 1, "amount": 10,
                                               "product_description": None, "status":"PENDING",
                                               "created_at":"2025-06-07T00:00:00"})
            if method == "POST":
                data = json.loads(content or b"{}")
                return DummyResponse(200, {"id": 2, **data, "status":"PENDING",
                                           "created_at":"2025-06-07T00:00:00"})
        if url.startswith("http://wallet"):
            if method == "POST":
                data = json.loads(content or b"{}")
                if url.rstrip("/").endswith("/wallets"):
                    return DummyResponse(200, {"user_id": data["user_id"], "money": 0})
                else:
                    return DummyResponse(200, {"user_id": 1, "money": data["amount"]})
            if method == "GET":
                return DummyResponse(200, {"user_id": 1, "money": 100})

        return DummyResponse(404, {"detail":"Not Found"})

    monkeypatch.setattr(async_client, "request", fake_request)


def test_proxy_list_purchases():
    r = client.get("/purchases")
    assert r.status_code == 200
    data = r.json()
    assert "purchases" in data and len(data["purchases"]) > 0
    assert data["purchases"][0]["id"] == 1

def test_proxy_get_purchase():
    r = client.get("/purchases/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1

def test_proxy_create_purchase():
    payload = {"user_id": 5, "amount": 7, "product_description": "Test item"}
    r = client.post("/purchases", json=payload)
    assert r.status_code == 200
    out = r.json()
    assert out["user_id"] == 5 and out["amount"] == 7 and out["status"] == "PENDING"

def test_proxy_create_and_deposit_wallet():
    r1 = client.post("/wallets", json={"user_id": 9})
    assert r1.status_code == 200 and r1.json()["money"] == 0
    r2 = client.post("/wallets/9/deposit", json={"amount": 50})
    assert r2.status_code == 200 and r2.json()["money"] == 50
    r3 = client.get("/wallets/9")
    assert r3.status_code == 200 and r3.json()["money"] == 100
