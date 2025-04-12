from fastapi import Depends, HTTPException, Request
from app.db.session import SessionLocal
from app.crud import session_crud

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request, db=Depends(get_db)):
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = session_crud.get_user_by_session(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    return user