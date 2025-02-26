from typing import List

from app.models.content import Content, ContentTypeEnum
from app.models.content_tag import content_tag_association
from app.models.post_metadata import PostMetadata
from app.models.tag import Tag
from app.models.user import User
from app.models.video_metadata import VideoMetadata
from app.schemas.content import (
    ContentPost,
    ContentPostResponse,
    UserBookmark,
    UserContents,
)
from app.services.post import PostService
from app.services.video import VideoService
from fastapi import HTTPException
from sqlalchemy import desc, insert
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func


class ContentService:
    @staticmethod
    async def get_user_all_contents(user: UserContents, db: Session) -> List[Content]:
        """
        유저가 소유한 모든 콘텐츠 정보를 반환
        """
        contents = (
            db.query(Content)
            .filter(Content.user.has(id=user.id))
            .options(
                joinedload(Content.tags),
                joinedload(Content.video_metadata),
                joinedload(Content.post_metadata),
            )
            .order_by(desc(Content.id))
            .all()
        )

        return contents

    @staticmethod
    async def get_user_all_sub_contents(
        user: UserContents, content_type: str, db: Session
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
    async def post_content(content_type: str, content: ContentPost, db: Session) -> int:
        """
        content 정보 db에 저장 (content, metadata, tag, content_tag)
        """
        db_user = db.query(User).filter(User.id == content.user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=404, detail=f"User with id {content.user_id} not found"
            )

        db_content = db.query(Content).filter(Content.url == content.url).first()
        if db_content:
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
        db.flush()
        db.refresh(new_content)

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
        if len(tag_list) == 0:
            tag_list.append("None")

        existing_tags = {
            tag.tagname: tag
            for tag in db.query(Tag).filter(Tag.tagname.in_(tag_list)).all()
        }

        new_tags = []
        for tag_name in tag_list:
            if tag_name not in existing_tags:
                new_tag = Tag(tagname=tag_name, user_id=db_user.id)
                db.add(new_tag)
                new_tags.append(new_tag)

        db.flush()
        existing_tags.update({tag.tagname: tag for tag in new_tags})

        db.execute(
            insert(content_tag_association),
            [
                {"content_id": new_content.id, "tag_id": tag.id}
                for tag in existing_tags.values()
            ],
        )

        db.commit()

        return new_content.id

    @staticmethod
    async def toggle_bookmark(content_id: int, db: Session):
        """
        콘텐츠 북마크 등록 <-> 해제 토글
        """
        content = (
            db.query(Content).with_for_update().filter(Content.id == content_id).first()
        )
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        content.bookmark = not content.bookmark
        db.commit()

        return

    @staticmethod
    async def get_bookmarked_contents(user: UserBookmark, db: Session) -> List[Content]:
        """
        북마크로 저장돼있는 콘텐츠 반환
        """
        contents = (
            db.query(Content)
            .filter(Content.bookmark == True)
            .order_by(desc(Content.id))
            .all()
        )

        return contents

    @staticmethod
    async def delete_content(content_id: int, db: Session):
        """
        특정 콘텐츠 삭제
        """

        content = db.query(Content).filter(Content.id == content_id).first()
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        # 해당 콘텐츠와 관계된, 다른 콘텐츠와는 관계되지 않은 모든 태그 삭제
        orphan_tags = []
        for tag in content.tags:
            other_content_tags = (
                db.query(content_tag_association)
                .filter(content_tag_association.c.tag_id == tag.id)
                .filter(content_tag_association.c.content_id != content_id)
                .count()
            )
            if other_content_tags == 0:
                orphan_tags.append(tag)

        for tag in orphan_tags:
            db.delete(tag)

        video_metadata = (
            db.query(VideoMetadata)
            .filter(VideoMetadata.content_id == content_id)
            .delete()
        )
        post_metadata = (
            db.query(PostMetadata)
            .filter(PostMetadata.content_id == content_id)
            .delete()
        )

        db.delete(content)
        db.commit()

        return
