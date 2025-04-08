import os
from fastapi import Depends, HTTPException, APIRouter, status
from typing import List
from datetime import datetime
import httpx
from pydantic import BaseModel
from fastapi import APIRouter
from auth import validate_token
from Routes import get_route_by_id

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



fake_trips_db = []

fake_trip_id = 0

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8003")

router = APIRouter(prefix="/trips",
    tags=["trips"])

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

@router.post("/create", response_model=TripResponse)
async def create_trip(
    trip: TripCreate, 
    cur_user: dict = Depends(validate_token)
):
    global fake_trip_id

    try:
        route = await get_route_by_id(trip.route, cur_user)
    except HTTPException:
        raise HTTPException(
            status_code=404,
            detail=f"Route {trip.route} not found"
        )

    try:
        inf_users = await get_users(trip.users, cur_user["token"])
    except HTTPException as e:
        raise e

    new_trip = {
        "id": fake_trip_id,
        "name": trip.name,
        "start_date": trip.start_date,
        "route": trip.route,
        "users": trip.users,
        "created_by": cur_user["id"]
    }
    
    fake_trips_db.append(new_trip)
    fake_trip_id += 1
    
    return {
        **new_trip, 
        "users": inf_users, 
        "route": route
        }

@router.get("/", response_model=List[TripResponse])
async def get_all_trips(cur_user: dict = Depends(validate_token)):
    trips = []
    for route in fake_trips_db:
        trip_info = await get_trip_info(route['id'], cur_user)
        trips.append(trip_info)
    return trips

@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: int, cur_user: dict = Depends(validate_token)):
    return await get_trip_info(trip_id, cur_user)

@router.delete("/{trip_id}", response_model=TripDeleteResponse)
async def delete_trip(
    trip_id: int, 
    cur_user: dict = Depends(validate_token)
):
    global fake_trips_db
    
    trip = next((t for t in fake_trips_db if t["id"] == trip_id), None)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip["created_by"] != cur_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="Only trip creator can delete the trip"
        )
    
    fake_trips_db = [t for t in fake_trips_db if t["id"] != trip_id]
    return {"message": "Trip deleted successfully"}

@router.put("/{trip_id}", response_model=TripResponse)
async def add_users_to_trip(
    trip_id: int,
    users: List[int],
    cur_user: dict = Depends(validate_token)
):
    trip = next((t for t in fake_trips_db if t["id"] == trip_id), None)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip["created_by"] != cur_user["id"]:
        raise HTTPException(
            status_code=403,
            detail="Only trip creator can add users"
        )

    try:
        new_users = await get_users(users, cur_user["token"])
    except HTTPException as e:
        raise e

    existing_ids = set(trip["users"])
    for user in new_users:
        if user["id"] not in existing_ids:
            trip["users"].append(user["id"])
    
    return await get_trip_info(trip['id'], cur_user)

@router.get("/user/{login}", response_model=List[TripResponse])
async def get_user_trips(
    login: str,
    cur_user: dict = Depends(validate_token)
):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{USER_SERVICE_URL}/login/{login}",
                params={"login": login},
                headers={"Authorization": f"Bearer {cur_user['token']}"}
            )
            user_data = response.json()

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"User {login} not found"
                )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="User service unavailable"
            )

    user_id = user_data["id"]
    
    user_trips = []
    for trip in fake_trips_db:
        if user_id in trip["users"] or trip["created_by"] == user_id:
            trip_info = await get_trip_info(trip["id"], cur_user)
            user_trips.append(trip_info)
    
    return user_trips