import os

import httpx
from fastapi import FastAPI, HTTPException, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, List
from pydantic import BaseModel
import json

app = FastAPI(
    title="E-Commerce API Gateway",
    description="API Gateway for the e-commerce microservices system",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
ORDERS_SERVICE_URL = os.getenv("ORDERS_SERVICE_URL", "http://orders_service:8000")
PAYMENTS_SERVICE_URL = os.getenv("PAYMENTS_SERVICE_URL", "http://payments_service:8000")
=======
ORDERS_URL = os.getenv("ORDERS_URL", "http://orders:8002")
PAYMENTS_URL = os.getenv("PAYMENTS_URL", "http://payments:8001")
WALLET_SERVICE_URL = "http://wallet_service:8000"
PURCHASE_SERVICE_URL = "http://purchase_service:8000"
>>>>>>> 8920008b2aafe9ef0737f46560bc2ee9d67f7662

client = httpx.AsyncClient(timeout=10.0)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, purchase_id: int):
        await websocket.accept()
        if purchase_id not in self.active_connections:
            self.active_connections[purchase_id] = []
        self.active_connections[purchase_id].append(websocket)

    def disconnect(self, websocket: WebSocket, purchase_id: int):
        if purchase_id in self.active_connections:
            self.active_connections[purchase_id].remove(websocket)
            if not self.active_connections[purchase_id]:
                del self.active_connections[purchase_id]

    async def broadcast_update(self, purchase_id: int, message: str):
        if purchase_id in self.active_connections:
            for connection in self.active_connections[purchase_id]:
                await connection.send_text(message)

manager = ConnectionManager()

class WalletCreate(BaseModel):
    user_id: int

class WalletDeposit(BaseModel):
    amount: float

class PurchaseCreate(BaseModel):
    user_id: int
    amount: float
    product_description: Optional[str] = None

async def proxy_request(request: Request, target_url: str) -> Response:
    url = target_url + request.url.path
    if request.url.query:
        url += f"?{request.url.query}"
    try:
        body_bytes = await request.body()
    except Exception:
        body_bytes = b""
    headers = {
        name.decode(): value.decode()
        for name, value in request.headers.raw
        if name.decode().lower() != "host"
    }
    try:
        resp = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body_bytes,
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Bad gateway: {e}")
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=dict(resp.headers),
        media_type=resp.headers.get("content-type"),
    )

<<<<<<< HEAD
=======

>>>>>>> 8920008b2aafe9ef0737f46560bc2ee9d67f7662
@app.post("/orders")
@app.get("/orders")
@app.get("/orders/{rest_of_path:path}")
async def proxy_orders(request: Request):
    """
    POST /orders
    GET  /orders
    GET  /orders/{order_id}
    Любые запросы, начинающиеся с /orders, проксируем в Orders Service.
    """
<<<<<<< HEAD
    return await proxy_request(request, ORDERS_SERVICE_URL)

@app.post("/api/wallet/create", tags=["Wallets"])
=======
    return await proxy_request(request, ORDERS_URL)


@app.post("/accounts")
@app.post("/accounts/{rest_of_path:path}")
@app.get("/accounts/{rest_of_path:path}")
async def proxy_payments(request: Request):
    """
    POST /accounts                    -> Payments
    POST /accounts/{user_id}/topup    -> Payments
    GET  /accounts/{user_id}          -> Payments
    Всё, что начинается с /accounts, по умолчанию идёт в Payments Service.
    """
    return await proxy_request(request, PAYMENTS_URL)


@app.websocket("/ws/{purchase_id}")
async def websocket_endpoint(websocket: WebSocket, purchase_id: int):
    await manager.connect(websocket, purchase_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle any incoming messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket, purchase_id)

@app.post("/wallets", tags=["Wallets"])
>>>>>>> 8920008b2aafe9ef0737f46560bc2ee9d67f7662
async def create_wallet(wallet: WalletCreate):
    """
    Create a new wallet for a user.
    """
    async with client as c:
<<<<<<< HEAD
        response = await c.post(f"{PAYMENTS_SERVICE_URL}/wallets", json=wallet.dict())
        return response.json()

@app.get("/api/wallet/{user_id}", tags=["Wallets"])
=======
        response = await c.post(f"{WALLET_SERVICE_URL}/wallets", json=wallet.dict())
        return response.json()

@app.get("/wallets/{user_id}", tags=["Wallets"])
>>>>>>> 8920008b2aafe9ef0737f46560bc2ee9d67f7662
async def get_wallet(user_id: int):
    """
    Get wallet information for a specific user.
    """
    async with client as c:
<<<<<<< HEAD
        response = await c.get(f"{PAYMENTS_SERVICE_URL}/wallets/{user_id}")
=======
        response = await c.get(f"{WALLET_SERVICE_URL}/wallets/{user_id}")
>>>>>>> 8920008b2aafe9ef0737f46560bc2ee9d67f7662
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Wallet not found")
        return response.json()

<<<<<<< HEAD
@app.post("/api/wallet/deposit", tags=["Wallets"])
=======
@app.post("/wallets/{user_id}/deposit", tags=["Wallets"])
>>>>>>> 8920008b2aafe9ef0737f46560bc2ee9d67f7662
async def deposit_money(user_id: int, deposit: WalletDeposit):
    """
    Deposit money into a user's wallet.
    """
    async with client as c:
<<<<<<< HEAD
        response = await c.post(f"{PAYMENTS_SERVICE_URL}/wallets/{user_id}/deposit", json=deposit.dict())
=======
        response = await c.post(f"{WALLET_SERVICE_URL}/wallets/{user_id}/deposit", json=deposit.dict())
>>>>>>> 8920008b2aafe9ef0737f46560bc2ee9d67f7662
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Wallet not found")
        return response.json()

@app.post("/purchases", tags=["Purchases"])
async def create_purchase(purchase: PurchaseCreate):
    """
    Create a new purchase order.
    """
    async with client as c:
<<<<<<< HEAD
        response = await c.post(f"{PAYMENTS_SERVICE_URL}/purchases", json=purchase.dict())
=======
        response = await c.post(f"{PURCHASE_SERVICE_URL}/purchases", json=purchase.dict())
>>>>>>> 8920008b2aafe9ef0737f46560bc2ee9d67f7662
        data = response.json()
        # Notify WebSocket clients about the new purchase
        await manager.broadcast_update(data["id"], json.dumps({
            "type": "purchase_update",
            "purchase_id": data["id"],
            "status": data["status"]
        }))
        return data

@app.get("/purchases/{purchase_id}", tags=["Purchases"])
async def get_purchase(purchase_id: int):
    """
    Get information about a specific purchase.
    """
    async with client as c:
<<<<<<< HEAD
        response = await c.get(f"{PAYMENTS_SERVICE_URL}/purchases/{purchase_id}")
=======
        response = await c.get(f"{PURCHASE_SERVICE_URL}/purchases/{purchase_id}")
>>>>>>> 8920008b2aafe9ef0737f46560bc2ee9d67f7662
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Purchase not found")
        data = response.json()
        # Notify WebSocket clients about any status changes
        await manager.broadcast_update(purchase_id, json.dumps({
            "type": "purchase_update",
            "purchase_id": purchase_id,
            "status": data["status"]
        }))
        return data

@app.get("/purchases", tags=["Purchases"])
async def list_purchases():
    """
    List all purchases.
    """
    async with client as c:
<<<<<<< HEAD
        response = await c.get(f"{PAYMENTS_SERVICE_URL}/purchases")
        return response.json()

@app.websocket("/ws/{purchase_id}")
async def websocket_endpoint(websocket: WebSocket, purchase_id: int):
    await manager.connect(websocket, purchase_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle any incoming messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket, purchase_id)

=======
        response = await c.get(f"{PURCHASE_SERVICE_URL}/purchases")
        return response.json()

>>>>>>> 8920008b2aafe9ef0737f46560bc2ee9d67f7662
@app.middleware("http")
async def catch_not_found(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as exc:
        if exc.status_code == 404:
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        raise
