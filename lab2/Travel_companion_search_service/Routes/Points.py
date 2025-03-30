from fastapi import Depends, HTTPException, APIRouter
from database import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter

import Models.userModal as userModal
import Models.pointModal as pointModal
from schemas import PointCreate, Point
from Routes.Users import get_current_user


router = APIRouter(prefix="/points",
    tags=["points"])

@router.post('/create_point', response_model=Point)
def create_new_point(point: PointCreate, db: Session = Depends(get_db), _: userModal.User = Depends(get_current_user)):
    db_point = db.query(pointModal.Point).filter(pointModal.Point.pointName == point.pointName).first()
    if db_point:
        raise HTTPException(status_code=400, detail="Point with this name already registered")
    
    new_point = pointModal.Point(pointName=point.pointName, px = point.px, py = point.py)
    db.add(new_point)
    db.commit()
    db.refresh(new_point)

    return new_point

@router.get("/get_point", response_model=Point)
def get_point_by_name(pointName: str, db: Session = Depends(get_db), _: userModal.User = Depends(get_current_user)):
    db_point = db.query(pointModal.Point).filter(pointModal.Point.pointName == pointName).first()
    if not db_point:
        raise HTTPException(status_code=400, detail="The point was not found")
    
    return db_point


@router.get("/")
def get_all_points(db: Session = Depends(get_db), _: userModal.User = Depends(get_current_user)):
    db_points = db.query(pointModal.Point).all()
    if not db_points:
        raise HTTPException(status_code=400, detail="The points was not found")
    
    return db_points