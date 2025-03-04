from datetime import datetime, timedelta, timezone

import httpx
import jwt
from fastapi import HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token

# from jose import JWTError, jwt


def create_access_token(settings, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(settings, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(settings, token: str):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload["sub"]

    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail=f"Token expired: {e}")
    except jwt.DecodeError as e:
        raise HTTPException(status_code=401, detail=f"Token decode error: {e}")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


async def verify_google_token(id_token_str: str, google_client_id: str) -> dict:
    try:
        id_info = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            google_client_id,
        )
        return id_info
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Google ID token")