from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(255), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="sessions")
