from typing import List

from app.models.article_tag import article_tag_association
from app.models.content import Content
from app.models.content_tag import content_tag_association
from app.models.post_metadata import PostMetadata
from app.models.tag import Tag
from app.models.user import User
from app.models.video_metadata import VideoMetadata
from app.schemas.content import (
    ContentPost,
    ContentPutRequest,
    UserBookmark,
    UserContents,
)
from app.services.post import PostService
from app.services.video import VideoService
from fastapi import HTTPException
from sqlalchemy import and_, delete, desc, insert, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload


class ContentService:
    @staticmethod
    async def get_user_all_contents(
        user: UserContents, db: AsyncSession
    ) -> List[Content]:
        """
        유저가 소유한 모든 콘텐츠 정보를 반환
        """
        stmt = (
            select(Content)
            .where(Content.user_id == user.id)
            .options(
                joinedload(Content.tags),
                joinedload(Content.video_metadata),
                joinedload(Content.post_metadata),
            )
            .order_by(desc(Content.created_at))
        )
        result = await db.execute(stmt)
        return result.unique().scalars().all()

    @staticmethod
    async def get_user_all_sub_contents(
        user: UserContents, content_type: str, db: AsyncSession
    ) -> List[Content]:
        """
        유저가 소유한 모든 서브 콘텐츠(비디오, 포스트, ...) 정보를 반환
        """
        if content_type == "video":
            return await VideoService.get_user_all_videos(user, db)
        elif content_type == "post":
            return await PostService.get_user_all_posts(user, db)
        else:
            raise HTTPException(status_code=400, detail="Unsupported Content Type")

    @staticmethod
    async def post_content(
        content_type: str, content: ContentPost, db: AsyncSession
    ) -> dict:
        """
        content 정보 db에 저장 (content, metadata, tag, content_tag)
        """
        result = await db.execute(select(User).where(User.id == content.user_id))
        db_user = result.unique().scalars().first()
        if not db_user:
            raise HTTPException(
                status_code=400, detail=f"User with id {content.user_id} not found"
            )

        stmt = select(Content).where(
            and_(Content.url == content.url, Content.user_id == content.user_id)
        )
        result = await db.execute(stmt)
        db_content = result.unique().scalars().first()
        if db_content and content.url != "":
            raise HTTPException(status_code=400, detail="Content already exists")

        new_content = Content(
            user_id=content.user_id,
            url=content.url,
            title=content.title,
            description=content.description,
            bookmark=content.bookmark,
            thumbnail=content.thumbnail,
            favicon=content.favicon,
            content_type=content_type,
        )
        db.add(new_content)
        await db.flush()
        await db.refresh(new_content)

        if content_type == "video":
            video_metadata = VideoMetadata(
                video_length=content.video_length,
                content_id=new_content.id,
            )
            db.add(video_metadata)
        elif content_type == "post":
            post_metadata = PostMetadata(
                body=content.body,
                content_id=new_content.id,
            )
            db.add(post_metadata)
        else:
            raise HTTPException(status_code=404, detail="Unsupported content type")

        tag_list = content.tags
        result = await db.execute(select(Tag).where(Tag.tagname.in_(tag_list)))
        existing_tags = {tag.tagname: tag for tag in result.unique().scalars().all()}

        new_tags = []
        for tagname in tag_list:
            if tagname not in existing_tags:
                new_tag = Tag(tagname=tagname, user_id=db_user.id)
                db.add(new_tag)
                new_tags.append(new_tag)

        await db.flush()
        for tag in new_tags:
            existing_tags[tag.tagname] = tag

        await db.execute(
            insert(content_tag_association),
            [
                {"content_id": new_content.id, "tag_id": tag.id}
                for tag in existing_tags.values()
            ],
        )

        await db.commit()

        return {"id": new_content.id, "tags": [tag for tag in existing_tags.values()]}

    @staticmethod
    async def toggle_bookmark(content_id: int, db: AsyncSession):
        """
        콘텐츠 북마크 등록 <-> 해제 토글
        """
        result = await db.execute(
            select(Content).where(Content.id == content_id).with_for_update()
        )
        content = result.scalar_one_or_none()
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        content.bookmark = not content.bookmark
        await db.commit()

    @staticmethod
    async def get_bookmarked_contents(
        user: UserBookmark, db: AsyncSession
    ) -> List[Content]:
        """
        북마크로 저장돼있는 콘텐츠 반환
        """
        stmt = (
            select(Content)
            .where(and_(Content.user_id == user.user_id, Content.bookmark == True))
            .order_by(desc(Content.created_at))
        )
        result = await db.execute(stmt)
        return result.unique().scalars().all()

    @staticmethod
    async def delete_content(content_id: int, db: AsyncSession):
        """
        특정 콘텐츠 삭제
        """

        result = await db.execute(
            select(Content)
            .options(selectinload(Content.tags))
            .where(Content.id == content_id)
        )
        content = result.unique().scalar()
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        orphan_tags = []
        for tag in content.tags:
            result = await db.execute(
                select(content_tag_association)
                .where(content_tag_association.c.tag_id == tag.id)
                .where(content_tag_association.c.content_id != content_id)
            )
            other_content_tags = result.rowcount

            result = await db.execute(
                select(article_tag_association).where(
                    article_tag_association.c.tag_id == tag.id
                )
            )
            article_count = result.rowcount

            if other_content_tags == 0 and article_count == 0:
                orphan_tags.append(tag)

        for tag in orphan_tags:
            await db.delete(tag)

        try:
            await db.execute(
                delete(VideoMetadata).where(VideoMetadata.content_id == content_id)
            )
            await db.execute(
                delete(PostMetadata).where(PostMetadata.content_id == content_id)
            )

            await db.delete(content)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=500, detail="DB error while deleting content"
            )

    @staticmethod
    async def put_content(
        user_id: int,
        content_id: int,
        content: ContentPutRequest,
        db: AsyncSession,
    ) -> List[dict]:
        """
        content_id에 해당하는 content 정보 수정 후 id 반환
        """
        stmt = (
            select(Content)
            .options(selectinload(Content.tags).selectinload(Tag.contents))
            .where(and_(Content.id == content_id, Content.user_id == user_id))
        )
        result = await db.execute(stmt)
        db_content = result.unique().scalars().first()

        if not db_content:
            raise HTTPException(status_code=404, detail="Content not found")

        db_content.title = content.title
        db_content.description = content.description
        db_content.thumbnail = content.thumbnail
        db_content.bookmark = content.bookmark

        existing_tag_names = {tag.tagname for tag in db_content.tags}
        new_tag_names = set(content.tags)

        return_tags = []

        tags_to_remove = [
            tag for tag in db_content.tags if tag.tagname not in new_tag_names
        ]
        for tag in tags_to_remove:
            db_content.tags.remove(tag)
            if len(tag.contents) == 0:
                await db.delete(tag)
            else:
                return_tags.append({"id": tag.id, "tagname": tag.tagname})

        tags_to_add = new_tag_names - existing_tag_names
        for tag_name in tags_to_add:
            result = await db.execute(
                select(Tag).where(and_(Tag.tagname == tag_name, Tag.user_id == user_id))
            )
            tag = result.unique().scalars().first()
            if not tag:
                tag = Tag(user_id=db_content.user_id, tagname=tag_name)
                db.add(tag)
                await db.flush()

            db_content.tags.append(tag)
            return_tags.append({"id": tag.id, "tagname": tag.tagname})

        await db.commit()

        return return_tags

    @staticmethod
    async def get_search_contents(
        user_id: int, keyword: str, db: AsyncSession
    ) -> List[Content]:
        """
        keyword에 근접한 content 반환
        todo: 추후 변경?
        """
        keyword_pattern = f"%{keyword}%"

        stmt = (
            select(Content)
            .outerjoin(
                content_tag_association,
                Content.id == content_tag_association.c.content_id,
            )
            .outerjoin(Tag, content_tag_association.c.tag_id == Tag.id)
            .where(
                Content.user_id == user_id,
                or_(
                    Content.title.ilike(keyword_pattern),
                    Content.description.ilike(keyword_pattern),
                    Tag.tagname.ilike(keyword_pattern),
                ),
            )
            .distinct()
            .order_by(desc(Content.created_at))
        )

        result = await db.execute(stmt)
        return result.unique().scalars().all()
