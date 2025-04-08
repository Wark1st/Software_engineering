from typing import List
from pydantic import BaseModel
from auth import validate_token
from fastapi import FastAPI, Depends, HTTPException, Query, status
from points_fake_db import fake_db

class PointBase(BaseModel):
    id: int
    pointName: str
    px: float
    py: float 

class PointResponse(PointBase):
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "pointName": "Kaluga",
                "px": 54.5293,
                "py": 36.2754
            }
        }

app = FastAPI()

@app.get("/points/", response_model=List[PointResponse])
async def get_all_points(_: dict = Depends(validate_token)):
    return fake_db

@app.get("/points/get_points", response_model=List[PointResponse])
async def get_points_by_id(ids: list[int] = Query(..., description="Массив ID точек"), _: dict = Depends(validate_token)):
    db_points = [p for p in fake_db if p["id"] in ids]
    if len(db_points) != len(ids):
        raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="One or more points were not found")
    return db_points

@app.get("/points/{id}", response_model=PointResponse)
async def get_point_by_id(id: str, _: dict = Depends(validate_token)):
    db_points = next((p for p in fake_db if p["id"] == int(id)), None)
    if not db_points:
        raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Point were not found")
    return db_points
