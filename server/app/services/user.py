from fastapi import HTTPException
from requests import Session
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.user import UserCreate, UserCreateResponse, UserLogin, UserLoginResponse
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService():
  @staticmethod
  async def get_user(user: UserLogin, db: Session) -> UserLoginResponse:
    """
    존재하는 사용자 확인 및 반환
    """
    db_user = db.query(User).filter(and_(User.email == user.email, User.oauth_id == user.oauth_id)).first()
    if not db_user:
      raise HTTPException(status_code=400, detail=f"Cannot find user {user.email}")
    
    return UserLoginResponse.model_validate(db_user, from_attributes=True)
    
  @staticmethod
  async def create_user(user: UserCreate, db: Session) -> UserCreateResponse:
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
      
      return UserCreateResponse.model_validate(db_user, from_attributes=True)
    
    except IntegrityError:
      db.rollback()
      raise HTTPException(status_code=500, detail="Database integrity error")
    except Exception as e:
      db.rollback()
      raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")