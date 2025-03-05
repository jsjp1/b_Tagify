from typing import List

import jwt
from app.models.user import User
from app.models.video_metadata import VideoMetadata
from app.schemas.user import (AllUsersResponse, TokenRefresh, UserCreate,
                              UserLogin)
from app.util.auth import (create_access_token, decode_token,
                           verify_google_token)
from config import Settings
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    @staticmethod
    async def login_google(user: UserLogin, db: Session, settings: Settings) -> User:
        google_user_info = await verify_google_token(
            user.id_token, settings
        )
        google_id = google_user_info.get("sub")

        if not google_id:
            raise HTTPException(status_code=400, detail="Invalid Google ID Token")

        db_user = db.query(User).filter(User.oauth_id == google_id).first()
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

    @staticmethod
    async def token_refresh(token: TokenRefresh, settings: Settings) -> str:
        """
        refresh 토큰 검증 후 access token 새로 발급
        """
        try:
            payload = decode_token(settings, token.refresh_token)

            if not payload:
                raise jwt.InvalidTokenError(status_code=401, detail="Invalid token")

            # TODO : 저장된 refresh_token 과 비교해서 존재하면 create access token
            new_access_token = create_access_token(settings, data={"sub": f"{payload}"})

            return new_access_token

        except jwt.InvalidSignatureError:
            raise HTTPException(status_code=401, detail="Invalid token signature")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
