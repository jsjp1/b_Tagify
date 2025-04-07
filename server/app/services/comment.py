from typing import List

from app.models.article import Article
from app.models.comment import Comment
from app.schemas.comment import PostCommentRequest
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
        db_article = db.query(Article).filter(Article.id == article_id).first()
        if not db_article:
            raise HTTPException(
                status_code=400, detail=f"Article id {article_id} does not exists"
            )  # TODO: 이 과정 꼭 필요한지?

        comments = (
            db.query(Comment)
            .filter(Comment.article_id == article_id)
            .order_by(asc(Comment.created_at))
            .all()
        )

        return comments

    @staticmethod
    async def post_comment(
        article_id: int, comment: PostCommentRequest, db: Session
    ) -> int:
        """
        특정 article에 속하는 comment 등록 후 해당 comment 정보 반환
        """
        db_article = db.query(Article).filter(Article.id == article_id).first()
        if not db_article:
            raise HTTPException(
                status_code=400, detail=f"Article id {article_id} does not exists"
            )

        new_comment = Comment(
            body=comment.body,
            user_id=comment.user_id,
            article_id=article_id,
        )

        try:
            db.add(new_comment)
            db.commit()
            db.refresh(new_comment)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=500, detail="DB error while creating comment"
            )

        return new_comment.id

    @staticmethod
    async def delete_comment(comment_id: int, db: Session) -> int:
        """
        특정 comment 삭제 후 id 반환
        """
        db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not db_comment:
            raise HTTPException(
                status_code=400, detail=f"Comment id {comment_id} does not exists"
            )

        try:
            db.delete(db_comment)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=500, detail="DB error while deleting comment"
            )

        return db_comment.id
