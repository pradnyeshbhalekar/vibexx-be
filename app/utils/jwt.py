import jwt
import os
from datetime import datetime, timedelta

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXP_MINUTES = 60


def create_jwt(payload: dict):
    payload = payload.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt(token: str):
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])