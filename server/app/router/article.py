from typing import List

from app.db import get_db
from app.middleware.exception_handler import handle_exceptions
from app.schemas.article import (
    AllArticlesLimitResponse,
    ArticleCreate,
    ArticleCreateResponse,
    ArticleDelete,
    ArticleDeleteResponse,
    ArticleDownload,
    ArticleDownloadResponse,
    ArticleModel,
)
from app.services.article import ArticleService
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/endpoint_test")
def endpoint_test():
    return {"message": "ok"}


@router.post("/")
async def create_article(
    request: ArticleCreate, db: Session = Depends(get_db)
) -> ArticleCreateResponse:
    article_id = await ArticleService.post_article(request, db)
    return ArticleCreateResponse(id=article_id)


@router.delete("/")
async def delete_article(
    request: ArticleDelete, db: Session = Depends(get_db)
) -> ArticleDeleteResponse:
    article_id = await ArticleService.delete_article(request, db)
    return ArticleDeleteResponse(id=article_id)


@router.get("/all")
async def get_all_articles_limit(
    limit: int,
    offset: int,
    db: Session = Depends(get_db),
) -> AllArticlesLimitResponse:
    articles = await ArticleService.get_all_articles_limit(limit, offset, db)
    return articles


@router.post("/download/{article_id}")
async def download_article(
    request: ArticleDownload,
    article_id: int,
    db: Session = Depends(get_db),
) -> ArticleDownloadResponse:
    tag_id = await ArticleService.download_article(request, article_id, db)
    return ArticleDownloadResponse(tag_id=tag_id)
