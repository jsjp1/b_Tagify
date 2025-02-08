from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config import get_settings
from app.db import get_db
from app.schemas.user import UserCreate, UserCreateResponse, UserLogin, UserLoginResponse, UserVideos, UserVideosResponse
from app.services.user import UserService
from app.util.auth import create_access_token, create_refresh_token

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/endpoint_test")
def endpoint_test():
  return {"message": "ok"}

@router.post("/login")
async def login(
  request: UserLogin,
  db: Session = Depends(get_db),
  settings = Depends(get_settings),
) -> UserLoginResponse:
  try:
    db_user = await UserService.get_user(request, db)

    access_token = create_access_token(settings, data={"sub": db_user.email})
    refresh_token = create_refresh_token(settings, data={"sub": db_user.email + "refresh"})

    db_user.access_token = access_token
    db_user.refresh_token = refresh_token

    return UserLoginResponse.model_validate(db_user, from_attributes=True)
      
  except HTTPException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/signup")
async def signup(
  request: UserCreate,
  db: Session = Depends(get_db),
) -> UserCreateResponse:
  try: 
    new_user = await UserService.create_user(request, db)
    return UserCreateResponse.model_validate(new_user, from_attributes=True)
  
  except HTTPException as e:
    raise e
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
  
@router.get("/{oauth_id}/videos")
async def videos(
  oauth_id: str,
  db: Session = Depends(get_db),
) -> List[UserVideosResponse]:
  try:
    request = UserVideos(oauth_id=oauth_id)
    videos = await UserService.get_user_videos(request, db)

    return [
        UserVideosResponse(
            title=video.title,
            link=video.link,
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