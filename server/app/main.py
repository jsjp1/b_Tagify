import os
import time
from contextlib import asynccontextmanager

import httpx
import jwt
from app.db import get_db, init_db
from app.middleware.auth import AuthMiddleware
from app.middleware.exception_handler import ExceptionHandlerMiddleware
from app.middleware.time import QueryTimeMiddleware
from app.router import router
from config import get_settings
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="tagify backend server", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router=router)

app.add_middleware(AuthMiddleware, settings=get_settings())
app.add_middleware(ExceptionHandlerMiddleware)
# app.add_middleware(QueryTimeMiddleware)


@app.get("/")
def get_root():
    return {"message": "FastAPI Version 0.115.6"}


@app.get("/health/db")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/privacy-policy", response_class=FileResponse)
async def privacy_policy():
    file_path = os.path.join("static", "privacy_policy.html")
    return FileResponse(file_path, media_type="text/html")


@app.get("/terms-of-service", response_class=FileResponse)
async def terms_of_service():
    return FileResponse("static/terms_of_service.html", media_type="text/html")
