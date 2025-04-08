import os
from typing import List
from fastapi import Depends, HTTPException, APIRouter
import httpx
from pydantic import BaseModel
from auth import validate_token
from fastapi import APIRouter, status

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
    id: int
    points: List[GeoPoint]

class DeleteRouteResponse(BaseModel):
    message: str
    deleted_route: RouteResponse

fake_route_db: RouteCreate = [
    {"id": 1, "name": "Название 1", "description": 'Описание маршрута 1', "points": [1, 2]},
    {"id": 2, "name": "Название 2", "description": 'Описание маршрута 2', "points": [3, 2, 4]},
    {"id": 3, "name": "Название 3", "description": 'Описание маршрута 3', "points": [3, 4, 1]}
]

fake_db_id_generate = 4

GEO_POINTS_URL = os.getenv("GEO_POINTS_URL")

router = APIRouter(prefix="/routes",
    tags=["routes"])

async def get_geo_points(ids, cur_user):
    async with httpx.AsyncClient() as client:
        try:
            token = cur_user["token"]
            response = await client.get(
                f"{GEO_POINTS_URL}/points/get_points",
                headers={"Authorization": f"Bearer {token}"},
                params= {"ids": ids}
            )
            
            return response.json()
        
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Auth service error: {e.response.text}"
            )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="GeoPoint service unavailable"
            )


@router.post('/create_route', response_model=RouteResponse)
async def create_new_route(route: RouteCreate, cur_user = Depends(validate_token)):
    global fake_db_id_generate
    db_route = list(filter(lambda p: p["name"] == route.name, fake_route_db))
    if db_route:
        raise HTTPException(status_code=400, detail="Route with this name already registered")
    
    points = await get_geo_points(route.points, cur_user)
    
    fake_route_db.append({'id': fake_db_id_generate, 'name': route.name, 'description': route.description, 'points': route.points})
    fake_db_id_generate += 1

    return {'id': fake_db_id_generate - 1, 'name': route.name, 'description': route.description, 'points': points}

@router.get('/', response_model=List[RouteResponse])
async def get_all_routes(cur_user: dict = Depends(validate_token)):
    response = []
    for route in fake_route_db:
        points = await get_geo_points(route['points'], cur_user)
        response.append({**route, 'points': points})
    return response


@router.get('/{route_id}', response_model=RouteResponse)
async def get_route_by_id(route_id: int, cur_user: dict = Depends(validate_token)):
    route = next((r for r in fake_route_db if r["id"] == route_id), None)
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found"
        )
    points = await get_geo_points(route['points'], cur_user)
    return {**route, 'points': points}


@router.delete('/{route_id}', response_model=DeleteRouteResponse)
async def delete_route(route_id: int, _: dict = Depends(validate_token)):
    global fake_route_db
    
    index = next((i for i, r in enumerate(fake_route_db) if r["id"] == route_id), None)
    
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found"
        )

    deleted_route = fake_route_db.pop(index)
    
    return {
        "message": "Route deleted successfully",
        "deleted_route": deleted_route
    }

