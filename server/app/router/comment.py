from typing import List

from app.db import get_db
from app.schemas.comment import (
    ArticleCommentsResponse,
    CommentModel,
    DeleteCommentResponse,
    PostCommentRequest,
    PostCommentResponse,
)
from app.services.comment import CommentService
from fastapi import APIRouter, Depends
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
            CommentModel(
                id=comment.id,
                user_id=comment.user_id,
                user_name=comment.user.username,
                user_profile_image=comment.user.profile_image,
                body=comment.body,
                up_count=comment.up_count,
                down_count=comment.down_count,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
            )
            for comment in comments
        ]
    )


@router.post("/article/{article_id}")
async def post_comment(
    article_id: int,
    request: PostCommentRequest,
    db: Session = Depends(get_db),
) -> PostCommentResponse:
    comment_id = await CommentService.post_comment(article_id, request, db)
    return PostCommentResponse(id=comment_id)


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
) -> DeleteCommentResponse:
    comment_id = await CommentService.delete_comment(comment_id, db)
    return DeleteCommentResponse(id=comment_id)
