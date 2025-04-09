from app.db import get_db, init_db
from app.middleware.auth import AuthMiddleware
from app.middleware.exception_handler import ExceptionHandlerMiddleware
from app.router import router
from config import get_settings
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

app = FastAPI(title="tagify backend server")


@app.on_event("startup")
async def on_startup():
    await init_db()


app.include_router(router=router)

app.add_middleware(AuthMiddleware, settings=get_settings())
app.add_middleware(ExceptionHandlerMiddleware)


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
