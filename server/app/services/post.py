from typing import List
from urllib.parse import urljoin, urlparse

import requests
from app.models.content import Content, ContentTypeEnum
from app.models.post_metadata import PostMetadata
from app.models.tag import Tag
from app.models.user import User
from app.schemas.content import (ContentAnalyze, ContentAnalyzeResponse,
                                 UserContents)
from bs4 import BeautifulSoup
from fastapi import HTTPException
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload


class PostService:
    @staticmethod
    def _extract_tag(body: str) -> List[str]:  # TODO: async? llama
        """
        텍스트 내용을 바탕으로 태그 list 추출 후 반환
        """
        return []

    @staticmethod
    def _get_favicon(url: str, bs: BeautifulSoup) -> str:
        """
        url로부터 favicon 추출 후 반환
        """
        domain = urlparse(url).netloc
        scheme = urlparse(url).scheme

        icon_link = bs.find("link", rel="shortcut icon")
        if icon_link is None:
            icon_link = bs.find("link", rel="icon")
        if icon_link is None:
            return f"{scheme}://{domain}/favicon.ico"

        icon_href = icon_link.get("href")

        if icon_href.startswith("http"):
            return icon_href
        elif icon_href.startswith("/"):
            return urljoin(f"{scheme}://{domain}", icon_href)
        else:
            # TODO: 기타 예외 처리
            return ""

    @staticmethod
    def _analyze(url: str) -> dict:
        """
        db에 저장할 Content 데이터 추출 후 반환
        """
        if not url.endswith("/"):
            url = url + "/"

        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36",
                "Accept-Language": "ko-KR,ko;q=0.9",
            },
            timeout=3,
            allow_redirects=True,
        )

        response.encoding = (
            response.apparent_encoding
        )  # 특정 사이트 글자 깨져서 나오는 문제 해결
        html = response.text

        bs = BeautifulSoup(html, "html.parser")

        title_tag = bs.find("title")
        og_title_tag = bs.find("meta", property="og:title")
        title = ""
        if og_title_tag:
            title = og_title_tag.get("content", "").strip()
        elif title_tag and title_tag.text:
            title = title_tag.text.strip()

        thumbnail_tag = bs.find("meta", property="og:image")
        description_tag = bs.find("meta", property="og:description")
        thumbnail = thumbnail_tag.get("content", "") if thumbnail_tag else ""
        description = description_tag.get("content", "") if description_tag else ""

        possible_selectors = [
            "article",
            "div.post-content",
            "div.notion-page-content",
            "div.tt_article_useless_p_margin",
            "div.se-main-container",
        ]
        body_element = None
        for selector in possible_selectors:
            body_element = bs.select_one(selector)
            if body_element:
                break
        body = body_element.get_text(separator="\n").strip() if body_element else ""

        tags = PostService._extract_tag(body)
        favicon = PostService._get_favicon(url, bs)

        return {
            "title": title,
            "thumbnail": thumbnail,
            "description": description,
            "favicon": favicon,
            "body": body,
            "tags": tags,
        }

    @staticmethod
    async def analyze_post(
        content_type: str, content: ContentAnalyze, db: AsyncSession
    ) -> ContentAnalyzeResponse:
        """
        post 정보 추출 후 반환
        """
        stmt = select(Content).where(
            and_(Content.url == content.url, Content.user_id == content.user_id)
        )
        result = await db.execute(stmt)
        db_content = result.scalar_one_or_none()

        if db_content:
            raise HTTPException(status_code=400, detail="Content already exists")

        post_info = PostService._analyze(content.url)

        content = ContentAnalyzeResponse(
            url=content.url,
            title=post_info["title"],
            thumbnail=post_info["thumbnail"],
            favicon=post_info["favicon"],
            description=post_info["description"],
            body=post_info["body"],
            tags=post_info["tags"],
        )

        return content

    @staticmethod
    async def get_user_all_posts(user: UserContents, db: AsyncSession) -> List[Content]:
        """
        유저가 소유한 포스트 정보를 모두 반환
        """
        stmt = (
            select(Content)
            .join(User)
            .where(User.id == user.id)
            .where(Content.content_type == ContentTypeEnum.POST)
            .options(
                selectinload(Content.tags),
                joinedload(Content.post_metadata),
            )
            .order_by(desc(Content.id))
        )

        result = await db.execute(stmt)
        contents = result.scalars().all()
        return contents
