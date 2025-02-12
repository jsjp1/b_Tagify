from typing import List

from fastapi import HTTPException
from passlib.context import CryptContext
from requests import Session
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.models.user import User
from app.models.video_metadata import VideoMetadata
from app.schemas.user import UserCreate, UserLogin, AllUsersResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    @staticmethod
    async def get_user(user: UserLogin, db: Session) -> User:
        """
        존재하는 사용자 확인 및 반환
        """
        db_user = (
            db.query(User)
            .filter(and_(User.email == user.email, User.oauth_id == user.oauth_id))
            .first()
        )
        if not db_user:
            raise HTTPException(
                status_code=400, detail=f"Cannot find user {user.email}"
            )

        return db_user
    
    
    @staticmethod
    async def get_all_users(db: Session) -> List[User]:
        """
        모든 사용자 정보를 가져오는 메서드
        """
        users = db.query(User).all()
        
        return users


    @staticmethod
    async def create_user(user: UserCreate, db: Session) -> User:
        """
        새로운 사용자 생성
        """
        existing_user = (
            db.query(User)
            .filter(and_(User.email == user.email, User.oauth_id == user.oauth_id))
            .first()
        )
        if existing_user:
            raise HTTPException(
                status_code=400, detail="Email(Social) already registered"
            )

        try:
            db_user = User(
                username=user.username,
                oauth_provider=user.oauth_provider,
                oauth_id=user.oauth_id,
                email=user.email,
                profile_image=user.profile_image,
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
