from typing import List

from app.models.article import Article
from app.models.comment import Comment
from fastapi import HTTPException
from sqlalchemy import and_, asc, desc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import Session, joinedload


class CommentService:
    @staticmethod
    async def get_article_all_comments(article_id: int, db: Session) -> int:
        """
        article id에 속하는 모든 comments 반환
        """
        comments = (
            db.query(Comment)
            .filter(Comment.article_id == article_id)
            .order_by(asc(Comment.created_at))
            .all()
        )

        return comments
