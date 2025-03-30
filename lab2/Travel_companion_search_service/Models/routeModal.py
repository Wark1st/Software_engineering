from sqlalchemy import Column, ForeignKey, Integer, String
from database import Base
from sqlalchemy.orm import relationship

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String, index=True)
    points = relationship("RoutePoints", back_populates="route")

class RoutePoints(Base):
    __tablename__ = "routePoints"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey('routes.id'))
    point_id = Column(Integer, ForeignKey('points.id'))
    stop_number = Column(Integer, index=True)
    route = relationship("Route", back_populates="points")
    point = relationship("Point")