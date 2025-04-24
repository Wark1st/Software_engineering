from datetime import datetime
from typing import List
from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str

class RoutePoint(BaseModel):
    id: int
    px: float
    py: float
    pointName: str

class RouteResponse(BaseModel):
    id: int
    name: str
    description: str
    points: List[RoutePoint]

class TripCreate(BaseModel):
    name: str
    start_date: datetime
    users: List[int]
    route: int

class TripBase(TripCreate):
    id: int
    created_by: int

class TripResponse(TripBase):
    users: List[UserResponse]
    route: RouteResponse

class TripUpdate(BaseModel):
    users: List[int]

class TripDeleteResponse(BaseModel):
    message: str
    deleted_trip: TripResponse