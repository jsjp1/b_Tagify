from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.video import VideoAnalyze
from config import get_settings
from app.services.video import VideoService

router = APIRouter(prefix="/videos", tags=["videos"])

@router.get("/endpoint_test")
def endpoint_test():
  return {"message": "ok"}

@router.post("/analyze")
async def analyze(
  request: VideoAnalyze,
  db: Session = Depends(get_db),
  settings = Depends(get_settings),
):
  try:
    tags = await VideoService.analyze_video(request, db, settings)
  
    return {"message": "success", "tags": tags}
    
  except HTTPException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")  
  
  