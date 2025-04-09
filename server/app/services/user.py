from typing import List

import jwt
from app.models.user import User
from app.schemas.user import (
    TokenRefresh,
    UserLogin,
    UserUpdateName,
    UserUpdateProfileImage,
)
from app.util.auth import (
    create_access_token,
    decode_token,
    verify_apple_token,
    verify_google_token,
)
from config import Settings
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    @staticmethod
    async def login_google(
        user: UserLogin, db: AsyncSession, settings: Settings
    ) -> User:
        """
        google oauth 로그인 처리 -> 없을 경우 db에 저장
        """
        google_user_info = await verify_google_token(user.id_token, settings)
        google_id = google_user_info.get("sub")

        if not google_id:
            raise HTTPException(status_code=400, detail="Invalid Google ID Token")

        db_user = db.query(User).filter(User.oauth_id == google_id).first()
        if not db_user:
            db_user = User(
                user_name=user.username,
                oauth_provider=user.oauth_provider,
                oauth_id=user.oauth_id,
                email=user.email,
                profile_image=user.profile_image,
                is_premium=False,
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

        return db_user

    @staticmethod
    async def login_apple(
        user: UserLogin, db: AsyncSession, settings: Settings
    ) -> User:
        """
        Apple OAuth 로그인 처리 -> 없을 경우 db에 저장
        """
        apple_user_info = await verify_apple_token(user.id_token, settings)
        apple_id = apple_user_info.get("sub")

        if not apple_id:
            raise HTTPException(status_code=400, detail="Invalid Apple ID Token")

        db_user = db.query(User).filter(User.oauth_id == apple_id).first()
        if not db_user:
            db_user = User(
                username=user.username,
                oauth_provider=user.oauth_provider,
                oauth_id=apple_id,
                email=apple_user_info.get("email", ""),
                profile_image=user.profile_image,
                is_premium=False,
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)

        return db_user

    @staticmethod
    async def get_all_users(db: AsyncSession) -> List[User]:
        """
        모든 사용자 정보를 가져오는 메서드
        """
        users = db.query(User).all()

        return users

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

    @staticmethod
    async def update_name(user: UserUpdateName, user_id: int, db: AsyncSession) -> int:
        """
        user 이름 변경 후 id 반환
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=400, detail=f"User with id {user_id} not found"
            )

        db_user.username = user.username
        db.commit()
        db.refresh(db_user)

        return db_user.id

    @staticmethod
    async def update_profile_image(
        user: UserUpdateProfileImage, user_id: int, db: AsyncSession
    ) -> int:
        """
        user 프로필 사진 변경 후 id 반환
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=400, detail=f"User with id {user_id} not found"
            )

        db_user.profile_image = user.profile_image
        db.commit()
        db.refresh(db_user)

        return db_user.id
