from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    __tablename__ = "users_info"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String)
    full_name = Column(String)
