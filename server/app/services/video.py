from http.client import HTTPException
from typing import List

import isodate
from googleapiclient.discovery import build
from requests import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.models.content import Content
from app.models.tag import Tag
from app.models.user import User
from app.models.content_tag import content_tag_association
from app.models.user_tag import user_tag_association
from app.models.video_metadata import VideoMetadata
from config import Settings
from app.schemas.content import (ContentAnalyze, ContentAnalyzeResponse, UserContents)


class VideoService:
    @staticmethod
    def _extract_video_id(video_url: str) -> str:
        """YouTube URL에서 영상 ID 추출"""
        from urllib.parse import parse_qs, urlparse

        parsed_url = urlparse(video_url)
        if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
            return parse_qs(parsed_url.query).get("v", [""])[0]
        elif parsed_url.hostname in ["youtu.be"]:
            return parsed_url.path.lstrip("/")
        return ""

    @staticmethod
    def _convert_duration_to_seconds(duration: str) -> int:
        """ISO 8601 형식의 동영상 길이를 초 단위로 변환"""
        try:
            return int(isodate.parse_duration(duration).total_seconds())
        except:
            return 0

    @staticmethod
    def _extract_video_info(
        video_url: str, settings: Settings, lang: str = "ko"
    ) -> dict:
        """
        유튜브 비디오 링크 -> 자막 반환
        """
        video_id = VideoService._extract_video_id(video_url)
        youtube = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)

        request = youtube.videos().list(part="snippet,contentDetails", id=video_id)
        response = request.execute()

        if not response["items"]:
            return {
                "title": "",
                "thumbnail": "",
                "description": "",
                "tags": [],
                "length": 0,  # 초 단위
                "summation": "",
            }

        video_data = response["items"][0]
        snippet = video_data["snippet"]
        content_details = video_data["contentDetails"]

        video_info = {
            "title": snippet.get("title", ""),
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "description": snippet.get("description", ""),
            "tags": snippet.get("tags", []),
            "length": VideoService._convert_duration_to_seconds(
                content_details.get("duration", "")
            ),
            "summation": "",  # TODO: caption 관련 처리
        }

        return video_info

    @staticmethod
    async def analyze_video(
        content_type: str, content: ContentAnalyze, db: Session, settings: Settings
    ) -> ContentAnalyzeResponse:
        """
        유저 oauth id + 콘텐츠 링크 + ... -> tag_count 만큼의 태그 리스트 생성, db 저장 후 content_id 반환
        """
        db_user = db.query(User).filter(User.oauth_id == content.oauth_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        db_content = db.query(Content).filter(Content.url == content.url).first()
        content_info = VideoService._extract_video_info(content.url, settings)

        if not db_content:
            db_content = Content(
                url=content.url,
                title=content_info["title"],
                thumbnail=content_info["thumbnail"],
                content_type=content_type,
                user_id=db_user.id,
            )

            db.add(db_content)
            db.commit()
            db.refresh(db_content)
            
            video_metadata = VideoMetadata(
                content_id=db_content.id,
                video_length=content_info.get("length", "0"),
            )
            
            db.add(video_metadata)
            db.commit()
            
        tag_list = content_info.get("tags", [])[: content.tag_count]
        content_tags = []
        user_tags = []

        for tag_name in tag_list:
            db_tag = db.query(Tag).filter(Tag.tagname == tag_name).first()

            if not db_tag:
                db_tag = Tag(tagname=tag_name)
                db.add(db_tag)
                try:
                    db.commit()
                except IntegrityError:
                    db.rollback()
                    db_tag = db.query(Tag).filter(Tag.tagname == tag_name).first()

            content_tags.append(content_tag_association(content_id=db_content.id, tag_id=db_tag.id))
            user_tags.append(user_tag_association(user_id=db_user.id, tag_id=db_tag.id))

        if content_tags:
            db.add_all(content_tags)
        if user_tags:
            db.add_all(user_tags)
        db.commit()

        return ContentAnalyzeResponse(content_id=db_content.id)

    @staticmethod
    async def get_user_videos(user: UserContents, db: Session) -> List[Content]:
        """
        유저가 소유한 비디오 정보를 모두 반환
        """
        contents = (
            db.query(Content, User)
            .join(User, Content.user_id == User.id)
            .all()
        )

        return contents
