from fastapi import FastAPI
from db import init_db
from router import router

init_db()
app = FastAPI()
app.include_router(router=router)

@app.get("/")
def get_root():
  return {"message": "FastAPI Version 0.115.6"}

@app.get("/health_check")
def health_check():
  return {"message": "alive"}