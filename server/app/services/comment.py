from typing import List

from app.models.article import Article
from app.models.comment import Comment
from app.schemas.comment import PostCommentRequest
from fastapi import HTTPException
from sqlalchemy import asc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class CommentService:
    @staticmethod
    async def get_article_all_comments(article_id: int, db: AsyncSession) -> int:
        """
        article id에 속하는 모든 comments 반환
        """
        result = await db.execute(select(Article).filter(Article.id == article_id))
        db_article = result.unique().scalars().first()
        if not db_article:
            raise HTTPException(
                status_code=400, detail=f"Article id {article_id} does not exists"
            )  # TODO: 이 과정 꼭 필요한지?

        result = await db.execute(
            select(Comment)
            .filter(Comment.article_id == article_id)
            .order_by(asc(Comment.created_at))
        )
        comments = result.unique().scalars().all()

        return comments

    @staticmethod
    async def post_comment(
        article_id: int, comment: PostCommentRequest, db: AsyncSession
    ) -> int:
        """
        특정 article에 속하는 comment 등록 후 해당 comment 정보 반환
        """
        result = await db.execute(select(Article).filter(Article.id == article_id))
        db_article = result.unique().scalars().first()
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
            await db.commit()
            await db.refresh(new_comment)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=500, detail="DB error while creating comment"
            )

        return new_comment.id

    @staticmethod
    async def delete_comment(comment_id: int, db: AsyncSession) -> int:
        """
        특정 comment 삭제 후 id 반환
        """
        result = await db.execute(select(Comment).filter(Comment.id == comment_id))
        db_comment = result.unique().scalars().first()
        if not db_comment:
            raise HTTPException(
                status_code=400, detail=f"Comment id {comment_id} does not exists"
            )

        try:
            await db.delete(db_comment)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=500, detail="DB error while deleting comment"
            )

        return db_comment.id
