from typing import List

from app.db import get_db
from app.schemas.comment import ArticleCommentsResponse, Comment
from app.services.comment import CommentService
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/endpoint_test")
def endpoint_test():
    return {"message": "ok"}


@router.get("/article/{article_id}")
async def get_article_all_comments(
    article_id: int,
    db: Session = Depends(get_db),
) -> ArticleCommentsResponse:
    comments = await CommentService.get_article_all_comments(article_id, db)
    return ArticleCommentsResponse(
        comments=[
            Comment(
                id=comment.id,
                user_id=comment.user_id,
                body=comment.body,
                up_count=comment.up_count,
                down_count=comment.down_count,
            )
            for comment in comments
        ]
    )