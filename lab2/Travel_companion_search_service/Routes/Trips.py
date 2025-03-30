from fastapi import Depends, HTTPException, APIRouter
from database import get_db
from sqlalchemy.orm import Session, joinedload
from fastapi import APIRouter

import Models.userModal as userModal
import Models.routeModal as routeModal
import Models.pointModal as pointModal
import Models.tripModal as tripModal

from schemas import TripCreate
from Routes.Users import get_current_user


router = APIRouter(prefix="/trips",
    tags=["trips"])


def get_trip_info(trip_id, db: Session = Depends(get_db)):
    db_trip = (
            db.query(tripModal.Trip)
            .options(
                joinedload(tripModal.Trip.route) 
                .joinedload(routeModal.Route.points)
                .joinedload(routeModal.RoutePoints.point),
                joinedload(tripModal.Trip.participants)
                .joinedload(tripModal.TripUser.user)
            )
            .filter(tripModal.Trip.id == trip_id)
            .first()
        )

    if not db_trip:
        raise HTTPException(status_code=400, detail="Trips not found")

    response = {
        "trip_id": db_trip.id,
        "name": db_trip.name,
        "description": db_trip.description,
        "max_users": db_trip.maxUsers,
        "main_user": {
            "id": db_trip.mainUser,
            "username": next(
                (p.user.username for p in db_trip.participants 
                    if p.user.id == db_trip.mainUser), None
            )
        },
        "route": {
            "id": db_trip.route.id,
            "name": db_trip.route.name,
            "points": [
                {
                    "stop_number": rp.stop_number,
                    "point_id": rp.point.id,
                    "name": rp.point.pointName,
                    "latitude": rp.point.px,
                    "longitude": rp.point.py
                } for rp in db_trip.route.points
            ]
        },
        "participants": [
            {
                "user_id": p.user.id,
                "username": p.user.username,
                "email": p.user.email
            } for p in db_trip.participants
        ]
    }

    response["route"]["points"].sort(key=lambda x: x["stop_number"])

    return response


@router.post('/create_trip')
def create_new_trip(trip: TripCreate, db: Session = Depends(get_db), current_user: userModal.User = Depends(get_current_user)):
    
    db_trip = db.query(tripModal.Trip).filter(tripModal.Trip.name == trip.name).first()
    if db_trip:
        raise HTTPException(status_code=400, detail="Trip with this name already registered")
    
    db_route = db.query(routeModal.Route).filter(routeModal.Route.id == trip.route_id).first()
    if not db_route:
        raise HTTPException(status_code=400, detail="The specified route was not found")
    
    db_users_count = db.query(userModal.User).filter(userModal.User.id.in_(trip.users)).count()
    
    if db_users_count != len(set(trip.users)):
        raise HTTPException(status_code=400, detail="One or more users were not found")
    
    if len(set(trip.users)) > trip.maxUsers:
        raise HTTPException(status_code=400, detail="There are more than the maximum number of fellow travelers")
    
    new_trip = tripModal.Trip(
            name = trip.name,
            mainUser = current_user.id,
            description = trip.description,
            start_at = trip.start_at,
            maxUsers = trip.maxUsers,
            route_id = trip.route_id
        )
    db.add(new_trip)
    db.flush() 

    participants = []
    for uid in list(set(trip.users)):
        participants.append(tripModal.TripUser(
            trip_id=new_trip.id,
            user_id=uid
        ))

    db.bulk_save_objects(participants)
    db.commit()
    db.refresh(new_trip)

    return get_trip_info(new_trip.id, db)
    
@router.get('/get_trip')
def get_trip_by_id(trip_id: int, db: Session = Depends(get_db), _: userModal.User = Depends(get_current_user)):
    return get_trip_info(trip_id, db)

@router.get('/')
def get_all_trips(db: Session = Depends(get_db), _: userModal.User = Depends(get_current_user)):
    db_trips = (
                db.query(tripModal.Trip)
                .options(
                    joinedload(tripModal.Trip.route) 
                    .joinedload(routeModal.Route.points)
                    .joinedload(routeModal.RoutePoints.point),
                    joinedload(tripModal.Trip.participants)
                    .joinedload(tripModal.TripUser.user)
                ).all()
            )

    if not db_trips:
        raise HTTPException(status_code=400, detail="Trips not found")

    response = [{
        "trip_id": db_trip.id,
        "name": db_trip.name,
        "description": db_trip.description,
        "max_users": db_trip.maxUsers,
        "main_user": {
            "id": db_trip.mainUser,
            "username": next(
                (p.user.username for p in db_trip.participants 
                    if p.user.id == db_trip.mainUser), None
            )
        },
        "route": {
            "id": db_trip.route.id,
            "name": db_trip.route.name,
            "points": [
                {
                    "stop_number": rp.stop_number,
                    "point_id": rp.point.id,
                    "name": rp.point.pointName,
                    "latitude": rp.point.px,
                    "longitude": rp.point.py
                } for rp in db_trip.route.points
            ]
        },
        "participants": [
            {
                "user_id": p.user.id,
                "username": p.user.username,
                "email": p.user.email
            } for p in db_trip.participants
        ]
    } for db_trip in db_trips]

    for i in range(len(response)):
        response[i]["route"]["points"].sort(key=lambda x: x["stop_number"])

    return response


@router.put('/add_user')
def add_user_to_trip_by_userId_and_tripId(userId: int, tripId:int, db: Session = Depends(get_db), _: userModal.User = Depends(get_current_user)):
    db_trip = db.query(tripModal.Trip).filter(tripModal.Trip.id == tripId).first()
    if not db_trip:
        raise HTTPException(status_code=400, detail="Trips not found")

    db_user = db.query(userModal.User).filter(userModal.User.id == userId).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    if db_trip.maxUsers and len(db_trip.participants) >= db_trip.maxUsers:
        raise HTTPException(status_code=400, detail="The maximum number of participants has been exceeded")

    existing = db.query(tripModal.Trip).filter(
        tripModal.TripUser.trip_id == tripId,
        tripModal.TripUser.user_id == userId
    ).first()
    
    if existing or userId == db_trip.mainUser:
        raise HTTPException(status_code=400, detail="The user has already been added to the trip")

    trip_user = tripModal.TripUser(trip_id=tripId, user_id=userId)
    db.add(trip_user)
    db.commit()
    return get_trip_info(tripId, db)

@router.delete('/delete_trip')

def delete_trip_by_id(tripId: int, db: Session = Depends(get_db), _: userModal.User = Depends(get_current_user)):

    db_trip = db.query(tripModal.Trip).filter(tripModal.Trip.id == tripId).first()
    if not db_trip:
        raise HTTPException(status_code=400, detail="Trips not found")

    db.query(tripModal.TripUser).filter(tripModal.TripUser.trip_id == tripId).delete()

    db_trip.route_id = None
    db.add(db_trip)
    db.delete(db_trip)
    db.commit()
    
    return {"status": "OK", "message": "Trip deleted"}