from sqlalchemy.orm import Session as DBSession
from app.models.session import Session
from app.core.security import generate_session_token

def create_session(user_id: int, request, db: DBSession) -> str:
    token = generate_session_token()
    db_session = Session(id=token, user_id=user_id, ip=get_client_ip(request))
    db.add(db_session)
    db.commit()
    return token

def get_user_by_session(token: str, db: DBSession):
    db_session = db.query(Session).filter_by(id=token).first()
    return db_session.user if db_session else None

def delete_session(token: str, db: DBSession):
    db.query(Session).filter_by(id=token).delete()
    db.commit()

def get_client_ip(request):
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.client.host
    return ip