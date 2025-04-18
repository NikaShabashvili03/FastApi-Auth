from sqlalchemy import Column, Integer, String, Enum, func, DateTime
from app.db.base import Base
from sqlalchemy.orm import relationship
import enum

class UserRole(enum.Enum):
    admin = "admin"
    moderator = "moderator"
    user = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))

    created_at = Column(DateTime, default=func.now())
    role = Column(Enum(UserRole), default=UserRole.user)
    
    sessions = relationship("Session", back_populates="user")
    blacklists_added = relationship("BlackList", back_populates="added_by_user")