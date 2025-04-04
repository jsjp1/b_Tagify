from typing import List

from app.models.content import Content, ContentTypeEnum
from app.models.content_tag import content_tag_association
from app.models.post_metadata import PostMetadata
from app.models.tag import Tag
from app.models.user import User
from app.models.video_metadata import VideoMetadata
from app.schemas.content import (ContentPost, ContentPostResponse,
                                 ContentPutRequest, UserBookmark, UserContents)
from app.services.post import PostService
from app.services.video import VideoService
from fastapi import HTTPException
from sqlalchemy import and_, desc, insert
from sqlalchemy.exc import IntegrityError
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
            .order_by(desc(Content.created_at))
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
    async def post_content(
        content_type: str, content: ContentPost, db: Session
    ) -> dict:
        """
        content 정보 db에 저장 (content, metadata, tag, content_tag)
        """
        db_user = db.query(User).filter(User.id == content.user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=400, detail=f"User with id {content.user_id} not found"
            )

        db_content = (
            db.query(Content)
            .filter(
                and_(Content.url == content.url, Content.user_id == content.user_id)
            )
            .first()
        )
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
        existing_tags = {
            tag.tagname: tag
            for tag in db.query(Tag).filter(Tag.tagname.in_(tag_list)).all()
        }

        new_tags = []
        for tagname in tag_list:
            if tagname not in existing_tags:
                new_tag = Tag(tagname=tagname, user_id=db_user.id)
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

        return {"id": new_content.id, "tags": [tag for tag in existing_tags.values()]}

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
            .filter(Content.user_id == user.user_id)
            .filter(Content.bookmark == True)
            .order_by(desc(Content.created_at))
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

        try:
            db.delete(content)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=500, detail="DB error while deleting content"
            )

        return

    @staticmethod
    async def put_content(
        user_id: int,
        content_id: int,
        content: ContentPutRequest,
        db: Session,
    ) -> List[dict]:
        """
        content_id에 해당하는 content 정보 수정 후 id 반환
        """
        db_content = db.query(Content).filter(and_(Content.id == content_id, Content.user_id == user_id)).first()

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
                db.delete(tag)
            else:
                return_tags.append({"id": tag.id, "tagname": tag.tagname})

        tags_to_add = new_tag_names - existing_tag_names
        for tag_name in tags_to_add:
            tag = db.query(Tag).filter(
                and_(Tag.tagname == tag_name, Tag.user_id == user_id)
            ).first()
            if not tag:
                tag = Tag(
                    user_id=db_content.user_id,
                    tagname=tag_name,
                )
                db.add(tag)
                db.flush()

            db_content.tags.append(tag)
            return_tags.append({"id": tag.id, "tagname": tag.tagname})

        db.commit()
        db.refresh(db_content)

        return return_tags

    @staticmethod
    async def get_search_contents(
        user_id: int, keyword: str, db: Session
    ) -> List[dict]:
        """
        keyword에 근접한 content 반환
        todo: 추후 변경?
        """
        pass
