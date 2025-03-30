from fastapi import Depends, HTTPException, APIRouter
from database import get_db
from sqlalchemy.orm import Session, joinedload
from fastapi import APIRouter

import Models.userModal as userModal
import Models.routeModal as routeModal
import Models.pointModal as pointModal

from schemas import RouteCreate
from Routes.Users import get_current_user


router = APIRouter(prefix="/routes",
    tags=["routes"])

def get_route_with_points(route_id, db: Session = Depends(get_db)):
    db_route = (
        db.query(routeModal.Route)
        .options(
            joinedload(routeModal.Route.points)
            .joinedload(routeModal.RoutePoints.point)
        )
        .filter(routeModal.Route.id == route_id)
        .first()
    )

    if not db_route:
        raise HTTPException(status_code=400, detail="Route not found")

    return {
        "id": db_route.id,
        "name": db_route.name,
        "description": db_route.description,
        "points": [
            {
                "point_id": p.point.id,
                "point_name": p.point.pointName,
                "latitude": p.point.px,
                "longitude": p.point.py,
                "stop_number": p.stop_number
            } for p in db_route.points
        ]
    }


@router.post('/create_route')
def create_new_route(route: RouteCreate, db: Session = Depends(get_db), _: userModal.User = Depends(get_current_user)):
    db_route = db.query(routeModal.Route).filter(routeModal.Route.name == route.name).first()
    if db_route:
        raise HTTPException(status_code=400, detail="Route with this name already registered")
    
    points = set(route.points)
    db_points = db.query(pointModal.Point).filter(pointModal.Point.id.in_(points)).all()
    if len(list(db_points)) < len(points):
        raise HTTPException(status_code=400, detail="Оne or more of the specified points does not exist")
    
    new_route = routeModal.Route(
        name=route.name,
        description=route.description
    )
    db.add(new_route)
    db.commit()
    db.refresh(new_route)
    
    for i, point_id in enumerate(route.points):
        new_route_point = routeModal.RoutePoints(
            route_id=new_route.id,
            point_id=point_id,
            stop_number= i + 1
        )
        db.add(new_route_point)
    db.commit()

    return get_route_with_points(new_route.id, db)

@router.get('/')
def get_all_routes(db: Session = Depends(get_db), _: userModal.User = Depends(get_current_user)):
    db_routes = (
        db.query(routeModal.Route)
        .options(
            joinedload(routeModal.Route.points)
            .joinedload(routeModal.RoutePoints.point)
        ).all()
    )

    if not db_routes:
        raise HTTPException(status_code=400, detail="Routes not found")

    return [{
        "id": db_route.id,
        "name": db_route.name,
        "description": db_route.description,
        "points": [
            {
                "point_id": p.point.id,
                "point_name": p.point.pointName,
                "latitude": p.point.px,
                "longitude": p.point.py,
                "stop_number": p.stop_number
            } for p in db_route.points
        ]
    } for db_route in db_routes]
    

@router.get('/get_route')
def get_route_by_id(id: int, db: Session = Depends(get_db), _: userModal.User = Depends(get_current_user)):
    return get_route_with_points(id, db)

# @router.get('/get_route')
# def get_route_by_id(routeId: int, db: Session = Depends(get_db), _: userModal.User = Depends(get_current_user)):
#     # res = (db.query(
#     #     routeModal.Route,
#     #     routeModal.RoureUsers,
#     #     userModal.User,
#     #     routeModal.RoutePoints,
#     #     pointModal.Point
#     # )
#     # .select_from(routeModal.Route)
#     # .outerjoin(routeModal.RoureUsers, routeModal.Route.id == routeModal.RoureUsers.route_id)
#     # .outerjoin(userModal.User, routeModal.RoureUsers.user_id == userModal.User.id)
#     # .outerjoin(routeModal.RoutePoints, routeModal.Route.id == routeModal.RoutePoints.route_id)
#     # .outerjoin(pointModal.Point, routeModal.RoutePoints.point_id == pointModal.Point.id)
#     # .filter(routeModal.Route.id == 1)
#     # .all())

#     # return res
#     db_route = db.query(routeModal.Route).filter(routeModal.Route.id == routeId).first()
#     if not db_route:
#         raise HTTPException(status_code=400, detail="Route with this id not found")

#     db_users_route = db.query(routeModal.RouteUsers).filter(routeModal.RouteUsers.route_id == db_route.id).all()
#     user_ids = [user.user_id for user in db_users_route]
#     db_users = db.query(userModal.User).filter(userModal.User.id.in_(user_ids)).all()

#     users_for_response = [{"id": user.id, "username": user.username, "email": user.email}  for user in db_users]

#     db_points_route = db.query(routeModal.RoutePoints).filter(routeModal.RoutePoints.route_id == db_route.id).order_by(routeModal.RoutePoints.stop_number).all()
    
#     points_ids = [points.point_id for points in db_points_route]
#     db_points = db.query(pointModal.Point).filter(pointModal.Point.id.in_(points_ids)).all()
    
#     print(points_ids)

#     return {
#         "routeName": db_route.routeName,
#         "mainUser": db_route.mainUser,
#         "description": db_route.description,
#         "maxUsers": db_route.maxUsers,
#         "points": sorted(db_points, key=lambda p: points_ids.index(p.id)),
#         "users": users_for_response
#     }

# @router.get('/')
# def get_all_routes(db: Session = Depends(get_db), _: userModal.User = Depends(get_current_user)):
#     db_route = db.query(routeModal.Route).all()
#     return db_route


# @router.put('/add_user')
# def add_user_to_route_by_login(add_info: AddUserToRoute, db: Session = Depends(get_db), current_user: userModal.User = Depends(get_current_user)):
#     #Можно добавить пользователя только в свою поездку или добавить себя в поездку
#     db_route = db.query(routeModal.Route).filter(routeModal.Route.id == add_info.routeId).first()
#     if not db_route:
#         raise HTTPException(status_code=400, detail="Route with this id not found")

#     if not add_info.userLogin:
#         user_info = {"username": current_user.username, "id": current_user.id}
#     else:
#         db_user = db.query(userModal.User).filter(userModal.User.username == add_info.userLogin).first()
#         if not db_user:
#             raise HTTPException(status_code=400, detail="User with this login not found")
#         user_info = {"username": db_user.username, "id": db_user.id}
    
#     if user_info["username"] != current_user.username and db_route.mainUser != current_user.username:
#         raise HTTPException(status_code=403, detail="Insufficient permissions to add a user to the trip")
    
#     db_users_route = db.query(routeModal.RouteUsers).filter(routeModal.RouteUsers.route_id == db_route.id).all()

#     print([el.id for el in db_users_route])

#     if len(db_users_route) + 1 > db_route.maxUsers:
#         raise HTTPException(status_code=400, detail="The maximum number of users has been exceeded")
    
#     if user_info["id"] in [el for el in db_users_route]:
#         raise HTTPException(status_code=400, detail="The user has already been added to this trip")
    
#     new_user = routeModal.RouteUsers(
#             route_id = db_route.id,
#             user_id = user_info["id"],
#             )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

    
#     return get_route_by_id(db_route.id, db)