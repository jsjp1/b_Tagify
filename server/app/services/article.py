from typing import List

from app.models.article import Article
from app.models.user import User
from app.schemas.article import ArticleCreate
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


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
    async def get_all_articles_limit(limit: int, offset: int, db: Session) -> List[Article]:
        """
        offset으로부터 limit 개수의 article 반환
        """
        db_articles = db.query(Article).limit(limit).offset(offset).all()

        return db_articles
