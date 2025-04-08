from fastapi import FastAPI
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import httpx
import os
from typing import List
from auth import validate_token

class UserInfo(BaseModel):
    username: str
    email: str
    full_name: str

class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    full_name: str

class UserResponse(UserInfo):
    id: int

fake_users_db = []
fake_db_id = 4

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")

app = FastAPI()

@app.post("/register")
async def create_user(user: UserCreate):
    global fake_db_id
    user_id = 0
    response = {}
    async with httpx.AsyncClient() as client:
        try:
            auth_response = await client.post(
                f"{AUTH_SERVICE_URL}/users/register",
                json={"username": user.username, "password": user.password}
            )
            print(auth_response.json())
            response = auth_response.json()
            if auth_response.status_code != 200:
                detail = response['detail']
                raise HTTPException(
                    status_code=auth_response.status_code,
                    detail=f'auth service response: {detail}',
                )
            print(user_id)
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authorization service unavailable"
            )

    new_user = {
        "id": response['id'],
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name
    }
    fake_users_db.append(new_user)
    fake_db_id += 1
    
    return new_user

@app.get("/", response_model=List[UserResponse])
async def get_all_users(_ = Depends(validate_token)):
    return fake_users_db

@app.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, _ = Depends(validate_token)):
    global fake_users_db
    print(user_id, fake_users_db)
    user = next((u for u in fake_users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("login/{login}", response_model=UserResponse)
async def get_user_by_login(login: str, _ = Depends(validate_token)):
    global fake_users_db
    user = next((u for u in fake_users_db if u["username"] == login), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_info: UserInfo, _ = Depends(validate_token)):
    user = next((u for u in fake_users_db if u["id"] == user_id), None)
    if not user:    
        raise HTTPException(status_code=404, detail="User not found")
    
    user.update(user_info)
    return user

@app.delete("/{user_id}")
async def delete_user(user_id: int, _ = Depends(validate_token)):
    global fake_users_db
    
    user = next((u for u in fake_users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    fake_users_db = [u for u in fake_users_db if u["id"] != user_id]
    
    return {"message": "User deleted successfully"}