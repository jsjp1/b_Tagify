from fastapi import Depends, FastAPI
from app.db import get_db, init_db
from app.router import router
from sqlalchemy.orm import Session

def get_application() -> FastAPI:
  init_db()
  app = FastAPI(title = "tagify backend server")
  
  app.include_router(router=router)

  @app.get("/")
  def get_root():
    return {"message": "FastAPI Version 0.115.6"}
  
  @app.get("/health/db")
  async def health_check(db: Session = Depends(get_db)):
      try:
          db.execute("SELECT 1")
          return {"status": "ok"}
      except Exception:
          return {"status": "error"}, 500

  return app

app = get_application()