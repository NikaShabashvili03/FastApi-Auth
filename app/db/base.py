from app.db.session import engine
from app.db.session import SessionLocal
from sqlalchemy.orm import declarative_base

Base = declarative_base()