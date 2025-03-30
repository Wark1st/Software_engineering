from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from database import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    mainUser = Column(Integer, ForeignKey('users.id'))
    description = Column(String, index=True)
    start_at = Column(String, index=True)
    maxUsers = Column(Integer, index=True)
    route_id = Column(Integer, ForeignKey('routes.id'))
    route = relationship("Route")
    participants = relationship("TripUser", back_populates="trip")

class TripUser(Base):
    __tablename__ = "tripUsers"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey('trips.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    trip = relationship("Trip", back_populates="participants")
    user = relationship("User")