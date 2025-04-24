from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from Routes import router as routeRouter
from Trips import router as tripRouter
from motor.motor_asyncio import AsyncIOMotorClient

DATABASE_URL = os.getenv("DATABASE_URL")
ROUTES = 'routes'

initial_data = [
    {"name": "Название 1", "description": "Описание маршрута 1", "points": [1, 2]},
    {"name": "Название 2", "description": "Описание маршрута 2", "points": [3, 2, 4]},
    {"name": "Название 3", "description": "Описание маршрута 3", "points": [3, 4, 1]}
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongodb_client = AsyncIOMotorClient(DATABASE_URL)
    app.mongodb = app.mongodb_client['trips_db']
    collection = app.mongodb[ROUTES]
    
    await collection.create_index([("name", 1)], unique=True)
    
    try:
        for data in initial_data:
            await collection.update_one(
                {"name": data["name"]},
                {"$setOnInsert": data},
                upsert=True
            )
    except Exception as e:
        pass
    
    yield
    
    app.mongodb_client.close()


app = FastAPI(lifespan=lifespan)

app.include_router(routeRouter)
app.include_router(tripRouter)