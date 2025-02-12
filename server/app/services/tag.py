from typing import List

from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.models.user import User
from app.models.user_tag import user_tag_association
from app.schemas.tag import UserTags


class TagService:
    @staticmethod
    async def get_user_tags(user: UserTags, db: Session) -> List[Tag]:
        """
        유저가 가지고 있는 모든 태그 반환
        """
        db_user = db.query(User).filter(User.oauth_id == user.oauth_id).first()
        if not db_user:
            return []

        return db_user.tags
