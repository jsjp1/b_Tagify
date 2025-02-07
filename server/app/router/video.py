from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.video import Video
from config import get_settings

router = APIRouter(prefix="/videos", tags=["videos"])

@router.get("/endpoint_test")
def endpoint_test():
  return {"message": "ok"}

@router.post("/analyze")
def analyze(
  request: Video,
  db: Session = Depends(get_db),
  settings = Depends(get_settings),
):
  """
  video link -> generate 3 tags
  """
  pass
  
  
  