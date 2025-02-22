from typing import List

import requests
from app.models.content import Content, ContentTypeEnum
from app.models.content_tag import content_tag_association
from app.models.post_metadata import PostMetadata
from app.models.tag import Tag
from app.models.user import User
from app.schemas.content import (ContentAnalyze, ContentAnalyzeResponse,
                                 UserContents)
from bs4 import BeautifulSoup
from config import Settings
from sqlalchemy import desc, insert
from sqlalchemy.orm import Session, joinedload


class PostService:
    @staticmethod
    def _extract_tag(body: str) -> List[str]: # TODO: async? llama
        """
        텍스트 내용을 바탕으로 태그 list 추출 후 반환
        """
        return []


    @staticmethod
    def _analyze(url: str) -> dict:
        """
        db에 저장할 Content 데이터 추출 후 반환
        """
        response = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        })
        html = response.text

        bs = BeautifulSoup(html, "html.parser")

        title = bs.find("title")
        thumbnail = bs.find("meta", property="og:image")
        description = bs.find("meta", property="og:description")
            
        possible_selectors = [
            "article",  # 일반적인 블로그 글
            "div.post-content",  # Velog, Tistory 일부
            "div.notion-page-content",  # Notion
            "div.tt_article_useless_p_margin",  # Tistory
            "div.se-main-container",  # Naver Blog
        ]
        body = None
        for selector in possible_selectors:
            body = bs.select_one(selector)
            if body:
                break

        tags = PostService._extract_tag(body if body else "")

        return {
            "title": title.text if title is not None else "",
            "thumbnail": thumbnail.get("content"),
            "description": description.get("content"), 
            "body": body.text if body is not None else "",
            "tags": tags,
        }


    @staticmethod
    async def analyze_post(
        content_type: str, content: ContentAnalyze, db: Session
    ) -> ContentAnalyzeResponse:
        """
        post 정보 추출 후 반환
        """
        db_content = db.query(Content).filter(
            Content.url == content.url).first()
        if db_content:
            raise HTTPException(status_code=400, detail="Content already exists")

        post_info = PostService._analyze(content.url)
        
        content = ContentAnalyzeResponse(
            url=content.url,
            title=post_info["title"],
            thumbnail=post_info["thumbnail"],
            description=post_info["description"],
            body=post_info["body"],
            tags=post_info["tags"],
        )

        return content


    @staticmethod
    async def get_user_all_posts(user: UserContents, db: Session) -> List[Content]:
        """
        유저가 소유한 포스트 정보를 모두 반환
        """
        contents = (
            db.query(Content)
            .filter(Content.user.has(oauth_id=user.oauth_id))
            .filter(Content.content_type == ContentTypeEnum.POST)
            .options(
                joinedload(Content.tags),
                joinedload(Content.post_metadata),
            )
            .order_by(desc(Content.updated_at)) 
            .all()
        )
        
        return contents