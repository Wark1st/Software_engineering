import os
from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from auth import validate_token
from points_fake_db import fake_db
from schemas import PointResponse

DATABASE_URL = os.getenv("DATABASE_URL")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongodb_client = AsyncIOMotorClient(DATABASE_URL)
    app.mongodb = app.mongodb_client["geopoints"]
    await app.mongodb.geopoints.create_index([("id", 1)], unique=True)
    if await app.mongodb.geopoints.count_documents({}) == 0:
        try:
            await app.mongodb.geopoints.insert_many(fake_db)
        except DuplicateKeyError:
            pass
    
    yield
    app.mongodb_client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/points/", response_model=List[PointResponse])
async def get_all_points(_: dict = Depends(validate_token)):
    db_points = await app.mongodb.geopoints.find({}, {"_id": 0}).to_list(1000)
    return db_points

@app.get("/points/get_points", response_model=List[PointResponse])
async def get_points_by_id(ids: list[int] = Query(..., description="Массив ID точек"), _: dict = Depends(validate_token)):
    db_points = await app.mongodb.geopoints.find({"id": {"$in": ids}}, {"_id": 0}).to_list(None)
    if len(db_points) != len(ids):
        raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="One or more points were not found")
    return db_points

@app.get("/points/{id}", response_model=PointResponse)
async def get_point_by_id(id: int, _: dict = Depends(validate_token)):
    db_points = await app.mongodb.geopoints.find_one({"id": id}, {"_id": 0})
    if not db_points:
        raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Point were not found")
    return db_points
