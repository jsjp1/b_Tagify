import json
from datetime import datetime, timedelta, timezone

import httpx
import jwt
import requests as apple_requests
from config import Settings
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
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
        raise HTTPException(status_code=401, detail=f"Token expired: {str(e)}")
    except jwt.DecodeError as e:
        raise HTTPException(status_code=401, detail=f"Token decode error: {str(e)}")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
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
            raise HTTPException(
                status_code=400, detail=f"Invalid Google ID token: {str(e)}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def verify_apple_token(id_token_str: str, settings: Settings) -> dict:
    try:
        apple_keys_url = "https://appleid.apple.com/auth/keys"
        response = apple_requests.get(apple_keys_url)
        apple_keys = response.json().get("keys", [])

        if not apple_keys:
            raise HTTPException(
                status_code=500, detail="Unable to fetch Apple public keys"
            )

        unverified_header = jwt.get_unverified_header(id_token_str)
        key_id = unverified_header.get("kid")

        apple_key = next((key for key in apple_keys if key["kid"] == key_id), None)
        if not apple_key:
            raise HTTPException(status_code=400, detail="Apple public key not found")

        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(apple_key))

        id_info = jwt.decode(
            id_token_str,
            public_key,
            algorithms=["RS256"],
            audience=settings.APPLE_CLIENT_ID,
            issuer="https://appleid.apple.com",
        )

        return id_info

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Apple ID Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Apple ID Token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
