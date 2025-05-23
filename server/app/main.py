import asyncio
import os
from contextlib import asynccontextmanager

from app.db import get_db, init_db
from app.middleware.auth import AuthMiddleware
from app.middleware.exception_handler import ExceptionHandlerMiddleware
from app.router import router
from config import get_settings
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="tagify backend server", lifespan=lifespan)

# pytest 위해 임시로 절대경로 추가
base_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(base_dir, "..", "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(router=router)

app.add_middleware(AuthMiddleware, settings=get_settings())
app.add_middleware(ExceptionHandlerMiddleware)
# app.add_middleware(QueryTimeMiddleware)

@app.get("/")
def get_root():
    print({type(asyncio.get_event_loop_policy())})
    return {"message": "FastAPI Version 0.115.6"}


@app.get("/health/db")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


HTML_MEDIA_TYPE = "text/html"

@app.get("/home", response_class=FileResponse)
async def home():
    return FileResponse("static/home.html", media_type=HTML_MEDIA_TYPE)


@app.get("/privacy-policy", response_class=FileResponse)
async def privacy_policy():
    return FileResponse("static/privacy_policy.html", media_type=HTML_MEDIA_TYPE)


@app.get("/terms-of-service", response_class=FileResponse)
async def terms_of_service():
    return FileResponse("static/terms_of_service.html", media_type=HTML_MEDIA_TYPE)
