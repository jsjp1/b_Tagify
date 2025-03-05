from datetime import datetime, timedelta, timezone

import httpx
import jwt
from config import Settings
from fastapi import HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token


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


async def verify_google_token(id_token_str: str, settings: Settings) -> dict:
    try:
        id_info = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            settings.GOOGLE_IOS_CLIENT_ID,
        )
        return id_info
    except ValueError:
        try:
            id_info = id_token.verify_oauth2_token(
                id_token_str,
                requests.Request(),
                settings.GOOGLE_ANDROID_CLIENT_ID,
            )
            return id_info

        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid Google ID token: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")