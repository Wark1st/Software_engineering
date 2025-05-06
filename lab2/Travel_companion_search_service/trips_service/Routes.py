import json
import os
from typing import List
from fastapi import Depends, HTTPException, APIRouter, Request
import httpx
from auth import validate_token
from fastapi import APIRouter, status
from schemasRoutes import DeleteRouteResponse, RouteCreate, RouteResponse
from bson.errors import InvalidId
from bson import ObjectId

ROUTES = 'routes'

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
async def create_new_route(route: RouteCreate, request: Request, cur_user = Depends(validate_token)):
    collection = request.app.mongodb[ROUTES]
    if await collection.find_one({"name": route.name}):
        raise HTTPException(status_code=400, detail="Route with this name already registered")
    
    points = await get_geo_points(route.points, cur_user)
    
    result = await collection.insert_one({
        "name": route.name,
        "description": route.description,
        "points": route.points
    })

    db_route = await collection.find_one({"_id": result.inserted_id})

    route_response = RouteResponse(
        id=str(db_route["_id"]),
        name=db_route["name"],
        description=db_route["description"],
        points=points
    )
    
    await request.app.redis.setex(
        f"route:{route_response.id}", 
        600,
        json.dumps(route_response.model_dump())
    )
    
    return route_response

@router.get('/')
async def get_all_routes(request: Request, cur_user: dict = Depends(validate_token)):
    collection = request.app.mongodb[ROUTES]
    routes = []
    async for route in collection.find():
        points = await get_geo_points(route["points"], cur_user)
        routes.append(RouteResponse(
            id=str(route["_id"]),
            name=route["name"],
            description=route["description"],
            points=points
        ))
    return routes

@router.get('/{route_id}', response_model=RouteResponse)
async def get_route_by_id(route_id: str, request: Request, cur_user: dict = Depends(validate_token)):
    try:
        obj_id = ObjectId(route_id)
    except InvalidId:
        raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Invalid route ID format"
            )
    cached_data = await request.app.redis.get(f"route:{route_id}")
    if cached_data:
        return json.loads(cached_data)
    
    collection = request.app.mongodb[ROUTES]
    db_route = await collection.find_one({"_id": obj_id})
    if not db_route:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Route not found"
            )

    points = await get_geo_points(db_route['points'], cur_user)
    route_response = RouteResponse(
        id=str(db_route["_id"]),
        name=db_route["name"],
        description=db_route["description"],
        points=points
    )

    await request.app.redis.setex(
        f"route:{route_id}", 
        600,
        json.dumps(route_response.dict())
    )
    
    return route_response


@router.delete('/{route_id}', response_model=DeleteRouteResponse)
async def delete_route(route_id: str, request: Request,  _: dict = Depends(validate_token)):
    try:
        obj_id = ObjectId(route_id)
    except InvalidId:
        raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Invalid route ID format"
            )
    
    collection = request.app.mongodb[ROUTES]
    
    db_route = await collection.find_one_and_delete({"_id": obj_id})
    
    if not db_route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found"
        )

    await request.app.redis.delete(f"route:{route_id}")
    
    return {
        "message": "Route deleted successfully",
    }

