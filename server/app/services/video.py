from http.client import HTTPException
from typing import List

import isodate
from app.models.content import Content, ContentTypeEnum
from app.models.content_tag import content_tag_association
from app.models.tag import Tag
from app.models.user import User
from app.models.video_metadata import VideoMetadata
from app.schemas.content import (ContentAnalyze, ContentAnalyzeResponse,
                                 UserContents)
from config import Settings
from googleapiclient.discovery import build
from sqlalchemy import desc, insert
from sqlalchemy.orm import Session, joinedload


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
            "tags": snippet.get("tags", []),  # TODO: tags 처리 -> llm api
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
        db_user = db.query(User).filter(
            User.id == content.user_id).first()
        if not db_user:
            raise ValueError(f"User with id {content.user_id} not found")

        db_content = db.query(Content).filter(
            Content.url == content.url).first()
        video_info = VideoService._extract_video_info(content.url, settings)

        if not db_content:
            db_content = Content(
                user_id=db_user.id,
                url=content.url,
                title=video_info["title"],
                thumbnail=video_info["thumbnail"],
                description=video_info["description"],
                content_type=content_type,
            )
            db.add(db_content)
            db.flush()
            db.refresh(db_content)

            video_metadata = VideoMetadata(
                content_id=db_content.id,
                video_length=video_info.get("length", "0"),
            )
            db.add(video_metadata)

        tag_list = video_info.get("tags", [])[: content.tag_count]
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
                {"content_id": db_content.id, "tag_id": tag.id}
                for tag in existing_tags.values()
            ],
        )

        db.commit()

        return ContentAnalyzeResponse(content_id=db_content.id)

    @staticmethod
    async def get_user_all_videos(user: UserContents, db: Session) -> List[Content]:
        """
        유저가 소유한 비디오 정보를 모두 반환
        """
        contents = (
            db.query(Content)
            .filter(Content.user.has(id=user.id))
            .filter(Content.content_type == ContentTypeEnum.VIDEO)
            .options(
                joinedload(Content.tags),
                joinedload(Content.video_metadata),
            )
            .order_by(desc(Content.created_at)) 
            .all()
        )

        return contents
