from typing import List
from urllib.parse import parse_qs, urlparse

import isodate
from app.models.content import Content, ContentTypeEnum
from app.models.tag import Tag
from app.models.user import User
from app.models.video_metadata import VideoMetadata
from app.schemas.content import (ContentAnalyze, ContentAnalyzeResponse,
                                 UserContents)
from config import Settings
from fastapi import HTTPException
from googleapiclient.discovery import build
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class VideoService:
    @staticmethod
    def _extract_video_id(video_url: str) -> str:
        """
        YouTube URL에서 영상 ID 추출
        """
        parsed_url = urlparse(video_url)

        if parsed_url.hostname in ["www.youtube.com", "youtube.com", "music.youtube.com"]:
            if "shorts" in parsed_url.path:
                return parsed_url.path.split("/")[-1].split("?")[0]
            return parse_qs(parsed_url.query).get("v", [""])[0]

        elif parsed_url.hostname in ["youtu.be"]:
            return parsed_url.path.lstrip("/")

        return ""

    @staticmethod
    def _convert_duration_to_seconds(duration: str) -> int:
        """
        ISO 8601 형식의 동영상 길이를 초 단위로 변환
        """
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

        if len(response["items"]) == 0:
            raise HTTPException(status_code=404, detail="Video not found on YouTube")

        if not response["items"]:
            return {
                "title": "",
                "thumbnail": "",
                "favicon": "https://www.youtube.com/favicon.ico",
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
            "favicon": "https://www.youtube.com/favicon.ico",
            "description": snippet.get("description", ""),
            "tags": snippet.get("tags", []),
            "length": VideoService._convert_duration_to_seconds(
                content_details.get("duration", "")
            ),
            "summation": "",
        }

        return video_info

    @staticmethod
    async def analyze_video(
        content: ContentAnalyze, db: AsyncSession, settings: Settings
    ) -> ContentAnalyzeResponse:
        """
        video 정보 추출 후 반환
        """
        result = await db.execute(
            select(Content).where(
                and_(Content.url == content.url, Content.user_id == content.user_id)
            )
        )
        db_content = result.unique().scalars().first()

        if db_content:
            raise HTTPException(status_code=400, detail="Content already exists")

        video_info = VideoService._extract_video_info(content.url, settings)

        content = ContentAnalyzeResponse(
            url=content.url,
            title=video_info["title"],
            thumbnail=video_info["thumbnail"],
            favicon=video_info["favicon"],
            description=video_info["description"],
            video_length=video_info["length"],
            tags=video_info["tags"],
        )

        return content

    @staticmethod
    async def get_user_all_videos(
        user: UserContents, db: AsyncSession
    ) -> List[Content]:
        """
        유저가 소유한 비디오 정보를 모두 반환
        """
        stmt = (
            select(Content)
            .options(
                joinedload(Content.tags),
                joinedload(Content.video_metadata),
            )
            .where(
                Content.user_id == user.id,
                Content.content_type == ContentTypeEnum.VIDEO,
            )
            .order_by(desc(Content.created_at))
        )
        result = await db.execute(stmt)
        contents = result.unique().scalars().all()

        return contents