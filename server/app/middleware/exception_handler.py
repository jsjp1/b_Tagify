from functools import wraps

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


def handle_exceptions(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        try:
            return await func(request, *args, **kwargs)
        except HTTPException as e:
            raise e
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"detail": f"Unexpected error: {str(e)}"},
            )

    return wrapper
