import os
import httpx
import logging
from fastapi import FastAPI, HTTPException, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, List
from pydantic import BaseModel
import json

import schemas
from config import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="E-Commerce API Gateway",
    description="API Gateway for the e-commerce microservices system",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

settings = Settings()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use settings for service URLs
ORDERS_SERVICE_URL = settings.PURCHASE_SERVICE_URL
PAYMENTS_SERVICE_URL = settings.WALLET_SERVICE_URL

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

# Data Models
class WalletCreate(BaseModel):
    user_id: int

class WalletDeposit(BaseModel):
    amount: float

# Wallet endpoints
@app.post("/api/wallet/create", response_model=schemas.WalletDetails)
async def create_wallet(wallet: WalletCreate):
    """
    Create a new wallet for a user.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(f"{PAYMENTS_SERVICE_URL}/wallets", json=wallet.dict())
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to create wallet")
        return response.json()

@app.get("/api/wallet/{user_id}", response_model=schemas.WalletDetails)
async def get_wallet(user_id: int):
    """
    Get wallet information for a specific user.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{PAYMENTS_SERVICE_URL}/wallets/{user_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Wallet not found")
        return response.json()

@app.post("/api/wallet/{user_id}/deposit", response_model=schemas.WalletDetails)
async def deposit_money(user_id: int, deposit: WalletDeposit):
    """
    Deposit money into a user's wallet.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(f"{PAYMENTS_SERVICE_URL}/wallets/{user_id}/deposit", json=deposit.dict())
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Wallet not found for deposit")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to deposit money")
        return response.json()

# WebSocket endpoint for real-time updates
@app.websocket("/ws/{purchase_id}")
async def websocket_endpoint(websocket: WebSocket, purchase_id: int):
    await manager.connect(websocket, purchase_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle any incoming messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket, purchase_id)

@app.post("/api/purchase", response_model=schemas.PurchaseRecord)
async def create_purchase(purchase: schemas.NewPurchaseContract):
    """
    Create a new purchase.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(f"{ORDERS_SERVICE_URL}/purchases", json=purchase.dict())
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to create purchase")
        return response.json()

@app.get("/api/purchase/{purchase_id}", response_model=schemas.PurchaseRecord)
async def get_purchase_details(purchase_id: int):
    """
    Get details of a specific purchase.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{ORDERS_SERVICE_URL}/purchases/{purchase_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Purchase not found")
        return response.json()

@app.get("/api/purchases", response_model=schemas.PurchaseList)
async def get_all_purchases():
    """
    Get a list of all purchases.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{ORDERS_SERVICE_URL}/purchases")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to get purchases")
        return {"purchases": response.json()}
