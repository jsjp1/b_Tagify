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
            "/home",
            "/static/img/app_icon.png",
            "/static/img/download_on_the_appstore.svg",
            "/privacy-policy",
            "/terms-of-service",
            "/static/privacy_policy.html",
            "/static/terms_of_service.html",
            "/api/users/login",
            "/api/users/token/refresh",
            "/api/users/token/check/refresh_token",
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
