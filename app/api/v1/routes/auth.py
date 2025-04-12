from fastapi import APIRouter, Depends, Response, Request, HTTPException
from sqlalchemy.orm import Session
from app.schemas import user as user_schema
from app.models.user import User
from app.models.session import Session as SessionModel
from app.core import security
from app.db.session import SessionLocal
from app.crud import session_crud
from app.dependencies.auth import get_db, get_current_user
from typing import List
from app.schemas.session import SessionOut


router = APIRouter()

@router.post("/register")
def register(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter_by(username=user.username).first():
        raise HTTPException(status_code=400, detail="Username taken")
    db_user = User(username=user.username, hashed_password=security.hash_password(user.password))
    db.add(db_user)
    db.commit()
    return {"msg": "Registered"}

@router.post("/login")
def login(user: user_schema.UserCreate, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(username=user.username).first()
    if not db_user or not security.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = session_crud.create_session(db_user.id, db)
    response.set_cookie(key="session", value=token, httponly=True)
    return {"msg": "Logged in"}

@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("session")
    if token:
        session_crud.delete_session(token, db)
    response.delete_cookie("session")
    return {"msg": "Logged out"}

@router.get("/me", response_model=user_schema.UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/sessions", response_model=List[SessionOut])
def get_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_sessions = db.query(SessionModel).filter_by(user_id=current_user.id).distinct(SessionModel.user_id).all()
    return db_sessions