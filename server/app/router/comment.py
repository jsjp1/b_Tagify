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


AllArticlesLimitResponse(
    articles=[
        ArticleModel(
            id=article.id,
            title=article.title,
            body=article.body,
            encoded_content=article.encoded_content,
            up_count=article.up_count,
            down_count=article.down_count,
            created_at=article.created_at,
            updated_at=article.updated_at,
            user_id=article.user.id,
            user_name=article.user.username,
            user_profile_image=article.user.profile_image,
            tags=[tag.tagname for tag in article.tags],
        )
        for article in articles
    ]
)
