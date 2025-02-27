from typing import List

from app.models.content import Content
from app.models.content_tag import content_tag_association
from app.models.tag import Tag
from app.models.user import User
from app.schemas.tag import TagContents, TagPost, UserTags
from sqlalchemy import desc
from sqlalchemy.orm import Session


class TagService:
    @staticmethod
    async def get_user_tags(user: UserTags, db: Session) -> List[Tag]:
        """
        유저가 가지고 있는 모든 태그 반환
        """
        db_user = db.query(User).filter(User.id == user.user_id).first()
        if not db_user:
            return []

        ordered_tags = (
            db.query(Tag)
            .filter(Tag.id.in_([tag.id for tag in db_user.tags]))
            .order_by(desc(Tag.id))
            .all()
        )

        # return db_user.tags?
        return ordered_tags

    @staticmethod
    async def get_tag_videos(tag: TagContents, db: Session) -> List[Content]:
        """
        태그와 매치되는 video 반환
        """
        db_videos = (
            db.query(Content)
            .join(content_tag_association)
            .filter(content_tag_association.c.tag_id == tag.tag_id)
            .order_by(desc(Content.id))
            .all()
        )

        if not db_videos:
            return []

        return db_videos

    @staticmethod
    async def get_tag_posts(tag: TagContents, db: Session) -> List[Content]:
        """
        태그와 매치되는 post 반환
        """
        pass

    @staticmethod
    async def post_tag(user_id: int, tag: TagPost, db: Session) -> int:
        """
        콘텐츠 없는 빈 태그 생성 후 tag id 반환
        """
        db_post = db.query(Tag).filter(Tag.tagname == tag.tagname).first()
        if db_post:
            raise HTTPException(
                status_code=400, detail=f"Tag name {tag.tagname} already exists"
            )

        new_tag = Tag(
            tagname=tag.tagname,
            user_id=user_id,
        )

        db.add(new_tag)
        db.commit()

        return new_tag.id
