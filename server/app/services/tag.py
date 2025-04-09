from typing import List

from app.models.content import Content
from app.models.content_tag import content_tag_association
from app.models.tag import Tag
from app.models.user import User
from app.schemas.tag import TagContents, TagDelete, TagPost, TagPut, UserTags
from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import exists


class TagService:
    @staticmethod
    async def get_user_tags(user: UserTags, db: AsyncSession) -> List[Tag]:
        """
        유저가 가지고 있는 모든 태그 반환
        """
        db_user = db.query(User).filter(User.id == user.user_id).first()
        if not db_user:
            return []

        user_tag_ids = [tag.id for tag in db_user.tags]

        ordered_tags = (
            db.query(Tag)
            .filter(Tag.id.in_(user_tag_ids))
            .join(content_tag_association, content_tag_association.c.tag_id == Tag.id)
            .order_by(desc(Tag.id))
            .distinct()
            .all()
        )

        return ordered_tags

    @staticmethod
    async def get_tag_all_contents(tag: TagContents, db: AsyncSession) -> List[Content]:
        """
        태그와 매치되는 모든 콘텐츠 반환
        """
        db_contents = (
            db.query(Content)
            .join(content_tag_association)
            .filter(content_tag_association.c.tag_id == tag.tag_id)
            .order_by(desc(Content.created_at))
            .all()
        )

        if not db_contents:
            return []

        return db_contents

    @staticmethod
    async def get_tag_videos(tag: TagContents, db: AsyncSession) -> List[Content]:
        """
        태그와 매치되는 video 반환
        """
        db_videos = (
            db.query(Content)
            .join(content_tag_association)
            .filter(Content.content_type == "VIDEO")
            .filter(content_tag_association.c.tag_id == tag.tag_id)
            .order_by(desc(Content.created_at))
            .all()
        )

        if not db_videos:
            return []

        return db_videos

    @staticmethod
    async def get_tag_posts(tag: TagContents, db: AsyncSession) -> List[Content]:
        """
        태그와 매치되는 post 반환
        """
        db_posts = (
            db.query(Content)
            .join(content_tag_association)
            .filter(Content.content_type == "POST")
            .filter(content_tag_association.c.tag_id == tag.tag_id)
            .order_by(desc(Content.created_at))
            .all()
        )

        if not db_posts:
            return []

        return db_posts

    @staticmethod
    async def post_tag(user_id: int, tag: TagPost, db: AsyncSession) -> Tag:
        """
        특정 사용자가 동일한 태그를 생성했는지 검사 후, 태그 생성 및 ID 반환
        """
        tag_exists = db.query(
            exists().where(Tag.tagname == tag.tagname, Tag.user_id == user_id)
        ).scalar()

        if tag_exists:
            raise HTTPException(
                status_code=400,
                detail=f"Tag name '{tag.tagname}' already exists for this user",
            )

        new_tag = Tag(
            tagname=tag.tagname,
            user_id=user_id,
        )

        try:
            db.add(new_tag)
            db.commit()
            db.refresh(new_tag)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=500, detail="DB error while creating tag")

        return new_tag

    @staticmethod
    async def update_tag(user_id: int, tag_id: int, tag: TagPut, db: AsyncSession) -> int:
        """
        태그 정보(이름, 색상) 수정 후 id 반환
        """
        db_tag = db.query(Tag).filter(Tag.id == tag_id, Tag.user_id == user_id).first()
        if not db_tag:
            raise HTTPException(
                status_code=404,
                detail=f"Tag name '{tag.tagname}' does not exist for user id '{user_id}'",
            )

        if tag.tagname:
            db_tag.tagname = tag.tagname
        if tag.color is not None:
            db_tag.color = tag.color

        db.commit()
        db.refresh(db_tag)

        return db_tag.id

    @staticmethod
    async def delete_tag(user_id: int, tag: TagDelete, db: AsyncSession) -> int:
        """
        콘텐츠 없는 빈 태그 삭제, 연관된 콘텐츠가 하나라도 있을시 예외 반환
        """
        db_tag = (
            db.query(Tag)
            .filter(Tag.tagname == tag.tagname, Tag.user_id == user_id)
            .first()
        )

        if not db_tag:
            raise HTTPException(
                status_code=400,
                detail=f"Tag name '{tag.tagname}' does not exist for user id '{user_id}'",
            )

        related_content_exists = db.query(
            exists().where(content_tag_association.c.tag_id == db_tag.id)
        ).scalar()

        if related_content_exists:
            raise HTTPException(
                status_code=400,
                detail=f"Tag '{tag.tagname}' has associated content and cannot be deleted",
            )

        try:
            db.delete(db_tag)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=500, detail="DB error while deleting tag")

        return db_tag.id
