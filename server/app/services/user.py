from typing import List
from fastapi import HTTPException
from requests import Session
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from app.models.user import User
from app.models.video import Video
from app.models.video_tag import VideoTag
from app.schemas.user import UserCreate, UserLogin, UserVideos
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService():
  @staticmethod
  async def get_user(user: UserLogin, db: Session) -> User:
    """
    존재하는 사용자 확인 및 반환
    """
    db_user = db.query(User).filter(and_(User.email == user.email, User.oauth_id == user.oauth_id)).first()
    if not db_user:
      raise HTTPException(status_code=400, detail=f"Cannot find user {user.email}")
    
    return db_user
    
  @staticmethod
  async def create_user(user: UserCreate, db: Session) -> User:
    """
    새로운 사용자 생성
    """
    existing_user = db.query(User).filter(and_(User.email == user.email, User.oauth_id == user.oauth_id)).first()
    if existing_user:
      raise HTTPException(status_code=400, detail="Email(Social) already registered")
    
    try:
      db_user = User(
        username = user.username,
        oauth_provider = user.oauth_provider,
        oauth_id = user.oauth_id,
        email = user.email,
        profile_image = user.profile_image,
      )
      
      db.add(db_user)
      db.commit()
      db.refresh(db_user)
      
      return db_user
    
    except IntegrityError:
      db.rollback()
      raise HTTPException(status_code=500, detail="Database integrity error")
    except Exception as e:
      db.rollback()
      raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
  @staticmethod
  async def get_user_videos(user: UserVideos, db: Session) -> List[Video]:
    """
    유저가 소유한 비디오 정보를 모두 반환
    """
    videos = (
        db.query(Video)
        .join(User)
        .filter(User.oauth_id == user.oauth_id)
        .options(joinedload(Video.video_tags).joinedload(VideoTag.tag)) 
        .all()
    )
      
    return videos