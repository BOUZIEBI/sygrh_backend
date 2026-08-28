from datetime import datetime, timedelta, UTC
from typing import Optional
from jose import jwt, JWTError
from app.core.config import settings

ALGORITHM = settings.JWT_ALGORITHM

def _create_token(data: dict, token_type: str, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    now = datetime.now(UTC)
    expire= now + expires_delta
    to_encode.update({ "iat": now, "exp": expire, "type": token_type })
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    lifetime = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(data, token_type="access", expires_delta=lifetime)

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    lifetime = expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token(data, token_type="refresh", expires_delta=lifetime)

def _decode_token(token: str, token_type: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        print("------- IMPRESSION DE PAYLOAD 4------------")
        print(payload)
        if payload.get("type") != token_type:
            raise JWTError(f"Invalid token type. Expected {token_type}.")
        return payload
    except JWTError as e:
        raise JWTError(f"Token validation error: {str(e)}")

def decode_access_token(token: str) -> dict:
    return _decode_token(token, token_type="access")

def decode_refresh_token(token: str) -> dict:
    return _decode_token(token, token_type="refresh")
