from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def get_root():
  return {"message": "FastAPI Version 0.115.6"}