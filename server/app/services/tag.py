from typing import List

from app.models.content import Content, ContentTypeEnum
from app.models.content_tag import content_tag_association
from app.models.post_metadata import PostMetadata
from app.models.tag import Tag
from app.models.video_metadata import VideoMetadata
from app.schemas.tag import TagContents, TagDelete, TagPost, TagPut, UserTags
from fastapi import HTTPException
from sqlalchemy import and_, desc, exists, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload


class TagService:
    @staticmethod
    async def get_user_tags(user: UserTags, db: AsyncSession) -> List[Tag]:
        """
        유저가 가지고 있는 모든 태그 반환
        """
        result = await db.execute(
            select(Tag.id, Tag.tagname, Tag.color)
            .where(Tag.user_id == user.user_id)
            .order_by(desc(Tag.id))
        )
        return result.mappings().all()

    @staticmethod
    async def get_tag_all_contents(tag: TagContents, db: AsyncSession) -> List[Content]:
        """
        태그와 매치되는 모든 콘텐츠 반환
        """
        stmt = (
            select(Content)
            .join(content_tag_association, content_tag_association.c.content_id == Content.id)
            .options(
                selectinload(Content.tags),
                joinedload(Content.video_metadata),
                joinedload(Content.post_metadata),
            )
            .where(content_tag_association.c.tag_id == tag.tag_id)
            .order_by(desc(Content.created_at))
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_tag_videos(tag: TagContents, db: AsyncSession) -> List[dict]:
        """
        VIDEO 콘텐츠 + tagname 리스트를 같이 조회
        """
        stmt = (
            select(Content)
            .join(content_tag_association, Content.id == content_tag_association.c.content_id)
            .options(
                selectinload(Content.tags),
                joinedload(Content.video_metadata),
                joinedload(Content.post_metadata),
            )
            .where(
                and_(
                    content_tag_association.c.tag_id == tag.tag_id,
                    Content.content_type == ContentTypeEnum.VIDEO,
                )
            )
            .order_by(desc(Content.created_at))
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_tag_posts(tag: TagContents, db: AsyncSession) -> List[Content]:
        """
        태그와 매치되는 post 반환
        """
        stmt = (
            select(Content)
            .join(content_tag_association, Content.id == content_tag_association.c.content_id)
            .options(
                selectinload(Content.tags),
                joinedload(Content.video_metadata),
                joinedload(Content.post_metadata),
            )
            .where(
                and_(
                    content_tag_association.c.tag_id == tag.tag_id,
                    Content.content_type == ContentTypeEnum.POST,
                )
            )
            .order_by(desc(Content.created_at))
        )

        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def post_tag(user_id: int, tag: TagPost, db: AsyncSession) -> Tag:
        """
        특정 사용자가 동일한 태그를 생성했는지 검사 후, 태그 생성 및 ID 반환
        """
        result = await db.execute(
            select(
                exists().where(and_(Tag.tagname == tag.tagname, Tag.user_id == user_id))
            )
        )
        tag_exists = result.scalar()

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
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=500, detail="DB error while creating tag")

        return new_tag

    @staticmethod
    async def update_tag(
        user_id: int, tag_id: int, tag: TagPut, db: AsyncSession
    ) -> int:
        """
        태그 정보(이름, 색상) 수정 후 id 반환
        """
        result = await db.execute(
            select(Tag).where(and_(Tag.id == tag_id, Tag.user_id == user_id))
        )
        db_tag = result.unique().scalars().first()

        if not db_tag:
            raise HTTPException(
                status_code=404,
                detail=f"Tag name '{tag.tagname}' does not exist for user id '{user_id}'",
            )

        if tag.tagname:
            db_tag.tagname = tag.tagname
        if tag.color is not None:
            db_tag.color = tag.color

        await db.commit()

        return db_tag.id

    @staticmethod
    async def delete_tag(user_id: int, tag: TagDelete, db: AsyncSession) -> int:
        """
        콘텐츠 없는 빈 태그 삭제, 연관된 콘텐츠가 하나라도 있을시 예외 반환
        """
        result = await db.execute(
            select(Tag).where(and_(Tag.tagname == tag.tagname, Tag.user_id == user_id))
        )
        db_tag = result.scalar_one_or_none()

        if not db_tag:
            raise HTTPException(
                status_code=400,
                detail=f"Tag name '{tag.tagname}' does not exist for user id '{user_id}'",
            )

        result = await db.execute(
            select(exists().where(content_tag_association.c.tag_id == db_tag.id))
        )
        related_content_exists = result.scalar()

        if related_content_exists:
            raise HTTPException(
                status_code=400,
                detail=f"Tag '{tag.tagname}' has associated content and cannot be deleted",
            )

        try:
            await db.delete(db_tag)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=500, detail="DB error while deleting tag")

        return db_tag.id
