from sqlite3 import IntegrityError
from typing import List

import jwt
from app.models.user import User
from app.schemas.content import ContentPost
from app.schemas.user import (
    CheckRefreshToken,
    TokenRefresh,
    UserDelete,
    UserLogin,
    UserUpdateName,
    UserUpdateProfileImage,
)
from app.services.content import ContentService
from app.services.post import PostService
from app.util.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_apple_token,
    verify_google_token,
)
from config import Settings
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    @staticmethod
    async def _insert_tutorial(db_user: User, db: AsyncSession, lang: str = "en"):
        """
        신규 가입자일 시 튜토리얼 컨텐츠 집어넣기
        """
        tutorial1_url = "https://jieeen.notion.site/How-to-use-Tagify-1c816dae3fdf80bab3e3dfc7fb6f387d?pvs=4"
        tutorial1_title = 'How to use "Tagify"? 🚀'
        tutorial1_description = "Check out how to use Tagify!"
        tutorial1_tags = ["Tutorial", "Tagify"]

        tutorial2_url = ""
        tutorial2_title = "Try tapping both the app logo and profile image at the top!"
        tutorial2_description = "Try tapping both the app logo and profile image at the top! What can you discover? Please delete this memo after reading it!"
        tutorial2_tags = ["Tutorial"]

        if lang == "ko":
            tutorial1_url = "https://jieeen.notion.site/Tagify-1c816dae3fdf809d8ad4fa66a417f1dd?pvs=4"
            tutorial1_title = "Tagify를 이용하는 방법 🚀"
            tutorial1_description = "Tagify를 이용하는 방법을 확인해보세요!"
            tutorial1_tags = ["튜토리얼", "Tagify"]

            tutorial2_title = "상단에 있는 앱 로고와 프로필 이미지를 모두 터치해보세요!"
            tutorial2_description = "상단에 있는 앱 로고와 프로필 이미지를 모두 터치해보세요! 어떤 것을 확인할 수 있을까요? 이 메모는 다 읽어보신 후 삭제해주시기 바랍니다!"
            tutorial2_tags = ["튜토리얼"]
        elif lang == "ja":
            tutorial1_url = "https://jieeen.notion.site/Tagify-1e416dae3fdf80d28f90f7b7a54a8f71?pvs=4"
            tutorial1_title = "Tagifyの使い方 🚀"
            tutorial1_description = "Tagifyの使い方をチェックしてみてください!"
            tutorial1_tags = ["チュートリアル", "Tagify"]

            tutorial2_title = (
                "上部のアプリアイコンとプロフィール画像をタップしてみてください！"
            )
            tutorial2_description = "上部のアプリアイコンとプロフィール画像をタップしてみてください！何が表示されるか確認してみましょう。読み終わったらこのメモを削除してください。"
            tutorial2_tags = ["チュートリアル"]

        analyzed_post = PostService._analyze(tutorial1_url)

        tutorial1 = ContentPost(
            user_id=db_user.id,
            bookmark=True,
            url=tutorial1_url,
            title=tutorial1_title,
            thumbnail=analyzed_post["thumbnail"],
            favicon=analyzed_post["favicon"],
            description=tutorial1_description,
            video_length=0,
            body="",
            tags=tutorial1_tags,
        )

        tutorial2 = ContentPost(
            user_id=db_user.id,
            bookmark=False,
            url=tutorial2_url,
            title=tutorial2_title,
            thumbnail="",
            favicon="",
            description=tutorial2_description,
            video_length=0,
            body="",
            tags=tutorial2_tags,
        )

        await ContentService.post_multiple_contents([tutorial1, tutorial2], "post", db)

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

        result = await db.execute(select(User).where(User.oauth_id == google_id))
        db_user = result.unique().scalars().first()

        if not db_user:
            db_user = User(
                username=user.username,
                oauth_provider=user.oauth_provider,
                oauth_id=user.oauth_id,
                email=user.email,
                profile_image=user.profile_image,
                is_premium=False,
            )
            db.add(db_user)
            await db.flush()
            await UserService._insert_tutorial(db_user, db, user.lang)

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

        result = await db.execute(select(User).where(User.oauth_id == apple_id))
        db_user = result.unique().scalars().first()

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
            await db.flush()
            await UserService._insert_tutorial(db_user, db, user.lang)

        return db_user

    @staticmethod
    async def delete_user(user: UserDelete, db: AsyncSession):
        """
        user_id에 해당하는 user 삭제
        """
        result = await db.execute(select(User).where(User.id == user.id))
        db_user = result.unique().scalars().first()
        if not db_user:
            raise HTTPException(
                status_code=404, detail=f"User with id {user.id} not found"
            )

        # TODO: user.reason에 해당하는 탈퇴 이유 및 피드백 저장하기

        try:
            await db.delete(db_user)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=500, detail="DB error while deleting comment"
            )

        return db_user.id

    @staticmethod
    async def get_all_users(db: AsyncSession) -> List[User]:
        """
        모든 사용자 정보를 가져오는 메서드
        """
        result = await db.execute(select(User))
        users = result.unique().scalars().all()

        return users

    @staticmethod
    async def token_refresh(token: TokenRefresh, settings: Settings) -> dict:
        """
        refresh 토큰 검증 후 access token 새로 발급
        """
        try:
            payload = decode_token(settings, token.refresh_token)

            if not payload:
                raise jwt.InvalidTokenError(
                    status_code=401, detail="Invalid refresh token"
                )

            # TODO: redis 같은 캐시 이용해 최신 refresh token인지 검증하는 로직 추가
            new_access_token = create_access_token(settings, data={"sub": f"{payload}"})
            new_refresh_token = create_refresh_token(
                settings, data={"sub": f"{payload}"}
            )

            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
            }

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token has expired")
        except jwt.InvalidSignatureError:
            raise HTTPException(status_code=401, detail="Invalid token signature")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    @staticmethod
    async def update_name(user: UserUpdateName, user_id: int, db: AsyncSession) -> int:
        """
        user 이름 변경 후 id 반환
        """
        result = await db.execute(select(User).where(User.id == user_id))
        db_user = result.unique().scalars().first()

        if not db_user:
            raise HTTPException(
                status_code=404, detail=f"User with id {user_id} not found"
            )

        db_user.username = user.username
        await db.commit()

        return db_user.id

    @staticmethod
    async def update_profile_image(
        user: UserUpdateProfileImage, user_id: int, db: AsyncSession
    ) -> int:
        """
        user 프로필 사진 변경 후 id 반환
        """
        result = await db.execute(select(User).where(User.id == user_id))
        db_user = result.unique().scalars().first()

        if not db_user:
            raise HTTPException(
                status_code=404, detail=f"User with id {user_id} not found"
            )

        db_user.profile_image = user.profile_image
        await db.commit()

        return db_user.id

    @staticmethod
    async def update_premium_status(user_id: int, db: AsyncSession) -> int:
        """
        user premium 상태 변경(일반 -> 프리미엄) 후 id 반환
        """
        result = await db.execute(select(User).where(User.id == user_id))
        db_user = result.unique().scalars().first()

        if not db_user:
            raise HTTPException(
                status_code=404, detail=f"User with id {user_id} not found"
            )

        db_user.is_premium = True
        await db.commit()

        return db_user.id

    @staticmethod
    async def check_refresh_token(token: CheckRefreshToken, settings: Settings) -> bool:
        """
        refresh token이 유효한지(만료기간, 등...) 확인 후 반환
        """
        refresh_token = token.refresh_token

        try:
            payload = decode_token(settings, refresh_token)
            if not payload:
                return False
            return True

        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
