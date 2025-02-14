from typing import List

from sqlalchemy.orm import joinedload, Session
from app.models.content import Content, ContentTypeEnum
from app.schemas.content import UserContents


class PostService:
    @staticmethod
    async def get_user_all_posts(user: UserContents, db: Session) -> List[Content]:
        """
        유저가 소유한 포스트 정보를 모두 반환
        """
        contents = (
            db.query(Content)
            .filter(Content.user.has(oauth_id=user.oauth_id))
            .filter(Content.content_type == ContentTypeEnum.POST)
            .options(
                joinedload(Content.tags),
                joinedload(Content.post_metadata),
            )
            .all()
        )
        
        return contents