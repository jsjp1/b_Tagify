from fastapi import FastAPI
from db import init_db

init_db()
app = FastAPI()

@app.get("/")
def get_root():
  return {"message": "FastAPI Version 0.115.6"}

@app.get("/health_check")
def health_check():
  return {"message": "alive"}