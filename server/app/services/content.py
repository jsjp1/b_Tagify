from http.client import HTTPException
from typing import List
from sqlalchemy.orm import joinedload, Session

from app.schemas.content import UserContents
from app.models.content import Content, ContentTypeEnum
from app.services.video import VideoService
from app.services.post import PostService


class ContentService:
    @staticmethod
    async def get_user_all_contents(user: UserContents, db: Session) -> List[Content]:
        """
        유저가 소유한 모든 콘텐츠 정보를 반환
        """
        contents = (
            db.query(Content)
            .filter(Content.user.has(oauth_id=user.oauth_id))
            .options(
                joinedload(Content.tags),
                joinedload(Content.video_metadata),
                joinedload(Content.post_metadata),
            )
            .all()
        )

        return contents
    
    @staticmethod
    async def get_user_all_sub_contents(user: UserContents, content_type: str, db: Session) -> List[Content]:
        """
        유저가 소유한 모든 서브 콘텐츠(비디오, 포스트, ...) 정보를 반환
        """
        if content_type == "video":
            return await VideoService.get_user_all_videos(user, db)
        elif content_type == "post":
            return await PostService.get_user_all_posts(user, db)
        else:
            raise HTTPException(status_code=400, detail="Unsupported Content Type")
    