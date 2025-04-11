import time

from starlette.middleware.base import BaseHTTPMiddleware


class QueryTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start_time
        print(f"{request.url.path} took {duration:.4f} seconds")
        return response
