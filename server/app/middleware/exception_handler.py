from traceback import print_exception

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispaych(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            print_exception(e)
            return JSONResponse(
                status_code=500,
                content={
                    "error": e.__class__.__name__,
                    "messages": e.args,
                },
            )
