from datetime import datetime, timedelta, timezone

import httpx
import jwt
from fastapi import HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token
from jose import JWTError, jwt


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


async def verify_apple_token(id_token: str) -> dict:
    try:
        apple_public_keys = await fetch_apple_public_keys()
        header = jwt.get_unverified_header(id_token)

        for key in apple_public_keys["keys"]:
            if key["kid"] == header["kid"]:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                break
        else:
            raise HTTPException(status_code=400, detail="Invalid Apple ID token")

        payload = jwt.decode(
            id_token,
            public_key,
            algorithms=["RS256"],
            audience="com.ellipsoid.tagi",
            issuer="https://appleid.apple.com",
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid Apple ID token")


async def fetch_apple_public_keys():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://appleid.apple.com/auth/keys")
        return response.json()
