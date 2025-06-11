import logging
import json
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.future import select
import asyncio
import aio_pika
import backoff
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

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
            
            queue = await channel.declare_queue(settings.PURCHASE_STATUS_QUEUE, durable=True)
            
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            data = json.loads(message.body.decode())
                            logger.info(f"Received status update: {data}")
                            
                            purchase_id = data["purchase_id"]
                            status = data["status"]
                            
                            async with database.SessionLocal() as session:
                                purchase = await session.execute(
                                    select(models.Purchase).where(models.Purchase.id == purchase_id)
                                )
                                purchase = purchase.scalar_one_or_none()
                                
                                if not purchase:
                                    logger.error(f"Purchase {purchase_id} not found")
                                    continue
                                    
                                purchase.status = status
                                await session.commit()
                                logger.info(f"Updated status of purchase {purchase_id} to {status}")
                                
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            
        except Exception as e:
            logger.error(f"Error in consume: {e}")
            await asyncio.sleep(5)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.post("/purchases", response_model=schemas.Purchase)
async def create_purchase(purchase: schemas.PurchaseCreate):
    logger.info(f"Received purchase request: {purchase.model_dump()}")
    try:
        async with database.SessionLocal() as session:
            try:
                db_purchase = models.Purchase(
                    user_id=purchase.user_id,
                    amount=purchase.amount,
                    description=purchase.description,
                    status=schemas.OrderStatus.NEW
                )
                session.add(db_purchase)
                await session.commit()
                await session.refresh(db_purchase)
                
                try:
                    connection = await get_rabbitmq_connection(asyncio.get_event_loop())
                    channel = await get_rabbitmq_channel(connection)
                    
                    queue = await channel.declare_queue(settings.PURCHASE_QUEUE, durable=True)
                    
                    message = {
                        "purchase_id": db_purchase.id,
                        "user_id": db_purchase.user_id,
                        "amount": float(db_purchase.amount)
                    }
                    
                    await channel.default_exchange.publish(
                        aio_pika.Message(body=json.dumps(message).encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                        routing_key=queue.name
                    )
                    
                    logger.info(f"Sent purchase {db_purchase.id} to processing")
                    await connection.close()
                    
                except Exception as e:
                    logger.error(f"Error sending purchase to processing: {e}")
                    db_purchase.status = schemas.OrderStatus.CANCELLED
                    await session.commit()
                    raise HTTPException(status_code=500, detail=str(e))
                    
                return db_purchase
                
            except Exception as e:
                logger.error(f"Database error creating purchase: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
    except Exception as e:
        logger.error(f"Error creating purchase: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/purchases/{purchase_id}", response_model=schemas.Purchase)
async def get_purchase(purchase_id: int):
    async with database.SessionLocal() as session:
        purchase = await session.execute(
            select(models.Purchase).where(models.Purchase.id == purchase_id)
        )
        purchase = purchase.scalar_one_or_none()
        if not purchase:
            raise HTTPException(status_code=404, detail="Purchase not found")
        return purchase

@app.get("/purchases", response_model=list[schemas.Purchase])
async def get_purchases():
    async with database.SessionLocal() as session:
        purchases = await session.execute(select(models.Purchase))
        return purchases.scalars().all() 