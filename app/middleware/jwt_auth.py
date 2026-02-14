from flask import request
from app.utils.jwt import decode_jwt

def require_jwt():
    auth = request.headers.get("Authorization")

    if not auth or not auth.startswith("Bearer "):
        raise Exception("Missing JWT")

    token = auth.split(" ")[1]
    return decode_jwt(token)