import logging
import json
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import and_
import asyncio
import aio_pika
import backoff
from datetime import datetime
from typing import List, Optional

import models
import schemas
import database
from config import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
settings = Settings()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup():
    await database.init_db()
    loop = asyncio.get_event_loop()
    loop.create_task(consume(loop))
    loop.create_task(process_outbox(loop))

@backoff.on_exception(backoff.expo, Exception, max_time=300)
async def get_rabbitmq_connection(loop):
    return await aio_pika.connect_robust(settings.RABBITMQ_URL, loop=loop)

@backoff.on_exception(backoff.expo, Exception, max_time=300)
async def get_rabbitmq_channel(connection):
    return await connection.channel()

async def consume(loop):
    while True:
        try:
            connection = await get_rabbitmq_connection(loop)
            channel = await get_rabbitmq_channel(connection)
            
            queue = await channel.declare_queue(settings.PURCHASE_QUEUE, durable=True)
            
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            data = json.loads(message.body.decode())
                            logger.info(f"Received purchase request: {data}")
                            
                            purchase_id = data["purchase_id"]
                            user_id = data["user_id"]
                            amount = data["amount"]
                            
                            async with database.SessionLocal() as session:
                                wallet = await session.execute(
                                    select(models.Wallet).where(models.Wallet.user_id == user_id)
                                )
                                wallet = wallet.scalar_one_or_none()
                                
                                if not wallet:
                                    logger.error(f"Wallet not found for user {user_id}")
                                    continue
                                    
                                if wallet.money < amount:
                                    logger.info(f"Payment for {purchase_id} cancelled due to insufficient funds")
                                    continue
                                    
                                wallet.money -= amount
                                await session.commit()
                                
                                logger.info(f"Payment for {purchase_id} completed. New balance for user {user_id} is {wallet.money}")
                                
                                status_message = {
                                    "purchase_id": purchase_id,
                                    "status": "FINISHED"
                                }
                                
                                status_queue = await channel.declare_queue(settings.PURCHASE_STATUS_QUEUE, durable=True)
                                await channel.default_exchange.publish(
                                    aio_pika.Message(body=json.dumps(status_message).encode()),
                                    routing_key=status_queue.name
                                )
                                
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            
        except Exception as e:
            logger.error(f"Error in consume: {e}")
            await asyncio.sleep(5)

async def process_outbox(loop):
    while True:
        try:
            connection = await get_rabbitmq_connection(loop)
            channel = await get_rabbitmq_channel(connection)
            
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Error in process_outbox: {e}")
            await asyncio.sleep(5)

@app.post("/wallets", response_model=schemas.Wallet)
async def create_wallet(wallet: schemas.WalletCreate):
    async with database.SessionLocal() as session:
        db_wallet = models.Wallet(user_id=wallet.user_id)
        session.add(db_wallet)
        await session.commit()
        await session.refresh(db_wallet)
        return db_wallet

@app.get("/wallets/{user_id}", response_model=schemas.Wallet)
async def get_wallet(user_id: int):
    async with database.SessionLocal() as session:
        wallet = await session.execute(
            select(models.Wallet).where(models.Wallet.user_id == user_id)
        )
        wallet = wallet.scalar_one_or_none()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
        return wallet

@app.post("/wallets/{user_id}/deposit", response_model=schemas.Wallet)
async def deposit(user_id: int, deposit: schemas.Deposit):
    async with database.SessionLocal() as session:
        wallet = await session.execute(
            select(models.Wallet).where(models.Wallet.user_id == user_id)
        )
        wallet = wallet.scalar_one_or_none()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")
            
        wallet.money += deposit.amount
        await session.commit()
        await session.refresh(wallet)
        return wallet 