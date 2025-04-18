from fastapi import APIRouter, Depends, Response, Request, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import user as user_schema
from app.models.user import User, UserRole
from app.models.session import Session as SessionModel
from app.core import security
from app.db.session import SessionLocal
from app.crud import session_crud
from app.dependencies.auth import get_db, get_current_user
from typing import List
from app.schemas.session import SessionOut
from app.schemas import blacklist as blacklist_schema
from app.schemas.blacklist import BlackListCreate 
from app.models.blacklist import BlackList

router = APIRouter()

@router.post(
    "/register",
    summary="Register",
    tags=["Allow Any"]
)
def register(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=user.email).first():
        raise HTTPException(status_code=400, detail="email taken")
    db_user = User(email=user.email, hashed_password=security.hash_password(user.password))
    db.add(db_user)
    db.commit()
    return {"msg": "Registered"}

@router.post("/login", 
    response_model=user_schema.UserOut,
    summary="Login",
    tags=["Allow Any"]
)
def login(user: user_schema.UserCreate, request: Request, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(email=user.email).first()
    if not db_user or not security.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = session_crud.create_session(db_user.id, request, db)
    response.set_cookie(key="session", value=token, httponly=True)
    return db_user

@router.post(
    "/logout",
    response_model=user_schema.UserOut,
    summary="Logout",
    tags=["Authentificated"]
)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("session")
    if token:
        session_crud.delete_session(token, db)
    response.delete_cookie("session")
    return {"msg": "Logged out"}

@router.get(
    "/me", 
    response_model=user_schema.UserOut,
    summary="Get Profile (Authentificated)",
    tags=["Authentificated"]
)
def me(current_user: User = Depends(get_current_user())):
    return current_user


@router.get("/sessions", response_model=List[SessionOut])
def get_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_sessions = db.query(SessionModel).filter_by(user_id=current_user.id).distinct(SessionModel.user_id).all()
    return db_sessions


@router.post(
    "/blacklist",
    response_model=blacklist_schema.BlackListOut,
    summary="Create a blacklist entry (Admin only)",
    tags=["Admin"]
)
def create_blacklist_entry(
        entry: BlackListCreate, 
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user(UserRole.admin))
    ):
        session = db.query(SessionModel).filter(SessionModel.ip == entry.ip).first()
        
        if session:
            user = session.user
            if user.role == UserRole.admin:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot blacklist IP belonging to an admin user."
                )
        
        db_entry = BlackList(ip=entry.ip, reason=entry.reason, added_by=current_user.id)
        db.add(db_entry)

        db.query(SessionModel).filter(SessionModel.ip == entry.ip).delete()
        
        db.commit()
        db.refresh(db_entry)
        return db_entry