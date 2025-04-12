import base64
import gzip
import json
from datetime import datetime, timedelta
from typing import List

from app.models.article import Article
from app.models.article_tag import article_tag_association
from app.models.content import Content
from app.models.content_tag import content_tag_association
from app.models.tag import Tag
from app.models.user import User
from app.schemas.article import (
    ArticleCreate,
    ArticleDelete,
    ArticleDownload,
    ArticleEdit,
)
from fastapi import HTTPException
from sqlalchemy import and_, desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload


class ArticleService:
    @staticmethod
    async def post_article(article: ArticleCreate, db: AsyncSession) -> int:
        """
        article db에 저장 후 id 반환
        """
        result = await db.execute(select(User).where(User.id == article.user_id))
        db_user = result.unique().scalars().first()
        if not db_user:
            raise HTTPException(
                status_code=400, detail=f"User id {article.user_id} does not exists"
            )

        tag_list = article.tags
        result = await db.execute(select(Tag).where(Tag.tagname.in_(tag_list)))
        existing_tags = {tag.tagname: tag for tag in result.unique().scalars().all()}

        new_tags = []
        for tagname in tag_list:
            if tagname not in existing_tags:
                new_tag = Tag(tagname=tagname, user_id=db_user.id)
                db.add(new_tag)
                new_tags.append(new_tag)

        await db.flush()
        all_tags = list(existing_tags.values()) + new_tags

        new_article = Article(
            title=article.title,
            body=article.body,
            encoded_content=article.encoded_content,
            up_count=0,
            down_count=0,
            user_id=article.user_id,
            tags=all_tags,
        )

        try:
            db.add(new_article)
            await db.commit()
            await db.refresh(new_article)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=500, detail="DB error while creating article"
            )

        return new_article.id

    @staticmethod
    async def put_article(
        article_id: int, article: ArticleEdit, db: AsyncSession
    ) -> int:
        """
        특정 article의 정보 수정 후 id 반환
        """
        result = await db.execute(select(Article).where(Article.id == article_id))
        db_article = result.unique().scalars().first()
        if not db_article:
            raise HTTPException(
                status_code=400,
                detail=f"Article id {article_id} does not exists",
            )

        db_article.title = article.title
        db_article.body = article.body

        result = await db.execute(select(Tag).where(Tag.tagname.in_(article.tags)))
        existing_tags = result.unique().scalars().all()
        existing_tags_names = {tag.tagname for tag in existing_tags}

        new_tag_names = set(article.tags) - existing_tags_names
        new_tags = [Tag(tagname=name) for name in new_tag_names]
        db.add_all(new_tags)
        await db.commit()
        await db.refresh(db_article)

        all_tags = existing_tags + new_tags
        db_article.tags = all_tags

        await db.commit()

        return db_article.id

    @staticmethod
    async def delete_article(article: ArticleDelete, db: AsyncSession) -> int:
        """
        특정 user의 특정 article 삭제 후 id 반환
        """
        result = await db.execute(
            select(Article).where(Article.id == article.article_id)
        )
        db_article = result.unique().scalars().first()
        if not db_article:
            raise HTTPException(
                status_code=400,
                detail=f"Article id {article.article_id} does not exists",
            )

        if db_article.user_id is not article.user_id:
            raise HTTPException(
                status_code=400,
                detail=f"Article {article.article_id} is not owned by user {article.user_id}",
            )

        try:
            await db.delete(db_article)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=500, detail="DB error while deleting article"
            )

        return db_article.id

    @staticmethod
    async def get_all_user_articles_limit(
        user_id: int, limit: int, offset: int, db: AsyncSession
    ) -> List[Article]:
        """
        특정 유저의 offset으로부터 limit만큼의 article 반환
        """
        result = await db.execute(
            select(Article)
            .options(
                selectinload(Article.user),
                selectinload(Article.tags),
            )
            .where(Article.user_id == user_id)
            .order_by(desc(Article.created_at))
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()

    @staticmethod
    async def get_all_articles_limit(
        limit: int, offset: int, db: AsyncSession
    ) -> List[Article]:
        """
        offset으로부터 limit 개수의 article 반환
        """
        result = await db.execute(
            select(Article)
            .join(User, User.id == Article.user_id)
            .options(
                selectinload(Article.user),
                selectinload(Article.tags),
            )
            .order_by(desc(Article.created_at))
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()

    @staticmethod
    async def get_popular_articles(
        limit: int, offset: int, db: AsyncSession
    ) -> List[Article]:
        """
        다운로드 수 내림차순으로 offset부터 limit만큼 articles 반환
        """
        result = await db.execute(
            select(Article)
            .options(
                selectinload(Article.user),
                selectinload(Article.tags),
            )
            .order_by(desc(Article.down_count))
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()

    @staticmethod
    async def get_hot_articles(
        limit: int, offset: int, db: AsyncSession
    ) -> List[Article]:
        """
        마지막 article로부터 24시간 이내에 있는 articles 중
        가장 download 수 많은 articles, offset부터 limit만큼 반환
        """
        result = await db.execute(select(func.max(Article.created_at)))
        last_article_time = result.scalar()

        result = await db.execute(
            select(Article)
            .options(
                selectinload(Article.user),
                selectinload(Article.tags),
            )
            .where(
                and_(
                    Article.created_at >= (last_article_time - timedelta(hours=24)),
                    Article.created_at <= last_article_time,
                )
            )
            .order_by(desc(Article.down_count))
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()

    @staticmethod
    async def get_upvote_articles(
        limit: int, offset: int, db: AsyncSession
    ) -> List[Article]:
        """
        upvote 수 내림차순으로 offset부터 limit만큼 articles 반환
        """
        result = await db.execute(
            select(Article)
            .options(
                selectinload(Article.user),
                selectinload(Article.tags),
            )
            .order_by(desc(Article.up_count))
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()

    @staticmethod
    async def get_newest_articles(
        limit: int, offset: int, db: AsyncSession
    ) -> List[Article]:
        """
        created_at 내림차순 offset부터 limit만큼 articles 반환
        """
        result = await db.execute(
            select(Article)
            .options(
                selectinload(Article.user),
                selectinload(Article.tags),
            )
            .order_by(desc(Article.created_at))
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()

    @staticmethod
    async def get_random_articles(
        limit: int, offset: int, db: AsyncSession
    ) -> List[Article]:
        """
        offset부터 limit만큼 임의의 articles 반환
        """
        result = await db.execute(
            select(Article)
            .options(
                selectinload(Article.user),
                selectinload(Article.tags),
            )
            .order_by(func.random())
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()

    @staticmethod
    async def download_article(
        article: ArticleDownload, article_id: int, db: AsyncSession
    ) -> int:
        """
        article에 존재하는 encoded_content 파싱 및 user에 저장 후 tag id 반환
        """
        result = await db.execute(select(User).where(User.id == article.user_id))
        db_user = result.unique().scalars().first()
        if not db_user:
            raise HTTPException(
                status_code=400, detail=f"User id {article.user_id} does not exists"
            )

        result = await db.execute(select(Article).where(Article.id == article_id))
        db_article = result.unique().scalars().first()
        if not db_article:
            raise HTTPException(
                status_code=400, detail=f"Article id {article_id} does not exists"
            )

        encoded_content = db_article.encoded_content

        decoded_data = base64.b64decode(encoded_content)
        decompressed_data = gzip.decompress(decoded_data).decode("utf-8")

        contents = json.loads(decompressed_data)["contents"]

        # 태그 새로 생성 -> tagname과 user_id가 같은게 있는지 확인해야됨
        result = await db.execute(
            select(Tag).where(
                and_(Tag.tagname == article.tagname, Tag.user_id == db_user.id)
            )
        )
        db_tag = result.unique().scalars().first()
        if not db_tag:
            db_tag = Tag(tagname=article.tagname, user_id=db_user.id)
            db.add(db_tag)
            await db.flush()
            await db.refresh(db_tag)

        for content in contents:
            db_content = Content(
                user_id=db_user.id,
                url=content["url"],
                title=content["title"],
                thumbnail=content["thumbnail"],
                favicon=content["favicon"],
                description=content["description"],
                bookmark=False,
                content_type=content["type"],
            )

            db.add(db_content)
            await db.flush()
            await db.refresh(db_content)

            stmt = content_tag_association.insert().values(
                content_id=db_content.id,
                tag_id=db_tag.id,
            )
            await db.execute(stmt)

        db_article.down_count = db_article.down_count + 1

        await db.commit()

        return db_tag.id

    @staticmethod
    async def get_popular_tags(count: int, db: AsyncSession) -> List[dict]:
        """
        article에 연결된 tag 중에 가장 다운로드 수가 많은 tags, count만큼 반환
        """
        result = await db.execute(
            select(
                Tag.id,
                Tag.tagname,
                func.sum(Article.down_count).label("total_down_count"),
            )
            .join(article_tag_association, Tag.id == article_tag_association.c.tag_id)
            .join(Article, article_tag_association.c.article_id == Article.id)
            .group_by(Tag.id, Tag.tagname)
            .order_by(desc("total_down_count"))
            .limit(count)
        )
        return [
            {
                "id": tag.id,
                "tagname": tag.tagname,
                "total_down_count": tag.total_down_count,
            }
            for tag in result.all()
        ]

    @staticmethod
    async def get_hot_tags(count: int, db: AsyncSession) -> List[dict]:
        """
        마지막 article로부터 24시간 이내에 있는 articles 중
        가장 download 수 많은 tags, count만큼 반환
        """
        result = await db.execute(select(func.max(Article.created_at)))
        last_article_time = result.scalar()

        result = await db.execute(
            select(
                Tag.id,
                Tag.tagname,
                func.sum(Article.down_count).label("total_down_count"),
            )
            .join(article_tag_association, Tag.id == article_tag_association.c.tag_id)
            .join(Article, article_tag_association.c.article_id == Article.id)
            .where(
                and_(
                    Article.created_at >= (last_article_time - timedelta(hours=24)),
                    Article.created_at <= last_article_time,
                )
            )
            .group_by(Tag.id, Tag.tagname)
            .order_by(desc("total_down_count"))
            .limit(count)
        )
        return [
            {
                "id": tag.id,
                "tagname": tag.tagname,
                "total_down_count": tag.total_down_count,
            }
            for tag in result.all()
        ]

    @staticmethod
    async def get_upvote_tags(count: int, db: AsyncSession) -> List[dict]:
        """
        가장 up vote가 많은 tags, count만큼 반환
        """
        result = await db.execute(
            select(
                Tag.id,
                Tag.tagname,
                func.sum(Article.up_count).label("total_up_count"),
            )
            .join(article_tag_association, Tag.id == article_tag_association.c.tag_id)
            .join(Article, article_tag_association.c.article_id == Article.id)
            .group_by(Tag.id, Tag.tagname)
            .order_by(desc("total_up_count"))
            .limit(count)
        )
        return [
            {
                "id": tag.id,
                "tagname": tag.tagname,
                "total_up_count": tag.total_up_count,
            }
            for tag in result.all()
        ]

    @staticmethod
    async def get_newest_tags(count: int, db: AsyncSession) -> List[dict]:
        """
        가장 최신의 tags, count만큼 반환
        """
        result = await db.execute(
            select(
                Tag.id,
                Tag.tagname,
            )
            .join(article_tag_association, Tag.id == article_tag_association.c.tag_id)
            .join(Article, article_tag_association.c.article_id == Article.id)
            .order_by(desc(Tag.id))
            .distinct(Tag.id)
            .limit(count)
        )
        return [
            {
                "id": tag.id,
                "tagname": tag.tagname,
            }
            for tag in result.all()
        ]

    @staticmethod
    async def get_owned_tags(user_id: int, count: int, db: AsyncSession) -> List[dict]:
        """
        유저가 작성한 article의 tags, count만큼 반환
        count가 -1일시 전부 반환
        """
        query = (
            select(
                Tag.id,
                Tag.tagname,
            )
            .join(article_tag_association, Tag.id == article_tag_association.c.tag_id)
            .join(Article, article_tag_association.c.article_id == Article.id)
            .where(Article.user_id == user_id)
            .order_by(desc(Tag.id))
            .distinct(Tag.id)
        )

        if count != -1:
            query = query.limit(count)

        result = await db.execute(query)
        return [
            {
                "id": tag.id,
                "tagname": tag.tagname,
            }
            for tag in result.all()
        ]

    @staticmethod
    async def get_random_tags(count: int, db: AsyncSession) -> List[dict]:
        """
        랜덤 tags, count만큼 반환
        """
        result = await db.execute(
            select(
                Tag.id,
                Tag.tagname,
            )
            .join(article_tag_association, Tag.id == article_tag_association.c.tag_id)
            .join(Article, article_tag_association.c.article_id == Article.id)
            .group_by(Tag.id, Tag.tagname)
            .order_by(func.random())
            .limit(count)
        )
        return [
            {
                "id": tag.id,
                "tagname": tag.tagname,
            }
            for tag in result.all()
        ]

    @staticmethod
    async def get_articles_by_tag_limit(
        tag_id: int, limit: int, offset: int, db: AsyncSession
    ) -> List[Article]:
        result = await db.execute(
            select(Article)
            .options(
                selectinload(Article.user),
                selectinload(Article.tags),
            )
            .where(Article.tags.any(Tag.id == tag_id))
            .order_by(desc(Article.updated_at))
            .limit(limit)
            .offset(offset)
        )
        return result.unique().scalars().all()
