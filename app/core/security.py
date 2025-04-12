from passlib.hash import bcrypt
from uuid import uuid4

def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.verify(password, hashed)

def generate_session_token() -> str:
    return str(uuid4())
