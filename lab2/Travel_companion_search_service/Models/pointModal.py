from sqlalchemy import Column, Integer, String, Float
from database import Base
from sqlalchemy.orm import relationship

class Point(Base):
    __tablename__ = "points"
    
    id = Column(Integer, primary_key=True, index=True)
    pointName = Column(String, unique=True, index=True)
    px = Column(Float)
    py = Column(Float)