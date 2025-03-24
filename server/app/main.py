from app.db import get_db, init_db
from app.middleware.auth import AuthMiddleware
from app.middleware.exception_handler import ExceptionHandlerMiddleware
from app.router import router
from config import get_settings
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text


def get_application() -> FastAPI:
    init_db()
    app = FastAPI(title="tagify backend server")

    app.include_router(router=router)

    app.add_exception_handler(ExceptionHandlerMiddleware)
    app.add_middleware(AuthMiddleware, settings=get_settings())

    @app.get("/")
    def get_root():
        return {"message": "FastAPI Version 0.115.6"}

    @app.get("/health/db")
    async def health_check(db: Session = Depends(get_db)):
        try:
            db.execute(text("SELECT 1"))
            return {"status": "ok"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    return app


app = get_application()
