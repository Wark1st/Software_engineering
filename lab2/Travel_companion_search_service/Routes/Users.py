from fastapi import Depends, HTTPException, status, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
import Models.userModal as userModal, schemas, auth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(prefix="/users",
    tags=["users"])

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = auth.verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(userModal.User).filter(userModal.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(userModal.User).filter(userModal.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = userModal.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(userModal.User).filter(userModal.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: userModal.User = Depends(get_current_user)):
    return current_user

@router.get("/get_user", response_model=schemas.User)
def get_user_by_login(login: str, db: Session = Depends(get_db), _: userModal.User = Depends(get_current_user)):
    db_user = db.query(userModal.User).filter(userModal.User.username == login).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="The user was not found")
    
    return db_user

@router.get("/", response_model=list[schemas.User])
def get_user_by_login(db: Session = Depends(get_db), _: userModal.User = Depends(get_current_user)):
    db_users = db.query(userModal.User).all()
    if not db_users:
        raise HTTPException(status_code=400, detail="The users was not found")
    
    return db_users

# @router.get("/get_user_by_mask", response_model=list[schemas.User])
# def get_user_by_mask(mask: str = '', db: Session = Depends(get_db), _: userModal.User = Depends(get_current_user)):
#     return db.query(userModal.User).filter(or_(userModal.User.name.ilike(f"%{mask}%"), userModal.User.lastname.ilike(f"%{mask}%"))).all()
    
