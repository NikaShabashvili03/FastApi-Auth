from sqlalchemy import Column, String, DateTime, func, ForeignKey, Integer
from app.db.base import Base
from sqlalchemy.orm import relationship

class BlackList(Base):
    __tablename__ = "blacklists"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String(45))
    reason = Column(String(255))

    added_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    added_by_user = relationship("User", back_populates="blacklists_added")

    created_at = Column(DateTime, default=func.now())