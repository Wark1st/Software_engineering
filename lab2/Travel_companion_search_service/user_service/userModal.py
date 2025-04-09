from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa

Base = declarative_base()

class User(Base):
    __tablename__ = "users_info"
    
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(50), nullable=False, unique=True)
    email = sa.Column(sa.String(100), nullable=False)
    full_name = sa.Column(sa.String(100), nullable=False)