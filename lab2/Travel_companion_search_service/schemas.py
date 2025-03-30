from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Annotated
from annotated_types import Ge

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    # name: str
    # lastname: str

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    # name: str
    # lastname: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class UserByLogin(BaseModel):
    login: str

class PointCreate(BaseModel):
    pointName: str
    px: float = Field(ge=-90, le=90)
    py: float = Field(ge=-180, le=180)

class Point(BaseModel):
    id: int
    pointName: str
    px: float = Field(ge=-90, le=90)
    py: float = Field(ge=-180, le=180)

class RouteCreate(BaseModel):
    name: str
    points: list[int]
    description: str = ''

class AddUserToRoute(BaseModel):
    routeId: int
    userLogin: str = ''

class TripCreate(BaseModel):
    name: str
    description: str = ''
    start_at: datetime
    maxUsers: Annotated[int, Ge(1)]
    route_id: int
    users: list[int]