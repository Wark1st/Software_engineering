import os
import httpx
from typing import List
from Routes import get_route_by_id
from fastapi import status
from http.client import HTTPException

GEO_POINTS_URL = os.getenv("GEO_POINTS_URL")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8003")

fake_route_db = [
    {"id": 1, "name": "Название 1", "description": 'Описание маршрута 1', "points": [1, 2]},
    {"id": 2, "name": "Название 2", "description": 'Описание маршрута 2', "points": [3, 2, 4]},
    {"id": 3, "name": "Название 3", "description": 'Описание маршрута 3', "points": [3, 4, 1]}
]

fake_trips_db = []

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

async def get_users(user_ids: List[int], token: str):
    async with httpx.AsyncClient() as client:
        try:
            users = []
            for user_id in user_ids:
                response = await client.get(
                    f"{USER_SERVICE_URL}/{user_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"User {user_id} not found"
                    )
                users.append(response.json())
            return users
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="User service unavailable"
            )
        
async def get_trip_info(trip_id, cur_user):
    trip = next((t for t in fake_trips_db if t["id"] == int(trip_id)), None)
    
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    users_info = await get_users(trip['users'], cur_user['token'])
    route_info = await get_route_by_id(trip['route'], cur_user)

    return {
        **trip, 
        'users': users_info, 
        'route': route_info
        }