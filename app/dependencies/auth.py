from fastapi import Depends, HTTPException, Request
from app.db.session import SessionLocal
from app.crud import session_crud
from app.models.blacklist import BlackList
from app.models.session import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(role: str = ''):
    def _get_current_user(request: Request, db=Depends(get_db)):
        token = request.cookies.get("session")
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        db_session = db.query(Session).filter_by(id=token).first()
        if not db_session:
            raise HTTPException(status_code=401, detail="Invalid session")

        blacklisted = db.query(BlackList).filter(BlackList.ip == db_session.ip).first()
        if blacklisted:
            raise HTTPException(status_code=403, detail="Access denied: IP is blacklisted")

        user = db_session.user
        if role and user.role != role:
            raise HTTPException(status_code=403, detail="Forbidden: insufficient role")

        return user

    return _get_current_user