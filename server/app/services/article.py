from typing import List

from app.models.article import Article
from app.models.user import User
from app.schemas.article import (
    AllArticlesLimitResponse,
    ArticleCreate,
    ArticleDelete,
    ArticleModel,
)
from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import Session, joinedload


class ArticleService:
    @staticmethod
    async def post_article(article: ArticleCreate, db: Session) -> int:
        """
        article db에 저장 후 id 반환
        """
        db_user = db.query(User).filter(User.id == article.user_id).first()
        if not db_user:
            raise HTTPException(
                status_code=400, detail=f"User id {article.user_id} does not exists"
            )

        new_article = Article(
            title=article.title,
            body=article.body,
            encoded_content=article.encoded_content,
            up_count=0,
            down_count=0,
            user_id=article.user_id,
        )

        try:
            db.add(new_article)
            db.commit()
            db.refresh(new_article)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=500, detail="DB error while creating article"
            )

        return new_article.id

    @staticmethod
    async def delete_article(article: ArticleDelete, db: Session) -> int:
        """
        특정 user의 특정 article 삭제 후 id 반환
        """
        db_article = db.query(Article).filter(Article.id == article.article_id).first()
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
            db.delete(db_article)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=500, detail="DB error while deleting article"
            )

        return db_article.id

    @staticmethod
    async def get_all_articles_limit(
        limit: int, offset: int, db: Session
    ) -> AllArticlesLimitResponse:
        """
        offset으로부터 limit 개수의 article 반환
        """
        db_articles = (
            db.query(Article)
            .join(User, User.id == Article.user_id)
            .options(joinedload(Article.user))
            .order_by(desc(Article.updated_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

        articles = [
            ArticleModel(
                **article.__dict__,
                user_name=article.user.username,
                user_profile_image=article.user.profile_image,
            )
            for article in db_articles
        ]

        return AllArticlesLimitResponse(articles=articles)
