from typing import List
from pydantic import BaseModel


class RouteCreate(BaseModel):
    name: str
    points: list[int]
    description: str = ''

class GeoPoint(BaseModel):
    id: int
    pointName: str
    px: float
    py: float 

class RouteCreate(BaseModel):
    name: str
    points: List[int]
    description: str = ''

class RouteResponse(RouteCreate):
    id: str
    points: List[GeoPoint]

class DeleteRouteResponse(BaseModel):
    message: str
    # deleted_route: RouteResponse