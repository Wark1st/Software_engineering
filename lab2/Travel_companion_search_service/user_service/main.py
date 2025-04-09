from fastapi import FastAPI
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
import httpx
import os
from typing import List
from auth import validate_token
from database import get_db, engine
import userModal as userModal

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

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")

userModal.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/register")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    response = {}
    async with httpx.AsyncClient() as client:
        try:
            auth_response = await client.post(
                f"{AUTH_SERVICE_URL}/users/register",
                json={"username": user.username, "password": user.password}
            )

            response = auth_response.json()
            if auth_response.status_code != 200:
                detail = response['detail']
                raise HTTPException(
                    status_code=auth_response.status_code,
                    detail=f'auth service response: {detail}',
                )

        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authorization service unavailable"
            )

    new_user = userModal.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/get_user_by_mask", response_model=list[UserResponse])
def get_user_by_mask(mask: str = '', db: Session = Depends(get_db), _: userModal.User = Depends(validate_token)):
    return db.query(userModal.User).filter(or_(userModal.User.username.ilike(f"%{mask}%"), userModal.User.full_name.ilike(f"%{mask}%"))).all()

@app.get("/login/{login}",  response_model=UserResponse)
async def get_user_by_login(login: str, db: Session = Depends(get_db), _ = Depends(validate_token)):
    user = db.query(userModal.User).filter(userModal.User.username == login).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/", response_model=List[UserResponse])
async def get_all_users(db: Session = Depends(get_db), _ = Depends(validate_token)):
    return db.query(userModal.User).all()

@app.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db), _ = Depends(validate_token)):
    global fake_users_db

    user = db.query(userModal.User).filter(userModal.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_info: UserInfo, db: Session = Depends(get_db), _ = Depends(validate_token)):
    user = db.query(userModal.User).filter(userModal.User.id == user_id).first()
    if not user:    
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in user_info.dict().items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@app.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db), _ = Depends(validate_token)):
    
    user = db.query(userModal.User).filter(userModal.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
