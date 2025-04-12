from typing import List
from urllib.parse import urljoin, urlparse

import requests
from app.models.content import Content, ContentTypeEnum
from app.models.post_metadata import PostMetadata
from app.models.tag import Tag
from app.models.user import User
from app.schemas.content import ContentAnalyze, ContentAnalyzeResponse, UserContents
from bs4 import BeautifulSoup
from fastapi import HTTPException
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload


class PostService:
    @staticmethod
    def _extract_tag(body: str) -> List[str]:
        """
        텍스트 내용을 바탕으로 태그 list 추출 후 반환
        실제 구현은 자연어처리/키워드 추출 방식 사용 가능
        """
        # TODO: 텍스트 기반 태그 추출 로직 구현
        return []

    @staticmethod
    def _get_favicon(url: str, bs: BeautifulSoup) -> str:
        """
        HTML 파싱된 객체로부터 favicon 경로 추출
        """
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        icon_link = bs.find("link", rel=lambda r: r and "icon" in r) or bs.find(
            "link", rel="shortcut icon"
        )

        if icon_link:
            icon_href = icon_link.get("href", "")
            if icon_href.startswith("http"):
                return icon_href
            elif icon_href.startswith("/"):
                return urljoin(base_url, icon_href)
            else:
                return urljoin(base_url + "/", icon_href)
        else:
            return f"{base_url}/favicon.ico"

    @staticmethod
    def _analyze(url: str) -> dict:
        """
        주어진 URL에서 콘텐츠 관련 정보를 추출하여 딕셔너리로 반환
        """
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = "http://" + url

            response = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36",
                    "Accept-Language": "ko-KR,ko;q=0.9",
                },
                timeout=5,
                allow_redirects=True,
            )
            response.encoding = response.apparent_encoding
            html = response.text

            soup = BeautifulSoup(html, "html.parser")

            # 제목
            title_tag = soup.find("meta", property="og:title")
            title = (
                title_tag.get("content", "").strip()
                if title_tag
                else soup.title.string.strip() if soup.title else ""
            )

            # 썸네일 / 설명
            thumbnail_tag = soup.find("meta", property="og:image")
            description_tag = soup.find("meta", property="og:description")
            thumbnail = (
                thumbnail_tag.get("content", "").strip() if thumbnail_tag else ""
            )
            description = (
                description_tag.get("content", "").strip() if description_tag else ""
            )

            # 본문 텍스트 추출
            possible_selectors = [
                "article",
                "div.post-content",
                "div.notion-page-content",
                "div.tt_article_useless_p_margin",
                "div.se-main-container",
            ]
            body_element = next(
                (
                    soup.select_one(sel)
                    for sel in possible_selectors
                    if soup.select_one(sel)
                ),
                None,
            )
            body = body_element.get_text(separator="\n").strip() if body_element else ""

            tags = PostService._extract_tag(body)
            favicon = PostService._get_favicon(url, soup)

            return {
                "title": title,
                "thumbnail": thumbnail,
                "description": description,
                "favicon": favicon,
                "body": body,
                "tags": tags,
            }

        except Exception as e:
            return {
                "title": "",
                "thumbnail": "",
                "description": "",
                "favicon": "",
                "body": "",
                "tags": [],
                "error": str(e),
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
