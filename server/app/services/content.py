from http.client import HTTPException
from typing import List

from app.models.content import Content, ContentTypeEnum
from app.schemas.content import UserBookmark, UserContents
from app.services.post import PostService
from app.services.video import VideoService
from sqlalchemy.orm import Session, joinedload


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
    
    
    @staticmethod
    async def toggle_bookmark(content_id: str, db: Session):
        """
        콘텐츠 북마크 등록 <-> 해제 토글
        """
        content = db.query(Content).with_for_update().filter(Content.id == content_id).first()
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
            .all()
        )
        
        return contents