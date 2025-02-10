from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.video import UserVideos, UserVideosResponse, VideoAnalyze, VideoAnalyzeResponse
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
) -> VideoAnalyzeResponse:
  try:
    video_id = await VideoService.analyze_video(request, db, settings)
  
    return VideoAnalyzeResponse.model_validate(video_id, from_attributes=True)
    
  except HTTPException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")  
  
  
@router.get("/user")
async def videos(
  oauth_id: str,
  db: Session = Depends(get_db),
) -> List[UserVideosResponse]:
  try:
    request = UserVideos(oauth_id=oauth_id)
    videos = await VideoService.get_user_videos(request, db)

    return [
        UserVideosResponse(
            title=video.title,
            url=video.url,
            thumbnail=video.thumbnail,
            summation=video.summation,
            video_length=video.video_length,
            tags=[tag.tag.tagname for tag in video.video_tags] if video.video_tags else []
        )
        for video in videos
    ]

  except HTTPException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")