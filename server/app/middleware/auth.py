import os

import jwt
from config import Settings
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next):
        if request.url.path not in [
            "/",
            "/docs",
            "/openapi.json",
            "/api/users/login/google",
            "/api/users/login/apple",
            "/api/users/signup",
            "/api/users/token/refresh",
        ]:
            authorization: str = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=401, detail="Missing or invalid Authorization header"
                )

            token = authorization.split(" ")[1]

            try:
                payload = jwt.decode(
                    token,
                    self.settings.SECRET_KEY,
                    algorithms=[self.settings.ALGORITHM],
                )

                email = payload.get("sub")
                if not email:
                    raise HTTPException(
                        status_code=401, detail="Invalid token: Missing 'sub' field"
                    )

                request.state.user = {"email": email, "payload": payload}

            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=401, detail="Token has expired")
            except jwt.InvalidTokenError:
                raise HTTPException(status_code=401, detail="Invalid token")

        response = await call_next(request)
        return response
