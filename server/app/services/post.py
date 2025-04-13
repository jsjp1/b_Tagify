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

        icon_links = bs.find_all("link", rel=lambda r: r and "icon" in r.lower())

        for icon_link in icon_links:
            icon_href = icon_link.get("href", "")
            if icon_href:
                if icon_href.startswith("http"):
                    return icon_href
                elif icon_href.startswith("/"):
                    return urljoin(base_url, icon_href)
                else:
                    return urljoin(base_url + "/", icon_href)

        return f"{base_url}/favicon.ico"

    @staticmethod
    def follow_redirects_until_valid(url: str, max_redirects: int = 5) -> str:
        """
        수동 리디렉션을 따라가며 최종 유효한 URL 반환
        intent:// 등 requests가 지원하지 않는 스킴을 피함
        """
        for _ in range(max_redirects):
            response = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36",
                    "Accept-Language": "ko-KR,ko;q=0.9",
                },
                timeout=1,
                allow_redirects=False,
            )
            if 300 <= response.status_code < 400:
                next_url = response.headers.get("Location", "")
                if next_url.startswith("intent://"):
                    parsed = urlparse(next_url)
                    query = parsed.fragment
                    fallback_key = "S.browser_fallback_url="
                    if fallback_key in query:
                        from urllib.parse import unquote

                        fallback_url = unquote(
                            query.split(fallback_key)[-1].split(";")[0]
                        )
                        return fallback_url
                    raise Exception("No fallback URL in intent scheme")
                elif next_url.startswith("http"):
                    url = next_url
                else:
                    url = urljoin(url, next_url)
            else:
                break
        return url

    @staticmethod
    def _analyze(url: str) -> dict:
        """
        주어진 URL에서 콘텐츠 관련 정보를 추출하여 딕셔너리로 반환
        """
        final_url = PostService.follow_redirects_until_valid(url)
        try:
            response = requests.get(
                final_url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/122.0.0.0 Safari/537.36"
                    ),
                    "Accept": (
                        "text/html,application/xhtml+xml,application/xml;"
                        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
                    ),
                    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Connection": "keep-alive",
                    "DNT": "1",  # Do Not Track 요청
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Referer": "https://www.google.com/",
                },
                timeout=2,
                allow_redirects=True,
            )
        except Exception as e:
            print(e)
            response = requests.get(
                final_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36",
                    "Accept": (
                        "text/html,application/xhtml+xml,application/xml;"
                        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
                    ),
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Connection": "keep-alive",
                    "DNT": "1",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Referer": "https://www.google.com/",
                },
                timeout=1,
                allow_redirects=True,
            )
        response.encoding = response.apparent_encoding

        html = response.text
        bs = BeautifulSoup(html, "html.parser")

        title_tag = bs.find("title")
        og_title_tag = bs.find("meta", property="og:title")
        title = (
            og_title_tag.get("content", "").strip()
            if og_title_tag
            else (title_tag.text.strip() if title_tag else "")
        )

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
        body_element = next(
            (
                bs.select_one(selector)
                for selector in possible_selectors
                if bs.select_one(selector)
            ),
            None,
        )
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
